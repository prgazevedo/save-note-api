# routes/scan.py - Notes-focused inbox scanning

from flask import Blueprint, request, jsonify
from utils.inbox_utils import scan_inbox_for_notes
from utils.config_utils import load_config, save_config, save_last_files  # Keep original functions
from utils.logging_utils import log
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
    description: |
      Returns raw notes in the Dropbox Inbox that haven't been processed with metadata yet. 
      These are candidates for GPT processing.
      
      REFACTORED: Now uses utils.inbox_utils.scan_inbox_for_notes() for better code reuse
      between Push and Pull modes, but maintains the same API contract and behavior.
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
                        example: "meeting ideas"
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
      400:
        description: Invalid query parameters
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
                  example: "Invalid query parameters"
      401:
        description: Missing or invalid Bearer token
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Invalid token"
      500:
        description: Error accessing Dropbox or internal server error
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
        # Get query parameters with validation (same as original)
        status = request.args.get('status', 'all')
        limit = min(int(request.args.get('limit', 50)), 100)  # Cap at 100
        offset = max(int(request.args.get('offset', 0)), 0)   # No negative offset
        
        # NEW: Use the extracted utility function instead of duplicating the logic
        scan_result = scan_inbox_for_notes(limit=limit, offset=offset)
        
        notes = scan_result["notes"]
        total = scan_result["total"]
        has_more = scan_result["has_more"]
        
        # Apply status filter (same as original - currently all inbox notes are unprocessed)
        if status == "unprocessed":
            # No filtering needed since all inbox notes are unprocessed
            pass
        
        # KEEP ORIGINAL BEHAVIOR: Update scan timestamp and save file list
        config = load_config()
        config["last_scan"] = datetime.now(timezone.utc).isoformat()
        save_config(config)
        save_last_files([note["filename"] for note in notes])  # Use original function name
        
        log(f"📥 Listed {len(notes)} inbox notes (total: {total})")
        
        # SAME RETURN FORMAT as original
        return jsonify({
            "status": "success",
            "notes": notes,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": has_more
            }
        }), 200
        
    except ValueError as e:
        # Handle invalid query parameters (same as original)
        log(f"❌ Invalid query parameters: {str(e)}", level="error")
        return jsonify({"status": "error", "message": "Invalid query parameters"}), 400
        
    except Exception as e:
        log(f"❌ List inbox notes error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# Export for app.py (same as original)
inbox_notes_routes = inbox_notes_bp