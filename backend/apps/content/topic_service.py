import re
from typing import List, Dict, Any
from apps.content.models import ContentArticle
from apps.core.models import SearchLog

# 核心选题库预置模板（按出海/涉外诉求分类）
CURATED_TOPICS = [
    {
        "business": "trade",
        "topic": "跨境电商货代卷款失联：提单被扣与货权救济路径",
        "slug_hint": "freight-forwarder-holding-cargo-remedies",
        "intent": "I",
        "keywords": ["货代扣货", "提单质押", "无单放货", "跨境海商"],
        "reason": "外贸高发痛点与货权紧急保全诉求",
    },
    {
        "business": "trade",
        "topic": "国际买家恶意拒付破产：中国出口企业跨境债权申报指南",
        "slug_hint": "foreign-buyer-bankruptcy-creditor-claims",
        "intent": "I",
        "keywords": ["买方破产", "债权申报", "出口信用险", "违约追偿"],
        "reason": "海外宏观波动下高频长尾搜索词",
    },
    {
        "business": "recovery",
        "topic": "胜诉判决落地难：中国法院判决在新加坡与香港的认可与执行程序",
        "slug_hint": "enforcing-chinese-judgments-in-hk-and-singapore",
        "intent": "T",
        "keywords": ["境外判决认可", "香港高院执行", "新加坡互认", "跨境资产查控"],
        "reason": "高意向跨境执行客户核心搜索词",
    },
    {
        "business": "recovery",
        "topic": "海外债务人恶意转移资产：离岸信托与空壳公司穿透取证法",
        "slug_hint": "piercing-offshore-trusts-and-shell-companies",
        "intent": "T",
        "keywords": ["隐匿资产", "离岸公司穿透", "虚假转让撤销", "跨境取证"],
        "reason": "高标的商事追索决策者关注主题",
    },
    {
        "business": "legacy",
        "topic": "外籍华人继承中国境内房产与银行存款：全流程公证及税务实务",
        "slug_hint": "foreign-citizens-inheriting-china-property-process",
        "intent": "I",
        "keywords": ["涉外遗产公证", "房产继承过户", "继承税费", "海外继承人"],
        "reason": "海外华人高搜索量与高咨询转化长尾词",
    },
    {
        "business": "legacy",
        "topic": "跨国遗嘱效力冲突：中美加澳跨境遗产规划与遗嘱互认避坑",
        "slug_hint": "cross-border-will-validity-and-conflict-of-laws",
        "intent": "I",
        "keywords": ["涉外遗嘱", "法律适用法", "双重国籍继承", "遗产信托"],
        "reason": "家族办公室与跨境高净值人群刚需",
    },
]

def get_suggested_topics() -> List[Dict[str, Any]]:
    """获取智能选题推荐列表，包含已有文章排重与站内搜索缺口结合"""
    existing_slugs = set()
    existing_titles = []
    try:
        existing_slugs = set(ContentArticle.objects.values_list("slug", flat=True))
        existing_titles = list(ContentArticle.objects.values_list("title_zh", flat=True))
    except Exception:
        pass
    
    suggestions: List[Dict[str, Any]] = []

    # 1. 过滤已写过的预置选题
    for item in CURATED_TOPICS:
        slug = item["slug_hint"]
        # 简单比对防重
        if slug in existing_slugs or any(item["topic"][:6] in t for t in existing_titles):
            continue
        suggestions.append({
            **item,
            "source": "curated_matrix",
        })

    # 2. 从站内搜索日志提取未命中的高频需求 (SearchLog)
    try:
        missed_searches = SearchLog.objects.filter(results=0).order_by("-created_at")[:10]
        seen_queries = set()
        for s in missed_searches:
            q = s.q.strip()
            if len(q) >= 4 and q not in seen_queries and not any(q in t for t in existing_titles):
                seen_queries.add(q)
                slug_hint = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-") or "cross-border-legal-guide"
                suggestions.append({
                    "business": "general",
                    "topic": f"【客户搜索关注】关于「{q}」的涉外法律实务与维权指引",
                    "slug_hint": slug_hint,
                    "intent": "I",
                    "keywords": [q, "涉外法律", "维权实务"],
                    "reason": "来自官网访客真实搜索未命中词（即时需求缺口）",
                    "source": "search_demand",
                })
    except Exception:
        pass

    return suggestions[:8]
