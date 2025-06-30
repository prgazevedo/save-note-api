from datetime import datetime
from services import dropbox_client
import utils

def process_raw_markdown(original_md: str, filename: str, yaml_override: dict = None):
    # Derive defaults from filename
    title = filename.rsplit(".", 1)[0].split("_", 1)[-1].replace("_", " ")
    date_str = filename.split("_")[0]

    # Use override if provided
    if yaml_override:
        title = yaml_override.get("title", title)
        date_str = yaml_override.get("date", date_str)

    # Generate YAML + structured markdown
    yaml_fields = {"title": title, "date": date_str}
    yaml_block = utils.generate_yaml_front_matter(yaml_fields)
    structured_note = f"{yaml_block}\n\n{original_md.strip()}"

    # Path formatting
    subfolder = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
    new_filename = f"{date_str}_{utils.sanitize_filename(title)}.md"
    new_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{new_filename}"

    # Upload to Dropbox
    upload_result = dropbox_client.upload_structured_note(new_path, structured_note)

    return {
        "status": "success",
        "dropbox_path": new_path,
        "upload": upload_result
    }
