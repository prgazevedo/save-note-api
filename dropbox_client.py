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
