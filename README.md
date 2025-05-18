# 🧠 SaveNotesGPT — A Personal Insight Capture System

SaveNotesGPT is a lightweight, extensible system for converting handwritten notes, personal journaling, and daily reflections into structured Markdown insights — using OCR and GPT processing — and storing them safely in Dropbox, with minimal overhead and maximum semantic clarity.

This project is part of a broader effort to build a **Personal Knowledge Infrastructure**, designed for long-term self-understanding, reflection, and synthesis.

---

## 🚀 Project Vision

To create a **fluid, semi-automated workflow** where raw, expressive content (like morning pages, dreams, work notes, or personal reflections) can be:

1. **Captured** via handwriting or text  
2. **Processed** by GPT (e.g., insight extraction, thematic tagging)  
3. **Structured** into clean, timestamped Markdown files  
4. **Archived** to a Dropbox folder, accessible across devices

> This is not just about saving notes. It's about **distilling symbolic meaning** over time, and preserving a living archive of thought.

---
## 🔄 Information Flows in SaveNotesGPT

### 🧭 1. **Input Flow → ChatGPT → Analysis**

**Goal:** Bring personal or work notes (especially handwritten Morning Pages) into ChatGPT for reflection and structured insight extraction.

#### 🔁 Steps:
1. **Manual or digital note creation**  
   - Morning Pages written by hand.  
   - Work notes written in notebooks or digital tools.

2. **Capture and upload**  
   - Photos taken with iPad Mini.  
   - Uploaded to ChatGPT as images or scanned PDFs.  
   - OCR happens either before upload (using iOS or Notes app) or during processing.

3. **Processing and insight generation in ChatGPT (via GPT-Freud)**  
   - ChatGPT reads, interprets symbolically or reflectively.  
   - Outputs a clean **Markdown insight note** with structure and date.

4. **Export to filesystem (automated)**  
   - Via `save_note.py` Flask API.  
   - Triggered by a cURL request or future automation.  
   - Note is saved as `.md` in Dropbox → synced to iCloud via Hazel or manually.

---

### 📤 2. **Output Flow (GPT → Knowledge Base / Indexing)**

**Goal:** Turn GPT-generated insights into persistent and searchable knowledge base entries.

#### 🔁 Steps:
1. **Markdown content generation**  
   - Structured with title, date, tags, body, and metadata (future-proof).  
   - Example:
     ```markdown
   title: Morning Note
   date: 2025-05-17
   tags: [note, text]
   source: gpt-freud
   type: text
   author: pedro.azevedo
   uid: generated_uid
   linked_files: []
   status: processed
   language: pt
   summary: > Morning Notes

     ```

2. **Send via API**  
   - POST request to `https://save-note-api.onrender.com/save_note`.  
   - Can be triggered by user manually or via SwiftBar/Shortcuts automation.

3. **Secure Dropbox storage**  
   - File saved to configured Dropbox folder using API.  
   - Named by date and title (`2025-05-17_Reflections.md`).  
   - Synced to iCloud folder or backup device.

4. **(Optional) Future indexing**  
   - Add tag system, backlinking, daily/weekly index generation.  
   - Organize by theme: personal growth vs. work notes.

---

---

## ✍️ Use Cases

### 1. Morning Pages → GPT-Freud → Markdown
- You handwrite 3 morning pages.
- You take 3 photos (iPad/phone).
- Upload to ChatGPT with GPT-Freud persona.
- Insight is extracted and saved to Dropbox in Markdown format, tagged with date and themes.

### 2. Work Notes, Research, Strategy Logs
- Typed or handwritten work reflections are uploaded.
- GPT assists in extracting themes, highlights, or summaries.
- Saved as timestamped Markdown files, organized by topic or role.
- Eventually forms a searchable knowledge base.

---

## 🧰 Technology Stack

| Component        | Role                         | Tool Used        |
|------------------|------------------------------|------------------|
| Input            | Handwritten notes            | iPad Camera / Files app |
| Processing       | Insight extraction            | ChatGPT (local or plugin) |
| Backend API      | Accepts note upload           | `save_note.py` (Flask) |
| Hosting          | Lightweight server            | [Render.com](https://render.com) |
| Storage          | File sync + access            | Dropbox |
| Archival Format  | Portable & editable notes     | Markdown `.md` |
| Auth             | Token via Dropbox API         | OAuth2 + refresh tokens |
| Virtualization   | Dev environment               | Python venv |
| Logging          | Inline curl + server printout | Flask debug |

---

## 🧪 Status

| Feature                      | Status     |
|------------------------------|------------|
| Dropbox API Upload           | ✅ Working |
| Refresh Token Flow (Render)  | ✅ Working |
| GPT Insight-to-Markdown Flow | ✅ Manual, GPT-assisted |
| OCR Image to Insight         | 🔜 Planned |
| Auto Tagging or Theming      | 🟡 Manual |
| Folder Structure Support     | 🔜 Not implemented |
| Semantic Archive Browser     | 🔜 Optional (Obsidian, Craft) |

---


## 🧩 Open Questions

- Should this connect to Obsidian, Craft, or stay Markdown-native?
- Should image-to-text (OCR) and GPT pipeline be automated via webhook?
- Should saved notes be indexed in SQLite or a static site?
- Can GPT suggest semantic tags or surface links across entries?


---

## 📁 Directory Structure

```
SaveNotes/
├── save_note.py              # Flask app (Render-compatible)
├── get_refresh_token.py      # Auth setup for one-time refresh token
├── refresh_access_token.py   # Manual access token regeneration (if needed)
├── get_new_refresh_token.py  # Uses .env for safe rotation
├── test_env.py               # Env var sanity check
├── requirements.txt          # Flask + dotenv + requests
├── render.yaml               # Render deployment configuration
├── .env                      # 🔐 NEVER COMMIT — contains secrets
├── README.md                 # This file
```

---

## ✅ To Do Next

- [ ] Automate GPT ↔ Markdown feedback loop
- [ ] Auto OCR integration (iOS Shortcut?)
- [ ] Local index viewer (Craft, Obsidian plugin?)
- [ ] Setup backup + Git auto-commit of notes
- [ ] Allow GPT to fetch from Dropbox via signed URL (temporary, secure)
