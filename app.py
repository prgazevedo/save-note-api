import os
from flask import Flask, redirect, url_for, jsonify
from dotenv import load_dotenv
from flasgger import Swagger
from utils.logging_utils import log
from utils.config_utils import load_config, load_logs, load_last_files
from flask import Flask, send_from_directory

# Load local .env for dev
load_dotenv()

# Route handlers (blueprints and views)
from routes.process import process_note_routes
from routes.auth import bp as auth_bp
from routes.admin import bp as admin_bp
from routes.scan import inbox_files_routes
from routes.upload import upload_note_api
from routes.download import download_routes
from routes.list import kb_notes_list_routes

app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-insecure-default")

# Swagger setup
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



# ✅ Register blueprints (all under /api)
app.register_blueprint(process_note_routes)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(inbox_files_routes)
app.register_blueprint(download_routes)
app.register_blueprint(upload_note_api)
app.register_blueprint(kb_notes_list_routes)

# Initial load
load_config()
load_logs()
load_last_files()

# Optional: Logtail test connection
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

# Health check route
@app.route("/")
def health_check():
    return jsonify({"status": "ok", "version": "v3.0.0"})
# Serve ai plugin route
@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
    return send_from_directory("static/.well-known", "ai-plugin.json", mimetype='application/json')

def startup_log():
    lines = [
        "✅ SaveNotesGPT is starting...",
        "📚 API Docs:    https://save-note-api.onrender.com/apidocs/",
        "🔐 Admin Panel: https://save-note-api.onrender.com/admin/dashboard",
        "📄 README:      https://github.com/prgazevedo/save-note-api/blob/main/README.md",
        "📂 OpenAPI JSON: https://save-note-api.onrender.com/static/.well-known/ai-plugin.json",
        "📊 Logs (BetterStack): https://telemetry.betterstack.com/team/385553"
    ]
    if os.getenv("RENDER") == "true":
        # Only log once in Render
        for line in lines:
            log(line, level="info")
    else:
        # Local dev: print and log
        for line in lines:
            print(line)
            log(line, level="info")

# Start Flask app
if __name__ == "__main__":
    startup_log()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
