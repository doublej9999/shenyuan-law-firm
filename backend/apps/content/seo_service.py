import html
import json
import logging
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

from apps.content.models import ContentArticle

logger = logging.getLogger(__name__)

DEFAULT_SITE_URL = os.environ.get("SITE_URL", "https://shenyuanlegal.com").rstrip("/")

def get_base_url() -> str:
    return os.environ.get("SITE_URL", "https://shenyuanlegal.com").rstrip("/")

def generate_sitemap_xml() -> str:
    """生成符合 Sitemaps XML 协议且包含中英双语与 xhtml:link 互链的站点地图"""
    base_url = get_base_url()
    entries: List[str] = []

    # 1. 静态基础页面（双语）
    static_routes = [
        ("/", "/en/"),
        ("/services", "/en/services"),
        ("/articles", "/en/articles"),
    ]

    for zh_path, en_path in static_routes:
        entries.append(
            f'  <url>\n'
            f'    <loc>{base_url}{zh_path}</loc>\n'
            f'    <changefreq>daily</changefreq>\n'
            f'    <priority>1.0</priority>\n'
            f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{base_url}{zh_path}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en" href="{base_url}{en_path}"/>\n'
            f'  </url>\n'
        )
        entries.append(
            f'  <url>\n'
            f'    <loc>{base_url}{en_path}</loc>\n'
            f'    <changefreq>daily</changefreq>\n'
            f'    <priority>0.9</priority>\n'
            f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{base_url}{zh_path}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en" href="{base_url}{en_path}"/>\n'
            f'  </url>\n'
        )

    # 2. 动态已发布文章列表
    published_articles = ContentArticle.objects.filter(status="published").order_by("-published_at")
    for article in published_articles:
        slug = html.escape(article.slug)
        dt = article.published_at or article.updated_at
        lastmod = dt.strftime("%Y-%m-%d") if dt else datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        zh_loc = f"{base_url}/articles/{slug}"
        en_loc = f"{base_url}/en/articles/{slug}"

        # 中文文章 URL 节点
        entries.append(
            f'  <url>\n'
            f'    <loc>{zh_loc}</loc>\n'
            f'    <lastmod>{lastmod}</lastmod>\n'
            f'    <changefreq>weekly</changefreq>\n'
            f'    <priority>0.8</priority>\n'
            f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{zh_loc}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en" href="{en_loc}"/>\n'
            f'  </url>\n'
        )

        # 英文文章 URL 节点
        entries.append(
            f'  <url>\n'
            f'    <loc>{en_loc}</loc>\n'
            f'    <lastmod>{lastmod}</lastmod>\n'
            f'    <changefreq>weekly</changefreq>\n'
            f'    <priority>0.8</priority>\n'
            f'    <xhtml:link rel="alternate" hreflang="zh-CN" href="{zh_loc}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en" href="{en_loc}"/>\n'
            f'  </url>\n'
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "".join(entries)
        + "</urlset>"
    )
    return xml


def generate_robots_txt() -> str:
    """生成利于主流搜索引擎抓取的 robots.txt"""
    base_url = get_base_url()
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /api/\n"
        f"Sitemap: {base_url}/sitemap.xml\n"
    )


def _get_google_token() -> str | None:
    sa_path = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip() or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not sa_path or not Path(sa_path).exists():
        return None
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(
            sa_path, scopes=["https://www.googleapis.com/auth/indexing"]
        )
        creds.refresh(Request())
        return creds.token
    except Exception as exc:
        logger.warning(f"Google service account auth failed: {exc}")
        return None


