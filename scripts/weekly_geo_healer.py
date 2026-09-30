#!/usr/bin/env python3
"""
深远律所官网 · 高商业意图（High-Intent）未收录与排名落后文章「自动微调自愈」脚本。
通过 GSC 官方接口筛选出排名在 15~60 位之间或曝光但零点击的潜力文章，
针对性检查并补齐权威条约法条、优化 Description 引导钩子，并重新报送 IndexNow / Google。
"""

import sys
import os
import json
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.batch_translate_multilingual import api_request
from scripts.geo_full_audit import GSC_SECRETS_PATH


def query_opportunity_pages() -> list[dict]:
    """通过 GSC 寻找具备曝光机会、但排名在 15~60 之间的潜力页面"""
    if not os.path.exists(GSC_SECRETS_PATH):
        print("⚠️ 未找到 GSC 密钥文件，跳过 GSC 智能筛选。")
        return []

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        creds = service_account.Credentials.from_service_account_file(
            GSC_SECRETS_PATH,
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        service = build('searchconsole', 'v1', credentials=creds)
        
        today = date.today()
        start_date = (today - timedelta(days=14)).isoformat()
        end_date = (today - timedelta(days=1)).isoformat()
        
        res = service.searchanalytics().query(
            siteUrl='sc-domain:shenyuanlegal.com',
            body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['page'],
                'rowLimit': 100
            }
        ).execute()

        rows = res.get('rows', [])
        opportunities = []
        for r in rows:
            url = r.get('keys', [''])[0]
            pos = r.get('position', 0)
            imp = r.get('impressions', 0)
            clicks = r.get('clicks', 0)
            # 筛选：文章页 + 排名处于第 2~6 页 (15~60名) 或有曝光但零点击
            if '/articles/' in url and (15 <= pos <= 60 or (imp >= 3 and clicks == 0)):
                slug = url.rstrip('/').split('/')[-1]
                opportunities.append({
                    "url": url,
                    "slug": slug,
                    "position": round(pos, 1),
                    "impressions": imp,
                    "clicks": clicks
                })
        return opportunities
    except Exception as e:
        print(f"⚠️ GSC 机会词拉取异常: {e}")
        return []


def heal_article(art: dict) -> bool:
    """自愈长文：确保 Description 吸引力，注入时效与维权红线"""
    art_id = art["id"]
    slug = art.get("slug", "")
    desc = art.get("description_zh", "")
    body = art.get("body_zh", "")
    changed = False

    # 1. 如果描述过短或平淡，优化为带有诱因与解决指引的文案
    if desc and "评估" not in desc and "时效" not in desc and len(desc) < 140:
        art["description_zh"] = desc.rstrip("。") + "。遇到类似涉外商事争议或跨国债务，建议第一时间固定原件证据并核验诉讼时效，避免超过权利保护期；深远涉外律师团队支持中英双语快速评估。"
        changed = True

    # 2. 如果正文缺少诉讼时效或公约提醒，追加权威注记
    if "诉讼时效" not in body and "时效" not in body:
        notice = "\n\n> ⚖️ **涉外法律实务与时效要点提示**：跨国贸易与国际商事追收案件中，不同法域诉讼时效差异巨大（通常在 1~6 年之间）。若对方已出现经营恶化或恶意失联迹象，应及早启动正式涉外律师函中断时效并展开财产调查，切勿因无序协商错过法定追偿窗口。\n"
        art["body_zh"] = body + notice
        changed = True

    if changed:
        try:
            api_request(f"/admin/api/content/{art_id}", data=art, method="PUT")
            print(f"  ✅ 文章 #{art_id} ({slug}) 事实与诱因已增强并写回！")
            # 报送搜索引擎
            api_request(f"/admin/api/content/{art_id}/notify-indexing", method="POST")
            print(f"  🚀 触发 Google Indexing / IndexNow 重新收录报送。")
            return True
        except Exception as e:
            print(f"  ❌ 回写自愈内容失败 #{art_id}: {e}")
            return False
    return False


def run_weekly_geo_heal(limit: int = 3):
    print("=" * 65)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 启动高商业意图长尾文章 SEO/GEO 自动微调自愈任务...")
    print("=" * 65)

    opportunities = query_opportunity_pages()
    print(f"从 GSC 检索到 {len(opportunities)} 篇处于提升窗口期的潜力长文")

    articles = api_request("/admin/api/content?status=published")
    art_map = {a["slug"]: a for a in articles}

    healed_count = 0
    # 优先自愈曝光高的潜力文章
    sorted_opps = sorted(opportunities, key=lambda x: x["impressions"], reverse=True)

    for opp in sorted_opps[:limit]:
        slug = opp["slug"]
        art = art_map.get(slug)
        if not art:
            continue
        print(f"\n🎯 诊断机会文章: {slug} (当前排名: {opp['position']}, 曝光: {opp['impressions']})")
        if heal_article(art):
            healed_count += 1
            time.sleep(2)

    # 如果 GSC 暂无足够条目，默认挑选未自愈过的存量文章巡检
    if healed_count == 0 and len(articles) > 0:
        print("\n🔍 扫描存量文章中缺少时效提示的长文进行防御性加固...")
        for a in articles:
            if "诉讼时效" not in a.get("body_zh", ""):
                print(f"🎯 选定待强化文章: #{a['id']} ({a.get('slug')})")
                if heal_article(a):
                    healed_count += 1
                    if healed_count >= limit:
                        break
                time.sleep(2)

    print("\n" + "=" * 65)
    print(f"本轮自愈完毕：成功微调加固 {healed_count} 篇潜力文章！")
    print("=" * 65)


if __name__ == "__main__":
    max_heal = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_weekly_geo_heal(max_heal)
