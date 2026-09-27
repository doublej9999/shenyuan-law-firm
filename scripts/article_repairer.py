#!/usr/bin/env python3
"""文章自动优化与自愈修复器 (Article Auto-Repair Engine).

当文章存在质量缺陷（如字数不足、缺少 CTA、缺少免责声明、缺少英文版、格式不合规等）时，
自动执行定向增补与合规修复，确保文章通过质量门禁并达到发布标准。
"""

import re
from typing import Dict, Any, Tuple

VALID_BUSINESS = {"trade", "recovery", "legacy", "general"}

KEYWORDS = {
    "trade": ["国际贸易", "货款追收", "合同违约", "提单质押", "信用证纠纷", "海运仲裁"],
    "recovery": ["跨境追收", "海外欠款", "债务执行", "诉讼时效", "跨境财产保全", "境外判决"],
    "legacy": ["涉外继承", "跨国遗产", "海外遗嘱认证", "产权过户", "境外继承人", "离岸信托"],
    "general": ["涉外法律", "跨国合规", "跨境争议解决", "涉外民商事"],
}

DEFAULT_CTA_ZH = "\n\n---\n\n## 寻求专业支持\n\n涉外法律事务涉及多国法域衔接与严苛程序时效。如您正面临相关法律争议，欢迎随时联系我们进行评估：\n\n[免费咨询 →](/#intake)\n"
DEFAULT_CTA_EN = "\n\n---\n\n## Professional Legal Support\n\nCross-border dispute resolution requires multi-jurisdictional coordination and rapid procedural response. If you require legal assessment, please reach out to our team:\n\n[Free consultation →](/#intake)\n"

DISCLAIMER_ZH = "\n\n---\n\n*免责声明：本文内容仅供涉外法律实务研讨与一般信息参考，不构成正式法律意见或建立委托代理关系。具体案件请结合案件事实与管辖法律单独咨询。*"
DISCLAIMER_EN = "\n\n---\n\n*Legal Disclaimer: The insights contained in this publication are for general informational purposes only and do not constitute formal legal opinion or create an attorney-client relationship.*"

COMPLIANCE_REPLACEMENTS = {
    "100%胜诉": "争取最大胜诉几率",
    "包胜": "全力争取有利判决",
    "必胜": "力争胜诉",
    "保证追回": "尽全力追回款项",
    "零风险": "有效控制法律风险",
    "完全追回": "依法主张全额追偿",
    "包打赢": "专业代理争取优势",
    "百分之百": "高度",
}

SUPPLEMENT_ZH = {
    "trade": """
### 补充实务指南：国际贸易履约风险排查清单
1. **单证一致性审查**：海运提单（B/L）、商业发票、装箱单与原产地证需保持严格一致，防范买方以单证瑕疵拒付。
2. **贸易术语（Incoterms）权责划分**：FOB 还是 CIF 条件下，货损风险移转点不同，发生争议应首先确认货物交付与通关责任。
3. **管辖权与仲裁条款校验**：优先约定具备涉外执行便利的仲裁机构（如贸仲、HKIAC、SIAC），避免境外地方保护。
""",
    "recovery": """
### 补充实务指南：跨境债务追讨黄金周期与排查
1. **时效中断操作**：在诉讼时效届满前，务必通过公证送达律师催款函、签署对账确认单等方式法定中断时效。
2. **财产穿透与保全**：协同当地专业调查机构排查债务人名下不动产、银行账户及关联公司应收款，抢占冻结先机。
3. **执行替代路径**：在判决难以执行时，评估通过提起破产清算清查董监高个人责任的可能性。
""",
    "legacy": """
### 补充实务指南：跨国遗产继承核心合规步骤
1. **身份与亲属关系公证认证**：境外出具的出生、死亡、亲属证明均须经由海牙认证（Apostille）或驻外使领馆认证。
2. **遗嘱认证程序（Probate）**：在普通法系国家（如美、英、加、澳），遗产通常需经当地法院认证后方可由遗产管理人分配。
3. **跨境继承税务申报**：在过户前须准确核算所在国的遗产税（Estate Tax）与资本利得税申报窗口，防范税务罚金。
""",
    "general": """
### 补充实务指南：跨国争议应对关键节点
1. **第一时间保全电子证据**：原始往来邮件、电子签名协议、支付水单均须保全电子哈希值或办理公证。
2. **双语专业律师介入**：尽早由熟悉两地实体法与程序法的涉外律师制定诉讼与和解备选双轨策略。
3. **成本效益动态评估**：结合境外诉讼费用、域外执行周期与预估回款比例，理性选择维权路径。
"""
}

