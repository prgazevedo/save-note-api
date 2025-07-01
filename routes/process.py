from flask import Blueprint, request, jsonify
from services.process_note import process_raw_markdown
from services import dropbox_client
from utils.dropbox_utils import generate_yaml_front_matter, sanitize_filename
from utils.logging_utils import log
from datetime import datetime

process_note_bp = Blueprint("process_note", __name__, url_prefix="/api")

@process_note_bp.route("/process_note", methods=["POST"])
def handle_process_note():
    """
    Process a Markdown file with given YAML front matter and reupload to structured KB path.
    ---
    tags:
      - Routes
    summary: Process raw file into structured note
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - filename
              - yaml
            properties:
              filename:
                type: string
                example: 2025-06-30_MinhaNota.md
              yaml:
                type: object
                properties:
                  title:
                    type: string
                    example: Minha Nota
                  date:
                    type: string
                    example: 2025-06-30
    responses:
      200:
        description: File processed and reuploaded
        content:
          application/json:
            example:
              status: success
              dropbox_path: /Apps/SaveNotesGPT/NotesKB/2025-06/2025-06-30_minha-nota.md
              upload: true
      400:
        description: Missing fields
      404:
        description: File not found in Dropbox Inbox
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        filename = data.get("filename")
        yaml_fields = data.get("yaml")

        if not filename or not yaml_fields:
            return jsonify({"status": "error", "message": "Missing filename or YAML metadata"}), 400

        # ✅ Validate date format
        date_str = yaml_fields.get("date")
        if not date_str:
            return jsonify({"status": "error", "message": "Missing 'date' in YAML metadata"}), 400

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "status": "error",
                "message": f"Invalid 'date' format: '{date_str}'. Expected YYYY-MM-DD."
            }), 400

        # Fetch original markdown from Dropbox Inbox
        original_md = dropbox_client.download_note_from_dropbox(filename, folder="Inbox")
        if not original_md:
            return jsonify({"status": "error", "message": f"File '{filename}' not found in Dropbox Inbox"}), 404

        # Generate YAML front matter
        yaml_block = generate_yaml_front_matter(yaml_fields)

        # Compose structured note
        structured_note = f"{yaml_block}\n\n{original_md.strip()}"

        # Build destination path
        subfolder = parsed_date.strftime("%Y-%m")
        new_filename = f"{date_str}_{sanitize_filename(yaml_fields['title'])}.md"
        new_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{new_filename}"

        # Upload to Dropbox
        result = dropbox_client.upload_structured_note(new_path, structured_note)

        log(f"📄 /process_note: Processed and uploaded '{filename}' to '{new_path}'")

        return jsonify({
            "status": "success",
            "dropbox_path": new_path,
            "upload": result
        })

    except Exception as e:
        log(f"❌ /process_note error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500

# 👇 For app.py import
process_note = process_note_bp
