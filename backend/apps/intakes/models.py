from django.db import models

class Intake(models.Model):
    STATUS_CHOICES = [
        ("new", "新线索"),
        ("contacted", "已联系"),
        ("processing", "处理中"),
        ("closed", "已结案"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    matter = models.CharField(max_length=50)
    summary = models.TextField()
    country_or_region = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=10, default="zh")
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    note = models.TextField(blank=True, null=True)
    consent_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    source = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "intakes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.matter} ({self.status})"

class IntakeFile(models.Model):
    intake = models.ForeignKey(Intake, on_delete=models.CASCADE, related_name="files")
    original_name = models.CharField(max_length=255)
    storage_path = models.CharField(max_length=500)
    size = models.BigIntegerField()
    content_type = models.CharField(max_length=100, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "intake_files"
