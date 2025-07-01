# utils/logging_utils.py

import os
import json
import logging
from datetime import datetime
from logtail import LogtailHandler

# Environment flags
IS_RENDER = os.getenv("RENDER", "false").lower() == "true"
LOGTAIL_TOKEN = os.getenv("LOGTAIL_TOKEN")

# Configure main logger
logger = logging.getLogger("SaveNotesLogger")
logger.setLevel(logging.INFO)

# Log to stdout (Render captures this)
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s"
))
logger.addHandler(stdout_handler)

# Log to Logtail (if token is present)
if LOGTAIL_TOKEN:
    logtail_handler = LogtailHandler(source_token=LOGTAIL_TOKEN)
    logtail_handler.setFormatter(logging.Formatter(fmt="%(message)s"))  # Keep Logtail clean
    logger.addHandler(logtail_handler)

# Local fallback files (only for local/dev)
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "admin_log.json")
FILES_FILE = os.path.join(DATA_DIR, "last_files.json")

if not IS_RENDER:
    os.makedirs(DATA_DIR, exist_ok=True)

def log(message: str, level: str = "info"):
    """
    Logs to stdout, Logtail (if available), and a local file (if dev).
    """
    timestamp = datetime.utcnow().isoformat()
    json_log = {
        "timestamp": timestamp,
        "level": level.upper(),
        "message": message
    }

    # Structured log to handlers
    if level == "error":
        logger.error(json_log)
    elif level == "warning":
        logger.warning(json_log)
    else:
        logger.info(json_log)

    # Local JSON file (dev only)
    if not IS_RENDER:
        try:
            logs = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    logs = json.load(f)
        except Exception:
            logs = []

        logs.insert(0, f"[{timestamp}] {level.upper()}: {message}")
        logs = logs[:50]
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

def update_last_files(files: list[str]):
    if not IS_RENDER:
        with open(FILES_FILE, "w") as f:
            json.dump(files, f, indent=2)
