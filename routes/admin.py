# routes/admin.py

import os
import json
from datetime import datetime
from flask import Blueprint, session, redirect, url_for, render_template, request, flash

bp = Blueprint("admin", __name__, url_prefix="/admin")

# 📁 Data file paths
DATA_DIR = "data"
CONFIG_FILE = os.path.join(DATA_DIR, "admin_config.json")
LOG_FILE = os.path.join(DATA_DIR, "admin_log.json")
FILES_FILE = os.path.join(DATA_DIR, "last_files.json")

def load_json_file(path, fallback):
    """
    Loads JSON from file or returns fallback if not found.
    """
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return fallback

def save_json_file(path, data):
    """
    Saves JSON to file, ensuring the parent folder exists.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


@bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """
    Admin dashboard for viewing/editing config and logs.
    Accessible only to logged-in users.
    """
    if "authenticated_user" not in session:
        return redirect(url_for("auth.login"))

    # Load persisted state
    config = load_json_file(CONFIG_FILE, {
        "kb_path": "/NotesKB",
        "inbox_path": "/Inbox",
        "last_scan": None
    })
    logs = load_json_file(LOG_FILE, [])
    files = load_json_file(FILES_FILE, [])

    if request.method == "POST":
        # Handle config update
        config["kb_path"] = request.form.get("kb_path", config["kb_path"]).strip()
        config["inbox_path"] = request.form.get("inbox_path", config["inbox_path"]).strip()

        if "scan_inbox" in request.form:
            config["last_scan"] = datetime.utcnow().isoformat()
            flash(f"Inbox scan triggered at {config['last_scan']}", "info")
        else:
            flash("Configuration updated successfully.", "success")

        save_json_file(CONFIG_FILE, config)
        return redirect(url_for("admin.dashboard"))

    return render_template("dashboard.html", config=config, logs=logs, files=files)
