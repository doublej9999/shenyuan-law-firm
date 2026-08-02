from __future__ import annotations

import re
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator


ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "lawyers.sqlite3"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS intakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                matter TEXT NOT NULL,
                summary TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT 'zh',
                user_agent TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        migrate_intakes_schema(connection)


def migrate_intakes_schema(connection: sqlite3.Connection) -> None:
    columns = [row["name"] for row in connection.execute("PRAGMA table_info(intakes)")]
    if "country_or_region" not in columns:
        return

    connection.execute("ALTER TABLE intakes RENAME TO intakes_old")
    connection.execute(
        """
        CREATE TABLE intakes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            matter TEXT NOT NULL,
            summary TEXT NOT NULL,
            language TEXT NOT NULL DEFAULT 'zh',
            user_agent TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO intakes (
            id, name, email, phone, matter, summary,
            language, user_agent, created_at
        )
        SELECT
            id, name, email, phone, matter, summary,
            language, user_agent, created_at
        FROM intakes_old
        """
    )
    connection.execute("DROP TABLE intakes_old")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Profound Law Firm", version="0.1.0", lifespan=lifespan)


class IntakeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=80)]
    email: Annotated[str, Field(min_length=3, max_length=254)]
    matter: Annotated[str, Field(min_length=1, max_length=80)]
    summary: Annotated[str, Field(min_length=1, max_length=2000)]
    phone: Annotated[str | None, Field(max_length=60)] = None
    language: Annotated[str, Field(pattern="^(zh|en)$")] = "zh"

    @field_validator("name", "email", "phone", "matter", "summary", mode="before")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return str(value).strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
            raise ValueError("Invalid email address")
        return value

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
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


@app.post("/api/intakes", response_model=IntakeCreated, status_code=201)
async def create_intake(payload: IntakeCreate, request: Request) -> IntakeCreated:
    created_at = datetime.now(timezone.utc).isoformat()
    user_agent = request.headers.get("user-agent")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO intakes (
                    name, email, phone, matter, summary,
                    language, user_agent, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.name,
                    payload.email,
                    payload.phone,
                    payload.matter,
                    payload.summary,
                    payload.language,
                    user_agent,
                    created_at,
                ),
            )
    except sqlite3.Error as exc:
        raise HTTPException(status_code=500, detail="Failed to save consultation") from exc

    return IntakeCreated(id=cursor.lastrowid, status="created", created_at=created_at)
