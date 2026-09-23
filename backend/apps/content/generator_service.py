import json
import logging
import os
import re
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional

from apps.content.quality_gate_service import evaluate_article_quality

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一名资深的涉外法律合规顾问与双语法律内容专家，服务于深远(国际)律师事务所 (Shenyuan International Law Firm)。
请基于用户提供的主题、业务领域与要求，输出一篇严谨、权威、具有实际操作价值且高度符合现代搜索引擎（Google/百度）SEO 规则的涉外法律实务双语文章。

【输出要求】
必须严格输出纯 JSON 格式（不得包含 Markdown 代码块标记如 ```json 或 ```），包含以下键名：
{
  "slug": "语义化英文URL路径(如 cross-border-debt-collection-guide)",
  "title_zh": "中文专业标题(30字以内，包含核心长尾词与实务痛点)",
  "title_en": "英文专业标题(70字符以内)",
  "description_zh": "中文SEO摘要(80-150字，精准概括核心痛点与法律应对路径)",
  "description_en": "英文SEO摘要(100-160字符)",
  "business": "所属领域(trade / recovery / legacy / general)",
  "intent": "搜索意图(I 代表信息类, T 代表交易与委托类)",
  "body_zh": "中文深度实务正文Markdown(1000-2000字，包含案件背景、法律适用与红线、实操维权流程、证据清单、FAQ、转化呼吁[免费咨询 →](/#intake)与免责声明)",
  "body_en": "地道英文Markdown正文(包含对应章节、[Free consultation →](/#intake)与英文Legal Disclaimer)"
}

【合规红线】
禁止使用“100%胜诉”、“必胜”、“保证追回全部损失”等承诺胜诉绝对化表述，正文末尾必须保留标准免责声明。
"""

def generate_article_with_llm(topic: str, business: str = "general", custom_prompt: str = "") -> Optional[Dict[str, Any]]:
    """尝试通过 OpenAI 兼容 API 调用大模型生成结构化双语文章"""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip() or os.environ.get("LLM_API_KEY", "").strip()
    if not api_key:
        return None

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("AI_MODEL", "gpt-4o-mini")

    user_content = f"文章主题：{topic}\n业务领域：{business}\n"
    if custom_prompt:
        user_content += f"特别补充要求：{custom_prompt}\n"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"} if "gpt-4" in model or "gpt-3.5" in model else None
    }

    try:
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content_str = data["choices"][0]["message"]["content"].strip()
            # 清理可能的 markdown 代码包裹
            if content_str.startswith("```"):
                content_str = re.sub(r"^```[a-z]*\n?", "", content_str)
                content_str = re.sub(r"\n?```$", "", content_str).strip()
            result = json.loads(content_str)
            return result
    except Exception as e:
        logger.warning(f"LLM API generation failed, falling back to rule engine: {e}")
        return None


def generate_article_from_template(topic: str, business: str = "general", custom_prompt: str = "") -> Dict[str, Any]:
    """高可用降级：涉外法务专业规则引擎生成标准双语文章"""
    slug_base = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")
    if not slug_base or len(slug_base) < 4:
        slug_base = f"cross-border-legal-insight-{business}"
    slug = f"{slug_base[:50].rstrip('-')}"

    biz_name_map = {
        "trade": "国际贸易与跨境合同纠纷",
        "recovery": "跨境债务追收与资产执行",
        "legacy": "涉外继承与离岸资产规划",
        "general": "涉外商事法律实务",
    }
    biz_label = biz_name_map.get(business, "涉外商事法律实务")

    title_zh = f"【涉外实务】{topic}：法律风险、维权路径与避坑清单"
    title_en = f"Navigating {topic}: Legal Strategies, Risk Controls and Cross-Border Enforcement"

    desc_zh = f"围绕「{topic}」核心焦点，深度剖析跨国管辖、法律适用与实务维权痛点，梳理核心证据保全与财产查控操作指南，帮助企业与当事人稳健应对跨境争议。"
    desc_en = f"Practical legal guide for {topic}: addressing cross-border jurisdiction, evidentiary preservation, asset trace, and effective dispute resolution procedures."

    body_zh = f"""# {title_zh}

在经济全球化与经贸合作日益加深的背景下，**{topic}** 成为众多出海企业、跨国经贸主体及当事人高频面临的法律难题。由于涉案当事人位于不同法域、合同履行地与财产所在地分散，一旦发生争议，往往面临管辖权冲突、文书域外送达耗时、实体法适用不确定以及跨境判决难以执行等多重壁垒。

---

## 一、 核心案由与法律风险焦点

结合涉外司法实践与多起典型案例，在处理此类纠纷时，当事人普遍面临以下核心风险：

1. **管辖权与适用法约定不明**：合同中若未明确约定争议解决机构（如贸仲 CIETAC、香港 HKIAC、新加坡 SIAC）及准据法，容易在起诉阶段遭遇管辖权异议，大幅拉长维权周期。
2. **证据链断裂与域外公证认证壁垒**：涉及境外主体资格证明、域外发生电邮、报关单证等关键材料，若未及时在所在国办理公证及海牙附加证明书（Apostille），常导致证据效力在法庭受挫。
3. **财产隐匿与转移速度快**：违约方或债务人常通过离岸架构、代持股权或关联方交易转移有效资产，错过最初的保全黄金窗口期将导致“赢了官司却拿不到钱”。

