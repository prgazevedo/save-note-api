#!/bin/bash

echo "🔧 Setting up development environment..."

# Check if running inside Codespaces
if [ "$CODESPACES" = "true" ]; then
  echo "⚙️ Running inside GitHub Codespaces."
fi

# 1. Create virtual environment
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo "✅ Virtual environment created."
else
  echo "✅ Virtual environment already exists."
fi

# Activate venv
source venv/bin/activate

# 2. Install dependencies
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
  echo "✅ Dependencies installed."
else
  echo "⚠️ requirements.txt not found."
fi

# 3. Setup .env
if [ ! -f ".env" ]; then
  cat <<EOF > .env
# Dropbox credentials
DROPBOX_APP_KEY=your_key_here
DROPBOX_APP_SECRET=your_secret_here
DROPBOX_REFRESH_TOKEN=your_refresh_token_here

# Flask secret
FLASK_SECRET_KEY=dev-insecure-default
EOF
  echo "⚠️  .env created. Fill in your Dropbox credentials."
else
  echo "✅ .env already exists."
fi

# 4. Ensure data directory and files exist
mkdir -p data

touch data/admin_config.json data/admin_log.json data/last_files.json

# 5. Prepopulate config file if empty
if [ ! -s data/admin_config.json ]; then
  cat <<EOF > data/admin_config.json
{
  "kb_path": "/Apps/SaveNotesGPT/NotesKB",
  "inbox_path": "/Apps/SaveNotesGPT/Inbox",
  "last_scan": null
}
EOF
  echo "✅ admin_config.json prepopulated."
fi

echo "✅ Development environment setup complete!"
