# app.py

import os
from flask import Flask, redirect, url_for, jsonify
from dotenv import load_dotenv
from flasgger import Swagger
from utils.logging_utils import log

from utils.config_utils import load_config, load_logs, load_last_files

# Load local .env for dev
load_dotenv()

# Route handlers
from routes.process import process_note
from routes.auth import bp as auth_bp
from routes.admin import bp as admin_bp
from routes.scan import bp as scan_bp
from routes.api import bp as api_bp
from routes.upload import upload_note_api
from routes.list import list_kb, list_kb_folder
from routes.download import download_routes

app = Flask(__name__)

# Session key (for login session)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-insecure-default")

# Swagger config with README link
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "info": {
        "title": "SaveNotesGPT API",
        "version": "0.1.0",
        "description": (
            "API for managing Markdown notes with Dropbox.\n\n"
            "👉 [📖 View README](https://github.com/prgazevedo/save-note-api/blob/main/README.md)"
        )
    }
}

Swagger(app, config=swagger_config, template=swagger_template)

# Function-based routes
app.add_url_rule("/save_note", view_func=upload_note, methods=["POST"])
app.add_url_rule("/list_kb", view_func=list_kb, methods=["GET"])
app.add_url_rule("/list_kb_folder", view_func=list_kb_folder, methods=["GET"])
app.add_url_rule("/get_kb_note", view_func=get_kb_note, methods=["GET"])
app.add_url_rule("/get_inbox_note", view_func=get_inbox_note, methods=["GET"])
# Register blueprints
app.register_blueprint(process_note)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(api_bp)
app.register_blueprint(download_routes)
app.register_blueprint(upload_note_api)


# Initial data files
load_config()
load_logs()
load_last_files()

# 🔍 Logtail Direct Test
if os.getenv("LOGTAIL_TOKEN"):
    import logging
    from logtail import LogtailHandler

    test_logger = logging.getLogger("LogtailTest")
    test_logger.setLevel(logging.INFO)
    handler = LogtailHandler(source_token=os.getenv("LOGTAIL_TOKEN"))
    handler.setFormatter(logging.Formatter(fmt="%(message)s"))
    test_logger.addHandler(handler)
    test_logger.propagate = False
    test_logger.info("🚀 LogtailHandler connected from app.py startup")
else:
    print("⚠️ LOGTAIL_TOKEN not found, skipping Logtail direct test")

@app.route("/")
def health_check():
    return jsonify({"status": "ok", "version": "v3.0.0"})

if __name__ == "__main__":
    print("✅ SaveNotesGPT is starting...")
    print("📚 API Docs:    https://save-note-api.onrender.com/apidocs/")
    print("🔐 Admin Panel: https://save-note-api.onrender.com/admin/dashboard")
    log("✅ SaveNotesGPT is starting...", level="info")
    log("📚 API Docs:    https://save-note-api.onrender.com/apidocs/", level="info")
    log("🔐 Admin Panel: https://save-note-api.onrender.com/admin/dashboard", level="info")
    app.run(host="0.0.0.0", port=5000, debug=True)
