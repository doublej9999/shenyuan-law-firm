from ninja import NinjaAPI
from apps.intakes.api import router as intakes_router
from apps.content.api import router as content_router
from apps.content.site_content_api import router as site_content_router
from apps.research.api import router as research_router
from apps.marketing.api import router as marketing_router

api = NinjaAPI(
    title="深远律师事务所 API (Django Ninja)",
    version="2.0.0",
    description="涉外法律事务、在线线索流转 CRM、多语言 CMS 与法律智能调研助手",
)

@api.get("/api/health")
def health_check(request):
    db_status = "unknown"
    db_error = None
    db_tables = []
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            db_status = f"connected ({row[0]})"
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            db_tables = [r[0] for r in cursor.fetchall()]
    except Exception as exc:
        db_status = "error"
        db_error = str(exc)
    return {
        "status": "ok",
        "framework": "Django Ninja",
        "storage": "Supabase",
        "db": db_status,
        "db_error": db_error,
        "tables": db_tables,
    }

api.add_router("", intakes_router)
api.add_router("", content_router)
api.add_router("", site_content_router)
api.add_router("", research_router)
api.add_router("", marketing_router)
