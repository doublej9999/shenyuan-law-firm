"""Tests for schema migration, validation, intake API, notifications,
admin API, and the lead status workflow.

Run with: pytest
"""

import io
import json
import logging
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
    "phone": "13800138000",
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
    monkeypatch.setattr(m, "FILES_DIR", tmp_path / "files")
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
        name="  王女士  ", email="  a@b.com  ", phone=" 138 ", matter=" 贸易 ",
        summary=" 欠款 ", consent=True,
    )
    assert payload.name == "王女士"
    assert payload.email == "a@b.com"
    assert payload.phone == "138"
    assert payload.matter == "贸易"


def test_empty_phone_and_country_become_none():
    payload = m.IntakeCreate(
        name="x", email="a@b.com", matter="m", summary="s",
        phone="123", country="", consent=True,
    )
    assert payload.phone == "123"
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
        # Phone-only lead: no email, no country.
        resp = client.post(
            "/api/intakes",
            json={
                "name": "李四", "phone": "13900000000", "matter": "继承",
                "summary": "遗嘱争议", "consent": True,
            },
        )
        assert resp.status_code == 201
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        assert row["country_or_region"] is None
        assert row["email"] is None
        assert row["phone"] == "13900000000"
        # Phone is now required: omitting it fails validation.
        bad = client.post(
            "/api/intakes",
            json={
                "name": "李四", "email": "l@test.com", "matter": "继承",
                "summary": "遗嘱争议", "consent": True,
            },
        )
        assert bad.status_code == 422


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


