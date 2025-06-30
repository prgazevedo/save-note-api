from datetime import datetime
from services import dropbox_client
from utils.dropbox_utils import generate_yaml_front_matter, sanitize_filename
from utils.logging_utils import log_event

def process_raw_markdown(original_md: str, filename: str, yaml_override: dict = None):
    # Derive defaults from filename
    title = filename.rsplit(".", 1)[0].split("_", 1)[-1].replace("_", " ")
    date_str = filename.split("_")[0]

    # Allow override from incoming YAML
    if yaml_override:
        title = yaml_override.get("title", title)
        date_str = yaml_override.get("date", date_str)

    # Build YAML metadata block
    yaml_fields = {
        "title": title,
        "date": date_str
    }
    yaml_block = generate_yaml_front_matter(yaml_fields)
    structured_note = f"{yaml_block}\n\n{original_md.strip()}"

    # Target Dropbox path
    subfolder = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
    new_filename = f"{date_str}_{sanitize_filename(title)}.md"
    new_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{new_filename}"

    # Upload to Dropbox
    upload_result = dropbox_client.upload_structured_note(new_path, structured_note)

    # Log
    log_event(f"📄 Uploaded: {new_filename}")

    return {
        "dropbox_path": new_path,
        "upload": upload_result
    }
