import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

def get_access_token():
    print("🔁 Refreshing access token...")
    url = "https://api.dropboxapi.com/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("✅ Access token refreshed.")
        return token
    else:
        print("❌ Failed to refresh token:", r.text)
        return None

def sanitize_filename(title):
    return title.strip().replace(" ", "_").replace(":", "-")

def upload_note_to_dropbox(title, date, content):
    filename = f"{date}_{sanitize_filename(title)}.md"
    dropbox_path = f"/{filename}"
    access_token = get_access_token()
    if not access_token:
        return {"status": "error", "dropbox_error": "Could not refresh token"}

    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": f"""{{"path": "{dropbox_path}", "mode": "overwrite", "autorename": false, "mute": false}}""",
        "Content-Type": "application/octet-stream"
    }

    print(f"📄 File: {dropbox_path}")
    response = requests.post(url, headers=headers, data=content.encode("utf-8"))
    return {
        "status": "success" if response.status_code == 200 else "error",
        "dropbox_status": response.status_code,
        "dropbox_error": response.text if response.status_code != 200 else None,
        "file": filename if response.status_code == 200 else None
    }

app = Flask(__name__)

@app.route("/save_note", methods=["POST"])
def save_note():
    data = request.get_json()
    title = data.get("title")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    content = data.get("content")
    if not title or not content:
        return jsonify({"status": "error", "message": "Missing title or content"}), 400
    result = upload_note_to_dropbox(title, date, content)
    return jsonify(result)

if __name__ == "__main__":
    print("🚀 Starting SaveNote API with refresh token...")
    app.run(debug=True)
