# routes/list.py - Knowledge Base note listing (Inbox handled by scan.py)

from flask import Blueprint, request, jsonify
from utils.config_utils import load_config
from services.dropbox_client import list_folder
from utils.logging_utils import log
from utils.token_utils import require_token

list_bp = Blueprint("list", __name__, url_prefix="/api")

# ──────────── KNOWLEDGE BASE ONLY ────────────
# (Inbox listing is handled by routes/scan.py)

@list_bp.route("/kb/notes", methods=["GET"])
@require_token
def list_kb_notes():
    """
    List processed notes in the Knowledge Base.
    ---
    tags:
      - Knowledge Base Notes
    summary: List KB notes
    description: |
      Lists all processed notes in the Knowledge Base. These notes have been enhanced with GPT-generated metadata 
      and are organized in date-based folders.
      
      Supports filtering by folder and pagination for large knowledge bases.
    parameters:
      - name: limit
        in: query
        schema:
          type: integer
          default: 50
          minimum: 1
          maximum: 100
        description: Maximum number of notes to return
      - name: offset
        in: query
        schema:
          type: integer
          default: 0
          minimum: 0
        description: Number of notes to skip for pagination
      - name: folder
        in: query
        schema:
          type: string
          example: "2025-07"
        description: Filter by specific KB subfolder (YYYY-MM format)
    responses:
      200:
        description: List of processed notes in the Knowledge Base
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                notes:
                  type: array
                  items:
                    type: object
                    properties:
                      filename:
                        type: string
                        example: "2025-07-03_weekly-meeting.md"
                      title:
                        type: string
                        example: "Weekly Meeting"
                      folder:
                        type: string
                        example: "2025-07"
                      path:
                        type: string
                        example: "/api/kb/notes/2025-07-03_weekly-meeting.md"
                      status:
                        type: string
                        example: "processed"
                      modified:
                        type: string
                        format: date-time
                      size:
                        type: integer
                pagination:
                  type: object
                  properties:
                    total:
                      type: integer
                    limit:
                      type: integer
                    offset:
                      type: integer
                    has_more:
                      type: boolean
      500:
        description: Error accessing Knowledge Base
    """
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
        folder_filter = request.args.get('folder')
        
        kb_path = load_config().get("kb_path")
        
        if folder_filter:
            # List specific subfolder
            folder_path = f"{kb_path}/{folder_filter}"
            entries = list_folder(folder_path)
            notes = []
            
            for item in entries:
                if item[".tag"] == "file" and item["name"].endswith(".md"):
                    # Extract title from filename
                    title = item["name"].replace('.md', '')
                    if '_' in title:
                        parts = title.split('_', 1)
                        if len(parts) > 1 and parts[0].count('-') == 2:
                            title = parts[1].replace('_', ' ').replace('-', ' ')
                    
                    notes.append({
                        "filename": item["name"],
                        "title": title,
                        "folder": folder_filter,
                        "path": f"/api/kb/notes/{item['name']}",
                        "status": "processed",
                        "modified": item.get("client_modified"),
                        "size": item.get("size")
                    })
        else:
            # List all folders and their contents
            entries = list_folder(kb_path)
            notes = []
            
            for folder_item in entries:
                if folder_item[".tag"] == "folder":
                    folder_name = folder_item["name"]
                    try:
                        folder_entries = list_folder(f"{kb_path}/{folder_name}")
                        for item in folder_entries:
                            if item[".tag"] == "file" and item["name"].endswith(".md"):
                                # Extract title from filename
                                title = item["name"].replace('.md', '')
                                if '_' in title:
                                    parts = title.split('_', 1)
                                    if len(parts) > 1 and parts[0].count('-') == 2:
                                        title = parts[1].replace('_', ' ').replace('-', ' ')
                                
                                notes.append({
                                    "filename": item["name"],
                                    "title": title,
                                    "folder": folder_name,
                                    "path": f"/api/kb/notes/{item['name']}",
                                    "status": "processed",
                                    "modified": item.get("client_modified"),
                                    "size": item.get("size")
                                })
                    except Exception as e:
                        log(f"⚠️ Could not access folder {folder_name}: {str(e)}", level="warning")
                        continue
        
        # Sort by modification date (newest first)
        notes.sort(key=lambda x: x.get("modified", ""), reverse=True)
        
        # Apply pagination
        total = len(notes)
        paginated_notes = notes[offset:offset + limit]
        
        log(f"📚 Listed {len(paginated_notes)} KB notes (total: {total})")
        
        return jsonify({
            "status": "success",
            "notes": paginated_notes,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }), 200
        
    except Exception as e:
        log(f"❌ List KB notes error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


@list_bp.route("/kb/folders", methods=["GET"])
@require_token
def list_kb_folders():
    """
    List Knowledge Base folders (organized by date).
    ---
    tags:
      - Knowledge Base Notes
    summary: List KB folders
    description: |
      Lists all folders in the Knowledge Base. These are typically organized by date (YYYY-MM format)
      and contain processed notes for that time period.
    responses:
      200:
        description: List of KB folders with note counts
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                folders:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                        example: "2025-07"
                      note_count:
                        type: integer
                        example: 15
                      path:
                        type: string
                        example: "/api/kb/notes?folder=2025-07"
                      latest_note:
                        type: string
                        format: date-time
                        example: "2025-07-03T14:30:00Z"
      500:
        description: Error accessing Knowledge Base
    """
    try:
        kb_path = load_config().get("kb_path")
        entries = list_folder(kb_path)
        
        folders = []
        for item in entries:
            if item[".tag"] == "folder":
                folder_name = item["name"]
                try:
                    # Get notes in this folder
                    folder_entries = list_folder(f"{kb_path}/{folder_name}")
                    note_files = [e for e in folder_entries if e[".tag"] == "file" and e["name"].endswith(".md")]
                    
                    # Find latest note
                    latest_note = None
                    if note_files:
                        latest_note = max(note_files, key=lambda x: x.get("client_modified", ""))["client_modified"]
                    
                    folders.append({
                        "name": folder_name,
                        "note_count": len(note_files),
                        "path": f"/api/kb/notes?folder={folder_name}",
                        "latest_note": latest_note
                    })
                    
                except Exception as e:
                    log(f"⚠️ Could not access folder {folder_name}: {str(e)}", level="warning")
                    # Add folder even if we can't read it
                    folders.append({
                        "name": folder_name,
                        "note_count": 0,
                        "path": f"/api/kb/notes?folder={folder_name}",
                        "latest_note": None
                    })
        
        # Sort folders by name (newest first for date-based folders)
        folders.sort(key=lambda x: x["name"], reverse=True)
        
        log(f"📁 Listed {len(folders)} KB folders")
        
        return jsonify({
            "status": "success",
            "folders": folders
        }), 200
        
    except Exception as e:
        log(f"❌ List KB folders error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# Export for app.py
kb_notes_list_routes = list_bp