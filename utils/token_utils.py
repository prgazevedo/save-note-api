import os
from flask import request, jsonify

# Load token from env or config file
GPT_AUTH_TOKEN = os.getenv("GPT_BEARER_TOKEN")

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
