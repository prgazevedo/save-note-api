# routes/list.py

from flask import Blueprint, request, jsonify
from utils.config_utils import load_config
from services.dropbox_client import list_folder
from utils.logging_utils import log
from utils.token_utils import require_token
from dateutil.parser import isoparse
from datetime import datetime, timezone

list_bp = Blueprint("list", __name__, url_prefix="/api")

# ──────────── KNOWLEDGE BASE ────────────

@list_bp.route("/kb/notes", methods=["GET"])
@require_token
def list_kb_notes():
    """
    List all notes in the Knowledge Base.
    ---
    tags:
      - Knowledge Base Notes
    summary: List KB notes
    responses:
      200:
        description: List of KB files
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                files:
                  type: array
                  items:
                    type: string
    """
    try:
        kb_path = load_config().get("kb_path")
        entries = list_folder(kb_path)
        files = [item["name"] for item in entries if item[".tag"] == "file"]
        log(f"📚 Listed KB folder: {len(files)} files")
        return jsonify({"status": "success", "files": files}), 200
    except Exception as e:
        log(f"❌ list_kb error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


@list_bp.route("/kb/notes/folder", methods=["GET"])
@require_token
def list_kb_subfolder():
    """
    List notes in a specific KB subfolder (e.g. `2025-06`).
    ---
    tags:
      - Knowledge Base Notes
    summary: List KB subfolder
    parameters:
      - name: folder
        in: query
        required: true
        schema:
          type: string
        description: Subfolder inside the KB (e.g., 2025-06)
    responses:
      200:
        description: Files in subfolder
        content:
          application/json:
            example:
              status: success
              files: ["2025-06-01_test-note.md"]
      400:
        description: Missing folder parameter
      500:
        description: Dropbox error
    """
    folder = request.args.get("folder")
    if not folder:
        return jsonify({"status": "error", "message": "Missing folder parameter"}), 400

    try:
        base = load_config().get("kb_path")
        path = f"{base}/{folder}"
        entries = list_folder(path)
        files = [item["name"] for item in entries if item[".tag"] == "file"]
        log(f"📁 Listed subfolder '{folder}': {len(files)} files")
        return jsonify({"status": "success", "files": files}), 200
    except Exception as e:
        log(f"❌ list_kb_folder error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500

# ──────────── INBOX ────────────

@list_bp.route("/inbox/notes/new", methods=["GET"])
@require_token
def list_new_inbox_files():
    """
    List new Markdown files in Dropbox Inbox since last scan.
    ---
    tags:
      - Inbox Notes
    summary: List new Inbox notes
    description: Scans the Dropbox Inbox folder and lists `.md` files added since last scan.
    responses:
      200:
        description: List of new files
        content:
          application/json:
            example:
              status: success
              new_files: ["2025-07-01_test.md"]
      500:
        description: Dropbox error
    """
    config = load_config()
    inbox_path = config.get("inbox_path")
    last_scan = config.get("last_scan")
    last_scan_dt = isoparse(last_scan) if last_scan else None

    try:
        entries = list_folder(inbox_path)
        new_files = [
            item["name"]
            for item in entries
            if item[".tag"] == "file"
            and item["name"].endswith(".md")
            and (not last_scan_dt or isoparse(item["client_modified"]) > last_scan_dt)
        ]
        log(f"📬 New inbox files: {len(new_files)}")
        return jsonify({"status": "success", "new_files": new_files}), 200

    except Exception as e:
        log(f"❌ list_inbox_files error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# 👇 For app.py import
kb_notes_list_routes = list_bp
