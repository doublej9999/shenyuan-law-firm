#!/usr/bin/env python3
"""
深远律所官网 · 每日增量多语言补译与四语对齐自动化任务。
每日自动扫描生产库中尚未翻译阿语 (ar) 或西语 (es) 的存量文章，按配置数量平稳翻译、回写数据库并推送 IndexNow。
"""

import sys
import os
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.batch_translate_multilingual import (
    translate_with_llm,
    api_request,
)


def run_daily_backfill(batch_size: int = 3):
    print("=" * 60)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 启动存量长文每日增量多语言补齐任务 (每语种上限: {batch_size} 篇)...")
    print("=" * 60)

    articles = api_request("/admin/api/content?status=published")
    print(f"线上总发布文章数: {len(articles)}")

    for lang in ["ar", "es"]:
        lang_name = "阿拉伯语 (ar)" if lang == "ar" else "西班牙语 (es)"
        print(f"\n>>> 正在检索缺少【{lang_name}】的存量文章...")
        
        candidates = []
        for a in articles:
            trans = a.get("translations") or {}
            # 缺乏该语言，或该语言仅是简陋占位
            if lang not in trans or not trans[lang].get("body") or trans[lang].get("title") == "...":
                candidates.append(a)

        print(f"待补齐【{lang_name}】文章数: {len(candidates)}")
        selected = candidates[:batch_size]

        if not selected:
            print(f"✅ 【{lang_name}】全库文章已全部对齐，无需补译。")
            continue

        success_count = 0
        for idx, art in enumerate(selected, 1):
            art_id = art["id"]
            slug = art.get("slug", "")
            title_zh = art.get("title_zh", "")
            print(f"\n[{idx}/{len(selected)}] 正在补译 #{art_id}: 《{title_zh[:32]}...》 -> {lang}")

            translated = translate_with_llm(art, lang)
            if not translated:
                print(f"  ❌ #{art_id} 翻译失败，跳过。")
                continue

            existing_trans = art.get("translations") or {}
            existing_trans[lang] = {
                "title": translated["title"],
                "description": translated.get("description", art.get("description_zh", "")),
                "body": translated["body"],
            }
            art["translations"] = existing_trans

            try:
                # 回写后端
                api_request(f"/admin/api/content/{art_id}", data=art, method="PUT")
                print(f"  ✅ 成功保存 #{art_id} translations.{lang} 入库！")

                # 推送 IndexNow
                try:
                    res = api_request(f"/admin/api/content/{art_id}/notify-indexing", method="POST")
                    print(f"  🚀 搜索引擎实时报送成功: {res.get('status')}")
                except Exception as se_err:
                    print(f"  ⚠️ 搜索引擎报送跳过: {se_err}")

                success_count += 1
            except Exception as put_err:
                print(f"  ❌ 回写文章 #{art_id} 失败: {put_err}")

            time.sleep(2)

        print(f"\n--- 【{lang_name}】本轮补译完毕：成功更新 {success_count}/{len(selected)} 篇 ---")

    print("\n" + "=" * 60)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 每日增量多语言补齐任务顺利完成。")
    print("=" * 60)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_daily_backfill(count)
