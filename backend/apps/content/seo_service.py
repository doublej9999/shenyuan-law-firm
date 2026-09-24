"""Search-engine surface for the public site: sitemap, robots.txt, llms.txt,
article crawler HTML, and search-engine notification.

One rule governs this module: **never advertise a URL the frontend does not
serve.** A sitemap full of 404s is worse than a short sitemap. Page families are
therefore gated by ``SITEMAP_ROUTE_FAMILIES`` so a family only appears once the
Nuxt frontend actually renders it.
"""

from __future__ import annotations

import html
import json
import logging
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from apps.content import site_content
from apps.content.models import ContentArticle

logger = logging.getLogger(__name__)

SITE_NAME_ZH = "深远(国际)律师事务所"
SITE_NAME_EN = "Shenyuan International Law Firm"
DEFAULT_SITE_URL = "https://shenyuanlegal.com"

# Page families the frontend serves. Keep this in lockstep with
# `frontend-web/pages/**`; a family listed here but not shipped puts 404s in
# front of crawlers.
#
# Every family below now has pages behind it. `SITEMAP_ROUTE_FAMILIES` remains as
# an override so a family can be pulled from the sitemap without a deploy if a
# route family is ever taken offline.
SHIPPED_ROUTE_FAMILIES = "core,articles,countries,services"
DEFAULT_ROUTE_FAMILIES = SHIPPED_ROUTE_FAMILIES

# Marketing pages that exist in both languages: (zh_path, en_path, changefreq, priority)
STATIC_PAIRS: List[Tuple[str, str, str, str]] = [
    ("/", "/en", "daily", "1.0"),
    ("/services", "/en/services", "weekly", "0.9"),
    ("/articles", "/en/articles", "daily", "0.9"),
]

# Landing-page families that also have an index page.
FAMILY_INDEX: Dict[str, Tuple[str, str, str, str]] = {
    "countries": ("/countries", "/en/countries", "weekly", "0.8"),
    "services": ("", "", "weekly", "0.8"),  # no index page: /services is in STATIC_PAIRS
}


def get_base_url() -> str:
    """Canonical site origin, normalised without a trailing slash."""
    return os.environ.get("SITE_URL", DEFAULT_SITE_URL).rstrip("/")


def _enabled_families() -> set:
    raw = os.environ.get("SITEMAP_ROUTE_FAMILIES", DEFAULT_ROUTE_FAMILIES)
    return {part.strip() for part in raw.split(",") if part.strip()}


def _hreflang_links(base_url: str, zh_path: str, en_path: str, indent: str = "    ") -> str:
    """xhtml:link alternates for a zh/en URL pair, including x-default."""
    return (
        f'{indent}<xhtml:link rel="alternate" hreflang="zh-CN" href="{base_url}{zh_path}"/>\n'
        f'{indent}<xhtml:link rel="alternate" hreflang="en" href="{base_url}{en_path}"/>\n'
        f'{indent}<xhtml:link rel="alternate" hreflang="x-default" href="{base_url}{zh_path}"/>\n'
    )


def frontend_routes() -> List[Dict[str, str]]:
    """Every non-article frontend URL the sitemap should advertise.

    Returns dicts of ``{zh, en, changefreq, priority}``. Article detail URLs are
    derived from the database in :func:`generate_sitemap_xml` instead, because
    they carry a real ``lastmod``.
    """
    families = _enabled_families()
    routes: List[Dict[str, str]] = []

    def add(zh: str, en: str, changefreq: str, priority: str) -> None:
        routes.append({"zh": zh, "en": en, "changefreq": changefreq, "priority": priority})

    if "core" in families:
        for zh, en, changefreq, priority in STATIC_PAIRS:
            add(zh, en, changefreq, priority)

    if "countries" in families:
        zh_index, en_index, changefreq, priority = FAMILY_INDEX["countries"]
        add(zh_index, en_index, changefreq, priority)
        for slug in site_content.get_countries():
            add(f"/countries/{slug}", f"/en/countries/{slug}", "monthly", "0.7")

    if "services" in families:
        for slug in site_content.get_services():
            add(f"/services/{slug}", f"/en/services/{slug}", "monthly", "0.8")

    return routes


