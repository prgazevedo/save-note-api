import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import datetime

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)
ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

app = Flask(__name__)

@app.route("/save_note", methods=["POST"])
def save_note():
    data = request.get_json()
    title = data.get("title", "Untitled").replace(" ", "_")
    date = data.get("date", datetime.date.today().isoformat())
    content = data.get("content", "")

    filename = f"{date}_{title}.md"
    dropbox_path = f"/{filename}"

    print(f"📄 File: {dropbox_path}")
    print(f"🔐 Using access token: {ACCESS_TOKEN[:20]}...")

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/octet-stream",
        "Dropbox-API-Arg": f'{{"path": "{dropbox_path}", "mode": "overwrite", "autorename": false, "mute": false}}'
    }

    response = requests.post("https://content.dropboxapi.com/2/files/upload", headers=headers, data=content.encode("utf-8"))

    if response.status_code == 200:
        return jsonify({"status": "success", "file": filename})
    else:
        return jsonify({
            "status": "error",
            "dropbox_status": response.status_code,
            "dropbox_error": response.text
        }), 500

if __name__ == "__main__":
    print("🚀 Starting SaveNote API with static access token...")
    app.run(debug=True)
