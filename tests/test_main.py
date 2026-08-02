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
    with TestClient(m.app) as client:
        # Unique emails so the dedupe check never fires; the rate limiter is
        # keyed by client IP, which stays the same.
        statuses = [
            client.post(
                "/api/intakes",
                json=dict(VALID_PAYLOAD, email=f"x{i}@test.com", name="x", matter="m", summary="s"),
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


def test_auto_reply_disabled_without_smtp(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_FROM", raising=False)
    try:
        m._send_auto_reply({"name": "x", "email": "x@test.com", "matter": "贸易", "summary": "s"})
    finally:
        monkeypatch.undo()


# --- File uploads ------------------------------------------------------


def _upload(client, intake_id, filename, content, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.post(
        f"/api/intakes/{intake_id}/files",
        files={"file": (filename, content)},
        headers=headers,
    )


def test_upload_valid_pdf(tmp_db):
    with TestClient(m.app) as client:
        intake_id = client.post("/api/intakes", json=VALID_PAYLOAD).json()["id"]
        resp = _upload(client, intake_id, "contract.pdf", b"%PDF-1.4 fake pdf content")
        assert resp.status_code == 200
        assert resp.json()["original_name"] == "contract.pdf"
        assert resp.json()["intake_id"] == intake_id

        # File is listed for admins.
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
        try:
            rows = client.get(
                f"/admin/api/intakes/{intake_id}/files",
                headers={"Authorization": "Bearer secret-token"},
            ).json()
            assert len(rows) == 1
            assert rows[0]["original_name"] == "contract.pdf"
        finally:
            monkeypatch.undo()


def test_upload_rejects_bad_extension(tmp_db):
    with TestClient(m.app) as client:
        intake_id = client.post("/api/intakes", json=VALID_PAYLOAD).json()["id"]
        resp = _upload(client, intake_id, "evil.exe", b"MZ fake exe")
        assert resp.status_code == 415


def test_upload_rejects_magic_mismatch(tmp_db):
    with TestClient(m.app) as client:
        intake_id = client.post("/api/intakes", json=VALID_PAYLOAD).json()["id"]
        resp = _upload(client, intake_id, "fake.pdf", b"not really a pdf")
        assert resp.status_code == 415


def test_upload_unknown_intake_404(tmp_db):
    with TestClient(m.app) as client:
        resp = _upload(client, 999, "a.pdf", b"%PDF-1.4 x")
        assert resp.status_code == 404


def test_admin_download_file(tmp_db):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    try:
        with TestClient(m.app) as client:
            intake_id = client.post("/api/intakes", json=VALID_PAYLOAD).json()["id"]
            _upload(client, intake_id, "contract.pdf", b"%PDF-1.4 hello")
            rows = client.get(
                f"/admin/api/intakes/{intake_id}/files",
                headers={"Authorization": "Bearer secret-token"},
            ).json()
            file_id = rows[0]["id"]
            resp = client.get(
                f"/admin/api/intakes/{intake_id}/files/{file_id}/download",
                headers={"Authorization": "Bearer secret-token"},
            )
            assert resp.status_code == 200
            assert resp.content == b"%PDF-1.4 hello"
            assert "contract.pdf" in resp.headers["content-disposition"]
    finally:
        monkeypatch.undo()


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
