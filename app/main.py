from __future__ import annotations

import csv
import html
import io
import json
import logging
import os
import re
import secrets
import sqlite3
import urllib.error
import urllib.request
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Iterator

import markdown

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, EmailStr, Field, field_validator
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)
# uvicorn 默认不配置 root logger，INFO 级日志（自动回复成功、webhook 活动等）
# 会被吞掉；显式配置后 docker logs 里才能看到。
logging.basicConfig(level=logging.INFO)

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "lawyers.sqlite3"
FILES_DIR = DB_PATH.parent / "files"
SCHEMA_VERSION = 3

# Public base URL used for canonical/OG/sitemap links. Override in prod.
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000").rstrip("/")


def _ga_tag() -> str:
    """Google Analytics 4 snippet, injected into HTML heads.

    Read per-request (like the admin token) so tests can toggle it via the
    environment. Empty/unset = analytics disabled and no tag is rendered.
    """
    ga_id = os.environ.get("GA_MEASUREMENT_ID", "").strip()
    if not ga_id:
        return ""
    return (
        '<script async src="https://www.googletagmanager.com/gtag/js?id={id}"></script>\n'
        '<script>window.dataLayer=window.dataLayer||[];'
        "function gtag(){{dataLayer.push(arguments);}}"
        "gtag('js',new Date());gtag('config','{id}');</script>"
    ).format(id=ga_id)

# Per-IP limit for the public intake form. Prevents spam bots from flooding
# the SQLite database. Humans rarely submit more than a few times a minute.
INTAKE_RATE_LIMIT = "5/minute"
ADMIN_RATE_LIMIT = "30/minute"

# Materials checklist per matter type, used in the auto-reply email.
MATERIALS_BY_MATTER = {
    "trade": ["合同、订单、发票、付款记录", "提单、物流、报关、质检文件", "与对方的邮件、微信、WhatsApp 记录", "对方公司名称、地址、联系人信息"],
    "recovery": ["欠款金额和到期时间", "债务人公司或个人信息", "合同、账单、催款记录", "已有判决、仲裁裁决或资产线索"],
    "legacy": ["亲属关系证明", "死亡证明、遗嘱或遗产文件", "房产、股权、存款等资产线索", "涉及国家或地区、家族成员联系方式"],
    "unsure": ["简要时间线", "相关人员、公司或家族成员信息", "合同、沟通记录、资产线索或已有文件", "你希望解决的问题和理想结果"],
}


def _matter_key(matter: str) -> str:
    if "国际贸易" in matter:
        return "trade"
    if "诉讼" in matter or "债务" in matter:
        return "recovery"
    if "继承" in matter or "家族" in matter:
        return "legacy"
    return "unsure"


def _dedupe_window_hours() -> int:
    """Reject resubmissions from the same email/phone within this window."""
    return int(os.environ.get("DEDUPE_WINDOW_HOURS", "24"))

# Lead status workflow: 新线索 -> 已联系 -> 处理中 -> 已结案
VALID_STATUSES = ("new", "contacted", "in_progress", "closed")
STATUS_LABELS = {
    "new": "新线索",
    "contacted": "已联系",
    "in_progress": "处理中",
    "closed": "已结案",
}

# Content for the three service landing pages (bilingual, matches homepage copy).
SERVICES = {
    "trade": {
        "slug": "trade",
        "number": "01 / TRADE",
        "zh_title": "国际贸易争议",
        "en_title": "International Trade Disputes",
        "zh_intro": "处理交易履行、货款、代理与跨境合同之间的纠纷，从欠款事实与证据入手，判断协商、追收或诉讼路径。",
        "en_intro": "We handle disputes over performance, payment, agencies, distribution, and cross-border contracts — starting from the facts and evidence to map negotiation, recovery, or litigation.",
        "items_zh": ["拖欠货款 / 供应商违约", "代理、经销、跨境合同审查", "海关、物流、质量争议", "国际贸易诈骗识别与应对"],
        "items_en": ["Unpaid invoices / supplier breach", "Agency, distribution & contract review", "Customs, logistics & quality disputes", "Trade fraud identification & response"],
        "materials_zh": MATERIALS_BY_MATTER["trade"],
        "materials_en": [
            "Contracts, purchase orders, invoices, and payment records",
            "Bills of lading, logistics, customs, and quality inspection documents",
            "Emails, WeChat, WhatsApp, or other communications",
            "Counterparty company name, address, and contact details",
        ],
    },
    "recovery": {
        "slug": "recovery",
        "number": "02 / RECOVERY",
        "zh_title": "诉讼与债务追收",
        "en_title": "Litigation & Debt Recovery",
        "zh_intro": "从欠款事实与资产线索出发，判断追收、诉讼或执行路径，覆盖中国境内与海外资产。",
        "en_intro": "We assess recovery, litigation, and enforcement options from the facts and asset trail — covering assets both in mainland China and abroad.",
        "items_zh": ["海外客户欠款追收", "中国境内与海外资产调查", "判决、仲裁裁决跨境执行", "商业欺诈调查"],
        "items_en": ["Overseas customer debt recovery", "Asset tracing in China and abroad", "Cross-border judgment & award enforcement", "Commercial fraud investigation"],
        "materials_zh": MATERIALS_BY_MATTER["recovery"],
        "materials_en": [
            "Debt amount and due date",
            "Debtor company or individual information",
            "Contracts, statements, and demand records",
            "Existing judgments, arbitral awards, or asset clues",
        ],
    },
    "legacy": {
        "slug": "legacy",
        "number": "03 / LEGACY",
        "zh_title": "继承与家族资产纠纷",
        "en_title": "Inheritance & Family Assets",
        "zh_intro": "协助梳理大陆与海外多地的继承、房产、股权与家族争议，明确材料、法域与处理顺序。",
        "en_intro": "We help you navigate multi-jurisdiction inheritance, property, equity, and family conflicts — clarifying documents, jurisdictions, and the order of steps.",
        "items_zh": ["中国大陆与海外多地继承", "房产、股权、存款继承", "遗嘱、遗产分割", "家族成员失联或争议"],
        "items_en": ["Mainland China and multi-country inheritance", "Property, equity, and deposit inheritance", "Wills and estate division", "Missing or disputed family members"],
        "materials_zh": MATERIALS_BY_MATTER["legacy"],
        "materials_en": [
            "Proof of family relationship",
            "Death certificate, will, or estate documents",
            "Property, equity, deposit, or other asset clues",
            "Relevant countries or regions and family member contact details",
        ],
    },
}


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    # WAL allows concurrent readers with a single writer; busy_timeout waits
    # instead of failing immediately with "database is locked".
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=5000")
    return connection


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    """Yield a connection, committing on success and always closing it.

    Unlike `with sqlite3.connect(...)` (which only commits/rolls back and
    leaks the connection until it is garbage-collected), this explicitly
    closes the underlying handle on every exit path.
    """
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    with db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS intakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                matter TEXT NOT NULL,
                summary TEXT NOT NULL,
                country_or_region TEXT,
                language TEXT NOT NULL DEFAULT 'zh',
                user_agent TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                note TEXT,
                consent_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intake_id INTEGER NOT NULL,
                original_name TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                size INTEGER NOT NULL,
                content_type TEXT,
                uploaded_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                viewed_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                ip TEXT,
                action TEXT NOT NULL,
                detail TEXT
            )
            """
        )
        migrate_schema(connection)


def migrate_schema(connection: sqlite3.Connection) -> None:
    """Forward-only, non-destructive schema migrations.

    Version tracking uses SQLite's PRAGMA user_version (0 = pre-migration).
    Each step only adds columns/tables; existing rows are never dropped.
    """
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version >= SCHEMA_VERSION:
        return

    columns = [row["name"] for row in connection.execute("PRAGMA table_info(intakes)")]
    if "country_or_region" not in columns:
        # v2: country/region field called for by design-sketch.md.
        connection.execute("ALTER TABLE intakes ADD COLUMN country_or_region TEXT")
    if "status" not in columns:
        # v3: lead status workflow (新线索 -> 已联系 -> 处理中 -> 已结案).
        connection.execute(
            "ALTER TABLE intakes ADD COLUMN status TEXT NOT NULL DEFAULT 'new'"
        )
    if "note" not in columns:
        # v3: follow-up notes per lead.
        connection.execute("ALTER TABLE intakes ADD COLUMN note TEXT")
    if "consent_at" not in columns:
        # v3: privacy consent timestamp (PIPL).
        connection.execute("ALTER TABLE intakes ADD COLUMN consent_at TEXT")

    # v4: case materials uploads.
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intake_id INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            size INTEGER NOT NULL,
            content_type TEXT,
            uploaded_at TEXT NOT NULL
        )
        """
    )
    # v5: lightweight conversion analytics (page views).
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS page_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viewed_at TEXT NOT NULL
        )
        """
    )
    # v6: admin/ops audit trail.
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            ip TEXT,
            action TEXT NOT NULL,
            detail TEXT
        )
        """
    )

    logger.info("Migrating intakes schema to version %d", SCHEMA_VERSION)
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


