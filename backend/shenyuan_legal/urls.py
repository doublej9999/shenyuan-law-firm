from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from shenyuan_legal.api import api
from apps.content.models import ContentArticle
from apps.content.seo_service import generate_sitemap_xml, generate_robots_txt, render_article_seo_html

def sitemap_view(request):
    xml_content = generate_sitemap_xml()
    resp = HttpResponse(xml_content, content_type="application/xml; charset=utf-8")
    resp["Cache-Control"] = "public, s-maxage=3600, stale-while-revalidate=86400"
    return resp

def robots_view(request):
    robots_content = generate_robots_txt()
    resp = HttpResponse(robots_content, content_type="text/plain; charset=utf-8")
    resp["Cache-Control"] = "public, s-maxage=86400"
    return resp

def article_seo_view(request, slug: str):
    article = get_object_or_404(ContentArticle, slug=slug, status="published")
    html_content = render_article_seo_html(article, is_en=False)
    resp = HttpResponse(html_content, content_type="text/html; charset=utf-8")
    resp["Cache-Control"] = "public, s-maxage=300, stale-while-revalidate=1200"
    return resp

def article_seo_en_view(request, slug: str):
    article = get_object_or_404(ContentArticle, slug=slug, status="published")
    html_content = render_article_seo_html(article, is_en=True)
    resp = HttpResponse(html_content, content_type="text/html; charset=utf-8")
    resp["Cache-Control"] = "public, s-maxage=300, stale-while-revalidate=1200"
    return resp

urlpatterns = [
    path("sitemap.xml", sitemap_view, name="sitemap"),
    path("robots.txt", robots_view, name="robots"),
    path("articles/<slug:slug>", article_seo_view, name="article_seo"),
    path("en/articles/<slug:slug>", article_seo_en_view, name="article_seo_en"),
    path("django-admin/", admin.site.urls),
    path("", api.urls),
]
