#!/usr/bin/env python3
"""全自动 CMS 内容生产、AI 创作、自愈优化与自动发布流水线脚本。

架构：
  1. AI 创作引擎：集成 cpa.927900.xyz (deepseek-v4.1-flash)，生成高深度双语专业涉外法务长文；
  2. 自愈优化引擎：自动筛查合规、补齐字数与结构化清单、注入转化 CTA 及标准涉外免责声明；
  3. 生产发布：直接对接生产端 CMS (https://shenyuan-backend.vercel.app)，零代码改动、无需重构；
  4. 实时推送：调用 Google Indexing API 主动提交中英双语 URL，加速搜索索引。

用法：
  python3 scripts/auto_content_pipeline.py --publish            # 自动调用 AI 生成 1 篇并通过优化后直接发布
  python3 scripts/auto_content_pipeline.py --repair-drafts 2    # 自动优化并发布 2 篇存量草稿
  python3 scripts/auto_content_pipeline.py --daily-run          # 每日综合任务：AI 生成发布 2 篇 + 优化发布 1 篇草稿
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# 防止控制台编码报错
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from article_repairer import repair_article

BACKEND_BASE = os.environ.get("BACKEND_API_URL", "https://shenyuan-backend.vercel.app").rstrip("/")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "shenyuan-admin-prod-token-2026").strip()

# AI 大模型配置（优先读取环境变量，其次从 .env 中提取）
LLM_API_BASE = os.environ.get("LLM_API_BASE", "https://cpa.927900.xyz/v1").rstrip("/")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini-3.8-flash-high").strip()


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


def api_request(path: str, data: dict = None, method: str = "GET") -> dict:
    url = f"{BACKEND_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "User-Agent": "Mozilla/5.0 (compatible; ShenyuanAutoPublisher/2.0)",
    }
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as exc:
        err_msg = exc.read().decode("utf-8", "replace")[:300]
        print(f"[API ERROR] {method} {path} -> HTTP {exc.code}: {err_msg}", file=sys.stderr)
        raise exc


INDEXNOW_KEY = "4b8f2d93e1074a3f890259bfae6741c0"
INDEXNOW_KEY_LOCATION = "https://shenyuanlegal.com/4b8f2d93e1074a3f890259bfae6741c0.txt"


def warmup_edge_cache(slug: str):
    """边缘节点预热：主动请求新发文章四语页与 Sitemap，确保爬虫首访极速命中。"""
    urls = [
        f"https://shenyuanlegal.com/articles/{slug}",
        f"https://shenyuanlegal.com/en/articles/{slug}",
        f"https://shenyuanlegal.com/ar/articles/{slug}",
        f"https://shenyuanlegal.com/es/articles/{slug}",
        "https://shenyuanlegal.com/sitemap.xml?refresh=1",
    ]
    print("       -> [边缘预热] 正在预热 Vercel Edge 缓存节点...")
    import time
    for url in urls:
        t0 = time.time()
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ShenyuanCacheWarmer/1.0)"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                elapsed = int((time.time() - t0) * 1000)
                print(f"          ✓ {url} ({resp.status} OK, {elapsed}ms)")
        except Exception as e:
            print(f"          ! 预热 {url} 提示: {e}")


def notify_indexnow(slug: str):
    """向 IndexNow API 提交实时收录通知（即时覆盖 Bing、ChatGPT Search、Copilot、Yandex）。"""
    try:
        urls = [
            f"https://shenyuanlegal.com/articles/{slug}",
            f"https://shenyuanlegal.com/en/articles/{slug}",
            f"https://shenyuanlegal.com/ar/articles/{slug}",
            f"https://shenyuanlegal.com/es/articles/{slug}",
        ]
        payload = {
            "host": "shenyuanlegal.com",
            "key": INDEXNOW_KEY,
            "keyLocation": INDEXNOW_KEY_LOCATION,
            "urlList": urls,
        }
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            headers={"Content-Type": "application/json; charset=utf-8"},
            data=json.dumps(payload).encode("utf-8"),
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"       -> IndexNow 实时推送成功 ({resp.status})！已即时同步 Bing & ChatGPT Search 索引库。")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"       -> IndexNow 推送响应 ({e.code}): {body}")
    except Exception as e:
        print(f"       -> IndexNow 推送异常: {e}")


def notify_indexing(slug: str):
    """向 Google Indexing API 主动提交收录通知。"""
    try:
        import subprocess
        urls = [
            f"https://shenyuanlegal.com/articles/{slug}",
            f"https://shenyuanlegal.com/en/articles/{slug}",
        ]
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "indexing_notify.py"),
            *urls,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output_clean = res.stdout.strip()
        print("       -> Google Indexing 提交输出: " + output_clean)
        if res.stderr:
            print("       -> 错误提示: " + res.stderr.strip())
    except Exception as e:
        print(f"       -> 提交 Google Indexing 异常: {e}")


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
  "body_zh": "中文深度实务正文Markdown(1200-2500字，包含案件背景、法律适用与红线、实操维权四步法、证据清单表格、常见问答FAQ、转化呼吁[免费咨询 →](/#intake)与标准免责声明)",
  "body_en": "地道英文Markdown正文(包含对应章节、Evidentiary Checklist、[Free consultation →](/#intake)与英文Legal Disclaimer)"
}

【合规红线】
禁止使用“100%胜诉”、“必胜”、“保证追回全部损失”等承诺胜诉绝对化表述，正文末尾必须保留标准免责声明。
"""


