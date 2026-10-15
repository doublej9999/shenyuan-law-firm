#!/usr/bin/env python3
"""
scripts/batch_google_indexing_push.py

每日批量调用 Google Indexing API（打满每日 ~200 次配额），
优先将未收录的阿/西/英/中四语深度文章和核心落地页推入 Googlebot VIP 极速抓取队列。
"""

import json
import logging
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API_URL = "https://indexing.googleapis.com/v3/urlNotifications:publish"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("google_indexing_batch")

STATE_FILE = ROOT / "data" / "google_indexing_history.json"


def _get_token() -> str | None:
    creds_path = ROOT / ".secrets" / "gsc.json"
    if not creds_path.exists():
        logger.error(f"GSC 凭证不存在: {creds_path}")
        return None
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(
            str(creds_path), scopes=["https://www.googleapis.com/auth/indexing"]
        )
        creds.refresh(Request())
        return creds.token
    except Exception as e:
        logger.error(f"获取 Google OAuth Token 失败: {e}")
        return None


def fetch_sitemap_urls() -> list[str]:
    sitemap_url = "https://shenyuanlegal.com/sitemap.xml"
    req = urllib.request.Request(sitemap_url, headers={"User-Agent": "Mozilla/5.0 (GoogleIndexingPusher/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            root = ET.fromstring(resp.read())
            urls = [elem.text for elem in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if elem.text]
            return urls
    except Exception as e:
        logger.error(f"读取 sitemap.xml 失败: {e}")
        return []


def load_history() -> dict[str, float]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_history(history: dict[str, float]):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def prioritize_urls(urls: list[str], history: dict[str, float], limit: int = 180) -> list[str]:
    now = time.time()
    # 过滤出 7 天内未提交过的 URL
    eligible = []
    for u in urls:
        last_pushed = history.get(u, 0)
        if now - last_pushed > 7 * 86400:
            eligible.append((u, last_pushed))

    # 排序策略：
    # 1. 优先从没提交过的 (last_pushed == 0)
    # 2. 语种优先级：ar (阿拉伯语) / es (西班牙语) / en (英语) > zh (中文，中文收录率最高)
    def sort_key(item):
        u, last_pushed = item
        never_pushed = 0 if last_pushed == 0 else 1
        lang_weight = 4
        if "/ar/" in u:
            lang_weight = 1
        elif "/es/" in u:
            lang_weight = 2
        elif "/en/" in u:
            lang_weight = 3
        return (never_pushed, lang_weight, last_pushed)

    eligible.sort(key=sort_key)
    return [u for u, _ in eligible[:limit]]


def push_url(token: str, url: str) -> bool:
    payload = json.dumps({"url": url, "type": "URL_UPDATED"}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status in (200, 204)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if e.code == 429:
            logger.warning("Google Indexing API 配额已达今日上限 (HTTP 429)")
        else:
            logger.warning(f"提交失败 {url} [HTTP {e.code}]: {body[:200]}")
        return False
    except Exception as e:
        logger.warning(f"提交网络异常 {url}: {e}")
        return False


def main():
    max_batch = 180  # 留 20 条余量给当日 auto_content_pipeline
    if len(sys.argv) > 1:
        try:
            max_batch = int(sys.argv[1])
        except ValueError:
            pass

    logger.info(f"开始执行 Google Indexing API 批量推流 (上限: {max_batch} 篇)...")
    token = _get_token()
    if not token:
        logger.error("未获取到认证 Token，退出")
        sys.exit(1)

    all_urls = fetch_sitemap_urls()
    logger.info(f"从 Sitemap 发现全站 URL 总数: {len(all_urls)}")
    if not all_urls:
        logger.error("未发现任何 URL，退出")
        sys.exit(1)

    history = load_history()
    to_push = prioritize_urls(all_urls, history, limit=max_batch)
    logger.info(f"本轮筛选待提速推进的 URL 数量: {len(to_push)}")

    success_count = 0
    now = time.time()
    for idx, u in enumerate(to_push, 1):
        ok = push_url(token, u)
        if ok:
            history[u] = now
            success_count += 1
            logger.info(f"[{idx}/{len(to_push)}] ✅ 成功提交: {u}")
        else:
            logger.warning(f"[{idx}/{len(to_push)}] ❌ 提交中断: {u}")
            # 如果遇到 429 额度打满，则安全终止本轮
            break
        # 适当休眠 0.1 秒，符合 Google 速率规范
        time.sleep(0.1)

    save_history(history)
    logger.info(f"Google Indexing API 批量推流完成！成功: {success_count}/{len(to_push)}")


if __name__ == "__main__":
    main()