_production = os.environ.get("APP_ENV") == "production"
app = FastAPI(
    title="Shenyuan Legal",
    version="0.1.0",
    lifespan=lifespan,
    # Interactive docs expose the API schema; hide them in production.
    docs_url=None if _production else "/docs",
    redoc_url=None if _production else "/redoc",
    openapi_url=None if _production else "/openapi.json",
)


def _client_ip(request: Request) -> str:
    """Use the real client IP when running behind a reverse proxy."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=_client_ip)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )


def _admin_token() -> str:
    """Bearer token for admin endpoints. Read per-request so tests can
    override it via the environment; empty means the admin area is disabled."""
    return os.environ.get("ADMIN_TOKEN", "")


def _is_authorized(request: Request) -> bool:
    token = _admin_token()
    if not token:
        return False
    provided = request.headers.get("authorization", "")
    if provided.startswith("Bearer "):
        provided = provided[len("Bearer ") :].strip()
    return secrets.compare_digest(provided, token)


def log_audit(ip: str, action: str, detail: str) -> None:
    """Append an entry to the audit trail. Best-effort: never raises."""
    try:
        with db_connection() as connection:
            connection.execute(
                "INSERT INTO audit_log (ts, ip, action, detail) VALUES (?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), ip, action, detail),
            )
    except sqlite3.Error:
        logger.exception("Failed to write audit log (%s %s)", action, detail)


def _require_admin(request: Request) -> None:
    if not _is_authorized(request):
        log_audit(_client_ip(request), "auth_failed", request.url.path)
        raise HTTPException(status_code=401, detail="Unauthorized")


def _notify_webhook_url() -> str:
    """Webhook URL for new-intake alerts (WeChat Work bot, DingTalk, ...).
    Empty means notifications are disabled. Read per-request for testability."""
    return os.environ.get("NOTIFY_WEBHOOK_URL", "")


def _send_intake_notification(intake: dict) -> None:
    """POST a new-intake alert to the configured webhook.

    Fire-and-forget: failures are logged, never surfaced to the client.
    The default payload format matches the WeChat Work group bot API.
    """
    url = _notify_webhook_url()
    if not url:
        return
    content = "\n".join(
        [
            "【新咨询通知】",
            f"姓名：{intake['name']}",
            f"事项类型：{intake['matter']}",
            f"国家/地区：{intake.get('country') or '-'}",
            f"邮箱：{intake['email']}",
            f"电话：{intake.get('phone') or '-'}",
            f"语言：{'中文' if intake.get('language', 'zh') == 'zh' else 'English'}",
            f"提交时间：{intake['created_at']}",
            f"问题描述：{intake['summary']}",
        ]
    )
    payload = json.dumps({"msgtype": "text", "text": {"content": content}}).encode("utf-8")
    request = urllib.request.Request(url, method="POST")
    # 显式设置 headers：如果通过构造参数传 data + headers，urllib 可能再自动
    # 附加一个 x-www-form-urlencoded 的 Content-Type（大小写敏感检查的坑）。
    request.add_header("Content-Type", "application/json")
    # Resend 的 API 在 Cloudflare 后面，默认的 Python-urllib UA 会被 1010 拦截。
    request.add_header("User-Agent", "shenyuan-law-firm/1.0")
    request.data = payload
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read()
        # WeChat-style webhooks return HTTP 200 with an errcode body even on
        # rejection (e.g. revoked key) — surface that instead of staying silent.
        try:
            result = json.loads(body.decode("utf-8", errors="replace"))
            if result.get("errcode"):
                logger.error(
                    "Notification webhook rejected: %s", result.get("errmsg", result)
                )
        except ValueError:
            pass  # non-JSON endpoint; assume delivered
    except Exception:
        logger.exception("Failed to send intake notification webhook")


def _resend_api_key() -> str:
    """Resend API key. Read per-request for testability; empty = feature off."""
    return os.environ.get("RESEND_API_KEY", "")


def _resend_from() -> str:
    return os.environ.get("RESEND_FROM", "no-reply@shenyuanlegal.com")


def _send_auto_reply(intake: dict) -> None:
    """Send a confirmation + materials-checklist email via the Resend API.

    Disabled unless RESEND_API_KEY is configured. Failures are logged,
    never surfaced to the request. The sender domain must be verified in
    Resend before messages will be accepted.
    """
    api_key = _resend_api_key()
    if not api_key:
        return

    key = _matter_key(intake["matter"])
    materials = "\n".join(f"- {item}" for item in MATERIALS_BY_MATTER[key])
    body = (
        f"您好，{intake['name']}，\n\n"
        "我们已收到您的咨询信息，会尽快与您联系。\n"
        "Dear client, we have received your inquiry and will get back to you shortly.\n\n"
        "建议先准备以下材料 / Suggested documents to prepare:\n"
        f"{materials}\n\n"
        "紧急情况（财产转移、期限临近、证据灭失等）请直接通过微信注明“紧急”。\n"
        "If the matter is urgent, please mark it as urgent on WeChat.\n\n"
        "本邮件不构成委托关系或正式法律意见。\n"
        "This email does not create an attorney-client relationship or formal legal advice."
    )
    html_body = (
        "<!doctype html><html><body "
        "style=\"font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;"
        "color:#172433;line-height:1.7;max-width:600px;margin:0 auto;padding:24px;\">"
        f"<h2 style=\"color:#0d6c6b;\">已收到您的咨询信息</h2>"
        f"<p>您好，{intake['name']}，</p>"
        "<p>我们已收到您的咨询信息，会尽快与您联系。<br>"
        "<em>Dear client, we have received your inquiry and will get back to you shortly.</em></p>"
        "<p><strong>建议先准备以下材料 / Suggested documents to prepare:</strong></p><ul>"
        + "".join(f"<li>{item}</li>" for item in MATERIALS_BY_MATTER[key])
        + "</ul>"
        "<p style=\"color:#6b341d;\">紧急情况（财产转移、期限临近、证据灭失等）请直接通过微信注明“紧急”。<br>"
        "<em>If the matter is urgent, please mark it as urgent on WeChat.</em></p>"
        "<p style=\"font-size:12px;color:#627180;\">本邮件不构成委托关系或正式法律意见。<br>"
        "<em>This email does not create an attorney-client relationship or formal legal advice.</em></p>"
        "</body></html>"
    )

    payload = json.dumps(
        {
            "from": _resend_from(),
            "to": [intake["email"]],
            "subject": "已收到您的咨询信息 / We received your inquiry",
            "text": body,
            "html": html_body,
        }
    ).encode("utf-8")
    request = urllib.request.Request("https://api.resend.com/emails", method="POST")
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("Content-Type", "application/json")
    # Cloudflare 会拦截 Python-urllib 默认 UA（403 error code: 1010）。
    request.add_header("User-Agent", "shenyuan-law-firm/1.0")
    request.data = payload
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response_body = response.read()
        logger.info(
            "Auto-reply sent to %s via Resend (%s)",
            intake["email"],
            response_body.decode("utf-8", "replace")[:120],
        )
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        logger.error(
            "Resend rejected auto-reply to %s: HTTP %s %s",
            intake["email"],
            exc.code,
            detail,
        )
    except Exception:
        logger.exception("Failed to send auto-reply to %s", intake["email"])


class IntakeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=80)]
    email: Annotated[EmailStr, Field(min_length=3, max_length=254)]
    matter: Annotated[str, Field(min_length=1, max_length=80)]
    summary: Annotated[str, Field(min_length=1, max_length=2000)]
    phone: Annotated[str | None, Field(max_length=60)] = None
    country: Annotated[str | None, Field(max_length=80)] = None
    language: Annotated[str, Field(pattern="^(zh|en)$")] = "zh"
    # Explicitly required: the frontend always sends it, and omitting it must
    # fail loudly instead of silently defaulting to False (pydantic v2 does
    # not validate default values unless validate_default is set).
    consent: bool

    @field_validator("name", "email", "phone", "country", "matter", "summary", mode="before")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return str(value).strip()

    @field_validator("phone", "country")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        return value or None

    @field_validator("consent")
    @classmethod
    def require_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Privacy consent is required")
        return value


class AdminIntakeUpdate(BaseModel):
    status: Annotated[str | None, Field(pattern="^(new|contacted|in_progress|closed)$")] = None
    note: Annotated[str | None, Field(max_length=2000)] = None


class IntakeCreated(BaseModel):
    id: int
    status: str
    created_at: str


def _record_page_view() -> None:
    """Count a homepage visit for conversion analytics. Best-effort only."""
    try:
        with db_connection() as connection:
            connection.execute(
                "INSERT INTO page_views (viewed_at) VALUES (?)",
                (datetime.now(timezone.utc).isoformat(),),
            )
    except sqlite3.Error:
        logger.exception("Failed to record page view")


def _render_service_page(svc: dict) -> str:
    items = "".join(
        f'<li data-zh="{z}" data-en="{e}">{z}</li>'
        for z, e in zip(svc["items_zh"], svc["items_en"])
    )
    materials = "".join(
        f'<li data-zh="{z}" data-en="{e}">{z}</li>'
        for z, e in zip(svc["materials_zh"], svc["materials_en"])
    )
    url = f"{SITE_URL}/services/{svc['slug']}"
    en_url = f"{SITE_URL}/en/services/{svc['slug']}"
    zh_title = svc["zh_title"]
    en_title = svc["en_title"]
    zh_intro = svc["zh_intro"]
    en_intro = svc["en_intro"]
    number = svc["number"]
    ga_tag = _ga_tag()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow">
  <meta name="description" content="{zh_intro}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{zh_title} | Shenyuan International">
  <meta property="og:description" content="{zh_intro}">
  <meta property="og:url" content="{url}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="zh-CN" href="{url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="x-default" href="{url}">
  {ga_tag}
  <title>{zh_title} | Shenyuan International 深远(国际)律师事务所</title>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "LegalService",
    "name": "Shenyuan International 深远(国际)律师事务所",
    "url": "{url}",
    "description": "{zh_intro}",
    "knowsLanguage": ["zh", "en"],
    "areaServed": "Worldwide"
  }}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --ink: #172433; --muted: #627180; --paper: #f6f3ed; --surface: #fffdf9;
      --line: #d9d9d2; --teal: #0d6c6b; --teal-deep: #084d50;
      --orange: #d76e39; --cream: #ede8de; --gold: #b08d57;
      --shadow: 0 20px 50px rgba(20, 33, 44, .11);
      --radius: 10px; --max: 1060px;
      --serif: "Playfair Display", "Noto Serif SC", Georgia, "Songti SC", "SimSun", serif;
      --sans: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: var(--ink); background: var(--paper); font-family: var(--sans); line-height: 1.65; }}
    a {{ color: inherit; text-decoration: none; }}
    button {{ font: inherit; cursor: pointer; }}
    h1, h2, h3, p {{ margin: 0; }}
    h1, h2, h3 {{ font-family: var(--serif); }}
    .wrap {{ width: min(calc(100% - 40px), var(--max)); margin: 0 auto; }}

    .topbar {{ background: var(--teal-deep); color: #f5f2ec; }}
    .topbar .wrap {{ display: flex; justify-content: space-between; align-items: center; min-height: 66px; gap: 18px; }}
    .topbar .brand {{ display: inline-flex; align-items: center; gap: 10px; color: #fff; font-size: 14px; font-weight: 700; }}
    .brand-mark {{ display: grid; place-items: center; width: 30px; height: 30px; color: var(--teal-deep); background: #f7f2e9; border-radius: 7px; font-family: var(--serif); font-size: 16px; }}
    .topbar .nav-links {{ display: flex; align-items: center; gap: 18px; font-size: 13px; }}
    .topbar a {{ color: rgba(255,255,255,.85); }}
    .topbar a:hover {{ color: #fff; }}
    .lang-switch {{ padding: 7px 10px; color: rgba(255,255,255,.85); background: transparent; border: 1px solid rgba(255,255,255,.3); border-radius: 6px; font-size: 12px; }}

    .hero {{ padding: 64px 0 34px; }}
    .number {{ color: var(--gold); font-size: 13px; font-weight: 800; letter-spacing: .08em; }}
    h1 {{ margin: 16px 0 10px; font-size: clamp(32px, 4.4vw, 50px); line-height: 1.14; letter-spacing: -.01em; }}
    .en-sub {{ color: var(--muted); font-size: 15px; }}
    .intro {{ margin-top: 18px; font-size: 16px; max-width: 720px; color: #334454; }}

    .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin: 40px auto 0; }}
    .card {{ background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 26px; }}
    .card h2 {{ margin: 0 0 14px; font-size: 18px; }}
    ul {{ margin: 0; padding: 0; list-style: none; display: grid; gap: 9px; }}
    li {{ position: relative; padding-left: 16px; font-size: 14px; color: #435363; }}
    li::before {{ content: ""; position: absolute; left: 0; top: 9px; width: 5px; height: 5px; background: var(--gold); border-radius: 50%; }}

    .steps {{ margin-top: 18px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }}
    .step {{ padding: 22px 24px; }}
    .step + .step {{ border-left: 1px solid var(--line); }}
    .step span {{ display: block; color: var(--gold); font-size: 13px; font-weight: 800; }}
    .step h3 {{ margin-top: 10px; font-size: 16px; }}
    .step p {{ margin-top: 8px; color: var(--muted); font-size: 13px; }}

    .cta {{ text-align: center; padding: 46px 0 70px; }}
    .button {{ display: inline-flex; align-items: center; gap: 9px; min-height: 48px; padding: 0 26px; color: #fff; background: var(--orange); border-radius: 8px; font-size: 15px; font-weight: 700; transition: transform .2s ease, background .2s ease; }}
    .button:hover {{ transform: translateY(-2px); background: #c85d2e; }}
    .cta .note {{ margin-top: 14px; color: var(--muted); font-size: 12px; }}

    footer {{ background: #15232d; color: rgba(255,255,255,.72); font-size: 12px; padding: 22px 0; text-align: center; line-height: 1.7; }}
    footer a {{ color: rgba(255,255,255,.85); }}

    @media (max-width: 720px) {{
      .cols {{ grid-template-columns: 1fr; }}
      .steps {{ grid-template-columns: 1fr; }}
      .step + .step {{ border-left: 0; border-top: 1px solid var(--line); }}
      .topbar .wrap {{ min-height: 60px; }}
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="wrap">
      <a class="brand" href="/" aria-label="返回首页">
        <span class="brand-mark">深</span>
        <span>Shenyuan International</span>
      </a>
      <div class="nav-links">
        <a href="/" data-zh="返回首页" data-en="Home">返回首页</a>
        <button class="lang-switch" type="button" id="langToggle" aria-label="切换语言">EN / 中</button>
      </div>
    </div>
  </div>

  <div class="wrap hero">
    <div class="number">{number}</div>
    <h1 data-zh="{zh_title}" data-en="{en_title}">{zh_title}</h1>
    <div class="en-sub" data-zh="跨境争议解决与家族资产保护" data-en="Cross-border dispute resolution & family asset protection">跨境争议解决与家族资产保护</div>
    <p class="intro" data-zh="{zh_intro}" data-en="{en_intro}">{zh_intro}</p>
  </div>

  <div class="wrap cols">
    <div class="card">
      <h2 data-zh="常见情形" data-en="Common scenarios">常见情形</h2>
      <ul>{items}</ul>
    </div>
    <div class="card">
      <h2 data-zh="建议准备的材料" data-en="Suggested documents">建议准备的材料</h2>
      <ul>{materials}</ul>
    </div>
  </div>

  <div class="wrap steps">
    <div class="step"><span>01</span><h3 data-zh="免费咨询建档" data-en="Free consultation & intake">免费咨询建档</h3><p data-zh="提交基本情况，我们梳理人物、金额、时间线与目标。" data-en="Share the essentials; we map the parties, amounts, timeline, and goals.">提交基本情况，我们梳理人物、金额、时间线与目标。</p></div>
    <div class="step"><span>02</span><h3 data-zh="事实、证据与法域评估" data-en="Facts, evidence & jurisdiction">事实、证据与法域评估</h3><p data-zh="识别时效、证据、资产位置与可能涉及的法域。" data-en="Identify timing, evidence, asset location, and relevant jurisdictions.">识别时效、证据、资产位置与可能涉及的法域。</p></div>
    <div class="step"><span>03</span><h3 data-zh="策略、报价与执行" data-en="Strategy & execution">策略、报价与执行</h3><p data-zh="确定谈判、追收或诉讼策略，明确材料、风险与里程碑。" data-en="Define the strategy with clear milestones and risk boundaries.">确定谈判、追收或诉讼策略，明确材料、风险与里程碑。</p></div>
  </div>

  <div class="wrap cta">
    <a class="button" href="/#intake" data-zh="免费评估我的案件 →" data-en="Free case assessment →">免费评估我的案件 →</a>
    <p class="note" data-zh="提交不代表建立委托关系。初步咨询不收费，不承诺结果。" data-en="Submitting does not create an attorney-client relationship. Initial consultation is free and honest.">提交不代表建立委托关系。初步咨询不收费，不承诺结果。</p>
  </div>

  <footer>
    © 2026 Shenyuan International · 深远(国际)律师事务所<br>
    <span data-zh="境外法律程序通过与当地执业律所合作提供。本页内容不构成法律意见。" data-en="Foreign proceedings are conducted through locally licensed counsel. This page does not constitute legal advice.">境外法律程序通过与当地执业律所合作提供。本页内容不构成法律意见。</span>
  </footer>

  <script>
    (function () {{
      var currentLang = "zh";
      var zhTitle = {zh_title!r};
      var enTitle = {en_title!r};
      var langToggle = document.getElementById("langToggle");
      function updateLanguage() {{
        document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
        document.title = currentLang === "zh" ? zhTitle + " | Shenyuan International 深远(国际)律师事务所" : enTitle + " | Shenyuan International";
        document.querySelectorAll("[data-zh][data-en]").forEach(function (node) {{
          node.textContent = currentLang === "zh" ? node.getAttribute("data-zh") : node.getAttribute("data-en");
        }});
      }}
      langToggle.addEventListener("click", function () {{
        currentLang = currentLang === "zh" ? "en" : "zh";
        updateLanguage();
      }});
    }}());
  </script>
</body>
</html>"""


