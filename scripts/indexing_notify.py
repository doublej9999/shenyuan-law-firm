#!/usr/bin/env python3
"""通知 Google Indexing API 收录新页面（发布后调用）。

前置条件（一次性，需用户操作）：
  1. GCP 启用 "Indexing API"（console.cloud.google.com -> APIs & Services）
  2. service account 的 JSON（GSC_SERVICE_ACCOUNT_JSON，与 gsc_report 共用）
  3. service account 邮箱加入 GSC 属性用户（owner/full）——如已配 GSC 则已完成
配额：每页每 30 天最多通知一次；每天总量约 200 条（新站够用）。

用法：
  python3 scripts/indexing_notify.py URL [URL...]
  python3 scripts/indexing_notify.py $(git diff --name-only HEAD~1 | grep articles | sed 's|content/articles/\([^/]*\)/index.md|https://shenyuanlegal.com/articles/\1|')

退出码：0 全部成功；1 有失败（打印详情）。
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def _env(name: str, default: str = "") -> str:
    val = os.environ.get(name, "").strip()
    if val:
        return val
    try:
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return default


def _token() -> str | None:
    path = _env("GSC_SERVICE_ACCOUNT_JSON").strip()
    if not path or not Path(path).exists():
        return None
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_file(
            path, scopes=["https://www.googleapis.com/auth/indexing"])
        creds.refresh(Request())
        return creds.token
    except Exception as exc:
        print(f"auth 失败: {exc}", file=sys.stderr)
        return None


def notify(url: str, token: str) -> str | None:
    body = json.dumps({"url": url, "type": "URL_UPDATED"}).encode("utf-8")
    req = urllib.request.Request(
        API, data=body, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        return f"HTTP {exc.code}: {detail}"
    except Exception as exc:
        return str(exc)


def main() -> int:
    urls = [u for u in sys.argv[1:] if u.startswith("http")]
    if not urls:
        print("用法：python3 scripts/indexing_notify.py URL [URL...]", file=sys.stderr)
        return 2
    token = _token()
    if not token:
        print("未配置 GSC_SERVICE_ACCOUNT_JSON 或认证失败——请先完成 GCP Indexing API 开通 + service account 配置。", file=sys.stderr)
        return 2
    failed = 0
    for url in urls:
        err = notify(url, token)
        if err:
            failed += 1
            print(f"❌ {url}: {err}")
        else:
            print(f"✅ {url} 已通知收录")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
