#!/bin/bash
STAGING_URL="https://save-note-api.onrender.com"

echo "🌍 Testing staging @ $STAGING_URL"

# Helper: test an endpoint
function test_endpoint() {
  local label="$1"
  local path="$2"
  local method="$3"
  local data="$4"

  echo -e "\n🔹 $label"
  if [ "$method" == "POST" ]; then
    RESPONSE=$(curl -s -X POST "$STAGING_URL$path" -H "Content-Type: application/json" -d "$data")
  else
    RESPONSE=$(curl -s "$STAGING_URL$path")
  fi

  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
}

# Run tests
test_endpoint "/api/scan_inbox" "/api/scan_inbox" POST '{}'
test_endpoint "/api/process_file" "/api/process_file" POST '{"filename": "2025-06-30_MinhaNota.md"}'
test_endpoint "/api/scan_and_process" "/api/scan_and_process" POST '{}'

echo -e "\n✅ Done testing staging!"
