import os
import requests
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
REDIRECT_URI = "http://localhost:53123"

if not APP_KEY or not APP_SECRET:
    print("❌ Erro: Verifica se DROPBOX_APP_KEY e DROPBOX_APP_SECRET estão definidos no .env")
    exit(1)

auth_url = (
    f"https://www.dropbox.com/oauth2/authorize"
    f"?client_id={APP_KEY}&response_type=code&redirect_uri={REDIRECT_URI}&token_access_type=offline"
)

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        code = self.path.split("code=")[-1]
        self.send_response(200)
        self.end_headers()
        self.wfile.write("✅ Código capturado. Pode fechar esta aba.".encode("utf-8"))
        print(f"\n🔐 Código recebido: {code}")
        exchange(code)

def exchange(code):
    print("\n🔁 A trocar por refresh token...")
    r = requests.post(
        "https://api.dropboxapi.com/oauth2/token",
        data={
            "code": code,
            "grant_type": "authorization_code",
            "client_id": APP_KEY,
            "client_secret": APP_SECRET,
            "redirect_uri": REDIRECT_URI,
        },
    )
    print(f"\n📦 Status: {r.status_code}")
    print(r.text)

print(f"🔑 APP_KEY:    {APP_KEY}")
print(f"🔐 APP_SECRET: {APP_SECRET[:4]}... (length: {len(APP_SECRET)})")

print("🌍 A abrir o browser para autorizar...")
webbrowser.open(auth_url)

print("🚀 A aguardar autorização em localhost:53123...")
httpd = HTTPServer(("localhost", 53123), AuthHandler)
httpd.handle_request()