@app.get("/")
def read_index() -> Response:
    _record_page_view()
    html = (ROOT_DIR / "index.html").read_text(encoding="utf-8")
    return Response(
        content=html.replace("{{SITE_URL}}", SITE_URL).replace("{{GA_TAG}}", _ga_tag()),
        media_type="text/html; charset=utf-8",
    )


@app.api_route("/en", methods=["GET", "HEAD"], include_in_schema=False)
@app.api_route("/en/", methods=["GET", "HEAD"], include_in_schema=False)
def read_index_en() -> Response:
    _record_page_view()
    html = (ROOT_DIR / "index.html").read_text(encoding="utf-8")
    html = html.replace("{{SITE_URL}}", SITE_URL).replace("{{GA_TAG}}", _ga_tag())
    html = _en_variant(html)
    html = _swap_meta(html, "meta name=\"description\"", _EN_HOME_DESC)
    html = _swap_meta(html, "meta property=\"og:title\"", _EN_HOME_TITLE)
    html = _swap_meta(html, "meta property=\"og:description\"", _EN_HOME_DESC)
    html = re.sub(r"(<title>)[^<]*(</title>)", rf"\g<1>{_EN_HOME_TITLE}\g<2>", html, count=1)
    html = html.replace(
        f'<link rel="canonical" href="{SITE_URL}/">',
        f'<link rel="canonical" href="{SITE_URL}/en/">',
    )
    return Response(content=html, media_type="text/html; charset=utf-8")


