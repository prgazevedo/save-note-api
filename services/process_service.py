from datetime import datetime
from services import dropbox_client
from utils.dropbox_utils import generate_yaml_front_matter, sanitize_filename
from utils.logging_utils import log


def archive_note_with_yaml(original_md: str, filename: str, yaml_override: dict = None) -> dict:
    """
    Archives a Markdown note by prepending provided YAML frontmatter and uploading to the Knowledge Base folder in Dropbox.

    Parameters:
        original_md (str): The body/content of the note (Markdown without YAML)
        filename (str): The original filename (e.g., 2025-07-01_Meeting-Notes.md)
        yaml_override (dict): Optional YAML metadata to override (e.g., title, date)

    Returns:
        dict: {
            "dropbox_path": <final Dropbox path>,
            "upload": <upload result: bool>
        }
    """

    # Derive defaults from filename
    title = filename.rsplit(".", 1)[0].split("_", 1)[-1].replace("_", " ")
    date_str = filename.split("_")[0]

    # Override with explicit YAML if provided
    if yaml_override:
        title = yaml_override.get("title", title)
        date_str = yaml_override.get("date", date_str)

    # YAML block
    yaml_fields = {
        "title": title,
        "date": date_str
    }
    yaml_block = generate_yaml_front_matter(yaml_fields)

    # Final content
    structured_note = f"{yaml_block}\n\n{original_md.strip()}"

    # Compute path and filename
    subfolder = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
    new_filename = f"{date_str}_{sanitize_filename(title)}.md"
    new_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}/{new_filename}"

    # Upload
    upload_result = dropbox_client.upload_structured_note(new_path, structured_note)
    log(f"📄 Uploaded: {new_filename}")

    return {
        "dropbox_path": new_path,
        "upload": upload_result
    }