def generate_sitemap_xml() -> str:
    """Sitemaps 0.9 document with zh/en pairs linked by hreflang and x-default."""
    base_url = get_base_url()
    entries: List[str] = []

    for route in frontend_routes():
        zh_loc = f"{base_url}{route['zh']}"
        en_loc = f"{base_url}{route['en']}"
        for loc in (zh_loc, en_loc):
            entries.append(
                "  <url>\n"
                f"    <loc>{loc}</loc>\n"
                f"    <changefreq>{route['changefreq']}</changefreq>\n"
                f"    <priority>{route['priority']}</priority>\n"
                + _hreflang_links(base_url, route["zh"], route["en"])
                + "  </url>\n"
            )

    if "articles" in _enabled_families():
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        published = ContentArticle.objects.filter(status="published").order_by("-published_at")
        for article in published:
            slug = html.escape(article.slug)
            dt = article.published_at or article.updated_at
            lastmod = dt.strftime("%Y-%m-%d") if dt else now
            zh_path = f"/articles/{slug}"
            en_path = f"/en/articles/{slug}"
            for loc in (f"{base_url}{zh_path}", f"{base_url}{en_path}"):
                entries.append(
                    "  <url>\n"
                    f"    <loc>{loc}</loc>\n"
                    f"    <lastmod>{lastmod}</lastmod>\n"
                    "    <changefreq>weekly</changefreq>\n"
                    "    <priority>0.8</priority>\n"
                    + _hreflang_links(base_url, zh_path, en_path)
                    + "  </url>\n"
                )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "".join(entries)
        + "</urlset>"
    )


def generate_robots_txt() -> str:
    """robots.txt that welcomes AI answer engines and Chinese search engines."""
    base_url = get_base_url()
    return (
        "# Shenyuan International — shenyuanlegal.com\n"
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /admin/\n"
        "Disallow: /django-admin/\n"
        "\n"
        "# AI / LLM crawlers are explicitly welcome (GEO):\n"
        "User-agent: GPTBot\n"
        "Allow: /\n"
        "User-agent: OAI-SearchBot\n"
        "Allow: /\n"
        "User-agent: ChatGPT-User\n"
        "Allow: /\n"
        "User-agent: ClaudeBot\n"
        "Allow: /\n"
        "User-agent: PerplexityBot\n"
        "Allow: /\n"
        "User-agent: Google-Extended\n"
        "Allow: /\n"
        "\n"
        "# Chinese search engines:\n"
        "User-agent: Baiduspider\n"
        "Allow: /\n"
        "User-agent: Sogou web spider\n"
        "Allow: /\n"
        "User-agent: 360Spider\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {base_url}/sitemap.xml\n"
        f"LLMtxt: {base_url}/llms.txt\n"
    )


def generate_llms_txt() -> str:
    """llms.txt (llmstxt.org): a curated, LLM-readable map of the site.

    Gives ChatGPT / Claude / Perplexity a single entry point instead of making
    them reverse-engineer a JavaScript app.
    """
    articles = list(
        ContentArticle.objects.filter(status="published").order_by("-published_at")[:25]
    )
    lines: List[str] = [
        f"# {SITE_NAME_ZH} / {SITE_NAME_EN}",
        "",
        "> Cross-border dispute resolution and family asset protection for Chinese "
        "businesses and families. Bilingual (中文/EN). Trade disputes, debt recovery, "
        "judgment and arbitral award enforcement, asset tracing, cross-border "
        "inheritance. Local counsel network in 30+ jurisdictions. Free initial "
        "assessment with a 24-hour response.",
        "",
        "## Services",
    ]
    for slug, service in site_content.get_services().items():
        lines.append(
            f"- [{service['en_title']} ({service['zh_title']})](/services/{slug}) — "
            f"{service['en_intro']}"
        )

    lines += ["", "## Country pages"]
    for slug, country in site_content.get_countries().items():
        lines.append(
            f"- [{country['name_en']} ({country['name_zh']})](/countries/{slug}) — "
            f"{country['en_title']}"
        )

    lines += ["", "## Legal guides (articles)"]
    for article in articles:
        title = article.title_en or article.title_zh
        description = (article.description_en or article.description_zh or "")[:160]
        lines.append(f"- [{title}](/articles/{article.slug}) — {description}")

    lines += [
        "",
        "## Contact",
        "- Website: /",
        "- Intake form: /#intake — free initial assessment, 24h response",
        "- AI assistant: chat widget on every page (English/中文)",
        "",
    ]
    return "\n".join(lines)


