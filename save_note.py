import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

# Load .env locally only
if os.getenv("ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

# Optional: debug print (can be commented out)
APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
print("🔍 DROPBOX_APP_KEY:", APP_KEY)
print("🔐 DROPBOX_APP_SECRET:", APP_SECRET[:4], "... (len:", len(APP_SECRET), ")")
print("🔄 DROPBOX_REFRESH_TOKEN:", REFRESH_TOKEN[:5], "... (len:", len(REFRESH_TOKEN), ")")

def get_access_token():
    print("🔁 Refreshing access token...")
    url = "https://api.dropboxapi.com/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code == 200:
        token = r.json()["access_token"]
        print("✅ Access token refreshed.")
        return token
    else:
        print("❌ Failed to refresh token:", r.text)
        return None

def sanitize_filename(title):
    return title.strip().replace(" ", "_").replace(":", "-")

def upload_note_to_dropbox(title, date, content):
    filename = f"{date}_{sanitize_filename(title)}.md"
    subfolder = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
    dropbox_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{filename}"
    access_token = get_access_token()
    if not access_token:
        return {"status": "error", "dropbox_error": "Could not refresh token"}

    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": f"""{{"path": "{dropbox_path}", "mode": "overwrite", "autorename": false, "mute": false}}""",
        "Content-Type": "application/octet-stream"
    }

    print(f"📄 File: {dropbox_path}")
    response = requests.post(url, headers=headers, data=content.encode("utf-8"))
    return {
        "status": "success" if response.status_code == 200 else "error",
        "dropbox_status": response.status_code,
        "dropbox_error": response.text if response.status_code != 200 else None,
        "file": filename if response.status_code == 200 else None
    }


app = Flask(__name__)

@app.route("/save_note", methods=["POST"])
def save_note():
    try:
        if request.content_type.startswith("multipart/form-data"):
            # Handle file upload
            file = request.files.get("file")
            if not file:
                return jsonify({"status": "error", "message": "No file provided"}), 400

            content = file.read().decode("utf-8")
            filename = file.filename
            title = filename.rsplit(".", 1)[0]  # use name without .md
            date = datetime.now().strftime("%Y-%m-%d")

            print(f"📤 Received file: {filename}")
            result = upload_note_to_dropbox(title, date, content)
            return jsonify(result)

        else:
            # Handle raw JSON body
            data = request.get_json()
            print("🔽 Incoming JSON:", data)

            title = data.get("title")
            date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
            content = data.get("content")

            if not title or not content:
                return jsonify({"status": "error", "message": "Missing title or content"}), 400

            result = upload_note_to_dropbox(title, date, content)
            return jsonify(result)

    except Exception as e:
        print("❌ Exception in save_note:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500



@app.errorhandler(Exception)
def handle_exception(e):
    print("❌ Uncaught exception:", str(e))
    return jsonify({
        "status": "error",
        "message": str(e)
    }), 500


@app.route("/openapi.json")
def serve_openapi():
    with open("openapi.json") as f:
        return f.read(), 200, {"Content-Type": "application/json"}


@app.route("/ai-plugin.json")
def serve_plugin_manifest():
    with open("ai-plugin.json") as f:
        return f.read(), 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    print("🚀 Starting SaveNote API...")
    token = get_access_token()
    if token:
        print("✅ Token refresh test succeeded.")
    else:
        print("❌ Token refresh test failed.")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
