from django.db import models

class ContentArticle(models.Model):
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("reviewing", "待审核"),
        ("published", "已发布"),
        ("archived", "已下线"),
    ]

    slug = models.SlugField(max_length=200, unique=True)
    title_zh = models.CharField(max_length=255, default="")
    title_en = models.CharField(max_length=255, default="", blank=True)
    description_zh = models.TextField(default="", blank=True)
    description_en = models.TextField(default="", blank=True)
    body_zh = models.TextField(default="", blank=True)
    body_en = models.TextField(default="", blank=True)
    business = models.CharField(max_length=50, default="general")
    intent = models.CharField(max_length=10, default="I")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "content_articles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title_zh or self.slug} ({self.status})"

class ArticleVersion(models.Model):
    article = models.ForeignKey(ContentArticle, on_delete=models.CASCADE, related_name="versions")
    version = models.IntegerField()
    snapshot = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content_article_versions"
        unique_together = ("article", "version")
        ordering = ["-version"]
