import requests
import os

# You may already have this in your environment or init code
DROPBOX_API_CONTENT_URL = "https://content.dropboxapi.com/2/files"
DROPBOX_API_ARG_HEADER = "Dropbox-API-Arg"
DROPBOX_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

def get_access_token():
    # In production use refresh token flow
    return DROPBOX_TOKEN

def download_note(filename):
    """
    Downloads a file from Dropbox by filename from the default NotesKB structure.
    """
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        DROPBOX_API_ARG_HEADER: f"{{\"path\": \"/Apps/SaveNotesGPT/NotesKB/2025-06/{filename}\"}}"
    }
    url = f"{DROPBOX_API_CONTENT_URL}/download"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print("❌ Dropbox download failed:", response.text)
        return None

def upload_structured_note(path, content):
    """
    Uploads a note to Dropbox at the specified path with overwrite mode.
    """
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        DROPBOX_API_ARG_HEADER: f"{{\"path\": \"{path}\", \"mode\": \"overwrite\"}}"
    }
    url = f"{DROPBOX_API_CONTENT_URL}/upload"
    response = requests.post(url, headers=headers, data=content.encode("utf-8"))
    return {
        "status": "success" if response.status_code == 200 else "error",
        "dropbox_status": response.status_code,
        "dropbox_error": response.text if response.status_code != 200 else None
    }
