# 🧠 SaveNotesGPT — A Semantic Personal Knowledge System

**SaveNotesGPT** is a lightweight, extensible platform for converting handwritten notes, daily entries, and research logs into structured, metadata-rich Markdown files. These notes are safely archived in Dropbox and semantically indexed using GPT — forming a durable, searchable personal knowledge base.

This project is part of a broader **Personal Knowledge Infrastructure**, built to support long-term memory, reflection, and insight retrieval across platforms like Obsidian, Craft, and ChatGPT.

---

## 🚀 Vision

Enable a fluid pipeline where:

1. Notes are written in any format — by hand or typed  
2. GPT structures them with metadata, tags, summaries  
3. They are saved in Markdown with standard YAML frontmatter  
4. Archived in Dropbox under date-based folders  
5. Queried later using GPT or Obsidian-style tools

---

## 📡 System Overview

| Component      | Description                                         |
|----------------|-----------------------------------------------------|
| **Capture**    | Daily logs, work notes, research snippets           |
| **Processing** | GPT-generated metadata + summary                    |
| **API Backend**| Flask microservice on Render                        |
| **Storage**    | Dropbox with date-based folders                     |
| **Format**     | Markdown .md with Obsidian/Craft-compatible YAML    |
| **Semantic Layer** | Embeddings + GPT vector search (planned)       |

---

## 🔄 Processing Modes

### 1️⃣ Push Metadata (external GPT adds metadata)

JarbasGPT or other client generates and sends full YAML:

`POST /api/process_note`

```json
{
  "filename": "2025-07-01_Meeting.md",
  "yaml": {
    "title": "Team Sync Notes",
    "date": "2025-07-01",
    "tags": ["team", "sync"],
    "author": "me",
    "summary": "Discussion of Q3 priorities and release plans."
  }
}
```

→ System reads the raw note from Dropbox Inbox, prepends YAML, archives to `/NotesKB/YYYY-MM/`.  
🔧 Implemented via: `archive_note_with_yaml()` in `process_service.py`

---

### 2️⃣ Pull Metadata (API extracts via GPT)

**Coming soon.**

`POST /api/process_file`

```json
{
  "filename": "README.md"
}
```

→ System will:

- Read note from Dropbox inbox  
- Parse or request GPT to generate YAML metadata  
- Archive to KB folder

---

## 📥 Note Upload (Direct)

`POST /save_note`

```json
{
  "title": "Work Log – Backend Refactor",
  "date": "2025-06-01",
  "content": "---\ntitle: Work Log – Backend Refactor\ndate: 2025-06-01\ntags: [work, backend, refactor]\nauthor: me\nsource: gpt\ntype: text\nuid: work-refactor-20250601\nstatus: processed\nlinked_files: []\nlanguage: en\nsummary: >\n  Refactoring backend modular structure for note processing API.\n---\n\n# Backend Refactor Log\n\nToday I finalized the modular restructure of the Flask API..."
}
```

Stored at:  
`/Apps/SaveNotesGPT/NotesKB/2025-06/2025-06-01_Work_Log_Backend_Refactor.md`

---

## 📂 Folder Navigation (via API)

- `GET /list_kb` → returns: `["2025-05", "2025-06"]`
- `GET /list_kb_folder?folder=2025-06` → lists all `.md` files in the folder
- `GET /get_kb_note?filename=...` → returns raw Markdown

---

## 🧰 Stack

| Layer    | Tool / Service           |
|----------|---------------------------|
| Backend  | Flask (Python)            |
| Deployment | Render.com              |
| Storage  | Dropbox (OAuth2 Refresh)  |
| Client   | ChatGPT (Custom GPT)      |
| Integration | Craft, Obsidian        |
| Language | Markdown .md              |
| Logging  | Logtail + JSON logs       |

---

## 🔐 Authentication

- `/login` and `/admin/dashboard` protected by session login
- Environment variables:
  - `ADMIN_USERNAME`
  - `ADMIN_PASSWORD` or `ADMIN_PASSWORD_HASH`
  - `FLASK_SECRET_KEY`

---

## 📜 Logging

Structured logging is handled via `logging_utils.py`:

| Output         | When                    |
|----------------|--------------------------|
| Stdout         | Always                   |
| Logtail        | If `LOGTAIL_TOKEN` is defined |
| admin_log.json | When running locally     |

All logs are JSON-structured to support Logtail ingestion and Render streaming.

---

## 🧪 Status

| Feature                         | State     |
|----------------------------------|-----------|
| Dropbox API File Upload         | ✅ Stable |
| GPT to Markdown Structuring Flow| ✅ Manual |
| GPT Metadata Injection          | ✅ Working|
| Obsidian/Craft Metadata Compatibility | ✅ Working |
| File Browser APIs               | ✅ Working |
| Embedded Swagger API Docs      | ✅ Working |
| Logtail Integration             | ✅ Working |
| Embedding + Semantic Search     | 🔜 Planned|
| Batch GPT Processing Queue      | 🔜 Planned|

---

## 📁 Dropbox Layout

```
Dropbox/
└── Apps/
    └── SaveNotesGPT/
        └── NotesKB/
            ├── 2025-05/
            │   └── 2025-05-17_Work_Log_API_Tests.md
            └── 2025-06/
                ├── 2025-06-01_work_log.md
                └── 2025-06-01_test_upload.md
```

---

## 🔧 Local Development Setup

1. Clone the repository

```bash
git clone https://github.com/prgazevedo/save-note-api.git
cd save-note-api
```

2. Run setup script

```bash
bash scripts/setup_dev.sh
```

Then fill in your Dropbox API credentials and admin variables in the generated `.env` file.

3. Run the Flask API

```bash
source venv/bin/activate
python app.py
```

---

## ⚙️ Project Scripts

| Script                          | Purpose                             |
|----------------------------------|-------------------------------------|
| scripts/init_modular_flask_kb.sh| Scaffolds a new modular Flask API   |
| scripts/setup_dev.sh            | Prepares dev environment and configs|

---

## 🔭 Swagger API

- Available at: `/apidocs`
- Uses Flasgger
- Custom description links to README
- Docs auto-load all Flask routes

---

## 🔐 Admin Dashboard

- Available at: `/admin/dashboard`
- Requires login with env credentials
- Allows:
  - Editing inbox / KB folders
  - Triggering inbox scan
  - Viewing logs and recent files

---

## 🧭 Roadmap

- `GET /list_inbox_notes` to find unprocessed files
- GPT-assisted batch processing via `/process_note`
- Embed notes into vector DB for GPT-powered semantic search
- SwiftBar/iOS Shortcuts integrations for upload

---

## 📜 License

MIT License — for personal use, reflection, and synthesis workflows.

---

## 🔖 Version Tag

**v2.2.0-arch-pushpull**  
Structure today. Retrieve tomorrow.