def generate_article_with_ai(topic: str, business: str = "general") -> dict:
    """调用 cpa.927900.xyz 的 deepseek-v4.1-flash 生成高质量涉外法律长文。"""
    api_key = get_llm_api_key()
    if not api_key:
        print("       [提示] 未检测到 LLM API Key，降级至专家规则模板生成。")
        return generate_article_template(topic, business)

    prompt = f"""你是一名资深涉外律师与合规主管。请撰写一篇关于《{topic}》的深度实务双语指南（业务线：{business}）。
请直接输出包含以下字段的合法纯 JSON 对象，不要输出任何前言、后记或说明：
{{
  "slug": "语义化英文URL路径(如 cross-border-debt-collection-guide)",
  "title_zh": "中文专业标题(30字以内，包含核心长尾词与实务痛点)",
  "title_en": "英文专业标题(70字符以内)",
  "description_zh": "中文SEO摘要(80-150字，精准概括核心痛点与法律应对路径)",
  "description_en": "英文SEO摘要(100-160字符)",
  "business": "{business}",
  "intent": "I",
  "body_zh": "中文深度实务正文Markdown(1500-2200字，包含案件背景、法律适用与管辖红线、实操维权四步法、证据清单对照表、业务常见问答FAQ、转化呼吁[免费咨询 →](/#intake)与免责声明)",
  "body_en": "地道英文Markdown正文(包含对应章节、Evidentiary Checklist、[Free consultation →](/#intake)与英文Legal Disclaimer)"
}}

【GEO（生成式 AI 引用）专属结构要求】
1. 包含一张《跨国实操要素与管辖对比表》（Markdown Table：对比法域/国家、诉讼或仲裁时效、举证要件、执行难点与周期成本）。
2. 明确援引具体法律法规或国际公约条款（例如《纽约公约》第V条、《海牙送达公约》、《海牙取证公约》、CISG或中国《涉外民事关系法律适用法》），以便 Perplexity/ChatGPT/Copilot 等生成式 AI 引擎直接抓取作为权威答案出处（Answer Source）。

【合规红线】
禁止使用“100%胜诉”、“必胜”、“保证追回全部损失”等承诺胜诉绝对化表述，正文末尾必须保留标准免责声明。"""

    models_to_try = [LLM_MODEL, "deepseek-v4.1-flash", "gemini-3.8-flash", "deepseek-v4-flash"]
    seen = set()
    models = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

    for model_name in models:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 16384,
        }
        req = urllib.request.Request(
            f"{LLM_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; ShenyuanAutoPublisher/2.0)",
            },
            data=json.dumps(payload).encode("utf-8"),
        )
        try:
            print(f"       -> 正在调用 cpa.927900.xyz 大模型 ({model_name})...")
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content_str = data["choices"][0]["message"].get("content", "").strip()
                s = content_str
                if s.startswith("```"):
                    s = re.sub(r"^```[a-zA-Z0-9]*\n?", "", s)
                    s = re.sub(r"\n?```$", "", s).strip()
                start = s.find('{')
                end = s.rfind('}')
                if start != -1 and end != -1 and end > start:
                    res_json = json.loads(s[start:end+1], strict=False)
                    zh_len = len(res_json.get("body_zh", ""))
                    en_len = len(res_json.get("body_en", ""))
                    print(f"       -> AI 大模型 ({model_name}) 创作成功！(中文: {zh_len} 字符, 英文: {en_len} 字符) ✓")
                    return res_json
                else:
                    print(f"       [WARN] 大模型 {model_name} 输出未能解析出闭合 JSON，尝试备选模型...")
        except Exception as e:
            print(f"       [WARN] 调用 {model_name} 异常: {e}，尝试备选模型...")

    print("       [降级] 全部大模型调用未果，安全降级至专家规则模板。")
    return generate_article_template(topic, business)


