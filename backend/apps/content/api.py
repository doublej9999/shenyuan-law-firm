from typing import List, Optional
from datetime import datetime
from ninja import Router, Schema
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.content.models import ContentArticle, ArticleVersion
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

# 公开阅读接口
@router.get("/api/articles", response=List[ArticleOut])
def get_public_articles(request, business: Optional[str] = None):
    qs = ContentArticle.objects.filter(status="published")
    if business:
        qs = qs.filter(business=business)
    return list(qs)

@router.get("/api/articles/{slug}", response=ArticleOut)
def get_public_article_by_slug(request, slug: str):
    return get_object_or_404(ContentArticle, slug=slug, status="published")

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
    return article
