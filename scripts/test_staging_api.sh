#!/bin/bash
STAGING_URL="https://save-note-api.onrender.com"

echo "🌍 Testing staging @ $STAGING_URL"

# Load token from .tokens
if [ -f ".tokens" ]; then
  export $(grep GPT_TOKEN .tokens | xargs)
else
  echo "❌ .tokens file not found!"
  exit 1
fi

if [ -z "$GPT_TOKEN" ]; then
  echo "❌ GPT_TOKEN not set in .tokens"
  exit 1
fi

# Helper: test an endpoint
function test_endpoint() {
  local label="$1"
  local path="$2"
  local method="$3"
  local data="$4"

  echo -e "\n🔹 $label"
  if [ "$method" == "POST" ]; then
    RESPONSE=$(curl -s -X POST "$STAGING_URL$path" -H "Authorization: Bearer $GPT_TOKEN" -H "Content-Type: application/json" -d "$data")
  else
    RESPONSE=$(curl -s "$STAGING_URL$path" -H "Authorization: Bearer $GPT_TOKEN")
  fi

  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
}

# Run tests
test_endpoint "Scan Inbox" "/api/scan_inbox" POST '{}'
test_endpoint "Process File" "/api/process_file" POST '{"filename": "2025-06-30_MinhaNota.md"}'
test_endpoint "Scan and Process" "/api/scan_and_process" POST '{}'

echo -e "\n✅ Done testing staging!"
