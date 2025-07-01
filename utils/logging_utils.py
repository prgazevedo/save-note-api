import os
import json
import logging
from datetime import datetime

# Create data dir (for local usage only)
os.makedirs("data", exist_ok=True)

LOG_FILE = os.path.join("data", "admin_log.json")
FILES_FILE = os.path.join("data", "last_files.json")

# Configure structured stdout logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def log(message: str, level: str = "info"):
    """
    Unified logger for info, warning, error, etc.
    Outputs to stdout and, if in dev mode, to admin_log.json.
    """
    timestamp = datetime.utcnow().isoformat()
    entry = f"[{timestamp}] {level.upper()}: {message}"

    # Always log to stdout
    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    else:
        logging.info(message)

    # If running locally, also write to local JSON log
    if os.getenv("RENDER") != "true":
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        logs.insert(0, entry)
        logs = logs[:50]
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

def update_last_files(files: list[str]):
    """
    Saves list of recently processed files to local file.
    """
    with open(FILES_FILE, "w") as f:
        json.dump(files, f, indent=2)
