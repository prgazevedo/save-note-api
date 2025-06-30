from flask import request, jsonify
from services.dropbox_client import list_folder

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

    result = list_folder(f"/Apps/SaveNotesGPT/NotesKB/{folder}")
    
    # If it's an error dict
    if isinstance(result, dict) and "error" in result:
        return jsonify({"status": "error", "message": result["error"]}), 500
    
    # If result is a dict with 'entries'
    if isinstance(result, dict) and "entries" in result:
        entries = result["entries"]
    # If result is already a list
    elif isinstance(result, list):
        entries = result
    else:
        return jsonify({"status": "error", "message": "Unexpected format returned from list_folder"}), 500

    files = [e["name"] for e in entries if e.get(".tag") == "file"]
    return jsonify({"status": "success", "files": files})

