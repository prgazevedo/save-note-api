# 🧠 SaveNotesGPT — A Semantic Personal Knowledge System

**SaveNotesGPT** is a lightweight, extensible platform for converting handwritten notes, daily entries, and research logs into structured, metadata-rich Markdown files. These notes are safely archived in Dropbox and semantically indexed using GPT — forming a durable, searchable personal knowledge base.

This project is part of a broader **Personal Knowledge Infrastructure**, built to support long-term memory, reflection, and insight retrieval across platforms like Obsidian and ChatGPT.

---

## 📡 System Overview

Enable a fluid pipeline where:

1. Notes are written in any format — by hand or typed  
2. GPT is used to append them with metadata, tags, summaries  
3. They are saved in Markdown with standard YAML frontmatter  
4. Archived in Dropbox under date-based folders  
5. Queried later using GPT or Obsidian-style tools

---

## 🔄 Processing Modes

### 📤 Push Mode (GPT sends metadata)

In this mode, an external GPT (e.g., `JarbasGPT`) performs metadata generation and pushes notes to the system.
→GPT reads the raw note from Dropbox Inbox, prepends YAML, archives to `/NotesKB/YYYY-MM/`. 
1. GPT calls `/api/scan_inbox` to list new files in the Inbox
2. For each file, GPT uses `/get_inbox_note` to fetch raw Markdown content
3. GPT generates YAML metadata (title, date, tags, etc.)
4. Then calls:
   - `POST /process_note` → if file exists in Inbox and needs metadata injection
   - `POST /save_note` → if GPT generated the full Markdown already

---
### 📥 Pull Mode (App generates metadata using GPT)

In this mode, the system automatically generates metadata using GPT calls.

1. App calls `/api/scan_inbox` to detect new raw notes
2. For each, the backend:
   - Downloads file via Dropbox API
   - Sends content to OpenAI/GPT
   - Extracts title, date, tags, summary, etc.
3. App then injects the YAML and archives it using `/process_note`

✅ This allows the app to function without GPT actively pushing notes — enabling full automation, batch processing, or scheduled runs.

---
## 🧠 GPT Integration (JarbasGPT via OpenAPI)

To connect **JarbasGPT** with your API backend and enable semantic note processing, you can import the OpenAPI schema directly from GitHub using the **"Import from URL"** option in the [ChatGPT Actions interface](https://platform.openai.com/docs/assistants/tools/actions).

### ✅ Steps to Connect SaveNotesGPT API to GPT (Jarbas)

1. The OpenAPI schema of the GPT is inthe GitHub repo:

   ```
   save-note-api/gpt/jarbas_openapi.json
   ```

2. In ChatGPT, go to:
   ```
   Assistants → Add Tool → Actions → Import from URL
   ```

3. Paste the raw GitHub URL to your schema file:

   ```
   https://raw.githubusercontent.com/prgazevedo/save-note-api/main/gpt/jarbas_openapi.json
   ```

4. Click **Import**. The assistant will recognize the API and expose the actions for calling:

---

### 📡 Supported API Actions

- | Operation         | Path                        | Description                                  |
- |------------------|-----------------------------|----------------------------------------------|
- | `scan_inbox`     | `POST /api/scan_inbox`      | List Markdown files in Inbox                 |
- | `get_inbox_note` | `GET /api/get_inbox_note`   | Fetch raw Markdown content from Inbox        |
- | `process_note`   | `POST /api/process_note`    | Inject metadata and archive a note           |
- | `save_note`      | `POST /api/save_note`       | Upload full Markdown note with frontmatter   |

+ | Operation              | Method & Path                                     | Description                                    |
+ |------------------------|---------------------------------------------------|------------------------------------------------|
+ | `list_inbox_files`     | `GET /api/inbox/files`                            | List new `.md` files since last scan           |
+ | `get_inbox_note`       | `GET /api/inbox/notes/{filename}`                | Fetch raw Markdown content from Inbox          |
+ | `process_inbox_note`   | `POST /api/inbox/notes/{filename}/process`       | Inject metadata and archive the file           |
+ | `list_kb_notes`        | `GET /api/kb/notes`                               | List all KB notes                              |
+ | `list_kb_subfolder`    | `GET /api/kb/notes/folder?folder=YYYY-MM`        | List `.md` files in a specific KB subfolder    |
+ | `get_kb_note`          | `GET /api/kb/notes/{filename}`                  | Retrieve note content from KB by filename      |
+ | `save_note`            | `POST /api/kb/notes`                              | Upload full Markdown note with YAML metadata   |


---

Once connected, JarbasGPT can list notes, read raw Markdown, inject GPT metadata, and archive files — all through your authenticated Render deployment.
___

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

## 🔐 Login and admin Authentication

- `/login` and `/admin/dashboard` protected by session login
- Environment variables:
  - `ADMIN_USERNAME`
  - `ADMIN_PASSWORD` or `ADMIN_PASSWORD_HASH`
  - `FLASK_SECRET_KEY`

## 🔐 Token Authentication for GPT API Access

All `/api/*` endpoints require a valid `Authorization: Bearer ...` token in the request header.

The token is stored **securely in `.tokens`** file during local dev and as environment variable in production.

### 🔐 In `.tokens` file

```env
GPT_TOKEN=sk-GPT-YourSecureTokenHere

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

## 📜 License

MIT License — for personal use, reflection, and synthesis workflows.

---

## 🔖 Version Tag

**v3.0.0-openapi-gpt**  
Structure today. Retrieve tomorrow.
