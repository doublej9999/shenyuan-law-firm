from typing import List
from ninja import Router, Schema
from shenyuan_legal.auth import GlobalAdminAuth

router = Router()

class MarketingBundle(Schema):
    topic: str
    target_audience: str
    wechat_post: str
    linkedin_post: str
    suggested_tags: List[str]

@router.get("/admin/api/marketing/generate", response=MarketingBundle, auth=GlobalAdminAuth())
def generate_marketing(request, topic: str):
    return MarketingBundle(
        topic=topic,
        target_audience="出海中企创始人、外商投资法务总监、跨境高净值人士",
        wechat_post=(
            f"【涉外法务精要】{topic}\n\n"
            f"随着跨国经贸合作与海外合规审查日趋严格，企业在落地与争议解决过程中面临全新合规挑战。"
            f"深远涉外律师团队梳理了核心实务要点与操作避坑清单，助您稳健出海！"
        ),
        linkedin_post=(
            f"Navigating cross-border legal challenges: {topic}.\n"
            f"Our team at Shenyuan Law Firm highlights critical compliance factors for multinational businesses and foreign investors. Feel free to connect or reach out for legal insights."
        ),
        suggested_tags=["#涉外法律", "#跨境合规", "#中国法", "#CrossBorderLaw", "#ShenyuanLegal"],
    )
