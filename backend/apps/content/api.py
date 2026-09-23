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
from shenyuan_legal.auth import GlobalAdminAuth

router = Router()

class ArticleOut(Schema):
    id: int
    slug: str
    title_zh: str
    title_en: str
    description_zh: str
    description_en: str
    body_zh: str
    body_en: str
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
    business: Optional[str] = "general"
    intent: Optional[str] = "I"
    status: Optional[str] = "draft"

# 公开阅读接口（开启 Vercel Edge 边缘缓存，60秒内边缘节点直出）
@router.get("/api/articles", response=List[ArticleOut])
def get_public_articles(request, business: Optional[str] = None):
    qs = ContentArticle.objects.filter(status="published")
    if business:
        qs = qs.filter(business=business)
    data = [ArticleOut.from_orm(a).dict() for a in qs]
    response = Response(data)
    response["Cache-Control"] = "public, s-maxage=60, stale-while-revalidate=300"
    return response

@router.get("/api/articles/{slug}", response=ArticleOut)
def get_public_article_by_slug(request, slug: str):
    article = get_object_or_404(ContentArticle, slug=slug, status="published")
    data = ArticleOut.from_orm(article).dict()
    response = Response(data)
    response["Cache-Control"] = "public, s-maxage=60, stale-while-revalidate=300"
    return response

# 后台 CMS 接口
@router.get("/admin/api/content", response=List[ArticleOut], auth=GlobalAdminAuth())
def list_admin_articles(request, status: Optional[str] = None):
    qs = ContentArticle.objects.all()
    if status:
        qs = qs.filter(status=status)
    return list(qs)

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

