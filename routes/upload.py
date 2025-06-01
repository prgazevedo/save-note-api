from flask import request, jsonify
from dropbox_client import upload_note_to_dropbox

def upload_note():
    try:
        data = request.get_json()

        title = data.get("title")
        date = data.get("date")
        content = data.get("content")

        if not title or not date or not content:
            return jsonify({"status": "error", "message": "Missing title, date, or content"}), 400

        success = upload_note_to_dropbox(title, date, content)

        if success:
            return jsonify({"status": "success", "message": "Note uploaded to Dropbox."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to upload note."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
