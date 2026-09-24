import json
import os
from pathlib import Path
from unittest import mock

from django.test import TestCase, Client
from django.utils import timezone
from apps.content import site_content
from apps.content.models import ContentArticle
from apps.content.seo_service import (
    frontend_routes,
    generate_llms_txt,
    generate_robots_txt,
    generate_sitemap_xml,
    render_article_seo_html,
)
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


class FrozenSiteContentTests(TestCase):
    """The country/service copy recovered from the legacy monolith."""

    def test_expected_coverage(self):
        self.assertEqual(len(site_content.get_countries()), 22)
        self.assertEqual(set(site_content.get_services()), {"trade", "recovery", "legacy"})

    def test_every_country_has_bilingual_copy(self):
        for slug, country in site_content.get_countries().items():
            with self.subTest(slug=slug):
                for field in ("name_zh", "name_en", "zh_title", "en_title", "zh_intro", "en_intro"):
                    self.assertTrue(country.get(field), f"{slug}.{field} is empty")
                self.assertEqual(len(country["faq_zh"]), len(country["faq_en"]))
                self.assertTrue(country["items_zh"] and country["items_en"])

    def test_parse_faq_splits_on_pipe(self):
        entries = site_content.parse_faq(["问？|答。", "没有分隔符"])
        self.assertEqual(entries[0], {"question": "问？", "answer": "答。"})
        self.assertEqual(entries[1], {"question": "没有分隔符", "answer": ""})


class SiteContentApiTests(TestCase):
    def test_country_index(self):
        r = self.client.get("/api/countries")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data), 22)
        self.assertEqual(data[0]["slug"], "united-states")
        self.assertIn("s-maxage", r["Cache-Control"])

    def test_country_detail_parses_faq(self):
        r = self.client.get("/api/countries/singapore")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["name_zh"], "新加坡")
        self.assertTrue(data["faq_zh"])
        self.assertIn("question", data["faq_zh"][0])
        self.assertIn("answer", data["faq_zh"][0])
        self.assertNotIn("|", data["faq_zh"][0]["question"])

    def test_unknown_country_is_404(self):
        self.assertEqual(self.client.get("/api/countries/atlantis").status_code, 404)

    def test_services(self):
        r = self.client.get("/api/services")
        self.assertEqual(r.status_code, 200)
        slugs = [s["slug"] for s in r.json()]
        self.assertEqual(slugs, ["trade", "recovery", "legacy"])

        detail = self.client.get("/api/services/trade").json()
        self.assertEqual(detail["zh_title"], "国际贸易争议")
        self.assertTrue(detail["materials_zh"])


class SitemapAndDiscoveryTests(TestCase):
    def setUp(self):
        self.article = ContentArticle.objects.create(
            slug="x-default-probe",
            title_zh="测试文章",
            title_en="Probe article",
            description_zh="描述",
            description_en="Description",
            body_zh="# 标题\n\n正文",
            body_en="# Heading\n\nBody",
            business="trade",
            intent="I",
            status="published",
            published_at=timezone.now(),
        )

    def test_every_sitemap_url_has_x_default(self):
        xml = generate_sitemap_xml()
        self.assertIn('hreflang="x-default"', xml)
        # One x-default per <loc> — a pair is emitted as two <url> entries.
        self.assertEqual(xml.count('hreflang="x-default"'), xml.count("<loc>"))

    def test_sitemap_covers_every_shipped_page_family(self):
        """Country and service landing pages now ship, so they are advertised."""
        xml = generate_sitemap_xml()
        self.assertIn("https://shenyuanlegal.com/countries", xml)
        self.assertIn("https://shenyuanlegal.com/countries/united-states", xml)
        self.assertIn("https://shenyuanlegal.com/services/trade", xml)
        self.assertIn("https://shenyuanlegal.com/en/services/legacy", xml)
        self.assertEqual(xml.count("<loc>"), xml.count('hreflang="x-default"'))

    def test_sitemap_omits_families_pulled_by_the_override(self):
        """A sitemap must never advertise a page the frontend does not serve."""
        with mock.patch.dict(os.environ, {"SITEMAP_ROUTE_FAMILIES": "core,articles"}):
            xml = generate_sitemap_xml()
        self.assertNotIn("/countries/", xml)
        self.assertNotIn("/services/trade", xml)
        self.assertIn("https://shenyuanlegal.com/articles/x-default-probe", xml)

    def test_every_sitemap_page_family_has_a_frontend_route(self):
        """Keep ``SITEMAP_ROUTE_FAMILIES`` in lockstep with ``frontend-web/pages``.

        The gate is only honest if the pages it enables actually exist; enabling
        a family without shipping its pages puts 404s in front of crawlers.
        """
        pages = Path(__file__).resolve().parents[3] / "frontend-web" / "pages"
        if not pages.is_dir():
            self.skipTest("frontend-web is not part of this checkout")

        def is_served(path: str) -> bool:
            rel = path.strip("/")
            if not rel:
                return (pages / "index.vue").is_file()
            target = pages / rel
            return any(
                candidate.is_file()
                for candidate in (
                    target.with_suffix(".vue"),  # /services -> services.vue
                    target / "index.vue",  # /countries -> countries/index.vue
                    target.parent / "[slug].vue",  # /services/trade -> services/[slug].vue
                )
            )

        for route in frontend_routes():
            for path in (route["zh"], route["en"]):
                with self.subTest(path=path):
                    self.assertTrue(
                        is_served(path),
                        f"{path} is advertised in the sitemap but has no page in frontend-web/pages",
                    )

    def test_robots_welcomes_ai_and_chinese_crawlers(self):
        robots = generate_robots_txt()
        for agent in ("GPTBot", "ClaudeBot", "PerplexityBot", "Baiduspider", "Sogou web spider"):
            self.assertIn(agent, robots)
        self.assertIn("Disallow: /api/", robots)
        self.assertIn("LLMtxt: https://shenyuanlegal.com/llms.txt", robots)

    def test_llms_txt_is_served_and_lists_the_whole_site(self):
        r = self.client.get("/llms.txt")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "text/plain; charset=utf-8")
        body = r.content.decode("utf-8")
        self.assertTrue(body.startswith("# "))
        self.assertIn("/services/trade", body)
        self.assertIn("/countries/united-states", body)
        self.assertIn("/articles/x-default-probe", body)

    def test_article_html_carries_breadcrumb_and_x_default(self):
        html = render_article_seo_html(self.article, is_en=False)
        self.assertIn('"@type": "BreadcrumbList"', html)
        self.assertIn('hreflang="x-default"', html)
        self.assertIn('"inLanguage": "zh-CN"', html)
        # No og:image until a real social card is shipped.
        self.assertNotIn("og:image", html)

    def test_markdown_renders_links_and_lists(self):
        self.article.body_zh = "## 标题\n\n- 第一项\n- 第二项\n\n[免费咨询](/#intake)\n\n**加粗**"
        html = render_article_seo_html(self.article, is_en=False)
        self.assertIn("<ul>", html)
        self.assertIn("<li>第一项</li>", html)
        self.assertIn('<a href="https://shenyuanlegal.com/#intake">免费咨询</a>', html)
        self.assertIn("<strong>加粗</strong>", html)
