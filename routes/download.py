# routes/download.py

from flask import Blueprint, request, jsonify
from services.dropbox_client import download_note_from_dropbox
from utils.logging_utils import log

download_bp = Blueprint("download", __name__, url_prefix="/api")


@download_bp.route("/get_kb_note", methods=["GET"])
def get_kb_note():
    """
    Download a note from the Knowledge Base by filename.
    ---
    tags:
      - Routes
    summary: Download note from KB
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

        log(f"⬇️ Downloaded KB note: {filename}")
        return jsonify({"status": "success", "content": content}), 200

    except Exception as e:
        log(f"❌ download KB error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


@download_bp.route("/get_inbox_note", methods=["GET"])
def get_inbox_note():
    """
    Download a raw note from the Dropbox Inbox folder.
    ---
    tags:
      - Routes
    summary: Download note from Inbox
    parameters:
      - name: filename
        in: query
        required: true
        schema:
          type: string
        description: Name of the file to download from Inbox (e.g., README.md)
    responses:
      200:
        description: File downloaded successfully
        content:
          application/json:
            example:
              status: success
              content: "# Raw Markdown content..."
      400:
        description: Missing filename parameter
      404:
        description: File not found in Inbox
      500:
        description: Unexpected error
    """
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"status": "error", "message": "Missing filename parameter"}), 400

    try:
        content = download_note_from_dropbox(filename, folder="Inbox")
        if not content:
            return jsonify({"status": "error", "message": "File not found"}), 404

        log(f"📥 Downloaded Inbox note: {filename}")
        return jsonify({"status": "success", "content": content}), 200

    except Exception as e:
        log(f"❌ download Inbox error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# 👇 Import this in app.py
download_routes = download_bp