def notify_search_engines(slug: str) -> Dict[str, Any]:
    """文章发布后自动联动推送 Google Indexing API、百度推送和 IndexNow"""
    base_url = get_base_url()
    urls = [
        f"{base_url}/articles/{slug}",
        f"{base_url}/en/articles/{slug}",
    ]
    results: Dict[str, Any] = {
        "google": {"status": "skipped", "message": "GSC service account not configured"},
        "baidu": {"status": "skipped", "message": "Baidu push token not configured"},
        "indexnow": {"status": "skipped", "message": "IndexNow key not configured"},
    }

    # 1. Google Indexing API
    g_token = _get_google_token()
    if g_token:
        g_results = []
        for u in urls:
            try:
                body = json.dumps({"url": u, "type": "URL_UPDATED"}).encode("utf-8")
                req = urllib.request.Request(
                    "https://indexing.googleapis.com/v3/urlNotifications:publish",
                    data=body,
                    method="POST",
                    headers={"Authorization": f"Bearer {g_token}", "Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    g_results.append({"url": u, "code": resp.status})
            except Exception as e:
                g_results.append({"url": u, "error": str(e)})
        results["google"] = {"status": "completed", "details": g_results}

    # 2. 百度站长平台主动推送 (API Push)
    baidu_token = os.environ.get("BAIDU_PUSH_TOKEN", "").strip()
    baidu_site = os.environ.get("BAIDU_SITE", "https://shenyuanlegal.com").strip()
    if baidu_token:
        try:
            api_url = f"http://data.zz.baidu.com/urls?site={baidu_site}&token={baidu_token}"
            body = "\n".join(urls).encode("utf-8")
            req = urllib.request.Request(
                api_url,
                data=body,
                method="POST",
                headers={"Content-Type": "text/plain"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                results["baidu"] = {"status": "completed", "response": resp_data}
        except Exception as e:
            results["baidu"] = {"status": "error", "message": str(e)}

    # 3. Bing / IndexNow
    indexnow_key = os.environ.get("INDEXNOW_KEY", "").strip()
    if indexnow_key:
        try:
            host = urllib.parse.urlparse(base_url).netloc
            payload = {
                "host": host,
                "key": indexnow_key,
                "urlList": urls,
            }
            req = urllib.request.Request(
                "https://api.indexnow.org/IndexNow",
                data=json.dumps(payload).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                results["indexnow"] = {"status": "completed", "code": resp.status}
        except Exception as e:
            results["indexnow"] = {"status": "error", "message": str(e)}

    return results


def render_article_seo_html(article: ContentArticle, is_en: bool = False) -> str:
    """为搜索引擎爬虫与边缘直出渲染带有全量 SEO Meta 与 JSON-LD 结构化数据的完整 HTML"""
    base_url = get_base_url()
    title = (article.title_en if is_en else article.title_zh) or article.title_zh
    desc = (article.description_en if is_en else article.description_zh) or article.description_zh
    body_md = (article.body_en if is_en else article.body_zh) or article.body_zh

    # 简单格式化 Markdown 为基础 HTML 段落与标题
    body_html_parts = []
    for line in body_md.replace("\r\n", "\n").split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#### "):
            body_html_parts.append(f"<h4>{html.escape(line[5:])}</h4>")
        elif line.startswith("### "):
            body_html_parts.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            body_html_parts.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            body_html_parts.append(f"<h2>{html.escape(line[2:])}</h2>")
        elif line.startswith("- ") or line.startswith("* "):
            body_html_parts.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.startswith("> "):
            body_html_parts.append(f"<blockquote><p>{html.escape(line[2:])}</p></blockquote>")
        else:
            body_html_parts.append(f"<p>{html.escape(line)}</p>")
    body_html = "\n".join(body_html_parts)

    canonical_url = f"{base_url}{'/en' if is_en else ''}/articles/{article.slug}"
    zh_url = f"{base_url}/articles/{article.slug}"
    en_url = f"{base_url}/en/articles/{article.slug}"
    site_name = "Shenyuan International Law Firm" if is_en else "深远(国际)律师事务所"

    json_ld_article = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "datePublished": article.published_at.isoformat() if article.published_at else "",
        "dateModified": article.updated_at.isoformat() if article.updated_at else "",
        "author": {
            "@type": "Organization",
            "name": "Shenyuan International Legal Team",
            "url": base_url,
        },
        "publisher": {
            "@type": "Organization",
            "name": site_name,
            "url": base_url,
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": canonical_url
        }
    }, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="{'en' if is_en else 'zh-CN'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | {site_name}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{canonical_url}">
  <link rel="alternate" hreflang="zh-CN" href="{zh_url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical_url}">
  <script type="application/ld+json">{json_ld_article}</script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.8; color: #2c3e50; max-width: 860px; margin: 0 auto; padding: 40px 20px; }}
    h1 {{ font-size: 28px; color: #0a3641; margin-bottom: 24px; }}
    h2 {{ font-size: 22px; color: #0a3641; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-top: 36px; }}
    h3 {{ font-size: 18px; color: #1f2937; margin-top: 24px; }}
    p {{ margin-bottom: 16px; text-align: justify; }}
    blockquote {{ border-left: 4px solid #0d9488; padding: 10px 18px; background: #f8fafc; color: #4b5563; margin: 20px 0; }}
    .disclaimer {{ background: #fefce8; border: 1px solid #fef08a; padding: 14px 18px; border-radius: 6px; font-size: 13px; margin-top: 36px; color: #713f12; }}
    .cta-box {{ background: #f0fdfa; border: 1px solid #ccfbf1; padding: 20px; border-radius: 8px; margin-top: 28px; text-align: center; }}
    .cta-btn {{ display: inline-block; background: #0d9488; color: #fff; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 10px; }}
  </style>
</head>
<body>
  <article>
    <header>
      <div style="color: #6b7280; font-size: 13px; margin-bottom: 10px;">
        <span>{article.business.upper()}</span> &bull; <span>{article.published_at.strftime('%Y-%m-%d') if article.published_at else ''}</span>
      </div>
      <h1>{html.escape(title)}</h1>
    </header>
    <main>
      {body_html}
    </main>
    <div class="disclaimer">
      <strong>{'免责声明' if not is_en else 'Legal Disclaimer'}：</strong>
      <span>{'本文内容仅供涉外法律实务研讨与一般信息参考，不构成针对任何具体案件的正式法律意见或委托代理关系。具体法律程序须结合案件全部证据、事实及相关管辖区法规一案一议。' if not is_en else 'The insights contained in this publication are intended for general information and practical commentary only. They do not constitute formal legal opinion or create an attorney-client relationship for any specific matter.'}</span>
    </div>
    <div class="cta-box">
      <h3>{'遇到类似跨境纠纷或需要法律协助？' if not is_en else 'Facing a similar cross-border legal issue?'}</h3>
      <p>{'我们拥有覆盖全球 30+ 司法辖区的涉外团队，为您提供初步案情分析与实务方案评估。' if not is_en else 'Our bilingual legal team provides initial case reviews within 24 hours.'}</p>
      <a href="{base_url}{'/en' if is_en else ''}#intake" class="cta-btn">{'免费法律咨询评估 →' if not is_en else 'Free Legal Consultation →'}</a>
    </div>
  </article>
</body>
</html>"""

