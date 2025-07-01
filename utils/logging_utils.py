# utils/logging_utils.py

import os
import json
import logging
from datetime import datetime
from logtail import LogtailHandler

# --- Config Flags ---
IS_RENDER = os.getenv("RENDER", "false").lower() == "true"
LOGTAIL_TOKEN = os.getenv("LOGTAIL_TOKEN")

# --- Paths ---
DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "admin_log.json")
FILES_FILE = os.path.join(DATA_DIR, "last_files.json")

if not IS_RENDER:
    os.makedirs(DATA_DIR, exist_ok=True)

# --- Logger Setup ---
logger = logging.getLogger("SaveNotesLogger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent double logs

# Avoid duplicate handlers
if not logger.handlers:
    # Stdout (Render reads this)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(stdout_handler)

    # Logtail (if available)
    if LOGTAIL_TOKEN:
        logtail_handler = LogtailHandler(source_token=LOGTAIL_TOKEN)
        logtail_handler.setFormatter(logging.Formatter(fmt="%(message)s"))
        logger.addHandler(logtail_handler)

# --- Log Function ---
def log(message: str, level: str = "info"):
    """
    Logs to stdout + Logtail (string), and to local JSON (structured).
    """
    timestamp = datetime.utcnow().isoformat()
    level = level.lower()

    # Render + Logtail = plain string
    log_str = f"[{timestamp}] {level.upper()}: {message}"

    if level == "error":
        logger.error(log_str)
    elif level == "warning":
        logger.warning(log_str)
    else:
        logger.info(log_str)

    # Local structured JSON log
    if not IS_RENDER:
        try:
            logs = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    logs = json.load(f)
        except Exception:
            logs = []

        logs.insert(0, {
            "timestamp": timestamp,
            "level": level.upper(),
            "message": message
        })
        logs = logs[:50]
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

# --- Helper for storing file history ---
def update_last_files(files: list[str]):
    if not IS_RENDER:
        with open(FILES_FILE, "w") as f:
            json.dump(files, f, indent=2)
