#!/bin/bash

# Create structure
mkdir -p routes
touch app.py dropbox_client.py utils.py requirements.txt .env
touch routes/__init__.py routes/upload.py routes/list.py routes/download.py

# Write app.py
cat <<'EOF' > app.py
from flask import Flask
from routes.upload import upload_note
from routes.list import list_kb, list_kb_folder
from routes.download import get_kb_note

app = Flask(__name__)

app.add_url_rule("/save_note", view_func=upload_note, methods=["POST"])
app.add_url_rule("/list_kb", view_func=list_kb, methods=["GET"])
app.add_url_rule("/list_kb_folder", view_func=list_kb_folder, methods=["GET"])
app.add_url_rule("/get_kb_note", view_func=get_kb_note, methods=["GET"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
EOF

# Write dropbox_client.py
cat <<'EOF' > dropbox_client.py
import os
import requests
from datetime import datetime

APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

def get_access_token():
    url = "https://api.dropboxapi.com/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }
    r = requests.post(url, headers=headers, data=data)
    return r.json().get("access_token") if r.status_code == 200 else None

def upload_note_to_dropbox(title, date, content):
    filename = f"{date}_{title.replace(' ', '_')}.md"
    subfolder = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
    dropbox_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{filename}"
    token = get_access_token()
    if not token:
        return {"status": "error", "message": "Token refresh failed"}

    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {token}",
        "Dropbox-API-Arg": f"""{{"path": "{dropbox_path}","mode": "overwrite"}}""",
        "Content-Type": "application/octet-stream"
    }
    r = requests.post(url, headers=headers, data=content.encode("utf-8"))
    return {
        "status": "success" if r.status_code == 200 else "error",
        "dropbox_status": r.status_code,
        "dropbox_error": None if r.status_code == 200 else r.text
    }

def download_note_from_dropbox(path):
    token = get_access_token()
    if not token:
        return None, "Token error"
    url = "https://content.dropboxapi.com/2/files/download"
    headers = {
        "Authorization": f"Bearer {token}",
        "Dropbox-API-Arg": f"""{{"path": "{path}"}}"""
    }
    r = requests.post(url, headers=headers)
    return (r.text, None) if r.status_code == 200 else (None, r.text)

def list_folder(path):
    token = get_access_token()
    if not token:
        return None, "Token error"
    url = "https://api.dropboxapi.com/2/files/list_folder"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json={"path": path})
    return (r.json(), None) if r.status_code == 200 else (None, r.text)
EOF

# routes/upload.py
cat <<'EOF' > routes/upload.py
from flask import request, jsonify
from dropbox_client import upload_note_to_dropbox
from datetime import datetime

def upload_note():
    file = request.files.get("file")
    if not file:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    content = file.read().decode("utf-8")
    title = file.filename.rsplit(".", 1)[0]
    date = datetime.now().strftime("%Y-%m-%d")
    result = upload_note_to_dropbox(title, date, content)
    return jsonify(result)
EOF

# routes/list.py
cat <<'EOF' > routes/list.py
from flask import request, jsonify
from dropbox_client import list_folder

def list_kb():
    result, err = list_folder("/Apps/SaveNotesGPT/NotesKB")
    if err:
        return jsonify({"status": "error", "message": err}), 500
    folders = [e["name"] for e in result.get("entries", []) if e[".tag"] == "folder"]
    return jsonify({"status": "success", "folders": folders})

def list_kb_folder():
    folder = request.args.get("folder")
    if not folder:
        return jsonify({"status": "error", "message": "Missing 'folder' param"}), 400
    result, err = list_folder(f"/Apps/SaveNotesGPT/NotesKB/{folder}")
    if err:
        return jsonify({"status": "error", "message": err}), 500
    files = [e["name"] for e in result.get("entries", []) if e[".tag"] == "file"]
    return jsonify({"status": "success", "files": files})
EOF

# routes/download.py
cat <<'EOF' > routes/download.py
from flask import request, jsonify
from dropbox_client import download_note_from_dropbox
from datetime import datetime

def get_kb_note():
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"status": "error", "message": "Missing filename"}), 400
    date_part = filename.split("_")[0]
    folder = datetime.strptime(date_part, "%Y-%m-%d").strftime("%Y-%m")
    path = f"/Apps/SaveNotesGPT/NotesKB/{folder}/{filename}"
    content, err = download_note_from_dropbox(path)
    if err:
        return jsonify({"status": "error", "message": err}), 500
    return content, 200, {"Content-Type": "text/markdown"}
EOF

echo "✅ Modular KB API scaffold complete."
