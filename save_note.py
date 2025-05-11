from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Lê o token diretamente do ficheiro secreto
try:
    with open("/etc/secrets/dropbox_token.txt", "r") as f:
        DROPBOX_TOKEN = f.read().strip()
except Exception as e:
    DROPBOX_TOKEN = None
    print(f"❌ Erro ao ler token do secret file: {e}")

DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"

@app.route("/save_note", methods=["POST"])
def save_note():
    if not DROPBOX_TOKEN:
        return jsonify({"status": "error", "message": "Token Dropbox não encontrado"}), 500

    data = request.json

    title = data.get("title", "untitled").strip().replace(" ", "_")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    content = data.get("content", "")

    filename = f"{date}_{title}.md"
    dropbox_path = f"/{filename}"

    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": f"""{{"path": "{dropbox_path}", "mode": "overwrite", "autorename": false, "mute": false}}"""
    }

    try:
        response = requests.post(
            DROPBOX_UPLOAD_URL,
            headers=headers,
            data=content.encode("utf-8")
        )

        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "file": filename
            }), 200
        else:
            return jsonify({
                "status": "error",
                "dropbox_status": response.status_code,
                "dropbox_error": response.text,
                "dropbox_headers": dict(response.headers)
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "exception": str(e)
        }), 500

@app.route("/", methods=["GET"])
def home():
    return "📝 Save Note API with Dropbox (token from secret file) is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
