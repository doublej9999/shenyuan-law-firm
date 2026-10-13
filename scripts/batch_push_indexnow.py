#!/usr/bin/env python3
"""
scripts/batch_push_indexnow.py

全量/增量批量向 IndexNow (Bing / Copilot / ChatGPT Search / Yandex) 报送全站四语优质页面，
加速爬虫配额分配与索引建立。
"""

import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

INDEXNOW_KEY = "4b8f2d93e1074a3f890259bfae6741c0"
INDEXNOW_KEY_LOCATION = "https://shenyuanlegal.com/4b8f2d93e1074a3f890259bfae6741c0.txt"
SITEMAP_URL = "https://shenyuanlegal.com/sitemap.xml"


def fetch_sitemap_urls():
    req = urllib.request.Request(SITEMAP_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        xml_data = resp.read()
    root = ET.fromstring(xml_data)
    urls = [elem.text for elem in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if elem.text]
    return urls


def push_batch(urls: list[str]):
    # IndexNow 单次最大支持 10,000 条
    chunk_size = 250
    print(f"[*] 准备向 IndexNow 推送共计 {len(urls)} 个合法页面...")
    for i in range(0, len(urls), chunk_size):
        chunk = urls[i : i + chunk_size]
        payload = {
            "host": "shenyuanlegal.com",
            "key": INDEXNOW_KEY,
            "keyLocation": INDEXNOW_KEY_LOCATION,
            "urlList": chunk,
        }
        try:
            req = urllib.request.Request(
                "https://api.indexnow.org/indexnow",
                headers={"Content-Type": "application/json; charset=utf-8"},
                data=json.dumps(payload).encode("utf-8"),
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                print(f" -> Batch {i // chunk_size + 1} ({len(chunk)} urls): HTTP {resp.status} OK")
        except urllib.error.HTTPError as e:
            print(f" -> Batch {i // chunk_size + 1} Error: HTTP {e.code} - {e.read().decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f" -> Batch {i // chunk_size + 1} Failed: {e}")


if __name__ == "__main__":
    try:
        urls = fetch_sitemap_urls()
        if urls:
            push_batch(urls)
            print("[✓] 全量 IndexNow 推流完成，已即时广播至 Bing, Yandex, Copilot, ChatGPT Search 网络！")
        else:
            print("[!] 未获取到 Sitemap URL")
    except Exception as e:
        print(f"[!] 脚本执行失败: {e}")
