# routes/api.py

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from dateutil.parser import isoparse
from utils.config_utils import load_config, save_config, save_last_files
from utils.logging_utils import log_event
from services.dropbox_client import list_folder, download_note_from_dropbox
from services.process_note import process_raw_markdown

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/api/scan_inbox", methods=["POST"])
def api_scan_inbox():
    """
    Scan Dropbox Inbox for new markdown files.
    ---
    tags:
      - Dropbox
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
        log_event(f"❌ scan_inbox error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/process_file", methods=["POST"])
def api_process_file():
    """
    Processa um único ficheiro Markdown do Inbox pelo nome.
    Exemplo payload: { "filename": "2025-06-30_MinhaNota.md" }
    """
    data = request.get_json()
    if not data or "filename" not in data:
        return jsonify({"status": "error", "message": "Missing 'filename' in request"}), 400

    filename = data["filename"]
    try:
        raw_md = download_note_from_dropbox(filename)
        result = process_raw_markdown(raw_md, filename)
        log_event(f"📦 Processed file via API: {filename}")
        return jsonify({"status": "success", "result": result}), 200
    except Exception as e:
        log_event(f"❌ process_file error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@bp.route("/scan_and_process", methods=["POST"])
def api_scan_and_process():
    """
    Combina scan + process de novos ficheiros Markdown do inbox.
    Atualiza o last_scan e devolve os resultados processados.
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
            result = process_raw_markdown(raw_md, filename)
            processed.append(result)

        # Atualizar estado
        config["last_scan"] = datetime.now(timezone.utc).isoformat()
        save_config(config)
        save_last_files(new_files)
        log_event(f"🤖 scan_and_process: {len(processed)} file(s)")

        return jsonify({
            "status": "success",
            "count": len(processed),
            "processed": processed
        }), 200

    except Exception as e:
        log_event(f"❌ scan_and_process error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
