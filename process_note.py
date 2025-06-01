from flask import Blueprint, request, jsonify
from datetime import datetime
import dropbox_client  # your wrapper for Dropbox upload
import utils  # helper functions for sanitizing filenames, etc.

process_note = Blueprint('process_note', __name__)

@process_note.route("/process_note", methods=["POST"])
def handle_process_note():
    try:
        data = request.get_json()
        filename = data.get("filename")
        yaml_fields = data.get("yaml")

        if not filename or not yaml_fields:
            return jsonify({"status": "error", "message": "Missing filename or YAML metadata"}), 400

        # Fetch original content from Dropbox
        original_md = dropbox_client.download_note_from_dropbox(filename, folder="Inbox")

        if not original_md:
            return jsonify({"status": "error", "message": f"File '{filename}' not found in Dropbox"}), 404

        # Construct YAML frontmatter
        yaml_block = utils.build_yaml_block(yaml_fields)

        # Combine YAML and original content
        structured_note = f"{yaml_block}\n\n{original_md.strip()}"

        # Compute new Dropbox path
        date_str = yaml_fields.get("date", datetime.now().strftime("%Y-%m-%d"))
        subfolder = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
        new_filename = f"{date_str}_{utils.sanitize_filename(yaml_fields['title'])}.md"
        new_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{new_filename}"

        # Upload the structured note
        upload_result = dropbox_client.upload_structured_note(new_path, structured_note)

        return jsonify({
            "status": "success",
            "dropbox_path": new_path,
            "upload": upload_result
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