SUPPLEMENT_EN = {
    "trade": """
### Supplementary Practice Checklist: International Trade Compliance
1. **Documentary Consistency**: Ensure absolute consistency across Bills of Lading, Commercial Invoices, and Packing Lists to preclude frivolous buyer rejections.
2. **Incoterms Risk Allocation**: Verify risk transfer points under FOB vs. CIF terms to determine immediate carrier and cargo liability.
3. **Dispute Resolution Clauses**: Standardize arbitration clauses specifying reputable institutions (CIETAC, HKIAC, SIAC) for streamlined international recognition.
""",
    "recovery": """
### Supplementary Practice Checklist: Cross-Border Asset Recovery
1. **Statute of Limitations Toll**: Formally toll local limitation periods through certified legal demand notices and debt acknowledgment protocols.
2. **Offshore Asset Tracing**: Deploy investigative measures targeting debtor bank accounts, real property, and subsidiary holdings prior to formal litigation.
3. **Alternative Insolvent Remedies**: Assess whether winding-up or bankruptcy petitions can induce settlement by exposing director and officer liabilities.
""",
    "legacy": """
### Supplementary Practice Checklist: Cross-Border Succession Protocols
1. **Apostille & Legalization**: Foreign death certificates, wills, and kinship affidavits must undergo Apostille or consular certification for domestic validity.
2. **Probate Proceedings**: In common law jurisdictions (US, UK, Australia, Singapore), estate administration mandates court probate before distribution.
3. **Cross-Border Tax Compliance**: Complete requisite inheritance and estate tax filings before transferring titles to mitigate cross-border penalty risks.
""",
    "general": """
### Supplementary Practice Checklist: Multi-Jurisdictional Litigation
1. **Digital Evidence Chain**: Secure cryptographic hash verification and notary seals for email trails and contract executions.
2. **Bilingual Counsel Representation**: Retain counsel experienced in cross-border civil procedure to align foreign litigation with domestic enforcement.
3. **Cost-Benefit Modeling**: Continually evaluate cross-border litigation expenditures against anticipated asset recovery realization rates.
"""
}


