#!/usr/bin/env bash
# Minimal post-deploy smoke test.
# Usage: API=https://api.tunmiscloset.com ./scripts/smoke_test.sh
set -euo pipefail

API="${API:-http://localhost:8000}"
API="${API%/}"

check() {
  local label="$1"
  local url="$2"
  local expected="${3:-200}"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$url")
  if [ "$code" != "$expected" ]; then
    echo "FAIL $label ($url) -> $code (expected $expected)"
    exit 1
  fi
  echo "OK   $label -> $code"
}

check "health" "$API/health/"
check "sitemap" "$API/sitemap.xml"
check "products" "$API/api/products/"
check "categories" "$API/api/categories/"
check "auth gate" "$API/api/orders/" "401"

echo "Smoke test passed for $API"
