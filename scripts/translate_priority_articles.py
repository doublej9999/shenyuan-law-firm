#!/usr/bin/env python3
"""Translate priority and anomalous articles to Arabic and Spanish and save to database."""
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.batch_translate_multilingual import (
    api_request,
    translate_with_llm,
)

TARGET_IDS = [105, 106, 104, 96, 95, 90, 85]

def run():
    print("Fetching published articles...")
    articles = api_request("/admin/api/content?status=published")
    art_map = {a["id"]: a for a in articles}

    for art_id in TARGET_IDS:
        art = art_map.get(art_id)
        if not art:
            print(f"Article #{art_id} not found!")
            continue

        slug = art.get("slug")
        title_zh = art.get("title_zh", "")
        print(f"\n=======================================================")
        print(f"Processing #{art_id}: {slug} ({title_zh[:30]}...)")
        print(f"=======================================================")

        trans = art.get("translations") or {}

        # 1. Check Arabic
        ar_cur = trans.get("ar") or {}
        ar_title = ar_cur.get("title", "")
        needs_ar = (not ar_title) or (ar_title == "...") or (len(ar_title.strip()) < 4) or ar_cur.get("body", "").startswith("# دليل الممارسة القانونية:")
        if needs_ar:
            print(f"  -> Translating to Arabic (current title: {ar_title!r})...")
            t0 = time.time()
            ar_res = translate_with_llm(art, "ar")
            if ar_res and ar_res.get("title") and ar_res.get("title") != "..." and ar_res.get("body"):
                trans["ar"] = ar_res
                print(f"  -> [OK] AR translated in {time.time()-t0:.1f}s: {ar_res['title'][:40]}...")
            else:
                print("  -> [FAIL] AR translation failed or invalid")
        else:
            print(f"  -> [SKIP] Arabic already valid: {ar_title[:40]}...")

        # 2. Check Spanish
        es_cur = trans.get("es") or {}
        es_title = es_cur.get("title", "")
        needs_es = (not es_title) or (es_title == "...") or (len(es_title.strip()) < 4) or es_cur.get("body", "").startswith("# Guía Jurídica Práctica:")
        if needs_es:
            print(f"  -> Translating to Spanish (current title: {es_title!r})...")
            t0 = time.time()
            es_res = translate_with_llm(art, "es")
            if es_res and es_res.get("title") and es_res.get("title") != "..." and es_res.get("body"):
                trans["es"] = es_res
                print(f"  -> [OK] ES translated in {time.time()-t0:.1f}s: {es_res['title'][:40]}...")
            else:
                print("  -> [FAIL] ES translation failed or invalid")
        else:
            print(f"  -> [SKIP] Spanish already valid: {es_title[:40]}...")

        art["translations"] = trans
        try:
            api_request(f"/admin/api/content/{art_id}", data=art, method="PUT")
            print(f"  -> [SAVED] Article #{art_id} successfully updated in database!")
            # Trigger IndexNow
            try:
                api_request(f"/admin/api/content/{art_id}/notify-indexing", method="POST")
            except Exception:
                pass
        except Exception as e:
            print(f"  -> [ERROR] Failed to save article #{art_id}: {e}")

        time.sleep(1)

    print("\nPriority articles translation completed!")

if __name__ == "__main__":
    run()
