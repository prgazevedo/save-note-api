import os
import re

def get_access_token():
    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not token:
        raise ValueError("DROPBOX_ACCESS_TOKEN not set in environment variables")
    return token

def sanitize_filename(name: str) -> str:
    # Replace unsafe characters with underscores
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name.replace(" ", "_").strip()

def build_yaml_block(fields: dict) -> str:
    yaml_lines = ["---"]
    for key, value in fields.items():
        if isinstance(value, list):
            yaml_lines.append(f"{key}:")
            for item in value:
                yaml_lines.append(f"  - {item}")
        else:
            yaml_lines.append(f"{key}: {value}")
    yaml_lines.append("---")
    return "\n".join(yaml_lines)
