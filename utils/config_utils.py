import os
import json

BASE_DIR = "data"
CONFIG_FILE = os.path.join(BASE_DIR, "admin_config.json")
LOG_FILE = os.path.join(BASE_DIR, "admin_log.json")
FILES_FILE = os.path.join(BASE_DIR, "last_files.json")
DEFAULT_CONFIG = {
    "kb_path": "/Apps/SaveNotesGPT/NotesKB",
    "inbox_path": "/Apps/SaveNotesGPT/Inbox",
    "last_scan": None
}

def ensure_data_dir():
    os.makedirs(BASE_DIR, exist_ok=True)

def load_json(path, fallback):
    ensure_data_dir()
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        # Auto-create the file with the fallback content
        save_json(path, fallback)
        return fallback

def save_json(path, data):
    ensure_data_dir()
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Shorthands for common ops
def load_config():
    return load_json(CONFIG_FILE, DEFAULT_CONFIG)

def save_config(config):
    save_json(CONFIG_FILE, config)

def load_logs():
    return load_json(LOG_FILE, [])

def save_logs(logs):
    save_json(LOG_FILE, logs)

def load_last_files():
    return load_json(FILES_FILE, [])

def save_last_files(files):
    save_json(FILES_FILE, files)
