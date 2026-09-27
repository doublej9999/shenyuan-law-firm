"""Public, cacheable endpoints for the country and service landing pages.

These pages were lost in the SPA rebuild; the copy now lives in
``apps.content.data.site_content`` (see that file's README for provenance).
The Nuxt frontend fetches them at request time so the HTML is server-rendered.

The payload is immutable, so the responses are cached hard at the edge.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from django.http import Http404
from ninja import Router, Schema
from ninja.responses import Response

from apps.content import site_content

router = Router(tags=["site-content"])

CACHE_HEADERS = {"Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400"}


class FaqOut(Schema):
    question: str
    answer: str


class CountrySummaryOut(Schema):
    slug: str
    name_zh: str
    name_en: str
    zh_title: str
    en_title: str


class CountryDetailOut(CountrySummaryOut):
    zh_intro: str
    en_intro: str
    items_zh: List[str]
    items_en: List[str]
    points_zh: List[str]
    points_en: List[str]
    faq_zh: List[FaqOut]
    faq_en: List[FaqOut]


class ServiceDetailOut(Schema):
    slug: str
    number: str
    zh_title: str
    en_title: str
    zh_intro: str
    en_intro: str
    items_zh: List[str]
    items_en: List[str]
    materials_zh: List[str]
    materials_en: List[str]


def _json(data: Any) -> Response:
    """JSON response with the shared edge-cache headers."""
    response = Response(data)
    for key, value in CACHE_HEADERS.items():
        response[key] = value
    return response


def _country_summary(slug: str, country: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "slug": slug,
        "name_zh": country.get("name_zh", ""),
        "name_en": country.get("name_en", ""),
        "zh_title": country.get("zh_title", ""),
        "en_title": country.get("en_title", ""),
    }


def _or_404(payload: Optional[Dict[str, Any]], slug: str, kind: str) -> Dict[str, Any]:
    if payload is None:
        raise Http404(f"unknown {kind}: {slug}")
    return payload


@router.get("/api/countries", response=List[CountrySummaryOut])
def list_countries(request):
    """Index of country landing pages, in editorial order."""
    payload = [
        _country_summary(slug, country)
        for slug, country in site_content.get_countries().items()
    ]
    return _json(payload)


@router.get("/api/countries/{slug}", response=CountryDetailOut)
def get_country(request, slug: str):
    """Full bilingual copy for one country landing page."""
    country = _or_404(site_content.get_country(slug), slug, "country")
    payload = _country_summary(slug, country)
    payload.update(
        {
            "zh_intro": country.get("zh_intro", ""),
            "en_intro": country.get("en_intro", ""),
            "items_zh": country.get("items_zh", []),
            "items_en": country.get("items_en", []),
            "points_zh": country.get("points_zh", []),
            "points_en": country.get("points_en", []),
            "faq_zh": site_content.parse_faq(country.get("faq_zh", [])),
            "faq_en": site_content.parse_faq(country.get("faq_en", [])),
        }
    )
    return _json(payload)


@router.get("/api/services", response=List[ServiceDetailOut])
def list_services(request):
    """The three service landing pages."""
    payload = [
        dict(service, slug=slug) for slug, service in site_content.get_services().items()
    ]
    return _json(payload)


@router.get("/api/services/{slug}", response=ServiceDetailOut)
def get_service(request, slug: str):
    """Full bilingual copy for one service landing page."""
    service = _or_404(site_content.get_service(slug), slug, "service")
    return _json(dict(service, slug=slug))
