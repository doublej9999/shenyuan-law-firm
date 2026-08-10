#!/usr/bin/env python3
"""Generate docs/keyword-research-v1.md — 300-keyword V1 list.

Sources:
- docs/article-manifest.csv (150 planned articles -> L2/L3 keywords)
- COUNTRIES slugs + name_zh from app/main.py (country intent keywords)
- Pattern-based expansion per business line (contract/execute/limitation etc.)

Output: structured markdown, grouped TRADE / RECOVERY / LEGACY x intent
(I=informational, C=commercial, T=transactional) x zh/en.
"""

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "docs" / "article-manifest.csv"
OUT = ROOT / "docs" / "keyword-research-v1.md"
TARGET = 300

INTENT_LABEL = {"I": "信息型", "C": "商业型", "T": "交易型"}
BUSINESS_ZH = {"trade": "国际贸易争议", "recovery": "诉讼与债务追收", "legacy": "继承与家族资产"}

# Pattern keywords per business line (zh + en), multiplied by country names.
PATTERNS = {
    "trade": [
        ("海外客户拖欠货款怎么办", "overseas buyer non-payment"),
        ("跨境合同违约赔偿", "cross-border contract breach damages"),
        ("外贸收款追讨", "export payment recovery"),
        ("信用证拒付维权", "letter of credit dishonor"),
        ("国际仲裁申请", "international arbitration claim"),
    ],
    "recovery": [
        ("债务追收律师", "debt recovery lawyer"),
        ("判决执行", "judgment enforcement"),
        ("仲裁裁决承认执行", "award recognition and enforcement"),
        ("债务人资产调查", "debtor asset investigation"),
        ("诉讼时效", "statute of limitations"),
    ],
    "legacy": [
        ("跨境继承", "cross-border inheritance"),
        ("海外房产继承", "inheriting overseas property"),
        ("遗嘱效力", "will validity"),
        ("遗产税", "inheritance tax"),
        ("Probate 遗嘱认证", "probate"),
    ],
}

COUNTRIES_ZH = [
    "美国", "加拿大", "澳大利亚", "新加坡", "英国", "香港", "德国", "日本",
    "阿联酋", "新西兰", "马来西亚", "法国", "瑞士", "韩国", "泰国", "越南",
    "荷兰", "意大利", "西班牙", "巴西", "印度", "爱尔兰",
]
COUNTRIES_EN = [
    "United States", "Canada", "Australia", "Singapore", "United Kingdom",
    "Hong Kong", "Germany", "Japan", "UAE", "New Zealand", "Malaysia",
    "France", "Switzerland", "South Korea", "Thailand", "Vietnam",
    "Netherlands", "Italy", "Spain", "Brazil", "India", "Ireland",
]


def load_manifest_rows():
    if not MANIFEST.exists():
        return []
    with open(MANIFEST, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    rows = load_manifest_rows()
    keywords = {b: {"I": [], "C": [], "T": []} for b in BUSINESS_ZH}

    # 1) From the manifest: title pairs per business/intent.
    for r in rows:
        biz = (r.get("business") or "").strip().lower()
        intent = (r.get("intent") or "I").strip().upper()
        t_zh = (r.get("title_zh") or "").strip()
        t_en = (r.get("title_en") or "").strip()
        if biz in keywords and intent in keywords[biz]:
            if t_zh:
                keywords[biz][intent].append(t_zh)
            if t_en:
                keywords[biz][intent].append(t_en)

    # 2) Country x pattern expansion (keeps the list within TARGET budget).
    per_biz_target = TARGET // len(BUSINESS_ZH)
    for biz, patterns in PATTERNS.items():
        budget = per_biz_target - len(keywords[biz]["I"]) - len(keywords[biz]["C"]) - len(keywords[biz]["T"])
        if budget <= 0:
            continue
        added = 0
        for p_zh, p_en in patterns:
            for i, (cz, ce) in enumerate(zip(COUNTRIES_ZH, COUNTRIES_EN)):
                if added >= budget:
                    break
                kw = f"{cz}{p_zh}"
                if kw not in keywords[biz]["C"]:
                    keywords[biz]["C"].append(kw)
                    added += 1
                if added >= budget:
                    break
                kwe = f"{p_en} in the {ce}"
                if kwe not in keywords[biz]["C"]:
                    keywords[biz]["C"].append(kwe)
                    added += 1

    # 3) Dedupe and count.
    total = 0
    lines = [
        "# 关键词库 V1（300 词）",
        "",
        "> 版本 V1.0 · 2026-08-10 · 由 docs/article-manifest.csv（150 选题）+ 22 国家专页提炼，",
        "> 按业务线 × 意图（I 信息型 / C 商业型 / T 交易型）× 中英双语组织。",
        "> 用途：文章选题去重、落地页关键词部署、GEO/LLM 引用词覆盖。",
        "",
    ]
    for biz, label in BUSINESS_ZH.items():
        lines.append(f"## {biz.upper()} · {label}")
        lines.append("")
        for intent in ("I", "C", "T"):
            kws = list(dict.fromkeys(keywords[biz][intent]))
            if not kws:
                continue
            lines.append(f"### {intent} · {INTENT_LABEL[intent]}（{len(kws)}）")
            lines.append("")
            for kw in kws:
                lines.append(f"- {kw}")
            lines.append("")
        total += sum(len(dict.fromkeys(keywords[biz][i])) for i in ("I", "C", "T"))

    lines.insert(3, f"> 实际词条：**{total}**")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"keywords written: {total} -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
