"""Tests for schema migration, validation, and the intake API.

Run with: pytest
"""

import sqlite3

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app.main as m

LEGACY_SCHEMA = """
CREATE TABLE intakes (
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


@pytest.fixture(autouse=True)
def _reset_limiter():
    """Rate-limit buckets are global per app instance; reset between tests."""
    limiter = getattr(m.app.state, "limiter", None)
    if limiter is not None:
        limiter.reset()
    yield


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    db = tmp_path / "lawyers.sqlite3"
    monkeypatch.setattr(m, "DB_PATH", db)
    return db


def make_legacy_db(path, with_country_col=True, rows=1):
    conn = sqlite3.connect(path)
    if with_country_col:
        conn.execute(LEGACY_SCHEMA)
    else:
        conn.execute(LEGACY_SCHEMA.replace(",\n    country_or_region TEXT", ""))
    for i in range(rows):
        if with_country_col:
            conn.execute(
                "INSERT INTO intakes (name,email,matter,summary,country_or_region,created_at)"
                " VALUES (?,?,?,?,?,?)",
                ("王女士", f"w{i}@example.com", "贸易", "客户欠款", "美国",
                 "2026-01-01T00:00:00+00:00"),
            )
        else:
            conn.execute(
                "INSERT INTO intakes (name,email,matter,summary,created_at)"
                " VALUES (?,?,?,?,?)",
                ("王女士", f"w{i}@example.com", "贸易", "客户欠款",
                 "2026-01-01T00:00:00+00:00"),
            )
    conn.commit()
    conn.close()


def table_info(db):
    conn = sqlite3.connect(db)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(intakes)")]
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.close()
    return cols, version


# --- Migration ---------------------------------------------------------


def test_fresh_init_creates_schema_with_country(tmp_db):
    m.init_db()
    cols, version = table_info(tmp_db)
    assert "country_or_region" in cols
    assert version == m.SCHEMA_VERSION


def test_legacy_db_with_column_preserves_data(tmp_path, monkeypatch):
    db = tmp_path / "lawyers.sqlite3"
    make_legacy_db(db, with_country_col=True)
    monkeypatch.setattr(m, "DB_PATH", db)

    m.init_db()

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT country_or_region FROM intakes").fetchone()
    conn.close()
    assert row["country_or_region"] == "美国"


def test_legacy_db_without_column_adds_it_and_preserves_rows(tmp_path, monkeypatch):
    db = tmp_path / "lawyers.sqlite3"
    make_legacy_db(db, with_country_col=False, rows=2)
    monkeypatch.setattr(m, "DB_PATH", db)

    m.init_db()

    cols, version = table_info(db)
    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM intakes").fetchone()[0]
    conn.close()
    assert "country_or_region" in cols
    assert count == 2
    assert version == m.SCHEMA_VERSION


def test_migration_is_idempotent(tmp_db):
    m.init_db()
    cols1, version1 = table_info(tmp_db)
    m.init_db()
    cols2, version2 = table_info(tmp_db)
    assert cols1 == cols2
    assert version1 == version2 == m.SCHEMA_VERSION


# --- Validation ---------------------------------------------------------


def test_email_validation():
    with pytest.raises(ValidationError):
        m.IntakeCreate(name="x", email="not-an-email", matter="m", summary="s")


def test_language_validation():
    with pytest.raises(ValidationError):
        m.IntakeCreate(name="x", email="a@b.com", matter="m", summary="s", language="fr")


def test_fields_are_trimmed():
    payload = m.IntakeCreate(
        name="  王女士  ", email="  a@b.com  ", matter=" 贸易 ", summary=" 欠款 "
    )
    assert payload.name == "王女士"
    assert payload.email == "a@b.com"
    assert payload.matter == "贸易"


def test_empty_phone_and_country_become_none():
    payload = m.IntakeCreate(
        name="x", email="a@b.com", matter="m", summary="s", phone="", country=""
    )
    assert payload.phone is None
    assert payload.country is None


# --- API ----------------------------------------------------------------


def test_post_intake_stores_country(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes",
            json={
                "name": "张三",
                "email": "z@test.com",
                "matter": "国际贸易争议",
                "summary": "客户拖欠尾款",
                "country": "美国",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "created"
        assert resp.json()["id"] == 1

        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        assert row["country_or_region"] == "美国"
        assert row["language"] == "zh"


def test_post_intake_without_optional_fields(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes",
            json={"name": "李四", "email": "l@test.com", "matter": "继承", "summary": "遗嘱争议"},
        )
        assert resp.status_code == 201
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        assert row["country_or_region"] is None
        assert row["phone"] is None


def test_api_rejects_invalid_email(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes",
            json={"name": "x", "email": "bad", "matter": "m", "summary": "s"},
        )
        assert resp.status_code == 422


def test_health(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_rate_limit_returns_429(tmp_db):
    payload = {"name": "x", "email": "x@test.com", "matter": "m", "summary": "s"}
    with TestClient(m.app) as client:
        statuses = [client.post("/api/intakes", json=payload).status_code for _ in range(6)]
    assert statuses[:5] == [201] * 5
    assert statuses[5] == 429


# --- Admin export -------------------------------------------------------


def test_admin_export_disabled_without_token(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    try:
        with TestClient(m.app) as client:
            assert client.get("/admin/intakes.csv").status_code == 401
            assert (
                client.get(
                    "/admin/intakes.csv",
                    headers={"Authorization": "Bearer wrong-token"},
                ).status_code
                == 401
            )
    finally:
        monkeypatch.undo()


def test_admin_export_with_token(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            client.post(
                "/api/intakes",
                json={
                    "name": "张三",
                    "email": "z@test.com",
                    "matter": "国际贸易争议",
                    "summary": "客户拖欠尾款",
                    "country": "美国",
                },
            )
            resp = client.get(
                "/admin/intakes.csv",
                headers={"Authorization": "Bearer secret-token"},
            )
            assert resp.status_code == 200
            assert resp.headers["content-type"].startswith("text/csv")
            assert "张三" in resp.text
            assert "country_or_region" in resp.text
            assert "美国" in resp.text
    finally:
        monkeypatch.undo()
