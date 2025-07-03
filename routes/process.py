# routes/process.py - Note processing with full Obsidian link support

from flask import Blueprint, request, jsonify
from services import dropbox_client
from utils.dropbox_utils import generate_yaml_front_matter, sanitize_filename, process_note_with_links
from utils.logging_utils import log
from utils.token_utils import require_token
from datetime import datetime

process_bp = Blueprint("process", __name__, url_prefix="/api/inbox/notes")


@process_bp.route("/<filename>", methods=["PATCH"])
@require_token
def process_inbox_note(filename):
    """
    Process a raw note by adding GPT-generated metadata and archiving to Knowledge Base.
    ---
    tags:
      - Inbox Notes
    summary: Process raw note with GPT metadata
    description: |
      Transforms a raw note from the Inbox into a structured Knowledge Base entry by:
      1. Adding GPT-generated YAML frontmatter with metadata
      2. Detecting and copying linked files (Obsidian support)
      3. Updating link paths in the note content
      4. Moving the processed note to the appropriate KB folder
      This is the core transformation step in the knowledge management pipeline.
    parameters:
      - name: filename
        in: path
        required: true
        schema:
          type: string
          example: "2025-07-03_meeting-ideas.md"
        description: Filename of the raw note to process
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - action
              - metadata
            properties:
              action:
                type: string
                enum: [process]
                example: "process"
                description: Action to perform (currently only 'process' supported)
              metadata:
                type: object
                required: [title, date]
                properties:
                  title:
                    type: string
                    example: "Weekly Team Meeting Notes"
                  date:
                    type: string
                    format: date
                    example: "2025-07-03"
                  tags:
                    type: array
                    items:
                      type: string
                    example: ["meeting", "team", "weekly"]
                  author:
                    type: string
                    example: "John Doe"
                  source:
                    type: string
                    example: "obsidian"
                  type:
                    type: string
                    example: "meeting-notes"
                  uid:
                    type: string
                    example: "weekly-team-meeting-2025-07-03"
                  status:
                    type: string
                    example: "processed"
                  language:
                    type: string
                    example: "en"
                  summary:
                    type: string
                    example: "Weekly team sync covering project updates and Q4 planning"
              copy_linked_files:
                type: boolean
                default: true
                description: "Whether to copy linked files from Inbox to KB"
          examples:
            obsidian_note:
              summary: Obsidian note with linked files
              value:
                action: "process"
                metadata:
                  title: "Project Design Review"
                  date: "2025-07-03"
                  tags: ["design", "project", "review"]
                  source: "obsidian"
                  summary: "Design review with wireframes and mockups"
                copy_linked_files: true
    responses:
      200:
        description: Note processed successfully with linked files
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                action:
                  type: string
                  example: processed
                result:
                  type: object
                  properties:
                    source_note:
                      type: string
                      example: "2025-07-03_meeting-ideas.md"
                    kb_path:
                      type: string
                      example: "/Apps/SaveNotesGPT/NotesKB/2025-07/2025-07-03_weekly-team-meeting-notes.md"
                    linked_files_detected:
                      type: integer
                      example: 3
                    linked_files_copied:
                      type: integer
                      example: 2
                    upload_success:
                      type: boolean
                      example: true
                    copied_files:
                      type: array
                      items:
                        type: object
                        properties:
                          filename:
                            type: string
                          source:
                            type: string
                          target:
                            type: string
                      example:
                        - filename: "wireframe.png"
                          source: "/Apps/SaveNotesGPT/Inbox/wireframe.png"
                          target: "/Apps/SaveNotesGPT/NotesKB/2025-07/wireframe.png"
                    failed_files:
                      type: array
                      items:
                        type: object
                      example: []
                metadata_applied:
                  type: object
                  description: The metadata that was applied to the note
      400:
        description: Invalid request or missing required fields
      404:
        description: Note not found in Inbox
      500:
        description: Processing error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "Request body required"}), 400
            
        action = data.get("action")
        if action != "process":
            return jsonify({"status": "error", "message": "Only 'process' action is supported"}), 400
        
        metadata = data.get("metadata", {})
        copy_linked_files = data.get("copy_linked_files", True)  # Default to True now
        
        # Validate required metadata
        if not metadata.get("title"):
            return jsonify({"status": "error", "message": "Metadata 'title' is required"}), 400
        if not metadata.get("date"):
            return jsonify({"status": "error", "message": "Metadata 'date' is required"}), 400
            
        # Validate date format
        try:
            parsed_date = datetime.strptime(metadata["date"], "%Y-%m-%d")
        except ValueError:
            return jsonify({"status": "error", "message": f"Invalid date format: {metadata['date']}. Use YYYY-MM-DD"}), 400

        # Load original note content
        original_content = dropbox_client.download_note_from_dropbox(filename, folder="Inbox")
        if not original_content:
            return jsonify({"status": "error", "message": f"Note '{filename}' not found in Inbox"}), 404

        # Set default metadata values
        metadata.setdefault("author", "user")
        metadata.setdefault("source", "inbox")
        metadata.setdefault("type", "note")
        metadata.setdefault("status", "processed")
        metadata.setdefault("language", "en")
        metadata.setdefault("uid", f"{sanitize_filename(metadata['title'])}-{metadata['date']}")

        # Compute target paths
        subfolder = parsed_date.strftime("%Y-%m")
        new_filename = f"{metadata['date']}_{sanitize_filename(metadata['title'])}.md"
        kb_folder_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}"
        kb_file_path = f"{kb_folder_path}/{new_filename}"

        # Process note with link handling (preserves folder structure)
        processing_result = process_note_with_links(
            content=original_content,
            metadata=metadata,
            kb_folder_path=kb_folder_path,
            copy_links=copy_linked_files
        )

        # Extract results
        processed_content = processing_result["processed_content"]  # Unchanged content
        detected_links = processing_result["detected_links"]
        copy_result = processing_result["copy_result"]
        final_metadata = processing_result["metadata"]

        # Generate final structured content with YAML frontmatter
        yaml_block = generate_yaml_front_matter(final_metadata)
        structured_content = f"{yaml_block}\n\n{processed_content.strip()}"

        # Upload processed note to Knowledge Base
        upload_success = dropbox_client.upload_structured_note(kb_file_path, structured_content)
        
        # Calculate totals
        total_links_detected = sum(len(links) for links in detected_links.values())
        
        # Log comprehensive result
        if copy_result["total_copied"] > 0:
            log(f"📦 Processed note with links: {filename} → {kb_file_path} "
                f"(detected {total_links_detected}, copied {copy_result['total_copied']} files)")
        else:
            log(f"📦 Processed note: {filename} → {kb_file_path} "
                f"(detected {total_links_detected} links, none copied)")

        return jsonify({
            "status": "success",
            "action": "processed",
            "result": {
                "source_note": filename,
                "kb_path": kb_file_path,
                "linked_files_detected": total_links_detected,
                "linked_files_copied": copy_result["total_copied"],
                "upload_success": upload_success,
                "copied_files": copy_result["copied_files"],
                "failed_files": copy_result["failed_files"]
            },
            "metadata_applied": final_metadata
        }), 200

    except Exception as e:
        log(f"❌ Note processing error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# Export for app.py
process_note_routes = process_bp