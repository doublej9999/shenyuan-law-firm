#!/usr/bin/env python3
"""全自动 CMS 内容生产、自愈优化与自动发布流水线脚本。

架构：
  直接对接生产环境后端 API (https://shenyuan-backend.vercel.app)，
  无需修改代码，无需本地 Git commit，无需重新构建部署。
  文章发布后，前台（Nuxt 3 SSR）与动态 Sitemap 实时同步呈现，
  并自动调用 Google Indexing API 提交抓取。

用法：
  python3 scripts/auto_content_pipeline.py --publish            # 自动生成 1 篇并通过优化后直接发布
  python3 scripts/auto_content_pipeline.py --repair-drafts 2    # 自动优化并发布 2 篇存量草稿
  python3 scripts/auto_content_pipeline.py --daily-run          # 每日综合任务：新生成发布 2 篇 + 优化发布 1 篇草稿
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from article_repairer import repair_article

BACKEND_BASE = os.environ.get("BACKEND_API_URL", "https://shenyuan-backend.vercel.app").rstrip("/")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "shenyuan-admin-prod-token-2026").strip()


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
        print("       -> Google Indexing 提交输出: " + res.stdout.strip())
        if res.stderr:
            print(f"       -> 错误提示: {res.stderr.strip()}")
    except Exception as e:
        print(f"       -> 提交 Google Indexing 异常: {e}")


def generate_article_template(topic: str, business: str = "general") -> dict:
    """生成具有高信息密度、合规严谨的涉外双语文章初稿。"""
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


def produce_and_publish_new_article(topic: str = "", business: str = "general"):
    """创作、自愈并自动发布一篇新文章。"""
    if not topic:
        topics_pool = [
            ("跨国商事仲裁裁决在海外法院的承认与执行", "recovery"),
            ("离岸信托设立后的穿透风险与境外诉讼防范", "legacy"),
            ("跨境电商海外知识产权侵权与临时禁令化解", "trade"),
            ("涉外继承中公证遗嘱与境外信托的法律效力冲突", "legacy"),
            ("国际海运货损索赔诉讼时效与提单免责条款破解", "trade"),
            ("海外债务人通过离岸架构转移资产的穿透追偿", "recovery"),
            ("美国特拉华州公司商业纠纷与衡平法院诉讼指南", "recovery"),
            ("新加坡国际商事法庭(SICC)争议解决与管辖权实务", "trade"),
            ("中英跨国婚姻财产分割与离岸信托资产保全", "legacy"),
            ("跨境供应链货款拖欠：离岸账户保全与破产清算联动", "recovery"),
        ]
        try:
            existing = api_request("/api/articles")
            existing_slugs = {a.get("slug") for a in existing}
            existing_titles = {a.get("title_zh") for a in existing}
        except Exception:
            existing_slugs, existing_titles = set(), set()

        chosen = None
        for t, b in topics_pool:
            t_full = f"【涉外实务】{t}：法律风险、维权路径与避坑清单"
            if t not in existing_titles and t_full not in existing_titles:
                chosen = (t, b)
                break
        if not chosen:
            chosen = (f"涉外商事争议与跨境维权要点-{int(datetime.now().timestamp())}", "general")
        topic, business = chosen

    print("\n" + f"[1/4 选题选定] 主题: {topic} (领域: {business})")

    print("[2/4 初步生成] 生成专业涉外双语内容框架...")
    art_data = generate_article_template(topic, business)

    print("[3/4 自愈优化] 执行合规词筛查、字数扩充、双语 CTA 及免责声明注入...")
    repaired, logs = repair_article(art_data)
    for log in logs:
        print(f"       [优化项] {log}")

    print("[4/4 自动发布] 向生产端 CMS 提交入库并直接发布...")
    repaired["status"] = "draft"
    create_res = api_request("/admin/api/content", data=repaired, method="POST")
    art_id = create_res["id"]
    slug = create_res["slug"]

    pub_res = api_request(f"/admin/api/content/{art_id}/publish", method="POST")
    print("\n" + f"[发布成功] 《{pub_res.get('title_zh')}》已正式发布上线 (ID: {art_id})！")
    print(f"       -> 中文地址: https://shenyuanlegal.com/articles/{slug}")
    print(f"       -> 英文地址: https://shenyuanlegal.com/en/articles/{slug}")

    print("[收录推送] 正在向 Google Indexing API 提交抓取通知...")
    notify_indexing(slug)
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
                    print(f"       -> 地址: https://shenyuanlegal.com/articles/{pub_res.get('slug')}")
                    notify_indexing(pub_res.get("slug"))
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
    parser.add_argument("--daily-run", action="store_true", help="每日综合任务（生产 2 篇新文章 + 优化发布 1 篇草稿）")
    args = parser.parse_args()

    if args.daily_run:
        print("==================================================")
        print("  深远涉外法务 — 每日 SEO 内容自动生产与发布流水线")
        print("==================================================")
        print("\n" + ">>> 步骤 1/2: 自动产出 2 篇中英双语深度实务文章...")
        produce_and_publish_new_article()
        produce_and_publish_new_article()

        print("\n" + ">>> 步骤 2/2: 自动自愈并发布 1 篇存量草稿...")
        repair_and_publish_existing_drafts(limit=1)

        print("\n" + "==================================================")
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
