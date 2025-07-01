# routes/download.py

from flask import request, jsonify
from services.dropbox_client import download_note_from_dropbox
from utils.logging_utils import log


def get_kb_note():
    """
    Download a note from the Knowledge Base by filename.
    ---
    tags:
      - Dropbox
    summary: Download note
    parameters:
      - name: filename
        in: query
        required: true
        schema:
          type: string
        description: Name of the file to download (e.g., 2025-06-01_test.md)
    responses:
      200:
        description: File downloaded successfully
        content:
          application/json:
            example:
              status: success
              content: "# Markdown content..."
      400:
        description: Missing filename parameter
      404:
        description: File not found
      500:
        description: Unexpected error
    """
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"status": "error", "message": "Missing filename parameter"}), 400

    try:
        content = download_note_from_dropbox(filename)
        if not content:
            return jsonify({"status": "error", "message": "File not found"}), 404

        log(f"⬇️ Downloaded note: {filename}")
        return jsonify({"status": "success", "content": content}), 200

    except Exception as e:
        log(f"❌ download error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500
