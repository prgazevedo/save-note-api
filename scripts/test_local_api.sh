#!/bin/bash
cd "$(dirname "$0")/.." || exit 1

echo "🚀 Starting SaveNotesGPT local test..."

# Enable mock mode for Dropbox etc
export MOCK_MODE=1

# Use token from environment if present, otherwise fallback to .tokens
if [ -z "$GPT_TOKEN" ]; then
  if [ -f ".tokens" ]; then
    export $(grep GPT_TOKEN .tokens | xargs)
  else
    echo "❌ GPT_TOKEN not set and .tokens file not found!"
    exit 1
  fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
  source venv/bin/activate
else
  echo "❌ Virtual environment not found. Run setup_dev.sh first."
  exit 1
fi

# Start Flask app in background
echo "⚙️ Starting Flask..."
FLASK_APP=app.py flask run > flask.log 2>&1 &
FLASK_PID=$!

# Wait for Flask to become available
TIMEOUT=10
for i in $(seq 1 $TIMEOUT); do
  if curl -s http://localhost:5000/ > /dev/null; then
    echo "✅ Flask is up (PID $FLASK_PID)"
    break
  fi

  if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "❌ Flask failed to start. Showing last 40 lines of flask.log:"
    tail -n 40 flask.log
    exit 1
  fi

  sleep 1
done

echo "📡 Testing endpoints..."

# Function to test an endpoint with token
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

# Inbox Notes
test_endpoint "📥 List Inbox files" GET http://localhost:5000/api/inbox/files
test_endpoint "📥 List new Inbox notes" GET http://localhost:5000/api/inbox/notes/new
test_endpoint "📥 Download Inbox note" GET http://localhost:5000/api/inbox/notes/2025-06-30_MinhaNota.md
test_endpoint "📥 Process Inbox note" POST http://localhost:5000/api/inbox/notes/2025-06-30_MinhaNota.md/process '{}'

# Knowledge Base Notes
test_endpoint "📚 List KB notes" GET http://localhost:5000/api/kb/notes
test_endpoint "📚 List KB subfolder" GET http://localhost:5000/api/kb/notes/folder?folder=2025-06
test_endpoint "📚 Download KB note" GET http://localhost:5000/api/kb/notes/2025-06-30_MinhaNota.md

# Cleanup
echo -e "\n🛑 Stopping Flask (PID $FLASK_PID)"
kill $FLASK_PID
sleep 1

echo "✅ Local test complete!"
