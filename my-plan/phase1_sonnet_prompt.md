# WhatsApp Forensic Analyzer - Phase 1 Build

## Development Environment
- **Primary Environment**: GitHub Codespaces
- **Repository**: https://github.com/yusufbuali/whatsapp-forensic-analyzer
- **Port**: 80 (app accessible via Codespace forwarded URL)
- **Working Method**: All code changes made directly in Codespace

## Tech Stack (Fixed)
- **Backend**: Python 3.11+ / FastAPI
- **Database**: PostgreSQL 15
- **Frontend**: Bootstrap 5 + HTMX (minimal JS, server-rendered)
- **Task Queue**: Celery + Redis
- **AI Options**: Local Ollama (primary) / Cloud API (optional)
- **Deployment**: Docker Compose

## Coding Standards
- Use Python type hints everywhere
- Include comprehensive docstrings (Google style)
- Follow existing patterns in the codebase
- Create unit tests for critical functions
- Use SQLAlchemy for all database operations
- Follow REST API conventions

## Common Commands
```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f app

# Restart after code changes
docker-compose restart app

# Access database
docker-compose exec db psql -U postgres -d forensic

# Run tests
docker-compose exec app pytest
```

## Phase 1 Deliverables (This Chat)

### 1. Docker Compose Setup
Create `docker-compose.yml` with services:
- `app` - FastAPI application (port 8000)
- `db` - PostgreSQL 15
- `redis` - For Celery task queue
- `celery_worker` - Background tasks

### 2. iOS WhatsApp Database Parser
Parse `ChatStorage.sqlite` (iOS WhatsApp backup):

**Key Tables:**
```sql
-- ZWACHATSESSION: Chat conversations
-- Key columns: Z_PK, ZCONTACTJID, ZPARTNERNAME, ZMESSAGECOUNTER, ZLASTMESSAGEDATE

-- ZWAMESSAGE: All messages  
-- Key columns: Z_PK, ZCHATSESSION, ZFROMJID, ZTEXT, ZMESSAGEDATE, ZISFROMME, ZMEDIAITEM

-- ZWAMEDIAITEM: Media files
-- Key columns: Z_PK, ZMESSAGE, ZMEDIALOCALPATH, ZVCARDSTRING, ZLATITUDE, ZLONGITUDE
```

**iOS Timestamp Conversion:**
```python
from datetime import datetime, timedelta
# iOS Core Data: seconds since 2001-01-01
reference_date = datetime(2001, 1, 1)
actual_time = reference_date + timedelta(seconds=ios_timestamp)
```

### 3. Database Schema
```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(50) UNIQUE NOT NULL,
    examiner_name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence_items (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size BIGINT,
    sha256_hash VARCHAR(64),
    md5_hash VARCHAR(32),
    device_type VARCHAR(20), -- 'ios' or 'android'
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    evidence_id INTEGER REFERENCES evidence_items(id) ON DELETE CASCADE,
    original_id INTEGER, -- Z_PK from source
    contact_jid VARCHAR(100),
    contact_name VARCHAR(100),
    is_group BOOLEAN DEFAULT FALSE,
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
    original_id INTEGER,
    sender_jid VARCHAR(100),
    sender_name VARCHAR(100),
    timestamp TIMESTAMP,
    text_content TEXT,
    is_from_me BOOLEAN,
    message_type VARCHAR(20), -- 'text', 'image', 'video', 'audio', 'document', 'location'
    media_path VARCHAR(500),
    media_mime_type VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    action VARCHAR(50),
    details JSONB,
    performed_by VARCHAR(100),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);
```

### 4. API Endpoints
```python
# Case Management
POST   /api/cases                     # Create new case
GET    /api/cases                     # List all cases
GET    /api/cases/{id}                # Get case details
DELETE /api/cases/{id}                # Delete case

# Evidence Upload
POST   /api/cases/{id}/evidence       # Upload WhatsApp DB + media folder
GET    /api/cases/{id}/evidence       # List evidence items
GET    /api/cases/{id}/evidence/{eid}/verify  # Verify hash integrity

# Chat Data
GET    /api/cases/{id}/chats          # List all chat sessions
GET    /api/cases/{id}/chats/{cid}/messages  # Get messages (paginated)
GET    /api/cases/{id}/chats/{cid}/media     # List media files

# Search
GET    /api/cases/{id}/search?q={query}      # Full-text search messages
```

### 5. Web UI Pages
1. **Dashboard** (`/`) - List cases, create new case button
2. **Case View** (`/cases/{id}`) - Evidence files, upload button, hash verification
3. **Chat List** (`/cases/{id}/chats`) - Table of all conversations, sortable
4. **Chat Viewer** (`/cases/{id}/chats/{cid}`) - WhatsApp-style message bubbles, media thumbnails

### 6. File Structure
```
whatsapp-forensic-analyzer/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database.py          # DB connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── case.py          # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── ios_parser.py    # ChatStorage.sqlite parser
│   │   └── base_parser.py   # Abstract base
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── cases.py
│   │   ├── evidence.py
│   │   ├── chats.py
│   │   └── search.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── hash_service.py  # SHA256/MD5 calculation
│   │   └── import_service.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── celery_app.py
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── dashboard.html
│       ├── case_view.html
│       ├── chat_list.html
│       └── chat_viewer.html
├── static/
│   ├── css/
│   └── js/
├── uploads/                 # Evidence storage
└── tests/
```

## Critical Requirements

1. **Air-Gapped Operation**: 100% offline capability, optional cloud mode for non-sensitive environments
2. **Evidence Integrity**: 
   - SHA256 + MD5 hash on upload
   - Never modify original files - create working copies
   - Verify hash on every access
   - Chain of custody tracking
3. **Audit Logging**: 
   - Log every action (view, search, export) with timestamp + user
   - Immutable logs (append-only)
4. **AI Verification** (Phase 3):
   - All AI outputs flagged as "AI-generated"
   - Human verification required
   - Confidence scores visible

## Response Guidelines
- When creating/modifying code, show full file content
- Test changes using docker-compose commands
- Provide verification steps after each change
- If changes require container restart, include that command

## First Task

Start by creating the complete Docker Compose setup and project structure. Then implement the iOS database parser that can:
1. Open ChatStorage.sqlite
2. Extract all chat sessions with contact info
3. Extract all messages with timestamps (properly converted)
4. Link media items to messages
5. Return structured data ready for database insertion

After the parser works, create the FastAPI endpoints and basic UI.

---

## Reference: Sample iOS Database Queries

```sql
-- Get all chats
SELECT 
    Z_PK as id,
    ZCONTACTJID as contact_jid,
    ZPARTNERNAME as contact_name,
    ZMESSAGECOUNTER as message_count,
    ZLASTMESSAGEDATE as last_message_date
FROM ZWACHATSESSION
WHERE ZCONTACTJID IS NOT NULL;

-- Get messages for a chat
SELECT 
    m.Z_PK as id,
    m.ZFROMJID as sender_jid,
    m.ZTEXT as text_content,
    m.ZMESSAGEDATE as timestamp,
    m.ZISFROMME as is_from_me,
    m.ZMESSAGETYPE as message_type,
    mi.ZMEDIALOCALPATH as media_path,
    mi.ZLATITUDE as latitude,
    mi.ZLONGITUDE as longitude
FROM ZWAMESSAGE m
LEFT JOIN ZWAMEDIAITEM mi ON mi.ZMESSAGE = m.Z_PK
WHERE m.ZCHATSESSION = ?
ORDER BY m.ZMESSAGEDATE;
```

Build this step by step, creating working code at each stage. Ask if you need clarification on any requirements.
