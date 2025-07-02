#!/bin/bash
cd "$(dirname "$0")/.." || exit 1

echo "🚀 Starting SaveNotesGPT local test..."

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

# 1. Activate venv
if [ -d "venv" ]; then
  source venv/bin/activate
else
  echo "❌ Virtual environment not found. Run setup_dev.sh first."
  exit 1
fi

# 2. Start Flask app in background
echo "⚙️ Starting Flask..."
FLASK_APP=app.py flask run > flask.log 2>&1 &
FLASK_PID=$!

# 3. Wait until server is up, or fail if Flask exits
TIMEOUT=10
for i in $(seq 1 $TIMEOUT); do
  if curl -s http://localhost:5000/ > /dev/null; then
    echo "✅ Flask is up (PID $FLASK_PID)"
    break
  fi

  if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "❌ Flask failed to start. Check flask.log below:"
    tail -n 40 flask.log
    exit 1
  fi

  sleep 1
done

echo "📡 Testing endpoints..."

# 4. Call endpoints with token
function test_endpoint() {
  local name="$1"
  local method="$2"
  local url="$3"
  local data="$4"

  echo -e "\n🔹 $name"
  if [ "$method" == "POST" ]; then
    RESPONSE=$(curl -s -X POST "$url" -H "Authorization: Bearer $GPT_TOKEN" -H "Content-Type: application/json" -d "$data")
  else
    RESPONSE=$(curl -s "$url" -H "Authorization: Bearer $GPT_TOKEN")
  fi

  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
}

test_endpoint "Scan Inbox" POST http://localhost:5000/api/scan_inbox '{}'
test_endpoint "Process File" POST http://localhost:5000/api/process_file '{"filename": "2025-06-30_MinhaNota.md"}'
test_endpoint "Scan and Process" POST http://localhost:5000/api/scan_and_process '{}'

# 5. Cleanup
echo -e "\n🛑 Stopping Flask (PID $FLASK_PID)"
kill $FLASK_PID
sleep 1

echo "✅ Done!"
