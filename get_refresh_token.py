import os
import requests
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Forçar o path absoluto para o .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, '.env')
print(f"🔍 Carregando .env de: {dotenv_path}")
load_dotenv(dotenv_path)

APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
REDIRECT_URI = "http://localhost:53682"

print(f"🔑 APP_KEY: {APP_KEY}")
print(f"🔐 APP_SECRET: {APP_SECRET}")

if not APP_KEY or not APP_SECRET:
    print("❌ Faltam DROPBOX_APP_KEY ou DROPBOX_APP_SECRET no .env. Verifica o ficheiro.")
    exit(1)

auth_url = (
    f"https://www.dropbox.com/oauth2/authorize"
    f"?client_id={APP_KEY}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&token_access_type=offline"
)

print("🌍 A abrir o browser para autorizar...")
webbrowser.open(auth_url)

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        code = parse_qs(urlparse(self.path).query).get("code", [None])[0]
        if code:
            print(f"✅ Authorization code: {code}")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Pode fechar esta aba. Código capturado!".encode())
            exchange_token(code)
            os._exit(0)
        else:
            self.send_error(400, "Código de autorização não encontrado.")

def exchange_token(code):
    print("🔁 A trocar código por refresh token...")
    resp = requests.post("https://api.dropbox.com/oauth2/token", data={
        "code": code,
        "grant_type": "authorization_code",
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
    })
    print(f"📦 Status: {resp.status_code}")
    print(resp.text)

httpd = HTTPServer(("localhost", 53682), OAuthHandler)
print("🚀 A aguardar autorização em localhost:53682 ...")
httpd.handle_request()
