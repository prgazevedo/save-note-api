# routes/scan.py

from flask import Blueprint, jsonify
from utils.config_utils import load_config, save_config, save_last_files
from utils.logging_utils import log
from services.dropbox_client import list_folder
from datetime import datetime, timezone

bp = Blueprint("scan", __name__, url_prefix="/scan")


@bp.route("/inbox", methods=["POST"])
def scan_inbox_manual():
    """
    Manual scan of Dropbox Inbox for new Markdown files.
    ---
    tags:
      - Routes
    summary: Scan Inbox (manual)
    description: |
      Triggers a manual scan of the Dropbox Inbox folder for `.md` files.
      Updates `last_scan` and `last_files.json`.
    responses:
      200:
        description: List of newly discovered files
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

        # Update state
        config["last_scan"] = datetime.now(timezone.utc).isoformat()
        save_config(config)
        save_last_files(new_files)
        log(f"📦 Manual scan: {len(new_files)} file(s)")

        return jsonify({"status": "success", "new_files": new_files}), 200

    except Exception as e:
        log(f"❌ scan error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500
