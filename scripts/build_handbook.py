#!/usr/bin/env python3
"""Build the 《跨境维权法律手册》 (Cross-Border Rights Handbook) as branded
HTML + PDF, compiled from all published articles.

Output:
  docs/handbook/handbook.html  (print-friendly, also served at /handbook)
  docs/handbook/handbook.pdf   (generated via Playwright chromium)

Usage: python3 scripts/build_handbook.py [--pdf]
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "content" / "articles"
OUT_DIR = ROOT / "docs" / "handbook"

BUSINESS_LABELS = {
    "trade": ("国际贸易争议", "International Trade Disputes", "TRADE"),
    "recovery": ("诉讼与债务追收", "Litigation & Debt Recovery", "RECOVERY"),
    "legacy": ("继承与家族资产", "Inheritance & Family Assets", "LEGACY"),
}


def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta


def split_body(text: str) -> tuple[str, str]:
    parts = text.split("<!-- EN -->", 1)
    zh = parts[0].strip()
    en = parts[1].strip() if len(parts) > 1 else ""
    # strip frontmatter from zh
    zh = re.sub(r"^---\n.*?\n---\n", "", zh, flags=re.S).strip()
    return zh, en


def load_articles() -> list[dict]:
    articles = []
    if not ARTICLES_DIR.exists():
        return articles
    for idx in sorted(ARTICLES_DIR.glob("*/index.md")):
        text = idx.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        zh, en = split_body(text)
        meta["slug"] = meta.get("slug", idx.parent.name)
        articles.append({"meta": meta, "zh": zh, "en": en})
    articles.sort(key=lambda a: a["meta"].get("business", ""))
    return articles


def build_html(articles: list[dict]) -> str:
    today = date.today().isoformat()
    chapters = ""
    toc_items = []
    for biz, (label_zh, label_en, tag) in BUSINESS_LABELS.items():
        group = [a for a in articles if a["meta"].get("business") == biz]
        if not group:
            continue
        toc_items.append(
            f'<li><a href="#{biz}"><span class="toc-tag">{tag}</span>{label_zh}'
            f'<span class="toc-count">{len(group)} 篇</span></a></li>'
        )
        arts = ""
        for a in group:
            title = a["meta"].get("title_zh", "")
            body = markdown.markdown(a["zh"], extensions=["extra", "sane_lists"])
            arts += (
                f'<article class="entry"><h3>{title}</h3>'
                f'<div class="body">{body}</div></article>'
            )
        chapters += (
            f'<section class="chapter" id="{biz}"><h2><span class="ch-tag">{tag}</span>'
            f"{label_zh}</h2>{arts}</section>"
        )
    toc = "".join(toc_items)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>跨境维权法律手册 · Shenyuan International</title>
<meta name="description" content="深远国际《跨境维权法律手册》：国际贸易争议、债务追收与跨境继承的实务路径汇编，由已发布法律专栏整理而成，仅供一般信息参考。">
<link rel="canonical" href="https://shenyuanlegal.com/handbook">
<link rel="alternate" hreflang="zh-CN" href="https://shenyuanlegal.com/handbook">
<meta property="og:type" content="website">
<meta property="og:title" content="跨境维权法律手册 · Shenyuan International">
<meta property="og:description" content="国际贸易争议、债务追收与跨境继承实务路径汇编。">
<meta property="og:image" content="https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1200&q=80">
<meta name="twitter:card" content="summary_large_image">
<style>
  @page {{ size: A4; margin: 18mm 16mm; @bottom-center {{ content: counter(page); font-size: 9px; color: #8a939b; }} }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Noto Serif SC", "Songti SC", SimSun, Georgia, serif;
          color: #172433; margin: 0; line-height: 1.75; font-size: 12.5px; }}
  .cover {{ text-align: center; padding: 90px 30px 40px; }}
  .cover .brand {{ color: #b08d57; letter-spacing: .35em; font-size: 13px; margin-bottom: 26px; }}
  .cover h1 {{ font-size: 34px; margin: 0 0 12px; color: #0d6c6b; }}
  .cover .sub {{ color: #627180; font-size: 14px; margin-bottom: 46px; }}
  .cover .meta {{ color: #8a939b; font-size: 11px; border-top: 1px solid #d9d9d2; padding-top: 16px; max-width: 320px; margin: 0 auto; }}
  .toc {{ page-break-before: always; }}
  .toc h2 {{ color: #0d6c6b; border-bottom: 2px solid #0d6c6b; padding-bottom: 6px; }}
  .toc ul {{ list-style: none; padding: 0; }}
  .toc li {{ border-bottom: 1px dashed #d9d9d2; }}
  .toc a {{ display: flex; justify-content: space-between; align-items: center;
            padding: 11px 4px; color: #172433; text-decoration: none; }}
  .toc-tag {{ background: #0d6c6b; color: #fff; font-size: 10px; padding: 2px 8px; border-radius: 4px; margin-right: 10px; }}
  .toc-count {{ color: #8a939b; font-size: 11px; }}
  .chapter {{ page-break-before: always; }}
  .ch-tag {{ background: #b08d57; color: #fff; font-size: 11px; padding: 3px 10px; border-radius: 4px; margin-right: 10px; vertical-align: 3px; }}
  .chapter h2 {{ color: #0d6c6b; font-size: 22px; border-bottom: 2px solid #b08d57; padding-bottom: 8px; }}
  .entry {{ margin-top: 26px; }}
  .entry h3 {{ color: #084d50; font-size: 16px; }}
  .entry .body h2 {{ font-size: 14px; border: 0; color: #0d6c6b; margin: 18px 0 6px; }}
  .entry .body h3 {{ font-size: 13px; color: #334454; }}
  .entry .body table {{ width: 100%; border-collapse: collapse; font-size: 11px; margin: 8px 0; }}
  .entry .body th, .entry .body td {{ border: 1px solid #d9d9d2; padding: 6px 8px; text-align: left; }}
  .entry .body th {{ background: #f6f3ed; }}
  .entry .body a {{ color: #0d6c6b; }}
  .back {{ page-break-before: always; text-align: center; padding-top: 120px; color: #627180; }}
  .back h2 {{ color: #0d6c6b; }}
</style>
</head>
<body>
  <section class="cover">
    <div class="brand">SHENYUAN INTERNATIONAL</div>
    <h1>跨境维权法律手册</h1>
    <div class="sub">国际贸易争议 · 债务追收 · 跨境继承 —— 中英双语律师团队</div>
    <div class="meta">
      深远国际律师事务所<br>深远(国际) · 跨境争议解决与家族资产保护<br>
      编制日期：{today}<br><br>
      本文档由已公开发布的法律专栏文章汇编而成，仅供一般信息参考，不构成法律意见。
      境外法律程序通过与当地执业律所合作提供。
    </div>
  </section>

  <section class="toc">
    <h2>目录</h2>
    <ul>{toc}</ul>
  </section>

  {chapters}

  <section class="back">
    <h2>需要评估您的案件？</h2>
    <p>通过官网表单或 AI 咨询助手提交基本信息，<br>我们免费判断时效、证据与可行路径。</p>
    <p style="color:#8a939b;font-size:11px;margin-top:30px">shenyuanlegal.com · 微信 ShenyuanLegal</p>
  </section>
</body>
</html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", action="store_true", help="also render PDF via Playwright")
    args = ap.parse_args()
    articles = load_articles()
    if not articles:
        print("no articles found", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = build_html(articles)
    (OUT_DIR / "handbook.html").write_text(html, encoding="utf-8")
    print(f"handbook.html: {len(articles)} articles -> {OUT_DIR / 'handbook.html'}")
    if args.pdf:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("playwright not installed; skipping PDF", file=sys.stderr)
            return 0
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{(OUT_DIR / 'handbook.html').resolve()}")
            page.pdf(path=str(OUT_DIR / "handbook.pdf"), format="A4",
                     print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            browser.close()
        print(f"handbook.pdf -> {OUT_DIR / 'handbook.pdf'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
