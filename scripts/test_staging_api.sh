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

# Test helper
function test_endpoint() {
  local name="$1"
  local path="$2"
  local method="$3"
  local data="$4"

  echo -e "\n🔹 $name"
  if [ "$method" == "POST" ]; then
    RESPONSE=$(curl -s -X POST "$STAGING_URL$path" -H "Authorization: Bearer $GPT_TOKEN" -H "Content-Type: application/json" -d "$data")
  else
    RESPONSE=$(curl -s "$STAGING_URL$path" -H "Authorization: Bearer $GPT_TOKEN")
  fi

  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
}

# Inbox Notes
test_endpoint "📥 List Inbox files" "/api/inbox/files" GET
test_endpoint "📥 List new Inbox notes" "/api/inbox/notes/new" GET
test_endpoint "📥 Download Inbox note" "/api/inbox/notes/2025-06-30_MinhaNota.md" GET
test_endpoint "📥 Process Inbox note" "/api/inbox/notes/2025-06-30_MinhaNota.md/process" POST '{}'

# Knowledge Base Notes
test_endpoint "📚 List KB notes" "/api/kb/notes" GET
test_endpoint "📚 List KB subfolder" "/api/kb/notes/folder?folder=2025-06" GET
test_endpoint "📚 Download KB note" "/api/kb/notes/2025-06-30_MinhaNota.md" GET

echo -e "\n✅ Staging test complete!"