def repair_article(article_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], list]:
    """修复与增强文章数据，使其达到质量门禁标准并可直接发布。"""
    repairs = []
    art = dict(article_dict)

    biz = art.get("business", "general")
    if biz not in VALID_BUSINESS:
        biz = "general"
        art["business"] = biz
        repairs.append("规范 business 为 general")

    # 1. 修复 slug
    slug = art.get("slug", "").strip()
    if not slug:
        slug = f"cross-border-legal-guide-{biz}"
        repairs.append(f"补齐缺失的 slug: {slug}")
    else:
        slug = re.sub(r"[^a-zA-Z0-9\-]+", "-", slug.lower()).strip("-")
        slug = re.sub(r"-+", "-", slug)
    art["slug"] = slug

    # 2. 修复标题
    title_zh = art.get("title_zh", "").strip()
    if not title_zh:
        title_zh = f"涉外法律实务指南：{biz} 核心争议与维权策略"
        repairs.append("补齐缺失的中文标题")
    if len(title_zh) > 40:
        title_zh = title_zh[:40].rstrip("，、；- ")
        repairs.append(f"裁剪过长的中文标题至 {len(title_zh)} 字符")
    art["title_zh"] = title_zh

    title_en = art.get("title_en", "").strip()
    if not title_en:
        title_en = f"Cross-Border Legal Practice Guide: Navigating {biz.capitalize()} Disputes"
        repairs.append("补齐缺失的英文标题")
    if len(title_en) > 70:
        title_en = title_en[:70].rsplit(" ", 1)[0]
        repairs.append(f"调整英文标题长度至 {len(title_en)} 字符")
    art["title_en"] = title_en

    # 3. 修复描述
    desc_zh = art.get("description_zh", "").strip()
    if len(desc_zh) < 60:
        desc_zh = f"{desc_zh} 本指南深度剖析跨国管辖、法律适用与实务维权痛点，梳理核心证据保全与财产查控操作指南，帮助企业与当事人稳健应对跨境争议，防范涉外经营风险。"[:140]
        repairs.append("增补中文摘要至合规长度(60-160字)")
    elif len(desc_zh) > 160:
        desc_zh = desc_zh[:155].rstrip("，、； ") + "..."
        repairs.append("裁剪过长的中文摘要至 ≤160 字符")
    art["description_zh"] = desc_zh

    desc_en = art.get("description_en", "").strip()
    if len(desc_en) < 60:
        desc_en = f"{desc_en} In-depth legal analysis on cross-border jurisdiction, evidentiary preservation, asset trace, and effective dispute resolution procedures for international parties."[:160]
        repairs.append("增补英文摘要至合规长度(60-170字符)")
    elif len(desc_en) > 170:
        desc_en = desc_en[:165].rsplit(" ", 1)[0] + "..."
        repairs.append("裁剪过长的英文摘要至 ≤170 字符")
    art["description_en"] = desc_en

    # 4. 修复正文（合规词替换）
    body_zh = art.get("body_zh", "").strip()
    body_en = art.get("body_en", "").strip()

    for risk_word, safe_word in COMPLIANCE_REPLACEMENTS.items():
        if risk_word in body_zh:
            body_zh = body_zh.replace(risk_word, safe_word)
            repairs.append(f"合规替换风险词: {risk_word} -> {safe_word}")
        if risk_word in art["title_zh"]:
            art["title_zh"] = art["title_zh"].replace(risk_word, safe_word)

    # 5. 增补中文正文字数与关键词覆盖
    if len(body_zh) < 800:
        supp = SUPPLEMENT_ZH.get(biz, SUPPLEMENT_ZH["general"])
        body_zh += "\n\n" + supp
        repairs.append(f"正文偏短，注入业务实务清单以达到 ≥800 字符 (现 {len(body_zh)} 字)")

    # 检查关键词
    keywords = KEYWORDS.get(biz, KEYWORDS["general"])
    hits = [kw for kw in keywords if kw in (body_zh + art["title_zh"])]
    if len(hits) < 2:
        k_str = "、".join(keywords[:3])
        body_zh += f"\n\n在具体的涉外实务中，针对{k_str}等环节的合规审查尤为关键，当事人需严控各阶段操作凭证。"
        repairs.append("补充业务线核心关键词覆盖")

    # 6. 检查 CTA
    if not any(c in body_zh for c in ("[免费咨询 →](/#intake)", "[免费评估我的案件 →](/#intake)", "[免费法律咨询 →](/#intake)")):
        body_zh += DEFAULT_CTA_ZH
        repairs.append("注入中文 CTA 转化链接")

    # 7. 检查免责声明
    if "不构成法律意见" not in body_zh:
        body_zh += DISCLAIMER_ZH
        repairs.append("注入中文标准法律免责声明")

    art["body_zh"] = body_zh

    # 8. 修复英文正文
    if not body_en or len(body_en) < 400:
        supp_en = SUPPLEMENT_EN.get(biz, SUPPLEMENT_EN["general"])
        if not body_en:
            body_en = f"""# {art['title_en']}

In cross-border business transactions and multi-jurisdictional proceedings, navigating legal disputes requires strategic risk allocation, stringent compliance, and timely judicial actions.

## Strategic Enforcement Framework
1. **Jurisdictional Review**: Identify whether court litigation or international arbitration governs the contractual relationship.
2. **Evidentiary Preservation**: Secure all cross-border communications, bank remittance records, and official notarized documents.
3. **Cross-Border Enforcement**: Leverage reciprocal enforcement treaties or local asset freezing orders to maximize recovery.
"""
        body_en += "\n\n" + supp_en
        repairs.append(f"注入英文正文结构以达到 ≥400 字符 (现 {len(body_en)} 字符)")

    if not any(c in body_en for c in ("[Free consultation →](/#intake)", "[Free case assessment →](/#intake)", "[Free legal consultation →](/#intake)")):
        body_en += DEFAULT_CTA_EN
        repairs.append("注入英文 CTA 转化链接")

    if "general information" not in body_en.lower() and "not legal advice" not in body_en.lower():
        body_en += DISCLAIMER_EN
        repairs.append("注入英文标准法律免责声明")

    art["body_en"] = body_en

    return art, repairs
