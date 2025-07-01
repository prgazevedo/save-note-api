# routes/api.py

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from dateutil.parser import isoparse
from utils.config_utils import load_config, save_config, save_last_files
from utils.logging_utils import log
from services.dropbox_client import list_folder, download_note_from_dropbox
from services.process_service import archive_note_with_yaml

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/scan_inbox", methods=["POST"])
def api_scan_inbox():
    """
    Scan Dropbox Inbox for new markdown files.
    ---
    tags:
      - Routes
    responses:
      200:
        description: Files listed
        schema:
          type: object
          properties:
            status:
              type: string
            new_files:
              type: array
              items:
                type: string
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

        return jsonify({"status": "success", "new_files": new_files}), 200
    except Exception as e:
        log(f"❌ scan_inbox error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/process_file", methods=["POST"])
def api_process_file():
    """
    Process a specific Markdown file from the Dropbox Inbox by name.
    ---
    tags:
      - Dropbox
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - filename
            properties:
              filename:
                type: string
                example: 2025-06-30_MinhaNota.md
    responses:
      200:
        description: File processed successfully
        content:
          application/json:
            example:
              status: success
              result:
                dropbox_path: /Apps/SaveNotesGPT/NotesKB/2025-06/2025-06-30_minha-nota.md
                upload: true
      400:
        description: Missing filename in request
      500:
        description: Error processing file
    """
    data = request.get_json()
    if not data or "filename" not in data:
        return jsonify({"status": "error", "message": "Missing 'filename' in request"}), 400

    filename = data["filename"]
    try:
        raw_md = download_note_from_dropbox(filename)
        result = archive_note_with_yaml(raw_md, filename)
        log(f"📦 Processed file via API: {filename}")
        return jsonify({"status": "success", "result": result}), 200
    except Exception as e:
        log(f"❌ process_file error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/scan_and_process", methods=["POST"])
def api_scan_and_process():
    """
    Scan Dropbox Inbox for new Markdown files and process them into structured notes.
    ---
    tags:
      - Dropbox
    summary: Scan & Process new files
    description: |
      Combines scanning and processing of newly added `.md` files in the Dropbox Inbox folder
      since the last scan. Uses and updates `last_scan` timestamp in `admin_config.json`.
      Saves processed file list and logs the operation.
    responses:
      200:
        description: Successfully processed new files
        content:
          application/json:
            example:
              status: success
              count: 2
              processed:
                - dropbox_path: /Apps/SaveNotesGPT/NotesKB/2025-06/2025-06-01_test-note.md
                  upload: true
                - dropbox_path: /Apps/SaveNotesGPT/NotesKB/2025-06/2025-06-02_refactor_patch_test.md
                  upload: true
      500:
        description: Server error while processing files
        content:
          application/json:
            example:
              status: error
              message: "Dropbox API error or invalid metadata"
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

        processed = []
        for filename in new_files:
            raw_md = download_note_from_dropbox(filename)
            result = archive_note_with_yaml(raw_md, filename)
            processed.append(result)

        # Atualizar estado
        config["last_scan"] = datetime.now(timezone.utc).isoformat()
        save_config(config)
        save_last_files(new_files)
        log(f"🤖 scan_and_process: {len(processed)} file(s)")

        return jsonify({
            "status": "success",
            "count": len(processed),
            "processed": processed
        }), 200

    except Exception as e:
        log(f"❌ scan_and_process error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
