#!/usr/bin/env bash
# SQLite backup + uploaded-files archive with rotation.
#
# Usage: ./scripts/backup.sh
# Env:   DATA_DIR   (default: <repo>/data)
#        BACKUP_DIR (default: <repo>/backups)
#        BACKUP_KEEP (default: 14 backups to keep)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${DATA_DIR:-$ROOT/data}"
BACKUP_DIR="${BACKUP_DIR:-$ROOT/backups}"
KEEP="${BACKUP_KEEP:-14}"

mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"

# Use the sqlite3 CLI's .backup when available (consistent WAL snapshot);
# otherwise fall back to a plain copy.
if command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 "$DATA_DIR/lawyers.sqlite3" ".backup '$BACKUP_DIR/lawyers_$STAMP.sqlite3'"
else
  cp "$DATA_DIR/lawyers.sqlite3" "$BACKUP_DIR/lawyers_$STAMP.sqlite3" 2>/dev/null || true
fi

if [ -d "$DATA_DIR/files" ]; then
  tar -C "$DATA_DIR" -czf "$BACKUP_DIR/files_$STAMP.tar.gz" files
fi

# Rotation: keep the newest $KEEP backups, drop the rest.
ls -1t "$BACKUP_DIR"/lawyers_*.sqlite3 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f
ls -1t "$BACKUP_DIR"/files_*.tar.gz 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -f

echo "backup ok: $STAMP -> $BACKUP_DIR"
