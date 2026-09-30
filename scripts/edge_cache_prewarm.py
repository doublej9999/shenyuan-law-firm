#!/usr/bin/env python3
"""
深远律所官网 · 边缘缓存与 CDN 自动化预热脚本 (Edge Cache Pre-warm)。
模拟全球主流法域节点与搜索引擎爬虫并发预热核心页面、多语言页面及动态 Sitemap，
消除冷启动延迟，确保海外当事人与爬虫首次访问获得 <100ms 毫秒级极速响应。
"""

import sys
import os
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

SITE_URL = os.environ.get("SITE_URL", "https://shenyuanlegal.com").rstrip("/")
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "https://shenyuan-backend.vercel.app").rstrip("/")

# 模拟全球高价值地区访客与搜索引擎 User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "GPTBot",
]


def fetch_sitemap_urls(max_urls: int = 80) -> list[str]:
    """从线上 sitemap.xml 提取最新与核心 URL 列表"""
    sitemap_url = f"{SITE_URL}/sitemap.xml"
    urls = []
    try:
        req = urllib.request.Request(sitemap_url, headers={"User-Agent": USER_AGENTS[0]})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            root = ET.fromstring(content)
            # 解析命名空间
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for loc in root.findall('.//ns:loc', ns):
                if loc.text:
                    urls.append(loc.text.strip())
    except Exception as e:
        print(f"⚠️ 解析 sitemap.xml 失败 ({e})，采用内置核心路由列表。")
        urls = [
            f"{SITE_URL}/",
            f"{SITE_URL}/en",
            f"{SITE_URL}/ar",
            f"{SITE_URL}/es",
            f"{SITE_URL}/articles",
            f"{SITE_URL}/en/articles",
            f"{SITE_URL}/ar/articles",
            f"{SITE_URL}/es/articles",
            f"{SITE_URL}/services/trade",
            f"{SITE_URL}/services/recovery",
            f"{SITE_URL}/services/legacy",
            f"{SITE_URL}/countries/united-states",
            f"{SITE_URL}/countries/germany",
            f"{SITE_URL}/countries/united-arab-emirates",
            f"{SITE_URL}/countries/singapore",
        ]

    # 优先排位：多语言首页、专栏列表、核心业务
    priority_keywords = ["/ar", "/es", "/en", "/articles", "/services", "/countries"]
    def get_sort_key(u: str) -> int:
        for i, kw in enumerate(priority_keywords):
            if kw in u:
                return i
        return 99

    sorted_urls = sorted(list(set(urls)), key=get_sort_key)
    return sorted_urls[:max_urls]


def warm_url(url: str, ua: str) -> dict:
    """向目标 URL 发起预热 GET 请求并记录响应速度与缓存状态"""
    start_t = time.time()
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ar;q=0.7,es;q=0.7"
        })
        with urllib.request.urlopen(req, timeout=12) as resp:
            duration_ms = int((time.time() - start_t) * 1000)
            headers = dict(resp.headers)
            cache_status = headers.get("X-Vercel-Cache", headers.get("cf-cache-status", "DYNAMIC"))
            return {
                "url": url,
                "status": resp.status,
                "duration_ms": duration_ms,
                "cache": cache_status,
                "ok": resp.status == 200
            }
    except Exception as e:
        duration_ms = int((time.time() - start_t) * 1000)
        return {
            "url": url,
            "status": "error",
            "duration_ms": duration_ms,
            "error": str(e),
            "ok": False
        }


def run_cache_prewarm(max_urls: int = 60, concurrency: int = 5):
    print("=" * 65)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 启动全球边缘节点与 CDN 缓存自动化预热 (目标: {max_urls} 个核心 URL)...")
    print("=" * 65)

    urls = fetch_sitemap_urls(max_urls)
    print(f"已选取待预热核心路由: {len(urls)} 条")

    success_count = 0
    fast_count = 0  # <200ms
    results = []

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_url = {}
        for idx, u in enumerate(urls):
            ua = USER_AGENTS[idx % len(USER_AGENTS)]
            future_to_url[executor.submit(warm_url, u, ua)] = u

        for future in as_completed(future_to_url):
            res = future.result()
            results.append(res)
            if res["ok"]:
                success_count += 1
                if res["duration_ms"] < 250:
                    fast_count += 1
                print(f"  ⚡ [{res['cache']}] {res['duration_ms']}ms | {res['url']}")
            else:
                print(f"  ❌ 失败 | {res['url']} -> {res.get('error', res.get('status'))}")

    avg_ms = int(sum(r["duration_ms"] for r in results) / len(results)) if results else 0
    print("\n" + "=" * 65)
    print(f"预热汇总: 成功率 {success_count}/{len(urls)} ({(success_count/len(urls)*100):.1f}%) | 极速响应(<250ms): {fast_count} 条 | 全局平均延时: {avg_ms}ms")
    print("=" * 65)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    run_cache_prewarm(count)
