# app.py

import os
from flask import Flask, redirect, url_for, jsonify
from dotenv import load_dotenv
from flasgger import Swagger

from utils.config_utils import load_config, load_logs, load_last_files

# Load local .env for dev
load_dotenv()

# Route handlers
from routes.upload import upload_note
from routes.list import list_kb, list_kb_folder
from routes.download import get_kb_note

# Blueprints
from routes.process import process_note
from routes.auth import bp as auth_bp
from routes.admin import bp as admin_bp
from routes.scan import bp as scan_bp
from routes.api import bp as api_bp

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

# Register blueprints
app.register_blueprint(process_note)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(scan_bp)
app.register_blueprint(api_bp)

# Initial data files
load_config()
load_logs()
load_last_files()

@app.route("/")
def health_check():
    return jsonify({"status": "ok", "version": "v3.0.0"})

if __name__ == "__main__":
    print("✅ SaveNotesGPT is starting...")
    print("📚 API Docs:    https://save-note-api.onrender.com/apidocs/")
    print("🔐 Admin Panel: https://save-note-api.onrender.com/admin/dashboard")
    app.run(host="0.0.0.0", port=5000, debug=True)
