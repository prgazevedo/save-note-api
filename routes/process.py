from flask import Blueprint, request, jsonify
from services.process_note import process_raw_markdown
from services import dropbox_client
from utils.dropbox_utils import generate_yaml_front_matter, sanitize_filename
from utils.logging_utils import log
from datetime import datetime

process_note_bp = Blueprint("process_note", __name__)

@process_note_bp.route("/process_note", methods=["POST"])
def handle_process_note():
    try:
        data = request.get_json()
        filename = data.get("filename")
        yaml_fields = data.get("yaml")

        if not filename or not yaml_fields:
            return jsonify({"status": "error", "message": "Missing filename or YAML metadata"}), 400

        # Fetch original content
        original_md = dropbox_client.download_note_from_dropbox(filename, folder="Inbox")
        if not original_md:
            return jsonify({"status": "error", "message": f"File '{filename}' not found in Dropbox"}), 404

        # Generate front matter block
        yaml_block = generate_yaml_front_matter(yaml_fields)

        # Compose full note
        structured_note = f"{yaml_block}\n\n{original_md.strip()}"

        # Build path for destination in Dropbox
        date_str = yaml_fields.get("date", datetime.now().strftime("%Y-%m-%d"))
        subfolder = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
        new_filename = f"{date_str}_{sanitize_filename(yaml_fields['title'])}.md"
        new_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{new_filename}"

        # Upload
        result = dropbox_client.upload_structured_note(new_path, structured_note)

        return jsonify({
            "status": "success",
            "dropbox_path": new_path,
            "upload": result
        })

    except Exception as e:
        log(f"❌ /process_note error: {str(e)}")
        print(f"❌ /process_note error: {str(e)}")  # Visible in Render logs
        return jsonify({"status": "error", "message": str(e)}), 500

# 👇 This is key for app.py
process_note = process_note_bp
