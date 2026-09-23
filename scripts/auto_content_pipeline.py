#!/usr/bin/env python3
"""全自动 CMS 内容生产与排产发布流水线脚本。

功能：
  1. 自动从选题引擎获取最高潜力的机会长尾词/搜索缺口选题；
  2. 自动通过涉外法务生成引擎创作双语专业文章（Markdown、Frontmatter、FAQ）；
  3. 执行严格的 SEO 质量门禁校验（评分 ≥ 80 通过）；
  4. 提交保存至 CMS 数据库，若带 --publish 参数则自动发布并推送搜索引擎收录。

用法：
  python scripts/auto_content_pipeline.py                    # 自动产出一篇草稿
  python scripts/auto_content_pipeline.py --publish          # 自动产出并直接发布上线
  python scripts/auto_content_pipeline.py --topic "外贸诈骗" --biz trade
"""

import argparse
import os
import sys
from pathlib import Path

# 防止 Windows 控制台在输出特殊字符时报编码错误
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 配置 Django 环境路径
ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shenyuan_legal.settings")

import django
django.setup()

from apps.content.models import ContentArticle, ArticleVersion
from apps.content.topic_service import get_suggested_topics
from apps.content.generator_service import generate_article_pipeline
from apps.content.seo_service import notify_search_engines
from django.utils import timezone

def main():
    parser = argparse.ArgumentParser(description="CMS 自动化生成与发布流水线")
    parser.add_argument("--topic", type=str, default="", help="指定文章主题（若为空则自动选取推荐选题）")
    parser.add_argument("--biz", type=str, default="general", help="业务线: trade / recovery / legacy / general")
    parser.add_argument("--publish", action="store_true", help="是否直接发布上线并通知搜索引擎收录")
    args = parser.parse_args()

    topic = args.topic.strip()
    business = args.biz.strip()

    if not topic:
        suggestions = get_suggested_topics()
        if not suggestions:
            print("[INFO] 当前暂无待生产的推荐选题，请手动指定 --topic。")
            return 0
        chosen = suggestions[0]
        topic = chosen["topic"]
        business = chosen.get("business", "general")
        print(f"[1/4 选题确定] 自动选定推荐主题: {topic} (领域: {business})")
    else:
        print(f"[1/4 选题确定] 指定主题: {topic} (领域: {business})")

    # 2. 调用生成引擎
    print("[2/4 AI 生成] 正在结合涉外法务知识库生成中英双语正文与 SEO 结构化数据...")
    pipeline_res = generate_article_pipeline(topic=topic, business=business)
    article_data = pipeline_res["article"]
    quality = pipeline_res["quality"]

    print(f"       -> 标题(中): {article_data['title_zh']}")
    print(f"       -> 标题(英): {article_data['title_en']}")
    print(f"       -> 路径 Slug: {article_data['slug']}")

    # 3. 质量门禁检查
    print(f"[3/4 质量门禁] 综合评分: {quality['score']}/100 | 是否通过: {quality['passed']}")
    if quality["issues"]:
        print(f"       [问题项] {', '.join(quality['issues'])}")
    if quality["warnings"]:
        print(f"       [优化建议] {', '.join(quality['warnings'])}")

    if not quality["passed"] and quality["score"] < 60:
        print("[ERROR] 质量门禁未通过且低于安全基线，终止落库。")
        return 1

    # 4. 数据落库
    status = "published" if args.publish else "draft"
    published_at = timezone.now() if args.publish else None

    # 防重检查
    slug = article_data["slug"]
    counter = 1
    orig_slug = slug
    while ContentArticle.objects.filter(slug=slug).exists():
        slug = f"{orig_slug}-{counter}"
        counter += 1
    article_data["slug"] = slug

    article = ContentArticle.objects.create(
        slug=slug,
        title_zh=article_data["title_zh"],
        title_en=article_data.get("title_en", ""),
        description_zh=article_data.get("description_zh", ""),
        description_en=article_data.get("description_en", ""),
        body_zh=article_data.get("body_zh", ""),
        body_en=article_data.get("body_en", ""),
        business=article_data.get("business", business),
        intent=article_data.get("intent", "I"),
        status=status,
        published_at=published_at,
    )

    ArticleVersion.objects.create(
        article=article,
        version=1,
        snapshot=article_data,
    )
    print(f"[4/4 存储完成] 文章已入库 (ID: {article.id}, 状态: {status})")

    # 5. 如果是发布状态，联动触发搜索引擎收录通知
    if args.publish:
        print("[收录推送] 触发主动推送通知网络...")
        results = notify_search_engines(article.slug)
        print(f"          Google: {results['google']['status']}")
        print(f"          百度: {results['baidu']['status']}")
        print(f"          IndexNow: {results['indexnow']['status']}")

    print("\n[OK] 流水线执行成功！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
