#!/usr/bin/env python3
"""Identify fallback/stub translations in the database and re-translate them with LLM."""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.batch_translate_multilingual import (
    api_request,
    translate_with_llm,
    BACKEND_BASE,
    ADMIN_TOKEN,
)

def clean_and_retranslate(target_lang: str):
    print(f"\n=======================================================")
    print(f"  Scanning for Fallback Translations [{target_lang.upper()}]")
    print(f"=======================================================")
    
    articles = api_request("/admin/api/content?status=published")
    print(f"Total published articles: {len(articles)}")
    
    fallback_articles = []
    for a in articles:
        trans = a.get("translations") or {}
        lang_data = trans.get(target_lang)
        if not lang_data:
            continue
        body = lang_data.get("body", "")
        # Detect fallback signature
        if (target_lang == "ar" and body.startswith("# دليل الممارسة القانونية:")) or \
           (target_lang == "es" and body.startswith("# Guía Jurídica Práctica:")):
            fallback_articles.append(a)

    print(f"Found {len(fallback_articles)} articles with fallback templates in [{target_lang.upper()}]")
    
    fixed_count = 0
    for idx, art in enumerate(fallback_articles, 1):
        art_id = art["id"]
        title_zh = art.get("title_zh", "")
        slug = art.get("slug", "")
        print(f"\n[{idx}/{len(fallback_articles)}] Re-translating #{art_id}: {title_zh[:32]}... ({slug})")
        
        translated = translate_with_llm(art, target_lang)
        if not translated or not translated.get("title") or not translated.get("body"):
            print(f"  -> [SKIP] LLM translation returned empty for #{art_id}")
            continue
            
        # Check that it's not the fallback again
        if (target_lang == "ar" and translated["body"].startswith("# دليل الممارسة القانونية:")) or \
           (target_lang == "es" and translated["body"].startswith("# Guía Jurídica Práctica:")):
            print(f"  -> [WARN] LLM returned fallback again. Skipping.")
            continue
            
        trans = art.get("translations") or {}
        trans[target_lang] = translated
        art["translations"] = trans
        
        try:
            res = api_request(f"/admin/api/content/{art_id}", data=art, method="PUT")
            print(f"  -> [OK] Successfully saved genuine {target_lang} translation to database!")
            fixed_count += 1
        except Exception as e:
            print(f"  -> [ERROR] Failed to save #{art_id}: {e}")
            
        time.sleep(1)

    print(f"\n=======================================================")
    print(f"  Finished [{target_lang.upper()}]: Fixed {fixed_count}/{len(fallback_articles)} articles!")
    print(f"=======================================================\n")

if __name__ == "__main__":
    clean_and_retranslate("es")
    clean_and_retranslate("ar")
