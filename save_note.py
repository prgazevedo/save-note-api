from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN", "")

DROPBOX_UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"

@app.route("/save_note", methods=["POST"])
def save_note():
    print("📥 Recebida requisição POST em /save_note")

    try:
        data = request.json
        print("🔍 Dados recebidos:")
        print(data)

        title = data.get("title", "untitled").strip().replace(" ", "_")
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        content = data.get("content", "")
        filename = f"{date}_{title}.md"
        dropbox_path = f"/{filename}"

        print(f"📄 Ficheiro a criar: {dropbox_path}")

        headers = {
            "Authorization": f"Bearer {DROPBOX_TOKEN}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({
                "path": dropbox_path,
                "mode": "overwrite",
                "autorename": False,
                "mute": False
            })
        }

        print("📦 Headers enviados:")
        for k, v in headers.items():
            print(f"{k}: {v[:100]}...")

        print("📤 Conteúdo:")
        print(content)

        response = requests.post(
            DROPBOX_UPLOAD_URL,
            headers=headers,
            data=content.encode("utf-8")
        )

        print("📥 Dropbox response:")
        print("Status:", response.status_code)
        print("Body:", response.text)

        if response.status_code == 200:
            return jsonify({"status": "success", "file": filename}), 200
        else:
            return jsonify({
                "status": "error",
                "dropbox_status": response.status_code,
                "dropbox_error": response.text
            }), 500

    except Exception as e:
        print("❌ Exceção:", str(e))
        return jsonify({"status": "error", "exception": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "📝 Save Note API (Render version with env var)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

