# routes/upload.py - Note creation and upload

from flask import Blueprint, request, jsonify
from services.dropbox_client import upload_note_to_dropbox
from utils.logging_utils import log
from utils.token_utils import require_token
from utils.dropbox_utils import sanitize_filename
from datetime import datetime

# Blueprint for note uploads
upload_note_bp = Blueprint("upload_note", __name__, url_prefix="/api")


@upload_note_bp.route("/inbox/notes", methods=["POST"])
@require_token
def create_inbox_note():
    """
    Create a new raw note in the Inbox for later GPT processing.
    ---
    tags:
      - Inbox Notes
    summary: Create raw note in Inbox
    description: |
      Creates a new raw note in the Dropbox Inbox. These notes are unprocessed and await GPT metadata generation.
      
      This endpoint is useful for:
      - Quickly capturing thoughts or ideas
      - Uploading handwritten notes (converted to text)
      - Saving content from external sources
      
      Notes created here will be discovered by the scan endpoint and can be processed with GPT metadata later.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - title
              - content
            properties:
              title:
                type: string
                example: "Meeting Ideas"
                description: "Title for the note (will be used in filename)"
              date:
                type: string
                format: date
                example: "2025-07-03"
                description: "Date for the note (defaults to today if not provided)"
              content:
                type: string
                example: "example"
                description: "Raw Markdown content of the note"
              source:
                type: string
                example: "handwritten"
                description: "Optional source of the note (handwritten, typed, web-clip, etc.)"
          examples:
            quick_note:
              summary: Quick idea capture
              value:
                title: "Project Brainstorm"
                content: "Content"
            handwritten_note:
              summary: Handwritten note upload
              value:
                title: "Meeting Notes"
                date: "2025-07-03"
                content: "Content"
                source: "handwritten"
    responses:
      201:
        description: Note created successfully in Inbox
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                note:
                  type: object
                  properties:
                    filename:
                      type: string
                      example: "2025-07-03_meeting-ideas.md"
                    title:
                      type: string
                      example: "Meeting Ideas"
                    path:
                      type: string
                      example: "/api/inbox/notes/2025-07-03_meeting-ideas.md"
                    status:
                      type: string
                      example: "unprocessed"
                    created:
                      type: string
                      format: date-time
                      example: "2025-07-03T14:30:00Z"
                message:
                  type: string
                  example: "Raw note created in Inbox. Ready for GPT processing."
      400:
        description: Invalid request or missing required fields
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
                  example: "Title and content are required"
      500:
        description: Upload failed
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
                  example: "Failed to upload note to Dropbox"
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "Request body required"}), 400

        title = data.get("title", "").strip()
        content = data.get("content", "").strip()
        date_str = data.get("date")
        source = data.get("source", "api")

        # Validate required fields
        if not title:
            return jsonify({"status": "error", "message": "Title is required"}), 400
        if not content:
            return jsonify({"status": "error", "message": "Content is required"}), 400

        # Use today's date if not provided
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        else:
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return jsonify({"status": "error", "message": f"Invalid date format: {date_str}. Use YYYY-MM-DD"}), 400

        # Create filename using date and sanitized title
        sanitized_title = sanitize_filename(title)
        filename = f"{date_str}_{sanitized_title}.md"

        # Upload to Dropbox Inbox
        upload_success = upload_note_to_dropbox(title, date_str, content)

        if upload_success:
            created_timestamp = datetime.now().isoformat()
            
            log(f"📝 Raw note created in Inbox: {filename} (source: {source})")
            
            return jsonify({
                "status": "success",
                "note": {
                    "filename": filename,
                    "title": title,
                    "path": f"/api/inbox/notes/{filename}",
                    "status": "unprocessed",
                    "created": created_timestamp,
                    "source": source
                },
                "message": "Raw note created in Inbox. Ready for GPT processing."
            }), 201
        else:
            log(f"❌ Failed to upload note: {filename}", level="error")
            return jsonify({
                "status": "error", 
                "message": "Failed to upload note to Dropbox"
            }), 500

    except Exception as e:
        log(f"❌ Note creation error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


@upload_note_bp.route("/kb/notes", methods=["POST"])
@require_token
def create_kb_note():
    """
    Create a note directly in the Knowledge Base (already processed with metadata).
    ---
    tags:
      - Knowledge Base Notes
    summary: Create processed note in KB
    description: |
      Creates a note directly in the Knowledge Base with complete YAML frontmatter.
      This bypasses the Inbox and GPT processing steps.
      
      Use this endpoint when you already have:
      - Complete YAML metadata
      - Structured content
      - No need for GPT processing
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - title
              - date
              - content
            properties:
              title:
                type: string
                example: "Quarterly Review Summary"
              date:
                type: string
                format: date
                example: "2025-07-03"
              content:
                type: string
                example: "example"
                description: "Complete Markdown content with YAML frontmatter"
              metadata:
                type: object
                description: "Optional additional metadata to merge with frontmatter"
                properties:
                  tags:
                    type: array
                    items:
                      type: string
                  author:
                    type: string
                  summary:
                    type: string
          examples:
            complete_note:
              summary: Note with full YAML frontmatter
              value:
                title: "Project Retrospective"
                date: "2025-07-03"
                content: "Content"
    responses:
      201:
        description: Note created successfully in Knowledge Base
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                note:
                  type: object
                  properties:
                    filename:
                      type: string
                      example: "2025-07-03_quarterly-review-summary.md"
                    kb_path:
                      type: string
                      example: "/Apps/SaveNotesGPT/NotesKB/2025-07/2025-07-03_quarterly-review-summary.md"
                    status:
                      type: string
                      example: "processed"
                message:
                  type: string
                  example: "Note created directly in Knowledge Base"
      400:
        description: Invalid request
      500:
        description: Upload failed
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "Request body required"}), 400

        title = data.get("title", "").strip()
        content = data.get("content", "").strip()
        date_str = data.get("date")

        # Validate required fields
        if not title or not content or not date_str:
            return jsonify({"status": "error", "message": "Title, date, and content are required"}), 400

        # Validate date format
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"status": "error", "message": f"Invalid date format: {date_str}. Use YYYY-MM-DD"}), 400

        # Import here to avoid circular imports
        from services.dropbox_client import upload_structured_note
        
        # Create KB path
        subfolder = parsed_date.strftime("%Y-%m")
        sanitized_title = sanitize_filename(title)
        filename = f"{date_str}_{sanitized_title}.md"
        kb_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{filename}"

        # Upload directly to KB
        upload_success = upload_structured_note(kb_path, content)

        if upload_success:
            log(f"📚 Note created directly in KB: {kb_path}")
            
            return jsonify({
                "status": "success",
                "note": {
                    "filename": filename,
                    "kb_path": kb_path,
                    "status": "processed"
                },
                "message": "Note created directly in Knowledge Base"
            }), 201
        else:
            log(f"❌ Failed to create KB note: {filename}", level="error")
            return jsonify({
                "status": "error", 
                "message": "Failed to upload note to Knowledge Base"
            }), 500

    except Exception as e:
        log(f"❌ KB note creation error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# Export for app.py
upload_note_api = upload_note_bp