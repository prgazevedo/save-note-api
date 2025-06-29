# utils/logging_utils.py

import json
import os
from datetime import datetime
os.makedirs("data", exist_ok=True)

LOG_FILE = os.path.join("data", "admin_log.json")
FILES_FILE = os.path.join("data", "last_files.json")


def log_event(message: str):
    entry = f"[{datetime.utcnow().isoformat()}] {message}"
    logs = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)

    logs.insert(0, entry)  # newest on top
    logs = logs[:50]       # limit to 50 entries

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def update_last_files(files: list[str]):
    with open(FILES_FILE, "w") as f:
        json.dump(files, f, indent=2)
