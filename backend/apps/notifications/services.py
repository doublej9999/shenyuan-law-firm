import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_intake_email(name: str, to_email: str, matter: str, language: str = "zh") -> bool:
    if not settings.RESEND_API_KEY or not to_email:
        return False
    try:
        subject = "【深远法律】咨询材料与后续跟进告知" if language == "zh" else "[Shenyuan Legal] Intake Received & Next Steps"
        body = f"""您好 {name}：

我们已收到您关于【{matter}】的法律咨询。涉外合伙人律师将在 24 小时内与您联系并评估案情。

感谢信任，
深远涉外法律服务团队"""
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.RESEND_FROM,
                "to": [to_email],
                "subject": subject,
                "text": body,
            },
            timeout=5,
        )
        return resp.status_code in (200, 201)
    except Exception as exc:
        logger.warning("Failed to send Resend email: %s", exc)
        return False

def send_lead_webhook(intake) -> bool:
    if not settings.NOTIFY_WEBHOOK_URL:
        return False
    try:
        text = (
            f"🔔 【新涉外法律咨询提醒】\n"
            f"姓名: {intake.name}\n"
            f"电话: {intake.phone or '未提供'}\n"
            f"事项: {intake.matter}\n"
            f"地区: {intake.country_or_region or '国内'}\n"
            f"简述: {intake.summary[:100]}"
        )
        resp = requests.post(
            settings.NOTIFY_WEBHOOK_URL,
            json={"msgtype": "text", "text": {"content": text}},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception as exc:
        logger.warning("Failed to push webhook notification: %s", exc)
        return False
