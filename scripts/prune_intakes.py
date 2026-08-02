#!/usr/bin/env python3
"""Delete intakes (and their uploaded files) older than N days.

Destructive by design: requires --older-than DAYS plus --yes to run, or
--dry-run to preview what would be deleted. Every deletion is recorded in
the audit_log table.

Examples:
    python scripts/prune_intakes.py --older-than 365 --dry-run
    python scripts/prune_intakes.py --older-than 365 --yes
"""

import argparse
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import app.main as m  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--older-than", type=int, required=True, metavar="DAYS")
    parser.add_argument("--dry-run", action="store_true", help="preview only, delete nothing")
    parser.add_argument("--yes", action="store_true", help="confirm deletion")
    args = parser.parse_args()

    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.older_than)).isoformat()
    with m.db_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, email, created_at FROM intakes WHERE created_at < ?",
            (cutoff,),
        ).fetchall()

    if args.dry_run:
        print(f"[dry-run] {len(rows)} intakes older than {args.older_than} days would be deleted")
        for row in rows:
            print(f"  - #{row['id']} {row['created_at']} {row['name']} <{row['email']}>")
        return 0

    if not rows:
        print("Nothing to prune.")
        return 0

    if not args.yes:
        print(f"{len(rows)} intakes to delete. Re-run with --yes to confirm.")
        return 1

    now = datetime.now(timezone.utc).isoformat()
    with m.db_connection() as connection:
        for row in rows:
            intake_id = row["id"]
            target = m.FILES_DIR / str(intake_id)
            if target.exists():
                shutil.rmtree(target)
            connection.execute("DELETE FROM files WHERE intake_id = ?", (intake_id,))
            connection.execute("DELETE FROM intakes WHERE id = ?", (intake_id,))
            connection.execute(
                "INSERT INTO audit_log (ts, ip, action, detail) VALUES (?, ?, ?, ?)",
                (now, "cli", "prune", f"deleted intake {intake_id}"),
            )
    print(f"Deleted {len(rows)} intakes older than {args.older_than} days.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
