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
import threading
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
SCHEMA_VERSION = 6

# Public base URL used for canonical/OG/sitemap links. Override in prod.
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000").rstrip("/")


def _ga_tag() -> str:
    """Analytics bundle injected into HTML heads: GA4 + optional Meta Pixel
    + optional Baidu analytics (each gated by its env ID; empty = disabled).

    Read per-request (like the admin token) so tests can toggle it via the
    environment.
    """
    parts = []
    ga_id = os.environ.get("GA_MEASUREMENT_ID", "").strip()
    if ga_id:
        parts.append(
            '<script async src="https://www.googletagmanager.com/gtag/js?id={id}"></script>\n'
            '<script>window.dataLayer=window.dataLayer||[];'
            "function gtag(){{dataLayer.push(arguments);}}"
            "gtag('js',new Date());gtag('config','{id}');</script>".format(id=ga_id)
        )
    pixel_id = os.environ.get("META_PIXEL_ID", "").strip()
    if pixel_id:
        parts.append(
            "<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?"
            "n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;"
            "n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
            "t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,"
            "document,'script','https://connect.facebook.net/en_US/fbevents.js');"
            "fbq('init','{id}');fbq('track','PageView');</script>".format(id=pixel_id)
        )
        parts.append(
            '<noscript><img height="1" width="1" style="display:none" '
            'src="https://www.facebook.com/tr?id={id}&ev=PageView&noscript=1"/></noscript>'.format(id=pixel_id)
        )
    baidu_id = os.environ.get("BAIDU_ANALYTICS_ID", "").strip()
    if baidu_id:
        parts.append(
            "<script>var _hmt=_hmt||[];(function(){{var hm=document.createElement('script');"
            "hm.src='https://hm.baidu.com/hm.js?{id}';var s=document.getElementsByTagName"
            "('script')[0];s.parentNode.insertBefore(hm,s);}})();</script>".format(id=baidu_id)
        )
    return "\n".join(parts)


def _cookie_banner() -> str:
    """GDPR-style cookie consent banner (zh/en, remembers the choice)."""
    return (
        '<div id="cookieBanner" role="dialog" aria-label="Cookie consent" '
        'style="position:fixed;left:16px;right:16px;bottom:16px;z-index:99999;'
        "max-width:560px;margin:0 auto;background:#172433;color:#f5f2ec;"
        'border-radius:10px;padding:14px 18px;font-size:13px;line-height:1.6;'
        "box-shadow:0 12px 32px rgba(20,33,44,.3);display:none;"
        'font-family:\'Segoe UI\',\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">'
        '<span data-zh="本网站使用 Cookie 与统计工具（Google Analytics）分析访问流量，以改进服务。'
        '继续访问即表示您同意。详见" data-en="This site uses cookies and analytics (Google '
        'Analytics) to understand traffic and improve our service. By continuing you consent. '
        'See">本网站使用 Cookie 与统计工具分析访问流量。详见</span> '
        '<a href="/privacy" style="color:#e8b26a;text-decoration:underline" '
        'data-zh="隐私政策" data-en="Privacy Policy">隐私政策</a>'
        '<div style="margin-top:10px;display:flex;gap:10px">'
        '<button type="button" id="cookieOk" style="padding:6px 18px;border:0;border-radius:6px;'
        'background:#d76e39;color:#fff;font-weight:700;cursor:pointer" data-zh="同意" '
        'data-en="Accept">同意</button>'
        '<button type="button" id="cookieNo" style="padding:6px 18px;border:1px solid '
        'rgba(255,255,255,.4);background:transparent;color:#f5f2ec;border-radius:6px;'
        'cursor:pointer" data-zh="拒绝" data-en="Decline">拒绝</button>'
        '</div></div>'
        "<script>(function(){try{var c=localStorage.getItem('sy_cookie');"
        "if(c)return;var b=document.getElementById('cookieBanner');b.style.display='block';"
        "document.getElementById('cookieOk').onclick=function(){localStorage.setItem('sy_cookie','ok');"
        "b.style.display='none';};document.getElementById('cookieNo').onclick=function(){"
        "localStorage.setItem('sy_cookie','no');b.style.display='none';};}catch(e){}})();</script>"
    )

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
                email TEXT,
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
    # v8: CRM Agent — lead score and last-touch timestamp.
    if "score" not in columns:
        connection.execute("ALTER TABLE intakes ADD COLUMN score INTEGER NOT NULL DEFAULT 0")
    if "updated_at" not in columns:
        connection.execute("ALTER TABLE intakes ADD COLUMN updated_at TEXT")
    # v9: lead acquisition source (UTM utm_source captured by the frontend).
    if "source" not in columns:
        connection.execute("ALTER TABLE intakes ADD COLUMN source TEXT")
    # v10: email becomes optional (phone is the required channel) — rebuild so
    # the email column is nullable (SQLite cannot alter column constraints).
    cols_info = {r[1]: r for r in connection.execute("PRAGMA table_info(intakes)")}
    if cols_info.get("email") and cols_info["email"][3]:
        connection.execute("ALTER TABLE intakes RENAME TO intakes_old")
        connection.execute(
            """
            CREATE TABLE intakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                matter TEXT NOT NULL,
                summary TEXT NOT NULL,
                country_or_region TEXT,
                language TEXT NOT NULL DEFAULT 'zh',
                user_agent TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                note TEXT,
                consent_at TEXT,
                score INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT,
                source TEXT
            )
            """
        )
        connection.execute(
            """
            INSERT INTO intakes (
                id, name, email, phone, matter, summary, country_or_region,
                language, user_agent, created_at, status, note, consent_at,
                score, updated_at, source
            )
            SELECT
                id, name, email, phone, matter, summary, country_or_region,
                language, user_agent, created_at, status, note, consent_at,
                score, updated_at, source
            FROM intakes_old
            """
        )
        connection.execute("DROP TABLE intakes_old")
        logger.info("Rebuilt intakes table: email is now optional")

    logger.info("Migrating intakes schema to version %d", SCHEMA_VERSION)
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # CRM Agent: daemon thread that periodically nudges about overdue leads.
    stop_event = threading.Event()
    thread = threading.Thread(
        target=_crm_reminder_loop, args=(stop_event,), daemon=True, name="crm-agent"
    )
    thread.start()
    try:
        yield
    finally:
        stop_event.set()


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


def _not_found_html() -> str:
    """Branded 404 page (instead of the default JSON) with recovery links."""
    ga_tag = _ga_tag()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, follow">
  <title>404 · 页面未找到 | Shenyuan International</title>
  {ga_tag}
  <style>
    :root {{ --ink:#172433; --muted:#627180; --paper:#f6f3ed; --teal:#0d6c6b; --teal-deep:#084d50; --serif:"Playfair Display","Noto Serif SC",Georgia,serif; --sans:"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--sans); min-height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px; text-align:center; }}
    h1 {{ font-family:var(--serif); font-size:64px; margin:0; color:var(--teal-deep); }}
    p {{ color:var(--muted); max-width:420px; }}
    a {{ color:var(--teal); font-weight:700; text-decoration:none; margin:0 8px; }}
    .links {{ margin-top:20px; }}
  </style>
</head>
<body>
  <h1>404</h1>
  <p data-zh="您访问的页面不存在或已移动。" data-en="The page you are looking for does not exist or has moved.">您访问的页面不存在或已移动。</p>
  <div class="links">
    <a href="/" data-zh="返回首页" data-en="Home">返回首页</a>
    <a href="/services/trade" data-zh="服务" data-en="Services">服务</a>
    <a href="/articles" data-zh="法律专栏" data-en="Articles">法律专栏</a>
    <a href="/countries" data-zh="国家专页" data-en="Countries">国家专页</a>
  </div>
</body>
</html>"""


@app.exception_handler(404)
def _not_found_handler(request: Request, exc) -> Response:
    """HTML 404 for browser requests, JSON for API-ish paths."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return Response(content=_not_found_html(), status_code=404, media_type="text/html; charset=utf-8")
    return JSONResponse(status_code=404, content={"detail": "Not found"})


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
    if not intake.get("email"):
        # No email address — nothing to send to (phone-only leads).
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
    # Email is optional — phone is the required contact channel.
    email: Annotated[EmailStr | None, Field(max_length=254)] = None
    matter: Annotated[str, Field(min_length=1, max_length=80)]
    summary: Annotated[str, Field(min_length=1, max_length=2000)]
    phone: Annotated[str, Field(min_length=1, max_length=60)]
    country: Annotated[str | None, Field(max_length=80)] = None
    language: Annotated[str, Field(pattern="^(zh|en)$")] = "zh"
    # Acquisition channel (utm_source), captured client-side from the URL.
    source: Annotated[str | None, Field(max_length=60)] = None
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


# --- AI 咨询助手 (chat intake) ---

_MATTER_LABEL_BY_KEY = {
    "trade": "国际贸易争议",
    "recovery": "诉讼与债务追收",
    "legacy": "继承与家族资产纠纷",
    "unsure": "不确定，希望先沟通",
}

_LEGACY_KW = ("继承", "遗产", "遗嘱", "房产", "去世", "亲属", "失联", "家族", "probate", "inheritance", "estate", "will")
_RECOVERY_KW = ("追收", "欠款", "欠债", "催收", "拖欠", "未付", "不付", "拒付", "讨债", "催款", "要账", "未还", "赖账", "跑路", "执行", "判决", "仲裁", "裁决", "欺诈", "诈骗", "资产", "collection", "debt", "judgment", "enforce", "fraud", "asset", "recover")
_TRADE_KW = ("合同", "订单", "货物", "供应商", "发货", "物流", "海关", "信用证", "贸易", "代理", "经销", "采购", "发票", "货款", "违约", "trade", "contract", "supplier", "shipment", "customs", "invoice", "breach")


def _classify_matter(summary: str, user_choice: str = "") -> str:
    """Keyword triage of a chat intake into trade / recovery / legacy / unsure.

    Only the free-text summary is keyword-scanned (the raw user_choice string
    is never appended to it — "recovery"/"trade" would match their own
    keyword lists). Priority: legacy > recovery > trade. The visitor's
    explicit choice is the fallback, then "unsure".
    """
    chosen = "unsure"
    if user_choice:
        for key, label in _MATTER_LABEL_BY_KEY.items():
            if user_choice == key or user_choice == label or key in user_choice:
                chosen = key
                break
    text = (summary or "").lower()
    for keywords, key in (
        (_LEGACY_KW, "legacy"),
        (_RECOVERY_KW, "recovery"),
        (_TRADE_KW, "trade"),
    ):
        if any(k in text for k in keywords):
            return key
    return chosen


def _split_contact(contact: str) -> tuple[str, str]:
    """Return (email, phone/wechat) — anything containing '@' counts as email."""
    contact = contact.strip()
    if "@" in contact:
        return contact, ""
    return "", contact


class ChatIntakeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=80)]
    contact: Annotated[str, Field(min_length=2, max_length=120)]
    matter: Annotated[str, Field(max_length=80)] = ""
    summary: Annotated[str, Field(min_length=1, max_length=3000)]
    parties: Annotated[str, Field(max_length=500)] = ""
    amount: Annotated[str, Field(max_length=200)] = ""
    timeline: Annotated[str, Field(max_length=200)] = ""
    evidence: Annotated[str, Field(max_length=500)] = ""
    goal: Annotated[str, Field(max_length=300)] = ""
    country: Annotated[str | None, Field(max_length=120)] = None
    language: Annotated[str, Field(pattern="^(zh|en)$")] = "zh"
    consent: bool = False
    transcript: Annotated[str | None, Field(max_length=6000)] = None
    # Acquisition channel (utm_source), captured client-side from the URL.
    source: Annotated[str | None, Field(max_length=60)] = None


# --- CRM Agent: lead scoring, SLA tracking, overdue reminders --------------

_URGENT_KW = (
    "紧急", "尽快", "马上", "立刻", "明天", "本周", "期限", "到期", "转移",
    "查封", "冻结", "跑路", "失联", "urgent", "deadline", "freeze", "asap",
)
_AMOUNT_HIGH_KW = ("50万以上", "百万", "千万", "100万", "500k", "million", "over ¥500k")
_AMOUNT_MID_KW = ("5-50万", "50k-500k", "¥50k–500k")
_NO_EVIDENCE_KW = ("暂无", "没有", "暂时没有", "none yet")


def _crm_first_sla_hours() -> int:
    """SLA: a 'new' lead should be contacted within this many hours."""
    return max(1, int(os.environ.get("CRM_FIRST_SLA_HOURS", "24")))


def _crm_progress_sla_days() -> int:
    """SLA: a 'contacted' lead should reach a decision/in_progress in days."""
    return max(1, int(os.environ.get("CRM_PROGRESS_SLA_DAYS", "7")))


def _crm_reminder_interval_hours() -> int:
    """How often the background CRM agent checks for overdue leads."""
    return max(1, int(os.environ.get("CRM_REMINDER_INTERVAL_HOURS", "12")))


def _lead_score(
    name: str,
    summary: str,
    matter: str,
    amount: str = "",
    evidence: str = "",
    email: str = "",
    phone: str = "",
) -> int:
    """Heuristic 0-100 lead score for opportunity triage.

    Signals: amount size (+30/+15), urgency keywords (+20), practice area
    (recovery/legacy +10, trade +5), evidence on file (+5), complete contact
    (+5). Base 30 so every lead is at least visible. Capped at 100.
    """
    text = f"{summary or ''} {amount or ''} {matter or ''} {evidence or ''}".lower()
    score = 30
    if any(k in text for k in _AMOUNT_HIGH_KW):
        score += 30
    elif any(k in text for k in _AMOUNT_MID_KW):
        score += 15
    if any(k in text for k in _URGENT_KW):
        score += 20
    if any(k in matter or "" for k in ("继承", "家族", "Inheritance", "Estate")):
        score += 10
    elif any(k in matter or "" for k in ("债务", "诉讼", "Litigation", "debt")):
        score += 10
    elif any(k in matter or "" for k in ("贸易", "Trade")):
        score += 5
    if evidence and not any(k in evidence.lower() for k in _NO_EVIDENCE_KW):
        score += 5
    if email:
        score += 5
    return min(score, 100)


def _overdue_leads() -> list[dict]:
    """Leads whose SLA has lapsed: 'new' untouched for first-SLA hours, or
    'contacted' with no movement for progress-SLA days. Ordered by score desc."""
    now = datetime.now(timezone.utc)
    first_cutoff = (now - timedelta(hours=_crm_first_sla_hours())).isoformat()
    progress_cutoff = (now - timedelta(days=_crm_progress_sla_days())).isoformat()
    with db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, email, phone, matter, summary, score, status,
                   created_at, updated_at
            FROM intakes
            WHERE (status = 'new' AND COALESCE(updated_at, created_at) < ?)
               OR (status = 'contacted' AND COALESCE(updated_at, created_at) < ?)
            ORDER BY score DESC, COALESCE(updated_at, created_at) ASC
            """,
            (first_cutoff, progress_cutoff),
        ).fetchall()
    leads = []
    for row in rows:
        lead = dict(row)
        last_touch = lead.get("updated_at") or lead["created_at"]
        try:
            lead["stale_hours"] = round(
                (now - datetime.fromisoformat(last_touch)).total_seconds() / 3600, 1
            )
        except (ValueError, TypeError):
            lead["stale_hours"] = 0
        leads.append(lead)
    return leads


def _stale_leads(days: int = 30, limit: int = 10) -> list[dict]:
    """Churn-risk leads: not closed and untouched for N days (流失预警)."""
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days)).isoformat()
    with db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, email, phone, matter, summary, score, status,
                   created_at, updated_at
            FROM intakes
            WHERE status != 'closed' AND COALESCE(updated_at, created_at) < ?
            ORDER BY score DESC, COALESCE(updated_at, created_at) ASC
            LIMIT ?
            """,
            (cutoff, limit),
        ).fetchall()
    leads = []
    for row in rows:
        lead = dict(row)
        last_touch = lead.get("updated_at") or lead["created_at"]
        try:
            lead["stale_days"] = round(
                (now - datetime.fromisoformat(last_touch)).total_seconds() / 86400, 1
            )
        except (ValueError, TypeError):
            lead["stale_days"] = days
        leads.append(lead)
    return leads