---

## 二、 关键维权与应对操作步骤

为最大程度止损并掌握处置主动权，建议严格按照以下步骤推进：

- **第一步：紧急固定与公证涉外证据**  
  立即对所有往来邮件（保留完整原始邮件头）、交易凭据、货代单证、银行流水进行固定并办理保全公证，防止数据灭失。
- **第二步：跨境财产线索穿透排查**  
  通过公开商业登记簿、不动产登记机构及境外关联司法查控网络，锁定债务人在海内外的核心资产账户与应收账款。
- **第三步：发出律师催告函（Legal Demand Letter）**  
  由资深涉外律师正式出具双语律师函，明确违约责任、主张逾期违约金及连带赔偿，同时施加信用与诉讼压力，争取以和解或分期担保协议结案。
- **第四步：申请跨国诉讼保全与正式仲裁/诉讼**  
  依据管辖条款向有管辖权的法院或仲裁庭提起诉请，同步申请财产保全裁定，对被申请人境内外核心账户采取冻结措施。

---

## 三、 常见问题解答 (FAQ)

**Q1: 对方是境外注册的空壳公司，能否直接起诉其实际控制人？**  
**A:** 在特定情形下，如能举证证明实际控制人存在资产与公司财产高度混同、抽逃出资或利用公司人格实施欺诈，可依据公司法法人人格否认（Piercing the Corporate Veil）原则追加股东或实控人承担连带责任。

**Q2: 已经拿到国内法院的生效判决，如何到债务人的境外资产地申请执行？**  
**A:** 可依据中国与当地签署的双边司法协助协定，或依据当地涉外民商事判决互认条例（如香港特区《内地民商事判决（相互强制执行）条例》），向境外法院申请认可并予以强制执行。

---

## 四、 寻求专业支持

涉外法律事务涉及多个主权法域的法律衔接与高密度的证据博弈，时间窗口极其宝贵。如果您正在经历类似争议，欢迎随时通过下方入口提交初步案情：

[免费咨询 →](/#intake)

---

*免责声明：本文内容仅供涉外法律实务研讨与一般信息参考，不构成针对任何具体案件的正式法律意见或委托代理关系。具体个案策略须结合全套证据材料与管辖法院判例综合判定。*
"""

    body_en = f"""# {title_en}

In cross-border business transactions and private wealth administration, **{topic}** has become a critical challenge demanding structured risk management and procedural expertise.

## 1. Key Legal Vulnerabilities
- **Jurisdictional Conflicts**: Inconsistent governing law and dispute resolution clauses frequently cause procedural delays.
- **Cross-Border Evidence & Notarization**: Foreign documents require consular legalization or Apostille certification to satisfy admissibility standards.
- **Dissipation of Assets**: Counterparties often leverage offshore corporate vehicles to obscure capital flows.

## 2. Strategic Action Plan
1. **Preserve Digital and Documentary Evidence**: Retain original electronic correspondence, headers, commercial invoices, and bills of lading.
2. **Conduct Offshore Asset Tracing**: Identify reachable onshore and offshore assets prior to alerting the opposing party.
3. **Formal Demand Letter**: Issue bilingual legal notices asserting claims, default interest, and immediate settlement terms.
4. **Interim Injunctions & Dispute Proceedings**: Initiate arbitration or litigation with urgent asset preservation motions.

## 3. Professional Legal Support
Cross-border dispute resolution requires seamless bilingual coordination across international jurisdictions. If you are confronting an active dispute or require strategic contract review, please reach out to our team:

[Free consultation →](/#intake)

---

*Legal Disclaimer: The insights contained in this publication are intended for general information and practical commentary only. They do not constitute formal legal opinion or create an attorney-client relationship for any specific matter.*
"""

    return {
        "slug": slug,
        "title_zh": title_zh,
        "title_en": title_en,
        "description_zh": desc_zh,
        "description_en": desc_en,
        "business": business,
        "intent": "I",
        "body_zh": body_zh,
        "body_en": body_en,
    }


def generate_article_pipeline(topic: str, business: str = "general", custom_prompt: str = "") -> Dict[str, Any]:
    """内容生成综合流水线：优先尝试 LLM，降级至专业模板引擎，并经过质量门禁审查"""
    raw_article = generate_article_with_llm(topic, business, custom_prompt)
    if not raw_article:
        raw_article = generate_article_from_template(topic, business, custom_prompt)

    # 规范 business 与 intent
    raw_article["business"] = raw_article.get("business") or business
    raw_article["intent"] = raw_article.get("intent") or "I"

    # 执行质量门禁审查
    quality = evaluate_article_quality(raw_article)

    return {
        "article": raw_article,
        "quality": quality,
        "generator_mode": "llm" if os.environ.get("OPENAI_API_KEY") else "rule_engine",
    }
