# routes/download.py - Notes content retrieval

from flask import Blueprint, jsonify
from services.dropbox_client import download_note_from_dropbox
from utils.logging_utils import log
from utils.token_utils import require_token

download_bp = Blueprint("download", __name__, url_prefix="/api")


@download_bp.route("/kb/notes/<filename>", methods=["GET"])
@require_token
def get_kb_note(filename):
    """
    Get a processed note from the Knowledge Base.
    ---
    tags:
      - Knowledge Base Notes
    summary: Get KB note content
    description: Retrieve the complete content of a processed note from the Knowledge Base. These notes include YAML frontmatter with GPT-generated metadata.
    parameters:
      - name: filename
        in: path
        required: true
        schema:
          type: string
          example: "2025-07-03_meeting-notes.md"
        description: Filename of the processed note in the Knowledge Base
    responses:
      200:
        description: Processed note with metadata and content
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
                      example: "2025-07-03_meeting-notes.md"
                    content:
                      type: string
                      example: "example"
                    content_type:
                      type: string
                      example: "text/markdown"
                    source:
                      type: string
                      example: "knowledge_base"
                    has_metadata:
                      type: boolean
                      example: true
      404:
        description: Note not found in Knowledge Base
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
                  example: "Note not found in Knowledge Base"
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
                  example: "Failed to retrieve note from storage"
    """
    try:
        content = download_note_from_dropbox(filename)
        if not content:
            log(f"📚 KB note not found: {filename}", level="warning")
            return jsonify({
                "status": "error", 
                "message": "Note not found in Knowledge Base"
            }), 404

        log(f"📚 Retrieved KB note: {filename}")
        return jsonify({
            "status": "success",
            "note": {
                "filename": filename,
                "content": content,
                "content_type": "text/markdown",
                "source": "knowledge_base",
                "has_metadata": content.strip().startswith("---")  # Check for YAML frontmatter
            }
        }), 200

    except Exception as e:
        log(f"❌ KB note retrieval error: {str(e)}", level="error")
        return jsonify({
            "status": "error", 
            "message": "Failed to retrieve note from storage"
        }), 500


@download_bp.route("/inbox/notes/<filename>", methods=["GET"])
@require_token
def get_inbox_note(filename):
    """
    Get a raw note from the Inbox (before GPT processing).
    ---
    tags:
      - Inbox Notes
    summary: Get raw inbox note content
    description: Retrieve the raw content of an unprocessed note from the Inbox. These notes typically lack YAML frontmatter and await GPT processing to add metadata.
    parameters:
      - name: filename
        in: path
        required: true
        schema:
          type: string
          example: "2025-07-03_meeting-ideas.md"
        description: Filename of the raw note in the Inbox
    responses:
      200:
        description: Raw note content without metadata
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
                    content:
                      type: string
                      example: "# Meeting Ideas\n\n- Discuss Q4 roadmap\n- Review team capacity\n- Plan holiday schedule"
                    content_type:
                      type: string
                      example: "text/markdown"
                    source:
                      type: string
                      example: "inbox"
                    has_metadata:
                      type: boolean
                      example: false
                    processing_status:
                      type: string
                      example: "unprocessed"
      404:
        description: Note not found in Inbox
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
                  example: "Note not found in Inbox"
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
                  example: "Failed to retrieve note from storage"
    """
    try:
        content = download_note_from_dropbox(filename, folder="Inbox")
        if not content:
            log(f"📥 Inbox note not found: {filename}", level="warning")
            return jsonify({
                "status": "error", 
                "message": "Note not found in Inbox"
            }), 404

        log(f"📥 Retrieved inbox note: {filename}")
        return jsonify({
            "status": "success",
            "note": {
                "filename": filename,
                "content": content,
                "content_type": "text/markdown",
                "source": "inbox",
                "has_metadata": content.strip().startswith("---"),  # Usually false for inbox
                "processing_status": "unprocessed"
            }
        }), 200

    except Exception as e:
        log(f"❌ Inbox note retrieval error: {str(e)}", level="error")
        return jsonify({
            "status": "error", 
            "message": "Failed to retrieve note from storage"
        }), 500


# Export for app.py
download_routes = download_bp