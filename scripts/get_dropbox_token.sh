#!/bin/bash
# scripts/get_dropbox_token.sh

echo "📡 Launching Dropbox OAuth2 flow..."
python3 scripts/get_new_refresh_token.py
