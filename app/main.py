from __future__ import annotations

import csv
import io
import json
import logging
import os
import secrets
import sqlite3
import urllib.request
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Iterator

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, EmailStr, Field, field_validator
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "lawyers.sqlite3"
SCHEMA_VERSION = 3

# Per-IP limit for the public intake form. Prevents spam bots from flooding
# the SQLite database. Humans rarely submit more than a few times a minute.
INTAKE_RATE_LIMIT = "5/minute"
ADMIN_RATE_LIMIT = "30/minute"

# Lead status workflow: 新线索 -> 已联系 -> 处理中 -> 已结案
VALID_STATUSES = ("new", "contacted", "in_progress", "closed")
STATUS_LABELS = {
    "new": "新线索",
    "contacted": "已联系",
    "in_progress": "处理中",
    "closed": "已结案",
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

    logger.info("Migrating intakes schema to version %d", SCHEMA_VERSION)
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


_production = os.environ.get("APP_ENV") == "production"
app = FastAPI(
    title="Profound Law Firm",
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
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            response.read()
    except Exception:
        logger.exception("Failed to send intake notification webhook")


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


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse(ROOT_DIR / "index.html")


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
    if not _is_authorized(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
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


@app.patch("/admin/api/intakes/{intake_id}", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def admin_update_intake(
    intake_id: int, payload: AdminIntakeUpdate, request: Request
) -> dict:
    if not _is_authorized(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

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

    logger.info(
        "Admin updated intake %d (%s) from %s",
        intake_id,
        ", ".join(updates),
        _client_ip(request),
    )
    return dict(row)


@app.get("/admin/intakes.csv", include_in_schema=False)
@limiter.limit(ADMIN_RATE_LIMIT)
def export_intakes(request: Request) -> Response:
    """Export all intakes as CSV. Protected by the ADMIN_TOKEN bearer token."""
    if not _is_authorized(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    with db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, name, email, phone, country_or_region,
                   matter, summary, language, status, note, consent_at
            FROM intakes
            ORDER BY id DESC
            """
        ).fetchall()

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

    return IntakeCreated(id=cursor.lastrowid, status="created", created_at=created_at)