@app.api_route("/robots.txt", methods=["GET", "HEAD"], include_in_schema=False)
def robots() -> Response:
    return Response(
        content=f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        media_type="text/plain",
    )


# ---------- English variants (/en/ URLs) ----------

_EN_HOME_TITLE = (
    "Shenyuan International | Cross-Border Dispute Resolution & Family Asset Protection"
)
_EN_HOME_DESC = (
    "Bilingual legal services for Chinese businesses and families: international trade "
    "disputes, cross-border debt recovery, inheritance and family assets. A local "
    "counsel network across 30+ jurisdictions."
)

# Swap the visible text of every `data-zh="..." data-en="..."` leaf node to its
# English value. All translatable nodes in our templates are plain-text leaves
# with attributes in exactly this order, so the regex is safe and dependency-free.
_SWAP_TO_EN_RE = re.compile(r'(data-zh=")([^"]*)(" data-en=")([^"]*)(">)([^<]*)(<)')


def _en_variant(html: str) -> str:
    """Turn a bilingual (zh-default) page into an English-default variant.

    Three changes: the visible leaf text is pre-swapped server-side (so even
    no-JS crawlers see English), the document language is set to en, and the
    in-page toggle initializes to English.
    """
    html = _SWAP_TO_EN_RE.sub(
        lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}{m.group(4)}{m.group(5)}{m.group(4)}{m.group(7)}",
        html,
    )
    html = html.replace('<html lang="zh-CN">', '<html lang="en">')
    html = html.replace('var currentLang = "zh";', 'var currentLang = "en";')
    html = html.replace(
        "}());\n  </script>",
        # Guarded: only the homepage/service-page scripts define updateLanguage();
        # article pages apply the EN state server-side already.
        "    if (typeof updateLanguage === \"function\") updateLanguage();\n    }());\n  </script>",
    )
    return html


def _swap_meta(html: str, tag: str, value: str) -> str:
    return re.sub(rf'(<{tag} content=")[^"]*(")', rf"\g<1>{value}\g<2>", html, count=1)


