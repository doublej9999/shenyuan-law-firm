import os
import sys
import sqlite3
from pathlib import Path

# 把 backend 加入 sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shenyuan_legal.settings")

import django
django.setup()

from apps.intakes.models import Intake, IntakeFile
from apps.content.models import ContentArticle, ArticleVersion
from apps.core.models import AuditLog, PageView, SearchLog

def migrate():
    sqlite_path = BASE_DIR.parent / "data" / "lawyers.sqlite3"
    if not sqlite_path.exists():
        print(f"SQLite DB not found at {sqlite_path}, skipping.")
        return

    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("Migrating intakes...")
    try:
        cursor.execute("SELECT * FROM intakes")
        rows = cursor.fetchall()
        for r in rows:
            d = dict(r)
            Intake.objects.update_or_create(
                id=d["id"],
                defaults={
                    "name": d["name"],
                    "email": d.get("email"),
                    "phone": d.get("phone"),
                    "matter": d["matter"],
                    "summary": d["summary"],
                    "country_or_region": d.get("country_or_region"),
                    "language": d.get("language", "zh"),
                    "user_agent": d.get("user_agent"),
                    "status": d.get("status", "new"),
                    "note": d.get("note"),
                    "score": d.get("score", 0),
                    "source": d.get("source"),
                }
            )
        print(f"Migrated {len(rows)} intakes.")
    except Exception as e:
        print(f"Intakes migration warning: {e}")

    print("Migrating content_articles...")
    try:
        cursor.execute("SELECT * FROM content_articles")
        rows = cursor.fetchall()
        for r in rows:
            d = dict(r)
            ContentArticle.objects.update_or_create(
                id=d["id"],
                defaults={
                    "slug": d["slug"],
                    "title_zh": d.get("title_zh", ""),
                    "title_en": d.get("title_en", ""),
                    "description_zh": d.get("description_zh", ""),
                    "description_en": d.get("description_en", ""),
                    "body_zh": d.get("body_zh", ""),
                    "body_en": d.get("body_en", ""),
                    "business": d.get("business", "general"),
                    "intent": d.get("intent", "I"),
                    "status": d.get("status", "draft"),
                }
            )
        print(f"Migrated {len(rows)} articles.")
    except Exception as e:
        print(f"Content migration warning: {e}")

    conn.close()
    print("Migration finished successfully!")

if __name__ == "__main__":
    migrate()
