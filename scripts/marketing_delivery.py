#!/usr/bin/env python3
"""营销素材·每周分发（no_agent 版）——零 LLM 依赖，杜绝 provider 524。

素材由站点后端规则引擎生成（/admin/api/marketing/generate），本脚本只负责：
  1. 找本周新文章（frontmatter date 近 7 天）
  2. 逐篇调生产接口取素材 JSON
  3. 整理成 markdown 交付报告（stdout）

用法：
  python3 scripts/marketing_delivery.py [--days 7] [--base https://shenyuanlegal.com]
输出：markdown 报告；无新文章时输出「本周无新发布文章，素材包跳过。」（cron 静默投递判断）。

环境：ADMIN_TOKEN 从仓库 .env 读取（脚本不打印 token）。
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "content" / "articles"

PLATFORM_SECTIONS = [
    ("公众号（周一）", "mp"),
    ("X / Twitter（周二）", "x"),
    ("小红书（周三）", "xiaohongshu"),
    ("Facebook（周四）", "facebook"),
    ("TikTok（周五）", "tiktok"),
    ("朋友圈+社群（周日）", "moments"),
]


def _env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if val:
        return val
    try:
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def _recent_articles(days: int) -> list[dict]:
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days)).date()
    out = []
    for idx in sorted(ARTICLES.glob("*/index.md")):
        text = idx.read_text(encoding="utf-8")
        meta = {}
        import re
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
        try:
            d = datetime.strptime(meta.get("date", ""), "%Y-%m-%d").date()
        except ValueError:
            continue
        if d >= cutoff:
            out.append({"slug": meta.get("slug", idx.parent.name),
                        "title": meta.get("title_zh", ""), "date": str(d)})
    return out


def _fetch_bundle(base: str, slug: str) -> dict:
    token = _env("ADMIN_TOKEN")
    url = f"{base}/admin/api/marketing/generate?slug={slug}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (compatible; ShenyuanMarketing/1.0)",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _render_bundle(article: dict, bundle: dict, base: str) -> str:
    lines = [f"## 📄 {article['title']}",
             f"- 链接：{base}/articles/{article['slug']}",
             f"- 发布日期：{article['date']}"]
    for label, key in PLATFORM_SECTIONS:
        content = bundle.get(key) or bundle.get(f"{key}_content") or ""
        if isinstance(content, dict):
            content = json.dumps(content, ensure_ascii=False, indent=2)
        if content:
            lines.append(f"**{label}**：")
            lines.append("```text")
            lines.append(str(content))
            lines.append("```")
    # UTM links
    utm = bundle.get("utm") or bundle.get("utm_links") or {}
    if isinstance(utm, dict) and utm:
        lines.append("**UTM 链接**：")
        for k, v in utm.items():
            lines.append(f"- {k}: {v}")
    return "\n".join(lines)


def main() -> int:
    days = 7
    base = "https://shenyuanlegal.com"
    args = sys.argv[1:]
    if "--days" in args:
        days = int(args[args.index("--days") + 1])
    if "--base" in args:
        base = args[args.index("--base") + 1].rstrip("/")
    articles = _recent_articles(days)
    if not articles:
        print("本周无新发布文章，素材包跳过。")
        return 0
    out = [f"# 📣 本周营销素材包（{datetime.now():%Y-%m-%d}）"]
    for a in articles:
        try:
            bundle = _fetch_bundle(base, a["slug"])
        except Exception as exc:
            print(f"❌ {a['title']} 素材获取失败：{exc}")
            continue
        out.append(_render_bundle(a, bundle, base))
    out.append("")
    out.append("素材已按每周排期（周一公众号/周二X/周三小红书/周四Facebook/周五TikTok/周日朋友圈）整理，可直接复制使用。")
    print("\n\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
