#!/bin/bash
STAGING_URL="https://save-note-api.onrender.com"
NOTE_FILE="2025-06-01_Test-Note.md"

echo "🔐 Loading GPT token..."

if [ -z "$GPT_TOKEN" ]; then
  if [ -f ".tokens" ]; then
    export $(grep GPT_TOKEN .tokens | xargs)
    echo "✅ Loaded GPT_TOKEN from .tokens"
  else
    echo "❌ GPT_TOKEN not set and .tokens not found!"
    exit 1
  fi
else
  echo "✅ Using GPT_TOKEN from environment"
fi

# Test helper
function test_endpoint() {
  local name="$1"
  local path="$2"
  local method="$3"
  local data="$4"

  echo -e "\n🔹 $name"
  if [ "$method" == "POST" ]; then
    RESPONSE=$(curl -s -X POST "$STAGING_URL$path" \
      -H "Authorization: Bearer $GPT_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$data")
  elif [ "$method" == "PATCH" ]; then
    RESPONSE=$(curl -s -X PATCH "$STAGING_URL$path" \
      -H "Authorization: Bearer $GPT_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$data")
  else
    RESPONSE=$(curl -s "$STAGING_URL$path" \
      -H "Authorization: Bearer $GPT_TOKEN")
  fi

  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
}

# Inbox Notes
test_endpoint "📥 List Inbox notes" "/api/inbox/notes" GET
test_endpoint "📥 Get Inbox note" "/api/inbox/notes/$NOTE_FILE" GET
test_endpoint "📥 Create Inbox note" "/api/inbox/notes" POST '{
  "title": "Staging Test Note",
  "content": "# Staging Test\n\nTesting the staging API deployment.",
  "date": "2025-07-03"
}'
test_endpoint "📥 Process Inbox note" "/api/inbox/notes/2025-07-03_staging-test-note.md" PATCH '{
  "action": "process",
  "metadata": {
    "title": "Staging Test Note",
    "date": "2025-07-03",
    "tags": ["staging", "test"],
    "summary": "Testing staging deployment"
  }
}'

# Knowledge Base Notes
test_endpoint "📚 List KB notes" "/api/kb/notes" GET
test_endpoint "📚 List KB folders" "/api/kb/folders" GET
test_endpoint "📚 Get KB note" "/api/kb/notes/$NOTE_FILE" GET

echo -e "\n✅ Staging test complete!"