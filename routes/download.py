from flask import Blueprint, jsonify
from services.dropbox_client import download_note_from_dropbox
from utils.logging_utils import log
from utils.token_utils import require_token

download_bp = Blueprint("download", __name__, url_prefix="/api")


@download_bp.route("/kb/notes/<filename>", methods=["GET"])
@require_token
def get_kb_note(filename):
    """
    Download a note from the Knowledge Base.
    ---
    tags:
      - Knowledge Base Notes
    summary: Get KB note by filename
    parameters:
      - name: filename
        in: path
        required: true
        schema:
          type: string
        description: Filename (e.g. 2025-06-01_test.md)
    responses:
      200:
        description: File downloaded
        content:
          application/json:
            example:
              status: success
              content: "# Markdown content..."
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        content = download_note_from_dropbox(filename)
        if not content:
            return jsonify({"status": "error", "message": "File not found"}), 404

        log(f"⬇️ Downloaded KB note: {filename}")
        return jsonify({"status": "success", "content": content}), 200

    except Exception as e:
        log(f"❌ KB download error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


@download_bp.route("/inbox/notes/<filename>", methods=["GET"])
@require_token
def get_inbox_note(filename):
    """
    Download a raw note from the Dropbox Inbox folder.
    ---
    tags:
      - Inbox Notes
    summary: Get Inbox note by filename
    parameters:
      - name: filename
        in: path
        required: true
        schema:
          type: string
        description: Filename to fetch (e.g. README.md)
    responses:
      200:
        description: File downloaded
        content:
          application/json:
            example:
              status: success
              content: "# Raw Markdown content..."
      404:
        description: File not found
      500:
        description: Server error
    """
    try:
        content = download_note_from_dropbox(filename, folder="Inbox")
        if not content:
            return jsonify({"status": "error", "message": "File not found"}), 404

        log(f"📥 Downloaded Inbox note: {filename}")
        return jsonify({"status": "success", "content": content}), 200

    except Exception as e:
        log(f"❌ Inbox download error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# 👇 Import this in app.py
download_routes = download_bp
