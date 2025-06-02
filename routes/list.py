from flask import request, jsonify
from dropbox_client import list_folder

def list_kb():
    result, err = list_folder("/Apps/SaveNotesGPT/NotesKB")
    if err:
        return jsonify({"status": "error", "message": err}), 500
    folders = [e["name"] for e in result.get("entries", []) if e[".tag"] == "folder"]
    return jsonify({"status": "success", "folders": folders})

def list_kb_folder():
    folder = request.args.get("folder")
    if not folder:
        return jsonify({"status": "error", "message": "Missing 'folder' param"}), 400
    
    result, err = list_folder(f"/Apps/SaveNotesGPT/NotesKB/{folder}")
    if err:
        return jsonify({"status": "error", "message": err}), 500
    
    files = [e["name"] for e in result.get("entries", []) if e[".tag"] == "file"]
    return jsonify({"status": "success", "files": files})
