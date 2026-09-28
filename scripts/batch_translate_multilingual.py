#!/usr/bin/env python3
"""Batch multilingual article generator and SEO indexer for Shenyuan International.

Selects high-value articles matching Middle Eastern (Arabic) and Latin American
(Spanish) commercial jurisdictions, translates them using DeepSeek via LLM API,
stores them into `translations[lang]` via CMS API, and notifies search engines.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent

# 后端配置
BACKEND_BASE = os.environ.get("BACKEND_BASE", "https://shenyuan-backend.vercel.app").rstrip("/")

def get_admin_token() -> str:
    token = os.environ.get("ADMIN_TOKEN", "").strip()
    if token:
        return token
    for p in ["/root/.hermes/.env", "/root/.env", str(ROOT / ".env")]:
        if os.path.exists(p):
            try:
                for line in open(p, encoding="utf-8"):
                    if "ADMIN_TOKEN=" in line:
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
    return ""

def get_llm_api_key() -> str:
    key = os.environ.get("LLM_API_KEY", "").strip() or os.environ.get("HERMES_CUSTOM_CPA_927900_XYZ_API_KEY", "").strip()
    if key:
        return key
    for p in ["/root/.hermes/.env", "/root/.env", str(ROOT / ".env")]:
        if os.path.exists(p):
            try:
                for line in open(p, encoding="utf-8"):
                    if "HERMES_CUSTOM_CPA_927900_XYZ_API_KEY=" in line:
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
    return ""

LLM_API_BASE = os.environ.get("LLM_API_BASE", "https://cpa.927900.xyz/v1").rstrip("/")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-v4.1-flash").strip()
ADMIN_TOKEN = get_admin_token()
LLM_KEY = get_llm_api_key()


def api_request(path: str, data: Optional[dict] = None, method: str = "GET") -> dict:
    url = f"{BACKEND_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "User-Agent": "Mozilla/5.0 (compatible; ShenyuanMultilingualPipeline/1.0)",
    }
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def translate_with_llm(article: dict, target_lang: str) -> Optional[dict]:
    """Call DeepSeek to accurately translate and localize the legal article."""
    if not LLM_KEY:
        print("  [ERROR] No LLM_KEY detected. Aborting translation.")
        return None

    lang_specs = {
        "ar": {
            "name": "现代标准阿拉伯语 (Modern Standard Arabic)",
            "context": "适用于阿联酋（迪拜国际金融中心 DIFC 法院、ADGM）及沙特阿拉伯商事法庭的正式涉外司法实务。要求法言法语严谨、术语准确，保留原有的 Markdown 表格和段落结构。",
            "cta": "[استشارة قانونية مجانية مع فريق شينيوان الدولي →](/#intake)"
        },
        "es": {
            "name": "标准司法西班牙语 (Español Jurídico Internacional)",
            "context": "适用于墨西哥近岸制造投资合规及拉美主要贸易国（智利、秘鲁、哥伦比亚、阿根廷）国际贸易货款清收与涉外诉讼。要求专业严谨，保留原有的 Markdown 表格和结构。",
            "cta": "[Consulta legal gratuita con Shenyuan International →](/#intake)"
        }
    }

    spec = lang_specs.get(target_lang, lang_specs["es"])
    system_prompt = f"""你是一名精通中国涉外经贸法以及目标法域司法的资深双语大律师。
你的任务是将提供的中国涉外法律实务指南精准、专业、地道地本地化翻译为{spec['name']}。
法域背景与语言规范：{spec['context']}

严格遵守以下输出要求：
1. 必须输出纯 JSON 格式，包含三个键：
   - "title": 翻译后的专业文章主标题
   - "description": 翻译后的简明摘要（100-160字符，用于搜索引擎结果展示）
   - "body": 翻译后的完整 Markdown 正文。必须完整保留原有的二级/三级标题结构、Markdown 格式对比表格（| col | col |）、列表与免责声明，文末附加咨询指引：{spec['cta']}
2. 不要输出任何额外的解释或开场白，直接输出包含 JSON 的响应。"""

    user_prompt = f"""待翻译文章标题：{article.get('title_zh')}
