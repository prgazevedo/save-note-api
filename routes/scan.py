# routes/inbox_files.py

from flask import Blueprint, jsonify
from utils.config_utils import load_config, save_config, save_last_files
from utils.logging_utils import log
from services.dropbox_client import list_folder
from utils.token_utils import require_token
from datetime import datetime, timezone

inbox_files_bp = Blueprint("inbox_files", __name__, url_prefix="/api/inbox")


@inbox_files_bp.route("/files", methods=["GET"])
@require_token
def list_inbox_files():
    """
    List all Markdown files in the Dropbox Inbox.
    ---
    tags:
      - Inbox Notes
    summary: List Inbox Files
    description: Returns a list of `.md` files found in the Dropbox Inbox folder.
    responses:
      200:
        description: List of discovered files
        content:
          application/json:
            example:
              status: success
              new_files:
                - 2025-06-01_test-note.md
                - 2025-06-02_refactor_patch_test.md
      500:
        description: Dropbox error
    """
    try:
        config = load_config()
        inbox_path = config.get("inbox_path")

        entries = list_folder(inbox_path)
        new_files = [item["name"] for item in entries if item[".tag"] == "file" and item["name"].endswith(".md")]

        # Update local state
        config["last_scan"] = datetime.now(timezone.utc).isoformat()
        save_config(config)
        save_last_files(new_files)

        log(f"📦 Listed inbox: {len(new_files)} file(s)")
        return jsonify({"status": "success", "new_files": new_files}), 200

    except Exception as e:
        log(f"❌ list inbox files error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# 👇 For app.py
inbox_files_routes = inbox_files_bp