def _post_webhook(url: str, text: str) -> None:
    """Best-effort push to the configured notification webhook (WeCom-style JSON)."""
    payload = json.dumps({"msgtype": "text", "text": {"content": text}}).encode("utf-8")
    request = urllib.request.Request(url, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("User-Agent", "shenyuan-law-firm/1.0")
    request.data = payload
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read()
        try:
            result = json.loads(body.decode("utf-8", errors="replace"))
            if result.get("errcode"):
                logger.error("Webhook rejected: %s", result.get("errmsg", result))
        except ValueError:
            pass
    except Exception:
        logger.exception("Failed to send webhook notification")


def _send_crm_reminder(leads: list[dict]) -> None:
    """Post a digest of overdue leads to the notification webhook (fire-and-forget)."""
    url = _notify_webhook_url()
    if not url or not leads:
        return
    new_count = sum(1 for lead in leads if lead["status"] == "new")
    stalled = len(leads) - new_count
    lines = [
        "【CRM 跟进提醒】",
        f"逾期未跟进线索：{len(leads)} 条（新线索未联系 {new_count}，已联系未推进 {stalled}）",
        "",
    ]
    for lead in leads[:5]:
        contact = lead["email"] or lead["phone"] or "-"
        lines.append(
            f"#{lead['id']} [{lead['status']}] {lead['name']} · {lead['matter']} · {contact}"
            f" · 评分 {lead['score']} · 逾期 {lead.get('stale_hours', 0)}h"
        )
    if len(leads) > 5:
        lines.append(f"… 共 {len(leads)} 条，其余见后台")
    lines.append("后台处理：/admin")
    _post_webhook(url, "\n".join(lines))


def _crm_reminder_loop(stop_event: threading.Event) -> None:
    """Background agent: periodically check overdue leads and notify. Daemon."""
    interval = _crm_reminder_interval_hours() * 3600
    while not stop_event.wait(interval):
        try:
            leads = _overdue_leads()
            if leads:
                _send_crm_reminder(leads)
                logger.info("CRM reminder sent for %d overdue leads", len(leads))
            stale = _stale_leads()
            if stale:
                url = _notify_webhook_url()
                if url:
                    lines = [
                        "【CRM 流失预警】",
                        f"以下 {len(stale)} 条线索超过 30 天未跟进，存在流失风险：",
                        "",
                    ] + [
                        f"- #{l['id']} {l.get('name', '?')} · {l.get('matter', '')[:16]} · "
                        f"评分{l.get('score') or 0} · {l['stale_days']} 天未动"
                        for l in stale
                    ]
                    _post_webhook(url, "\n".join(lines))
                    logger.info("CRM churn alert sent for %d stale leads", len(stale))
        except Exception:
            logger.exception("CRM reminder loop iteration failed")


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
    og_image = OG_IMAGE
    crumbs_html, crumbs_jsonld = _crumbs([
        ("首页", f"{SITE_URL}/"),
        (zh_title[:20], f"{SITE_URL}/services/{svc['slug']}"),
    ])
    cookie_banner = _cookie_banner()
    related = _related_html(
        [a for a in _related_articles({"slug": "__svc__", "business": svc["slug"]})],
        base="/articles",
    )
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
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{zh_title} | Shenyuan International">
  <meta name="twitter:description" content="{zh_intro}">
  <meta name="twitter:image" content="{og_image}">
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
  {crumbs_jsonld}
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
    .crumbs {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; font-size:12.5px; color:var(--muted); padding:22px 0 0; }}
    .crumbs a {{ color:var(--teal); }}
    .crumb-sep {{ color:#b9c2c9; }}
    .related {{ margin:40px 0 10px; padding:20px 24px; background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); }}
    .related h3 {{ font-size:16px; margin:0 0 12px; color:var(--teal-deep); }}
    .related ul {{ margin:0; padding-left:0; list-style:none; }}
    .related li {{ margin:8px 0; }}
    .related a {{ color:var(--teal); font-weight:600; font-size:14px; }}
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
    {crumbs_html}
    <div class="number" data-zh="服务 · {number}" data-en="SERVICE · {number}">服务 · {number}</div>
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

  {related}

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
  <div id="chat-widget-root"></div>
  <script src="/static/chat.js" defer></script>
  {cookie_banner}
</body>
</html>"""


def _whatsapp_button() -> str:
    """WhatsApp quick-consult link (shown only when WHATSAPP_NUMBER is set)."""
    number = os.environ.get("WHATSAPP_NUMBER", "").strip()
    if not number:
        return ""
    digits = "".join(ch for ch in number if ch.isdigit())
    if not digits:
        return ""
    href = f"https://wa.me/{digits}"
    return (
        '<div class="contact-options wa-options">'
        '<a class="wa-btn" href="' + href + '" target="_blank" rel="noopener">'
        '<strong data-zh="WhatsApp 快速咨询" data-en="Quick WhatsApp consult">WhatsApp 快速咨询</strong>'
        '<p data-zh="海外客户可通过 WhatsApp 直接留言，24 小时内回复。" data-en="Overseas clients can message us on WhatsApp — we reply within 24 hours.">'
        "海外客户可通过 WhatsApp 直接留言，24 小时内回复。</p></a></div>"
    )


@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
def read_index() -> Response:
    _record_page_view()
    html = (ROOT_DIR / "index.html").read_text(encoding="utf-8")
    html = (
        html.replace("{{SITE_URL}}", SITE_URL)
        .replace("{{GA_TAG}}", _ga_tag())
        .replace("{{WHATSAPP_BUTTON}}", _whatsapp_button())
        .replace("{{COOKIE_BANNER}}", _cookie_banner())
    )
    return Response(
        content=html,
        media_type="text/html; charset=utf-8",
    )


@app.api_route("/en", methods=["GET", "HEAD"], include_in_schema=False)
@app.api_route("/en/", methods=["GET", "HEAD"], include_in_schema=False)
def read_index_en() -> Response:
    _record_page_view()
    html = (ROOT_DIR / "index.html").read_text(encoding="utf-8")
    html = (
        html.replace("{{SITE_URL}}", SITE_URL)
        .replace("{{GA_TAG}}", _ga_tag())
        .replace("{{WHATSAPP_BUTTON}}", _whatsapp_button())
        .replace("{{COOKIE_BANNER}}", _cookie_banner())
    )
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
        content=(
            "# Shenyuan International — shenyuanlegal.com\n"
            "User-agent: *\n"
            "Allow: /\n"
            "\n"
            "# AI / LLM crawlers are explicitly welcome (GEO):\n"
            "User-agent: GPTBot\n"
            "Allow: /\n"
            "User-agent: ChatGPT-User\n"
            "Allow: /\n"
            "User-agent: ClaudeBot\n"
            "Allow: /\n"
            "User-agent: PerplexityBot\n"
            "Allow: /\n"
            "User-agent: Google-Extended\n"
            "Allow: /\n"
            "\n"
            "# Chinese search engines:\n"
            "User-agent: Baiduspider\n"
            "Allow: /\n"
            "User-agent: Sogou web spider\n"
            "Allow: /\n"
            "User-agent: 360Spider\n"
            "Allow: /\n"
            "\n"
            f"Sitemap: {SITE_URL}/sitemap.xml\n"
            f"LLMtxt: {SITE_URL}/llms.txt\n"
        ),
        media_type="text/plain",
    )


@app.api_route("/llms.txt", methods=["GET", "HEAD"], include_in_schema=False)
def llms_txt() -> Response:
    """llms.txt (llmstxt.org): a compact, LLM-readable site map. GEO best practice —
    gives ChatGPT/Claude/Perplexity a curated entry point instead of crawling raw HTML."""
    articles = sorted(_load_articles(), key=lambda a: a["meta"].get("date", ""), reverse=True)
    lines = [
        "# Shenyuan International 深远(国际)律师事务所",
        "",
        "> Cross-border dispute resolution & family asset protection for Chinese businesses "
        "and families. Bilingual (中文/EN). Trade disputes, debt recovery, judgment "
        "enforcement, asset tracing, cross-border inheritance. Local counsel network in "
        "30+ jurisdictions. Free initial assessment.",
        "",
        "## Services",
        f"- [Trade disputes](/services/trade) — 国际贸易争议：跨境合同、货款追收",
        f"- [Debt recovery](/services/recovery) — 诉讼与债务追收：判决执行、资产调查",
        f"- [Inheritance & family assets](/services/legacy) — 继承与家族资产：跨境继承、遗嘱、信托",
        "",
        "## Country pages",
    ]
    for slug, c in COUNTRIES.items():
        lines.append(f"- [{c['name_en']} ({c['name_zh']})](/countries/{slug}) — {c['en_title']}")
    lines.append("")
    lines.append("## Legal guides (articles)")
    for a in articles[:25]:
        meta = a["meta"]
        lines.append(f"- [{meta.get('title_en', meta.get('title_zh', '?'))}](/articles/{meta['slug']}) — {meta.get('description_en', '')[:160]}")
    lines.append("")
    lines.append("## Contact")
    lines.append("- Website: /")
    lines.append("- Intake form: /#contact — free initial assessment, 24h response")
    lines.append("- AI assistant: chat widget on every page (English/中文)")
    return Response(content="\n".join(lines) + "\n", media_type="text/plain; charset=utf-8")


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
    # Language-aware links (e.g. homepage region chips): point href at the /en/ URL.
    html = re.sub(
        r'(href=")([^"]*)(" data-zh-href=")([^"]*)(" data-en-href=")([^"]*)(")',
        lambda m: f"{m.group(1)}{m.group(6)}{m.group(3)}{m.group(4)}{m.group(5)}{m.group(6)}{m.group(7)}",
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
    entries = []
    # Static pages carry no reliable modification date — omit lastmod
    # (Google prefers an accurate lastmod over a guessed one).
    for u in (
        f"{SITE_URL}/", f"{SITE_URL}/articles", f"{SITE_URL}/en/", f"{SITE_URL}/en/articles",
        f"{SITE_URL}/countries", f"{SITE_URL}/en/countries",
        f"{SITE_URL}/about", f"{SITE_URL}/en/about",
        f"{SITE_URL}/fees", f"{SITE_URL}/en/fees",
        f"{SITE_URL}/privacy", f"{SITE_URL}/en/privacy",
    ):
        entries.append(f"  <url><loc>{u}</loc></url>\n")
    for slug in COUNTRIES:
        entries.append(f"  <url><loc>{SITE_URL}/countries/{slug}</loc></url>\n")
        entries.append(f"  <url><loc>{SITE_URL}/en/countries/{slug}</loc></url>\n")
    for slug in SERVICES:
        entries.append(f"  <url><loc>{SITE_URL}/services/{slug}</loc></url>\n")
        entries.append(f"  <url><loc>{SITE_URL}/en/services/{slug}</loc></url>\n")
    for a in _load_articles():
        date = a["meta"].get("date", "")
        for path in (f"/articles/{a['meta']['slug']}", f"/en/articles/{a['meta']['slug']}"):
            if date:
                entries.append(f"  <url><loc>{SITE_URL}{path}</loc><lastmod>{date}</lastmod></url>\n")
            else:
                entries.append(f"  <url><loc>{SITE_URL}{path}</loc></url>\n")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(entries)
        + "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@app.api_route("/services/{slug}", methods=["GET", "HEAD"], include_in_schema=False)
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
# Shared social-card image (OG + Twitter) for generated pages.
OG_IMAGE = "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1200&q=80"
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


def _related_articles(meta: dict, limit: int = 3) -> list[dict]:
    """Internal-link candidates: same business line first, then latest others."""
    biz_key = _business_key(meta.get("business", ""))
    others = [a for a in _load_articles() if a["meta"]["slug"] != meta["slug"]]
    same = [a for a in others if _business_key(a["meta"].get("business", "")) == biz_key]
    rest = [a for a in others if a not in same]
    same.sort(key=lambda a: a["meta"].get("date", ""), reverse=True)
    rest.sort(key=lambda a: a["meta"].get("date", ""), reverse=True)
    return (same + rest)[:limit]


def _related_html(articles: list[dict], base: str = "/articles") -> str:
    """Bilingual 'related reading' block (empty when no candidates)."""
    if not articles:
        return ""
    cards = []
    for a in articles:
        meta = a["meta"]
        slug = html.escape(meta["slug"])
        title_zh = html.escape(meta.get("title_zh", ""))
        title_en = html.escape(meta.get("title_en", ""))
        cards.append(
            f'<li><a href="{base}/{slug}" data-zh="{title_zh}" data-en="{title_en}">{title_zh}</a></li>'
        )
    return (
        '<div class="related"><h3 data-zh="延伸阅读" data-en="Related reading">延伸阅读</h3>'
        "<ul>" + "".join(cards) + "</ul></div>"
    )


def _crumbs(items: list[tuple[str, str]]) -> tuple[str, str]:
    """Visual breadcrumbs + BreadcrumbList JSON-LD. items = [(name_zh, url), ...]."""
    parts = []
    for i, (name_zh, url) in enumerate(items):
        safe_name = html.escape(name_zh)
        if i == len(items) - 1:
            parts.append(f'<span class="crumb" data-zh="{safe_name}" data-en="{safe_name}">{safe_name}</span>')
        else:
            parts.append(f'<a class="crumb" href="{url}" data-zh="{safe_name}" data-en="{safe_name}">{safe_name}</a>')
        if i < len(items) - 1:
            parts.append('<span class="crumb-sep">›</span>')
    crumbs_html = '<nav class="crumbs" aria-label="Breadcrumb">' + "".join(parts) + "</nav>"
    items_json = ",".join(
        f'{{"@type": "ListItem", "position": {i}, "name": "{html.escape(name)}", "item": "{url}"}}'
        for i, (name, url) in enumerate(items, start=1)
    )
    jsonld = (
        '<script type="application/ld+json">\n'
        '{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ['
        + items_json
        + "]}\n</script>"
    )
    return crumbs_html, jsonld


# ---------- Case Research Agent: knowledge base, search, memo drafts -------

_KB_DIR = ROOT_DIR / "legal_kb"

_MATTER_META = {
    "trade": {
        "label": "国际贸易争议",
        "next": [
            "核对合同与凭证：订单、提单、验收单、往来邮件——确认欠款金额与违约事实",
            "发正式催款函（模板见知识库 templates/demand-letter.md），保留送达凭证",
            "确认合同争议解决条款：优先仲裁（HKIAC/SIAC）优于诉讼（执行便利性）",
            "评估诉讼时效（中国法 3 年）与证据完整性，必要时申请财产保全",
        ],
    },
    "recovery": {
        "label": "诉讼与债务追收",
        "next": [
            "定位债务人资产：境内（股权/房产/存款）与境外（各国执行路径见知识库）",
            "判断执行路径：外国判决执行成功率低，评估在当地重新起诉",
            "如为仲裁裁决，确认纽约公约成员国与承认条件",
            "启动财产保全防止资产转移，同步评估时效与成本",
        ],
    },
    "legacy": {
        "label": "继承与家族资产",
        "next": [
            "按知识库 templates/probate-checklist.md 收集材料清单",
            "区分动产（死亡时经常居所地法）与不动产（所在地法）两条路径",
            "死亡证明等外国文件走海牙/领事认证 + 有资质翻译",
            "确认遗产税申报义务后再操作过户（美/英/德/日等国）",
        ],
    },
}


def _kb_search(query: str, top: int = 5) -> list[dict]:
    """Search the Case Research knowledge base (title hits weigh more)."""
    q = query.strip().lower()
    if not q or not _KB_DIR.exists():
        return []
    tokens = [t for t in re.split(r"[,\s，。、/]+", q) if len(t) >= 2]
    if not tokens:
        return []
    results = []
    for path in sorted(_KB_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = path.stem
        score = 0
        for t in tokens:
            tl = t.lower()
            if tl in title.lower():
                score += 3
            if tl in text.lower():
                score += 1
        if not score:
            continue
        snippet = next(
            (ln.strip()[:120] for ln in lines if any(t.lower() in ln.lower() for t in tokens)),
            (lines[0].strip()[:120] if lines else ""),
        )
        results.append(
            {
                "path": str(path.relative_to(_KB_DIR)),
                "title": title,
                "score": score,
                "snippet": snippet,
            }
        )
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top]


class ResearchMemoCreate(BaseModel):
    matter_type: Annotated[str, Field(pattern="^(trade|recovery|legacy)$")]
    facts: Annotated[str, Field(min_length=10, max_length=2000)]
    amount: Annotated[str, Field(max_length=200)] = ""
    country: Annotated[str | None, Field(max_length=120)] = None


def _research_memo(payload: ResearchMemoCreate) -> dict:
    """Rule-based initial memo draft: links KB hits + per-line next steps."""
    meta = _MATTER_META[payload.matter_type]
    hits = _kb_search(f"{payload.facts} {payload.country or ''} {meta['label']}", top=4)
    return {
        "matter_type": payload.matter_type,
        "label": meta["label"],
        "facts": payload.facts.strip(),
        "amount": payload.amount.strip(),
        "country": payload.country.strip() if payload.country else "",
        "kb_hits": hits,
        "next_steps": meta["next"],
        "disclaimer": "本备忘录由 Case Research Agent 依据内部知识库自动生成，仅供内部研究参考，不构成法律意见；对外使用前须经执业律师复核签字。",
    }


@app.get("/admin/api/research/search", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_research_search(request: Request, q: str = "", top: int = 5) -> list[dict]:
    _require_admin(request)
    results = _kb_search(q, top=max(1, min(top, 20)))
    log_audit(request.client.host if request.client else "", "research.search", q[:120])
    return results


@app.post("/admin/api/research/memo", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_research_memo(payload: ResearchMemoCreate, request: Request) -> dict:
    _require_admin(request)
    memo = _research_memo(payload)
    log_audit(
        request.client.host if request.client else "",
        "research.memo",
        f"{payload.matter_type} :: {payload.facts[:120]}",
    )
    return memo


@app.get("/admin/research", include_in_schema=False)
def admin_research_page() -> FileResponse:
    return FileResponse(ROOT_DIR / "admin_research.html", media_type="text/html; charset=utf-8")


# ---------- Trust pages: about / fees / privacy (bilingual static) ----------

_STATIC_PAGES: dict[str, dict] = {
    "about": {
        "title_zh": "关于我们",
        "title_en": "About Us",
        "sections": [
            (
                "律所定位",
                "Who we are",
                "深远国际律师事务所（Shenyuan International）专注于跨境争议解决与家族资产保护：国际贸易争议、债务追收、判决与裁决执行、跨境继承与遗嘱规划。团队中英双语工作，服务中国大陆、港澳台及海外华人客户。",
                "Shenyuan International focuses on cross-border dispute resolution and family asset protection: trade disputes, debt recovery, judgment and award enforcement, and cross-border inheritance and estate planning. Our team works bilingually in Chinese and English, serving clients across China, Hong Kong, Macau, Taiwan, and the overseas Chinese diaspora.",
            ),
            (
                "全球合作网络",
                "Global network",
                "我们与 30 多个国家和地区的当地执业律所保持合作，境外法律程序通过与当地执业律所合作提供，确保程序符合当地法律要求。",
                "We work with locally licensed counsel in 30+ jurisdictions. Foreign legal proceedings are conducted through locally licensed counsel to ensure compliance with local law.",
            ),
            (
                "律师团队",
                "Our team",
                "团队成员简介正在整理中，将陆续发布。",
                "Team profiles are being finalized and will be published soon.",
            ),
            (
                "执业承诺",
                "Our commitments",
                "客户信息严格保密，受律师-客户保密特权保护；评估与报价透明；我们诚实评估案件可行性，不承诺任何结果。",
                "Client information is kept strictly confidential and protected by attorney-client privilege. Our assessments and fees are transparent, and we are honest about case prospects — we never promise results.",
            ),
        ],
    },
    "fees": {
        "title_zh": "收费说明",
        "title_en": "Fees",
        "sections": [
            (
                "初步评估免费",
                "Free initial assessment",
                "通过官网表单或 AI 咨询助手提交基本信息后，我们会进行初步评估，判断事项类型、时效与可行路径。初步评估不收费，不产生任何委托关系。",
                "After you share the basics via our form or AI assistant, we conduct an initial assessment of the matter type, limitation period, and viable paths. The initial assessment is free and creates no attorney-client relationship.",
            ),
            (
                "分阶段透明报价",
                "Transparent, stage-based fees",
                "正式委托按阶段报价：策略评估、证据梳理、函件与谈判、仲裁/诉讼程序、执行。每阶段开始前书面确认费用与范围，无隐藏费用。",
                "Engagement is quoted by stage: strategy review, evidence organization, letters and negotiation, arbitration/litigation, and enforcement. Fees and scope are confirmed in writing before each stage begins; no hidden charges.",
            ),
            (
                "境外程序费用",
                "Foreign proceedings",
                "涉及境外法域时，当地律师费由合作律所按其标准收取，我们会在委托前提供费用预估区间，并全程协调沟通。",
                "Where foreign jurisdictions are involved, local counsel fees are charged by the cooperating firm at its own rates. We provide an estimated range before engagement and coordinate throughout.",
            ),
            (
                "诚实承诺",
                "Honest promise",
                "我们不对案件结果作任何承诺。费用与周期以书面协议为准。",
                "We make no promises regarding outcomes. Fees and timelines are governed by the written engagement agreement.",
            ),
        ],
    },
    "privacy": {
        "title_zh": "隐私政策",
        "title_en": "Privacy Policy",
        "sections": [
            (
                "我们收集的信息",
                "Information we collect",
                "咨询表单与 AI 咨询助手收集您主动提供的联系信息（姓名、电话、邮箱）与案件描述；网站使用统计工具（Google Analytics）收集匿名访问数据。",
                "Our consultation form and AI assistant collect contact details you provide (name, phone, email) and your matter description. Anonymous traffic data is collected via analytics (Google Analytics).",
            ),
            (
                "信息用途",
                "How we use it",
                "仅用于：评估您的咨询、由律师团队与您联系、改进网站服务。我们不会向第三方出售您的信息。",
                "Information is used solely to assess your inquiry, enable our team to contact you, and improve our website. We never sell your data to third parties.",
            ),
            (
                "合规与保护",
                "Compliance & protection",
                "我们遵守《个人信息保护法》（PIPL）与 GDPR 的相关要求；客户信息受律师-客户保密特权保护，仅限办理案件所必需的人员接触。",
                "We comply with PIPL and, where applicable, GDPR. Client information is protected by attorney-client privilege and accessible only to those necessary to handle the matter.",
            ),
            (
                "Cookie 说明",
                "Cookies",
                "本站使用 Cookie 与统计工具分析流量。继续使用本网站即表示您同意；您可随时清除浏览器 Cookie。",
                "This site uses cookies and analytics tools to understand traffic. By continuing to use the site you consent; you may clear cookies in your browser at any time.",
            ),
            (
                "联系我们",
                "Contact us",
                "如对隐私政策有任何疑问，可通过网站表单或微信（ShenyuanLegal）与我们联系。",
                "For any privacy questions, contact us via the website form or WeChat (ShenyuanLegal).",
            ),
        ],
    },
}


def _render_static_page(slug: str, en: bool = False) -> Response:
    page = _STATIC_PAGES[slug]
    title = page["title_en"] if en else page["title_zh"]
    lang = "en" if en else "zh-CN"
    sections = ""
    for h2_zh, h2_en, p_zh, p_en in page["sections"]:
        h2 = h2_en if en else h2_zh
        p = p_en if en else p_zh
        sections += (
            f'<section class="sp-sec"><h2 data-zh="{h2_zh}" data-en="{h2_en}">{h2}</h2>'
            f'<p data-zh="{p_zh}" data-en="{p_en}">{p}</p></section>'
        )
    crumbs_html, crumbs_jsonld = _crumbs(
        [("首页", f"{SITE_URL}/"), (title, f"{SITE_URL}/{slug}")]
    )
    html = f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{title} | Shenyuan International">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="{SITE_URL}/{slug}">
  <link rel="alternate" hreflang="zh-CN" href="{SITE_URL}/{slug}">
  <link rel="alternate" hreflang="en" href="{SITE_URL}/en/{slug}">
  <link rel="alternate" hreflang="x-default" href="{SITE_URL}/{slug}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title} | Shenyuan International">
  <meta property="og:url" content="{SITE_URL}/{slug}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta name="twitter:card" content="summary_large_image">
  {crumbs_jsonld}
  {_ga_tag()}
  <title>{title} | Shenyuan International</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --ink:#172433; --muted:#627180; --paper:#f6f3ed; --surface:#fffdf9;
      --line:#d9d9d2; --teal:#0d6c6b; --teal-deep:#084d50; --orange:#d76e39;
      --gold:#b08d57; --max:1060px;
      --serif:"Playfair Display","Noto Serif SC",Georgia,"Songti SC","SimSun",serif;
      --sans:"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; color:var(--ink); background:var(--paper); font-family:var(--sans); line-height:1.7; }}
    a {{ color:inherit; text-decoration:none; }}
    h1,h2,h3,p {{ margin:0; }}
    h1,h2,h3 {{ font-family:var(--serif); }}
    .wrap {{ width:min(calc(100% - 40px), var(--max)); margin:0 auto; }}
    .topbar {{ background:var(--teal-deep); color:#f5f2ec; }}
    .topbar .wrap {{ display:flex; justify-content:space-between; align-items:center; min-height:64px; gap:18px; }}
    .topbar .brand {{ display:inline-flex; align-items:center; gap:10px; color:#fff; font-weight:700; font-size:14px; }}
    .brand-mark {{ width:34px;height:34px;display:inline-flex;align-items:center;justify-content:center;background:var(--gold);color:#fff;border-radius:8px;font-family:var(--serif);font-weight:700; }}
    .nav-links {{ display:flex; align-items:center; gap:18px; font-size:13.5px; }}
    .nav-links a {{ color:rgba(255,255,255,.85); }}
    .nav-links a:hover {{ color:#fff; }}
    .crumbs {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; font-size:12.5px; color:var(--muted); padding:26px 0 0; }}
    .crumbs a {{ color:var(--teal); }}
    .crumb-sep {{ color:#b9c2c9; }}
    .sp-head {{ padding:40px 0 8px; }}
    .sp-head h1 {{ font-size:clamp(28px, 4vw, 42px); line-height:1.15; }}
    .sp-body {{ padding:18px 0 70px; }}
    .sp-sec {{ padding:22px 0; border-bottom:1px solid var(--line); }}
    .sp-sec:last-child {{ border-bottom:0; }}
    .sp-sec h2 {{ font-size:19px; color:var(--teal-deep); margin-bottom:8px; }}
    .sp-sec p {{ font-size:14.5px; color:#334454; max-width:760px; }}
    footer {{ background:#15232d; color:rgba(255,255,255,.72); font-size:12px; padding:24px 0; text-align:center; line-height:2; }}
    footer a {{ color:rgba(255,255,255,.85); margin:0 8px; }}
    .lang-switch {{ padding:7px 10px; color:rgba(255,255,255,.85); background:transparent; border:1px solid rgba(255,255,255,.3); border-radius:6px; font-size:12px; cursor:pointer; }}
    @media (max-width:720px) {{ .nav-links {{ gap:10px; font-size:12px; }} .topbar .wrap {{ min-height:56px; }} }}
  </style>
</head>
<body>
  <div class="topbar"><div class="wrap">
    <a class="brand" href="/"><span class="brand-mark">深</span><span>Shenyuan International</span></a>
    <div class="nav-links">
      <a href="/" data-zh="首页" data-en="Home">首页</a>
      <a href="/countries" data-zh="国家专页" data-en="Countries">国家专页</a>
      <a href="/articles" data-zh="法律专栏" data-en="Articles">法律专栏</a>
      <button class="lang-switch" type="button" id="langToggle" aria-label="切换语言">EN / 中</button>
    </div>
  </div></div>
  {crumbs_html}
  <div class="wrap sp-head"><h1 data-zh="{page['title_zh']}" data-en="{page['title_en']}">{title}</h1></div>
  <div class="wrap sp-body">{sections}</div>
  <footer>
    © 2026 Shenyuan International · 深远(国际)律师事务所
    <div>
      <a href="/about" data-zh="关于我们" data-en="About Us">关于我们</a>
      <a href="/fees" data-zh="收费说明" data-en="Fees">收费说明</a>
      <a href="/privacy" data-zh="隐私政策" data-en="Privacy">隐私政策</a>
      <a href="/articles" data-zh="法律专栏" data-en="Articles">法律专栏</a>
    </div>
  </footer>
  <script>
    (function () {{
      var currentLang = "{'en' if en else 'zh'}";
      var zhTitle = {page['title_zh']!r};
      var enTitle = {page['title_en']!r};
      var toggle = document.getElementById("langToggle");
      toggle.addEventListener("click", function () {{
        window.location.href = currentLang === "zh" ? "/en/{slug}" : "/{slug}";
      }});
    }}());
  </script>
  {_cookie_banner()}
</body>
</html>"""
    return Response(content=html, media_type="text/html; charset=utf-8")


@app.api_route("/about", methods=["GET", "HEAD"], include_in_schema=False)
def static_about() -> Response:
    _record_page_view()
    return _render_static_page("about")


@app.api_route("/fees", methods=["GET", "HEAD"], include_in_schema=False)
def static_fees() -> Response:
    _record_page_view()
    return _render_static_page("fees")


@app.api_route("/privacy", methods=["GET", "HEAD"], include_in_schema=False)
def static_privacy() -> Response:
    _record_page_view()
    return _render_static_page("privacy")


@app.api_route("/en/about", methods=["GET", "HEAD"], include_in_schema=False)
def static_about_en() -> Response:
    _record_page_view()
    return _render_static_page("about", en=True)


@app.api_route("/en/fees", methods=["GET", "HEAD"], include_in_schema=False)
def static_fees_en() -> Response:
    _record_page_view()
    return _render_static_page("fees", en=True)


@app.api_route("/en/privacy", methods=["GET", "HEAD"], include_in_schema=False)
def static_privacy_en() -> Response:
    _record_page_view()
    return _render_static_page("privacy", en=True)


# ---------- Marketing Agent: collateral generator ---------------------------

_MARKETING_KW = {
    "trade": {
        "zh": ["国际贸易争议", "跨境合同", "外贸货款", "供应商违约", "国际仲裁"],
        "en": ["international trade dispute", "cross-border contract", "export payment", "supplier breach", "trade arbitration"],
        "tags": ["#国际贸易", "#外贸", "#跨境法律", "#货款追收", "#合同纠纷"],
        "tags_en": ["#TradeLaw", "#ExportRecovery", "#CrossBorder", "#InvoiceDisputes"],
        "hook": "外贸生意最怕的不是没订单，而是货发了、款收不回来。",
        "hook_en": "Your goods shipped. The invoice went unpaid. Here is what to do next.",
        "ads_zh": ["跨境贸易纠纷 专业律师", "外贸货款追收 律师团队", "国际合同审查 免费评估"],
        "ads_en": ["Cross-border trade lawyers", "Export debt recovery experts", "International contract review"],
    },
    "recovery": {
        "zh": ["债务追收", "欠款催收", "判决执行", "资产调查", "商业欺诈"],
        "en": ["debt collection", "judgment enforcement", "asset tracing", "commercial fraud", "arbitral award"],
        "tags": ["#债务追收", "#欠款催收", "#跨境维权", "#判决执行", "#法律"],
        "tags_en": ["#DebtRecovery", "#JudgmentEnforcement", "#AssetTracing", "#CommercialLaw"],
        "hook": "欠款拖一天，追回难一分。对方的耐心，就是你坏账的成本。",
        "hook_en": "Every day a debt goes unchased, the harder it becomes to recover.",
        "ads_zh": ["债务追收 专业律师", "欠款催收 律师出面", "判决执行 跨境协作"],
        "ads_en": ["Cross-border debt recovery", "Judgment enforcement China", "Asset tracing lawyers"],
    },
    "legacy": {
        "zh": ["跨境继承", "遗嘱效力", "房产继承", "遗产规划", "家族资产"],
        "en": ["cross-border inheritance", "probate", "estate planning", "family assets", "will dispute"],
        "tags": ["#跨境继承", "#遗嘱", "#遗产规划", "#家族资产", "#法律"],
        "tags_en": ["#Probate", "#EstatePlanning", "#Inheritance", "#FamilyAssets"],
        "hook": "海外亲人的遗产，拖着拖着，就成了别人的。",
        "hook_en": "Inheritance abroad doesn't wait — and neither should you.",
        "ads_zh": ["跨境继承 专业律师", "海外房产继承 咨询", "遗嘱规划 提前安排"],
        "ads_en": ["Cross-border inheritance", "Probate for Chinese heirs", "Estate planning lawyers"],
    },
    "unsure": {
        "zh": ["跨境法律咨询", "涉外纠纷", "律师咨询"],
        "en": ["cross-border legal advice", "international dispute", "legal consultation"],
        "tags": ["#跨境法律", "#法律咨询", "#律师"],
        "tags_en": ["#CrossBorder", "#LegalAdvice", "#BusinessLaw"],
        "hook": "跨境的法律问题，最贵的是“等等再说”。",
        "hook_en": "Cross-border legal issues cost the most when you wait.",
        "ads_zh": ["跨境法律 免费咨询", "涉外纠纷 专业律师"],
        "ads_en": ["Cross-border legal advice", "International dispute lawyers"],
    },
}


def _business_key(raw: str) -> str:
    if any(k in raw for k in ("继承", "家族", "legacy", "Inheritance")):
        return "legacy"
    if any(k in raw for k in ("债务", "诉讼", "追收", "recovery", "debt", "Litigation")):
        return "recovery"
    if any(k in raw for k in ("贸易", "trade", "Trade")):
        return "trade"
    return "unsure"


def _article_headings(md: str) -> list[str]:
    return [line.lstrip("# ").strip() for line in (md or "").splitlines() if line.startswith("## ")]


def _article_intro(md: str, max_chars: int = 200) -> str:
    out = []
    for line in (md or "").splitlines():
        if line.strip() and not line.startswith("#"):
            out.append(line.strip())
        if sum(len(x) for x in out) > max_chars:
            break
    return " ".join(out)[:max_chars]


def _marketing_bundle(article: dict | None, business: str, article_url: str) -> dict:
    """Deterministic marketing collateral for one article (or a business line).

    Sections: WeChat 公众号 titles, 小红书 note, video script (YouTube/视频号),
    Google Ads (headlines/descriptions/keywords/sitelinks), 朋友圈 copy,
    LinkedIn (EN), UTM-tagged links, and a weekly posting schedule. No LLM
    dependency: templates + article structure, so it is stable and testable.
    """
    meta = (article or {}).get("meta", {})
    biz = _MARKETING_KW.get(business, _MARKETING_KW["unsure"])
    title_zh = meta.get("title_zh", "") or biz["zh"][0]
    title_en = meta.get("title_en", "") or biz["en"][0]
    desc_zh = meta.get("description_zh", "") or _article_intro((article or {}).get("zh", ""))
    desc_en = meta.get("description_en", "") or _article_intro((article or {}).get("en", ""))
    points = _article_headings((article or {}).get("zh", ""))[:3] or [
        "第一步：梳理事实与证据", "第二步：确认时效与管辖", "第三步：谈判或诉讼路径",
    ]
    points_en = _article_headings((article or {}).get("en", ""))[:3] or points

    def utm(channel: str, medium: str) -> str:
        campaign = f"article-{meta.get('slug', business)}"
        return f"{article_url}?utm_source={channel}&utm_medium={medium}&utm_campaign={campaign}"

    moments = "\n".join([biz["hook"], f"——{title_zh}", "有类似问题？欢迎私信评估（免费，不承诺结果）。", f"🔗 {utm('wechat', 'moments')}"])

    # --- Facebook: story-style post (EN) + ad pack ---
    facebook_post_en = "\n".join(
        [biz["hook_en"]]
        + [f"📌 {title_en}"]
        + [f"• {p}" for p in points_en[:3]]
        + [
            "",
            "💬 Need help with a similar situation? We work with local counsel in 30+ jurisdictions — free initial assessment, no promise of results.",
            f"🔗 {utm('facebook', 'post')}",
            "#ShenyuanInternational " + " ".join(biz["tags_en"]),
        ]
    )
    facebook_ad = {
        "primary_text_en": f"{biz['hook_en']} We help Chinese businesses recover unpaid invoices and resolve disputes overseas — bilingual, with local counsel in 30+ jurisdictions. Free initial assessment.",
        "headline_en": f"{title_en[:38]}",
        "description_en": "Free assessment · Bilingual · 30+ countries",
        "cta": "Learn More",
        "targeting": {
            "geo": ["目标国家", "中国大陆（出海企业主）"],
            "age": "30-55",
            "interests": ["International trade", "Import/export business", "Small business owner", "Real estate investor"],
        },
    }

    # --- X: short tweets (EN + ZH) + thread ---
    # Keep tweets under 280: use "link in bio" (X profile link carries the UTM);
    # the full link goes in the last thread post.
    tweet_en = f"{biz['hook_en']} {title_en[:60]} — Free assessment, link in bio. {' '.join(biz['tags_en'][:2])}"
    tweet_zh = f"{biz['hook']} {title_zh[:40]} — 免费初步评估，链接见简介。{' '.join(biz['tags'][:2])}"
    thread_en = "\n\n".join(
        [
            f"1/ {biz['hook_en']}",
            f"2/ {desc_en[:200]}",
            f"3/ {points_en[0]}",
            f"4/ {points_en[1] if len(points_en) > 1 else ''}",
            f"5/ Free initial assessment — {utm('x', 'thread')} {' '.join(biz['tags_en'][:3])}",
        ]
    )

    # --- TikTok: 15-30s vertical script (ZH + EN) ---
    tiktok_script_zh = "\n".join(
        [
            f"[0-3s 钩子·竖屏大字] {biz['hook']}",
            f"[3-8s] 今天讲一个很多老板都遇到过的问题：{title_zh}",
            *[f"[{8 + i * 6}-{14 + i * 6}s] {p}。" for i, p in enumerate(points[:3])],
            "[结尾 3s] 评论区扣「咨询」，或点主页链接。跨境法律问题，交给专业的人。（不构成法律意见）",
        ]
    )
    tiktok_script_en = "\n".join(
        [
            f"[0-3s hook] {biz['hook_en']}",
            f"[3-8s] Today: {title_en}",
            *[f"[{8 + i * 6}-{14 + i * 6}s] {p}." for i, p in enumerate(points_en[:3])],
            "[end 3s] Comment 'help' or tap the link. Free initial assessment. (Not legal advice)",
        ]
    )
    tiktok = {
        "script_zh": tiktok_script_zh,
        "script_en": tiktok_script_en,
        "caption_en": f"{desc_en[:200]}\n\nFree assessment — link in bio.\n\n{' '.join(biz['tags_en'])} #ShenyuanInternational",
        "hashtags_zh": biz["tags"] + ["#跨境法律"],
        "on_screen_captions": "每句配屏幕字幕（大字白底黑边），hook 句用红色强调词",
        "sound": "建议原声口播（专业感强）或 trending business 类背景音；15-30s 竖屏 9:16",
        "cover": "封面大字：痛点问题（如『客户拖欠货款怎么办？』）+ 律师形象或场景图",
        "ad_spark": "投 Spark Ads 时用原生账号发帖加热度再投放，成本低于冷启动",
    }

    # --- 小红书增强：三种选题角度 ---
    xhs_angles = {
        "干货型": f"跨境法律干货｜{title_zh[:24]}",
        "避坑型": f"外贸人注意！{title_zh[:22]}（附避坑清单）",
        "故事型": f"客户被拖款 8 个月后，我们做了什么｜{title_zh[:18]}",
    }

    return {
        "slug": meta.get("slug", ""),
        "business": business,
        "title_zh": title_zh,
        "title_en": title_en,
        "article_url": article_url,
        "utm": {
            "wechat_mp": utm("wechat", "mp"),
            "xiaohongshu": utm("xiaohongshu", "note"),
            "video": utm("youtube", "video"),
            "ads": utm("google", "cpc"),
            "moments": utm("wechat", "moments"),
            "facebook": utm("facebook", "post"),
            "x": utm("x", "post"),
            "tiktok": utm("tiktok", "video"),
        },
        "wechat_mp": {
            "titles": [title_zh, f"律师提醒：{title_zh}", f"一文讲透：{title_zh}"],
            "summary": desc_zh,
        },
        "xiaohongshu": {
            "title": f"跨境法律干货｜{title_zh[:28]}",
            "angles": xhs_angles,
            "body": "\n".join(
                [biz["hook"], ""]
                + [f"✅ {p}" for p in points]
                + ["", "需要帮您评估？评论区留「咨询」或私信。", "👨‍⚖️ 深远国际 · 跨境争议解决与家族资产保护", "（本内容不构成法律意见）"]
            ),
            "tags": biz["tags"],
            "cover": "建议：纯色底 + 痛点大字标题 + 品牌角标",
        },
        "video": {
            "youtube_title": f"{title_zh}｜跨境法律 一分钟讲清",
            "script_zh": "\n".join(
                [f"[开头3秒] {biz['hook']}"]
                + [f"[正文] 今天用一分钟讲清楚：{title_zh}。"]
                + [f"{i + 1}) {p}。" for i, p in enumerate(points)]
                + ["[结尾] 有类似情况？评论区或私信「评估」，免费初步咨询。跨境法律问题，交给专业的人。"]
            ),
            "hashtags": biz["tags"] + ["#ShenyuanInternational"],
            "caption_en": f"{desc_en[:220]}\n\nNeed help? Free initial assessment — link below.\n\n#ShenyuanInternational",
        },
        "ads": {
            "headlines": (biz["ads_zh"] + ["免费初步评估", "中英双语 · 30+国家网络"])[:5],
            "descriptions": [
                "专注跨境争议解决与债务追收：中国律师+当地律所协作网络，免费初步评估，不承诺结果。",
                "国际贸易纠纷、判决执行、跨境继承一站处理。提交表单，24小时内响应。",
                "Overseas disputes? Bilingual team, 30+ jurisdictions. Free initial assessment.",
            ],
            "keywords": (biz["zh"] + biz["en"] + [title_zh[:20]])[:10],
            "final_url": article_url,
            "sitelinks": [
                f"{SITE_URL}/services/trade",
                f"{SITE_URL}/services/recovery",
                f"{SITE_URL}/services/legacy",
                f"{SITE_URL}/articles",
            ],
        },
        "moments": moments,
        "facebook": {
            "post_en": facebook_post_en,
            "ad": facebook_ad,
        },
        "x": {
            "tweet_en": tweet_en,
            "tweet_zh": tweet_zh,
            "thread_en": thread_en,
        },
        "tiktok": tiktok,
        "linkedin": {
            "headline": title_en,
            "body_en": "\n".join(
                [desc_en[:300], ""]
                + [f"• {p}" for p in points_en[:3]]
                + ["", "Free initial assessment — DM or comment. Shenyuan International: bilingual cross-border dispute resolution & family asset protection."]
            ),
        },
        "schedule": [
            ("周一", "公众号推文（标题+摘要，附文章链接）"),
            ("周二", "X 线程（英文专业向）+ 短推文 EN/ZH"),
            ("周三", "小红书笔记（干货型，标题/正文/标签/封面）"),
            ("周四", "Facebook 帖文（英文故事向）+ 广告组素材"),
            ("周五", "TikTok 短视频脚本（竖屏 15-30s，中英各一）"),
            ("周六", "小红书二发（避坑型/故事型换角度）"),
            ("周日", "朋友圈 + 社群文案"),
        ],
    }


@app.get("/admin/api/marketing/generate", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_marketing_generate(
    request: Request,
    slug: str | None = None,
    business: str | None = None,
) -> dict:
    """Marketing Agent: collateral for an article slug, or a business line."""
    _require_admin(request)
    article = None
    if slug:
        article = next((a for a in _load_articles() if a["meta"]["slug"] == slug), None)
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        biz = _business_key(article["meta"].get("business", ""))
        if business in _MARKETING_KW:
            biz = business
        url = f"{SITE_URL}/articles/{slug}"
    else:
        biz = business if business in _MARKETING_KW else "unsure"
        url = f"{SITE_URL}/services/{biz}" if biz in ("trade", "recovery", "legacy") else f"{SITE_URL}/articles"
    log_audit(
        request.client.host if request.client else "",
        "marketing.generate",
        f"{slug or business or 'unsure'} :: {biz}",
    )
    return _marketing_bundle(article, biz, url)


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
  <div id="chat-widget-root"></div>
  <script src="/static/chat.js" defer></script>
  {cookie_banner}
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
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Shenyuan International">
  <meta property="og:title" content="{title_zh} | Shenyuan International">
  <meta property="og:description" content="{description_zh}">
  <meta property="og:url" content="{site_url}/articles/{slug}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title_zh} | Shenyuan International">
  <meta name="twitter:description" content="{description_zh}">
  <meta name="twitter:image" content="{og_image}">
  {ga_tag}
  <title>{title_zh} | Shenyuan International</title>
  {breadcrumb_jsonld}
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{json_title_zh}",
    "description": "{json_desc_zh}",
    "datePublished": "{json_date}",
    "dateModified": "{json_date}",
    "image": "{og_image}",
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
    .cta-box {{ margin:10px auto 70px; padding:30px; text-align:center; background:var(--teal-deep); border-radius:12px; color:#f5f2ec; }}
    .cta-box h2 {{ font-size:22px; }}
    .cta-box p {{ margin-top:10px; color:rgba(255,255,255,.75); font-size:14px; }}
    .button {{ display:inline-flex; align-items:center; gap:9px; margin-top:18px; min-height:46px; padding:0 24px; color:#fff; background:var(--orange); border-radius:8px; font-size:14px; font-weight:700; }}
    .button:hover {{ background:#c85d2e; }}
    footer {{ background:#15232d; color:rgba(255,255,255,.72); font-size:12px; padding:22px 0; text-align:center; line-height:1.7; }}
    footer a {{ color:rgba(255,255,255,.85); }}
    .crumbs {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; font-size:12.5px; color:var(--muted); padding:22px 0 0; }}
    .crumbs a {{ color:var(--teal); }}
    .crumb-sep {{ color:#b9c2c9; }}
    .related {{ margin:30px 0 10px; padding:20px 24px; background:var(--surface); border:1px solid var(--line); border-radius:10px; }}
    .related h3 {{ font-size:16px; margin:0 0 12px; color:var(--teal-deep); }}
    .related ul {{ margin:0; padding-left:0; list-style:none; }}
    .related li {{ margin:8px 0; }}
    .related a {{ color:var(--teal); font-weight:600; font-size:14px; }}
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
  {crumbs}
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
  {related}
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
  <div id="chat-widget-root"></div>
  <script src="/static/chat.js" defer></script>
  {cookie_banner}
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
        site_url=SITE_URL, cards="\n".join(cards), ga_tag=_ga_tag(), cookie_banner=_cookie_banner()
    )


@app.api_route("/articles", methods=["GET", "HEAD"], include_in_schema=False)
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


@app.api_route("/articles/{slug}", methods=["GET", "HEAD"], include_in_schema=False)
def article_page(slug: str) -> Response:
    if not _SLUG_RE.match(slug):
        raise HTTPException(status_code=404, detail="Not found")
    article = next((a for a in _load_articles() if a["meta"]["slug"] == slug), None)
    if article is None:
        raise HTTPException(status_code=404, detail="Not found")
    body_zh, body_en = _article_html(article)
    meta = article["meta"]
    biz = BUSINESS_LABELS.get(meta.get("business", ""), ("法律专栏", "Legal"))
    crumbs_html, crumbs_jsonld = _crumbs([
        ("首页", f"{SITE_URL}/"),
        ("法律专栏", f"{SITE_URL}/articles"),
        (meta.get("title_zh", "")[:24], f"{SITE_URL}/articles/{meta['slug']}"),
    ])
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
        crumbs=crumbs_html,
        breadcrumb_jsonld=crumbs_jsonld,
        related=_related_html(_related_articles(meta)),
        cookie_banner=_cookie_banner(),
        # Raw (unescaped) values for the JSON-LD block — escaping would corrupt JSON.
        json_title_zh=meta.get("title_zh", ""),
        json_desc_zh=meta.get("description_zh", ""),
        json_date=meta.get("date", ""),
        json_slug=meta["slug"],
        json_site_url=SITE_URL,
        og_image=OG_IMAGE,
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


# ---------- Country landing pages (high commercial intent) ----------

# Shared CSS for the landing-page templates (plain string — not an f-string).
_PAGE_CSS = """
    :root {
      --ink: #172433; --muted: #627180; --paper: #f6f3ed; --surface: #fffdf9;
      --line: #d9d9d2; --teal: #0d6c6b; --teal-deep: #084d50;
      --orange: #d76e39; --cream: #ede8de; --gold: #b08d57;
      --shadow: 0 20px 50px rgba(20, 33, 44, .11);
      --radius: 10px; --max: 1060px;
      --serif: "Playfair Display", "Noto Serif SC", Georgia, "Songti SC", "SimSun", serif;
      --sans: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; color: var(--ink); background: var(--paper); font-family: var(--sans); line-height: 1.65; }
    a { color: inherit; text-decoration: none; }
    button { font: inherit; cursor: pointer; }
    h1, h2, h3, p { margin: 0; }
    h1, h2, h3 { font-family: var(--serif); }
    .wrap { width: min(calc(100% - 40px), var(--max)); margin: 0 auto; }
    .crumbs { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; font-size: 12.5px; color: var(--muted); padding: 22px 0 0; }
    .crumbs a { color: var(--teal); }
    .crumb-sep { color: #b9c2c9; }
    .related { margin: 40px 0 10px; padding: 20px 24px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }
    .related h3 { font-size: 16px; margin: 0 0 12px; color: var(--teal-deep); }
    .related ul { margin: 0; padding-left: 0; list-style: none; }
    .related li { margin: 8px 0; }
    .related a { color: var(--teal); font-weight: 600; font-size: 14px; }
    .topbar { background: var(--teal-deep); color: #f5f2ec; }
    .topbar .wrap { display: flex; justify-content: space-between; align-items: center; min-height: 66px; gap: 18px; }
    .topbar .brand { display: inline-flex; align-items: center; gap: 10px; color: #fff; font-size: 14px; font-weight: 700; }
    .brand-mark { display: grid; place-items: center; width: 30px; height: 30px; color: var(--teal-deep); background: #f7f2e9; border-radius: 7px; font-family: var(--serif); font-size: 16px; }
    .topbar .nav-links { display: flex; align-items: center; gap: 18px; font-size: 13px; }
    .topbar a { color: rgba(255,255,255,.85); }
    .topbar a:hover { color: #fff; }
    .lang-switch { padding: 7px 10px; color: rgba(255,255,255,.85); background: transparent; border: 1px solid rgba(255,255,255,.3); border-radius: 6px; font-size: 12px; }
    .hero { padding: 64px 0 34px; }
    .number { color: var(--gold); font-size: 13px; font-weight: 800; letter-spacing: .08em; }
    h1 { margin: 16px 0 10px; font-size: clamp(32px, 4.4vw, 50px); line-height: 1.14; letter-spacing: -.01em; }
    .en-sub { color: var(--muted); font-size: 15px; }
    .intro { margin-top: 18px; font-size: 16px; max-width: 720px; color: #334454; }
    .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin: 40px auto 0; }
    .card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 26px; }
    .card h2 { margin: 0 0 14px; font-size: 18px; }
    ul { margin: 0; padding: 0; list-style: none; display: grid; gap: 9px; }
    li { position: relative; padding-left: 16px; font-size: 14px; color: #435363; }
    li::before { content: ""; position: absolute; left: 0; top: 9px; width: 5px; height: 5px; background: var(--gold); border-radius: 50%; }
    .steps { margin-top: 18px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }
    .step { padding: 22px 24px; }
    .step + .step { border-left: 1px solid var(--line); }
    .step span { display: block; color: var(--gold); font-size: 13px; font-weight: 800; }
    .step h3 { margin-top: 10px; font-size: 16px; }
    .step p { margin-top: 8px; color: var(--muted); font-size: 13px; }
    .cta { text-align: center; padding: 46px 0 70px; }
    .button { display: inline-flex; align-items: center; gap: 9px; min-height: 48px; padding: 0 26px; color: #fff; background: var(--orange); border-radius: 8px; font-size: 15px; font-weight: 700; transition: transform .2s ease, background .2s ease; }
    .button:hover { transform: translateY(-2px); background: #c85d2e; }
    .cta .note { margin-top: 14px; color: var(--muted); font-size: 12px; }
    footer { background: #15232d; color: rgba(255,255,255,.72); font-size: 12px; padding: 22px 0; text-align: center; line-height: 1.7; }
    footer a { color: rgba(255,255,255,.85); }
    @media (max-width: 720px) {
      .cols { grid-template-columns: 1fr; }
      .steps { grid-template-columns: 1fr; }
      .step + .step { border-left: 0; border-top: 1px solid var(--line); }
      .topbar .wrap { min-height: 60px; }
    }
"""

# Country landing pages: high-commercial-intent keywords per market.
COUNTRIES = {
    "united-states": {
        "name_zh": "美国",
        "name_en": "United States",
        "zh_title": "美国跨境法律服务：欠款追收 · 判决执行 · 房产继承",
        "en_title": "US Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "美国客户拖欠货款、中国判决在美国执行、父母留下的美国房产——跨时区的沟通与陌生的程序让很多企业和家庭一拖再拖。本页梳理在美国最常见的三类跨境法律事项：贸易追收、判决执行与遗产继承。",
        "en_intro": "Unpaid invoices from US buyers, Chinese judgments to enforce in the United States, and property left behind in America — time zones and unfamiliar procedures make many businesses and families delay. This page maps the three most common cross-border matters: trade recovery, judgment enforcement, and inheritance.",
        "items_zh": ["美国客户货款追收与律师函", "中国判决在美国的承认与执行", "美国房产与银行账户资产调查", "跨境继承与美国遗嘱认证 (Probate)"],
        "items_en": ["Debt recovery & demand letters against US buyers", "Recognition & enforcement of Chinese judgments in the US", "Tracing US property and bank accounts", "Cross-border inheritance & US probate"],
        "points_zh": ["多数州承认外国金钱判决不要求互惠，但各州规则与程序不同", "诉讼时效各州不同，常见 2-6 年，务必尽早确认", "财产保全须取得法院命令，资产调查与保全应同步规划", "联邦与州两级司法体系，法院程序须由当地执业律师办理", "继承通常须走 Probate，中国公证文件不能直接替代当地程序"],
        "points_en": ["Most states recognize foreign money judgments without reciprocity, but rules differ by state", "Statutes of limitation vary by state, commonly 2-6 years — confirm early", "Asset preservation requires a court order; plan tracing and preservation together", "Federal and state courts are separate systems; local licensed counsel is required", "Inheritance usually runs through probate; Chinese notarized documents do not replace local procedure"],
        "faq_zh": [
            "中国法院的判决能在美国执行吗？|多数州承认外国金钱判决且不要求互惠，但各州规则与程序不同，需在当地法院申请承认后执行，建议尽早评估。",
            "在美国追收欠款的诉讼时效是多久？|诉讼时效各州不同，常见 2-6 年，务必尽早确认并保全证据。",
            "中国公民继承美国房产需要走什么程序？|通常须经遗嘱认证（Probate），中国公证文件不能直接替代当地程序，需当地律师办理。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in the United States?|Most states recognise foreign money judgments without requiring reciprocity, but rules differ by state; apply for recognition in the local court and assess early.",
            "What is the statute of limitations for collecting a debt in the US?|Limitation periods vary by state, commonly 2-6 years; confirm early and preserve evidence.",
            "What procedure applies when a Chinese citizen inherits US property?|Probate is usually required; Chinese notarised documents do not replace local procedure, and local counsel is needed.",
        ],
    },
    "canada": {
        "name_zh": "加拿大",
        "name_en": "Canada",
        "zh_title": "加拿大跨境法律服务：欠款追收 · 判决执行 · 房产继承",
        "en_title": "Canada Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "加拿大客户拖欠款项、中国判决在加执行、温哥华或多伦多的房产继承——普通法与各省差异让跨境处理并不简单。本页梳理在加拿大最常见的跨境法律事项。",
        "en_intro": "Unpaid amounts from Canadian customers, Chinese judgments to enforce in Canada, and property in Vancouver or Toronto — common law and provincial differences complicate cross-border matters. This page maps the common paths.",
        "items_zh": ["加拿大客户欠款追收与协商", "中国判决在加拿大的承认与执行", "加拿大房产与资产调查", "跨境继承与遗产管理"],
        "items_en": ["Debt recovery & negotiation with Canadian counterparties", "Recognition & enforcement of Chinese judgments in Canada", "Tracing Canadian property and assets", "Cross-border inheritance & estate administration"],
        "points_zh": ["普通法省份对外国金钱判决的执行规则成熟，多数不要求互惠", "各省规则不同；魁北克为大陆法系省份，程序有别", "加拿大无遗产税，但去世时视为按市价处置资产，可能产生资本利得税", "时效各省不同，通常 2-6 年", "银行与地产登记查询渠道因省而异，需当地律师协助"],
        "points_en": ["Common-law provinces have settled foreign-judgment rules, mostly without reciprocity", "Rules vary by province; Quebec is a civil-law province with different procedures", "No estate tax, but deemed disposition at death can trigger capital gains tax", "Limitation periods vary by province, commonly 2-6 years", "Bank and property record access varies by province; local counsel is needed"],
        "faq_zh": [
            "中国法院的判决能在加拿大执行吗？|普通法省份对外国金钱判决的执行规则成熟，多数不要求互惠，但需依各省程序在当地法院申请承认执行。",
            "在加拿大追收欠款的诉讼时效是多久？|时效各省不同，通常 2-6 年。",
            "加拿大有遗产税吗？|加拿大无遗产税，但去世时视为按市价处置资产，可能产生资本利得税，需提前规划。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Canada?|Common-law provinces have settled foreign-judgment rules, mostly without reciprocity; apply for recognition under provincial procedure.",
            "What is the limitation period for collecting a debt in Canada?|Limitation periods vary by province, commonly 2-6 years.",
            "Is there an estate tax in Canada?|No estate tax, but deemed disposition at death can trigger capital gains tax — plan ahead.",
        ],
    },
    "australia": {
        "name_zh": "澳大利亚",
        "name_en": "Australia",
        "zh_title": "澳大利亚跨境法律服务：欠款追收 · 判决执行 · 房产继承",
        "en_title": "Australia Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "澳洲客户拖欠货款、中国判决在澳执行、悉尼或墨尔本的房产继承——执行路径清晰但程序严格。本页梳理在澳大利亚最常见的跨境法律事项。",
        "en_intro": "Unpaid invoices from Australian buyers, Chinese judgments to enforce in Australia, and property in Sydney or Melbourne — enforcement paths are clear but procedural. This page maps the common cross-border matters.",
        "items_zh": ["澳洲客户货款追收与律师函", "中国判决在澳大利亚的执行", "澳洲房产与资产调查", "跨境继承与遗嘱认证"],
        "items_en": ["Debt recovery & demand letters against Australian buyers", "Enforcement of Chinese judgments in Australia", "Tracing Australian property and assets", "Cross-border inheritance & probate"],
        "points_zh": ["外国判决执行依据各州《外国判决法》与普通法规则，程序成熟", "商业债务时效通常 6 年，需尽早启动", "澳大利亚无遗产税，但继承后出售房产可能产生资本利得税", "律师在各州分别执业，跨州案件需协调", "法院程序与文件认证要求严格，建议委托当地律师办理"],
        "points_en": ["Enforcement follows state Foreign Judgments Acts and common law — a settled path", "Limitation for commercial debts is typically 6 years; start early", "No inheritance tax, but selling inherited property may trigger capital gains tax", "Lawyers are admitted per state; multi-state matters need coordination", "Court procedure and document legalization are strict; use local counsel"],
        "faq_zh": [
            "中国法院的判决能在澳大利亚执行吗？|执行依据各州《外国判决法》与普通法规则，程序成熟，可在当地法院申请承认执行。",
            "在澳大利亚追收欠款的诉讼时效是多久？|商业债务时效通常 6 年，需尽早启动。",
            "澳大利亚有遗产税吗？|澳大利亚无遗产税，但继承后出售房产可能产生资本利得税。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Australia?|Enforcement follows state Foreign Judgments Acts and common law — a settled path; apply for recognition in the local court.",
            "What is the limitation period for collecting a debt in Australia?|Limitation for commercial debts is typically 6 years; start early.",
            "Is there an inheritance tax in Australia?|No inheritance tax, but selling inherited property may trigger capital gains tax.",
        ],
    },
    "singapore": {
        "name_zh": "新加坡",
        "name_en": "Singapore",
        "zh_title": "新加坡跨境法律服务：欠款追收 · 裁决执行 · 家族资产",
        "en_title": "Singapore Cross-Border Legal Services: Debt Recovery, Award Enforcement & Family Assets",
        "zh_intro": "新加坡是华人企业出海与家族资产布局的重镇——中间商纠纷、仲裁裁决执行、家族信托与继承。本页梳理在新加坡最常见的跨境法律事项。",
        "en_intro": "Singapore is a hub for Chinese business expansion and family wealth — intermediary disputes, award enforcement, family trusts and inheritance. This page maps the common cross-border matters.",
        "items_zh": ["新加坡客户与中间商欠款追收", "中国判决与仲裁裁决在新加坡执行", "新加坡银行与公司资产调查", "跨境继承、信托与家族资产规划"],
        "items_en": ["Debt recovery from Singapore buyers and intermediaries", "Enforcement of Chinese judgments and arbitral awards in Singapore", "Tracing Singapore bank and corporate assets", "Cross-border inheritance, trusts & family wealth planning"],
        "points_zh": ["普通法体系，外国判决执行路径成熟（普通法 + 成文法）", "仲裁裁决依据《纽约公约》执行，速度快、可预期", "债务时效通常 6 年", "家族办公室与信托常见，继承与传承规划需求高", "银行信息受严格保密法规约束，资产调查需法律程序配合"],
        "points_en": ["Common-law system with a mature foreign-judgment enforcement path", "Arbitral awards enforce under the New York Convention — fast and predictable", "Limitation for debts is typically 6 years", "Family offices and trusts are common; succession planning demand is high", "Banking secrecy is strict; asset tracing needs court processes"],
        "faq_zh": [
            "中国法院的判决能在新加坡执行吗？|新加坡是普通法体系，外国判决执行路径成熟（普通法 + 成文法），可在当地法院申请承认执行。",
            "仲裁裁决在新加坡执行容易吗？|依据《纽约公约》执行，速度快、可预期，是跨境争议的常用路径。",
            "在新加坡追收欠款的诉讼时效是多久？|债务时效通常 6 年。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Singapore?|Singapore is a common-law system with a mature foreign-judgment enforcement path; apply for recognition in the local court.",
            "Are arbitral awards easy to enforce in Singapore?|Awards enforce under the New York Convention — fast and predictable, a common route for cross-border disputes.",
            "What is the limitation period for collecting a debt in Singapore?|Limitation for debts is typically 6 years.",
        ],
    },
    "united-kingdom": {
        "name_zh": "英国",
        "name_en": "United Kingdom",
        "zh_title": "英国跨境法律服务：欠款追收 · 判决执行 · 遗产规划",
        "en_title": "UK Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Estate Planning",
        "zh_intro": "英国客户拖欠货款、中国判决在英国执行、伦敦房产与遗产继承——普通法传统与遗产税制度让规划尤为关键。本页梳理在英国最常见的跨境法律事项。",
        "en_intro": "Unpaid invoices from UK buyers, Chinese judgments to enforce in the UK, and London property and estates — common-law tradition and inheritance tax make planning essential. This page maps the common cross-border matters.",
        "items_zh": ["英国客户货款追收与律师函", "中国判决与仲裁裁决在英国执行", "英国房产与资产调查", "跨境继承、遗嘱认证与遗产税规划"],
        "items_en": ["Debt recovery & demand letters against UK buyers", "Enforcement of Chinese judgments and awards in the UK", "Tracing UK property and assets", "Cross-border inheritance, probate & inheritance tax planning"],
        "points_zh": ["外国判决执行依据《外国判决法》与普通法规则", "商业债务时效通常 6 年", "遗产税 (IHT) 最高 40%，继承规划窗口重要", "律师与出庭律师分业，程序角色分明", "房产登记与产权查询渠道公开，调查相对便利"],
        "points_en": ["Enforcement follows the Foreign Judgments Act and common law", "Limitation for commercial debts is typically 6 years", "Inheritance tax reaches 40% — planning windows matter", "Solicitors and barristers have distinct roles in proceedings", "Land registry searches are accessible, making tracing easier"],
        "faq_zh": [
            "中国法院的判决能在英国执行吗？|执行依据《外国判决法》与普通法规则，可在当地法院申请承认执行。",
            "在英国追收欠款的诉讼时效是多久？|商业债务时效通常 6 年。",
            "英国的遗产税高吗？|遗产税（IHT）最高 40%，提前规划窗口很重要。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in the UK?|Enforcement follows the Foreign Judgments Act and common law; apply for recognition in the local court.",
            "What is the limitation period for collecting a debt in the UK?|Limitation for commercial debts is typically 6 years.",
            "Is UK inheritance tax high?|Inheritance tax reaches 40% — planning windows matter.",
        ],
    },
    "hong-kong": {
        "name_zh": "香港",
        "name_en": "Hong Kong",
        "zh_title": "香港跨境法律服务：内地判决执行 · 欠款追收 · 遗产继承",
        "en_title": "Hong Kong Cross-Border Legal Services: Mainland Judgment Enforcement, Debt Recovery & Inheritance",
        "zh_intro": "内地与香港经贸往来密切，商事纠纷、货款拖欠与跨境继承常年高发。2024 年起内地民商事判决可在香港法院认可与执行，路径已大幅拓宽。本页梳理在香港最常见的跨境法律事项。",
        "en_intro": "Mainland–Hong Kong trade is dense, and commercial disputes, unpaid debts and cross-border inheritance are common. Since 2024, mainland civil and commercial judgments can be recognised and enforced in Hong Kong courts. This page maps the common cross-border matters.",
        "items_zh": ["内地判决在香港的认可与执行", "香港客户与中间商欠款追收", "香港公司查册与资产调查", "跨境继承、遗嘱认证与家族资产"],
        "items_en": ["Recognition & enforcement of mainland judgments in Hong Kong", "Debt recovery from Hong Kong buyers and intermediaries", "Hong Kong company searches and asset tracing", "Cross-border inheritance, probate & family assets"],
        "points_zh": ["2024 年 1 月起《内地与香港民商事判决互认安排》生效，覆盖绝大多数民商事判决（含非金钱判决），范围远大于旧安排", "债务诉讼时效一般 6 年（《时效条例》）", "香港不征收遗产税、赠与税与资本利得税", "事务律师与大律师分业，法院程序通常需本地律师", "公司查册、土地查册渠道公开，资产调查相对便利"],
        "points_en": ["The 2024 Mainland–Hong Kong Judgment Arrangement covers most civil and commercial judgments (including non-money judgments), far beyond the old regime", "Limitation for debts is generally 6 years (Limitation Ordinance)", "No estate, gift or capital gains tax in Hong Kong", "Solicitors and barristers are separate branches; local counsel is usual in court", "Company and land searches are public, making tracing easier"],
        "faq_zh": [
            "内地法院的判决能在香港执行吗？|自 2024 年 1 月 29 日起，依据《内地与香港特别行政区法院相互认可和执行民商事案件判决的安排》，绝大多数内地民商事判决可在香港法院申请认可与执行，不再限于协议管辖案件。",
            "在香港追收欠款的诉讼时效是多久？|依据《时效条例》，债务诉讼时效一般为 6 年，建议尽早启动并同步保全证据。",
            "香港有遗产税吗？|香港不征收遗产税、赠与税与资本利得税；跨境继承主要关注遗嘱认证程序与内地公证文书的衔接。",
        ],
        "faq_en": [
            "Can a mainland Chinese judgment be enforced in Hong Kong?|Since 29 January 2024, the Mainland–Hong Kong Arrangement on Recognition and Enforcement of Civil and Commercial Judgments allows most mainland judgments to be recognised and enforced in Hong Kong courts, no longer limited to jurisdiction-agreement cases.",
            "What is the limitation period for collecting a debt in Hong Kong?|Under the Limitation Ordinance, the limitation period for debts is generally 6 years; start early and preserve evidence.",
            "Is there an estate tax in Hong Kong?|No estate, gift or capital gains tax applies in Hong Kong; cross-border inheritance mainly concerns probate and the linkage of mainland notarised documents.",
        ],
    },
    "germany": {
        "name_zh": "德国",
        "name_en": "Germany",
        "zh_title": "德国跨境法律服务：欠款追收 · 判决执行 · 遗产继承",
        "en_title": "Germany Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "德国是中国在欧洲最大的贸易伙伴，机械、汽车与化工行业的应收款纠纷频发。本页梳理在德国最常见的跨境法律事项：贸易追收、判决执行与继承。",
        "en_intro": "Germany is China's largest trading partner in Europe, and receivables disputes are common in machinery, automotive and chemicals. This page maps the common cross-border matters: trade recovery, judgment enforcement and inheritance.",
        "items_zh": ["德国客户货款追收与律师函", "中国判决在德国的承认与执行", "德国公司与动产资产调查", "跨境继承与德国遗产税规划"],
        "items_en": ["Debt recovery & demand letters against German buyers", "Recognition & enforcement of Chinese judgments in Germany", "Tracing German company and movable assets", "Cross-border inheritance & German inheritance-tax planning"],
        "points_zh": ["中德无双边判决互认条约，外国判决依《民事诉讼法》第 328 条审查，互惠认定严格，个案差异大", "一般债权的诉讼时效为 3 年（自债权到期年度末起算）", "德国遗产税按亲等与金额累进，最高约 50%，配偶有高额免税额", "法院程序原则上须由德国律师代理", "德国公司登记（Handelsregister）公开可查，资产调查有据可依"],
        "points_en": ["No bilateral judgment treaty with China; foreign judgments are reviewed under §328 ZPO with strict reciprocity — case-specific", "General limitation for claims is 3 years (running from year-end after maturity)", "German inheritance tax is progressive by kinship and amount, up to about 50%, with a high spouse allowance", "Court proceedings generally require German counsel", "The commercial register (Handelsregister) is public, giving tracing a solid basis"],
        "faq_zh": [
            "中国法院的判决能在德国执行吗？|中德之间没有双边判决互认条约，德国法院依《民事诉讼法》第 328 条逐案审查（含互惠要求），结果因案而异，常需重新起诉，建议事先评估。",
            "在德国追收欠款的诉讼时效是多久？|一般债权的时效为 3 年，自债权到期年度的年末起算，逾期将难以主张。",
            "德国的遗产税高吗？|德国遗产税按亲等与金额累进，最高约 50%，配偶享有高额免税额，提前规划窗口很重要。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Germany?|There is no bilateral treaty; German courts review foreign judgments case-by-case under §328 ZPO (including reciprocity), so outcomes vary and re-litigation is common — assess first.",
            "What is the limitation period for collecting a debt in Germany?|General claims lapse after 3 years, running from year-end after maturity; acting late can bar the claim.",
            "Is German inheritance tax high?|German inheritance tax is progressive by kinship and amount, up to about 50%; spouses enjoy a high allowance, so early planning matters.",
        ],
    },
    "japan": {
        "name_zh": "日本",
        "name_en": "Japan",
        "zh_title": "日本跨境法律服务：欠款追收 · 判决执行 · 遗产继承",
        "en_title": "Japan Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "日本是中国的重要贸易伙伴，商事纠纷与在日华人房产继承需求持续存在。本页梳理在日本最常见的跨境法律事项。",
        "en_intro": "Japan is a major trading partner of China, with ongoing demand on commercial disputes and inheritance of property held by Chinese families in Japan. This page maps the common cross-border matters.",
        "items_zh": ["日本客户欠款追收与协商", "中国判决在日本的承认与执行", "日本不动产与资产调查", "跨境继承与日本遗产税规划"],
        "items_en": ["Debt recovery & negotiation with Japanese counterparties", "Recognition & enforcement of Chinese judgments in Japan", "Tracing Japanese real estate and assets", "Cross-border inheritance & Japanese inheritance-tax planning"],
        "points_zh": ["外国判决依《民事诉讼法》第 118 条执行，需满足互惠等要件，中日判决互认实践存在障碍，常需重新起诉", "一般债权时效为 5 年（2020 年民法修正后统一）", "日本遗产税最高约 55%，配偶有基础免税额", "不动产物权登记与公证手续严格，交易与继承均需日本律师/司法书士协助", "公司登记（商业登记簿）公开，资产调查渠道明确"],
        "points_en": ["Foreign judgments execute under Art. 118 of the Code of Civil Procedure, requiring reciprocity among other conditions; China–Japan recognition practice is difficult and re-litigation is common", "General claims lapse after 5 years (post-2020 Civil Code reform)", "Japanese inheritance tax can reach about 55%; spouses have a basic allowance", "Real-property registration and notarisation are strict; Japanese counsel/ judicial scriveners are involved in both transactions and inheritance", "The commercial register is public, giving tracing a clear channel"],
        "faq_zh": [
            "中国法院的判决能在日本执行吗？|日本法院依《民事诉讼法》第 118 条审查外国判决，须满足互惠等要件；中日之间判决互认实践存在障碍，实务中常需重新起诉。",
            "在日本追收欠款的诉讼时效是多久？|2020 年民法修正后一般债权时效统一为 5 年。",
            "日本的遗产税高吗？|日本遗产税最高约 55%，配偶有基础免税额（1.6 亿日元），提前规划非常重要。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Japan?|Japanese courts review foreign judgments under Art. 118 CCP, requiring reciprocity among other conditions; China–Japan recognition practice faces hurdles, so re-litigation is common.",
            "What is the limitation period for collecting a debt in Japan?|General claims lapse after 5 years following the 2020 Civil Code reform.",
            "Is Japanese inheritance tax high?|Japanese inheritance tax can reach about 55%; spouses enjoy a basic allowance of JPY 160 million, making early planning essential.",
        ],
    },
    "united-arab-emirates": {
        "name_zh": "阿联酋",
        "name_en": "UAE (Dubai)",
        "zh_title": "阿联酋跨境法律服务：欠款追收 · 判决执行 · 房产继承",
        "en_title": "UAE Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Property Inheritance",
        "zh_intro": "迪拜是中东贸易枢纽与华人商区重镇，货款纠纷与房产投资继承需求集中。本页梳理在阿联酋最常见的跨境法律事项。",
        "en_intro": "Dubai is a Middle East trading hub with a large Chinese business community; invoice disputes and property-investment inheritance are concentrated here. This page maps the common cross-border matters in the UAE.",
        "items_zh": ["阿联酋客户与中间商欠款追收", "中国判决在阿联酋的承认与执行", "迪拜房产与银行资产调查", "跨境继承与迪拜房产规划"],
        "items_en": ["Debt recovery from UAE buyers and intermediaries", "Recognition & enforcement of Chinese judgments in the UAE", "Tracing Dubai property and bank assets", "Cross-border inheritance & Dubai property planning"],
        "points_zh": ["中阿民商事司法协助条约（2004 年签署）涵盖判决承认与执行", "联邦法院与迪拜国际金融中心（DIFC）法院双轨并行，路径选择影响执行效率", "阿联酋不征收个人所得税与遗产税，2020 年后非穆斯林继承适用成文继承法，可依遗嘱继承", "穆斯林继承适用伊斯兰继承规则，与遗嘱自由并存但有限制", "银行开户与资金流调查须经法律程序配合"],
        "points_en": ["The 2004 China–UAE judicial assistance treaty covers recognition and enforcement of judgments", "Federal courts and the DIFC courts run in parallel; the chosen route affects enforcement efficiency", "No personal income tax or estate tax; since 2020 non-Muslims inherit under codified rules and may inherit by will", "Muslim succession follows Islamic inheritance rules, coexisting with (but limiting) testamentary freedom", "Bank-account and fund-flow tracing requires court processes"],
        "faq_zh": [
            "中国法院的判决能在阿联酋执行吗？|中阿民商事司法协助条约（2004 年签署）涵盖判决承认与执行，可在阿联酋法院申请；联邦法院与 DIFC 法院两条路径效率不同，建议先评估。",
            "阿联酋有遗产税吗？|阿联酋不征收遗产税；2020 年后非穆斯林适用成文继承法，可依遗嘱继承，穆斯林则适用伊斯兰继承规则。",
            "在迪拜追收欠款需要注意什么？|迪拜法律环境对债权保护较完善，但银行信息与资金流调查须经法律程序，建议尽早固定证据并评估 DIFC 路径。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in the UAE?|The 2004 China–UAE judicial assistance treaty covers judgment recognition and enforcement; applications go to UAE courts, with the federal and DIFC routes differing in efficiency — assess first.",
            "Is there an estate tax in the UAE?|No estate tax applies; since 2020 non-Muslims inherit under codified rules and may inherit by will, while Muslims follow Islamic inheritance rules.",
            "What matters when collecting a debt in Dubai?|Dubai's legal environment is creditor-friendly, but bank and fund-flow tracing needs court processes — preserve evidence early and evaluate the DIFC route.",
        ],
    },
    "new-zealand": {
        "name_zh": "新西兰",
        "name_en": "New Zealand",
        "zh_title": "新西兰跨境法律服务：欠款追收 · 判决执行 · 房产继承",
        "en_title": "New Zealand Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Property Inheritance",
        "zh_intro": "新西兰华人移民众多，奥克兰房产继承与对澳新客户的欠款追收需求持续。本页梳理在新西兰最常见的跨境法律事项。",
        "en_intro": "New Zealand has a large Chinese community; Auckland property inheritance and debt recovery from NZ/AU clients are steady demands. This page maps the common cross-border matters.",
        "items_zh": ["新西兰客户欠款追收与律师函", "中国判决在新西兰的承认与执行", "新西兰房产与资产调查", "跨境继承与遗嘱认证"],
        "items_en": ["Debt recovery & demand letters against New Zealand buyers", "Recognition & enforcement of Chinese judgments in New Zealand", "Tracing New Zealand property and assets", "Cross-border inheritance & probate"],
        "points_zh": ["互惠执行判决法覆盖指定互惠国；中国不在名单内时依普通法重新起诉", "债务诉讼时效一般 6 年", "新西兰无遗产税、无赠与税、无资本利得税", "房产交易与继承均须律师办理交割/认证程序", "土地登记（LINZ）公开可查，资产调查便利"],
        "points_en": ["The Reciprocal Enforcement of Judgments Act covers designated countries; otherwise re-litigation at common law", "Limitation for debts is generally 6 years", "No estate, gift or capital gains tax in New Zealand", "Property conveyancing and probate both require lawyers", "Land records (LINZ) are public, making tracing easy"],
        "faq_zh": [
            "中国法院的判决能在新西兰执行吗？|互惠执行判决法仅覆盖指定互惠国，中国不在名单内，通常需依普通法在新西兰重新起诉后执行。",
            "新西兰有遗产税吗？|新西兰不征收遗产税、赠与税与资本利得税，跨境继承主要关注遗嘱认证与文件公证衔接。",
            "在新西兰追收欠款的诉讼时效是多久？|债务诉讼时效一般为 6 年。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in New Zealand?|The Reciprocal Enforcement of Judgments Act covers designated countries only; China is not on the list, so re-litigation at common law is usual.",
            "Is there an estate tax in New Zealand?|No estate, gift or capital gains tax applies; cross-border inheritance mainly concerns probate and document legalisation.",
            "What is the limitation period for collecting a debt in New Zealand?|The limitation period for debts is generally 6 years.",
        ],
    },
    "malaysia": {
        "name_zh": "马来西亚",
        "name_en": "Malaysia",
        "zh_title": "马来西亚跨境法律服务：欠款追收 · 判决执行 · 遗产继承",
        "en_title": "Malaysia Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "马来西亚华人社区庞大，中马贸易与吉隆坡房产投资活跃。本页梳理在马来西亚最常见的跨境法律事项。",
        "en_intro": "Malaysia has a large Chinese community with active China–Malaysia trade and Kuala Lumpur property investment. This page maps the common cross-border matters.",
        "items_zh": ["马来西亚客户与中间商欠款追收", "中国判决在马来西亚的执行", "吉隆坡房产与资产调查", "跨境继承（穆斯林/非穆斯林双轨）"],
        "items_en": ["Debt recovery from Malaysian buyers and intermediaries", "Enforcement of Chinese judgments in Malaysia", "Tracing Kuala Lumpur property and assets", "Cross-border inheritance (Muslim / non-Muslim dual system)"],
        "points_zh": ["互惠执行判决法（REOJ 1958）覆盖英联邦及指定国家，中国不在名单内，通常依普通法重新起诉", "债务诉讼时效一般 6 年", "马来西亚已停征遗产税", "继承制度分穆斯林与非穆斯林两套，程序与适用法不同", "公司查册（SSM）公开，资产调查有渠道"],
        "points_en": ["The Reciprocal Enforcement of Judgments Act 1958 covers Commonwealth and designated countries; China is not on the list, so re-litigation at common law is usual", "Limitation for debts is generally 6 years", "Estate duty has been abolished in Malaysia", "Muslim and non-Muslim succession are separate systems with different procedures and laws", "Company searches (SSM) are public, giving tracing a channel"],
        "faq_zh": [
            "中国法院的判决能在马来西亚执行吗？|互惠执行判决法仅覆盖英联邦及指定国家，中国不在名单内，通常需依普通法重新起诉后执行。",
            "马来西亚有遗产税吗？|马来西亚已停征遗产税；继承需注意穆斯林与非穆斯林两套制度的适用。",
            "在马来西亚追收欠款的诉讼时效是多久？|债务诉讼时效一般为 6 年。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Malaysia?|The Reciprocal Enforcement of Judgments Act 1958 covers Commonwealth and designated countries only; China is not on the list, so re-litigation at common law is usual.",
            "Is there an estate tax in Malaysia?|Estate duty has been abolished; note the dual Muslim / non-Muslim succession systems.",
            "What is the limitation period for collecting a debt in Malaysia?|The limitation period for debts is generally 6 years.",
        ],
    },
    "france": {
        "name_zh": "法国",
        "name_en": "France",
        "zh_title": "法国跨境法律服务：欠款追收 · 判决执行 · 遗产继承",
        "en_title": "France Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "法国是中国在欧盟的重要贸易伙伴，奢侈品、葡萄酒与机械贸易中的应收款纠纷常见。本页梳理在法国最常见的跨境法律事项。",
        "en_intro": "France is a major EU trading partner of China; receivables disputes are common in luxury goods, wine and machinery trade. This page maps the common cross-border matters.",
        "items_zh": ["法国客户货款追收与律师函", "中国判决在法国的承认与执行", "法国房产与资产调查", "跨境继承与法国遗产税规划"],
        "items_en": ["Debt recovery & demand letters against French buyers", "Recognition & enforcement of Chinese judgments in France", "Tracing French property and assets", "Cross-border inheritance & French inheritance-tax planning"],
        "points_zh": ["中法无双边判决互认条约，法国法院依国际私法规则审查外国判决，承认条件相对成熟但逐案审查", "一般债权时效为 5 年（《民法典》第 2224 条）", "法国遗产税直系子女最高约 45%，配偶免税", "公证人（Notaire）在房产交易与继承程序中角色关键", "房产登记公开，资产调查依赖公证与登记渠道"],
        "points_en": ["No bilateral treaty with China; French courts review foreign judgments under private-international-law rules — a settled but case-by-case regime", "General claims lapse after 5 years (Art. 2224 Civil Code)", "French inheritance tax reaches about 45% for direct descendants; spouses are exempt", "Notaires play a key role in property transactions and succession", "Land registration is public; tracing relies on notarial and registry channels"],
        "faq_zh": [
            "中国法院的判决能在法国执行吗？|中法没有双边互认条约，法国法院依国际私法规则逐案审查外国判决，条件相对成熟，但需个案评估。",
            "在法国追收欠款的诉讼时效是多久？|一般债权时效为 5 年。",
            "法国的遗产税高吗？|法国遗产税直系子女最高约 45%，配偶免税；房产继承还涉及公证程序，规划窗口重要。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in France?|No bilateral treaty exists; French courts review foreign judgments case-by-case under private-international-law rules — a settled regime, but assess each case.",
            "What is the limitation period for collecting a debt in France?|General claims lapse after 5 years.",
            "Is French inheritance tax high?|French inheritance tax reaches about 45% for direct descendants; spouses are exempt, and property succession involves notarial procedures — plan early.",
        ],
    },
    "switzerland": {
        "name_zh": "瑞士",
        "name_en": "Switzerland",
        "zh_title": "瑞士跨境法律服务：欠款追收 · 判决执行 · 资产调查",
        "en_title": "Switzerland Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Asset Tracing",
        "zh_intro": "瑞士是全球资产聚集地，跨境欠款、判决执行与银行资产调查需求集中。本页梳理在瑞士最常见的跨境法律事项。",
        "en_intro": "Switzerland is a global wealth hub, with concentrated demand for cross-border debt recovery, judgment enforcement and bank-asset tracing. This page maps the common cross-border matters.",
        "items_zh": ["瑞士客户与机构欠款追收", "中国判决在瑞士的承认与执行", "瑞士银行与资产调查", "跨境继承与瑞士税务规划"],
        "items_en": ["Debt recovery from Swiss counterparties", "Recognition & enforcement of Chinese judgments in Switzerland", "Tracing Swiss bank accounts and assets", "Cross-border inheritance & Swiss tax planning"],
        "points_zh": ["中瑞司法协助条约（1988 年签署）涵盖民商事判决承认与执行", "外国判决执行依《联邦国际私法法》（PILA）第 25-32 条", "一般债权时效为 10 年（《债法》第 127 条）", "瑞士无联邦遗产税，州级遗产税差异大，规划需按州评估", "银行保密与 CRS 框架并存，资产调查须经法律程序配合"],
        "points_en": ["The 1988 China–Switzerland judicial assistance treaty covers recognition and enforcement of civil and commercial judgments", "Foreign judgments enforce under Art. 25–32 PILA", "General claims lapse after 10 years (Art. 127 Code of Obligations)", "No federal estate tax; cantonal estate taxes vary widely — plan per canton", "Banking secrecy coexists with CRS; tracing requires court processes"],
        "faq_zh": [
            "中国法院的判决能在瑞士执行吗？|中瑞司法协助条约（1988 年签署）涵盖民商事判决的承认与执行，可依《联邦国际私法法》第 25-32 条申请执行。",
            "在瑞士追收欠款的诉讼时效是多久？|一般债权时效为 10 年（《债法》第 127 条）。",
            "瑞士的遗产税情况如何？|瑞士无联邦遗产税，州级遗产税差异很大，继承规划需要按居住州个案评估。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Switzerland?|The 1988 China–Switzerland judicial assistance treaty covers recognition and enforcement of civil and commercial judgments; apply under Art. 25–32 PILA.",
            "What is the limitation period for collecting a debt in Switzerland?|General claims lapse after 10 years (Art. 127 Code of Obligations).",
            "How does Swiss estate tax work?|No federal estate tax; cantonal estate taxes vary widely, so plan according to the canton of residence.",
        ],
    },
    "south-korea": {
        "name_zh": "韩国",
        "name_en": "South Korea",
        "zh_title": "韩国跨境法律服务：欠款追收 · 判决执行 · 遗产继承",
        "en_title": "South Korea Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "韩国是中国近邻与重要贸易伙伴，半导体、化妆品与消费品贸易中的货款纠纷常见。本页梳理在韩国最常见的跨境法律事项。",
        "en_intro": "South Korea is a close neighbour and major trading partner of China; invoice disputes are common in semiconductors, cosmetics and consumer goods. This page maps the common cross-border matters.",
        "items_zh": ["韩国客户货款追收与律师函", "中国判决在韩国的承认与执行", "韩国公司与资产调查", "跨境继承与韩国遗产税规划"],
        "items_en": ["Debt recovery & demand letters against Korean buyers", "Recognition & enforcement of Chinese judgments in South Korea", "Tracing Korean company and assets", "Cross-border inheritance & Korean inheritance-tax planning"],
        "points_zh": ["外国判决依《民事诉讼法》第 217 条审查，互惠认定严格，中韩判决互认实践存在障碍，常需重新起诉", "商事债权时效一般 5 年，普通债权 10 年", "韩国遗产税较高，最高档约 40%-50%，需按现行税法确认", "诉讼原则上须由韩国律师代理", "公司登记（法院登记）公开，资产调查有渠道"],
        "points_en": ["Foreign judgments are reviewed under Art. 217 of the Civil Procedure Act with strict reciprocity; China–Korea recognition practice faces hurdles and re-litigation is common", "Commercial claims generally lapse after 5 years; general claims after 10", "Korean inheritance tax is high, top bracket around 40-50% — confirm current law", "Korean counsel is generally required in proceedings", "Company registers are public, giving tracing a channel"],
        "faq_zh": [
            "中国法院的判决能在韩国执行吗？|韩国依《民事诉讼法》第 217 条审查外国判决，互惠认定严格，中韩互认实践存在障碍，实务中常需重新起诉。",
            "在韩国追收欠款的诉讼时效是多久？|商事债权时效一般 5 年，普通债权 10 年，需按债权性质确认。",
            "韩国的遗产税高吗？|韩国遗产税较高，最高档约 40%-50%，配偶有免税额，需按现行税法提前规划。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in South Korea?|Korean courts review foreign judgments under Art. 217 CCP with strict reciprocity; China–Korea recognition practice faces hurdles, so re-litigation is common.",
            "What is the limitation period for collecting a debt in South Korea?|Commercial claims generally lapse after 5 years and general claims after 10; confirm by claim type.",
            "Is Korean inheritance tax high?|Korean inheritance tax is high, top bracket around 40-50%; spouses have an allowance, and planning under current law matters.",
        ],
    },
    "thailand": {
        "name_zh": "泰国",
        "name_en": "Thailand",
        "zh_title": "泰国跨境法律服务：欠款追收 · 争议解决 · 房产继承",
        "en_title": "Thailand Cross-Border Legal Services: Debt Recovery, Dispute Resolution & Property Inheritance",
        "zh_intro": "泰国是中国游客与投资者聚集地，曼谷贸易与房产纠纷、在泰华人继承需求持续。本页梳理在泰国最常见的跨境法律事项。",
        "en_intro": "Thailand hosts large numbers of Chinese visitors and investors; Bangkok trade and property disputes and inheritance matters for Chinese families are steady demands. This page maps the common cross-border matters.",
        "items_zh": ["泰国客户与中间商欠款追收", "中国判决在泰国的执行（需重新起诉）", "曼谷房产与资产调查", "跨境继承与泰国房产限制"],
        "items_en": ["Debt recovery from Thai buyers and intermediaries", "Enforcement of Chinese judgments in Thailand (re-litigation)", "Tracing Bangkok property and assets", "Cross-border inheritance & Thai property restrictions"],
        "points_zh": ["泰国不承认外国法院判决，须在泰国法院重新起诉，外国判决可作参考证据", "一般合同债权时效为 10 年", "泰国遗产税法已通过但长期未实际征收，仍需关注立法动向", "外国人通常不能直接持有泰国土地，房产继承有特殊规则", "公司查册与土地厅登记公开，资产调查有渠道"],
        "points_en": ["Thailand does not recognise foreign court judgments; re-litigation in Thai courts is required, with the foreign judgment usable as reference evidence", "General contractual claims lapse after 10 years", "The Thai inheritance tax law was enacted but has long remained unimplemented; monitor legislative developments", "Foreigners generally cannot directly own Thai land; special rules apply to inherited property", "Company and Land Department records are public, giving tracing a channel"],
        "faq_zh": [
            "中国法院的判决能在泰国执行吗？|泰国不承认外国法院判决，须在泰国法院重新起诉，中国判决可作为参考证据使用。",
            "在泰国追收欠款的诉讼时效是多久？|一般合同债权时效为 10 年。",
            "外国人能在泰国继承房产吗？|外国人通常不能直接持有泰国土地，房产继承有特殊规则，需当地律师个案处理。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Thailand?|Thailand does not recognise foreign judgments; re-litigation in Thai courts is required, with the Chinese judgment usable as reference evidence.",
            "What is the limitation period for collecting a debt in Thailand?|General contractual claims lapse after 10 years.",
            "Can foreigners inherit property in Thailand?|Foreigners generally cannot directly own Thai land; special rules apply to inherited property — handle case-by-case with local counsel.",
        ],
    },
    "vietnam": {
        "name_zh": "越南",
        "name_en": "Vietnam",
        "zh_title": "越南跨境法律服务：欠款追收 · 判决执行 · 投资纠纷",
        "en_title": "Vietnam Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Investment Disputes",
        "zh_intro": "越南是供应链转移与中资投资热点，工厂货款纠纷与投资争议增长迅速。本页梳理在越南最常见的跨境法律事项。",
        "en_intro": "Vietnam is a hotspot for supply-chain relocation and Chinese investment; factory invoice disputes and investment disagreements are growing fast. This page maps the common cross-border matters.",
        "items_zh": ["越南客户与工厂欠款追收", "中国判决在越南的承认与执行", "越南公司与资产调查", "投资合作纠纷与仲裁"],
        "items_en": ["Debt recovery from Vietnamese buyers and factories", "Recognition & enforcement of Chinese judgments in Vietnam", "Tracing Vietnamese company and assets", "Investment disputes and arbitration"],
        "points_zh": ["中越司法协助条约（1998 年签署）涵盖民商事判决承认执行，执行须经越南最高人民检察院审核后指定法院办理", "合同违约请求权时效为 3 年（2015 年民法典）", "越南无遗产税", "仲裁是外资纠纷常用路径（越南为《纽约公约》成员）", "公司登记公开，资产调查可依登记与银行程序进行"],
        "points_en": ["The 1998 China–Vietnam judicial assistance treaty covers recognition and enforcement; enforcement is reviewed by the Supreme People's Procuracy and assigned to a court", "Contract claims lapse after 3 years (2015 Civil Code)", "No inheritance tax in Vietnam", "Arbitration is a common route for foreign-invested disputes (Vietnam is a New York Convention member)", "Company registers are public; tracing follows registries and bank processes"],
        "faq_zh": [
            "中国法院的判决能在越南执行吗？|依据中越司法协助条约（1998 年签署），民商事判决可申请承认执行，程序经越南最高人民检察院审核后指定法院办理。",
            "在越南追收欠款的诉讼时效是多久？|依 2015 年民法典，合同违约请求权时效为 3 年，需尽早启动。",
            "越南有遗产税吗？|越南不征收遗产税。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Vietnam?|Under the 1998 China–Vietnam judicial assistance treaty, civil and commercial judgments may be recognised and enforced, with the application reviewed by the Supreme People's Procuracy and assigned to a court.",
            "What is the limitation period for collecting a debt in Vietnam?|Under the 2015 Civil Code, contract claims lapse after 3 years — start early.",
            "Is there an inheritance tax in Vietnam?|No inheritance tax is levied in Vietnam.",
        ],
    },
    "netherlands": {
        "name_zh": "荷兰",
        "name_en": "Netherlands",
        "zh_title": "荷兰跨境法律服务：欠款追收 · 判决执行 · 遗产继承",
        "en_title": "Netherlands Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "荷兰是欧洲门户与鹿特丹港贸易枢纽，中荷贸易应收款纠纷与房产继承需求并存。本页梳理在荷兰最常见的跨境法律事项。",
        "en_intro": "The Netherlands is Europe's gateway and the Rotterdam port hub; China–Netherlands trade receivables disputes and property inheritance coexist. This page maps the common cross-border matters.",
        "items_zh": ["荷兰客户货款追收与律师函", "中国判决在荷兰的执行（需重新起诉）", "荷兰公司与资产调查", "跨境继承与荷兰遗产税规划"],
        "items_en": ["Debt recovery & demand letters against Dutch buyers", "Enforcement of Chinese judgments in the Netherlands (re-litigation)", "Tracing Dutch company and assets", "Cross-border inheritance & Dutch inheritance-tax planning"],
        "points_zh": ["荷兰《民事诉讼法》第 431 条规定外国判决原则上不可直接执行（无条约时），通常需重新起诉", "一般合同债权时效为 5 年", "荷兰遗产税最高约 40%，配偶与直系子女适用不同税率", "法院程序须由荷兰律师代理", "商会登记（KvK）与土地登记公开，资产调查便利"],
        "points_en": ["Art. 431 of the Dutch Code of Civil Procedure bars direct enforcement of foreign judgments absent a treaty — re-litigation is usually required", "General contractual claims lapse after 5 years", "Dutch inheritance tax reaches about 40%, with different rates for spouses and children", "Dutch counsel is required in court proceedings", "Chamber of Commerce (KvK) and land registers are public, making tracing easy"],
        "faq_zh": [
            "中国法院的判决能在荷兰执行吗？|依荷兰《民事诉讼法》第 431 条，无条约时外国判决原则上不可直接执行，通常需在荷兰重新起诉。",
            "在荷兰追收欠款的诉讼时效是多久？|一般合同债权时效为 5 年。",
            "荷兰的遗产税高吗？|荷兰遗产税最高约 40%，配偶与直系子女适用不同税率，建议提前规划。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in the Netherlands?|Under Art. 431 of the Dutch Code of Civil Procedure, foreign judgments are not directly enforceable absent a treaty — re-litigation is usually required.",
            "What is the limitation period for collecting a debt in the Netherlands?|General contractual claims lapse after 5 years.",
            "Is Dutch inheritance tax high?|Dutch inheritance tax reaches about 40%, with different rates for spouses and children — plan early.",
        ],
    },
    "italy": {
        "name_zh": "意大利",
        "name_en": "Italy",
        "zh_title": "意大利跨境法律服务：欠款追收 · 判决执行 · 遗产继承",
        "en_title": "Italy Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "意大利在奢侈品、机械与时尚领域与中国贸易密切，应收款纠纷常见。本页梳理在意大利最常见的跨境法律事项。",
        "en_intro": "Italy trades closely with China in luxury goods, machinery and fashion, where receivables disputes are common. This page maps the common cross-border matters.",
        "items_zh": ["意大利客户货款追收与律师函", "中国判决在意大利的承认与执行", "意大利公司与资产调查", "跨境继承与意大利遗产税规划"],
        "items_en": ["Debt recovery & demand letters against Italian buyers", "Recognition & enforcement of Chinese judgments in Italy", "Tracing Italian company and assets", "Cross-border inheritance & Italian inheritance-tax planning"],
        "points_zh": ["中意无判决互认条约，外国判决依国际私法（218/1995 号法）审查承认", "一般债权时效为 10 年（《民法典》第 2946 条）", "意大利遗产税税率较低：配偶与直系子女约 4%，其他亲属 6%-8%", "法院程序须由意大利律师代理", "公司登记与不动产登记公开，资产调查有渠道"],
        "points_en": ["No bilateral treaty with China; foreign judgments are reviewed for recognition under Law 218/1995", "General claims lapse after 10 years (Art. 2946 Civil Code)", "Italian inheritance tax is low: about 4% for spouses and direct descendants, 6-8% for other relatives", "Italian counsel is required in court proceedings", "Company and property registers are public, giving tracing a channel"],
        "faq_zh": [
            "中国法院的判决能在意大利执行吗？|中意没有判决互认条约，外国判决依意大利国际私法（Law 218/1995）逐案审查承认。",
            "在意大利追收欠款的诉讼时效是多久？|一般债权时效为 10 年。",
            "意大利的遗产税高吗？|意大利遗产税较低：配偶与直系子女约 4%，其他亲属 6%-8%。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Italy?|No bilateral treaty exists; foreign judgments are reviewed for recognition case-by-case under Law 218/1995.",
            "What is the limitation period for collecting a debt in Italy?|General claims lapse after 10 years.",
            "Is Italian inheritance tax high?|Italian inheritance tax is low: about 4% for spouses and direct descendants, 6-8% for other relatives.",
        ],
    },
    "spain": {
        "name_zh": "西班牙",
        "name_en": "Spain",
        "zh_title": "西班牙跨境法律服务：欠款追收 · 判决执行 · 房产继承",
        "en_title": "Spain Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Property Inheritance",
        "zh_intro": "西班牙房产是华人投资热点，马德里与巴塞罗那的贸易纠纷、房产继承需求持续。本页梳理在西班牙最常见的跨境法律事项。",
        "en_intro": "Spanish property is a hotspot for Chinese investors; Madrid and Barcelona trade disputes and property inheritance are steady demands. This page maps the common cross-border matters.",
        "items_zh": ["西班牙客户货款追收与律师函", "中国判决在西班牙的承认与执行", "西班牙房产与资产调查", "跨境继承与西班牙遗产税规划"],
        "items_en": ["Debt recovery & demand letters against Spanish buyers", "Recognition & enforcement of Chinese judgments in Spain", "Tracing Spanish property and assets", "Cross-border inheritance & Spanish inheritance-tax planning"],
        "points_zh": ["中西司法协助条约（1992 年签署）涵盖民商事判决承认执行", "一般债权时效为 5 年（2015 年改革后）", "西班牙遗产税各自治区差异大，国家税率最高约 34%，部分大区有高额减免", "公证人（Notario）在房产交易中角色法定", "不动产登记公开，资产调查渠道明确"],
        "points_en": ["The 1992 China–Spain judicial assistance treaty covers recognition and enforcement of civil and commercial judgments", "General claims lapse after 5 years (post-2015 reform)", "Spanish inheritance tax varies by autonomous community; the state rate reaches about 34%, with significant reliefs in some regions", "Notaries play a statutory role in property transactions", "Land registration is public, giving tracing a clear channel"],
        "faq_zh": [
            "中国法院的判决能在西班牙执行吗？|中西司法协助条约（1992 年签署）涵盖民商事判决的承认与执行，可依条约申请。",
            "在西班牙追收欠款的诉讼时效是多久？|一般债权时效为 5 年。",
            "西班牙的遗产税高吗？|西班牙遗产税各自治区差异很大，国家税率最高约 34%，部分大区有高额减免，需按房产所在地评估。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Spain?|The 1992 China–Spain judicial assistance treaty covers recognition and enforcement of civil and commercial judgments; apply under the treaty.",
            "What is the limitation period for collecting a debt in Spain?|General claims lapse after 5 years.",
            "Is Spanish inheritance tax high?|Spanish inheritance tax varies widely by autonomous community; the state rate reaches about 34%, with significant reliefs in some regions — assess by property location.",
        ],
    },
    "brazil": {
        "name_zh": "巴西",
        "name_en": "Brazil",
        "zh_title": "巴西跨境法律服务：欠款追收 · 判决执行 · 投资纠纷",
        "en_title": "Brazil Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Investment Disputes",
        "zh_intro": "巴西是拉美最大经济体与中资出海重镇，圣保罗贸易货款纠纷与投资争议常见。本页梳理在巴西最常见的跨境法律事项。",
        "en_intro": "Brazil is Latin America's largest economy and a major destination for Chinese outbound investment; São Paulo trade receivables and investment disputes are common. This page maps the common cross-border matters.",
        "items_zh": ["巴西客户货款追收与律师函", "中国判决在巴西的承认与执行", "巴西公司与资产调查", "投资合作纠纷与仲裁"],
        "items_en": ["Debt recovery & demand letters against Brazilian buyers", "Recognition & enforcement of Chinese judgments in Brazil", "Tracing Brazilian company and assets", "Investment disputes and arbitration"],
        "points_zh": ["外国判决须经巴西高等法院（STJ）确认（homologação）后方可执行，中巴无专门民商事判决条约", "一般合同债权时效为 10 年（《民法典》第 206 条）", "巴西遗产税为州级税（ITCMD），各州 4%-8%", "仲裁是外资纠纷常用路径（巴西为《纽约公约》成员）", "公司登记（CNPJ）与不动产登记公开，资产调查有渠道"],
        "points_en": ["Foreign judgments must be homologated by the Superior Court of Justice (STJ) before enforcement; no dedicated China–Brazil civil judgment treaty exists", "General contractual claims lapse after 10 years (Art. 206 Civil Code)", "Brazilian inheritance tax (ITCMD) is state-level, 4-8% by state", "Arbitration is a common route for foreign-invested disputes (Brazil is a New York Convention member)", "Company (CNPJ) and property registers are public, giving tracing a channel"],
        "faq_zh": [
            "中国法院的判决能在巴西执行吗？|外国判决须先经巴西高等法院（STJ）确认（homologação）后方可执行；中巴之间没有专门的民商事判决互认条约，程序耗时较长。",
            "在巴西追收欠款的诉讼时效是多久？|一般合同债权时效为 10 年。",
            "巴西的遗产税高吗？|巴西遗产税为州级税（ITCMD），税率约 4%-8%，各州不同。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Brazil?|Foreign judgments must first be homologated by the Superior Court of Justice (STJ); no dedicated China–Brazil civil judgment treaty exists and the procedure takes time.",
            "What is the limitation period for collecting a debt in Brazil?|General contractual claims lapse after 10 years.",
            "Is Brazilian inheritance tax high?|Brazilian inheritance tax (ITCMD) is state-level at about 4-8%, varying by state.",
        ],
    },
    "india": {
        "name_zh": "印度",
        "name_en": "India",
        "zh_title": "印度跨境法律服务：欠款追收 · 判决执行 · 争议解决",
        "en_title": "India Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Dispute Resolution",
        "zh_intro": "印度市场庞大且增长快，中印贸易货款纠纷与投资争议不断增加。本页梳理在印度最常见的跨境法律事项。",
        "en_intro": "India's market is vast and fast-growing; China–India trade receivables and investment disputes are increasing. This page maps the common cross-border matters.",
        "items_zh": ["印度客户货款追收与律师函", "中国判决在印度的承认与执行", "印度公司与资产调查", "商事仲裁与投资争议"],
        "items_en": ["Debt recovery & demand letters against Indian buyers", "Recognition & enforcement of Chinese judgments in India", "Tracing Indian company and assets", "Commercial arbitration and investment disputes"],
        "points_zh": ["依《民事诉讼法》第 13 条审查外国判决；中印无互惠安排，通常需在当地重新起诉，外国判决可作证据", "合同债务时效一般为 3 年（《时效法 1963》）", "印度无遗产税（1985 年废除）", "仲裁是外资纠纷常用路径（印度为《纽约公约》成员）", "公司登记（MCA）公开，资产调查有渠道"],
        "points_en": ["Foreign judgments are reviewed under s.13 CPC; absent reciprocity arrangements with China, re-litigation is usual, with the foreign judgment as evidence", "Contract debts generally lapse after 3 years (Limitation Act 1963)", "No inheritance tax in India (abolished 1985)", "Arbitration is a common route for foreign-invested disputes (India is a New York Convention member)", "Company records (MCA) are public, giving tracing a channel"],
        "faq_zh": [
            "中国法院的判决能在印度执行吗？|中印没有互惠安排，通常需在印度依《民事诉讼法》第 13 条审查后重新起诉，中国判决可作为证据参考。",
            "在印度追收欠款的诉讼时效是多久？|合同债务时效一般为 3 年。",
            "印度有遗产税吗？|印度于 1985 年废除遗产税。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in India?|Without reciprocity arrangements, re-litigation in India is usual, with the foreign judgment reviewed under s.13 CPC and usable as evidence.",
            "What is the limitation period for collecting a debt in India?|Contract debts generally lapse after 3 years.",
            "Is there an inheritance tax in India?|India abolished inheritance tax in 1985.",
        ],
    },
    "ireland": {
        "name_zh": "爱尔兰",
        "name_en": "Ireland",
        "zh_title": "爱尔兰跨境法律服务：欠款追收 · 判决执行 · 遗产继承",
        "en_title": "Ireland Cross-Border Legal Services: Debt Recovery, Judgment Enforcement & Inheritance",
        "zh_intro": "爱尔兰是欧洲科技与生物医药中心，中爱贸易与都柏林投资活跃。本页梳理在爱尔兰最常见的跨境法律事项。",
        "en_intro": "Ireland is a European tech and biopharma hub with active China–Ireland trade and Dublin investment. This page maps the common cross-border matters.",
        "items_zh": ["爱尔兰客户货款追收与律师函", "中国判决在爱尔兰的承认与执行", "爱尔兰公司与资产调查", "跨境继承与爱尔兰 CAT 规划"],
        "items_en": ["Debt recovery & demand letters against Irish buyers", "Recognition & enforcement of Chinese judgments in Ireland", "Tracing Irish company and assets", "Cross-border inheritance & Irish CAT planning"],
        "points_zh": ["中爱无判决互认条约，非欧盟外国判决通常依普通法重新起诉", "合同债务时效一般为 6 年（《时效法 1957》）", "爱尔兰资本取得税（CAT）最高 33%，配偶有高额免税额", "法院程序须由爱尔兰律师代理", "公司登记（CRO）公开，资产调查有渠道"],
        "points_en": ["No bilateral treaty with China; non-EU foreign judgments are usually re-litigated at common law", "Contract debts generally lapse after 6 years (Statute of Limitations 1957)", "Irish Capital Acquisitions Tax (CAT) reaches 33%, with a high spouse allowance", "Irish counsel is required in court proceedings", "Company records (CRO) are public, giving tracing a channel"],
        "faq_zh": [
            "中国法院的判决能在爱尔兰执行吗？|中爱没有判决互认条约，非欧盟外国判决通常需依普通法在爱尔兰重新起诉。",
            "在爱尔兰追收欠款的诉讼时效是多久？|合同债务时效一般为 6 年。",
            "爱尔兰的遗产税高吗？|爱尔兰资本取得税（CAT）最高 33%，配偶享有高额免税额。",
        ],
        "faq_en": [
            "Can a Chinese judgment be enforced in Ireland?|No bilateral treaty exists; non-EU foreign judgments are usually re-litigated at common law in Ireland.",
            "What is the limitation period for collecting a debt in Ireland?|Contract debts generally lapse after 6 years.",
            "Is Irish inheritance tax high?|Irish Capital Acquisitions Tax (CAT) reaches 33%, with a high spouse allowance.",
        ],
    },
}


def _country_faq_jsonld(country: dict) -> str:
    """FAQPage JSON-LD built from the country's faq_zh entries ("Q|A" pairs)."""
    faqs = []
    for entry in country.get("faq_zh", []):
        q, _, a = entry.partition("|")
        if q and a:
            faqs.append(f'{{"@type": "Question", "name": "{html.escape(q)}", '
                        f'"acceptedAnswer": {{"@type": "Answer", "text": "{html.escape(a)}"}}}}')
    if not faqs:
        return ""
    return (
        '<script type="application/ld+json">\n'
        '{\n'
        '  "@context": "https://schema.org",\n'
        '  "@type": "FAQPage",\n'
        '  "mainEntity": [' + ",".join(faqs) + "]\n"
        "}\n"
        "</script>\n"
    )


def _render_country_page(country: dict, slug: str) -> str:
    items = "".join(
        f'<li data-zh="{z}" data-en="{e}">{z}</li>'
        for z, e in zip(country["items_zh"], country["items_en"])
    )
    points = "".join(
        f'<li data-zh="{z}" data-en="{e}">{z}</li>'
        for z, e in zip(country["points_zh"], country["points_en"])
    )
    url = f"{SITE_URL}/countries/{slug}"
    en_url = f"{SITE_URL}/en/countries/{slug}"
    page_css = _PAGE_CSS
    ga_tag = _ga_tag()
    og_image = OG_IMAGE
    faq_jsonld = _country_faq_jsonld(country)
    crumbs_html, crumbs_jsonld = _crumbs([
        ("首页", f"{SITE_URL}/"),
        ("国家专页", f"{SITE_URL}/countries"),
        (country["name_zh"], f"{SITE_URL}/countries/{slug}"),
    ])
    cookie_banner = _cookie_banner()
    related = _related_html(
        _related_articles({"slug": f"__{slug}__", "business": ""}),
        base="/articles",
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow">
  <meta name="description" content="{country['zh_intro']}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{country['zh_title']} | Shenyuan International">
  <meta property="og:description" content="{country['zh_intro']}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{country['zh_title']} | Shenyuan International">
  <meta name="twitter:description" content="{country['zh_intro']}">
  <meta name="twitter:image" content="{og_image}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="zh-CN" href="{url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="x-default" href="{url}">
  {ga_tag}
  <title>{country['zh_title']} | Shenyuan International 深远(国际)律师事务所</title>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "LegalService",
    "name": "Shenyuan International 深远(国际)律师事务所",
    "url": "{url}",
    "description": "{country['zh_intro']}",
    "areaServed": "{country['name_zh']}",
    "knowsLanguage": ["zh", "en"]
  }}
  </script>
  {faq_jsonld}
  {crumbs_jsonld}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
  <style>{page_css}</style>
</head>
<body>
  <div class="topbar">
    <div class="wrap">
      <a class="brand" href="/"><span class="brand-mark">深</span><span>Shenyuan International</span></a>
      <div class="nav-links">
        <a href="/" data-zh="返回首页" data-en="Home">返回首页</a>
        <a href="/countries" data-zh="国家专页" data-en="Country pages">国家专页</a>
        <button class="lang-switch" type="button" id="langToggle" aria-label="切换语言">EN / 中</button>
      </div>
    </div>
  </div>
  <div class="wrap hero">
    {crumbs_html}
    <div class="number" data-zh="国家专页 · {country['name_zh']}" data-en="COUNTRY PAGE · {country['name_en']}">国家专页 · {country['name_zh']}</div>
    <h1 data-zh="{country['zh_title']}" data-en="{country['en_title']}">{country['zh_title']}</h1>
    <div class="en-sub" data-zh="跨境争议解决与家族资产保护" data-en="Cross-border dispute resolution & family asset protection">跨境争议解决与家族资产保护</div>
    <p class="intro" data-zh="{country['zh_intro']}" data-en="{country['en_intro']}">{country['zh_intro']}</p>
  </div>
  <div class="wrap cols">
    <div class="card">
      <h2 data-zh="覆盖服务" data-en="What we cover">覆盖服务</h2>
      <ul>{items}</ul>
    </div>
    <div class="card">
      <h2 data-zh="当地实务要点" data-en="Local practice notes">当地实务要点</h2>
      <ul>{points}</ul>
    </div>
  </div>
  <div class="wrap steps">
    <div class="step"><span>01</span><h3 data-zh="免费咨询建档" data-en="Free consultation & intake">免费咨询建档</h3><p data-zh="提交基本情况，我们梳理人物、金额、时间线与目标。" data-en="Share the essentials; we map the parties, amounts, timeline, and goals.">提交基本情况，我们梳理人物、金额、时间线与目标。</p></div>
    <div class="step"><span>02</span><h3 data-zh="事实、证据与法域评估" data-en="Facts, evidence & jurisdiction">事实、证据与法域评估</h3><p data-zh="识别时效、证据、资产位置与涉及的法域。" data-en="Identify timing, evidence, asset location, and relevant jurisdictions.">识别时效、证据、资产位置与涉及的法域。</p></div>
    <div class="step"><span>03</span><h3 data-zh="策略、报价与执行" data-en="Strategy & execution">策略、报价与执行</h3><p data-zh="确定谈判、追收或诉讼策略，明确材料、风险与里程碑。" data-en="Define the strategy with clear milestones and risk boundaries.">确定谈判、追收或诉讼策略，明确材料、风险与里程碑。</p></div>
  </div>
  <div class="wrap cta">
    <a class="button" href="/#intake" data-zh="免费评估我的案件 →" data-en="Free case assessment →">免费评估我的案件 →</a>
    <p class="note" data-zh="提交不代表建立委托关系。初步咨询不收费，不承诺结果。" data-en="Submitting does not create an attorney-client relationship. Initial consultation is free and honest.">提交不代表建立委托关系。初步咨询不收费，不承诺结果。</p>
  </div>

  {related}

  <footer>
    © 2026 Shenyuan International · 深远(国际)律师事务所<br>
    <span data-zh="境外法律程序通过与当地执业律所合作提供。本页内容不构成法律意见。" data-en="Foreign proceedings are conducted through locally licensed counsel. This page does not constitute legal advice.">境外法律程序通过与当地执业律所合作提供。本页内容不构成法律意见。</span>
  </footer>
  <script>
    (function () {{
      var currentLang = "zh";
      var zhTitle = {country['zh_title']!r};
      var enTitle = {country['en_title']!r};
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
  <div id="chat-widget-root"></div>
  <script src="/static/chat.js" defer></script>
  {cookie_banner}
</body>
</html>"""


_COUNTRY_INDEX_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="深远国际律师事务所国家专页：美国、加拿大、澳大利亚、新加坡、英国——欠款追收、判决执行与跨境继承的当地实务要点。">
  <link rel="canonical" href="{site_url}/countries">
  <link rel="alternate" hreflang="zh-CN" href="{site_url}/countries">
  <link rel="alternate" hreflang="en" href="{site_url}/en/countries">
  <link rel="alternate" hreflang="x-default" href="{site_url}/countries">
  {ga_tag}
  <title>国家专页 | Shenyuan International 深远(国际)律师事务所</title>
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
    .cards {{ display:grid; grid-template-columns:repeat(2, 1fr); gap:18px; padding-bottom:80px; }}
    .c-card {{ padding:28px; background:var(--surface); border:1px solid var(--line); border-radius:10px; transition:transform .2s ease, box-shadow .2s ease; }}
    .c-card:hover {{ transform:translateY(-3px); box-shadow:0 20px 50px rgba(20,33,44,.11); }}
    .c-name {{ color:var(--gold); font-size:12px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }}
    .c-card h2 {{ margin-top:12px; font-size:20px; }}
    .c-card p {{ margin-top:9px; color:var(--muted); font-size:13.5px; line-height:1.6; }}
    .c-more {{ display:inline-block; margin-top:14px; color:var(--teal); font-size:13px; font-weight:800; }}
    footer {{ background:#15232d; color:rgba(255,255,255,.72); font-size:12px; padding:22px 0; text-align:center; }}
    footer a {{ color:rgba(255,255,255,.85); }}
    @media (max-width:720px) {{ .cards {{ grid-template-columns:1fr; }} .topbar .wrap {{ min-height:60px; }} }}
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
    <div class="eyebrow" data-zh="国家专页" data-en="Country pages">国家专页</div>
    <h1 data-zh="客户在哪里，协作网络就在哪里。" data-en="Where our clients are, our network follows.">客户在哪里，协作网络就在哪里。</h1>
    <p data-zh="每个国家专页梳理当地最常见的跨境法律事项：欠款追收、判决执行与跨境继承的实务要点与处理路径。" data-en="Each country page maps the most common cross-border matters: debt recovery, judgment enforcement, and inheritance — with local practice notes and a clear path forward.">每个国家专页梳理当地最常见的跨境法律事项：欠款追收、判决执行与跨境继承的实务要点与处理路径。</p>
  </div>
  <div class="wrap cards">{cards}</div>
  <footer>© 2026 Shenyuan International · 深远(国际)律师事务所 · <a href="/">返回首页</a></footer>
  <script>
    (function () {{
      var currentLang = "zh";
      document.getElementById("langToggle").addEventListener("click", function () {{
        currentLang = currentLang === "zh" ? "en" : "zh";
        document.documentElement.lang = currentLang === "zh" ? "zh-CN" : "en";
        document.title = currentLang === "zh" ? "国家专页 | Shenyuan International 深远(国际)律师事务所" : "Country Pages | Shenyuan International";
        document.querySelectorAll("[data-zh][data-en]").forEach(function (node) {{
          node.textContent = currentLang === "zh" ? node.getAttribute("data-zh") : node.getAttribute("data-en");
        }});
      }});
    }}());
  </script>
  <div id="chat-widget-root"></div>
  <script src="/static/chat.js" defer></script>
  {cookie_banner}
</body>
</html>"""


def _countries_index_html() -> str:
    cards = []
    for slug, c in COUNTRIES.items():
        cards.append(
            '<article class="c-card">'
            f'<div class="c-name" data-zh="{c["name_zh"]}" data-en="{c["name_en"]}">{c["name_zh"]}</div>'
            f'<a href="/countries/{slug}"><h2 data-zh="{html.escape(c["zh_title"])}" data-en="{html.escape(c["en_title"])}">{html.escape(c["zh_title"])}</h2></a>'
            f'<p data-zh="{html.escape(c["zh_intro"])}" data-en="{html.escape(c["en_intro"])}">{html.escape(c["zh_intro"])}</p>'
            f'<a class="c-more" href="/countries/{slug}" data-zh="查看专页 →" data-en="View page →">查看专页 →</a>'
            "</article>"
        )
    return _COUNTRY_INDEX_TEMPLATE.format(
        site_url=SITE_URL, cards="\n".join(cards), ga_tag=_ga_tag(), cookie_banner=_cookie_banner()
    )


@app.api_route("/countries", methods=["GET", "HEAD"], include_in_schema=False)
def countries_index() -> Response:
    return Response(content=_countries_index_html(), media_type="text/html; charset=utf-8")


@app.api_route("/countries/{slug}", methods=["GET", "HEAD"], include_in_schema=False)
def country_page(slug: str) -> Response:
    country = COUNTRIES.get(slug)
    if country is None:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(
        content=_render_country_page(country, slug),
        media_type="text/html; charset=utf-8",
    )


@app.api_route("/en/countries/{slug}", methods=["GET", "HEAD"], include_in_schema=False)
def country_page_en(slug: str) -> Response:
    country = COUNTRIES.get(slug)
    if country is None:
        raise HTTPException(status_code=404, detail="Not found")
    page = _en_variant(_render_country_page(country, slug))
    page = _swap_meta(page, "meta name=\"description\"", html.escape(country["en_intro"]))
    page = _swap_meta(page, "meta property=\"og:title\"", html.escape(country["en_title"]) + " | Shenyuan International")
    page = _swap_meta(page, "meta property=\"og:description\"", html.escape(country["en_intro"]))
    page = re.sub(
        r"(<title>)[^<]*(</title>)",
        rf"\g<1>{html.escape(country['en_title'])} | Shenyuan International\g<2>",
        page,
        count=1,
    )
    page = page.replace(
        f'<link rel="canonical" href="{SITE_URL}/countries/{slug}">',
        f'<link rel="canonical" href="{SITE_URL}/en/countries/{slug}">',
    )
    return Response(content=page, media_type="text/html; charset=utf-8")


@app.api_route("/en/countries", methods=["GET", "HEAD"], include_in_schema=False)
def countries_index_en() -> Response:
    page = _en_variant(_countries_index_html())
    page = _swap_meta(
        page,
        "meta name=\"description\"",
        "Shenyuan International country pages: United States, Canada, Australia, "
        "Singapore, United Kingdom — local practice notes on debt recovery, "
        "judgment enforcement, and inheritance.",
    )
    page = page.replace(
        f'<link rel="canonical" href="{SITE_URL}/countries">',
        f'<link rel="canonical" href="{SITE_URL}/en/countries">',
    )
    return Response(content=page, media_type="text/html; charset=utf-8")


@app.get("/static/chat.js", include_in_schema=False)
def chat_widget_js() -> FileResponse:
    """The AI 咨询助手 widget script (self-contained: styles + flow + submit)."""
    path = ROOT_DIR / "app" / "static" / "chat.js"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="chat.js not found")
    return FileResponse(path, media_type="application/javascript")


@app.get("/wechat-qrcode.png", include_in_schema=False)
def wechat_qrcode() -> FileResponse:
    """Real WeChat QR code for the contact section and success modal."""
    path = ROOT_DIR / "wechat-qrcode.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="QR code image not found")
    return FileResponse(path, media_type="image/png")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/vcard.vcf", include_in_schema=False)
def vcard() -> Response:
    """Electronic business card (vCard 3.0). Contact info via env; 404 when unset."""
    name = os.environ.get("CONTACT_NAME", "Shenyuan International 深远(国际)律师事务所")
    email = os.environ.get("CONTACT_EMAIL", "")
    phone = os.environ.get("CONTACT_PHONE", "")
    if not (email or phone):
        raise HTTPException(status_code=404, detail="Contact not configured")
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"FN:{name}", f"ORG:{name}", f"URL:{SITE_URL}"]
    if email:
        lines.append(f"EMAIL:{email}")
    if phone:
        lines.append(f"TEL:{phone}")
    lines.append("END:VCARD")
    return Response(content="\n".join(lines) + "\n", media_type="text/vcard; charset=utf-8")


@app.get("/admin", include_in_schema=False)
def admin_page() -> FileResponse:
    """Admin dashboard shell. The page itself is unauthenticated; every API
    call it makes carries the bearer token from the login form."""
    return FileResponse(ROOT_DIR / "admin.html")


@app.get("/admin/marketing", include_in_schema=False)
def admin_marketing_page() -> FileResponse:
    """Marketing Agent console: generate & copy the full collateral bundle."""
    return FileResponse(ROOT_DIR / "admin_marketing.html")


@app.get("/admin/api/articles", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_list_articles(request: Request) -> list[dict]:
    """Articles for the marketing console dropdown (newest first)."""
    _require_admin(request)
    return [
        {
            "slug": a["meta"]["slug"],
            "title_zh": a["meta"].get("title_zh", ""),
            "title_en": a["meta"].get("title_en", ""),
            "date": a["meta"].get("date", ""),
            "business": _business_key(a["meta"].get("business", "")),
            "url": f"{SITE_URL}/articles/{a['meta']['slug']}",
        }
        for a in _load_articles()
    ]


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
    overdue = _overdue_leads()
    return {
        "intakes_total": intakes_total,
        "intakes_today": intakes_today,
        "intakes_week": intakes_week,
        "views_total": views_total,
        "views_today": views_today,
        "conversion_today_pct": conversion,
        "by_status": by_status,
        "by_matter": by_matter,
        "crm_overdue": len(overdue),
        "crm_overdue_new": sum(1 for lead in overdue if lead["status"] == "new"),
        "crm_overdue_progress": sum(1 for lead in overdue if lead["status"] == "contacted"),
    }


@app.get("/admin/api/intakes/sources", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_intake_sources(request: Request) -> list[dict]:
    """Lead counts by acquisition source (utm_source; empty -> direct)."""
    _require_admin(request)
    with db_connection() as connection:
        rows = connection.execute(
            "SELECT COALESCE(NULLIF(TRIM(source), ''), 'direct') AS src, COUNT(*) AS n "
            "FROM intakes GROUP BY src ORDER BY n DESC, src"
        ).fetchall()
    return [{"source": r["src"], "count": r["n"]} for r in rows]


@app.get("/admin/api/crm/overdue", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_crm_overdue(request: Request) -> dict:
    """CRM Agent: leads past their follow-up SLA, highest score first."""
    _require_admin(request)
    leads = _overdue_leads()
    stale = _stale_leads()
    return {
        "count": len(leads),
        "first_sla_hours": _crm_first_sla_hours(),
        "progress_sla_days": _crm_progress_sla_days(),
        "leads": leads,
        "stale_count": len(stale),
        "stale": stale,
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
    # CRM: any status/note change counts as a touch (resets the SLA clock).
    updates.append("updated_at = ?")
    params.append(datetime.now(timezone.utc).isoformat())

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
    score = _lead_score(
        payload.name,
        payload.summary,
        payload.matter,
        email=payload.email,
        phone=payload.phone or "",
    )

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
                    language, user_agent, created_at, status, note, consent_at,
                    score, updated_at, source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', NULL, ?, ?, ?, ?)
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
                    score,
                    created_at,
                    payload.source,
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


@app.post("/api/intakes/chat", response_model=IntakeCreated, status_code=201)
@limiter.limit(INTAKE_RATE_LIMIT)
def create_chat_intake(
    payload: ChatIntakeCreate,
    request: Request,
    background_tasks: BackgroundTasks,
) -> IntakeCreated:
    """Save a guided-chat intake from the AI 咨询助手 widget.

    The widget collects the same core fields as the form (structured), and the
    server re-classifies the matter with keyword triage so a visitor's free
    description can override their quick pick. Structured fields land in the
    `note` column so admin triage sees them without opening files.
    """
    if not payload.consent:
        raise HTTPException(
            status_code=400,
            detail="需要同意隐私说明后才能提交 / Please accept the privacy notice to continue",
        )
    matter_key = _classify_matter(payload.summary, payload.matter)
    matter_label = _MATTER_LABEL_BY_KEY[matter_key]
    email, phone = _split_contact(payload.contact)
    created_at = datetime.now(timezone.utc).isoformat()
    user_agent = request.headers.get("user-agent")
    score = _lead_score(
        payload.name,
        payload.summary,
        matter_label,
        amount=payload.amount,
        evidence=payload.evidence,
        email=email,
        phone=phone,
    )

    note_parts = ["来源：AI 咨询助手"]
    for label, value in (
        ("主体", payload.parties),
        ("金额", payload.amount),
        ("时间", payload.timeline),
        ("证据", payload.evidence),
        ("诉求", payload.goal),
    ):
        if value:
            note_parts.append(f"{label}：{value}")
    if payload.transcript:
        note_parts.append(f"对话记录：{payload.transcript[:3800]}")
    note = "\n".join(note_parts)[:2000]

    try:
        with db_connection() as connection:
            cutoff = (
                datetime.now(timezone.utc) - timedelta(hours=_dedupe_window_hours())
            ).isoformat()
            duplicate = connection.execute(
                """
                SELECT id FROM intakes
                WHERE created_at > ?
                  AND ((email != '' AND email = ?) OR (phone != '' AND ? != '' AND phone = ?))
                LIMIT 1
                """,
                (cutoff, email, phone, phone),
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
                    language, user_agent, created_at, status, note, consent_at,
                    score, updated_at, source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?, ?, ?, ?)
                """,
                (
                    payload.name,
                    email,
                    phone,
                    matter_label,
                    payload.summary,
                    payload.country,
                    payload.language,
                    user_agent,
                    created_at,
                    note,
                    created_at,
                    score,
                    created_at,
                    payload.source,
                ),
            )
    except sqlite3.Error:
        logger.exception("Failed to save chat intake for %s", payload.contact)
        raise HTTPException(status_code=500, detail="Failed to save consultation") from None

    background_tasks.add_task(
        _send_intake_notification,
        {
            "name": payload.name,
            "email": email or "-",
            "phone": phone,
            "country": payload.country,
            "matter": matter_label,
            "summary": payload.summary,
            "language": payload.language,
            "created_at": created_at,
        },
    )
    if email:
        background_tasks.add_task(
            _send_auto_reply,
            {
                "name": payload.name,
                "email": email,
                "matter": matter_label,
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