文章业务领域：{article.get('business')}
中文摘要：{article.get('description_zh')}
中文正文参考：
{article.get('body_zh', '')[:3500]}
"""

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
    }

    models_to_try = [LLM_MODEL, "deepseek-v4-flash"]
    for m in models_to_try:
        payload["model"] = m
        try:
            req = urllib.request.Request(
                f"{LLM_API_BASE}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {LLM_KEY}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = re.sub(r"^```[a-z]*\n?", "", content)
                    content = re.sub(r"\n?```$", "", content).strip()
                parsed = json.loads(content)
                if parsed.get("title") and parsed.get("body"):
                    return parsed
        except Exception as e:
            print(f"  [WARN] LLM model {m} attempt failed: {e}")
            time.sleep(2)

    return None


def run_batch_translation(target_lang: str, limit: int = 15):
    """Filter candidate articles and translate them into target_lang."""
    print(f"\n=======================================================")
    print(f"  Starting Batch Translation for: [{target_lang.upper()}] (Target: {limit} articles)")
    print(f"=======================================================")

    articles = api_request("/admin/api/content?status=published")
    print(f"Total published articles retrieved from CMS: {len(articles)}")

    # 针对性筛选规则
    candidates = []
    if target_lang == "ar":
        # 中东、阿联酋、海运、仲裁、波斯湾、离岸
        ar_keywords = ["海运", "货损", "提单", "苏伊士", "中东", "阿联酋", "迪拜", "沙特", "仲裁", "纽约公约", "跨境执行", "信用证", "贸易", "争议"]
        for a in articles:
            trans = a.get("translations") or {}
            if trans.get("ar") and trans["ar"].get("title"):
                continue  # 已存在阿语版本
            full_text = f"{a.get('title_zh', '')} {a.get('body_zh', '')}"
            if any(k in full_text for k in ar_keywords):
                candidates.append(a)
    elif target_lang == "es":
        # 墨西哥、拉美、外贸欠款、买家拖欠、货款追收、合同违约
        es_keywords = ["外贸", "拖欠", "货款", "追收", "买家", "违约", "合同", "清收", "破产", "执行", "信用证", "诉讼", "证据"]
        for a in articles:
            trans = a.get("translations") or {}
            if trans.get("es") and trans["es"].get("title"):
                continue  # 已存在西语版本
            full_text = f"{a.get('title_zh', '')} {a.get('body_zh', '')}"
            if any(k in full_text for k in es_keywords):
                candidates.append(a)

    print(f"Matching candidate articles for [{target_lang.upper()}]: {len(candidates)}")
    selected = candidates[:limit]

    success_count = 0
    for idx, art in enumerate(selected, 1):
        art_id = art["id"]
        title_zh = art.get("title_zh", "")
        slug = art.get("slug", "")
        print(f"\n[{idx}/{len(selected)}] Processing #{art_id}: {title_zh[:36]}... ({slug})")

        translated = translate_with_llm(art, target_lang)
        if not translated:
            print(f"  -> [FAIL] Translation generation failed for #{art_id}")
            continue

        # 更新文章 translations
        existing_trans = art.get("translations") or {}
        existing_trans[target_lang] = {
            "title": translated["title"],
            "description": translated.get("description", art.get("description_zh", "")),
            "body": translated["body"],
        }
        art["translations"] = existing_trans

        try:
            # PUT 回写后端
            updated = api_request(f"/admin/api/content/{art_id}", data=art, method="PUT")
            print(f"  -> [OK] Successfully saved translations.{target_lang} to database!")

            # 触发搜索引擎收录主动报送
            try:
                indexing_res = api_request(f"/admin/api/content/{art_id}/notify-indexing", method="POST")
                print(f"  -> [SEO] Search engine indexing pushed: {indexing_res.get('status')}")
            except Exception as se_err:
                print(f"  -> [SEO] Indexing notify skipped: {se_err}")

            success_count += 1
        except Exception as put_err:
            print(f"  -> [ERROR] Failed to save #{art_id}: {put_err}")

        # 友好的速率间隔
        time.sleep(2)

    print(f"\n=======================================================")
    print(f"  Finished [{target_lang.upper()}]: {success_count}/{len(selected)} articles updated!")
    print(f"=======================================================\n")


if __name__ == "__main__":
    lang_arg = sys.argv[1] if len(sys.argv) > 1 else "both"
    count_arg = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    if lang_arg in ("ar", "both"):
        run_batch_translation("ar", limit=count_arg)
    if lang_arg in ("es", "both"):
        run_batch_translation("es", limit=count_arg)
