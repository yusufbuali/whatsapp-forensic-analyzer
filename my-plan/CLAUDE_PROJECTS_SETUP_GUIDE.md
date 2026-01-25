# Claude Projects Setup Guide for WhatsApp Forensic Analyzer

## What is Claude Projects?

Claude Projects lets you create a persistent workspace where:
- Files you upload stay available across ALL chats in that project
- Claude remembers the project context without re-pasting
- You can have multiple related chats that all see the same codebase

## Step 1: Create the Project

1. Go to **claude.ai**
2. Click **"Projects"** in the left sidebar (or top menu on mobile)
3. Click **"Create Project"**
4. Fill in:
   - **Name**: `WhatsApp Forensic Analyzer`
   - **Description**: `Forensic analysis tool for WhatsApp data extraction - iOS/Android support, AI analysis, court-admissible reports`

## Step 2: Add Project Instructions

In the project settings, add these **Custom Instructions**:

```
# WhatsApp Forensic Analyzer - Development Guide

## DEVELOPMENT ENVIRONMENT
- **Primary Environment**: GitHub Codespaces
- **Repository**: https://github.com/yusufbuali/whatsapp-forensic-analyzer
- **Port**: 80
- **Working Method**: All code changes should be made directly in the Codespace environment

## TECH STACK (fixed)
- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL 15
- **Frontend**: Bootstrap 5 + HTMX (minimal JS, server-rendered)
- **Task Queue**: Celery + Redis
- **AI Options**: 
  - Primary: Local Ollama (air-gapped deployments)
  - Optional: Cloud/API (for connected deployments)
- **Deployment**: Docker Compose

## CRITICAL REQUIREMENTS
1. **Air-Gapped Operation**: 100% offline capability, optional cloud mode
2. **Evidence Integrity**: SHA256 + MD5 hash, never modify originals, chain of custody
3. **Audit Trail**: Complete logging, immutable logs (append-only)
4. **AI Verification**: All AI outputs flagged, human verification required, confidence scores visible

## CODING STANDARDS
- Use Python type hints everywhere
- Include comprehensive docstrings (Google style)
- Follow existing patterns in the codebase
- Create unit tests for critical functions
- Use SQLAlchemy for all database operations
- Follow REST API conventions

## COMMON COMMANDS
docker-compose up --build          # Start all services
docker-compose logs -f app         # View logs
docker-compose restart app         # Restart after changes
docker-compose exec db psql -U postgres -d forensic  # Access DB

## RESPONSE GUIDELINES
- When creating/modifying code, show full file content
- Test changes using docker-compose commands
- Provide verification steps after each change
- If changes require container restart, include that command
```

## Step 3: Phase 1 - Initial Setup

### Start First Chat

1. Inside your project, click **"New Chat"**
2. Name it: `Phase 1 - Core Setup`
3. Paste the entire `phase1_sonnet_prompt.md`
4. Let Sonnet build the initial structure

### After Sonnet Creates Files

As Sonnet generates code, **save files locally** and **add key files to Project Knowledge**:

Click **"Add to Project Knowledge"** (📎 icon in project settings) and upload:

```
Phase 1 Files to Add:
┌─────────────────────────────────────────────────────────────┐
│ PRIORITY   │ FILE                        │ WHY              │
├────────────┼─────────────────────────────┼──────────────────┤
│ ⭐ HIGH    │ docker-compose.yml          │ Infrastructure   │
│ ⭐ HIGH    │ app/models/case.py          │ Data models      │
│ ⭐ HIGH    │ app/models/schemas.py       │ API schemas      │
│ ⭐ HIGH    │ app/parsers/ios_parser.py   │ Core parser      │
│ ⭐ HIGH    │ app/database.py             │ DB connection    │
│ MEDIUM     │ app/routers/cases.py        │ API endpoints    │
│ MEDIUM     │ app/routers/chats.py        │ API endpoints    │
│ MEDIUM     │ requirements.txt            │ Dependencies     │
│ LOW        │ app/templates/base.html     │ UI template      │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1 Chat Workflow

```
Chat: "Phase 1 - Core Setup"
├── Message 1: Paste phase1_sonnet_prompt.md
├── Message 2: "Create the docker-compose.yml"
├── Message 3: "Now create the iOS parser"
├── Message 4: "Add the database models"
├── Message 5: "Create FastAPI endpoints for cases"
├── ... continue until Phase 1 complete
└── Final: Test everything works

