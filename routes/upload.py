# routes/upload.py

from flask import request, jsonify
from services.dropbox_client import upload_note_to_dropbox
from utils.logging_utils import log

def upload_note():
    """
    Upload a raw note to Dropbox (unstructured).
    ---
    tags:
      - Routes
    summary: Upload a note
    description: Uploads a note file to the configured Dropbox path based on title and date.
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
                example: Minha Nota
              date:
                type: string
                example: 2025-07-01
              content:
                type: string
                example: "# Título\n\nEste é o conteúdo da nota"
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
            log(f"📤 Note uploaded: {title} ({date})")
            return jsonify({"status": "success", "message": "Note uploaded to Dropbox."}), 200
        else:
            log(f"❌ Upload failed for: {title} ({date})", level="error")
            return jsonify({"status": "error", "message": "Failed to upload note."}), 500

    except Exception as e:
        log(f"❌ Exception during note upload: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500
