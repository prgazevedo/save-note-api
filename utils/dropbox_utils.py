#utils/dropbox_utils.py
import os
import json
import requests
from datetime import datetime
import yaml
import re
from urllib.parse import unquote

MOCK_MODE = os.getenv("MOCK_MODE") == "1"

def get_access_token():
    if MOCK_MODE:
        return "mock-access-token"
    
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
        .replace("\\", "-")
    )

# ====== NEW: Obsidian Link Processing Functions ======

def detect_obsidian_links(content):
    """
    Detect Obsidian and Markdown links in note content.
    Returns a dict with detected links categorized by type.
    """
    links = {
        "wiki_links": [],      # [[Internal Link]]
        "embedded_files": [],  # ![[image.png]]
        "markdown_links": [],  # [text](./file.pdf)
        "markdown_images": []  # ![alt](./image.png)
    }
    
    # Embedded files: ![[filename.ext]]
    embedded_pattern = r'!\[\[([^\]]+)\]\]'
    embedded_matches = re.findall(embedded_pattern, content)
    links["embedded_files"] = embedded_matches
    
    # Wiki-style links: [[Internal Link]] (excluding embedded files)
    wiki_pattern = r'(?<!\!)\[\[([^\]]+)\]\]'
    wiki_matches = re.findall(wiki_pattern, content)
    links["wiki_links"] = wiki_matches
    
    # Markdown links: [text](./path/file.ext) - only local files
    md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    md_matches = re.findall(md_link_pattern, content)
    for text, path in md_matches:
        if is_local_file_path(path):
            links["markdown_links"].append({"text": text, "path": path})
    
    # Markdown images: ![alt](./path/image.ext) - only local files
    md_img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    img_matches = re.findall(md_img_pattern, content)
    for alt, path in img_matches:
        if is_local_file_path(path):
            links["markdown_images"].append({"alt": alt, "path": path})
    
    return links

def is_local_file_path(path):
    """
    Determine if a path refers to a local file (not a URL).
    """
    path = path.strip()
    return (
        path.startswith('./') or 
        path.startswith('../') or 
        path.startswith('attachments/') or
        path.startswith('assets/') or
        (not path.startswith('http') and not path.startswith('mailto:') and '.' in path)
    )