→ Upload completed files to Project Knowledge
→ Start new chat for Phase 2
```

## Step 4: Phase 2 - Features

### Start New Chat

1. Click **"New Chat"** (still in same project)
2. Name it: `Phase 2 - Search, Maps, Reports`
3. Brief context + paste prompt:

```markdown
Phase 1 is complete. The project files are in Project Knowledge.
Current status:
- Docker setup working
- iOS parser extracts chats/messages/media
- Basic UI shows chat list and messages
- Case management with hash verification

Now starting Phase 2. Here's the plan:
[paste phase2_sonnet_prompt.md]

Start with the Android parser.
```

### Files to Add After Phase 2

```
Phase 2 Files to Add:
┌─────────────────────────────────────────────────────────────┐
│ PRIORITY   │ FILE                        │ WHY              │
├────────────┼─────────────────────────────┼──────────────────┤
│ ⭐ HIGH    │ app/parsers/android_parser.py│ Android support │
│ ⭐ HIGH    │ app/services/search_service.py│ Full-text search│
│ ⭐ HIGH    │ app/services/report_service.py│ PDF generation │
│ MEDIUM     │ app/routers/locations.py    │ GPS endpoints   │
│ MEDIUM     │ app/routers/reports.py      │ Report endpoints│
│ MEDIUM     │ app/templates/map_view.html │ Map UI          │
│ LOW        │ Updated requirements.txt    │ New deps        │
└─────────────────────────────────────────────────────────────┘
```

## Step 5: Phase 3 - AI Integration

### Start New Chat

1. Click **"New Chat"**
2. Name it: `Phase 3 - AI Analysis`
3. Context + prompt:

```markdown
Phases 1-2 complete. The project has:
- iOS + Android parsing
- Full-text search
- GPS map view
- PDF/Excel reports
- All in Docker

Now adding AI analysis. Key requirement: ALL AI runs locally (air-gapped).
Hardware: RTX 5080 GPU available.

[paste phase3_sonnet_prompt.md]

Start with adding Whisper for voice message transcription.
```

### Files to Add After Phase 3

```
Phase 3 Files to Add:
┌─────────────────────────────────────────────────────────────┐
│ PRIORITY   │ FILE                        │ WHY              │
├────────────┼─────────────────────────────┼──────────────────┤
│ ⭐ HIGH    │ app/services/whisper_service.py│ Transcription │
│ ⭐ HIGH    │ app/services/ocr_service.py │ Text extraction │
│ ⭐ HIGH    │ app/services/pii_service.py │ PII detection   │
│ ⭐ HIGH    │ app/services/verification_service.py│ AI verify│
│ MEDIUM     │ app/tasks/ai_tasks.py       │ Celery tasks    │
│ MEDIUM     │ app/routers/analysis.py     │ AI endpoints    │
│ MEDIUM     │ Updated docker-compose.yml  │ New services    │
│ LOW        │ config/presidio/            │ PII config      │
└─────────────────────────────────────────────────────────────┘
```

## Project Knowledge Management

### Size Limits
- Claude Projects has a knowledge limit (~200K tokens)
- Don't upload everything - only KEY files
- Remove outdated versions when you update

### What TO Upload ✅
- Core models and schemas
- Parsers (ios_parser.py, android_parser.py)
- Service files (business logic)
- Docker configuration
- Database schema

### What NOT to Upload ❌
- node_modules / __pycache__
- Large static files (CSS libraries, images)
- Test data files
- Temporary/generated files
- Multiple versions of same file

### Keeping Knowledge Updated

When you modify a file significantly:
1. Go to Project Knowledge
2. Delete the old version
3. Upload the new version

```
Example: You improved ios_parser.py