@app.api_route("/sitemap.xml", methods=["GET", "HEAD"], include_in_schema=False)
def sitemap() -> Response:
    urls = [f"{SITE_URL}/", f"{SITE_URL}/articles", f"{SITE_URL}/en/", f"{SITE_URL}/en/articles"] + [
        f"{SITE_URL}/services/{slug}" for slug in SERVICES
    ] + [f"{SITE_URL}/en/services/{slug}" for slug in SERVICES] + [
        f"{SITE_URL}/articles/{a['meta']['slug']}" for a in _load_articles()
    ] + [f"{SITE_URL}/en/articles/{a['meta']['slug']}" for a in _load_articles()]
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@app.get("/services/{slug}", include_in_schema=False)
def service_page(slug: str) -> Response:
    svc = SERVICES.get(slug)
    if svc is None:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(
        content=_render_service_page(svc),
        media_type="text/html; charset=utf-8",
    )


@app.api_route("/en/services/{slug}", methods=["GET", "HEAD"], include_in_schema=False)
def service_page_en(slug: str) -> Response:
    svc = SERVICES.get(slug)
    if svc is None:
        raise HTTPException(status_code=404, detail="Not found")
    page = _en_variant(_render_service_page(svc))
    page = _swap_meta(page, "meta name=\"description\"", html.escape(svc["en_intro"]))
    page = _swap_meta(page, "meta property=\"og:title\"", html.escape(svc["en_title"]) + " | Shenyuan International")
    page = _swap_meta(page, "meta property=\"og:description\"", html.escape(svc["en_intro"]))
    page = re.sub(
        r"(<title>)[^<]*(</title>)",
        rf"\g<1>{html.escape(svc['en_title'])} | Shenyuan International\g<2>",
        page,
        count=1,
    )
    page = page.replace(
        f'<link rel="canonical" href="{SITE_URL}/services/{slug}">',
        f'<link rel="canonical" href="{SITE_URL}/en/services/{slug}">',
    )
    return Response(content=page, media_type="text/html; charset=utf-8")


# ---------- Articles (content factory) ----------

ARTICLES_DIR = ROOT_DIR / "content" / "articles"
_SLUG_RE = re.compile(r"^[a-z0-9-]{1,80}$")
BUSINESS_LABELS = {
    "trade": ("国际贸易争议", "Trade"),
    "recovery": ("诉讼与债务追收", "Recovery"),
    "legacy": ("继承与家族资产", "Legacy"),
}


def _parse_article_file(path: Path) -> dict | None:
    """Parse one article: YAML-ish frontmatter + zh body + `<!-- EN -->` + en body."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    _, frontmatter, body = text.split("---", 2)
    meta = {}
    for line in frontmatter.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    parts = body.split("\n<!-- EN -->\n", 1)
    meta["slug"] = path.parent.name
    return {
        "meta": meta,
        "zh": parts[0].strip(),
        "en": parts[1].strip() if len(parts) > 1 else "",
    }


def _load_articles() -> list[dict]:
    """All articles sorted by date descending; invalid entries are skipped."""
    articles = []
    if ARTICLES_DIR.is_dir():
        for path in sorted(ARTICLES_DIR.glob("*/index.md")):
            try:
                article = _parse_article_file(path)
            except (OSError, ValueError):
                continue
            if article and _SLUG_RE.match(article["meta"].get("slug", "")):
                articles.append(article)
    return sorted(articles, key=lambda a: a["meta"].get("date", ""), reverse=True)


def _article_html(article: dict) -> tuple[str, str]:
    """Render zh/en markdown bodies to HTML (extra enables tables, etc.)."""
    render = lambda text: markdown.markdown(text, extensions=["extra", "sane_lists"])
    return render(article["zh"]), render(article["en"])


_ARTICLE_INDEX_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="跨境法律实务指南：国际贸易争议、债务追收、继承与家族资产。深远国际律师事务所律师团队撰写。">
  <link rel="canonical" href="{site_url}/articles">
  <link rel="alternate" hreflang="zh-CN" href="{site_url}/articles">
  <link rel="alternate" hreflang="en" href="{site_url}/en/articles">
  <link rel="alternate" hreflang="x-default" href="{site_url}/articles">
  {ga_tag}
  <title>法律专栏 | Shenyuan International 深远(国际)律师事务所</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{ --ink:#172433; --muted:#627180; --paper:#f6f3ed; --surface:#fffdf9; --line:#d9d9d2; --teal:#0d6c6b; --teal-deep:#084d50; --orange:#d76e39; --gold:#b08d57; --max:1060px;
      --serif:"Playfair Display","Noto Serif SC",Georgia,"Songti SC","SimSun",serif; --sans:"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; color:var(--ink); background:var(--paper); font-family:var(--sans); line-height:1.65; }}
    a {{ color:inherit; text-decoration:none; }} button {{ font:inherit; cursor:pointer; }}
    h1,h2,h3,p {{ margin:0; }} h1,h2,h3 {{ font-family:var(--serif); }}
    .wrap {{ width:min(calc(100% - 40px), var(--max)); margin:0 auto; }}
    .topbar {{ background:var(--teal-deep); color:#f5f2ec; }}
    .topbar .wrap {{ display:flex; justify-content:space-between; align-items:center; min-height:66px; gap:18px; }}
    .topbar .brand {{ display:inline-flex; align-items:center; gap:10px; color:#fff; font-size:14px; font-weight:700; }}
    .brand-mark {{ display:grid; place-items:center; width:30px; height:30px; color:var(--teal-deep); background:#f7f2e9; border-radius:7px; font-family:var(--serif); font-size:16px; }}
    .topbar .nav-links {{ display:flex; align-items:center; gap:18px; font-size:13px; }}
    .topbar a {{ color:rgba(255,255,255,.85); }} .topbar a:hover {{ color:#fff; }}
    .lang-switch {{ padding:7px 10px; color:rgba(255,255,255,.85); background:transparent; border:1px solid rgba(255,255,255,.3); border-radius:6px; font-size:12px; }}
    .page-head {{ padding:64px 0 30px; }}
    .eyebrow {{ display:inline-flex; align-items:center; gap:8px; color:var(--gold); font-size:12px; font-weight:700; letter-spacing:.13em; text-transform:uppercase; }}
    .eyebrow::before {{ content:""; width:24px; height:2px; background:var(--gold); }}
    h1 {{ margin:16px 0 0; font-size:clamp(30px,4vw,44px); line-height:1.15; }}
    .page-head p {{ margin-top:14px; color:var(--muted); font-size:15px; max-width:720px; }}
    .cards {{ display:grid; gap:18px; padding-bottom:80px; }}
    .a-card {{ padding:28px; background:var(--surface); border:1px solid var(--line); border-radius:var(--radius,10px); transition:transform .2s ease, box-shadow .2s ease; }}
    .a-card:hover {{ transform:translateY(-3px); box-shadow:0 20px 50px rgba(20,33,44,.11); }}
    .a-meta {{ display:flex; align-items:center; gap:12px; font-size:12px; color:var(--muted); }}
    .a-tag {{ display:inline-block; padding:3px 10px; color:var(--teal-deep); background:#deefea; border-radius:12px; font-weight:700; }}
    .a-card h2 {{ margin-top:14px; font-size:21px; line-height:1.3; }}
    .a-card h2:hover {{ color:var(--teal); }}
    .a-card p {{ margin-top:10px; color:var(--muted); font-size:14px; }}
    .a-more {{ display:inline-block; margin-top:14px; color:var(--teal); font-size:13px; font-weight:800; }}
    footer {{ background:#15232d; color:rgba(255,255,255,.72); font-size:12px; padding:22px 0; text-align:center; }}
    footer a {{ color:rgba(255,255,255,.85); }}
    @media (max-width:720px) {{ .topbar .wrap {{ min-height:60px; }} }}
  </style>
</head>
<body>
  <div class="topbar"><div class="wrap">
    <a class="brand" href="/"><span class="brand-mark">深</span><span>Shenyuan International</span></a>
    <div class="nav-links">
      <a href="/" data-zh="返回首页" data-en="Home">返回首页</a>
      <button class="lang-switch" type="button" id="langToggle" aria-label="切换语言">EN / 中</button>
    </div>
  </div></div>
  <div class="wrap page-head">
    <div class="eyebrow" data-zh="法律专栏" data-en="Legal insights">法律专栏</div>
    <h1 data-zh="跨境法律实务指南" data-en="Cross-border legal guides">跨境法律实务指南</h1>
    <p data-zh="由深远国际律师事务所团队撰写，围绕国际贸易争议、债务追收、继承与家族资产，用中文讲清跨境法律实务。" data-en="Written by the Shenyuan International team on international trade disputes, debt recovery, inheritance, and family assets — cross-border legal practice in plain language.">由深远国际律师事务所团队撰写，围绕国际贸易争议、债务追收、继承与家族资产，用中文讲清跨境法律实务。</p>
  </div>
  <div class="wrap cards">{cards}</div>
  <footer>© 2026 Shenyuan International · 深远(国际)律师事务所 · <a href="/">返回首页</a></footer>
  <script>
    (function () {{
      var currentLang = "zh";
      document.getElementById("langToggle").addEventListener("click", function () {{
        currentLang = currentLang === "zh" ? "en" : "zh";
        document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
        document.title = currentLang === "zh" ? "法律专栏 | Shenyuan International 深远(国际)律师事务所" : "Legal Insights | Shenyuan International";
        document.querySelectorAll("[data-zh][data-en]").forEach(function (node) {{
          node.textContent = currentLang === "zh" ? node.getAttribute("data-zh") : node.getAttribute("data-en");
        }});
      }});
    }}());
  </script>
</body>
</html>"""

