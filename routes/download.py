from flask import request, jsonify
from dropbox_client import download_note_from_dropbox
from datetime import datetime

def get_kb_note():
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"status": "error", "message": "Missing filename"}), 400
    date_part = filename.split("_")[0]
    folder = datetime.strptime(date_part, "%Y-%m-%d").strftime("%Y-%m")
    path = f"/Apps/SaveNotesGPT/NotesKB/{folder}/{filename}"
    content, err = download_note_from_dropbox(path)
    if err:
        return jsonify({"status": "error", "message": err}), 500
    return content, 200, {"Content-Type": "text/markdown"}