def generate_article_template(topic: str, business: str = "general") -> dict:
    """备用高可用降级模板引擎。"""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", topic.lower()).strip("-")
    if not slug or len(slug) < 4:
        slug = f"cross-border-{business}-practice"
    slug = f"{slug[:50].rstrip('-')}"

    title_zh = f"【涉外实务】{topic}：法律风险、维权路径与避坑清单"
    title_en = f"Navigating {topic}: Legal Strategies, Risk Controls and Enforcement"

    desc_zh = f"围绕「{topic}」核心焦点，深度剖析跨国管辖、法律适用与实务维权痛点，梳理核心证据保全与财产查控操作指南，帮助企业与当事人稳健应对跨境争议。"
    desc_en = f"Practical legal guide for {topic}: addressing cross-border jurisdiction, evidentiary preservation, asset trace, and effective dispute resolution procedures."

    body_zh = f"""# {title_zh}

在经济全球化与跨国商贸合作深入推进的当下，**{topic}** 成为中国涉外企业、跨境投资人及出海主体高频遭遇的复杂法律争议。因涉及两个或多个不同主权法域的司法管辖、两地实体法差异及执行阻隔，当事人如果处置不当，往往极易错失跨国财产保全与追偿的黄金时间窗口。

---

## 一、 涉案争议焦点与常见风险壁垒

在多年的涉外司法实践与代理案例中，我们发现此类案件普遍存在以下系统性风险：

1. **涉外管辖权异议与平行诉讼风险**：双方若未在初始交易合同中订立明确排他的争议解决条款，常在起诉阶段遭遇对方恶意提起的管辖权异议，甚至在多国法院发起平行诉讼以拖延时间。
2. **域外证据链形式合规缺陷**：涉及境外主体身份信息、往来电邮及付款凭单，未按照海牙公约要求办理海牙附加证明书（Apostille）或领事认证，导致法庭证据效力遭遇挑战。
3. **跨境财产隐匿与转移速度快**：涉案债务人或违约方往往通过离岸空壳公司、代持协议或多层嵌套账户快速转移有效资金，若未提前进行资产线索穿透排查，常面临“赢了判决却无财产可执”的困局。

---

## 二、 涉外维权与争议应对实务四步法

针对上述痛点，涉外当事人与法务团队应当依托以下实操步骤掌握处置主动权：

- **第一步：全面固定电子证据与链条公证**  
  第一时间对全部订单确认函、商业发票、海运提单、跨境汇款底单及原始电子邮件通讯记录进行哈希值固定与公证，确保证据的真实性与不可篡改性。
- **第二步：开展多维度离岸与境内财产穿透排查**  
  利用商业登记公开数据库、离岸司法查控网络及不动产登记薄，全面摸排涉案主体名下的有效动产、不动产、知识产权及第三方应收账款。
- **第三步：由涉外律师出具中英双语正式催告函（Legal Demand Letter）**  
  结合管辖国实体法与利息违约金计息规则，向违约方精准阐明法律后果并施加商誉信用抗辩压力，争取通过商业谈判或附担保分期和解快速结案。
- **第四步：申请跨国诉讼保全与正式仲裁/诉讼**  
  依据管辖条款在具备执行便利的法院或国际仲裁院（如 CIETAC、HKIAC、SIAC）启动程序，并同步申请财产冻结令（Freezing Order）。

---

## 三、 常见问题解答与实操要点 (FAQ)

**Q1: 境外违约方是注册在 BVI 或开曼的离岸公司，能否穿透追索其实际控制人？**  
**A:** 在符合法定要件的情形下，如能充分举证其实际控制人滥用公司独立法人地位、财产与个人高度混同以逃避债务，可依法主张“揭开公司面纱”（Piercing the Corporate Veil），要求股东或实控人承担连带偿还责任。

**Q2: 取得国内法院的生效判决书后，如何前往债务人所在法域申请执行？**  
**A:** 可依据两国双边民商事司法协助条约、互惠原则或特定地区的判决互认安排（如香港《内地民商事判决（相互强制执行）条例》），向境外法院申请判决承认并签发执行令。

---

## 四、 寻求专业支持

涉外法律实务涉及复杂的跨国程序协同与高密度的证据博弈，时间窗口极其宝贵。如果您正在经历类似争议，欢迎随时通过下方入口提交初步案情：

[免费咨询 →](/#intake)

---

*免责声明：本文内容仅供涉外法律实务研讨与一般信息参考，不构成针对任何具体案件的正式法律意见或委托代理关系。具体个案策略须结合全套证据材料与管辖法院判例综合判定。*
"""

    body_en = f"""# {title_en}

In cross-border commerce, international trade, and multinational asset management, **{topic}** has emerged as a high-stakes challenge that demands strategic risk allocation, rigorous compliance, and swift judicial response.

---

## 1. Key Vulnerabilities and Procedural Impediments
- **Jurisdictional Collisions**: Ambiguous choice of law and forum selection clauses frequently trigger costly jurisdictional disputes and parallel proceedings across jurisdictions.
- **Cross-Border Evidence Admissibility**: Documentation generated abroad requires Apostille certification under the Hague Convention to satisfy strict evidentiary standards in court.
- **Offshore Asset Dissipation**: Counterparties frequently leverage offshore shell companies and multi-tiered entity structures to conceal capital flows before formal claims are served.

---

## 2. Strategic Action and Dispute Resolution Protocol
1. **Preserve Digital Evidence Chains**: Secure server headers, electronic mail correspondence, bills of lading, and verified bank records immediately.
2. **Execute Offshore Asset Investigations**: Conduct investigative due diligence to identify bank accounts, corporate equity, and physical assets across targeted jurisdictions.
3. **Issue Formal Bilingual Demand Notices**: Assert statutory claims, contract default penalties, and specific settlement deadlines under governing law.
4. **Interim Measures and Dispute Adjudication**: File for urgent worldwide freezing injunctions and commence litigation or arbitration before designated tribunals (e.g., CIETAC, HKIAC, SIAC).

---

## 3. Professional Legal Assistance
Cross-border dispute resolution requires coordinated advocacy across civil and common law systems. If your organization is facing cross-border contractual breaches or requires urgent asset tracing, please contact our international legal practice:

[Free consultation →](/#intake)

---

*Legal Disclaimer: The insights contained in this publication are for general informational purposes only and do not constitute formal legal opinion or create an attorney-client relationship for any specific matter.*
"""

    return {
        "slug": slug,
        "title_zh": title_zh,
        "title_en": title_en,
        "description_zh": desc_zh,
        "description_en": desc_en,
        "body_zh": body_zh,
        "body_en": body_en,
        "business": business,
        "intent": "I",
    }


