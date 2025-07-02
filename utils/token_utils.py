import os
from flask import request, jsonify
from dotenv import load_dotenv

# Load GPT token from .tokens file
load_dotenv(dotenv_path=".tokens")
GPT_AUTH_TOKEN = os.getenv("GPT_TOKEN")  # Just the token string, no "Bearer"

def require_token(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing Bearer token"}), 401

        token = auth_header.replace("Bearer ", "").strip()
        if token != GPT_AUTH_TOKEN:
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)
    return wrapper
