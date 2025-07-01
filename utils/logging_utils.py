# utils/logging_utils.py

import os
import json
import logging
import requests
from datetime import datetime

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

if not logger.handlers:
    # Stdout handler (Render reads this)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(stdout_handler)

# --- Logtail HTTP Fallback (bypassing SDK) ---
def send_to_logtail(message: str):
    if not LOGTAIL_TOKEN:
        return

    try:
        requests.post(
            url="https://in.logs.betterstack.com",
            headers={
                "Authorization": f"Bearer {LOGTAIL_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"message": message},
            timeout=2
        )
    except Exception as e:
        logger.warning(f"Logtail send failed: {e}")

# --- Log Function ---
def log(message: str, level: str = "info"):
    """
    Logs to stdout, Logtail (via HTTP), and to local JSON file (dev only).
    """
    timestamp = datetime.utcnow().isoformat()
    level = level.lower()
    log_str = f"[{timestamp}] {level.upper()}: {message}"

    # Stdout (Render)
    if level == "error":
        logger.error(log_str)
    elif level == "warning":
        logger.warning(log_str)
    else:
        logger.info(log_str)

    # Logtail (HTTP)
    send_to_logtail(log_str)

    # Dev-only local JSON log
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