def test_wechat_qrcode_served(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/wechat-qrcode.png")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("image/png")
        assert resp.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_rate_limit_returns_429(tmp_db):
    with TestClient(m.app) as client:
        # Unique emails so the dedupe check never fires; the rate limiter is
        # keyed by client IP, which stays the same.
        # 6 次提交去重测试：email 和 phone 都要唯一
        statuses = [
            client.post(
                "/api/intakes",
                json=dict(VALID_PAYLOAD, email=f"x{i}@test.com", phone=f"13{i}00000000", name="x", matter="m", summary="s"),
            ).status_code
            for i in range(6)
        ]
    assert statuses[:5] == [201] * 5
    assert statuses[5] == 429


# --- Duplicate detection ----------------------------------------------


def test_duplicate_email_rejected(tmp_db):
    with TestClient(m.app) as client:
        assert client.post("/api/intakes", json=VALID_PAYLOAD).status_code == 201
        resp = client.post("/api/intakes", json=VALID_PAYLOAD)
        assert resp.status_code == 409
        assert "请勿重复提交" in resp.json()["detail"]


def test_duplicate_phone_rejected(tmp_db):
    with TestClient(m.app) as client:
        p1 = dict(VALID_PAYLOAD, email="a1@test.com", phone="+1 555 0100")
        p2 = dict(VALID_PAYLOAD, email="a2@test.com", phone="+1 555 0100")
        assert client.post("/api/intakes", json=p1).status_code == 201
        assert client.post("/api/intakes", json=p2).status_code == 409


def test_same_email_after_window_allowed(tmp_db, monkeypatch):
    monkeypatch.setenv("DEDUPE_WINDOW_HOURS", "0")
    with TestClient(m.app) as client:
        assert client.post("/api/intakes", json=VALID_PAYLOAD).status_code == 201
        assert client.post("/api/intakes", json=VALID_PAYLOAD).status_code == 201


# --- Auto-reply email --------------------------------------------------


def test_intake_triggers_auto_reply(tmp_db, monkeypatch):
    sent = {}
    monkeypatch.setattr(m, "_send_auto_reply", lambda intake: sent.update(intake))
    with TestClient(m.app) as client:
        resp = client.post("/api/intakes", json=VALID_PAYLOAD)
        assert resp.status_code == 201
    assert sent.get("email") == "z@test.com"
    assert sent.get("matter") == "国际贸易争议"


def test_auto_reply_disabled_without_key(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    try:
        m._send_auto_reply({"name": "x", "email": "x@test.com", "matter": "贸易", "summary": "s"})
    finally:
        monkeypatch.undo()


class _FakeResponse:
    def __init__(self, body=b"{}"):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


def test_resend_request_shape_and_success(tmp_db, monkeypatch, caplog):
    captured = {}
    monkeypatch.setenv("RESEND_API_KEY", "re_test_123")

    def fake_urlopen(request, timeout=10):
        captured["url"] = request.full_url
        captured["auth"] = request.get_header("Authorization")
        # urllib stores headers capitalized ("Content-type"); HTTP headers
        # are case-insensitive, so the server sees Content-Type correctly.
        captured["content_type"] = request.get_header("Content-type")
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return _FakeResponse(b'{"id":"abc123"}')

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with caplog.at_level(logging.INFO):
        m._send_auto_reply({"name": "王女士", "email": "w@example.com", "matter": "国际贸易争议", "summary": "欠款"})

    assert captured["url"] == "https://api.resend.com/emails"
    assert captured["auth"] == "Bearer re_test_123"
    assert captured["content_type"] == "application/json"
    assert captured["body"]["from"] == "no-reply@shenyuanlegal.com"
    assert captured["body"]["to"] == ["w@example.com"]
    assert "已收到您的咨询信息" in captured["body"]["subject"]
    assert "合同、订单、发票、付款记录" in captured["body"]["text"]
    assert "<html>" in captured["body"]["html"]
    assert "合同、订单、发票、付款记录" in captured["body"]["html"]
    assert "Auto-reply sent" in caplog.text


def test_resend_from_override(tmp_db, monkeypatch):
    captured = {}
    monkeypatch.setenv("RESEND_API_KEY", "re_test_123")
    monkeypatch.setenv("RESEND_FROM", "custom@shenyuanlegal.com")

    def fake_urlopen(request, timeout=10):
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return _FakeResponse(b'{"id":"x"}')

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    m._send_auto_reply({"name": "x", "email": "a@b.com", "matter": "贸易", "summary": "s"})
    assert captured["body"]["from"] == "custom@shenyuanlegal.com"


def test_resend_rejection_is_logged(tmp_db, monkeypatch, caplog):
    monkeypatch.setenv("RESEND_API_KEY", "re_test_123")

    def fake_urlopen(request, timeout=10):
        raise urllib.error.HTTPError(
            "https://api.resend.com/emails",
            401,
            "Unauthorized",
            {},
            io.BytesIO(b'{"statusCode":401,"message":"API key invalid","name":"authentication_error"}'),
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with caplog.at_level(logging.ERROR):
        m._send_auto_reply({"name": "x", "email": "a@b.com", "matter": "贸易", "summary": "s"})
    assert "Resend rejected" in caplog.text
    assert "API key invalid" in caplog.text


# --- Admin file management --------------------------------------------
# The public upload entry was removed; previously uploaded files remain
# viewable/downloadable by admins. Seed rows directly to test this path.


def test_admin_list_and_download_file(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            intake_id = client.post("/api/intakes", json=VALID_PAYLOAD).json()["id"]
            stored = "abc123.pdf"
            target = m.FILES_DIR / str(intake_id)
            target.mkdir(parents=True, exist_ok=True)
            (target / stored).write_bytes(b"%PDF-1.4 hello")
            with m.db_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO files (intake_id, original_name, stored_name, size, content_type, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (intake_id, "合同.pdf", stored, 13, "application/pdf",
                     "2026-08-03T00:00:00+00:00"),
                )

            headers = {"Authorization": "Bearer secret-token"}
            rows = client.get(f"/admin/api/intakes/{intake_id}/files", headers=headers).json()
            assert len(rows) == 1
            assert rows[0]["original_name"] == "合同.pdf"

            resp = client.get(
                f"/admin/api/intakes/{intake_id}/files/{rows[0]['id']}/download",
                headers=headers,
            )
            assert resp.status_code == 200
            assert resp.content == b"%PDF-1.4 hello"
            assert resp.headers["content-disposition"].startswith("attachment")
    finally:
        monkeypatch.undo()


def test_admin_files_require_token(tmp_db):
    with TestClient(m.app) as client:
        assert client.get("/admin/api/intakes/1/files").status_code == 401
        assert client.get("/admin/api/intakes/1/files/1/download").status_code == 401


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


def test_webhook_rejection_is_logged(tmp_db, monkeypatch, caplog):
    """WeChat returns HTTP 200 + errcode on rejection (e.g. revoked key);
    the app must surface it instead of staying silent."""

    class FakeResponse:
        def __init__(self, body):
            self._body = body

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return self._body

    monkeypatch.setenv("NOTIFY_WEBHOOK_URL", "https://example.com/hook")
    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda request, timeout=5: FakeResponse(b'{"errcode":40013,"errmsg":"invalid webhook key"}'),
    )
    with caplog.at_level(logging.ERROR):
        m._send_intake_notification(
            {"name": "x", "email": "a@b.com", "matter": "贸易", "summary": "s",
             "language": "zh", "created_at": "2026-08-03T00:00:00+00:00"}
        )
    assert "webhook rejected" in caplog.text
    assert "invalid webhook key" in caplog.text


# --- Admin API ---------------------------------------------------------


def test_admin_page_served(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/admin")
        assert resp.status_code == 200
        assert "管理后台" in resp.text


def test_static_pages_exist_on_disk():
    """FileResponse endpoints must point at files that actually exist —
    regression guard for the Docker image missing admin.html."""
    for name in ("index.html", "admin.html"):
        assert (m.ROOT_DIR / name).is_file(), f"{name} missing from repo root"


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


def test_admin_export_filters(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            headers = {"Authorization": "Bearer secret-token"}
            client.post("/api/intakes", json=VALID_PAYLOAD)
            client.patch("/admin/api/intakes/1", headers=headers, json={"status": "closed"})

            all_csv = client.get("/admin/intakes.csv", headers=headers).text
            closed_csv = client.get("/admin/intakes.csv?status=closed", headers=headers).text
            q_csv = client.get("/admin/intakes.csv?q=张三", headers=headers).text
            empty_csv = client.get("/admin/intakes.csv?status=new", headers=headers).text
            assert "张三" in all_csv and "张三" in closed_csv and "张三" in q_csv
            assert "张三" not in empty_csv  # only the header line remains
    finally:
        monkeypatch.undo()


# --- SEO & landing pages ----------------------------------------------


def test_index_injects_site_url(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/")
        assert resp.status_code == 200
        assert "{{SITE_URL}}" not in resp.text
        assert 'content="http://localhost:8000/"' in resp.text  # og:url default
        assert "LegalService" in resp.text  # JSON-LD
        assert "FAQPage" in resp.text  # homepage FAQ rich results


def test_index_records_page_view(tmp_db):
    with TestClient(m.app) as client:
        client.get("/")
        client.get("/")
        conn = sqlite3.connect(tmp_db)
        count = conn.execute("SELECT COUNT(*) FROM page_views").fetchone()[0]
        conn.close()
        assert count == 2


def test_sitemap_lists_pages(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/sitemap.xml")
        assert resp.status_code == 200
        assert "application/xml" in resp.headers["content-type"]
        assert "http://localhost:8000/" in resp.text
        for slug in ("trade", "recovery", "legacy"):
            assert f"/services/{slug}" in resp.text


def test_service_pages(tmp_db):
    with TestClient(m.app) as client:
        for slug in ("trade", "recovery", "legacy"):
            resp = client.get(f"/services/{slug}")
            assert resp.status_code == 200
            assert "建议准备的材料" in resp.text
        assert client.get("/services/bogus").status_code == 404


def test_service_page_cards_centered(tmp_db):
    # Regression: .cols used to override .wrap's auto centering with
    # margin:36px 0, pushing the two cards (常见情形 / 建议准备的材料)
    # flush left instead of centered.
    with TestClient(m.app) as client:
        resp = client.get("/services/trade")
        assert "margin: 40px auto 0" in resp.text


# --- Conversion stats --------------------------------------------------


def test_stats_requires_token(tmp_db):
    with TestClient(m.app) as client:
        assert client.get("/admin/api/stats").status_code == 401


def test_stats_numbers(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            client.get("/")
            client.get("/")
            client.post("/api/intakes", json=VALID_PAYLOAD)
            stats = client.get(
                "/admin/api/stats",
                headers={"Authorization": "Bearer secret-token"},
            ).json()
            assert stats["intakes_total"] == 1
            assert stats["intakes_today"] == 1
            assert stats["views_total"] == 2
            assert stats["views_today"] == 2
            assert stats["conversion_today_pct"] == 50.0
            assert stats["by_status"]["new"] == 1
            assert stats["by_matter"][0]["matter"] == "国际贸易争议"
    finally:
        monkeypatch.undo()


# --- Audit trail & ops scripts ----------------------------------------


def audit_rows(db):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM audit_log ORDER BY id")]
    conn.close()
    return rows


def test_audit_logged_on_failed_auth(tmp_db):
    with TestClient(m.app) as client:
        client.get("/admin/api/intakes")
        client.get("/admin/intakes.csv", headers={"Authorization": "Bearer wrong"})
    rows = audit_rows(tmp_db)
    assert len(rows) == 2
    assert all(r["action"] == "auth_failed" for r in rows)


def test_audit_logged_on_update_and_export(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            headers = {"Authorization": "Bearer secret-token"}
            client.post("/api/intakes", json=VALID_PAYLOAD)
            client.patch("/admin/api/intakes/1", headers=headers, json={"status": "closed"})
            client.get("/admin/intakes.csv", headers=headers)
        rows = audit_rows(tmp_db)
        actions = [r["action"] for r in rows]
        assert "update" in actions
        assert "export" in actions
        update = next(r for r in rows if r["action"] == "update")
        assert "intake 1" in update["detail"]
        assert "status" in update["detail"]
    finally:
        monkeypatch.undo()


def test_prune_dry_run_and_execute(tmp_db, monkeypatch, capsys):
    m.init_db()
    # Insert one old and one recent intake directly.
    conn = sqlite3.connect(tmp_db)
    conn.execute(
        "INSERT INTO intakes (name,email,matter,summary,created_at,consent_at,status)"
        " VALUES ('旧线索','old@x.com','贸易','s','2020-01-01T00:00:00+00:00','2020-01-01T00:00:00+00:00','new')"
    )
    conn.execute(
        "INSERT INTO intakes (name,email,matter,summary,created_at,consent_at,status)"
        " VALUES ('新线索','new@x.com','贸易','s','2026-08-01T00:00:00+00:00','2026-08-01T00:00:00+00:00','new')"
    )
    conn.commit()
    conn.close()

    from scripts import prune_intakes

    # Dry run: previews, deletes nothing.
    monkeypatch.setattr("sys.argv", ["prune", "--older-than", "365", "--dry-run"])
    assert prune_intakes.main() == 0
    assert "[dry-run]" in capsys.readouterr().out
    conn = sqlite3.connect(tmp_db)
    assert conn.execute("SELECT COUNT(*) FROM intakes").fetchone()[0] == 2
    conn.close()

    # Without --yes: refuses.
    monkeypatch.setattr("sys.argv", ["prune", "--older-than", "365"])
    assert prune_intakes.main() == 1

    # Execute: deletes only the old one, records an audit row.
    monkeypatch.setattr("sys.argv", ["prune", "--older-than", "365", "--yes"])
    assert prune_intakes.main() == 0
    conn = sqlite3.connect(tmp_db)
    conn.row_factory = sqlite3.Row
    remaining = [dict(r) for r in conn.execute("SELECT name FROM intakes")]
    conn.close()
    assert remaining == [{"name": "新线索"}]
    rows = audit_rows(tmp_db)
    assert any(r["action"] == "prune" for r in rows)


# --- Articles (content factory) -----------------------------------------


def test_articles_index_lists_articles(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/articles")
        assert resp.status_code == 200
        assert "法律专栏" in resp.text
        assert "跨境法律实务指南" in resp.text
        # At least the 10 published articles appear as cards.
        assert resp.text.count("a-card") >= 10


def test_article_pages_render_bilingual(tmp_db):
    with TestClient(m.app) as client:
        for slug in (
            "trade-payment-recovery-5-steps",
            "trade-export-debt-collection-process",
            "trade-contract-review-10-clauses",
            "recovery-demand-letter-vs-lawsuit",
            "recovery-debt-collection-golden-window",
            "recovery-enforce-chinese-judgment-us-canada",
            "recovery-locate-debtor-overseas-assets",
            "recovery-enforce-arbitral-award-new-york-convention",
            "legacy-chinese-citizen-dies-abroad",
            "legacy-relative-dies-abroad-china-heirs",
            "legacy-inheriting-overseas-property-us-canada-australia",
            "recovery-types-of-commercial-fraud-contracts-investments-exports",
            "trade-jurisdiction-governing-law-clauses-how-to-negotiate",
            "recovery-won-the-case-but-no-money-enforcement-strategies",
            "legacy-foreign-heirs-inheriting-china-company-shares",
            "legacy-cross-border-inheritance-from-death-certificate-to-transfer",
            "trade-supplier-late-delivery-buyer-s-legal-remedies",
            "recovery-investigating-assets-inside-china-equity-property-deposits",
            "legacy-making-a-will-abroad-does-it-cover-china-assets",
            "trade-first-24-hours-after-trade-fraud-evidence-and-freezing",
            "trade-freight-forwarder-withholding-cargo-legal-remedies",
            "recovery-legal-ways-to-find-us-real-estate-and-bank-accounts",
            "legacy-drafting-a-cross-border-valid-will-key-elements",
            "recovery-expired-limitation-period-can-you-still-collect",
            "trade-10-common-international-trade-scams-and-how-to-spot-them",
            "trade-common-excuses-for-late-payment-and-legal-responses",
            "recovery-collection-agencies-vs-lawyers-why-legal-counsel-wins",
            "recovery-international-construction-payment-disputes-recovery-strategies",
            "recovery-can-the-debtor-pay-your-legal-costs-cost-shifting",
            "recovery-investment-fraud-abroad-legal-recourse-for-victims",
            "trade-terminating-a-delinquent-distributor-legal-steps",
            "trade-platform-seller-disputes-amazon-aliexpress-legal-issues",
            "recovery-legal-expense-insurance-what-it-covers",
            "recovery-private-investigators-vs-lawyers-admissibility",
            "recovery-what-is-a-solicitor-vs-barrister-cross-border",
            "trade-collecting-from-us-buyers-from-demand-to-lawsuit",
            "recovery-enforcing-us-judgments-in-chinese-courts",
            "topic-041",
            "recovery-solicitor-role-cross-border-how-to-choose",
            "legacy-inheriting-shares-in-an-overseas-company",
            "recovery-offshore-companies-and-trusts-uncovering-hidden-assets",
            "trade-business-email-compromise-recovering-funds-after-fraud",
            "recovery-freezing-injunctions-and-asset-preservation-orders",
            "legacy-missing-relative-abroad-locating-person-and-estate",
            "trade-buyer-bankruptcy-can-you-still-recover-your-export-debt",
            "trade-defective-goods-rejection-vs-damages",
            "recovery-debtor-vanished-6-strategies-to-find-and-recover",
            "legacy-foreign-heirs-inheriting-china-property-process-and-tax",
            "recovery-enforcing-hk-and-singapore-awards-in-mainland-china",
            "legacy-overseas-children-inheriting-parents-property-in-china",
            "trade-incoterms-2020-choosing-the-right-term",
            "recovery-cross-border-collection-playbook-debtor-abroad",
            "legacy-china-wills-vs-foreign-wills-validity-and-conflicts",
            "trade-supplier-disputes-in-southeast-asia-practical-guide",
            "recovery-litigation-arbitration-or-mediation-choosing-the-path",
            "trade-disputes-in-the-middle-east-arbitration-vs-litigation",
            "trade-trading-with-russia-cis-contract-and-payment-risks",
            "trade-cultural-differences-in-cross-border-negotiation",
            "recovery-executive-misappropriation-shareholder-remedies",
            "trade-commission-disputes-with-overseas-sales-agents",
            "legacy-inheriting-beneficially-owned-nominee-shares",
            "legacy-time-limits-for-contesting-estates-don-t-miss-the-deadline",
            "legacy-beneficiary-disputes-resolving-claims-to-the-estate",
            "international-law-firm-cross-border-business-disputes",
            "international-lawyer-cross-border-case-coordination",
            "xiteng-outsourcing-trade-dispute-evidence-response",
            "trade-t-t-deposit-payments-contract-clauses-that-protect-exporters",
            "recovery-fraudulent-transfers-setting-aside-asset-transfers",
            "legacy-family-inheritance-disputes-mediation-litigation-settlement",
            "recovery-10-asset-investigation-sources-registries-and-records",
            "trade-exclusive-agency-vs-distribution-which-to-choose",
        ):
            resp = client.get(f"/articles/{slug}")
            assert resp.status_code == 200, slug
            # Both language bodies are present and the EN marker is consumed.
            assert "bodyZh" in resp.text and "bodyEn" in resp.text
            assert "<!-- EN -->" not in resp.text
            # Markdown actually rendered (headings + CTA).
            assert "<h2" in resp.text and "免费法律咨询" in resp.text


def test_article_unknown_slug_404(tmp_db):
    with TestClient(m.app) as client:
        assert client.get("/articles/no-such-article").status_code == 404
        assert client.get("/articles/../../etc/passwd").status_code == 404
        assert client.get("/articles/..%2f..%2fetc%2fpasswd").status_code == 404


def test_sitemap_includes_articles(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/sitemap.xml")
        assert resp.status_code == 200
        assert "/articles" in resp.text


def test_sitemap_includes_new_countries(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/sitemap.xml")
        assert resp.status_code == 200
        for slug in ("hong-kong", "germany", "japan", "united-arab-emirates",
                     "new-zealand", "malaysia", "france", "switzerland",
                     "south-korea", "thailand", "vietnam", "netherlands", "italy",
                     "spain", "brazil", "india", "ireland"):
            assert f"/countries/{slug}" in resp.text, slug
            assert f"/en/countries/{slug}" in resp.text, slug
        assert "/articles/trade-payment-recovery-5-steps" in resp.text


def test_sitemap_lastmod_on_articles_only(tmp_db):
    with TestClient(m.app) as client:
        text = client.get("/sitemap.xml").text
        # Articles carry lastmod from their frontmatter date.
        assert "<lastmod>2026-08-10</lastmod>" in text
        assert '<loc>http://localhost:8000/articles/trade-payment-recovery-5-steps</loc><lastmod>' in text
        # Static pages (home, indexes, country/service pages) omit lastmod.
        assert "<loc>http://localhost:8000/</loc><lastmod>" not in text
        assert "<loc>http://localhost:8000/countries/united-states</loc><lastmod>" not in text
        assert "<loc>http://localhost:8000/services/trade</loc><lastmod>" not in text
        # Every article URL has a lastmod (all articles carry dates).
        import re as _re
        article_locs = _re.findall(r"<loc>(http://localhost:8000/(?:en/)?articles/[^<]+)</loc>", text)
        assert article_locs, "no article locs found"
        for loc in article_locs:
            assert "<lastmod>" in text.split(loc)[1].split("</url>")[0], loc


# --- English variants (/en/ URLs) -----------------------------------------


def test_en_homepage(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/en/")
        assert resp.status_code == 200
        assert '<html lang="en">' in resp.text
        assert "Cross-border disputes," in resp.text
        assert "resolved in your language." in resp.text
        assert 'var currentLang = "en";' in resp.text
        assert 'hreflang="en" href="http://localhost:8000/en/"' in resp.text
        assert client.get("/en").status_code == 200
        # zh homepage stays the default with zh text
        zh = client.get("/")
        assert '<html lang="zh-CN">' in zh.text
        assert "跨境的纠纷" in zh.text


def test_en_service_pages(tmp_db):
    with TestClient(m.app) as client:
        for slug in ("trade", "recovery", "legacy"):
            resp = client.get(f"/en/services/{slug}")
            assert resp.status_code == 200, slug
            assert '<html lang="en">' in resp.text
            assert "International Trade Disputes" in resp.text or "Litigation" in resp.text or "Inheritance" in resp.text
            assert 'hreflang="en"' in resp.text
        assert client.get("/en/services/bogus").status_code == 404


def test_en_articles(tmp_db):
    with TestClient(m.app) as client:
        index = client.get("/en/articles")
        assert index.status_code == 200
        assert '<html lang="en">' in index.text
        page = client.get("/en/articles/trade-payment-recovery-5-steps")
        assert page.status_code == 200
        # English body visible, Chinese body hidden server-side (no-JS crawlers)
        assert '<div class="wrap article-body" id="bodyEn">' in page.text
        assert '<div class="wrap article-body" id="bodyZh" hidden>' in page.text
        assert "What to Do When an Overseas Buyer Won" in page.text
        assert client.get("/en/articles/no-such-article").status_code == 404


def test_sitemap_includes_en_urls(tmp_db):
    with TestClient(m.app) as client:
        text = client.get("/sitemap.xml").text
        assert "/en/" in text
        assert "/en/articles" in text
        assert "/en/services/trade" in text
        assert "/en/articles/trade-payment-recovery-5-steps" in text


def test_article_blogposting_schema(tmp_db):
    with TestClient(m.app) as client:
        zh = client.get("/articles/trade-payment-recovery-5-steps").text
        assert '"@type": "BlogPosting"' in zh
        assert '"headline": "海外客户拖欠货款怎么办？律师教你5步合法追收"' in zh
        assert '"inLanguage": "zh-CN"' in zh
        en = client.get("/en/articles/trade-payment-recovery-5-steps").text
        assert '"headline": "What to Do When an Overseas Buyer Won' in en
        assert '"inLanguage": "en"' in en


# --- Country landing pages -------------------------------------------------


def test_country_pages(tmp_db):
    with TestClient(m.app) as client:
        index = client.get("/countries")
        assert index.status_code == 200
        assert "国家专页" in index.text
        slugs = (
            "united-states", "canada", "australia", "singapore", "united-kingdom",
            "hong-kong", "germany", "japan", "united-arab-emirates", "new-zealand",
            "malaysia", "france", "switzerland",
            "south-korea", "thailand", "vietnam", "netherlands", "italy",
            "spain", "brazil", "india", "ireland",
        )
        for slug in slugs:
            resp = client.get(f"/countries/{slug}")
            assert resp.status_code == 200, slug
            assert 'hreflang="en"' in resp.text
            assert "LegalService" in resp.text
            assert "FAQPage" in resp.text, slug
            assert 'name": "中国法院的判决能' in resp.text or 'name": "内地法院的判决能' in resp.text, slug
            en = client.get(f"/en/countries/{slug}")
            assert en.status_code == 200
            assert '<html lang="en">' in en.text
        assert client.get("/countries/bogus").status_code == 404
        assert client.get("/en/countries/bogus").status_code == 404
        # Homepage region chips link to country pages (language-aware hrefs)
        home = client.get("/").text
        assert "/countries/united-states" in home
        assert 'data-en-href="/en/countries/united-states"' in home


def test_sitemap_includes_countries(tmp_db):
    with TestClient(m.app) as client:
        text = client.get("/sitemap.xml").text
        assert "/countries" in text
        assert "/countries/united-states" in text
        assert "/en/countries/united-states" in text


# --- AI 咨询助手 (chat intake) ---------------------------------------------


def test_chat_widget_static_file(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/static/chat.js")
        assert resp.status_code == 200
        assert "cw-launcher" in resp.text
        assert "/api/intakes/chat" in resp.text


def test_chat_intake_stores_and_classifies(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes/chat",
            json={
                "name": "王工",
                "contact": "13800000000",
                "matter": "trade",
                "summary": "美国客户拖欠货款，希望追回欠款",
                "parties": "我方工厂，对方美国采购商",
                "amount": "50万以上",
                "timeline": "2年以上",
                "evidence": "合同、发票",
                "goal": "追回欠款",
                "country": "美国",
                "language": "zh",
                "consent": True,
                "transcript": "bot: hi\nuser: 美国客户欠款",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["id"] == 1
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        # 追收/欠款 keywords override the visitor's "trade" pick -> recovery
        assert row["matter"] == "诉讼与债务追收"
        assert row["phone"] == "13800000000"
        assert row["email"] == ""
        assert row["country_or_region"] == "美国"
        assert row["consent_at"] == row["created_at"]
        assert "来源：AI 咨询助手" in row["note"]
        assert "对话记录" in row["note"]


def test_chat_intake_contact_email_split(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes/chat",
            json={
                "name": "李女士",
                "contact": "li@example.com",
                "matter": "legacy",
                "summary": "父亲在加拿大去世，留下房产需要继承",
                "consent": True,
            },
        )
        assert resp.status_code == 201
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        assert row["email"] == "li@example.com"
        assert row["matter"] == "继承与家族资产纠纷"


def test_chat_intake_classification_trade(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes/chat",
            json={
                "name": "赵经理",
                "contact": "zhao@example.com",
                "matter": "recovery",
                "summary": "供应商延期交货，质量不合格，合同违约",
                "consent": True,
            },
        )
        assert resp.status_code == 201
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        assert row["matter"] == "国际贸易争议"


def test_chat_intake_requires_consent(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes/chat",
            json={
                "name": "陈先生",
                "contact": "chen@example.com",
                "summary": "需要咨询",
                "consent": False,
            },
        )
        assert resp.status_code == 400


def test_chat_intake_dedupe_by_phone(tmp_db):
    with TestClient(m.app) as client:
        first = client.post(
            "/api/intakes/chat",
            json={"name": "刘", "contact": "13900000000", "summary": "客户拖欠货款", "consent": True},
        )
        assert first.status_code == 201
        second = client.post(
            "/api/intakes/chat",
            json={"name": "刘", "contact": "13900000000", "summary": "客户拖欠货款", "consent": True},
        )
        assert second.status_code == 409


def test_chat_widget_mounted_on_all_pages(tmp_db):
    with TestClient(m.app) as client:
        for url in ("/", "/services/trade", "/articles", "/articles/trade-payment-recovery-5-steps",
                    "/countries", "/countries/united-states", "/en/", "/en/services/recovery"):
            html = client.get(url).text
            assert 'id="chat-widget-root"' in html, url
            assert '/static/chat.js' in html, url


# --- CRM Agent: scoring, SLA, reminders -------------------------------------


def test_crm_migration_adds_score_and_updated_at(tmp_db):
    m.init_db()
    conn = sqlite3.connect(tmp_db)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(intakes)")]
    conn.close()
    assert "score" in cols
    assert "updated_at" in cols


def test_lead_score_heuristic():
    # Base + amount + urgency + recovery matter + evidence + full contact
    high = m._lead_score(
        "张", "美国客户拖欠货款50万以上，情况紧急",
        "诉讼与债务追收", amount="50万以上", evidence="合同、发票",
        email="a@b.com", phone="138",
    )
    assert high >= 80
    # Plain small lead stays low
    low = m._lead_score("李", "简单咨询", "国际贸易争议")
    assert low <= 35
    # Legacy matter signal
    legacy = m._lead_score("王", "父亲去世继承房产", "继承与家族资产纠纷")
    assert 40 <= legacy <= 60


def test_overdue_leads_sla(tmp_db):
    m.init_db()
    now = m.datetime.now(m.timezone.utc).isoformat()
    old_new = (m.datetime.now(m.timezone.utc) - m.timedelta(hours=100)).isoformat()
    old_progress = (m.datetime.now(m.timezone.utc) - m.timedelta(hours=200)).isoformat()
    with m.db_connection() as conn:
        for i, (status, ts, score) in enumerate(
            [
                ("new", old_new, 30),          # overdue: new untouched 100h (>24h SLA)
                ("contacted", old_progress, 80),  # overdue: no progress 200h (>7d SLA)
                ("new", now, 60),              # fresh — not overdue
                ("closed", old_new, 90),       # closed — excluded
            ]
        ):
            conn.execute(
                "INSERT INTO intakes (name, email, matter, summary, status, created_at, updated_at, score, consent_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f"n{i}", f"n{i}@test.com", "国际贸易争议", "s", status, ts, ts, score, now),
            )
    leads = m._overdue_leads()
    ids = sorted(l["id"] for l in leads)
    assert len(leads) == 2, leads
    # highest score first
    assert leads[0]["score"] == 80
    assert leads[0]["stale_hours"] > 190


def test_crm_overdue_endpoint(tmp_db, monkeypatch):
    m.init_db()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    old = (m.datetime.now(m.timezone.utc) - m.timedelta(hours=100)).isoformat()
    with m.db_connection() as conn:
        conn.execute(
            "INSERT INTO intakes (name, email, matter, summary, status, created_at, updated_at, score, consent_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("逾期客户", "late@test.com", "诉讼与债务追收", "欠款未还", "new", old, old, 70, old),
        )
    with TestClient(m.app) as client:
        assert client.get("/admin/api/crm/overdue").status_code == 401
        headers = {"Authorization": "Bearer secret-token"}
        resp = client.get("/admin/api/crm/overdue", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["leads"][0]["name"] == "逾期客户"
        assert data["first_sla_hours"] == 24


def test_crm_reminder_webhook_payload(tmp_db, monkeypatch):
    monkeypatch.setenv("NOTIFY_WEBHOOK_URL", "https://webhook.test/crm")
    captured = {}

    def fake_urlopen(request, timeout=5):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return _FakeResponse(b'{"errcode":0,"errmsg":"ok"}')

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    m._send_crm_reminder(
        [
            {"id": 1, "status": "new", "name": "张", "matter": "诉讼与债务追收",
             "email": "a@b.com", "phone": "", "score": 80, "stale_hours": 30},
            {"id": 2, "status": "contacted", "name": "李", "matter": "继承",
             "email": "", "phone": "138", "score": 55, "stale_hours": 200},
        ]
    )
    assert captured["url"] == "https://webhook.test/crm"
    content = captured["body"]["text"]["content"]
    assert "【CRM 跟进提醒】" in content
    assert "新线索未联系 1" in content
    assert "#1" in content and "评分 80" in content
    assert captured["body"]["msgtype"] == "text"


def test_intake_creation_sets_score_and_updated_at(tmp_db):
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes/chat",
            json={
                "name": "高优先客户",
                "contact": "gao@example.com",
                "matter": "recovery",
                "summary": "客户拖欠货款100万，非常紧急，对方可能转移资产",
                "amount": "50万以上",
                "evidence": "合同、发票",
                "consent": True,
            },
        )
        assert resp.status_code == 201
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM intakes").fetchone()
        conn.close()
        assert row["score"] >= 70
        assert row["updated_at"] == row["created_at"]


def test_admin_update_touches_updated_at(tmp_db, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    with TestClient(m.app) as client:
        resp = client.post(
            "/api/intakes/chat",
            json={"name": "王", "contact": "wang@example.com", "summary": "咨询", "consent": True},
        )
        intake_id = resp.json()["id"]
        headers = {"Authorization": "Bearer secret-token"}
        # 48h pass...
        client.patch(f"/admin/api/intakes/{intake_id}", json={"status": "contacted"}, headers=headers)
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT updated_at FROM intakes WHERE id = ?", (intake_id,)).fetchone()
        conn.close()
        assert row["updated_at"] is not None


def test_intake_source_captured_and_aggregated(tmp_db, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    with TestClient(m.app) as client:
        # Form intake with utm_source
        client.post(
            "/api/intakes",
            json={
                "name": "李", "email": "li@example.com", "phone": "13800138000",
                "matter": "贸易", "summary": "美国客户欠款", "source": "facebook", "consent": True,
            },
        )
        # Chat intake without source -> direct
        client.post(
            "/api/intakes/chat",
            json={"name": "赵", "contact": "zhao@example.com", "summary": "咨询继承", "consent": True},
        )
        # Chat intake with tiktok source
        client.post(
            "/api/intakes/chat",
            json={
                "name": "钱", "contact": "qian@example.com", "summary": "追收欠款",
                "source": "tiktok", "consent": True,
            },
        )
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT source FROM intakes ORDER BY id").fetchall()
        conn.close()
        assert [r["source"] for r in rows] == ["facebook", None, "tiktok"]
        headers = {"Authorization": "Bearer secret-token"}
        agg = client.get("/admin/api/intakes/sources", headers=headers)
        assert agg.status_code == 200
        by = {d["source"]: d["count"] for d in agg.json()}
        assert by.get("facebook") == 1 and by.get("tiktok") == 1 and by.get("direct") == 1
        # auth required
        assert client.get("/admin/api/intakes/sources").status_code == 401


# --- Marketing Agent: collateral generator -----------------------------------


def test_marketing_headings_and_intro():
    md = "# 标题\n\n开头段落一。\n\n## 第一点\n\n内容。\n## 第二点\n\n内容。\n\n结尾。"
    assert m._article_headings(md) == ["第一点", "第二点"]
    intro = m._article_intro(md)
    assert "开头段落一" in intro
    assert len(intro) <= 200


def test_marketing_bundle_for_article(tmp_db):
    article = next(a for a in m._load_articles() if a["meta"]["slug"] == "trade-payment-recovery-5-steps")
    biz = m._business_key(article["meta"].get("business", ""))
    bundle = m._marketing_bundle(article, biz, "https://shenyuanlegal.com/articles/trade-payment-recovery-5-steps")
    assert bundle["business"] == "trade"
    assert len(bundle["wechat_mp"]["titles"]) == 3
    # 小红书 note has points + CTA + disclaimer
    assert "✅" in bundle["xiaohongshu"]["body"]
    assert "不构成法律意见" in bundle["xiaohongshu"]["body"]
    # video script has hook, body and CTA
    assert "[开头3秒]" in bundle["video"]["script_zh"]
    # ads respect platform limits (headline <= 30, description <= 90)
    assert all(len(h) <= 30 for h in bundle["ads"]["headlines"])
    assert all(len(d) <= 90 for d in bundle["ads"]["descriptions"])
    assert len(bundle["ads"]["keywords"]) == 10
    # UTM links carry channel params
    assert "utm_source=xiaohongshu" in bundle["utm"]["xiaohongshu"]
    assert "utm_medium=cpc" in bundle["utm"]["ads"]
    assert "utm_source=facebook" in bundle["utm"]["facebook"]
    assert "utm_source=x" in bundle["utm"]["x"]
    assert "utm_source=tiktok" in bundle["utm"]["tiktok"]
    # weekly schedule
    assert bundle["schedule"][0][0] == "周一"


def test_marketing_social_bundle_sections(tmp_db):
    """Facebook / X / TikTok / 小红书增强 sections are present and sane."""
    article = next(a for a in m._load_articles() if a["meta"]["slug"] == "trade-payment-recovery-5-steps")
    biz = m._business_key(article["meta"].get("business", ""))
    bundle = m._marketing_bundle(article, biz, "https://shenyuanlegal.com/articles/trade-payment-recovery-5-steps")
    # Facebook: EN post + ad pack with targeting
    assert "free initial assessment" in bundle["facebook"]["post_en"].lower()
    assert len(bundle["facebook"]["ad"]["primary_text_en"]) <= 500  # FB platform limit
    assert "interests" in bundle["facebook"]["ad"]["targeting"]
    # X: tweets within 280 chars, thread exists
    assert len(bundle["x"]["tweet_en"]) <= 280
    assert len(bundle["x"]["tweet_zh"]) <= 280
    assert "1/" in bundle["x"]["thread_en"] and "5/" in bundle["x"]["thread_en"]
    # TikTok: dual-language scripts with time-coded segments + production tips
    assert "[0-3s" in bundle["tiktok"]["script_zh"]
    assert "[0-3s" in bundle["tiktok"]["script_en"]
    assert "on_screen_captions" in bundle["tiktok"] and "ad_spark" in bundle["tiktok"]
    # 小红书: three angles
    assert set(bundle["xiaohongshu"]["angles"]) == {"干货型", "避坑型", "故事型"}


def test_marketing_generate_endpoint(tmp_db, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    with TestClient(m.app) as client:
        assert client.get("/admin/api/marketing/generate?slug=x").status_code == 401
        headers = {"Authorization": "Bearer secret-token"}
        resp = client.get(
            "/admin/api/marketing/generate?slug=trade-payment-recovery-5-steps", headers=headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "trade-payment-recovery-5-steps"
        assert "wechat_mp" in data and "ads" in data and "linkedin" in data
        # unknown slug -> 404
        assert client.get("/admin/api/marketing/generate?slug=no-such", headers=headers).status_code == 404
        # business-only mode (no slug) works as an ad-landing generator
        biz = client.get("/admin/api/marketing/generate?business=legacy", headers=headers)
        assert biz.status_code == 200
        assert biz.json()["business"] == "legacy"
        assert "/services/legacy" in biz.json()["article_url"]


def test_admin_marketing_page_and_articles_api(tmp_db, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    with TestClient(m.app) as client:
        # console shell is unauthenticated (like /admin)
        page = client.get("/admin/marketing")
        assert page.status_code == 200
        assert "营销素材" in page.text
        # articles API requires token
        assert client.get("/admin/api/articles").status_code == 401
        headers = {"Authorization": "Bearer secret-token"}
        articles = client.get("/admin/api/articles", headers=headers)
        assert articles.status_code == 200
        data = articles.json()
        slugs = [a["slug"] for a in data]
        assert "trade-payment-recovery-5-steps" in slugs
        assert all(a["business"] in ("trade", "recovery", "legacy", "unsure") for a in data)
        # newest first
        dates = [a["date"] for a in data]
        assert dates == sorted(dates, reverse=True)


def test_dockerfile_ships_content_dir():
    # Regression: articles are served from content/, so the image must copy
    # the directory — otherwise /articles/{slug} 404s in production only.
    docke = (Path(__file__).resolve().parent.parent / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY content ./content" in docke


def test_dockerfile_ships_admin_marketing_page():
    # Regression: the marketing console is served from admin_marketing.html,
    # so the image must copy it like admin.html.
    docke = (Path(__file__).resolve().parent.parent / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY admin_marketing.html ." in docke


# --- SEO / analytics plumbing --------------------------------------------


def test_robots_txt_points_to_sitemap(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/robots.txt")
        assert resp.status_code == 200
        assert "Sitemap: http://localhost:8000/sitemap.xml" in resp.text


def test_robots_allows_ai_crawlers_and_llms(tmp_db):
    # GEO: AI crawlers explicitly allowed; llms.txt advertised in robots.
    with TestClient(m.app) as client:
        robots = client.get("/robots.txt").text
        for agent in ("GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended",
                      "Baiduspider", "Sogou web spider", "360Spider"):
            assert f"User-agent: {agent}" in robots, agent
        assert "LLMtxt: http://localhost:8000/llms.txt" in robots


def test_related_reading_and_breadcrumbs(tmp_db):
    with TestClient(m.app) as client:
        # Article page: related block + BreadcrumbList JSON-LD
        article = client.get("/articles/trade-payment-recovery-5-steps").text
        assert "延伸阅读" in article
        assert 'class="related"' in article
        assert 'href="/articles/trade-' in article  # same-business suggestion
        assert "BreadcrumbList" in article
        assert 'class="crumbs"' in article
        # Service page: crumbs + related
        service = client.get("/services/trade").text
        assert "BreadcrumbList" in service
        assert 'class="crumbs"' in service
        assert "延伸阅读" in service
        # Country page: crumbs (3 levels) + related
        country = client.get("/countries/united-states").text
        assert "BreadcrumbList" in country
        assert 'class="crumbs"' in country
        assert "国家专页" in country
        assert "延伸阅读" in country


# --- Case Research Agent ------------------------------------------------


def test_kb_search_finds_statutes_and_practice(tmp_db, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    with TestClient(m.app) as client:
        # Unauthorized
        assert client.get("/admin/api/research/search?q=时效").status_code == 401
        headers = {"Authorization": "Bearer secret-token"}
        hits = client.get("/admin/api/research/search?q=时效 判决执行", headers=headers).json()
        assert hits, "knowledge base should return hits"
        paths = {h["path"] for h in hits}
        assert any("statutes" in p for p in paths)
        assert any("practice" in p for p in paths)
        # Every hit carries a snippet
        assert all(h.get("snippet") for h in hits)


def test_research_memo_generation(tmp_db, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    with TestClient(m.app) as client:
        headers = {"Authorization": "Bearer secret-token", "Content-Type": "application/json"}
        memo = client.post(
            "/admin/api/research/memo",
            json={
                "matter_type": "recovery",
                "facts": "美国客户收货后拖欠货款 45 万美元，逾期 6 个月，合同约定纽约法管辖",
                "amount": "45 万美元",
                "country": "美国",
            },
            headers=headers,
        )
        assert memo.status_code == 200
        data = memo.json()
        assert data["label"] == "诉讼与债务追收"
        assert data["facts"].startswith("美国客户")
        assert len(data["kb_hits"]) > 0
        assert any("时效" in h["snippet"] for h in data["kb_hits"]) or any("美国" in h["snippet"] for h in data["kb_hits"])
        assert data["next_steps"]
        assert "不构成法律意见" in data["disclaimer"]
        # Invalid matter type rejected
        bad = client.post(
            "/admin/api/research/memo",
            json={"matter_type": "tax", "facts": "x" * 20},
            headers=headers,
        )
        assert bad.status_code == 422
        # Audit trail written
        conn = sqlite3.connect(tmp_db)
        n = conn.execute("SELECT COUNT(*) FROM audit_log WHERE action LIKE 'research.%'").fetchone()[0]
        conn.close()
        assert n >= 1


def test_admin_research_page_and_dockerfile_ship_it(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/admin/research")
        assert resp.status_code == 200
        assert "案件研究" in resp.text
    dockerfile = (Path(__file__).resolve().parent.parent / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY admin_research.html" in dockerfile
    assert "COPY legal_kb ./legal_kb" in dockerfile


def test_crm_stale_leads_churn_warning(tmp_db, monkeypatch):
    """30-day-no-touch leads surface as stale (流失预警) and are audited."""
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    with TestClient(m.app) as client:
        # Create a lead, then backdate it 40 days so it is stale.
        resp = client.post(
            "/api/intakes",
            json=dict(VALID_PAYLOAD, email="stale@test.com", phone="13812345678"),
        )
        assert resp.status_code == 201
        conn = sqlite3.connect(tmp_db)
        old = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
        conn.execute("UPDATE intakes SET created_at = ?, updated_at = ? WHERE id = ?",
                     (old, old, resp.json()["id"]))
        conn.commit()
        conn.close()

        headers = {"Authorization": "Bearer secret-token"}
        c = client.get("/admin/api/crm/overdue", headers=headers).json()
        assert c["stale_count"] >= 1
        assert any(l["id"] == resp.json()["id"] and l["stale_days"] >= 30 for l in c["stale"])

        # Marketing generation is audited (6.6.4 留痕).
        bundle = client.get("/admin/api/marketing/generate?business=trade", headers=headers)
        assert bundle.status_code == 200
        conn = sqlite3.connect(tmp_db)
        n = conn.execute("SELECT COUNT(*) FROM audit_log WHERE action = 'marketing.generate'").fetchone()[0]
        conn.close()
        assert n >= 1


def test_trust_pages_and_cookie_banner(tmp_db, monkeypatch):
    """/about /fees /privacy render bilingual; cookie banner + analytics bundle."""
    monkeypatch.setenv("GA_MEASUREMENT_ID", "G-TEST123")
    monkeypatch.setenv("META_PIXEL_ID", "123456789")
    monkeypatch.setenv("BAIDU_ANALYTICS_ID", "baidu-test")
    with TestClient(m.app) as client:
        for slug in ("about", "fees", "privacy"):
            zh = client.get(f"/{slug}")
            assert zh.status_code == 200
            assert "Shenyuan International" in zh.text
            en = client.get(f"/en/{slug}")
            assert en.status_code == 200
            assert 'hreflang="en"' in en.text
            assert "cookieBanner" in zh.text
            assert 'hreflang="zh-CN"' in zh.text
        # Analytics bundle: GA + Meta Pixel + Baidu all present when configured
        home = client.get("/").text
        assert "googletagmanager.com/gtag/js?id=G-TEST123" in home
        assert "connect.facebook.net/en_US/fbevents.js" in home
        assert "hm.baidu.com/hm.js?baidu-test" in home
        # Sitemap includes trust pages
        sitemap = client.get("/sitemap.xml").text
        for u in ("/about", "/en/about", "/fees", "/privacy"):
            assert f"<loc>http://localhost:8000{u}</loc>" in sitemap
    # Disabled when unset
    monkeypatch.delenv("META_PIXEL_ID")
    monkeypatch.delenv("BAIDU_ANALYTICS_ID")
    monkeypatch.delenv("GA_MEASUREMENT_ID")
    with TestClient(m.app) as client:
        home = client.get("/").text
        assert "fbevents" not in home
        assert "hm.baidu" not in home
        assert "cookieBanner" in home  # banner is independent of analytics


def test_handbook_route_and_keyword_docs(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/handbook")
        assert resp.status_code == 200
        assert "跨境维权法律手册" in resp.text
        assert "Shenyuan International" in resp.text
        sitemap = client.get("/sitemap.xml").text
        assert "<loc>http://localhost:8000/handbook</loc>" in sitemap
    dockerfile = (Path(__file__).resolve().parent.parent / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY docs/handbook ./docs/handbook" in dockerfile
    # Keyword research V1 and handbook artifacts exist
    repo = Path(__file__).resolve().parent.parent
    assert (repo / "docs" / "keyword-research-v1.md").exists()
    assert (repo / "docs" / "handbook" / "handbook.html").exists()
    assert (repo / "docs" / "handbook" / "handbook.pdf").exists()


def test_site_search_and_faq_hub_and_analytics(tmp_db, monkeypatch):
    """/search ranks articles+countries; /faq aggregates; analytics API works."""
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    with TestClient(m.app) as client:
        # Search: article hit for a real keyword
        s = client.get("/search?q=执行")
        assert s.status_code == 200
        assert "条结果" in s.text
        assert "articles/" in s.text
        # Search: country hit
        s2 = client.get("/search?q=德国")
        assert s2.status_code == 200
        assert "/countries/germany" in s2.text
        # Empty query shows the prompt
        s0 = client.get("/search")
        assert "输入关键词开始搜索" in s0.text
        # FAQ hub
        faq = client.get("/faq")
        assert faq.status_code == 200
        assert "faq-item" in faq.text
        assert "FAQPage" in faq.text
        assert "常见问题" in faq.text
        en_faq = client.get("/en/faq")
        assert en_faq.status_code == 200 and 'hreflang="en"' in en_faq.text
        # Analytics API (auth required)
        assert client.get("/admin/api/intakes/analytics").status_code == 401
        headers = {"Authorization": "Bearer secret-token"}
        client.post("/api/intakes", json=dict(VALID_PAYLOAD, email="an@test.com", phone="13700000001"))
        a = client.get("/admin/api/intakes/analytics", headers=headers).json()
        assert "by_business" in a and "by_country" in a and "by_source" in a
        assert a["by_business"]["trade"] >= 1  # VALID_PAYLOAD matter is 贸易
        # WebSite SearchAction on home
        home = client.get("/").text
        assert '"@type": "WebSite"' in home
        assert "SearchAction" in home
        assert "/search?q={search_term_string}" in home


def test_cases_page_anonymized(tmp_db):
    """Case studies page renders 5 anonymized examples with compliance framing."""
    with TestClient(m.app) as client:
        zh = client.get("/cases")
        assert zh.status_code == 200
        assert "脱敏示例" in zh.text
        assert "不承诺" in zh.text
        assert "美国买家拖欠货款" in zh.text
        assert "加拿大债务人" in zh.text
        assert "美国房产继承" in zh.text
        assert "ItemList" in zh.text  # structured data
        en = client.get("/en/cases")
        assert en.status_code == 200
        assert "Anonymized Examples" in en.text
        sitemap = client.get("/sitemap.xml").text
        assert "<loc>http://localhost:8000/cases</loc>" in sitemap
        assert "<loc>http://localhost:8000/faq</loc>" in sitemap
        # Home footer links to cases
        home = client.get("/").text
        assert 'href="/cases"' in home


def test_indexes_search_log_and_article_faq(tmp_db):
    """Indexes exist, /search logs queries, article pages embed FAQ."""
    with TestClient(m.app) as client:
        # 1) indexes + search_log table
        m.init_db()
        conn = sqlite3.connect(tmp_db)
        idxs = {r[1] for r in conn.execute("PRAGMA index_list(intakes)")}
        for idx in ("idx_intakes_status", "idx_intakes_created_at",
                    "idx_intakes_updated_at", "idx_intakes_source"):
            assert idx in idxs, idx
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "search_log" in tables
        # 2) search logging
        client.get("/search?q=执行")
        client.get("/search?q=执行")
        n = conn.execute("SELECT COUNT(*) FROM search_log WHERE q='执行'").fetchone()[0]
        assert n == 2
        conn.close()
        # 3) article FAQ block + JSON-LD (business-matched)
        art = client.get("/articles/recovery-enforce-chinese-judgment-us-canada").text
        assert "article-faq" in art
        assert "常见问题" in art
        assert '"@type": "FAQPage"' in art
        assert art.count("FAQPage") >= 1
        # 4) JSON-LD must stay parseable even when text contains ASCII quotes
        art2 = client.get("/articles/recovery-debt-collection-golden-window").text
        import json as _json, re as _re
        for block in _re.findall(r'<script type="application/ld\+json">(.*?)</script>', art2, _re.S):
            _json.loads(block)  # raises on broken JSON


def test_vcard_and_whatsapp_are_env_gated(tmp_db, monkeypatch):
    monkeypatch.delenv("CONTACT_EMAIL", raising=False)
    monkeypatch.delenv("CONTACT_PHONE", raising=False)
    monkeypatch.delenv("WHATSAPP_NUMBER", raising=False)
    with TestClient(m.app) as client:
        assert client.get("/vcard.vcf").status_code == 404
        home = client.get("/").text
        assert "WHATSAPP_BUTTON" not in home  # placeholder resolved to empty
        assert "wa.me" not in home
    # Configured: vCard served, WhatsApp button appears
    monkeypatch.setenv("CONTACT_EMAIL", "info@shenyuanlegal.com")
    monkeypatch.setenv("WHATSAPP_NUMBER", "+86 138 0000 0000")
    with TestClient(m.app) as client:
        vc = client.get("/vcard.vcf")
        assert vc.status_code == 200
        assert "BEGIN:VCARD" in vc.text and "info@shenyuanlegal.com" in vc.text
        assert "text/vcard" in vc.headers["content-type"]
        home = client.get("/").text
        assert "wa.me/8613800000000" in home
        en_home = client.get("/en/").text
        assert "wa.me/8613800000000" in en_home
        assert "{{WHATSAPP_BUTTON}}" not in en_home


def test_llms_txt_curates_site(tmp_db):
    with TestClient(m.app) as client:
        resp = client.get("/llms.txt")
        assert resp.status_code == 200
        text = resp.text
        assert "Shenyuan International" in text
        assert "## Services" in text and "/services/trade" in text
        assert "## Country pages" in text
        for slug in ("united-states", "hong-kong", "germany", "switzerland"):
            assert f"/countries/{slug}" in text, slug
        assert "## Legal guides (articles)" in text
        assert "/articles/legacy-foreign-heirs-inheriting-china-property-process-and-tax" in text


def test_head_requests_supported_on_core_pages(tmp_db):
    # Search engines and uptime tools probe URLs with HEAD; 405 breaks that.
    with TestClient(m.app) as client:
        for path in ("/", "/services/trade", "/articles",
                     "/articles/trade-payment-recovery-5-steps",
                     "/countries", "/countries/united-states",
                     "/robots.txt", "/llms.txt", "/sitemap.xml"):
            assert client.head(path).status_code == 200, path


def test_404_returns_html_for_browsers_json_for_api(tmp_db):
    with TestClient(m.app) as client:
        html_resp = client.get("/no-such-page", headers={"accept": "text/html"})
        assert html_resp.status_code == 404
        assert "text/html" in html_resp.headers["content-type"]
        assert "404" in html_resp.text
        assert "/articles" in html_resp.text  # recovery links
        json_resp = client.get("/no-such-page", headers={"accept": "application/json"})
        assert json_resp.status_code == 404
        assert "application/json" in json_resp.headers["content-type"]


def test_twitter_cards_and_og_image_on_core_pages(tmp_db):
    with TestClient(m.app) as client:
        for path in ("/", "/services/trade", "/countries/united-states",
                     "/articles/trade-payment-recovery-5-steps"):
            html = client.get(path).text
            assert 'name="twitter:card" content="summary_large_image"' in html, path
            assert 'property="og:image"' in html, path
        article = client.get("/articles/trade-payment-recovery-5-steps").text
        assert '"dateModified"' in article  # BlogPosting completeness


def test_sitemap_and_robots_accept_head(tmp_db):
    # Regression: GSC's fetcher probes with HEAD; a 405 there surfaces as
    # "couldn't fetch" in Search Console even though GET works fine.
    with TestClient(m.app) as client:
        assert client.head("/sitemap.xml").status_code == 200
        assert client.head("/robots.txt").status_code == 200


def test_ga_tag_absent_without_config(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.delenv("GA_MEASUREMENT_ID", raising=False)
    try:
        with TestClient(m.app) as client:
            # Without a measurement ID the gtag LOADER must not be injected;
            # conversion-event calls may still be present (guarded at runtime).
            for path in ("/", "/services/trade", "/articles", "/articles/trade-payment-recovery-5-steps"):
                html = client.get(path).text
                assert "gtag/js?id=" not in html, path
                assert "gtag('config'" not in html, path
    finally:
        monkeypatch.undo()


def test_ga_tag_injected_when_configured(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("GA_MEASUREMENT_ID", "G-TEST123")
    try:
        with TestClient(m.app) as client:
            for path in ("/", "/services/trade", "/articles", "/articles/trade-payment-recovery-5-steps"):
                text = client.get(path).text
                assert "gtag/js?id=G-TEST123" in text, path
                assert "gtag('config','G-TEST123')" in text, path
    finally:
        monkeypatch.undo()
