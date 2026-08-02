from __future__ import annotations

import csv
import io
import logging
import os
import secrets
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Iterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, EmailStr, Field, field_validator
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "lawyers.sqlite3"
SCHEMA_VERSION = 2

# Per-IP limit for the public intake form. Prevents spam bots from flooding
# the SQLite database. Humans rarely submit more than a few times a minute.
INTAKE_RATE_LIMIT = "5/minute"


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
                created_at TEXT NOT NULL
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
        # v2: add the country/region field called for by design-sketch.md.
        # The previous migration renamed + recreated the table, silently
        # dropping this column and its data — ADD COLUMN preserves rows.
        connection.execute("ALTER TABLE intakes ADD COLUMN country_or_region TEXT")

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


class IntakeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=80)]
    email: Annotated[EmailStr, Field(min_length=3, max_length=254)]
    matter: Annotated[str, Field(min_length=1, max_length=80)]
    summary: Annotated[str, Field(min_length=1, max_length=2000)]
    phone: Annotated[str | None, Field(max_length=60)] = None
    country: Annotated[str | None, Field(max_length=80)] = None
    language: Annotated[str, Field(pattern="^(zh|en)$")] = "zh"

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


def _admin_token() -> str:
    """Bearer token for the admin export. Read per-request so tests can
    override it via the environment; empty means the endpoint is disabled."""
    return os.environ.get("ADMIN_TOKEN", "")


def _is_authorized(request: Request) -> bool:
    token = _admin_token()
    if not token:
        return False
    provided = request.headers.get("authorization", "")
    if provided.startswith("Bearer "):
        provided = provided[len("Bearer ") :].strip()
    return secrets.compare_digest(provided, token)


@app.get("/admin/intakes.csv", include_in_schema=False)
@limiter.limit("10/minute")
def export_intakes(request: Request) -> Response:
    """Export all intakes as CSV. Protected by the ADMIN_TOKEN bearer token."""
    if not _is_authorized(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

    with db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, name, email, phone, country_or_region,
                   matter, summary, language
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
def create_intake(payload: IntakeCreate, request: Request) -> IntakeCreated:
    """Save an intake form submission.

    Sync def on purpose: FastAPI runs sync endpoints in a threadpool, so the
    blocking SQLite write never stalls the async event loop.
    """
    created_at = datetime.now(timezone.utc).isoformat()
    user_agent = request.headers.get("user-agent")

    try:
        with db_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO intakes (
                    name, email, phone, matter, summary,
                    country_or_region, language, user_agent, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                ),
            )
    except sqlite3.Error:
        logger.exception("Failed to save intake for %s", payload.email)
        raise HTTPException(status_code=500, detail="Failed to save consultation") from None

    return IntakeCreated(id=cursor.lastrowid, status="created", created_at=created_at)
