from django.db import models

class AuditLog(models.Model):
    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    action = models.CharField(max_length=100)
    detail = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-ts"]

class PageView(models.Model):
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "page_views"
        ordering = ["-viewed_at"]

class SearchLog(models.Model):
    q = models.CharField(max_length=255, db_index=True)
    results = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "search_log"
        ordering = ["-created_at"]
