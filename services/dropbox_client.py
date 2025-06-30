import os
import requests
import json
from dotenv import load_dotenv
from utils.dropbox_utils import get_access_token

load_dotenv()

DROPBOX_API_UPLOAD = "https://content.dropboxapi.com/2/files/upload"
DROPBOX_API_LIST_FOLDER = "https://api.dropboxapi.com/2/files/list_folder"
DROPBOX_API_GET_FILE = "https://content.dropboxapi.com/2/files/download"
DROPBOX_API_SAVE_FILE = "https://api.dropboxapi.com/2/files/save_url"

BASE_DROPBOX_PATH = "/Apps/SaveNotesGPT"
INBOX_PATH = f"{BASE_DROPBOX_PATH}/Inbox"
NOTES_KB_PATH = f"{BASE_DROPBOX_PATH}/NotesKB"


def upload_note_to_dropbox(title, date, content):
    """
    Uploads a Markdown file to Dropbox under the NotesKB/{YYYY-MM}/ directory.
    Automatically builds the path from date and title.
    """
    access_token = get_access_token()
    filename = f"{date}_{title.replace(' ', '_')}.md"
    subfolder = date[:7]
    dropbox_path = f"{NOTES_KB_PATH}/{subfolder}/{filename}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": json.dumps({
            "path": dropbox_path,
            "mode": "overwrite",
            "mute": False,
            "strict_conflict": False
        })
    }

    response = requests.post(DROPBOX_API_UPLOAD, headers=headers, data=content.encode('utf-8'))

    if response.status_code == 200:
        print(f"✅ Uploaded note to Dropbox at {dropbox_path}")
        return True
    else:
        print("❌ Dropbox upload failed:", response.text)
        return False


def upload_structured_note(path: str, content: str) -> bool:
    """
    Uploads a structured Markdown note (already containing YAML front matter) to Dropbox at the given full path.
    Example path: /Apps/SaveNotesGPT/NotesKB/2025-06/2025-06-29_Title.md
    """
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": json.dumps({
            "path": path,
            "mode": "overwrite",
            "autorename": False,
            "mute": False
        })
    }

    response = requests.post(DROPBOX_API_UPLOAD, headers=headers, data=content.encode("utf-8"))

    if response.status_code == 200:
        print(f"✅ Structured note uploaded to {path}")
        return True
    else:
        print(f"❌ Upload failed: {response.text}")
        return False


def download_note_from_dropbox(filename: str, folder: str = "Inbox") -> str:
    """
    Downloads the content of a Markdown note from Dropbox.
    Defaults to the Inbox folder.
    Returns raw Markdown content as a string.
    """
    access_token = get_access_token()
    path = f"{INBOX_PATH}/{filename}" if folder == "Inbox" else f"{NOTES_KB_PATH}/{folder}/{filename}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": json.dumps({"path": path}),
    }

    response = requests.post(DROPBOX_API_GET_FILE, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to download file: {response.text}")

    return response.text


def get_file_from_dropbox(filename, folder):
    """
    Alternative helper to download a file from NotesKB subfolder.
    Returns the file content or None on failure.
    """
    access_token = get_access_token()
    path = f"{NOTES_KB_PATH}/{folder}/{filename}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": json.dumps({"path": path})
    }

    response = requests.post(DROPBOX_API_GET_FILE, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print("❌ Dropbox file fetch failed:", response.text)
        return None


def list_folder(path):
    """
    Lists files and folders inside the specified Dropbox path.
    Raises Exception if the API call fails.
    Returns a list of metadata entries.
    """
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "path": path,
        "recursive": False
    }

    response = requests.post(DROPBOX_API_LIST_FOLDER, headers=headers, json=data)

    if response.status_code == 200:
        return response.json().get("entries", [])
    else:
        raise Exception(f"Dropbox list_folder failed: {response.text}")
