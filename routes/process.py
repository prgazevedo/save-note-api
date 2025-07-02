from flask import Blueprint, request, jsonify
from services.process_service import archive_note_with_yaml
from services import dropbox_client
from utils.dropbox_utils import generate_yaml_front_matter, sanitize_filename
from utils.logging_utils import log
from utils.token_utils import require_token
from datetime import datetime

process_bp = Blueprint("process", __name__, url_prefix="/api/inbox/notes")

@process_bp.route("/<filename>/process", methods=["POST"])
@require_token
def process_note(filename):
    """
    Process a note from the Inbox by injecting YAML metadata and archiving to the Knowledge Base.
    ---
    tags:
      - Inbox Notes
    summary: Process and archive a note
    description: Takes a note in the Inbox, injects YAML frontmatter, and moves it to the structured KB folder.
    parameters:
      - name: filename
        in: path
        required: true
        schema:
          type: string
        description: Name of the file to process (e.g., README.md)
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - yaml
            properties:
              yaml:
                type: object
                properties:
                  title:
                    type: string
                  date:
                    type: string
                    format: date
                  tags:
                    type: array
                    items:
                      type: string
                  author:
                    type: string
                  source:
                    type: string
                  type:
                    type: string
                  uid:
                    type: string
                  status:
                    type: string
                  linked_files:
                    type: array
                    items:
                      type: string
                  language:
                    type: string
                  summary:
                    type: string
    responses:
      200:
        description: Note processed and archived
        content:
          application/json:
            example:
              status: success
              dropbox_path: /Apps/SaveNotesGPT/NotesKB/2025-07/2025-07-01_readme.md
              upload: true
      400:
        description: Missing required fields
      404:
        description: File not found
      500:
        description: Internal error
    """
    try:
        data = request.get_json()
        yaml_fields = data.get("yaml")

        if not filename or not yaml_fields:
            return jsonify({"status": "error", "message": "Missing filename or YAML metadata"}), 400

        # ✅ Validate date
        date_str = yaml_fields.get("date")
        if not date_str:
            return jsonify({"status": "error", "message": "Missing 'date' in YAML"}), 400

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"status": "error", "message": f"Invalid date format: {date_str}. Use YYYY-MM-DD"}), 400

        # ⬇️ Load original MD from Dropbox Inbox
        original_md = dropbox_client.download_note_from_dropbox(filename, folder="Inbox")
        if not original_md:
            return jsonify({"status": "error", "message": f"File '{filename}' not found in Inbox"}), 404

        # 🧱 Build YAML + content
        yaml_block = generate_yaml_front_matter(yaml_fields)
        structured_note = f"{yaml_block}\n\n{original_md.strip()}"

        # 📁 Compute path
        subfolder = parsed_date.strftime("%Y-%m")
        new_filename = f"{date_str}_{sanitize_filename(yaml_fields['title'])}.md"
        new_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{new_filename}"

        # ⬆️ Upload to Dropbox
        result = dropbox_client.upload_structured_note(new_path, structured_note)
        log(f"📦 Archived note: {filename} → {new_path}")

        return jsonify({
            "status": "success",
            "dropbox_path": new_path,
            "upload": result
        })

    except Exception as e:
        log(f"❌ Processing error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# 👇 Import into app.py as:
process_note_routes = process_bp
