# routes/pull.py - Pull Mode API Routes with full Swagger documentation

from flask import Blueprint, request, jsonify
from services.pull_service import pull_service
from utils.logging_utils import log
from utils.token_utils import require_token

pull_bp = Blueprint("pull", __name__, url_prefix="/api/pull")


@pull_bp.route("/preview", methods=["POST"])
@require_token
def preview_metadata():
    """
    Preview GPT-generated metadata without processing notes.
    ---
    tags:
      - Pull Mode
    summary: Preview metadata generation
    description: |
      Generate metadata for inbox notes using GPT without actually processing them.
      This allows you to review the AI-generated metadata before deciding to process the notes.
      
      Useful for:
      - Testing metadata generation quality
      - Manual review before batch processing
      - Adjusting custom instructions
    requestBody:
      required: false
      content:
        application/json:
          schema:
            type: object
            properties:
              filenames:
                type: array
                items:
                  type: string
                example: ["2025-07-03_meeting-notes.md", "2025-07-03_ideas.md"]
                description: Specific filenames to preview (if not provided, uses first 5 inbox notes)
              limit:
                type: integer
                minimum: 1
                maximum: 20
                default: 5
                example: 5
                description: Maximum number of notes to preview (ignored if filenames provided)
              custom_instructions:
                type: string
                example: "Focus on work-related tags and use Portuguese summaries"
                description: Optional custom instructions for GPT metadata generation
          examples:
            specific_files:
              summary: Preview specific files
              value:
                filenames: ["2025-07-03_meeting.md", "2025-07-03_ideas.md"]
                custom_instructions: "Use project-related tags"
            auto_discovery:
              summary: Auto-discover files to preview
              value:
                limit: 3
                custom_instructions: "Focus on business context"
    responses:
      200:
        description: Metadata preview generated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                previews:
                  type: array
                  items:
                    type: object
                    properties:
                      filename:
                        type: string
                        example: "2025-07-03_meeting-notes.md"
                      metadata:
                        type: object
                        properties:
                          title:
                            type: string
                            example: "Weekly Team Meeting"
                          date:
                            type: string
                            example: "2025-07-03"
                          tags:
                            type: array
                            items:
                              type: string
                            example: ["meeting", "team", "weekly"]
                          summary:
                            type: string
                            example: "Weekly team sync covering project updates"
                          type:
                            type: string
                            example: "meeting-notes"
                          language:
                            type: string
                            example: "en"
                      content_preview:
                        type: string
                        example: "# Meeting Notes\n\n## Agenda\n- Project updates\n- Q4 planning..."
                      error:
                        type: string
                        nullable: true
                        example: null
      400:
        description: Invalid request parameters
      401:
        description: Missing or invalid Bearer token
      500:
        description: Internal server error or GPT generation failed
    """
    try:
        data = request.get_json() or {}
        
        filenames = data.get("filenames", [])
        limit = min(int(data.get("limit", 5)), 20)
        custom_instructions = data.get("custom_instructions", "").strip()
        
        # Use the pull service for preview
        if filenames:
            # Preview specific files
            result = pull_service.preview_metadata(
                filenames=filenames,
                custom_instructions=custom_instructions if custom_instructions else None
            )
        else:
            # Auto-discover files to preview
            result = pull_service.preview_metadata(
                limit=limit,
                custom_instructions=custom_instructions if custom_instructions else None
            )
        
        log(f"🔍 Generated metadata preview for {len(result['previews'])} notes")
        
        return jsonify(result), 200
        
    except Exception as e:
        log(f"❌ Preview metadata error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


@pull_bp.route("/process", methods=["POST"])
@require_token
def batch_process():
    """
    Batch process inbox notes with GPT-generated metadata.
    ---
    tags:
      - Pull Mode
    summary: Batch process notes with AI
    description: |
      Automatically scan the inbox, generate metadata using GPT, and process notes into 
      the Knowledge Base. This is the core Pull Mode functionality.
      
      Process:
      1. Scan inbox for unprocessed notes
      2. Generate metadata using GPT for each note
      3. Optionally auto-approve and process to Knowledge Base
      4. Copy linked files (Obsidian support)
      5. Return detailed processing results
    requestBody:
      required: false
      content:
        application/json:
          schema:
            type: object
            properties:
              batch_size:
                type: integer
                minimum: 1
                maximum: 20
                default: 5
                example: 10
                description: Maximum number of notes to process in this batch
              auto_approve:
                type: boolean
                default: false
                example: true
                description: Whether to automatically process generated metadata (true) or just generate for review (false)
              custom_instructions:
                type: string
                example: "Focus on work-related tags, use Portuguese summaries for Portuguese content"
                description: Optional custom instructions for GPT metadata generation
              copy_linked_files:
                type: boolean
                default: true
                example: true
                description: Whether to copy linked files from Inbox to KB (Obsidian support)
          examples:
            auto_process:
              summary: Auto-process with approval
              value:
                batch_size: 5
                auto_approve: true
                custom_instructions: "Use project-specific tags"
                copy_linked_files: true
            review_only:
              summary: Generate for manual review
              value:
                batch_size: 10
                auto_approve: false
                custom_instructions: "Focus on business context"
    responses:
      200:
        description: Batch processing completed
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                processed:
                  type: integer
                  example: 3
                  description: Number of notes successfully processed to KB
                skipped:
                  type: integer
                  example: 2
                  description: Number of notes skipped (auto_approve=false)
                failed:
                  type: integer
                  example: 0
                  description: Number of notes that failed processing
                message:
                  type: string
                  example: "Batch complete: 3 processed, 2 skipped, 0 failed"
                results:
                  type: array
                  items:
                    type: object
                    properties:
                      filename:
                        type: string
                        example: "2025-07-03_meeting-notes.md"
                      status:
                        type: string
                        enum: [success, skipped, failed]
                        example: "success"
                      metadata_generated:
                        type: object
                        description: The GPT-generated metadata
                      kb_path:
                        type: string
                        example: "/Apps/SaveNotesGPT/NotesKB/2025-07/2025-07-03_weekly-team-meeting.md"
                        description: Path in Knowledge Base (only for successful processing)
                      linked_files_copied:
                        type: integer
                        example: 2
                        description: Number of linked files copied (only for successful processing)
                      error:
                        type: string
                        description: Error message (only for failed processing)
                      message:
                        type: string
                        description: Status message (for skipped notes)
      400:
        description: Invalid request parameters
      401:
        description: Missing or invalid Bearer token
      500:
        description: Internal server error
    """
    try:
        data = request.get_json() or {}
        
        batch_size = min(int(data.get("batch_size", 5)), 20)
        auto_approve = data.get("auto_approve", False)
        custom_instructions = data.get("custom_instructions", "").strip()
        copy_linked_files = data.get("copy_linked_files", True)
        
        # Use the pull service for batch processing
        result = pull_service.batch_process_notes(
            batch_size=batch_size,
            auto_approve=auto_approve,
            custom_instructions=custom_instructions if custom_instructions else None,
            copy_linked_files=copy_linked_files
        )
        
        log(f"🤖 Pull mode batch: {result['message']}")
        
        return jsonify(result), 200
        
    except Exception as e:
        log(f"❌ Batch process error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


@pull_bp.route("/status", methods=["GET"])
@require_token
def get_pull_status():
    """
    Get Pull Mode status and inbox statistics.
    ---
    tags:
      - Pull Mode
    summary: Get Pull Mode status
    description: |
      Returns current status of the Pull Mode system including inbox statistics,
      last processing information, and system health.
    responses:
      200:
        description: Pull Mode status information
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: success
                inbox_stats:
                  type: object
                  properties:
                    total_notes:
                      type: integer
                      example: 15
                    total_size:
                      type: integer
                      example: 45123
                      description: Total size in bytes
                    latest_note:
                      type: string
                      format: date-time
                      example: "2025-07-03T14:30:00Z"
                    oldest_note:
                      type: string
                      format: date-time
                      example: "2025-07-01T09:15:00Z"
                system_status:
                  type: object
                  properties:
                    gpt_available:
                      type: boolean
                      example: true
                    dropbox_connected:
                      type: boolean
                      example: true
                    last_scan:
                      type: string
                      format: date-time
                      example: "2025-07-03T15:45:00Z"
                config:
                  type: object
                  properties:
                    inbox_path:
                      type: string
                      example: "/Apps/SaveNotesGPT/Inbox"
                    kb_path:
                      type: string
                      example: "/Apps/SaveNotesGPT/NotesKB"
      401:
        description: Missing or invalid Bearer token
      500:
        description: Internal server error
    """
    try:
        from utils.inbox_utils import get_inbox_stats
        from utils.config_utils import load_config
        from services.gpt_service import OPENAI_API_KEY
        import os
        
        # Get inbox statistics
        inbox_stats = get_inbox_stats()
        
        # Get system configuration
        config = load_config()
        
        # Check system status
        system_status = {
            "gpt_available": bool(OPENAI_API_KEY and not os.getenv("MOCK_MODE")),
            "dropbox_connected": True,  # If we get here, Dropbox is working
            "last_scan": config.get("last_scan")
        }
        
        result = {
            "status": "success",
            "inbox_stats": inbox_stats,
            "system_status": system_status,
            "config": {
                "inbox_path": config.get("inbox_path"),
                "kb_path": config.get("kb_path")
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        log(f"❌ Get pull status error: {str(e)}", level="error")
        return jsonify({"status": "error", "message": str(e)}), 500


# Export for app.py
pull_routes = pull_bp