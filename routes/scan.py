# routes/scan.py

from flask import Blueprint, jsonify
from datetime import datetime
from dateutil.parser import isoparse
from dropbox_client import list_folder
from utils.config_utils import load_config, save_config, save_last_files
from utils.logging_utils import log_event

bp = Blueprint("scan", __name__, url_prefix="/admin")


@bp.route("/scan_inbox", methods=["POST"])
def scan_inbox():
    config = load_config()
    inbox_path = config.get("inbox_path", "/Inbox")
    last_scan = config.get("last_scan")
    last_scan_dt = isoparse(last_scan) if last_scan else None

    try:
        entries = list_folder(inbox_path)
        new_files = []

        for item in entries:
            if item[".tag"] == "file":
                mod_time = isoparse(item["client_modified"])
                if not last_scan_dt or mod_time > last_scan_dt:
                    new_files.append(item["name"])

        config["last_scan"] = datetime.utcnow().isoformat()
        save_config(config)
        save_last_files(new_files)
        log_event(f"📥 Scanned inbox: {len(new_files)} new file(s)")

        return jsonify({
            "status": "success",
            "new_files": new_files,
            "count": len(new_files)
        }), 200

    except Exception as e:
        log_event(f"❌ Dropbox scan error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
