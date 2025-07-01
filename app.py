import os
from flask import Flask, redirect, url_for, jsonify
from dotenv import load_dotenv
from utils.config_utils import load_config, load_logs, load_last_files
from flasgger import Swagger

# Load .env if running locally (e.g., Codespaces)
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
swagger = Swagger(app)


# Secure key for session cookies (used by Flask-Login)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-insecure-default")

# Function-based API routes
app.add_url_rule("/save_note", view_func=upload_note, methods=["POST"])
app.add_url_rule("/list_kb", view_func=list_kb, methods=["GET"])
app.add_url_rule("/list_kb_folder", view_func=list_kb_folder, methods=["GET"])
app.add_url_rule("/get_kb_note", view_func=get_kb_note, methods=["GET"])

# Blueprints
app.register_blueprint(process_note)  # /process_note
app.register_blueprint(auth_bp)       # /login, /logout
app.register_blueprint(admin_bp)      # /admin/dashboard
app.register_blueprint(scan_bp)
app.register_blueprint(api_bp)

# Create initial files on app startup
load_config()
load_logs()
load_last_files()

# Health check route
@app.route("/")
def health_check():
    return jsonify({"status": "ok", "version": "v3.0.0"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
