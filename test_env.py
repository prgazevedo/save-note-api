from dotenv import load_dotenv
import os

load_dotenv()

print("🔑 DROPBOX_APP_KEY:", os.getenv("DROPBOX_APP_KEY"))
print("🔐 DROPBOX_APP_SECRET:", os.getenv("DROPBOX_APP_SECRET"))
print("🔄 DROPBOX_REFRESH_TOKEN:", os.getenv("DROPBOX_REFRESH_TOKEN"))
