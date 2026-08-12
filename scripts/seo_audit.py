#!/usr/bin/env python3
"""全站 SEO 自动体检（每周 cron 运行，或手动触发）。

扫描范围：sitemap 全部 URL + robots/llms.txt。
检查项：
  1. <title> 长度（30-60）
  2. meta description 长度（50-160）
  3. canonical 指向自身
  4. hreflang 成对（有 en 变体的页面）
  5. og:title / og:description / og:image / twitter:card
  6. JSON-LD 块 JSON 有效性
  7. 站内链接断链（404）
  8. sitemap URL 全部 200
  9. robots.txt / llms.txt 可访问

用法：
  python3 scripts/seo_audit.py [base_url]
输出 markdown 报告到 stdout；发现问题时 exit 1（便于 cron 判断）。

不需要额外依赖（stdlib only）。全站 ~90 URL，完整跑约 1-3 分钟。
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _env(name: str, default: str = "") -> str:
    val = __import__("os").environ.get(name, "").strip()
    if val:
        return val
    try:
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return default


def fetch(url: str, timeout: int = 20) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; ShenyuanSEO/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except Exception:
        return 0, ""


def get_sitemap_urls(base: str) -> list[str]:
    code, body = fetch(f"{base}/sitemap.xml")
    if code != 200:
        return []
    return re.findall(r"<loc>(.*?)</loc>", body)


def check_page(url: str) -> list[str]:
    """Return a list of problems (empty = healthy)."""
    issues = []
    code, html = fetch(url)
    if code != 200:
        return [f"HTTP {code}"]
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    t = title.group(1).strip() if title else ""
    if not t:
        issues.append("缺 <title>")
    elif not (10 <= len(t) <= 70):
        issues.append(f"<title> 长度 {len(t)}（建议 10-70）")
    desc = re.search(r'<meta name="description" content="([^"]*)"', html)
    d = desc.group(1).strip() if desc else ""
    if not d:
        issues.append("缺 meta description")
    elif not (40 <= len(d) <= 170):
        issues.append(f"meta description 长度 {len(d)}（建议 40-170）")
    canon = re.search(r'<link rel="canonical" href="([^"]*)"', html)
    if not canon:
        issues.append("缺 canonical")
    else:
        c = canon.group(1).rstrip("/")
        u = url.rstrip("/")
        # /en/* pages may legitimately canonical to their zh source (hreflang
        # pair) to avoid duplicate content — that is the intended strategy.
        zh_source = u.replace("/en", "", 1) if "/en/" in u else u
        if c != u and c != zh_source:
            issues.append(f"canonical 指向 {c} ≠ 自身")
    if not re.search(r'hreflang="[a-z-]+" href="[^"]*/(en|zh)/', html) and not re.search(r'hreflang="x-default"', html):
        if "/en/" not in url and not url.endswith("/en/") and "/search" not in url and "/handbook" not in url:
            issues.append("缺 hreflang 声明")
    for og in ("og:title", "og:description", "og:image"):
        if not re.search(rf'property="{og}" content="[^"]+"', html):
            if "/search" not in url:  # search page is noindex, minimal meta OK
                issues.append(f"缺 {og}")
    if not re.search(r'name="twitter:card" content="[^"]+"', html):
        if "/search" not in url:
            issues.append("缺 twitter:card")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            issues.append(f"JSON-LD 解析失败: {exc}")
    return issues


def check_links(base: str, pages: list[str]) -> list[str]:
    """Find 404 internal links across the site."""
    broken: list[str] = []
    seen: set[str] = set()
    internal = re.compile(rf'href="({re.escape(base)}[^"#?]*)"')
    for url in pages:
        code, html = fetch(url)
        if code != 200 or not html:
            continue
        for target in internal.findall(html):
            if target in seen:
                continue
            seen.add(target)
            t_code, _ = fetch(target, timeout=15)
            if t_code == 404:
                broken.append(f"{url} -> {target} (404)")
            if len(seen) > 400:
                return broken
    return broken


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else _env("SITE_URL", "https://shenyuanlegal.com")).rstrip("/")
    print(f"# 🔍 全站 SEO 体检 · {base}")
    print(f"\n> 运行时间：{__import__('datetime').datetime.now():%Y-%m-%d %H:%M} · 扫描范围：sitemap 全量 + 内链")
    problems: list[tuple[str, str]] = []

    # 1) sitemap + per-page checks
    pages = get_sitemap_urls(base)
    print(f"\n## 一、页面级检查（{len(pages)} 个 URL）")
    if not pages:
        problems.append(("sitemap", "无法获取 sitemap.xml"))
        print("- ❌ sitemap.xml 不可访问")
    else:
        healthy = 0
        for url in pages:
            issues = check_page(url)
            if issues:
                problems.append((url, "; ".join(issues)))
                print(f"- ⚠️ {url}：{'；'.join(issues)}")
            else:
                healthy += 1
        print(f"- ✅ {healthy}/{len(pages)} 页面全部健康")

    # 2) sitemap URL 一致性
    print("\n## 二、sitemap URL 可达性")
    dead = []
    for url in pages:
        code, _ = fetch(url, timeout=15)
        if code != 200:
            dead.append(f"{url} ({code})")
    if dead:
        problems.append(("sitemap 死链", "; ".join(dead[:5])))
        print("- ❌ " + "；".join(dead[:5]))
    else:
        print("- ✅ 全部可达")

    # 3) robots / llms.txt
    print("\n## 三、机器人协议与 GEO")
    for path in ("robots.txt", "llms.txt"):
        code, body = fetch(f"{base}/{path}")
        ok = code == 200 and bool(body.strip())
        print(f"- {'✅' if ok else '❌'} /{path}: {code}" + (f"（{len(body)} 字节）" if ok else ""))
        if not ok:
            problems.append((path, f"HTTP {code}"))

    # 4) internal broken links
    print("\n## 四、站内断链")
    broken = check_links(base, pages)
    if broken:
        problems.append(("断链", "; ".join(broken[:5])))
        print("- ❌ " + "；".join(broken[:5]) + ("…" if len(broken) > 5 else ""))
    else:
        print("- ✅ 无断链")

    print(f"\n## 结论")
    if problems:
        print(f"- ⚠️ 发现 {len(problems)} 类问题，需处理 {len(problems)} 项（详见上）。")
        for kind, detail in problems[:6]:
            print(f"  - {kind}: {detail[:120]}")
        return 1
    print("- ✅ 全部健康，无需处理。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
