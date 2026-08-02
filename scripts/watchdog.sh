#!/usr/bin/env bash
# Lightweight watchdog: alerts via NOTIFY_WEBHOOK_URL when disk usage or the
# SQLite database size crosses a threshold. Always exits 0 (cron-friendly).
#
# Env: DISK_THRESHOLD_PCT (default 90), DB_MAX_MB (default 500),
#      NOTIFY_WEBHOOK_URL (required to actually send alerts)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${DATA_DIR:-$ROOT/data}"
WEBHOOK="${NOTIFY_WEBHOOK_URL:-}"
DISK_THRESHOLD="${DISK_THRESHOLD_PCT:-90}"
DB_MAX_MB="${DB_MAX_MB:-500}"

alerts=()

pct="$(df -P "$DATA_DIR" 2>/dev/null | awk 'NR==2 {gsub("%","",$5); print $5}')"
if [ -n "$pct" ] && [ "$pct" -ge "$DISK_THRESHOLD" ]; then
  alerts+=("磁盘使用率 ${pct}%（阈值 ${DISK_THRESHOLD}%）")
fi

db_mb="$(du -sm "$DATA_DIR/lawyers.sqlite3" 2>/dev/null | cut -f1 || echo 0)"
if [ "$db_mb" -gt "$DB_MAX_MB" ]; then
  alerts+=("数据库已达 ${db_mb}MB（阈值 ${DB_MAX_MB}MB）")
fi

if [ "${#alerts[@]}" -gt 0 ] && [ -n "$WEBHOOK" ]; then
  content="【服务器告警】"
  for a in "${alerts[@]}"; do
    content="$content
$a"
  done
  payload="$(python3 -c 'import json,sys; print(json.dumps({"msgtype":"text","text":{"content":sys.argv[1]}}, ensure_ascii=False))' "$content")"
  curl -s -m 10 -X POST "$WEBHOOK" -H 'Content-Type: application/json' -d "$payload" >/dev/null 2>&1 || true
fi
