import json
from django.test import TestCase, Client
from django.utils import timezone
from apps.content.models import ContentArticle
from apps.content.seo_service import generate_sitemap_xml, generate_robots_txt, render_article_seo_html
from apps.content.quality_gate_service import evaluate_article_quality
from apps.content.generator_service import generate_article_pipeline
from apps.content.topic_service import get_suggested_topics

class ContentAndSeoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.article = ContentArticle.objects.create(
            slug="test-cross-border-enforcement-case",
            title_zh="涉外判决跨境认可与执行实务要点",
            title_en="Practical Points on Cross-Border Enforcement of Judgments",
            description_zh="深度解析涉外生效判决在境外的认可与执行实务流程与财产查控技巧。",
            description_en="In-depth analysis of cross-border recognition and enforcement of court judgments.",
            body_zh="# 涉外判决跨境认可与执行实务要点\n\n债务人在境外隐匿资产是当前追索的主要难点。通过离岸穿透与司法互认可有效推进。\n\n[免费咨询 →](/#intake)\n\n免责声明：本文不构成法律意见。",
            body_en="# Practical Points\n\nCross-border enforcement requires procedural precision.\n\n[Free consultation →](/#intake)\n\nLegal Disclaimer: Not legal advice.",
            business="recovery",
            intent="I",
            status="published",
            published_at=timezone.now(),
        )

    def test_sitemap_generation(self):
        xml = generate_sitemap_xml()
        self.assertIn("<urlset", xml)
        self.assertIn("https://shenyuanlegal.com/articles/test-cross-border-enforcement-case", xml)
        self.assertIn("https://shenyuanlegal.com/en/articles/test-cross-border-enforcement-case", xml)
        self.assertIn("xhtml:link", xml)

    def test_robots_generation(self):
        robots = generate_robots_txt()
        self.assertIn("User-agent: *", robots)
        self.assertIn("Sitemap: https://shenyuanlegal.com/sitemap.xml", robots)

    def test_quality_gate(self):
        # 正常文章评分测试
        payload = {
            "slug": "sample-slug-test",
            "title_zh": "涉外合同违约赔偿与国际海运争议处理",
            "title_en": "Breach of Cross-Border Trade Contract and Remedies",
            "description_zh": "针对跨国贸易违约及海运纠纷的索赔流程与风险控制指南，提供实务维权步骤分析。",
            "description_en": "Comprehensive legal guidance for international trade breach and logistics dispute claims.",
            "body_zh": "关于涉外贸易违约与货款追偿的实务指引，正文必须包含核心业务分析与法务步骤。" * 15 + "\n\n[免费咨询 →](/#intake)\n\n免责声明：本文仅供参考，不构成正式法律意见。",
            "body_en": "Practical legal analysis for cross-border trade disputes." * 20 + "\n\n[Free consultation →](/#intake)\n\nLegal Disclaimer: Not legal advice.",
            "business": "trade",
        }
        res = evaluate_article_quality(payload)
        self.assertTrue(res["passed"])
        self.assertGreaterEqual(res["score"], 80)

        # 包含违规夸大胜诉词的惩罚检测
        payload_risk = dict(payload, title_zh="100%胜诉包打赢合同追索")
        res_risk = evaluate_article_quality(payload_risk)
        self.assertFalse(res_risk["passed"])
        self.assertTrue(any("绝对化用语" in issue for issue in res_risk["issues"]))

    def test_article_pipeline_generation(self):
        res = generate_article_pipeline("外贸跨境货代提单扣货", "trade")
        self.assertIn("article", res)
        self.assertIn("quality", res)
        self.assertTrue(res["article"]["title_zh"])
        self.assertTrue(res["article"]["body_zh"])
        self.assertIn("[免费咨询 →](/#intake)", res["article"]["body_zh"])

    def test_suggested_topics(self):
        topics = get_suggested_topics()
        self.assertIsInstance(topics, list)
        self.assertGreater(len(topics), 0)

    def test_public_views(self):
        # Sitemap
        r_sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(r_sitemap.status_code, 200)
        self.assertEqual(r_sitemap["Content-Type"], "application/xml; charset=utf-8")

        # Robots
        r_robots = self.client.get("/robots.txt")
        self.assertEqual(r_robots.status_code, 200)

        # 爬虫直出 HTML
        r_html_zh = self.client.get(f"/articles/{self.article.slug}")
        self.assertEqual(r_html_zh.status_code, 200)
        self.assertIn("涉外判决跨境认可与执行实务要点", r_html_zh.content.decode("utf-8"))
        self.assertIn("schema.org", r_html_zh.content.decode("utf-8"))

        r_html_en = self.client.get(f"/en/articles/{self.article.slug}")
        self.assertEqual(r_html_en.status_code, 200)
        self.assertIn("Practical Points", r_html_en.content.decode("utf-8"))