HIGH_VALUE_TOPICS_POOL = [
    # 一、国际贸易与跨境商事争端 (trade - 18)
    ("中国跨境电商应对美国特拉华州商事诉讼管辖权异议实务", "trade"),
    ("新加坡国际商事法庭(SICC)中英双语审判与跨国判决执行", "trade"),
    ("国际海运货损索赔诉讼时效与提单免责条款破解", "trade"),
    ("中资企业赴美被诉知识产权侵权与ITC 337调查应对", "trade"),
    ("国际贸易UCP600信用证欺诈与法院止付令申请实操", "trade"),
    ("跨国货运提单无单放货中承运人连带赔偿追索实务", "trade"),
    ("中企出海欧盟面对CBAM碳边境调节机制与ESG合规审查", "trade"),
    ("涉外大宗商品贸易买方拒收货物后的转售减损与违约救济", "trade"),
    ("中德跨国机械设备采购质量异议与CISG公约索赔程序", "trade"),
    ("国际仲裁裁决依据《纽约公约》在香港高等法院申请执行", "trade"),
    ("跨国原产地规则与海关关税穿透核查抗辩实操", "trade"),
    ("涉外独家代理分销协议解除后的商誉补偿与竞业限制争议", "trade"),
    ("中国企业应对美国商务部反倾销反补贴双反调查程序", "trade"),
    ("涉外保税仓货物权属争议与仓储质押监管人连带责任", "trade"),
    ("跨国技术许可协议中提成费审计纠纷与出口管制红线", "trade"),
    ("国际航运滞期费(Demurrage)争议与不可抗力条款援引", "trade"),
    ("中阿跨国基础设施承包工程保函欺诈与止付救济实务", "trade"),
    ("跨境跨境电商平台海外商标抢注与马德里协定异议维权", "trade"),

    # 二、海外资产穿透查控与债权追收 (recovery - 18)
    ("海外债务人通过离岸架构隐匿资产的穿透查控路径", "recovery"),
    ("跨国供应链货款逾期：离岸账户冻结与跨境清算协同", "recovery"),
    ("跨境商业欺诈追索：境外资产调查网络与全球冻结令申请", "recovery"),
    ("债务人转移资产至开曼/BVI离岸公司的欺诈撤销权诉讼", "recovery"),
    ("英国高等法院Mareva全球财产冻结令申请与跨境执行门槛", "recovery"),
    ("美国破产法第15章(Chapter 15)跨境破产承认与资产查扣", "recovery"),
    ("跨国判决在澳大利亚联邦法院申请普通法诉讼执行路径", "recovery"),
    ("迪拜国际金融中心(DIFC)法院判决在阿联酋全境跨法域执行", "recovery"),
    ("中企追讨拉美买方欠款：本国司法协助与当地追偿策略", "recovery"),
    ("债务人隐匿加密资产时的链上追踪与境外民事查扣指引", "recovery"),
    ("中国法院生效商事判决依据互惠原则在境外申请承认", "recovery"),
    ("日本东京地方法院商事债权保全与不动产临时假扣押", "recovery"),
    ("跨国买卖合同欺诈中法定代表人个人无限连带责任刺破", "recovery"),
    ("涉外应收账款保理违约追索与跨境双保理商连带责任", "recovery"),
    ("新加坡《破产、重组与解散法》(IRDA)下跨国债务人债务重组", "recovery"),
    ("跨境货款逾期超诉讼时效后的自然之债转化与重新催告", "recovery"),
    ("韩国大法院对外国仲裁裁决承认与强制执行实务要点", "recovery"),
    ("涉外担保物权在债务人境外破产程序中的优先受偿权主张", "recovery"),

    # 三、离岸信托、跨境继承与家族财富 (legacy - 18)
    ("离岸信托设立后的穿透风险与跨境诉讼实务", "legacy"),
    ("涉外继承中公证遗嘱与普通法系Probate认证的衔接冲突", "legacy"),
    ("跨国婚姻离岸资产分配与家族信托财产保全", "legacy"),
    ("美籍华人继承国内房产及银行存款的涉外继承权公证指南", "legacy"),
    ("跨国代际传承中离岸家族办公室(FO)双重税籍申报与CRS合规", "legacy"),
    ("涉及香港不动产与离岸保单的跨境遗产承办与遗嘱检验", "legacy"),
    ("新加坡VCC可变动资本公司在家族财富离岸隔离中的法律边界", "legacy"),
    ("跨国非婚生子女境外家族信托受益人资格确认与争议化解", "legacy"),
    ("泽西岛与根西岛海峡群岛信托防范债权人追索的法定防火墙", "legacy"),
    ("移民前海外资产重组与家族信托税务筹划风险防范", "legacy"),
    ("中美跨国婚姻离婚诉讼管辖权竞合与不方便法院原则抗辩", "legacy"),
    ("离岸私人信托公司(PTC)治理结构失效与受托人背信救济", "legacy"),
    ("加拿大华人跨国财产继承与海外资产申报(T1135)合规实务", "legacy"),
    ("跨国婚姻共同财产境外购置房产的物权认定与分割清算", "legacy"),
    ("涉外意定监护与跨国失能失智财产委托管理法律实操", "legacy"),
    ("家族信托保护人(Protector)滥用否决权的司法撤换与诉讼", "legacy"),
    ("澳大利亚华人跨国跨境遗嘱信托设立与外国居民继承税筹", "legacy"),
    ("跨境双重国籍身份冲突下的涉外继承准据法适用与排除", "legacy"),
]