def _get_google_token() -> Optional[str]:
    sa_path = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip() or os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS", ""
    ).strip()
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
    """Push a newly published article to Google, Baidu and IndexNow."""
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
    baidu_site = os.environ.get("BAIDU_SITE", DEFAULT_SITE_URL).strip()
    if baidu_token:
        try:
            api_url = f"http://data.zz.baidu.com/urls?site={baidu_site}&token={baidu_token}"
            body = "\n".join(urls).encode("utf-8")
            req = urllib.request.Request(
                api_url, data=body, method="POST", headers={"Content-Type": "text/plain"}
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
            payload = {"host": host, "key": indexnow_key, "urlList": urls}
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


# --------------------------------------------------------------------------- #
# Crawler-facing article HTML
# --------------------------------------------------------------------------- #

# Inline markdown the legacy article bodies actually use.
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def _inline(text: str, base_url: str) -> str:
    """Escape and inline-render a single line of markdown."""
    out = html.escape(text)

    def render_link(match: "re.Match[str]") -> str:
        label, href = match.group(1), match.group(2)
        # Root-relative links must be absolute so a crawler is not left guessing.
        if href.startswith("/"):
            href = f"{base_url}{href}"
        if href.startswith("http") and not href.startswith(base_url):
            return f'<a href="{href}" rel="noopener">{label}</a>'
        return f'<a href="{href}">{label}</a>'

    out = _LINK_RE.sub(render_link, out)
    out = _BOLD_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>", out)
    return out


def _render_markdown(body: str, base_url: str) -> str:
    """Minimal, dependency-free markdown renderer for article bodies."""
    out: List[str] = []
    list_open = False

    def close_list() -> None:
        nonlocal list_open
        if list_open:
            out.append("</ul>")
            list_open = False

    for raw in (body or "").replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if not line:
            close_list()
            continue
        if line.startswith(("- ", "* ")):
            if not list_open:
                out.append("<ul>")
                list_open = True
            out.append(f"  <li>{_inline(line[2:], base_url)}</li>")
            continue
        close_list()
        if line.startswith("#### "):
            out.append(f"<h4>{_inline(line[5:], base_url)}</h4>")
        elif line.startswith("### "):
            out.append(f"<h3>{_inline(line[4:], base_url)}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{_inline(line[3:], base_url)}</h2>")
        elif line.startswith("# "):
            out.append(f"<h2>{_inline(line[2:], base_url)}</h2>")
        elif line.startswith("> "):
            out.append(f"<blockquote><p>{_inline(line[2:], base_url)}</p></blockquote>")
        else:
            out.append(f"<p>{_inline(line, base_url)}</p>")

    close_list()
    return "\n".join(out)


_ARTICLE_CSS = """
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.8; color: #2c3e50; max-width: 860px; margin: 0 auto; padding: 40px 20px; }
    h1 { font-size: 28px; color: #0a3641; margin-bottom: 24px; }
    h2 { font-size: 22px; color: #0a3641; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-top: 36px; }
    h3 { font-size: 18px; color: #1f2937; margin-top: 24px; }
    p { margin-bottom: 16px; text-align: justify; }
    ul { padding-left: 22px; margin-bottom: 16px; }
    blockquote { border-left: 4px solid #0d9488; padding: 10px 18px; background: #f8fafc; color: #4b5563; margin: 20px 0; }
    .disclaimer { background: #fefce8; border: 1px solid #fef08a; padding: 14px 18px; border-radius: 6px; font-size: 13px; margin-top: 36px; color: #713f12; }
    .cta-box { background: #f0fdfa; border: 1px solid #ccfbf1; padding: 20px; border-radius: 8px; margin-top: 28px; text-align: center; }
    .cta-btn { display: inline-block; background: #0d9488; color: #fff; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 10px; }
""".strip()


def render_article_seo_html(article: ContentArticle, is_en: bool = False) -> str:
    """Crawler-facing HTML for one article, with full meta and JSON-LD.

    This is the fallback for anything reaching the Django host directly. The
    Nuxt frontend renders the same page for normal traffic.
    """
    base_url = get_base_url()
    site_name = SITE_NAME_EN if is_en else SITE_NAME_ZH
    lang = "en" if is_en else "zh-CN"

    title = (article.title_en if is_en else article.title_zh) or article.title_zh
    desc = (article.description_en if is_en else article.description_zh) or article.description_zh
    body_md = (article.body_en if is_en else article.body_zh) or article.body_zh

    body_html = _render_markdown(body_md, base_url)

    canonical_url = f"{base_url}{'/en' if is_en else ''}/articles/{article.slug}"
    zh_url = f"{base_url}/articles/{article.slug}"
    en_url = f"{base_url}/en/articles/{article.slug}"

    json_ld_article = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": desc,
            "inLanguage": lang,
            "datePublished": article.published_at.isoformat() if article.published_at else "",
            "dateModified": article.updated_at.isoformat() if article.updated_at else "",
            # No `image`: the site has no per-article social card yet. A 404 in
            # og:image is worse than an absent one, so this waits for the asset.
            "author": {
                "@type": "Organization",
                "name": "Shenyuan International Legal Team",
                "url": base_url,
            },
            "publisher": {"@type": "Organization", "name": site_name, "url": base_url},
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical_url},
        },
        ensure_ascii=False,
    )

    json_ld_breadcrumb = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home" if is_en else "首页",
                    "item": f"{base_url}/en" if is_en else f"{base_url}/",
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Articles" if is_en else "文章",
                    "item": f"{base_url}/en/articles" if is_en else f"{base_url}/articles",
                },
                {"@type": "ListItem", "position": 3, "name": title, "item": canonical_url},
            ],
        },
        ensure_ascii=False,
    )

    disclaimer = (
        "The insights contained in this publication are intended for general information "
        "and practical commentary only. They do not constitute formal legal opinion or "
        "create an attorney-client relationship for any specific matter."
        if is_en
        else "本文内容仅供涉外法律实务研讨与一般信息参考，不构成针对任何具体案件的正式法律意见或委托代理关系。"
        "具体法律程序须结合案件全部证据、事实及相关管辖区法规一案一议。"
    )
    cta_heading = (
        "Facing a similar cross-border legal issue?"
        if is_en
        else "遇到类似跨境纠纷或需要法律协助？"
    )
    cta_body = (
        "Our bilingual legal team provides initial case reviews within 24 hours."
        if is_en
        else "我们拥有覆盖全球 30+ 司法辖区的涉外团队，为您提供初步案情分析与实务方案评估。"
    )
    cta_label = "Free Legal Consultation →" if is_en else "免费法律咨询评估 →"
    cta_href = f"{base_url}{'/en' if is_en else ''}/#intake"
    published_label = article.published_at.strftime("%Y-%m-%d") if article.published_at else ""

    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | {site_name}</title>
  <meta name="description" content="{html.escape(desc or '')}">
  <link rel="canonical" href="{canonical_url}">
  <link rel="alternate" hreflang="zh-CN" href="{zh_url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="x-default" href="{zh_url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{html.escape(site_name)}">
  <meta property="og:locale" content="{'en_US' if is_en else 'zh_CN'}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc or '')}">
  <meta property="og:url" content="{canonical_url}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{json_ld_article}</script>
  <script type="application/ld+json">{json_ld_breadcrumb}</script>
  <style>
{_ARTICLE_CSS}
  </style>
</head>
<body>
  <article>
    <header>
      <div style="color: #6b7280; font-size: 13px; margin-bottom: 10px;">
        <span>{html.escape(article.business.upper())}</span> &bull; <span>{published_label}</span>
      </div>
      <h1>{html.escape(title)}</h1>
    </header>
    <main>
      {body_html}
    </main>
    <div class="disclaimer">
      <strong>{'Legal Disclaimer' if is_en else '免责声明'}：</strong>
      <span>{disclaimer}</span>
    </div>
    <div class="cta-box">
      <h3>{cta_heading}</h3>
      <p>{cta_body}</p>
      <a href="{cta_href}" class="cta-btn">{cta_label}</a>
    </div>
  </article>
</body>
</html>"""
