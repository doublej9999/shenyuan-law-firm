#!/usr/bin/env python3
"""Google Search Console performance puller (service-account auth).

GSC API does NOT accept API keys — it requires OAuth2 credentials that
assert a principal. The standard headless/cron-friendly path is a Google
Cloud **service account**:

  1. console.cloud.google.com -> IAM & Admin -> Service Accounts -> Create
  2. Keys -> Add Key -> JSON (download; store on this server)
  3. search.google.com/search-console -> Settings -> Users and permissions
     -> add the service-account email (e.g. xxx@yyy.iam.gserviceaccount.com)
     as OWNER or FULL
  4. Point GSC_SERVICE_ACCOUNT_JSON at the JSON file

Config:
  GSC_SERVICE_ACCOUNT_JSON  required path to the service-account JSON
  GSC_SITE_URL              default https://shenyuanlegal.com/

Output: a markdown section (7-day clicks/impressions/CTR/position + top
queries). Prints nothing when unconfigured or on failure, so callers
(weekly/monthly reports) degrade gracefully.

Requires: pip install google-auth  (not google-api-python-client)
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
API = "https://searchconsole.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"


def _access_token() -> str | None:
    path = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if not path or not Path(path).exists():
        return None
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(path, scopes=[SCOPE])
        creds.refresh(Request())
        return creds.token
    except Exception:
        print("gsc: auth failed", file=sys.stderr)
        return None


def _query(token: str, site: str, start: str, end: str, dimensions: list[str],
           row_limit: int = 0) -> list[dict]:
    body = {"startDate": start, "endDate": end, "dimensions": dimensions}
    if row_limit:
        body["rowLimit"] = row_limit
    req = urllib.request.Request(
        API.format(site=urllib.parse.quote(site, safe="")),
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("rows", [])


def fetch(days: int = 7) -> str:
    token = _access_token()
    if not token:
        return ""
    site = os.environ.get("GSC_SITE_URL", "https://shenyuanlegal.com/").strip()
    end = datetime.now(timezone.utc) - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    try:
        daily = _query(token, site, s, e, ["date"])
        top = _query(token, site, s, e, ["query"], row_limit=5)
    except Exception as exc:
        print(f"gsc: query failed: {exc}", file=sys.stderr)
        return ""

    clicks = sum(r.get("clicks", 0) for r in daily)
    impr = sum(r.get("impressions", 0) for r in daily)
    ctr = clicks / impr * 100 if impr else 0.0
    pos = (
        sum(r.get("position", 0) * r.get("impressions", 0) for r in daily) / impr
        if impr
        else 0.0
    )

    lines = [f"## 🔍 Google 搜索表现（近 {days} 天）"]
    lines.append(f"- 点击 **{clicks}** · 展示 **{impr}** · CTR **{ctr:.1f}%** · 平均排名 **{pos:.1f}**")
    if top:
        lines.append("- 热门查询：")
        for r in top:
            q = r.get("keys", ["?"])[0]
            lines.append(
                f"  - 「{q}」点击 {r.get('clicks', 0)} · 展示 {r.get('impressions', 0)} · "
                f"排名 {r.get('position', 0):.1f}"
            )
    else:
        lines.append("- 近 7 天无搜索展示数据（新站正常，等收录爬升）")
    return "\n".join(lines)


if __name__ == "__main__":
    out = fetch(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    if out:
        print(out)
