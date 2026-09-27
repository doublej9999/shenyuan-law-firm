"""Typed access to the frozen bilingual site content.

The country landing pages, the service landing pages and the matter metadata
used to live only in the legacy FastAPI monolith (``app/main.py``). When the
site was rebuilt as a Vue SPA those pages disappeared from the public site, so
their copy was recovered into :mod:`apps.content.data.site_content`.

The JSON file is the single source of truth until the copy moves into the CMS.
Nothing here touches the database, so it is safe to call from the sitemap,
``llms.txt`` and the public API at any time.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_PATH = Path(__file__).resolve().parent / "data" / "site_content.json"


@lru_cache(maxsize=1)
def _payload() -> Dict[str, Any]:
    """Load (once) and cache the frozen content payload."""
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_countries() -> Dict[str, Dict[str, Any]]:
    """Country landing pages keyed by slug, in their original display order."""
    return _payload()["countries"]


def get_country(slug: str) -> Optional[Dict[str, Any]]:
    return get_countries().get(slug)


def get_services() -> Dict[str, Dict[str, Any]]:
    """Service landing pages keyed by slug (``trade`` / ``recovery`` / ``legacy``)."""
    return _payload()["services"]


def get_service(slug: str) -> Optional[Dict[str, Any]]:
    return get_services().get(slug)


def get_business_labels() -> Dict[str, List[str]]:
    """``business`` code -> ``[zh_label, en_label]``."""
    return _payload()["business_labels"]


def get_matter_meta() -> Dict[str, Dict[str, Any]]:
    return _payload()["matter_meta"]


def get_materials_by_matter() -> Dict[str, List[str]]:
    return _payload()["materials_by_matter"]


def get_faq_group_labels() -> Dict[str, List[str]]:
    return _payload()["faq_group_labels"]


def get_case_business_labels() -> Dict[str, List[str]]:
    return _payload()["case_business_labels"]


def parse_faq(pairs: List[str]) -> List[Dict[str, str]]:
    """Split legacy ``"question|answer"`` strings into structured FAQ entries.

    The legacy templates stored FAQ copy as single strings joined by a pipe so
    they could be swapped wholesale for the English variant. Anything without a
    separator is treated as a question with an empty answer rather than being
    dropped, so a malformed entry stays visible during review.
    """
    entries: List[Dict[str, str]] = []
    for raw in pairs or []:
        question, sep, answer = raw.partition("|")
        entries.append({"question": question.strip(), "answer": answer.strip() if sep else ""})
    return entries
