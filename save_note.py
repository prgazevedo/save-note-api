import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import datetime

# Load .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# Credentials from env
APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

# Refresh token to get access token
def get_access_token():
    url = "https://api.dropboxapi.com/oauth2/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("🔐 Novo access token obtido.")
        return token
    else:
        print("❌ Erro ao obter access token:", r.text)
        return None

# Setup Flask
app = Flask(__name__)

@app.route("/save_note", methods=["POST"])
def save_note():
    data = request.get_json()
    title = data.get("title", "Untitled").replace(" ", "_")
    date = data.get("date", datetime.date.today().isoformat())
    content = data.get("content", "")

    filename = f"{date}_{title}.md"
    dropbox_path = f"/{filename}"
    access_token = get_access_token()

    if not access_token:
        return jsonify({"status": "error", "reason": "Failed to get access token"}), 500

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": f'{{"path": "{dropbox_path}", "mode": "overwrite", "autorename": false, "mute": false}}'
    }

    response = requests.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=content.encode("utf-8"))

    if response.status_code == 200:
        return jsonify({"status": "success", "file": filename})
    else:
        return jsonify({
            "status": "error",
            "dropbox_status": response.status_code,
            "dropbox_error": response.text
        }), 500

if __name__ == "__main__":
    print("🚀 Running SaveNote with refresh token flow...")
    app.run(debug=True)
