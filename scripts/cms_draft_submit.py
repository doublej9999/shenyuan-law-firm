#!/usr/bin/env python3
"""Submit one bilingual Markdown article to the CMS as a draft.

The content agent writes a normal article file, runs the quality gate, then
calls this script. The script reads ADMIN_TOKEN from the repository .env and
never prints it. No Git commit or Docker deployment is performed.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def env(name: str, default: str = "") -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value
    try:
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return default

def parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("frontmatter missing")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    parts = m.group(2).split("<!-- EN -->", 1)
    if len(parts) != 2:
        raise ValueError("<!-- EN --> separator missing")
    required = ("slug", "title_zh", "title_en", "description_zh", "description_en", "business", "intent")
    missing = [k for k in required if not meta.get(k)]
    if missing:
        raise ValueError("missing frontmatter: " + ", ".join(missing))
    return {**meta, "body_zh": parts[0].strip(), "body_en": parts[1].strip()}

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: cms_draft_submit.py path/to/article.md", file=sys.stderr)
        return 2
    article = parse(Path(sys.argv[1]))
    base = env("CMS_BASE_URL", "https://shenyuanlegal.com").rstrip("/")
    token = env("ADMIN_TOKEN")
    if not token:
        print("ADMIN_TOKEN is not configured", file=sys.stderr)
        return 2
    payload = {k: article[k] for k in ("slug", "title_zh", "title_en", "description_zh", "description_en", "body_zh", "body_en", "business", "intent")}
    payload["status"] = "draft"
    req = urllib.request.Request(
        base + "/admin/api/content", data=json.dumps(payload, ensure_ascii=False).encode(), method="POST",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (compatible; ShenyuanContentFactory/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        print(f"CMS HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1
    print(json.dumps({"id": result.get("id"), "slug": result.get("slug"), "status": result.get("status")}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
