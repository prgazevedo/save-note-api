import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("DROPBOX_APP_KEY")
CLIENT_SECRET = os.getenv("DROPBOX_APP_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
    print("❌ Erro: Verifica se DROPBOX_APP_KEY, DROPBOX_APP_SECRET e DROPBOX_REFRESH_TOKEN estão definidos no .env")
    exit(1)

print("🔄 A pedir novo access token com refresh_token...")

url = "https://api.dropboxapi.com/oauth2/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

response = requests.post(url, headers=headers, data=data)

print(f"📦 Status: {response.status_code}")
if response.ok:
    access_token = response.json().get("access_token")
    print(f"✅ Novo access token:\n{access_token}")
else:
    print(f"❌ Erro:\n{response.text}")
