# services/pull_service.py - Simplified Pull Mode Service

from services.gpt_service import generate_metadata_from_content
from utils.inbox_utils import (
    scan_inbox_for_notes, 
    get_inbox_note_content, 
    get_multiple_inbox_notes_content,
    update_scan_timestamp,
    save_processed_files_list
)
from utils.logging_utils import log


class PullModeService:
    """
    Internal service for Pull Mode batch processing.
    Focuses on the core functionality: automatically processing notes with GPT.
    """
    
    def batch_process_notes(self, batch_size=5, auto_approve=False, custom_instructions=None, copy_linked_files=True):
        """
        Main Pull Mode functionality: scan inbox, generate metadata with GPT, optionally process to KB.
        
        Args:
            batch_size: Maximum number of notes to process
            auto_approve: Whether to automatically process generated metadata to KB
            custom_instructions: Optional custom instructions for GPT
            copy_linked_files: Whether to copy linked files (Obsidian support)
        
        Returns:
            dict: Processing results summary
        """
        # Step 1: Scan inbox
        scan_result = scan_inbox_for_notes(limit=batch_size, offset=0)
        notes = scan_result["notes"]
        
        if not notes:
            return {
                "status": "success",
                "processed": 0,
                "skipped": 0,
                "failed": 0,
                "results": [],
                "message": "No notes found in inbox"
            }
        
        results = []
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        
        log(f"🔄 Pull mode batch: processing {len(notes)} notes")
        
        # Step 2: Process each note
        for note_info in notes:
            filename = note_info["filename"]
            result = self._process_single_note(
                filename, 
                auto_approve=auto_approve,
                custom_instructions=custom_instructions,
                copy_linked_files=copy_linked_files
            )
            
            results.append(result)
            
            if result["status"] == "success":
                processed_count += 1
            elif result["status"] == "skipped":
                skipped_count += 1
            else:
                failed_count += 1
        
        # Step 3: Update system state
        update_scan_timestamp()
        processed_filenames = [r["filename"] for r in results if r["status"] == "success"]
        save_processed_files_list(processed_filenames)
        
        summary = {
            "status": "success",
            "processed": processed_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "results": results,
            "message": f"Batch complete: {processed_count} processed, {skipped_count} skipped, {failed_count} failed"
        }
        
        log(f"✅ Pull mode complete: {summary['message']}")
        return summary
    
    def preview_metadata(self, filenames=None, limit=5, custom_instructions=None):
        """
        Preview GPT-generated metadata without processing notes.
        Useful for testing and manual review.
        
        Args:
            filenames: Specific files to preview (if None, auto-discovers from inbox)
            limit: Maximum number of notes to preview (ignored if filenames provided)
            custom_instructions: Optional custom instructions for GPT
        
        Returns:
            dict: Preview results
        """
        if filenames:
            # Preview specific files
            content_results = get_multiple_inbox_notes_content(filenames)
        else:
            # Auto-discover files to preview
            scan_result = scan_inbox_for_notes(limit=limit, offset=0)
            discovered_filenames = [note["filename"] for note in scan_result["notes"]]
            content_results = get_multiple_inbox_notes_content(discovered_filenames)
        
        previews = []
        for content_result in content_results:
            filename = content_result["filename"]
            content = content_result["content"]
            error = content_result["error"]
            
            if content and not error:
                try:
                    metadata = generate_metadata_from_content(content, custom_instructions)
                    previews.append({
                        "filename": filename,
                        "metadata": metadata,
                        "content_preview": content[:200] + "..." if len(content) > 200 else content,
                        "error": None
                    })
                except Exception as e:
                    previews.append({
                        "filename": filename,
                        "metadata": None,
                        "content_preview": None,
                        "error": f"Metadata generation failed: {str(e)}"
                    })
            else:
                previews.append({
                    "filename": filename,
                    "metadata": None,
                    "content_preview": None,
                    "error": error or "Could not download content"
                })
        
        return {
            "status": "success",
            "previews": previews
        }
    
    def _process_single_note(self, filename, auto_approve=False, custom_instructions=None, copy_linked_files=True):
        """
        Process a single note: download content, generate metadata, optionally upload to KB.
        """
        try:
            # Step 1: Get note content
            content = get_inbox_note_content(filename)
            if not content:
                return {
                    "filename": filename,
                    "status": "failed",
                    "error": "Could not download note content"
                }
            
            # Step 2: Generate metadata with GPT
            metadata = generate_metadata_from_content(content, custom_instructions)
            if not metadata:
                return {
                    "filename": filename,
                    "status": "failed",
                    "error": "Failed to generate metadata with GPT"
                }
            
            # Step 3: Process to KB if auto-approved
            if auto_approve:
                process_result = self._upload_to_kb(filename, content, metadata, copy_linked_files)
                
                if process_result["status"] == "success":
                    return {
                        "filename": filename,
                        "status": "success",
                        "metadata_generated": metadata,
                        "kb_path": process_result["kb_path"],
                        "linked_files_copied": process_result.get("linked_files_copied", 0)
                    }
                else:
                    return {
                        "filename": filename,
                        "status": "failed",
                        "metadata_generated": metadata,
                        "error": process_result["error"]
                    }
            else:
                # Just generate metadata for review
                return {
                    "filename": filename,
                    "status": "skipped",
                    "metadata_generated": metadata,
                    "message": "Generated metadata, requires manual approval"
                }
                
        except Exception as e:
            log(f"❌ Error processing {filename}: {str(e)}", level="error")
            return {
                "filename": filename,
                "status": "failed",
                "error": str(e)
            }
    
    def _upload_to_kb(self, filename, content, metadata, copy_linked_files=True):
        """
        Upload processed note to Knowledge Base.
        Reuses the same logic as the Push mode to ensure consistency.
        """
        try:
            from services.dropbox_client import upload_structured_note
            from utils.dropbox_utils import generate_yaml_front_matter, sanitize_filename, process_note_with_links
            from datetime import datetime
            
            # Set default metadata values (same defaults as Push mode)
            metadata.setdefault("author", "pull-mode")
            metadata.setdefault("source", "gpt-pull-mode")
            metadata.setdefault("type", "note")
            metadata.setdefault("status", "processed")
            metadata.setdefault("language", "en")
            metadata.setdefault("uid", f"{sanitize_filename(metadata['title'])}-{metadata['date']}")

            # Compute KB paths (same logic as Push mode)
            parsed_date = datetime.strptime(metadata["date"], "%Y-%m-%d")
            subfolder = parsed_date.strftime("%Y-%m")
            new_filename = f"{metadata['date']}_{sanitize_filename(metadata['title'])}.md"
            kb_folder_path = f"/Apps/SaveNotesGPT/NotesKB/{subfolder}"
            kb_file_path = f"{kb_folder_path}/{new_filename}"

            # Process with link handling (same utility as Push mode)
            processing_result = process_note_with_links(
                content=content,
                metadata=metadata,
                kb_folder_path=kb_folder_path,
                copy_links=copy_linked_files
            )

            # Generate final content (same format as Push mode)
            processed_content = processing_result["processed_content"]
            final_metadata = processing_result["metadata"]
            copy_result = processing_result["copy_result"]
            
            yaml_block = generate_yaml_front_matter(final_metadata)
            structured_content = f"{yaml_block}\n\n{processed_content.strip()}"

            # Upload to KB
            upload_success = upload_structured_note(kb_file_path, structured_content)
            
            if upload_success:
                return {
                    "status": "success",
                    "kb_path": kb_file_path,
                    "linked_files_copied": copy_result["total_copied"]
                }
            else:
                return {"status": "error", "error": "Upload to Knowledge Base failed"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Singleton instance for easy importing
pull_service = PullModeService()