def synthesize_dynamic_topic(existing_titles: set) -> tuple:
    """当静态选题池耗尽时，调用 DeepSeek 结合已有标题库衍生出全新的前沿涉外实操选题。"""
    api_key = get_llm_api_key()
    if not api_key:
        return (f"跨国商事争议维权与涉外法务实务-{int(datetime.now().timestamp())}", "trade")

    sample_existing = list(existing_titles)[:20]
    prompt = (
        "你是一名深远国际律师事务所的资深跨境业务合伙人。我们已经发布了以下涉外法律实务指南：\n"
        + "\n".join(f"- {t}" for t in sample_existing)
        + "\n\n请避开上述已有主题，针对当前中企出海、跨国追偿、离岸信托或涉外继承最新的痛点（如美国长臂管辖、新加坡合规、开曼BVI穿透、海牙公证或中东/欧洲纠纷），"
        "构思一个具有高搜索量、专业深度且具体明确的全新法律实操指南选题。\n"
        "请直接输出合法 JSON，格式为：{\"topic\": \"中文选题名称(30字以内)\", \"business\": \"trade|recovery|legacy\"}"
    )

    try:
        payload = {
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500,
        }
        req = urllib.request.Request(
            f"{LLM_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload).encode(),
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
                content = re.sub(r"\n?```$", "", content).strip()
            parsed = json.loads(content)
            topic = parsed.get("topic", "").strip()
            biz = parsed.get("business", "trade").strip()
            if topic and biz in ["trade", "recovery", "legacy"]:
                print(f"       [AI 衍生选题成功] 自动衍生出全新选题: {topic} ({biz})")
                return (topic, biz)
    except Exception as e:
        print(f"       [AI 衍生选题降级] {e}")

    return (f"跨国商事争议维权与涉外法务实战-{int(datetime.now().timestamp())}", "trade")


def generate_multilingual_translations(art: dict, art_id: int) -> dict:
    """自动为新生成的涉外长文生成阿拉伯语 (ar) 与西班牙语 (es) 地道母语版本并写回数据库。"""
    print("\n[多语言管线] 开始为新发文章自动生成阿语 (ar) 与西语 (es) 地道母语版本...")
    try:
        from scripts.batch_translate_multilingual import translate_with_llm
    except ImportError:
        import sys
        sys.path.insert(0, str(ROOT))
        from scripts.batch_translate_multilingual import translate_with_llm

    trans = art.get("translations") or {}

    for lang in ["ar", "es"]:
        lang_name = "阿拉伯语" if lang == "ar" else "西班牙语"
        print(f"       -> 正在调用大模型生成{lang_name} ({lang}) 法律实务译文...")
        t0 = time.time()
        try:
            res = translate_with_llm(art, lang)
            if res and res.get("title") and res.get("title") != "..." and res.get("body"):
                trans[lang] = res
                print(f"          ✓ {lang_name}翻译完成 ({int((time.time()-t0)*1000)}ms): 《{res['title'][:32]}...》")
            else:
                print(f"          ! {lang_name}翻译结果为空或不合规")
        except Exception as e:
            print(f"          ! {lang_name}生成失败: {e}")

    art["translations"] = trans
    try:
        api_request(f"/admin/api/content/{art_id}", data=art, method="PUT")
        print(f"       ✓ 多语言母语数据已成功持久化至数据库 (ID: {art_id})！")
    except Exception as e:
        print(f"       ! 多语言持久化回写异常: {e}")

    return trans


def produce_and_publish_new_article(topic: str = "", business: str = "general"):
    """由 AI 创作、自愈优化并自动发布一篇新文章。"""
    if not topic:
        try:
            existing = api_request("/api/articles")
            existing_slugs = {a.get("slug") for a in existing}
            existing_titles = {a.get("title_zh") for a in existing}
        except Exception:
            existing_slugs, existing_titles = set(), set()

        chosen = None
        for t, b in HIGH_VALUE_TOPICS_POOL:
            if t not in existing_titles and not any(t in title for title in existing_titles):
                chosen = (t, b)
                break
        if not chosen:
            print("       [选题池提醒] 预设 54 篇涉外高价值选题已全部覆盖，正在调用 AI 动态衍生全新前沿选题...")
            chosen = synthesize_dynamic_topic(existing_titles)
        topic, business = chosen

    print("\n" + f"[1/4 选题选定] 主题: {topic} (领域: {business})")

    # 2. AI 创作
    print("[2/4 AI 创作] 调用 DeepSeek-v4.1-Flash 进行涉外法务专业双语创作...")
    art_data = generate_article_with_ai(topic, business)

    # 3. 自愈优化与质量门禁修复
    print("[3/4 自愈优化] 执行合规词筛查、字数扩充、双语 CTA 及免责声明注入...")
    repaired, logs = repair_article(art_data)
    for log in logs:
        print(f"       [优化项] {log}")

    # 4. 调用后端 API 创建并发布
    print("[4/4 自动发布] 向生产端 CMS 提交入库并直接发布...")
    repaired["status"] = "draft"
    
    # 防重 slug 校验
    slug_candidate = repaired["slug"]
    counter = 1
    orig_slug = slug_candidate
    while slug_candidate in existing_slugs:
        slug_candidate = f"{orig_slug}-{counter}"
        counter += 1
    repaired["slug"] = slug_candidate
    
    create_res = api_request("/admin/api/content", data=repaired, method="POST")
    art_id = create_res["id"]
    slug = create_res["slug"]

    pub_res = api_request(f"/admin/api/content/{art_id}/publish", method="POST")
    print("\n" + f"[发布成功] 《{pub_res.get('title_zh')}》已正式发布上线 (ID: {art_id})！")
    print(f"       -> 中文地址: https://shenyuanlegal.com/articles/{slug}")
    print(f"       -> 英文地址: https://shenyuanlegal.com/en/articles/{slug}")

    # 4.5. 自动多语言翻译扩展（阿拉伯语 + 西班牙语）
    repaired["id"] = art_id
    repaired["status"] = "published"
    generate_multilingual_translations(repaired, art_id)
    print(f"       -> 阿语地址: https://shenyuanlegal.com/ar/articles/{slug}")
    print(f"       -> 西语地址: https://shenyuanlegal.com/es/articles/{slug}")

    # 5. 边缘预热（覆盖中英阿西四语）
    warmup_edge_cache(slug)

    # 6. 推送搜索引擎收录 (Google & IndexNow for Bing/ChatGPT 覆盖四语)
    print("[收录推送] 正在向 Google Indexing API 与 IndexNow 提交抓取通知...")
    notify_indexing(slug)
    notify_indexnow(slug)
    return art_id


def repair_and_publish_existing_drafts(limit: int = 1):
    """自动检出未发布草稿，自愈达标后自动发布。"""
    import sqlite3
    db_file = ROOT / "data" / "lawyers.sqlite3"
    if db_file.exists():
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT id, slug, title_zh, title_en, description_zh, description_en, body_zh, body_en, business, intent FROM content_articles WHERE status = 'draft' ORDER BY id ASC LIMIT ?",
            (limit,)
        ).fetchall()
        if rows:
            print("\n" + f"[存量自愈] 发现存量待优化文章 {len(rows)} 篇，开始自愈并自动发布至生产...")
            for r in rows:
                art_dict = {
                    "slug": r["slug"],
                    "title_zh": r["title_zh"],
                    "title_en": r["title_en"],
                    "description_zh": r["description_zh"],
                    "description_en": r["description_en"],
                    "body_zh": r["body_zh"],
                    "body_en": r["body_en"],
                    "business": r["business"],
                    "intent": r["intent"],
                }
                repaired, logs = repair_article(art_dict)
                for log in logs:
                    print(f"       [优化项] {log}")
                repaired["status"] = "draft"
                try:
                    create_res = api_request("/admin/api/content", data=repaired, method="POST")
                    art_id = create_res["id"]
                    pub_res = api_request(f"/admin/api/content/{art_id}/publish", method="POST")
                    print("\n" + f"[发布成功] 《{pub_res.get('title_zh')}》已正式发布上线！")
                    published_slug = str(pub_res.get("slug") or "")
                    if published_slug:
                        print(f"       -> 中文地址: https://shenyuanlegal.com/articles/{published_slug}")
                        repaired["id"] = art_id
                        repaired["status"] = "published"
                        generate_multilingual_translations(repaired, art_id)
                        print(f"       -> 阿语地址: https://shenyuanlegal.com/ar/articles/{published_slug}")
                        print(f"       -> 西语地址: https://shenyuanlegal.com/es/articles/{published_slug}")
                        warmup_edge_cache(published_slug)
                        notify_indexing(published_slug)
                        notify_indexnow(published_slug)
                    conn.execute("UPDATE content_articles SET status = 'published' WHERE id = ?", (r["id"],))
                    conn.commit()
                except Exception as e:
                    print(f"       [跳过] 同步失败或已存在: {e}")
            conn.close()


