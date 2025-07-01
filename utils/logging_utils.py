import os
import json
import logging
from datetime import datetime

# --- Config Flags ---
IS_RENDER = os.getenv("RENDER", "false").lower() == "true"

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
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(stdout_handler)

# --- Log Function ---
def log(message: str, level: str = "info"):
    """
    Logs to stdout (picked up by Render & Logtail) and optionally to file in dev.
    """
    timestamp = datetime.utcnow().isoformat()
    level = level.lower()
    log_str = f"[{timestamp}] {level.upper()}: {message}"

    if level == "error":
        logger.error(log_str)
    elif level == "warning":
        logger.warning(log_str)
    else:
        logger.info(log_str)

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
