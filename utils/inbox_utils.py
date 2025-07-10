# utils/inbox_utils.py - Common inbox operations for both Push and Pull modes

from services.dropbox_client import list_folder, download_note_from_dropbox
from utils.logging_utils import log
from utils.config_utils import load_config
from datetime import datetime, timezone


def scan_inbox_for_notes(limit=50, offset=0):
    """
    Scans the inbox for Markdown notes and returns structured note information.
    
    This function is used by both:
    - routes/scan.py (Push mode API endpoint)
    - services/pull_service.py (Pull mode internal service)
    
    Args:
        limit: Maximum number of notes to return
        offset: Number of notes to skip for pagination
        
    Returns:
        dict: {
            "notes": [...],
            "total": int,
            "has_more": bool
        }
    """
    try:
        config = load_config()
        inbox_path = config.get("inbox_path")
        
        # Get raw entries from Dropbox
        entries = list_folder(inbox_path)
        
        # Transform to notes with meaningful metadata
        all_notes = []
        for item in entries:
            if item[".tag"] == "file" and item["name"].endswith(".md"):
                # Extract title from filename (remove date prefix and extension)
                filename = item["name"]
                title = _extract_title_from_filename(filename)
                
                all_notes.append({
                    "filename": filename,
                    "title": title,
                    "status": "unprocessed",  # All inbox notes are unprocessed
                    "created": item.get("client_modified"),
                    "size": item.get("size"),
                    "path": f"/api/inbox/notes/{filename}"
                })
        
        # Sort by creation date (newest first)
        all_notes.sort(key=lambda x: x.get("created", ""), reverse=True)
        
        # Apply pagination
        total = len(all_notes)
        paginated_notes = all_notes[offset:offset + limit] if offset < total else []
        has_more = offset + limit < total
        
        return {
            "notes": paginated_notes,
            "total": total,
            "has_more": has_more
        }
        
    except Exception as e:
        log(f"❌ Error scanning inbox: {str(e)}", level="error")
        raise


def get_inbox_note_content(filename):
    """
    Downloads and returns the content of a specific note from the inbox.
    
    This function is used by both:
    - routes/download.py (Push mode API endpoint)
    - services/pull_service.py (Pull mode internal service)
    
    Args:
        filename: Name of the file in the inbox
        
    Returns:
        str: Note content or None if not found
    """
    try:
        content = download_note_from_dropbox(filename, folder="Inbox")
        if content:
            log(f"📥 Retrieved inbox note: {filename}")
            return content
        else:
            log(f"📥 Inbox note not found: {filename}", level="warning")
            return None
            
    except Exception as e:
        log(f"❌ Error retrieving inbox note {filename}: {str(e)}", level="error")
        raise


def get_multiple_inbox_notes_content(filenames):
    """
    Downloads content for multiple inbox notes in batch.
    
    This is primarily used by:
    - services/pull_service.py (Pull mode batch processing)
    
    Args:
        filenames: List of filenames to download
        
    Returns:
        list: [{"filename": str, "content": str, "error": str}, ...]
    """
    results = []
    
    for filename in filenames:
        try:
            content = get_inbox_note_content(filename)
            results.append({
                "filename": filename,
                "content": content,
                "error": None if content else "Content not found"
            })
        except Exception as e:
            results.append({
                "filename": filename,
                "content": None,
                "error": str(e)
            })
    
    return results


def update_scan_timestamp():
    """
    Updates the last scan timestamp in configuration.
    COMPATIBILITY: Uses the same functions as the original routes/scan.py
    """
    try:
        from utils.config_utils import load_config, save_config
        
        config = load_config()
        config["last_scan"] = datetime.now(timezone.utc).isoformat()
        save_config(config)
        
        log(f"📅 Updated scan timestamp: {config['last_scan']}")
        
    except Exception as e:
        log(f"❌ Error updating scan timestamp: {str(e)}", level="error")


def save_processed_files_list(filenames):
    """
    Saves the list of processed files for admin dashboard display.
    COMPATIBILITY: Uses the same function name as original routes/scan.py
    """
    try:
        from utils.config_utils import save_last_files  # Use original function name
        save_last_files(filenames)
        
    except Exception as e:
        log(f"❌ Error saving processed files list: {str(e)}", level="error")


def _extract_title_from_filename(filename):
    """
    Helper function to extract a clean title from a filename.
    
    Examples:
        "2025-07-03_meeting-notes.md" → "meeting notes"
        "2025-07-03_project_ideas.md" → "project ideas"
        "simple-note.md" → "simple note"
    """
    title = filename.replace('.md', '')
    
    # Remove date prefix if present (YYYY-MM-DD_)
    if '_' in title:
        parts = title.split('_', 1)
        if len(parts) > 1 and parts[0].count('-') == 2:
            title = parts[1]
    
    # Clean up the title
    return title.replace('_', ' ').replace('-', ' ').strip()


# Validation functions
def validate_inbox_note_filename(filename):
    """
    Validates that a filename is valid for inbox operations.
    
    Args:
        filename: Filename to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not filename or not isinstance(filename, str):
        return False
        
    if not filename.endswith('.md'):
        return False
        
    # Check for invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in filename for char in invalid_chars):
        return False
        
    return True


def get_inbox_stats():
    """
    Get summary statistics about the inbox.
    
    Returns:
        dict: {
            "total_notes": int,
            "total_size": int,
            "latest_note": str,
            "oldest_note": str
        }
    """
    try:
        result = scan_inbox_for_notes(limit=1000)  # Get all notes for stats
        notes = result["notes"]
        
        if not notes:
            return {
                "total_notes": 0,
                "total_size": 0,
                "latest_note": None,
                "oldest_note": None
            }
        
        total_size = sum(note.get("size", 0) for note in notes)
        latest_note = notes[0]["created"] if notes else None  # Already sorted by date desc
        oldest_note = notes[-1]["created"] if notes else None
        
        return {
            "total_notes": len(notes),
            "total_size": total_size,
            "latest_note": latest_note,
            "oldest_note": oldest_note
        }
        
    except Exception as e:
        log(f"❌ Error getting inbox stats: {str(e)}", level="error")
        return {
            "total_notes": 0,
            "total_size": 0,
            "latest_note": None,
            "oldest_note": None
        }