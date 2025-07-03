# routes/scan.py - Notes-focused inbox scanning

from flask import Blueprint, request, jsonify
from utils.config_utils import load_config, save_config, save_last_files
from utils.logging_utils import log
from services.dropbox_client import list_folder
from utils.token_utils import require_token
from datetime import datetime, timezone

inbox_notes_bp = Blueprint("inbox_notes", __name__, url_prefix="/api/inbox")


@inbox_notes_bp.route("/notes", methods=["GET"])
@require_token
def list_inbox_notes():
    """
    List raw notes in the inbox awaiting GPT processing.
    ---
    tags:
      - Inbox Notes
    summary: List Inbox Notes
    description: Returns raw notes in the Dropbox Inbox that haven't been processed with metadata yet. These are candidates for GPT processing.
    parameters:
      - name: status
        in: query
        schema:
          type: string
          enum: [all, unprocessed]
          default: all
        description: Filter notes by processing status
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
    responses:
      200:
        description: List of raw notes awaiting processing
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
                        example: "2025-07-03_meeting-ideas.md"
                      title:
                        type: string
                        example: "meeting-ideas"
                      status:
                        type: string
                        example: "unprocessed"
                      created:
                        type: string
                        format: date-time
                        example: "2025-07-03T10:30:00Z"
                      size:
                        type: integer
                        example: 1024
                      path:
                        type: string
                        example: "/api/inbox/notes/2025-07-03_meeting-ideas.md"
                pagination:
                  type: object
                  properties:
                    total:
                      type: integer
                      example: 5
                    limit:
                      type: integer
                      example: 50
                    offset:
                      type: integer
                      example: 0
                    has_more:
                      type: boolean
                      example: false
      500:
        description: Error accessing Dropbox
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: error
                message:
                  type: string
                  example: "Dropbox connection failed"
    """
    try:
        # Get query parameters with validation
        status = request.args.get('status', 'all')
        limit = min(int(request.args.get('limit', 50)), 100)  # Cap at 100
        offset = max(int(request.args.get('offset', 0)), 0)   # No negative offset
        
        config = load_config()
        inbox_path = config.get("inbox_path")
        
        # Get raw entries from Dropbox
        entries = list_folder(inbox_path)
        
        # Transform to notes with meaningful metadata
        notes = []
        for item in entries:
            if item[".tag"] == "file" and item["name"].endswith(".md"):
                # Extract title from filename (remove date prefix and extension)
                filename = item["name"]
                title = filename.replace('.md', '')
                if '_' in title:
                    # Remove date prefix like "2025-07-03_"
                    parts = title.split('_', 1)
                    if len(parts) > 1 and parts[0].count('-') == 2:
                        title = parts[1]
                
                notes.append({
                    "filename": filename,
                    "title": title.replace('_', ' ').replace('-', ' '),
                    "status": "unprocessed",  # All inbox notes are unprocessed
                    "created": item.get("client_modified"),
                    "size": item.get("size"),
                    "path": f"/api/inbox/notes/{filename}"
                })
        
        # Apply status filter (currently all inbox notes are unprocessed)
        if status == "unprocessed":
            # No filtering needed since all inbox notes are unprocessed
            pass
        
        # Sort by creation date (newest first)
        notes.sort(key=lambda x: x.get("created", ""), reverse=True)
        
        # Apply pagination
        total = len(notes)
        paginated_notes = notes[offset:offset + limit]
        
        # Update scan timestamp and save file list
        config["last_scan"] = datetime.now(timezone.utc).isoformat()
        save_config(config)
        save_last_files([note["filename"] for note in paginated_notes])
        
        log(f"📥 Listed {len(paginated_notes)} inbox notes (total: {total})")
        
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
        
    except ValueError as e:
        # Handle invalid query parameters
        log(f"❌ Invalid query parameters: {str(e)}", level="error")
        return jsonify({"status": "error", "message": "Invalid query parameters"}), 400
        
    except Exception as e:
        log(f"❌ List inbox notes error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# Export for app.py
inbox_notes_routes = inbox_notes_bp