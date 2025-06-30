#utils/dropbox_utils.py
import os
import json
import requests
from datetime import datetime
import yaml

def get_access_token():
    """
    Uses Dropbox refresh token flow to get a new short-lived access token.
    """
    refresh_token = os.getenv("DROPBOX_REFRESH_TOKEN")
    client_id = os.getenv("DROPBOX_APP_KEY")
    client_secret = os.getenv("DROPBOX_APP_SECRET")

    if not refresh_token or not client_id or not client_secret:
        raise EnvironmentError("Missing Dropbox API credentials in environment.")

    response = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        auth=(client_id, client_secret),
    )

    if response.status_code != 200:
        raise Exception(f"Failed to refresh access token: {response.text}")

    return response.json()["access_token"]

def generate_uid(title, date_str):
    """
    Generates a simple UID based on date and slugified title.
    """
    slug = title.lower().strip().replace(" ", "-").replace("_", "-")
    return f"{slug}-{date_str}"

def generate_yaml_front_matter(metadata: dict) -> str:
    """
    Converts a Python dictionary to a YAML front matter string.
    """
    yaml_part = yaml.dump(metadata, default_flow_style=False, allow_unicode=True).strip()
    return f"---\n{yaml_part}\n---"

def parse_yaml_from_markdown(md_content: str) -> dict:
    """
    Extracts YAML metadata block from a Markdown file, if any.
    """
    if md_content.startswith("---"):
        parts = md_content.split("---", 2)
        if len(parts) > 2:
            return yaml.safe_load(parts[1])
    return {}

def append_metadata_to_content(content: str, metadata: dict) -> str:
    """
    Prepends YAML metadata block to markdown content.
    """
    yaml_block = generate_yaml_front_matter(metadata)
    return f"{yaml_block}\n\n{content.strip()}"

def sanitize_filename(title):
    """
    Converts a title to a filename-safe string.
    """
    return (
        title.strip()
        .lower()
        .replace(" ", "_")
        .replace(":", "-")
        .replace("/", "-")
    )