_ARTICLE_PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description_zh}">
  <link rel="canonical" href="{site_url}/articles/{slug}">
  <link rel="alternate" hreflang="zh-CN" href="{site_url}/articles/{slug}">
  <link rel="alternate" hreflang="en" href="{site_url}/en/articles/{slug}">
  <link rel="alternate" hreflang="x-default" href="{site_url}/articles/{slug}">
  {ga_tag}
  <title>{title_zh} | Shenyuan International</title>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{json_title_zh}",
    "description": "{json_desc_zh}",
    "datePublished": "{json_date}",
    "inLanguage": "zh-CN",
    "author": {{ "@type": "Organization", "name": "Shenyuan International 深远(国际)律师事务所" }},
    "publisher": {{ "@type": "Organization", "name": "Shenyuan International", "url": "{json_site_url}" }},
    "mainEntityOfPage": "{json_site_url}/articles/{json_slug}"
  }}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{ --ink:#172433; --muted:#627180; --paper:#f6f3ed; --surface:#fffdf9; --line:#d9d9d2; --teal:#0d6c6b; --teal-deep:#084d50; --orange:#d76e39; --gold:#b08d57; --max:820px;
      --serif:"Playfair Display","Noto Serif SC",Georgia,"Songti SC","SimSun",serif; --sans:"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; color:var(--ink); background:var(--paper); font-family:var(--sans); line-height:1.75; }}
    a {{ color:inherit; text-decoration:none; }} button {{ font:inherit; cursor:pointer; }}
    h1,h2,h3,p {{ margin:0; }} h1,h2,h3 {{ font-family:var(--serif); }}
    .wrap {{ width:min(calc(100% - 40px), var(--max)); margin:0 auto; }}
    .topbar {{ background:var(--teal-deep); color:#f5f2ec; }}
    .topbar .wrap {{ display:flex; justify-content:space-between; align-items:center; min-height:66px; gap:18px; }}
    .topbar .brand {{ display:inline-flex; align-items:center; gap:10px; color:#fff; font-size:14px; font-weight:700; }}
    .brand-mark {{ display:grid; place-items:center; width:30px; height:30px; color:var(--teal-deep); background:#f7f2e9; border-radius:7px; font-family:var(--serif); font-size:16px; }}
    .topbar .nav-links {{ display:flex; align-items:center; gap:18px; font-size:13px; }}
    .topbar a {{ color:rgba(255,255,255,.85); }} .topbar a:hover {{ color:#fff; }}
    .lang-switch {{ padding:7px 10px; color:rgba(255,255,255,.85); background:transparent; border:1px solid rgba(255,255,255,.3); border-radius:6px; font-size:12px; }}
    .article-head {{ padding:56px 0 26px; }}
    .a-meta {{ display:flex; align-items:center; gap:12px; font-size:12px; color:var(--muted); }}
    .a-tag {{ display:inline-block; padding:3px 10px; color:var(--teal-deep); background:#deefea; border-radius:12px; font-weight:700; }}
    h1 {{ margin-top:16px; font-size:clamp(28px,3.8vw,40px); line-height:1.25; }}
    .a-desc {{ margin-top:14px; color:var(--muted); font-size:15px; }}
    .article-body {{ padding-bottom:34px; }}
    .article-body h2 {{ margin:38px 0 14px; font-size:24px; }}
    .article-body h3 {{ margin:26px 0 10px; font-size:18px; color:var(--teal-deep); }}
    .article-body p {{ margin-top:12px; font-size:15px; color:#334454; }}
    .article-body ul, .article-body ol {{ margin:12px 0 0; padding-left:22px; color:#334454; font-size:15px; }}
    .article-body li {{ margin-top:6px; }}
    .article-body table {{ width:100%; margin:16px 0 4px; border-collapse:collapse; font-size:13.5px; background:var(--surface); }}
    .article-body th, .article-body td {{ border:1px solid var(--line); padding:9px 12px; text-align:left; vertical-align:top; }}
    .article-body th {{ background:var(--cream); color:var(--teal-deep); font-weight:700; }}
    .article-body strong {{ color:var(--ink); }}
    .article-body a {{ color:var(--teal); font-weight:700; border-bottom:1px solid rgba(13,108,107,.3); }}
    .article-body hr {{ margin:30px 0 0; border:0; border-top:1px solid var(--line); }}
    .cta-box {{ margin:10px 0 70px; padding:30px; text-align:center; background:var(--teal-deep); border-radius:12px; color:#f5f2ec; }}
    .cta-box h2 {{ font-size:22px; }}
    .cta-box p {{ margin-top:10px; color:rgba(255,255,255,.75); font-size:14px; }}
    .button {{ display:inline-flex; align-items:center; gap:9px; margin-top:18px; min-height:46px; padding:0 24px; color:#fff; background:var(--orange); border-radius:8px; font-size:14px; font-weight:700; }}
    .button:hover {{ background:#c85d2e; }}
    footer {{ background:#15232d; color:rgba(255,255,255,.72); font-size:12px; padding:22px 0; text-align:center; line-height:1.7; }}
    footer a {{ color:rgba(255,255,255,.85); }}
    @media (max-width:720px) {{ .topbar .wrap {{ min-height:60px; }} .article-body table {{ font-size:12.5px; }} }}
  </style>
</head>
<body>
  <div class="topbar"><div class="wrap">
    <a class="brand" href="/"><span class="brand-mark">深</span><span>Shenyuan International</span></a>
    <div class="nav-links">
      <a href="/" data-zh="返回首页" data-en="Home">返回首页</a>
      <a href="/articles" data-zh="全部文章" data-en="All articles">全部文章</a>
      <button class="lang-switch" type="button" id="langToggle" aria-label="切换语言">EN / 中</button>
    </div>
  </div></div>
  <div class="wrap article-head">
    <div class="a-meta"><span class="a-tag">{tag_zh}</span><span data-zh="发布于" data-en="Published">发布于</span><span>{date}</span></div>
    <h1 data-zh="{title_zh}" data-en="{title_en}">{title_zh}</h1>
    <p class="a-desc" data-zh="{description_zh}" data-en="{description_en}">{description_zh}</p>
  </div>
  <div class="wrap article-body" id="bodyZh">{body_zh}</div>
  <div class="wrap article-body" id="bodyEn" hidden>{body_en}</div>
  <div class="wrap cta-box">
    <h2 data-zh="您的案件需要评估？" data-en="Need your case assessed?">您的案件需要评估？</h2>
    <p data-zh="提交基本信息，我们会判断时效、证据与可行路径——免费评估，不承诺结果。" data-en="Share the basics and we will review the limitation period, evidence, and viable paths — free, honest, no promised outcomes.">提交基本信息，我们会判断时效、证据与可行路径——免费评估，不承诺结果。</p>
    <a class="button" href="/#intake" data-zh="免费法律咨询 →" data-en="Free legal consultation →">免费法律咨询 →</a>
  </div>
  <footer>© 2026 Shenyuan International · 深远(国际)律师事务所 · <a href="/articles" data-zh="法律专栏" data-en="Legal insights">法律专栏</a></footer>
  <script>
    (function () {{
      var currentLang = "zh";
      var zhTitle = {title_zh!r};
      var enTitle = {title_en!r};
      var bodyZh = document.getElementById("bodyZh");
      var bodyEn = document.getElementById("bodyEn");
      document.getElementById("langToggle").addEventListener("click", function () {{
        currentLang = currentLang === "zh" ? "en" : "zh";
        document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
        document.title = currentLang === "zh" ? zhTitle + " | Shenyuan International" : enTitle + " | Shenyuan International";
        bodyZh.hidden = currentLang !== "zh";
        bodyEn.hidden = currentLang !== "en";
        document.querySelectorAll("[data-zh][data-en]").forEach(function (node) {{
          node.textContent = currentLang === "zh" ? node.getAttribute("data-zh") : node.getAttribute("data-en");
        }});
      }});
    }}());
  </script>
</body>
</html>"""


def _articles_index_html() -> str:
    cards = []
    for article in _load_articles():
        meta = article["meta"]
        biz = BUSINESS_LABELS.get(meta.get("business", ""), ("法律专栏", "Legal"))
        cards.append(
            '<article class="a-card">'
            f'<div class="a-meta"><span class="a-tag">{biz[0]}</span><span>{html.escape(meta.get("date", ""))}</span></div>'
            f'<a href="/articles/{html.escape(meta["slug"])}"><h2 data-zh="{html.escape(meta.get("title_zh", ""))}" data-en="{html.escape(meta.get("title_en", ""))}">{html.escape(meta.get("title_zh", ""))}</h2></a>'
            f'<p data-zh="{html.escape(meta.get("description_zh", ""))}" data-en="{html.escape(meta.get("description_en", ""))}">{html.escape(meta.get("description_zh", ""))}</p>'
            f'<a class="a-more" href="/articles/{html.escape(meta["slug"])}" data-zh="阅读全文 →" data-en="Read more →">阅读全文 →</a>'
            "</article>"
        )
    return _ARTICLE_INDEX_TEMPLATE.format(
        site_url=SITE_URL, cards="\n".join(cards), ga_tag=_ga_tag()
    )


@app.get("/articles", include_in_schema=False)
def articles_index() -> Response:
    return Response(content=_articles_index_html(), media_type="text/html; charset=utf-8")


@app.api_route("/en/articles", methods=["GET", "HEAD"], include_in_schema=False)
def articles_index_en() -> Response:
    page = _en_variant(_articles_index_html())
    page = _swap_meta(
        page,
        "meta name=\"description\"",
        "Cross-border legal guides: international trade disputes, debt recovery, "
        "inheritance and family assets — written by the Shenyuan International team.",
    )
    page = page.replace(
        f'<link rel="canonical" href="{SITE_URL}/articles">',
        f'<link rel="canonical" href="{SITE_URL}/en/articles">',
    )
    return Response(content=page, media_type="text/html; charset=utf-8")


@app.get("/articles/{slug}", include_in_schema=False)
def article_page(slug: str) -> Response:
    if not _SLUG_RE.match(slug):
        raise HTTPException(status_code=404, detail="Not found")
    article = next((a for a in _load_articles() if a["meta"]["slug"] == slug), None)
    if article is None:
        raise HTTPException(status_code=404, detail="Not found")
    body_zh, body_en = _article_html(article)
    meta = article["meta"]
    biz = BUSINESS_LABELS.get(meta.get("business", ""), ("法律专栏", "Legal"))
    content = _ARTICLE_PAGE_TEMPLATE.format(
        site_url=SITE_URL,
        slug=html.escape(meta["slug"]),
        tag_zh=biz[0],
        date=html.escape(meta.get("date", "")),
        title_zh=html.escape(meta.get("title_zh", "")),
        title_en=html.escape(meta.get("title_en", "")),
        description_zh=html.escape(meta.get("description_zh", "")),
        description_en=html.escape(meta.get("description_en", "")),
        body_zh=body_zh,
        body_en=body_en,
        ga_tag=_ga_tag(),
        # Raw (unescaped) values for the JSON-LD block — escaping would corrupt JSON.
        json_title_zh=meta.get("title_zh", ""),
        json_desc_zh=meta.get("description_zh", ""),
        json_date=meta.get("date", ""),
        json_slug=meta["slug"],
        json_site_url=SITE_URL,
    )
    return Response(content=content, media_type="text/html; charset=utf-8")


@app.api_route("/en/articles/{slug}", methods=["GET", "HEAD"], include_in_schema=False)
def article_page_en(slug: str) -> Response:
    if not _SLUG_RE.match(slug):
        raise HTTPException(status_code=404, detail="Not found")
    article = next((a for a in _load_articles() if a["meta"]["slug"] == slug), None)
    if article is None:
        raise HTTPException(status_code=404, detail="Not found")
    # Reuse the zh page and flip it to English (text swap + body visibility).
    page = _en_variant(bytes(article_page(slug).body).decode("utf-8"))
    meta = article["meta"]
    page = _swap_meta(page, "meta name=\"description\"", html.escape(meta.get("description_en", "")))
    page = re.sub(
        r"(<title>)[^<]*(</title>)",
        rf"\g<1>{html.escape(meta.get('title_en', ''))} | Shenyuan International\g<2>",
        page,
        count=1,
    )
    page = page.replace(
        f'<link rel="canonical" href="{SITE_URL}/articles/{slug}">',
        f'<link rel="canonical" href="{SITE_URL}/en/articles/{slug}">',
    )
    page = page.replace(
        '<div class="wrap article-body" id="bodyZh">',
        '<div class="wrap article-body" id="bodyZh" hidden>',
    )
    page = page.replace(
        '<div class="wrap article-body" id="bodyEn" hidden>',
        '<div class="wrap article-body" id="bodyEn">',
    )
    # Keep the BlogPosting JSON-LD in sync with the English variant.
    zh_title = meta.get("title_zh", "")
    en_title = meta.get("title_en", "")
    if zh_title:
        page = page.replace(f'"headline": "{zh_title}"', f'"headline": "{en_title}"')
    page = page.replace('"inLanguage": "zh-CN"', '"inLanguage": "en"')
    return Response(content=page, media_type="text/html; charset=utf-8")


@app.get("/wechat-qrcode.png", include_in_schema=False)
def wechat_qrcode() -> FileResponse:
    """Real WeChat QR code for the contact section and success modal."""
    path = ROOT_DIR / "wechat-qrcode.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="QR code image not found")
    return FileResponse(path, media_type="image/png")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/admin", include_in_schema=False)
def admin_page() -> FileResponse:
    """Admin dashboard shell. The page itself is unauthenticated; every API
    call it makes carries the bearer token from the login form."""
    return FileResponse(ROOT_DIR / "admin.html")


@app.get("/admin/api/intakes", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_list_intakes(
    request: Request,
    status: str | None = None,
    q: str | None = None,
    limit: int = 100,
) -> list[dict]:
    _require_admin(request)
    if limit < 1 or limit > 500:
        limit = 100

    where, params = [], []
    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=422, detail="Invalid status")
        where.append("status = ?")
        params.append(status)
    if q:
        where.append(
            "(name LIKE ? OR email LIKE ? OR phone LIKE ? OR matter LIKE ? OR summary LIKE ?)"
        )
        params.extend([f"%{q}%"] * 5)

    sql = "SELECT * FROM intakes"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with db_connection() as connection:
        rows = connection.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


@app.get("/admin/api/stats", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_stats(request: Request) -> dict:
    """Conversion analytics: intakes vs homepage views (lightweight)."""
    _require_admin(request)

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()

    with db_connection() as connection:
        intakes_total = connection.execute("SELECT COUNT(*) FROM intakes").fetchone()[0]
        intakes_today = connection.execute(
            "SELECT COUNT(*) FROM intakes WHERE created_at >= ?", (today_start,)
        ).fetchone()[0]
        intakes_week = connection.execute(
            "SELECT COUNT(*) FROM intakes WHERE created_at >= ?", (week_ago,)
        ).fetchone()[0]
        views_total = connection.execute("SELECT COUNT(*) FROM page_views").fetchone()[0]
        views_today = connection.execute(
            "SELECT COUNT(*) FROM page_views WHERE viewed_at >= ?", (today_start,)
        ).fetchone()[0]
        by_status = {
            row["status"]: row["c"]
            for row in connection.execute(
                "SELECT status, COUNT(*) c FROM intakes GROUP BY status"
            )
        }
        by_matter = [
            dict(row)
            for row in connection.execute(
                """
                SELECT matter, COUNT(*) c FROM intakes
                GROUP BY matter ORDER BY c DESC LIMIT 8
                """
            )
        ]

    conversion = round(intakes_today / views_today * 100, 2) if views_today else 0.0
    return {
        "intakes_total": intakes_total,
        "intakes_today": intakes_today,
        "intakes_week": intakes_week,
        "views_total": views_total,
        "views_today": views_today,
        "conversion_today_pct": conversion,
        "by_status": by_status,
        "by_matter": by_matter,
    }


@app.patch("/admin/api/intakes/{intake_id}", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_update_intake(
    intake_id: int, payload: AdminIntakeUpdate, request: Request
) -> dict:
    _require_admin(request)

    updates, params = [], []
    if payload.status is not None:
        updates.append("status = ?")
        params.append(payload.status)
    if payload.note is not None:
        updates.append("note = ?")
        params.append(payload.note)
    if not updates:
        raise HTTPException(status_code=400, detail="Nothing to update")

    params.append(intake_id)
    with db_connection() as connection:
        connection.execute(
            f"UPDATE intakes SET {', '.join(updates)} WHERE id = ?", params
        )
        row = connection.execute(
            "SELECT * FROM intakes WHERE id = ?", (intake_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Intake not found")

    log_audit(_client_ip(request), "update", f"intake {intake_id}: {', '.join(updates)}")
    return dict(row)


@app.get("/admin/intakes.csv", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def export_intakes(
    request: Request, status: str | None = None, q: str | None = None
) -> Response:
    """Export all intakes as CSV. Protected by the ADMIN_TOKEN bearer token."""
    _require_admin(request)

    where, params = [], []
    if status:
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=422, detail="Invalid status")
        where.append("status = ?")
        params.append(status)
    if q:
        where.append(
            "(name LIKE ? OR email LIKE ? OR phone LIKE ? OR matter LIKE ? OR summary LIKE ?)"
        )
        params.extend([f"%{q}%"] * 5)
    sql = """
        SELECT id, created_at, name, email, phone, country_or_region,
               matter, summary, language, status, note, consent_at
        FROM intakes
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC"

    with db_connection() as connection:
        rows = connection.execute(sql, params).fetchall()
    log_audit(
        _client_ip(request),
        "export",
        f"intakes.csv rows={len(rows)} status={status or '-'} q={q or '-'}",
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id", "created_at", "name", "email", "phone",
            "country_or_region", "matter", "summary", "language",
            "status", "note", "consent_at",
        ]
    )
    writer.writerows(rows)
    # UTF-8 BOM so Excel opens the Chinese content correctly.
    content = "\ufeff" + buffer.getvalue()
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="intakes.csv"'},
    )


@app.post("/api/intakes", response_model=IntakeCreated, status_code=201)
@limiter.limit(INTAKE_RATE_LIMIT)
def create_intake(
    payload: IntakeCreate,
    request: Request,
    background_tasks: BackgroundTasks,
) -> IntakeCreated:
    """Save an intake form submission.

    Sync def on purpose: FastAPI runs sync endpoints in a threadpool, so the
    blocking SQLite write never stalls the async event loop. A webhook
    notification for the new lead runs as a background task after the
    response is sent.
    """
    created_at = datetime.now(timezone.utc).isoformat()
    user_agent = request.headers.get("user-agent")
    consent_at = created_at if payload.consent else None

    try:
        with db_connection() as connection:
            # Duplicate detection: same email or phone within the window.
            cutoff = (
                datetime.now(timezone.utc) - timedelta(hours=_dedupe_window_hours())
            ).isoformat()
            duplicate = connection.execute(
                """
                SELECT id FROM intakes
                WHERE created_at > ?
                  AND (email = ? OR (phone IS NOT NULL AND ? IS NOT NULL AND phone = ?))
                LIMIT 1
                """,
                (cutoff, payload.email, payload.phone, payload.phone),
            ).fetchone()
            if duplicate:
                raise HTTPException(
                    status_code=409,
                    detail="已收到过您的信息，请勿重复提交 / We already received your submission",
                )
            cursor = connection.execute(
                """
                INSERT INTO intakes (
                    name, email, phone, matter, summary, country_or_region,
                    language, user_agent, created_at, status, note, consent_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', NULL, ?)
                """,
                (
                    payload.name,
                    payload.email,
                    payload.phone,
                    payload.matter,
                    payload.summary,
                    payload.country,
                    payload.language,
                    user_agent,
                    created_at,
                    consent_at,
                ),
            )
    except sqlite3.Error:
        logger.exception("Failed to save intake for %s", payload.email)
        raise HTTPException(status_code=500, detail="Failed to save consultation") from None

    background_tasks.add_task(
        _send_intake_notification,
        {
            "name": payload.name,
            "email": payload.email,
            "phone": payload.phone,
            "country": payload.country,
            "matter": payload.matter,
            "summary": payload.summary,
            "language": payload.language,
            "created_at": created_at,
        },
    )
    background_tasks.add_task(
        _send_auto_reply,
        {
            "name": payload.name,
            "email": payload.email,
            "matter": payload.matter,
            "summary": payload.summary,
        },
    )

    return IntakeCreated(id=cursor.lastrowid, status="created", created_at=created_at)


@app.get("/admin/api/intakes/{intake_id}/files", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_list_files(intake_id: int, request: Request) -> list[dict]:
    _require_admin(request)
    with db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, original_name, size, content_type, uploaded_at
            FROM files WHERE intake_id = ?
            ORDER BY id
            """,
            (intake_id,),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/admin/api/intakes/{intake_id}/files/{file_id}/download", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_download_file(intake_id: int, file_id: int, request: Request) -> FileResponse:
    _require_admin(request)
    with db_connection() as connection:
        row = connection.execute(
            "SELECT * FROM files WHERE id = ? AND intake_id = ?", (file_id, intake_id)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="File not found")
    path = FILES_DIR / str(intake_id) / row["stored_name"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File missing on disk")
    logger.info("Admin downloaded file %d (intake %d) from %s", file_id, intake_id, _client_ip(request))
    return FileResponse(path, filename=row["original_name"])