1. Project Settings → Knowledge
2. Find "ios_parser.py" → Delete
3. Upload new ios_parser.py
4. New chats will use updated version
```

## Recommended Chat Structure

```
Project: WhatsApp Forensic Analyzer
│
├── 📁 Project Knowledge (files persist here)
│   ├── docker-compose.yml
│   ├── app/models/case.py
│   ├── app/parsers/ios_parser.py
│   └── ... (key files)
│
├── 💬 Phase 1 - Core Setup (completed)
│   └── [archived - don't delete, good for reference]
│
├── 💬 Phase 1 - Bug Fixes (completed)
│   └── [fixed timestamp conversion issue]
│
├── 💬 Phase 2 - Search & Maps (completed)
│
├── 💬 Phase 2 - Reports (completed)
│
├── 💬 Phase 3 - Whisper Integration (active)
│   └── [currently working on transcription]
│
└── 💬 Quick Questions
    └── [misc questions that don't need full context]
```

## Troubleshooting

### "Claude doesn't see my file"
- Check if file is in Project Knowledge
- Try: "Can you see the ios_parser.py in project knowledge?"
- Re-upload if needed

### "Claude forgot what we built"
- Start message with brief context:
  "Continuing the WhatsApp forensic tool. We're working on the OCR service."
- Reference specific files: "Update the ocr_service.py to add Arabic support"

### "Project Knowledge is full"
- Remove old file versions
- Keep only current, essential files
- Move reference docs to local storage

### "Claude is confused about versions"
- Be explicit: "Use the ios_parser.py from Project Knowledge, not the one I pasted earlier"
- When in doubt, paste the current code directly

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY WORKFLOW                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Open Project "WhatsApp Forensic Analyzer"              │
│                                                             │
│  2. Continue existing chat OR start new chat               │
│     - Same topic? Continue existing                        │
│     - New feature? New chat with context                   │
│                                                             │
│  3. When Sonnet creates/updates a file:                    │
│     a. Copy code to your local project                     │
│     b. Test it works                                       │
│     c. If it's a KEY file, update Project Knowledge        │
│                                                             │
│  4. Starting new chat? Include:                            │
│     - Current phase                                        │
│     - What's working                                       │
│     - What you need next                                   │
│     - Paste relevant prompt (phase1/2/3)                   │
│                                                             │
│  5. End of session:                                        │
│     - Ensure local files are saved                         │
│     - Update Project Knowledge if major changes            │
│     - Note where you left off                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Files Checklist

Print this and check off as you add files:

### Phase 1 Files
- [ ] docker-compose.yml
- [ ] Dockerfile
- [ ] requirements.txt
- [ ] app/main.py
- [ ] app/config.py
- [ ] app/database.py
- [ ] app/models/case.py
- [ ] app/models/schemas.py
- [ ] app/parsers/ios_parser.py
- [ ] app/routers/cases.py
- [ ] app/routers/chats.py
- [ ] app/services/hash_service.py

### Phase 2 Files
- [ ] app/parsers/android_parser.py
- [ ] app/services/search_service.py
- [ ] app/services/report_service.py
- [ ] app/services/export_service.py
- [ ] app/routers/locations.py
- [ ] app/routers/reports.py
- [ ] app/routers/search.py

### Phase 3 Files
- [ ] app/services/whisper_service.py
- [ ] app/services/ocr_service.py
- [ ] app/services/pii_service.py
- [ ] app/services/caption_service.py
- [ ] app/services/verification_service.py
- [ ] app/tasks/ai_tasks.py
- [ ] app/routers/analysis.py
- [ ] Updated docker-compose.yml (with AI services)

---

Good luck with the build! 🚀
