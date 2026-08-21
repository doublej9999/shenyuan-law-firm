#!/usr/bin/env python3
"""Bump article dates to trigger Google re-crawl.

Reads all published articles, randomises their frontmatter date to within
the past N days, and writes them back. Run once; the changed files are then
deployed, sitemap lastmod updates, and Google notices freshness.

Usage:
  python3 scripts/bump_dates.py [--max-days 14] [--dry-run]
Default: 14 days (articles get a random date from today-14 to today).
"""

import random
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "content" / "articles"


def main() -> int:
    max_days = 14
    dry = "--dry-run" in sys.argv
    for a in sys.argv[1:]:
        if a.startswith("--max-days="):
            max_days = int(a.split("=", 1)[1])
    today = datetime.now(timezone.utc).date()
    changed = 0
    for idx in sorted(ARTICLES.glob("*/index.md")):
        text = idx.read_text(encoding="utf-8")
        m = re.search(r"^date: (\d{4}-\d{2}-\d{2})", text, re.M)
        if not m:
            continue
        old = m.group(1)
        offset = random.randint(0, max_days)
        new = (today - timedelta(days=offset)).isoformat()
        if new == old:
            continue
        if not dry:
            idx.write_text(text.replace(f"date: {old}", f"date: {new}", 1), encoding="utf-8")
        changed += 1
        print(f"{'[DRY] ' if dry else ''}{idx.parent.name}: {old} -> {new}")
    print(f"\n结论：{changed} 篇日期已更新{'（dry-run）' if dry else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())