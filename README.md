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

| Component            | Description                                         |
|----------------------|-----------------------------------------------------|
| **Capture**          | Daily logs, work notes, research snippets           |
| **Processing**       | GPT-generated metadata + summary                    |
| **API Backend**      | Flask microservice on Render                        |
| **Storage**          | Dropbox with date-based folders                     |
| **Format**           | Markdown `.md` with Obsidian/Craft-compatible YAML |
| **Semantic Layer**   | Embeddings + GPT vector search (planned)            |

---

## 🔄 Current Flows

### 📥 1. Structured Note Upload

```json
POST /save_note
{
  "content": "---\ntitle: Work Log – Backend Refactor\ndate: 2025-06-01\ntags: [work, backend, refactor]\nauthor: pedro.azevedo\nsource: gpt\ntype: text\nuid: work-refactor-20250601\nstatus: processed\nlinked_files: []\nlanguage: en\nsummary: >\n  Refactoring backend modular structure for note processing API.\n---\n\n# Backend Refactor Log\n\nToday I finalized the modular restructure of the Flask API..."
}
```

- Stored at:  
  `/Apps/SaveNotesGPT/NotesKB/2025-06/2025-06-01_Work_Log_Backend_Refactor.md`

---

### 📂 2. Folder Navigation (via API)

- `GET /list_kb` → returns: `["2025-05", "2025-06"]`
- `GET /list_kb_folder?folder=2025-06` → lists all `.md` files in the folder
- `GET /get_kb_note?filename=...` → returns raw Markdown

---

### 🧠 3. GPT-Based Metadata Injection

```json
POST /process_note
{
  "filename": "2025-06-01_work_log.md",
  "yaml": {
    "title": "Work Log – Backend Refactor",
    "date": "2025-06-01",
    "tags": ["work", "backend", "refactor"],
    "author": "pedro.azevedo",
    "source": "gpt",
    "type": "text",
    "uid": "work-refactor-20250601",
    "status": "processed",
    "linked_files": [],
    "language": "en",
    "summary": "Refactoring backend modular structure for note processing API."
  }
}
```

- Flask reads the file, constructs YAML, prepends it, and saves the structured note to `/NotesKB/YYYY-MM/`.

---

## 🧰 Stack

| Layer         | Tool / Service               |
|---------------|------------------------------|
| **Backend**   | Flask (Python)               |
| **Deployment**| Render.com                   |
| **Storage**   | Dropbox (OAuth2 Refresh)     |
| **Client**    | ChatGPT (Custom GPT)         |
| **Integration** | Craft, Obsidian            |
| **Language**  | Markdown `.md`               |

---

## 🧩 Compatibility

| Tool      | Compatibility            | Notes                                  |
|-----------|--------------------------|----------------------------------------|
| **Craft** | ✅ Accepts Markdown        | May display YAML as plain text         |
| **Obsidian** | ✅ Full YAML + backlinks | Ideal for queries, dataview, templates |
| **Custom GPT** | ✅ Can read/process notes | Calls API directly                     |

---

## 🧪 Status

| Feature                              | State     |
|--------------------------------------|-----------|
| Dropbox API File Upload              | ✅ Stable |
| GPT to Markdown Structuring Flow     | ✅ Manual |
| GPT Metadata Injection (`/process_note`) | ✅ Working |
| Obsidian/Craft Metadata Compatibility| ✅ Working |
| File Browser APIs (`/list_kb`, etc.) | ✅ Working |
| Embedding + Semantic Search          | 🔜 Planned |
| Batch GPT Processing Queue           | 🔜 Planned |

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

## 🧭 Future Roadmap

- [ ] `GET /list_inbox_notes` to find unprocessed files
- [ ] GPT-assisted batch processing via `/process_note`
- [ ] Embed notes into vector DB for GPT-powered semantic search
- [ ] SwiftBar/iOS Shortcuts integrations for upload

---

## 🔐 Privacy

No user data is retained.  
- Notes are sent only to Dropbox.  
- No server-side storage or tracking.  
- GPT only reads/transforms content at your request.

---

## 📜 License

MIT License — for personal use, reflection, and synthesis workflows.

---

## 🔖 Tag

```
v2.0.1-structured-pipeline-20250601
```

> Structure today. Retrieve tomorrow.
