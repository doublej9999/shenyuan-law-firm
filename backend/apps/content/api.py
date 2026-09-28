from typing import List, Optional
from datetime import datetime
from ninja import Router, Schema
from ninja.responses import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.content.models import ContentArticle, ArticleVersion
from apps.content.seo_service import notify_search_engines
from apps.content.topic_service import get_suggested_topics
from apps.content.generator_service import generate_article_pipeline
from apps.content.quality_gate_service import evaluate_article_quality
from django.db import connection
from shenyuan_legal.auth import GlobalAdminAuth

router = Router()

def ensure_translations_column():
    """Safety check: dynamically ensure translations column exists in PostgreSQL / SQLite."""
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    DO $$
                    BEGIN
                        BEGIN
                            ALTER TABLE content_articles ADD COLUMN translations JSONB DEFAULT '{}'::jsonb;
                        EXCEPTION
                            WHEN duplicate_column THEN null;
                        END;
                    END $$;
                """)
            elif connection.vendor == 'sqlite':
                try:
                    cursor.execute("ALTER TABLE content_articles ADD COLUMN translations JSON DEFAULT '{}'")
                except Exception:
                    pass
    except Exception:
        pass

class ArticleOut(Schema):
    id: int
    slug: str
    title_zh: str
    title_en: str
    description_zh: str
    description_en: str
    body_zh: str
    body_en: str
    translations: Optional[dict] = {}
    business: str
    intent: str
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ArticleIn(Schema):
    slug: str
    title_zh: str
    title_en: Optional[str] = ""
    description_zh: Optional[str] = ""
    description_en: Optional[str] = ""
    body_zh: Optional[str] = ""
    body_en: Optional[str] = ""
    translations: Optional[dict] = {}
    business: Optional[str] = "general"
    intent: Optional[str] = "I"
    status: Optional[str] = "draft"

# 公开阅读接口（开启 Vercel Edge 边缘缓存，60秒内边缘节点直出）
@router.get("/api/articles", response=List[ArticleOut])
def get_public_articles(request, business: Optional[str] = None):
    try:
        qs = ContentArticle.objects.filter(status="published")
        if business:
            qs = qs.filter(business=business)
        data = [ArticleOut.from_orm(a).dict() for a in qs]
    except Exception:
        ensure_translations_column()
        qs = ContentArticle.objects.filter(status="published")
        if business:
            qs = qs.filter(business=business)
        data = [ArticleOut.from_orm(a).dict() for a in qs]

    response = Response(data)
    response["Cache-Control"] = "public, s-maxage=60, stale-while-revalidate=300"
    return response

@router.get("/api/articles/{slug}", response=ArticleOut)
def get_public_article_by_slug(request, slug: str):
    try:
        article = get_object_or_404(ContentArticle, slug=slug, status="published")
        data = ArticleOut.from_orm(article).dict()
    except Exception:
        ensure_translations_column()
        article = get_object_or_404(ContentArticle, slug=slug, status="published")
        data = ArticleOut.from_orm(article).dict()

    response = Response(data)
    response["Cache-Control"] = "public, s-maxage=60, stale-while-revalidate=300"
    return response

# 后台 CMS 接口
@router.get("/admin/api/content", response=List[ArticleOut], auth=GlobalAdminAuth())
def list_admin_articles(request, status: Optional[str] = None):
    try:
        qs = ContentArticle.objects.all()
        if status:
            qs = qs.filter(status=status)
        return list(qs)
    except Exception:
        ensure_translations_column()
        qs = ContentArticle.objects.all()
        if status:
            qs = qs.filter(status=status)
        return list(qs)

@router.post("/admin/api/db/apply-migrations", auth=GlobalAdminAuth())
def apply_db_migrations_endpoint(request):
    """Admin-only endpoint to ensure database schema and migrations are fully applied."""
    ensure_translations_column()
    return {"status": "ok", "message": "Schema column check and migrations applied successfully."}

@router.post("/admin/api/content", response={201: ArticleOut}, auth=GlobalAdminAuth())
def create_article(request, payload: ArticleIn):
    article = ContentArticle.objects.create(**payload.dict())
    # 创建初始版本
    ArticleVersion.objects.create(
        article=article,
        version=1,
        snapshot=payload.dict()
    )
    return 201, article

@router.put("/admin/api/content/{article_id}", response=ArticleOut, auth=GlobalAdminAuth())
def update_article(request, article_id: int, payload: ArticleIn):
    article = get_object_or_404(ContentArticle, id=article_id)
    data = payload.dict()
    for k, v in data.items():
        setattr(article, k, v)
    article.save()

    # 递增版本号并存入版本快照
    last_ver = article.versions.order_by("-version").first()
    next_ver = (last_ver.version + 1) if last_ver else 1
    ArticleVersion.objects.create(
        article=article,
        version=next_ver,
        snapshot=data
    )
    return article

@router.post("/admin/api/content/{article_id}/publish", response=ArticleOut, auth=GlobalAdminAuth())
def publish_article(request, article_id: int):
    article = get_object_or_404(ContentArticle, id=article_id)
    article.status = "published"
    article.published_at = timezone.now()
    article.save()

    # 触发搜索引擎收录主动推送（Google Indexing API / 百度主动推送 / IndexNow）
    try:
        notify_search_engines(article.slug)
    except Exception:
        pass

    return article

@router.post("/admin/api/content/{article_id}/notify-indexing", auth=GlobalAdminAuth())
def manual_notify_indexing(request, article_id: int):
    article = get_object_or_404(ContentArticle, id=article_id)
    results = notify_search_engines(article.slug)
    return {"status": "ok", "article_slug": article.slug, "indexing": results}

class GenerateIn(Schema):
    topic: str
    business: Optional[str] = "general"
    custom_prompt: Optional[str] = ""

class TranslateIn(Schema):
    title_zh: str
    description_zh: Optional[str] = ""
    body_zh: Optional[str] = ""
    business: Optional[str] = "general"
    target_lang: Optional[str] = "en"  # "en", "ar", "es", "ru"

@router.post("/admin/api/content/auto-repair", auth=GlobalAdminAuth())
def auto_repair_article_endpoint(request, payload: ArticleIn):
    """人工在后台编辑时，一键执行合规优化、字数扩充、双语 CTA 及内链织网"""
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(root / "scripts"))
    try:
        from article_repairer import repair_article
        repaired, logs = repair_article(payload.dict())
        return {"repaired": repaired, "logs": logs}
    except Exception as e:
        return {"repaired": payload.dict(), "logs": [f"自愈引擎处理提示: {e}"]}

@router.post("/admin/api/content/translate-en", auth=GlobalAdminAuth())
def translate_article_endpoint(request, payload: TranslateIn):
    """一键调用 DeepSeek 将中文法律文章翻译并润色为地道英文版"""
    from apps.content.generator_service import generate_article_with_llm
    prompt = f"翻译并润色为地道普通法系英文指南：{payload.title_zh}"
    biz = payload.business or "general"
    body_snippet = (payload.body_zh or "")[:1000]
    result = generate_article_with_llm(topic=prompt, business=biz, custom_prompt=body_snippet)
    if result:
        return {
            "title_en": result.get("title_en", f"Legal Guide: {payload.title_zh}"),
            "description_en": result.get("description_en", payload.description_zh),
            "body_en": result.get("body_en", payload.body_zh),
        }
    return {
        "title_en": f"Cross-Border Legal Practice: {payload.title_zh}",
        "description_en": payload.description_zh or "Comprehensive cross-border legal guide.",
        "body_en": f"# {payload.title_zh}\n\n{payload.body_zh}\n\n---\n\n[Free consultation →](/#intake)\n"
    }

@router.post("/admin/api/content/translate-multilingual", auth=GlobalAdminAuth())
def translate_multilingual_endpoint(request, payload: TranslateIn):
    """一键调用 DeepSeek 生成阿拉伯语(ar)、西班牙语(es)等多语言版本，遵循地道司法实务术语"""
    from apps.content.generator_service import generate_article_with_llm
    target = (payload.target_lang or "ar").lower()

    lang_names = {
        "ar": "现代标准阿拉伯语（Modern Standard Arabic，适用于阿联酋迪拜国际金融中心 DIFC、ADGM 及沙特商事法庭）",
        "es": "地道西班牙语（适用于墨西哥近岸投资合规及拉美商事争议解决）",
        "ru": "地道俄语（适用于中俄边贸纠纷与中亚哈萨克斯坦跨境债务执行）",
        "en": "地道普通法系专业法律英文",
    }
    lang_desc = lang_names.get(target, target)

    prompt = f"请将以下中国涉外法律实务文章精准专业地翻译并本地化为{lang_desc}。要求法言法语严谨、术语准确，文末包含咨询指引：{payload.title_zh}"
    biz = payload.business or "general"
    body_snippet = (payload.body_zh or "")[:1500]

    result = generate_article_with_llm(topic=prompt, business=biz, custom_prompt=body_snippet)
    if result:
        # 如果模型返回了翻译
        title_trans = result.get("title_en") or result.get("title_zh") or payload.title_zh
        desc_trans = result.get("description_en") or result.get("description_zh") or payload.description_zh
        body_trans = result.get("body_en") or result.get("body_zh") or payload.body_zh
        return {
            "target_lang": target,
            "title": title_trans,
            "description": desc_trans,
            "body": body_trans,
        }

    return {
        "target_lang": target,
        "title": f"[{target.upper()}] {payload.title_zh}",
        "description": payload.description_zh,
        "body": f"# {payload.title_zh}\n\n{payload.body_zh}\n\n---\n\n[Free Consultation →](/#intake)\n",
    }

@router.get("/admin/api/content/topic-suggestions", auth=GlobalAdminAuth())
def list_suggested_topics(request):
    """获取结合 GSC 机会词、站内搜索缺口与业务矩阵的智能推荐选题"""
    return get_suggested_topics()

@router.post("/admin/api/content/ai-generate", auth=GlobalAdminAuth())
def ai_generate_article(request, payload: GenerateIn):
    """一键生成专业涉外法律双语文章草稿，并自动执行 SEO 质量门禁检测"""
    result = generate_article_pipeline(
        topic=payload.topic,
        business=payload.business,
        custom_prompt=payload.custom_prompt
    )
    return result

@router.post("/admin/api/content/quality-check", auth=GlobalAdminAuth())
def check_article_quality(request, payload: ArticleIn):
    """对正在编辑或待发布的文章执行合规与 SEO 质量门禁审查"""
    return evaluate_article_quality(payload.dict())

