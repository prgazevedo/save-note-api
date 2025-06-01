from flask import request, jsonify
from dropbox_client import upload_note_to_dropbox
from datetime import datetime

def upload_note():
    file = request.files.get("file")
    if not file:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    content = file.read().decode("utf-8")
    title = file.filename.rsplit(".", 1)[0]
    date = datetime.now().strftime("%Y-%m-%d")
    result = upload_note_to_dropbox(title, date, content)
    return jsonify(result)