def main():
    parser = argparse.ArgumentParser(description="CMS 自动化内容流水线（带自愈与即时索引）")
    parser.add_argument("--topic", type=str, default="", help="指定文章主题")
    parser.add_argument("--biz", type=str, default="general", help="业务线: trade / recovery / legacy / general")
    parser.add_argument("--publish", action="store_true", help="生产 1 篇新文章并直接发布")
    parser.add_argument("--repair-drafts", type=int, default=0, help="优化并发布指定数量的存量草稿")
    parser.add_argument("--daily-run", action="store_true", help="每日综合任务（AI 创作 2 篇新文章 + 优化发布 1 篇草稿）")
    args = parser.parse_args()

    if args.daily_run:
        print("==================================================")
        print("  深远涉外法务 — 每日 SEO 内容自动生产与发布流水线")
        print("==================================================")
        print("\n>>> 步骤 1/2: AI 自动创作 2 篇中英双语深度实务文章...")
        produce_and_publish_new_article()
        produce_and_publish_new_article()

        print("\n>>> 步骤 2/2: 自动自愈并发布 1 篇存量草稿...")
        repair_and_publish_existing_drafts(limit=1)

        print("\n==================================================")
        print("  本日 SEO 内容发布与索引提交任务全部完成 ✓")
        print("==================================================")
        return 0

    if args.repair_drafts > 0:
        repair_and_publish_existing_drafts(limit=args.repair_drafts)
        return 0

    if args.publish or args.topic:
        produce_and_publish_new_article(topic=args.topic, business=args.biz)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