def copy_dropbox_file(source_path, target_path):
    """
    Copy a file within Dropbox from source_path to target_path.
    Returns True if successful, False otherwise.
    """
    if MOCK_MODE:
        print(f"📎 [MOCK] Copy file: {source_path} → {target_path}")
        return True
    
    access_token = get_access_token()
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "from_path": source_path,
        "to_path": target_path,
        "allow_shared_folder": False,
        "autorename": False,
        "allow_ownership_transfer": False
    }
    
    response = requests.post(
        "https://api.dropboxapi.com/2/files/copy_v2",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Failed to copy file {source_path} → {target_path}: {response.text}")
        return False

def find_linked_files_in_inbox(detected_links, inbox_path="/Apps/SaveNotesGPT/Inbox"):
    """
    Find which detected links actually exist as files in the Inbox, preserving folder structure.
    Returns a list of files that exist and can be copied with their relative paths.
    """
    if MOCK_MODE:
        return [
            {"link": "screenshot.png", "inbox_path": f"{inbox_path}/screenshot.png", "relative_path": "screenshot.png"},
            {"link": "./attachments/diagram.pdf", "inbox_path": f"{inbox_path}/attachments/diagram.pdf", "relative_path": "attachments/diagram.pdf"}
        ]
    
    existing_files = []
    
    from services.dropbox_client import list_folder
    
    try:
        # Get all files in inbox recursively
        def get_all_files_recursive(path, relative_base=""):
            files = []
            entries = list_folder(path)
            
            for item in entries:
                if item[".tag"] == "file":
                    relative_path = f"{relative_base}/{item['name']}" if relative_base else item["name"]
                    files.append({
                        "name": item["name"],
                        "full_path": f"{path}/{item['name']}",
                        "relative_path": relative_path
                    })
                elif item[".tag"] == "folder":
                    # Recursively get files from subfolders
                    subfolder_path = f"{path}/{item['name']}"
                    subfolder_relative = f"{relative_base}/{item['name']}" if relative_base else item["name"]
                    files.extend(get_all_files_recursive(subfolder_path, subfolder_relative))
            
            return files
        
        all_inbox_files = get_all_files_recursive(inbox_path)
        
        # Check each detected link against all inbox files
        for link_type, links in detected_links.items():
            if link_type == "embedded_files":
                # ![[filename.ext]] - look for exact filename anywhere
                for link in links:
                    for file_info in all_inbox_files:
                        if file_info["name"] == link:
                            existing_files.append({
                                "link": link,
                                "inbox_path": file_info["full_path"],
                                "relative_path": file_info["relative_path"]
                            })
                            break
            
            elif link_type == "wiki_links":
                # [[filename.ext]] - look for exact filename anywhere  
                for link in links:
                    for file_info in all_inbox_files:
                        if file_info["name"] == link:
                            existing_files.append({
                                "link": link,
                                "inbox_path": file_info["full_path"],
                                "relative_path": file_info["relative_path"]
                            })
                            break
            
            elif link_type in ["markdown_links", "markdown_images"]:
                # [text](./path/file.ext) or ![alt](./path/file.ext)
                for link in links:
                    path = link["path"] if isinstance(link, dict) else link
                    
                    # Clean up the path (remove ./ prefix, normalize)
                    clean_path = path.lstrip('./').lstrip('../')
                    
                    # Look for file at this relative path
                    for file_info in all_inbox_files:
                        if file_info["relative_path"] == clean_path:
                            existing_files.append({
                                "link": path,
                                "inbox_path": file_info["full_path"],
                                "relative_path": file_info["relative_path"]
                            })
                            break
    
    except Exception as e:
        print(f"❌ Error finding linked files: {str(e)}")
    
    return existing_files


def copy_linked_files_to_kb(detected_links, kb_folder_path, inbox_path="/Apps/SaveNotesGPT/Inbox"):
    """
    Copy linked files from Inbox to Knowledge Base folder, preserving folder structure.
    
    Args:
        detected_links: Dict from detect_obsidian_links()
        kb_folder_path: Target KB path like "/Apps/SaveNotesGPT/NotesKB/2025-07"
        inbox_path: Source inbox path
    
    Returns:
        dict: {"copied_files": [...], "failed_files": [...], "total_copied": int}
    """
    result = {
        "copied_files": [],
        "failed_files": [], 
        "total_copied": 0
    }
    
    # Find existing files in inbox with their relative paths
    existing_files = find_linked_files_in_inbox(detected_links, inbox_path)
    
    if not existing_files:
        return result
    
    # Copy each existing file preserving folder structure
    for file_info in existing_files:
        source_path = file_info["inbox_path"]
        # Preserve the relative folder structure in the target
        target_path = f"{kb_folder_path}/{file_info['relative_path']}"
        
        if copy_dropbox_file(source_path, target_path):
            result["copied_files"].append({
                "filename": file_info["relative_path"],  # Full relative path
                "source": source_path,
                "target": target_path
            })
            result["total_copied"] += 1
        else:
            result["failed_files"].append({
                "filename": file_info["relative_path"],
                "source": source_path,
                "error": "Copy operation failed"
            })
    
    return result



def process_note_with_links(content, metadata, kb_folder_path, copy_links=True):
    """
    Complete note processing with optional link handling.
    
    Args:
        content: Raw note content
        metadata: Note metadata dict
        kb_folder_path: Target KB folder path
        copy_links: Whether to copy linked files
    
    Returns:
        dict: {
            "processed_content": str (unchanged - no need to update paths),
            "detected_links": dict,
            "copy_result": dict,
            "metadata": dict (updated with linked_files)
        }
    """
    # Detect links
    detected_links = detect_obsidian_links(content)
    total_links = sum(len(links) for links in detected_links.values())
    
    # Content remains unchanged since we preserve folder structure
    processed_content = content
    copy_result = {"copied_files": [], "failed_files": [], "total_copied": 0}
    
    # Copy linked files if requested
    if copy_links and total_links > 0:
        copy_result = copy_linked_files_to_kb(detected_links, kb_folder_path)
    
    # Update metadata with linked files
    if total_links > 0:
        all_links = []
        for link_type, links in detected_links.items():
            if link_type in ["embedded_files", "wiki_links"]:
                all_links.extend(links)
            else:  # markdown_links, markdown_images
                all_links.extend([os.path.basename(link["path"]) for link in links])
        metadata["linked_files"] = list(set(all_links))  # Remove duplicates
    else:
        metadata["linked_files"] = []
    
    return {
        "processed_content": processed_content,  # No changes needed!
        "detected_links": detected_links,
        "copy_result": copy_result,
        "metadata": metadata
    }