from flask import Blueprint, request, jsonify
from services.dropbox_client import upload_note_to_dropbox
from utils.logging_utils import log
from utils.token_utils import require_token

# All routes under /api
upload_note_bp = Blueprint("upload_note", __name__, url_prefix="/api")

@upload_note_bp.route("/inbox/notes", methods=["POST"])
@require_token
def upload_note():
    """
    Upload a raw Markdown note to Dropbox Inbox.
    ---
    tags:
      - Inbox Notes
    summary: Upload raw note to Inbox
    description: Receives a Markdown file with basic metadata and uploads it to the unstructured Dropbox Inbox folder.
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
                example: Test Note
              date:
                type: string
                format: date
                example: 2025-07-01
              content:
                type: string
                example: "# Title\n\nThis is the note content."
    responses:
      200:
        description: Note uploaded successfully
        content:
          application/json:
            example:
              status: success
              message: Note uploaded to Dropbox.
      400:
        description: Missing required fields
        content:
          application/json:
            example:
              status: error
              message: Missing title, date, or content
      500:
        description: Internal server error
        content:
          application/json:
            example:
              status: error
              message: Unexpected error message
    """
    try:
        data = request.get_json()

        title = data.get("title")
        date = data.get("date")
        content = data.get("content")

        if not title or not date or not content:
            return jsonify({"status": "error", "message": "Missing title, date, or content"}), 400

        success = upload_note_to_dropbox(title, date, content)

        if success:
            log(f"📤 Note uploaded to Inbox: {title} ({date})")
            return jsonify({"status": "success", "message": "Note uploaded to Dropbox."}), 200
        else:
            log(f"❌ Upload failed: {title} ({date})", level="error")
            return jsonify({"status": "error", "message": "Failed to upload note."}), 500

    except Exception as e:
        log(f"❌ Exception during upload: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# 👇 For app.py import
upload_note_api = upload_note_bp
