# routes/list.py

from flask import request, jsonify
from utils.config_utils import load_config
from services.dropbox_client import list_folder
from utils.logging_utils import log


def list_kb():
    """
    List all files in the knowledge base folder.
    ---
    tags:
      - Routes
    summary: List KB folder
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


def list_kb_folder():
    """
    List files inside a specific subfolder in the KB (e.g. `2025-06`).
    ---
    tags:
      - Routes
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
        description: Files found in subfolder
        content:
          application/json:
            example:
              status: success
              files: ["2025-06-01_test-note.md"]
      400:
        description: Missing folder parameter
      500:
        description: Error accessing Dropbox
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
