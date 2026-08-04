#!/usr/bin/env bash
# Marketing Agent helper: fetch the collateral bundle for one article from the
# production admin API. Reads ADMIN_TOKEN from .env (never prints it).
#
# Usage: bash scripts/fetch_marketing_bundle.sh <slug> [base_url]
set -euo pipefail

SLUG="${1:?usage: fetch_marketing_bundle.sh <slug> [base_url]}"
BASE="${2:-https://shenyuanlegal.com}"

ENV_FILE="$(cd "$(dirname "$0")/.." && pwd)/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "error: $ENV_FILE not found" >&2
  exit 1
fi

TOKEN="$(sed -n 's/^ADMIN_TOKEN=//p' "$ENV_FILE" | head -1 | tr -d '\r')"
if [[ -z "$TOKEN" ]]; then
  echo "error: ADMIN_TOKEN empty in $ENV_FILE" >&2
  exit 1
fi

curl -sS --fail -H "Authorization: Bearer ${TOKEN}" \
  "${BASE}/admin/api/marketing/generate?slug=${SLUG}"
