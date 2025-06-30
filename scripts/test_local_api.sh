#!/bin/bash
cd "$(dirname "$0")/.." || exit 1

echo "🚀 Starting SaveNotesGPT local test..."

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
    echo "------------------------------------------"
    tail -n 40 flask.log
    echo "------------------------------------------"
    exit 1
  fi

  sleep 1
done

# Timeout
if ! kill -0 $FLASK_PID 2>/dev/null; then
  echo "❌ Flask did not start in time. Aborting."
  tail -n 40 flask.log
  exit 1
fi

echo "📡 Testing endpoints..."

# 4. Call endpoints
echo -e "\n🔍 /api/scan_inbox"
curl -s -X POST http://localhost:5000/api/scan_inbox | jq

echo -e "\n📦 /api/process_file (example)"
curl -s -X POST http://localhost:5000/api/process_file \
  -H "Content-Type: application/json" \
  -d '{"filename": "2025-06-30_MinhaNota.md"}' | jq

echo -e "\n🤖 /api/scan_and_process"
curl -s -X POST http://localhost:5000/api/scan_and_process | jq

# 5. Cleanup
echo -e "\n🛑 Stopping Flask (PID $FLASK_PID)"
kill $FLASK_PID
sleep 1

echo "✅ Done!"
