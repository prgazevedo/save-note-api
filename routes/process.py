from flask import Blueprint, request, jsonify
from services.process_note import process_raw_markdown
from services import dropbox_client
import utils

process_note_bp = Blueprint("process_note", __name__)

@process_note_bp.route("/process_note", methods=["POST"])
def handle_process_note():
    try:
        data = request.get_json()
        filename = data.get("filename")
        yaml_fields = data.get("yaml")

        if not filename or not yaml_fields:
            return jsonify({"status": "error", "message": "Missing filename or YAML metadata"}), 400

        original_md = dropbox_client.download_note_from_dropbox(filename, folder="Inbox")
        if not original_md:
            return jsonify({"status": "error", "message": f"File '{filename}' not found in Dropbox"}), 404

        result = process_raw_markdown(original_md, filename, yaml_fields)
        return jsonify({"status": "success", "result": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 👇 This is key for app.py import
process_note = process_note_bp
