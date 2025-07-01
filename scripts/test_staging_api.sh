#!/bin/bash
STAGING_URL="https://save-note-api.onrender.com"

echo "🌍 Testing staging @ $STAGING_URL"

echo -e "\n🔍 /api/scan_inbox"
curl -s -X POST "$STAGING_URL/api/scan_inbox" | jq

echo -e "\n📦 /api/process_file (example)"
curl -s -X POST "$STAGING_URL/api/process_file" \
  -H "Content-Type: application/json" \
  -d '{"filename": "2025-06-30_MinhaNota.md"}' | jq

echo -e "\n🤖 /api/scan_and_process"
curl -s -X POST "$STAGING_URL/api/scan_and_process" | jq

echo -e "\n✅ Done testing staging!"
