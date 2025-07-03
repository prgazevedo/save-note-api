# 🧠 SaveNotesGPT — AI-Powered Personal Knowledge Management

[![Mock Tests](https://github.com/prgazevedo/save-note-api/actions/workflows/test_mock_api.yml/badge.svg)](https://github.com/prgazevedo/save-note-api/actions/workflows/test_mock_api.yml)
[![Staging Tests](https://github.com/prgazevedo/save-note-api/actions/workflows/test_staging_api.yml/badge.svg)](https://github.com/prgazevedo/save-note-api/actions/workflows/test_staging_api.yml)

---

Welcome to the SaveNotesGPT API documentation and resources.

🚀 Live Service

- Production API: https://save-note-api.onrender.com
- API Documentation: https://save-note-api.onrender.com/apidocs/
- Admin Dashboard: https://save-note-api.onrender.com/admin/dashboard

📋 API Resources 

- OpenAPI Specifications at github:
-- GPT Plugin Manifest: [ai-plugin.json](https://prgazevedo.github.io/save-note-api/.well-known/ai-plugin.json)
-- OpenAPI Schema: [jarbas_openapi.json](https://save-note-api.onrender.com/gpt/jarbas_openapi.json)
-- OpenAPI Specifications at render: [https://save-note-api.onrender.com/](https://save-note-api.onrender.com/static/.well-known/ai-plugin.json)


**SaveNotesGPT** transforms your raw notes into a structured, searchable personal knowledge base using AI-generated metadata. 
Drop in handwritten notes, thoughts, or Obsidian files — GPT enhances them with tags, summaries, and organization.

---
## 🔄 How It Works

```
Raw Note (Inbox) → GPT Processing → Structured Knowledge Base
```

1. **Capture**: Add notes to your Dropbox Inbox (handwritten, typed, Obsidian exports)
2. **Enhance**: GPT adds metadata (tags, summaries, titles, dates) 
3. **Organize**: Notes move to date-organized Knowledge Base with preserved links
4. **Search**: Use Obsidian, GPT, or API to find connections and insights


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

1. GPT calls `GET /api/inbox/notes` to list new files in the Inbox
2. For each file, GPT uses `GET /api/inbox/notes/{filename}` to fetch raw Markdown content
3. GPT generates YAML metadata (title, date, tags, etc.)
4. Then calls `PATCH /api/inbox/notes/{filename}` to process and archive

### 📥 Pull Mode (App generates metadata using GPT)

In this mode, the system automatically generates metadata using GPT calls.

1. App calls `GET /api/inbox/notes` to detect new raw notes
2. For each, the backend:
   - Downloads file via Dropbox API
   - Sends content to OpenAI/GPT
   - Extracts title, date, tags, summary, etc.
3. App then injects the YAML and archives it using the process endpoint

✅ This allows the app to function without GPT actively pushing notes — enabling full automation, batch processing, or scheduled runs.

---

## 🎯 Use Cases

- **📝 Quick Capture**: Voice-to-text → API → GPT processing
- **📚 Research Notes**: Web clips → Inbox → AI categorization  
- **✍️ Handwritten Notes**: OCR → Upload → Metadata enhancement
- **🔗 Obsidian Sync**: Export vault → Process → Enhanced re-import
- **🤖 ChatGPT Memory**: Give ChatGPT access to your personal knowledge base

---


## 🚀 Quick Start

### 1. **Add a Raw Note**
```bash
curl -X POST https://save-note-api.onrender.com/api/inbox/notes \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Meeting Ideas", 
    "content": "# Ideas\n\n- Discuss Q4 roadmap\n- Review capacity"
  }'
```

### 2. **Discover Notes** 
```bash
curl https://save-note-api.onrender.com/api/inbox/notes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. **Process with GPT**
```bash
curl -X PATCH https://save-note-api.onrender.com/api/inbox/notes/2025-07-03_meeting-ideas.md \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "process",
    "metadata": {
      "title": "Q4 Planning Meeting Ideas",
      "date": "2025-07-03", 
      "tags": ["meeting", "planning", "q4"],
      "summary": "Initial ideas for Q4 planning discussion"
    }
  }'
```

### 4. **Browse Knowledge Base**
```bash
curl https://save-note-api.onrender.com/api/kb/notes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📡 API Endpoints

### **📥 Inbox (Raw Notes)**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/inbox/notes` | List raw notes awaiting processing |
| `GET` | `/api/inbox/notes/{filename}` | Read note content |
| `POST` | `/api/inbox/notes` | Create new raw note |
| `PATCH` | `/api/inbox/notes/{filename}` | Process with GPT metadata |

### **📚 Knowledge Base (Processed Notes)**  
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/kb/notes` | List processed notes |
| `GET` | `/api/kb/notes/{filename}` | Read processed note |
| `GET` | `/api/kb/folders` | List date-organized folders |
| `POST` | `/api/kb/notes` | Create processed note directly |

---

## 🔗 Obsidian Integration

SaveNotesGPT fully supports **Obsidian linking**:

- **`[[Wiki Links]]`** - Links preserved across vault
- **`![[Embedded Files]]`** - Images/attachments copied automatically  
- **`[Markdown](./links)`** - Relative paths maintained
- **Folder structure** - Preserved when copying linked files

**Example**: Upload an Obsidian note with `![[diagram.png]]` → GPT processes it → Both note and diagram.png end up in your Knowledge Base with working links.

---

## 🧠 GPT Integration 

### **Connect to ChatGPT:**

1. Go to **ChatGPT → Create GPT**
2. **Import API**: Use `https://save-note-api.onrender.com/.well-known/ai-plugin.json`
3. **Set Authentication**: Bearer token (get from your deployment)
4. **Test**: "Scan my inbox for new notes to process"

### **GPT Instructions:**
```
You are SaveNotesGPT, an AI assistant that processes raw notes into structured knowledge.

Your workflow:
1. Scan inbox for unprocessed notes
2. Read note content and understand context  
3. Generate meaningful metadata (title, tags, summary)
4. Process notes to move them to organized Knowledge Base

Always generate 3-7 descriptive tags, concise summaries, and clear titles.
```

---

## 🏗️ Architecture

| Layer | Technology |
|-------|------------|
| **API** | Flask (Python) |
| **Storage** | Dropbox (OAuth2) |
| **Deployment** | Render.com |
| **Client** | ChatGPT Actions |
| **Integration** | Obsidian, Craft |
| **Format** | Markdown + YAML |

---

## 📁 Knowledge Base Structure

```
Dropbox/Apps/SaveNotesGPT/
├── Inbox/                           # Raw notes
│   ├── 2025-07-03_ideas.md         # Unprocessed
│   └── attachments/
│       └── diagram.png             # Linked files
└── NotesKB/                        # Processed notes  
    └── 2025-07/                    # Date-organized
        ├── 2025-07-03_meeting-notes.md  # With YAML metadata
        └── diagram.png             # Copied with links intact
```

---

## 🔧 Local Development

```bash
# Clone and setup
git clone https://github.com/prgazevedo/save-note-api.git
cd save-note-api
bash scripts/setup_dev.sh

# Configure environment
# Edit .env with your Dropbox credentials

# Run locally  
source venv/bin/activate
python app.py
```

**API Documentation**: `http://localhost:5000/apidocs/`

---

## 🔐 Authentication

### **API Access**
All `/api/*` endpoints require Bearer token authentication:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://save-note-api.onrender.com/api/inbox/notes
```

### **Admin Dashboard**
- **URL**: `/admin/dashboard`  
- **Credentials**: Set via `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables
- **Features**: View logs, manage configurations, trigger scans

---

## 📜 Version History

- **v3.1.0** - API refactor with improved Swagger docs and route organization
- **v3.0.0** - API GPT Actions Auth integration (Bearer token)
- **v2.0.0** - RESTful API redesign, Obsidian support, GPT Actions integration
- **v1.0.0** - Initial release with basic note processing

---

## 📄 License

MIT License — Build your knowledge, own your data.

---

**Structure today. Retrieve tomorrow.** 🧠✨
