# utils/logging_utils.py

import os
import json
import logging
from datetime import datetime

ENV = os.getenv("RENDER", "false").lower()
IS_RENDER = ENV == "true"

# Structured JSON logs (for Render streaming)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# Local file fallback (for dev only)
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "admin_log.json")
FILES_FILE = os.path.join(DATA_DIR, "last_files.json")

if not IS_RENDER:
    os.makedirs(DATA_DIR, exist_ok=True)

def log(message: str, level: str = "info"):
    """
    Unified logger for all levels.
    Logs to stdout and (if not on Render) also to admin_log.json.
    """
    timestamp = datetime.utcnow().isoformat()
    json_log = {
        "timestamp": timestamp,
        "level": level.upper(),
        "message": message
    }

    # Always log to stdout
    if level == "error":
        logging.error(json.dumps(json_log))
    elif level == "warning":
        logging.warning(json.dumps(json_log))
    else:
        logging.info(json.dumps(json_log))

    # Only save to local file if not on Render
    if not IS_RENDER:
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        logs.insert(0, f"[{timestamp}] {level.upper()}: {message}")
        logs = logs[:50]
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

def update_last_files(files: list[str]):
    if not IS_RENDER:
        with open(FILES_FILE, "w") as f:
            json.dump(files, f, indent=2)
