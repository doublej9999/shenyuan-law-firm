import re
from typing import Dict, Any, List

VALID_BUSINESS = {"trade", "recovery", "legacy", "general"}
KEYWORDS = {
    "trade": ["贸易", "货款", "合同", "违约", "国际", "提单", "信用证", "海运", "仲裁"],
    "recovery": ["追收", "欠款", "债务", "执行", "时效", "保全", "财产线索", "判决"],
    "legacy": ["继承", "遗产", "遗嘱", "过户", "继承人", "公证", "信托", "涉外继承"],
    "general": ["涉外", "法律", "合规", "跨境", "争议解决"],
}

# 律所合规违禁词（承诺结果、绝对化夸大）
COMPLIANCE_RISK_WORDS = [
    "100%胜诉", "包胜", "必胜", "保证追回", "零风险", "完全追回", "包打赢", "百分之百"
]

def evaluate_article_quality(payload: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[str] = []
    warnings: List[str] = []
    score = 100

    title_zh = payload.get("title_zh", "").strip()
    title_en = payload.get("title_en", "").strip()
    desc_zh = payload.get("description_zh", "").strip()
    desc_en = payload.get("description_en", "").strip()
    body_zh = payload.get("body_zh", "").strip()
    body_en = payload.get("body_en", "").strip()
    business = payload.get("business", "general")
    slug = payload.get("slug", "").strip()

    # 1. 必填与长度检测
    if not slug:
        issues.append("Slug 缺失")
        score -= 20
    elif not re.match(r"^[a-z0-9\-]+$", slug):
        issues.append("Slug 格式需为纯小写英文、数字和短横线")
        score -= 10

    if not title_zh:
        issues.append("中文标题缺失")
        score -= 20
    elif len(title_zh) > 50:
        warnings.append(f"中文标题过长（{len(title_zh)} 字符，建议 ≤40）")
        score -= 5

    if not title_en:
        warnings.append("英文标题缺失（建议提供双语以优化海外搜索）")
        score -= 10

    if len(desc_zh) < 40:
        warnings.append(f"中文描述较短（{len(desc_zh)} 字符，建议 60-160 字符以利于搜索摘要展示）")
        score -= 5
    elif len(desc_zh) > 200:
        warnings.append("中文描述超过 200 字符，可能在搜索结果截断")
        score -= 3

    # 2. 正文字数与深度检测
    len_zh = len(body_zh)
    len_en = len(body_en)
    if len_zh < 500:
        issues.append(f"中文正文内容过短（{len_zh} 字，建议 ≥800 字提供充分专业分析）")
        score -= 20
    elif len_zh < 800:
        warnings.append(f"中文正文字数偏少（{len_zh} 字，建议 ≥800 字）")
        score -= 5

    if not body_en:
        warnings.append("缺少英文正文（建议提供双语内容）")
        score -= 10
    elif len_en < 300:
        warnings.append("英文正文偏短（建议 ≥400 字符）")
        score -= 5

    # 3. 转化 CTA 检测
    cta_zh_candidates = ["咨询", "评估", "联系", "/#intake", "微信"]
    if not any(c in body_zh for c in cta_zh_candidates):
        warnings.append("中文正文缺少引导咨询或评估的 CTA 行动呼吁")
        score -= 5

    # 4. 律所免责声明检测
    disclaimer_zh_candidates = ["免责", "不构成法律意见", "仅供参考", "委托关系"]
    if not any(d in body_zh for d in disclaimer_zh_candidates):
        issues.append("中文缺少合规免责声明（必须说明文章不构成正式法律意见）")
        score -= 15

    # 5. 业务线关键词命中
    biz_keywords = KEYWORDS.get(business, KEYWORDS["general"])
    hits = [kw for kw in biz_keywords if kw in (body_zh + title_zh)]
    if len(hits) < 2:
        warnings.append(f"未充分覆盖核心业务关键词（已命中: {hits}，建议融入更多行业搜索词）")
        score -= 5

    # 6. 合规红线检测
    risk_hits = [r for r in COMPLIANCE_RISK_WORDS if r in body_zh or r in title_zh]
    if risk_hits:
        issues.append(f"发现可能违规的胜诉保证绝对化用语: {', '.join(risk_hits)}")
        score -= 30

    final_score = max(0, score)
    passed = len(issues) == 0 and final_score >= 70

    return {
        "score": final_score,
        "passed": passed,
        "issues": issues,
        "warnings": warnings,
        "word_count_zh": len_zh,
        "word_count_en": len_en,
        "keyword_hits": hits,
    }
