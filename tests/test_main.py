"""Tests for schema migration, validation, intake API, notifications,
admin API, and the lead status workflow.

Run with: pytest
"""

import sqlite3

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app.main as m

# Simulates a v2-era schema (country_or_region present, no status/note/consent_at).
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

VALID_PAYLOAD = {
    "name": "张三",
    "email": "z@test.com",
    "matter": "国际贸易争议",
    "summary": "客户拖欠尾款",
    "country": "美国",
    "consent": True,
}


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


def test_fresh_init_creates_full_schema(tmp_db):
    m.init_db()
    cols, version = table_info(tmp_db)
    for col in ("country_or_region", "status", "note", "consent_at"):
        assert col in cols
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


def test_v2_db_migrates_to_v3_preserving_rows(tmp_path, monkeypatch):
    db = tmp_path / "lawyers.sqlite3"
    make_legacy_db(db, with_country_col=True, rows=2)
    monkeypatch.setattr(m, "DB_PATH", db)

    m.init_db()

    cols, version = table_info(db)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM intakes").fetchall()
    conn.close()
    assert "status" in cols and "note" in cols and "consent_at" in cols
    assert len(rows) == 2
    assert all(r["status"] == "new" for r in rows)
    assert version == m.SCHEMA_VERSION


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
        m.IntakeCreate(name="x", email="not-an-email", matter="m", summary="s", consent=True)


def test_language_validation():
    with pytest.raises(ValidationError):
        m.IntakeCreate(name="x", email="a@b.com", matter="m", summary="s", language="fr", consent=True)


def test_fields_are_trimmed():
    payload = m.IntakeCreate(
        name="  王女士  ", email="  a@b.com  ", matter=" 贸易 ", summary=" 欠款 ", consent=True
    )
    assert payload.name == "王女士"
    assert payload.email == "a@b.com"
    assert payload.matter == "贸易"


def test_empty_phone_and_country_become_none():
    payload = m.IntakeCreate(
        name="x", email="a@b.com", matter="m", summary="s",
        phone="", country="", consent=True,
    )
    assert payload.phone is None
    assert payload.country is None


def test_consent_is_required():
    with pytest.raises(ValidationError):
        m.IntakeCreate(name="x", email="a@b.com", matter="m", summary="s", consent=False)


# --- Intake API --------------------------------------------------------


def test_post_intake_stores_country_and_consent(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post("/api/intakes", json=VALID_PAYLOAD)
        assert resp.status_code == 201
        assert resp.json()["status"] == "created"
        assert resp.json()["id"] == 1

        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        assert row["country_or_region"] == "美国"
        assert row["language"] == "zh"
        assert row["status"] == "new"
        assert row["consent_at"] is not None
        assert row["consent_at"] == row["created_at"]


def test_post_intake_without_optional_fields(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes",
            json={
                "name": "李四", "email": "l@test.com", "matter": "继承",
                "summary": "遗嘱争议", "consent": True,
            },
        )
        assert resp.status_code == 201
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        assert row["country_or_region"] is None
        assert row["phone"] is None


def test_api_rejects_missing_consent(tmp_db):
    with TestClient(m.app) as client:
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "consent"}
        resp = client.post("/api/intakes", json=payload)
        assert resp.status_code == 422


def test_api_rejects_invalid_email(tmp_db):
    with TestClient(m.app) as client:
        payload = dict(VALID_PAYLOAD, email="bad")
        resp = client.post("/api/intakes", json=payload)
        assert resp.status_code == 422


def test_health(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_rate_limit_returns_429(tmp_db):
    payload = dict(VALID_PAYLOAD, email="x@test.com", name="x", matter="m", summary="s")
    with TestClient(m.app) as client:
        statuses = [client.post("/api/intakes", json=payload).status_code for _ in range(6)]
    assert statuses[:5] == [201] * 5
    assert statuses[5] == 429


# --- Notifications -----------------------------------------------------


def test_intake_sends_notification(tmp_db, monkeypatch):
    sent = {}
    monkeypatch.setattr(m, "_send_intake_notification", lambda intake: sent.update(intake))
    with TestClient(m.app) as client:
        resp = client.post("/api/intakes", json=VALID_PAYLOAD)
        assert resp.status_code == 201
    assert sent.get("name") == "张三"
    assert sent.get("matter") == "国际贸易争议"
    assert sent.get("country") == "美国"


def test_notification_without_webhook_url_is_noop(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.delenv("NOTIFY_WEBHOOK_URL", raising=False)
    try:
        # Real function, no URL configured: must not raise.
        m._send_intake_notification(VALID_PAYLOAD)
    finally:
        monkeypatch.undo()


# --- Admin API ---------------------------------------------------------


def test_admin_page_served(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert "管理后台" in resp.text


def test_admin_list_requires_token(tmp_db):
    with TestClient(m.app) as client:
        assert client.get("/admin/api/intakes").status_code == 401


def test_admin_list_and_update_workflow(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            headers = {"Authorization": "Bearer secret-token"}
            client.post("/api/intakes", json=VALID_PAYLOAD)

            rows = client.get("/admin/api/intakes", headers=headers).json()
            assert len(rows) == 1
            assert rows[0]["status"] == "new"

            # Filter by status
            rows = client.get("/admin/api/intakes?status=new", headers=headers).json()
            assert len(rows) == 1
            rows = client.get("/admin/api/intakes?status=closed", headers=headers).json()
            assert rows == []

            # Search by name
            rows = client.get("/admin/api/intakes?q=张三", headers=headers).json()
            assert len(rows) == 1
            rows = client.get("/admin/api/intakes?q=不存在", headers=headers).json()
            assert rows == []

            # Status + note update
            resp = client.patch(
                "/admin/api/intakes/1",
                headers=headers,
                json={"status": "contacted", "note": "已电话联系，客户在海外"},
            )
            assert resp.status_code == 200
            assert resp.json()["status"] == "contacted"
            assert resp.json()["note"] == "已电话联系，客户在海外"

            rows = client.get("/admin/api/intakes", headers=headers).json()
            assert rows[0]["status"] == "contacted"
    finally:
        monkeypatch.undo()


def test_admin_update_invalid_status_rejected(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            headers = {"Authorization": "Bearer secret-token"}
            client.post("/api/intakes", json=VALID_PAYLOAD)
            resp = client.patch(
                "/admin/api/intakes/1", headers=headers, json={"status": "bogus"}
            )
            assert resp.status_code == 422
    finally:
        monkeypatch.undo()


def test_admin_update_missing_intake_404(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            resp = client.patch(
                "/admin/api/intakes/999",
                headers={"Authorization": "Bearer secret-token"},
                json={"status": "closed"},
            )
            assert resp.status_code == 404
    finally:
        monkeypatch.undo()


def test_admin_update_requires_token(tmp_db):
    with TestClient(m.app) as client:
        resp = client.patch("/admin/api/intakes/1", json={"status": "closed"})
        assert resp.status_code == 401


# --- Admin CSV export --------------------------------------------------


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
            client.post("/api/intakes", json=VALID_PAYLOAD)
            resp = client.get(
                "/admin/intakes.csv",
                headers={"Authorization": "Bearer secret-token"},
            )
            assert resp.status_code == 200
            assert resp.headers["content-type"].startswith("text/csv")
            assert "张三" in resp.text
            assert "country_or_region" in resp.text
            assert "status" in resp.text
            assert "美国" in resp.text
    finally:
        monkeypatch.undo()
