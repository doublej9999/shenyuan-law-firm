from typing import List, Optional
from datetime import datetime, timedelta
from ninja import Router, Schema
from django.utils import timezone
from django.db.models import Q
from apps.intakes.models import Intake, IntakeFile
from apps.notifications.services import send_intake_email, send_lead_webhook
from shenyuan_legal.auth import GlobalAdminAuth

router = Router()

class IntakeIn(Schema):
    name: str
    matter: str
    summary: str
    email: Optional[str] = None
    phone: Optional[str] = None
    country_or_region: Optional[str] = None
    language: Optional[str] = "zh"
    consent: bool = True
    source: Optional[str] = None

class IntakeOut(Schema):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    matter: str
    summary: str
    country_or_region: Optional[str] = None
    language: str
    status: str
    note: Optional[str] = None
    score: int
    source: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class IntakeUpdateIn(Schema):
    status: Optional[str] = None
    note: Optional[str] = None
    score: Optional[int] = None

class BatchDeleteIn(Schema):
    ids: List[int]

@router.post("/api/intakes", response={201: dict, 409: dict, 422: dict, 500: dict})
def create_intake(request, payload: IntakeIn):
    if not payload.consent:
        return 422, {"detail": "提交前必须同意隐私权保护政策"}

    try:
        # 24小时防重校验
        dedupe_cutoff = timezone.now() - timedelta(hours=24)
        q_filter = Q()
        if payload.phone:
            q_filter |= Q(phone=payload.phone)
        if payload.email:
            q_filter |= Q(email=payload.email)

        if q_filter and Intake.objects.filter(q_filter, created_at__gte=dedupe_cutoff).exists():
            return 409, {"detail": "您在 24 小时内已提交过咨询，我们的律师正在加紧处理，请勿重复提交"}

        # 计算初步意向分
        score = 10
        if payload.phone:
            score += 20
        if len(payload.summary) > 50:
            score += 20
        if payload.country_or_region:
            score += 10

        intake = Intake.objects.create(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            matter=payload.matter,
            summary=payload.summary,
            country_or_region=payload.country_or_region,
            language=payload.language or "zh",
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            consent_at=timezone.now(),
            score=score,
            source=payload.source,
        )

        # 异步或后台触发通知（异常捕获保护，避免未配置网络服务时抛出 500）
        try:
            if payload.email:
                send_intake_email(intake.name, intake.email, intake.matter, intake.language)
            send_lead_webhook(intake)
        except Exception:
            pass

        return 201, {"id": intake.id, "status": intake.status, "message": "咨询提交成功，律师将尽快与您联系"}
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return 500, {"detail": f"服务器内部错误: {str(exc)}"}

@router.post("/api/intakes/chat", response={201: dict})
def create_chat_intake(request, payload: IntakeIn):
    return create_intake(request, payload)

@router.get("/admin/api/intakes", response=List[IntakeOut], auth=GlobalAdminAuth())
def list_intakes(
    request,
    status: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    qs = Intake.objects.all()
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q) | Q(summary__icontains=q))
    return list(qs[offset : offset + limit])

# 注意：静态路径必须注册在 {intake_id} 动态路径之前。
# 否则 /admin/api/intakes/batch-delete 会被解析为 intake_id="batch-delete"，
# 命中 PATCH/DELETE 路由后返回 405 Method Not Allowed。
@router.post("/admin/api/intakes/batch-delete", response={200: dict}, auth=GlobalAdminAuth())
def batch_delete_intakes(request, payload: BatchDeleteIn):
    if not payload.ids:
        return 200, {"success": True, "deleted_count": 0, "message": "未指定要删除的记录"}
    count, _ = Intake.objects.filter(id__in=payload.ids).delete()
    return 200, {"success": True, "deleted_count": count, "message": f"成功删除 {count} 条客户档案"}

@router.patch("/admin/api/intakes/{intake_id}", response={200: IntakeOut, 404: dict}, auth=GlobalAdminAuth())
def update_intake(request, intake_id: int, payload: IntakeUpdateIn):
    try:
        intake = Intake.objects.get(id=intake_id)
    except Intake.DoesNotExist:
        return 404, {"detail": "Intake not found"}

    if payload.status:
        intake.status = payload.status
    if payload.note is not None:
        intake.note = payload.note
    if payload.score is not None:
        intake.score = payload.score
    intake.save()
    return intake

@router.delete("/admin/api/intakes/{intake_id}", response={200: dict, 404: dict}, auth=GlobalAdminAuth())
def delete_intake(request, intake_id: int):
    try:
        intake = Intake.objects.get(id=intake_id)
        intake.delete()
        return 200, {"success": True, "message": "线索及客户档案已删除"}
    except Intake.DoesNotExist:
        return 404, {"detail": "Intake not found"}

@router.get("/admin/api/stats", auth=GlobalAdminAuth())
def get_stats(request):
    total = Intake.objects.count()
    new_count = Intake.objects.filter(status="new").count()
    contacted = Intake.objects.filter(status="contacted").count()
    processing = Intake.objects.filter(status="processing").count()
    closed = Intake.objects.filter(status="closed").count()
    return {
        "total": total,
        "new": new_count,
        "contacted": contacted,
        "processing": processing,
        "closed": closed,
    }
