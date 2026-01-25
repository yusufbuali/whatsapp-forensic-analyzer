# Development Prompt: WhatsApp Forensic Analyzer

## Project Context

I am building a **WhatsApp Forensic Analysis Tool** for a law enforcement digital forensics laboratory. The tool will analyze WhatsApp databases exported from mobile devices using tools like Oxygen Forensic Detective, Cellebrite UFED, or MSAB XRY.

## Technical Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL 15+
- **Frontend**: Bootstrap 5 + HTMX (minimal JavaScript)
- **Task Queue**: Celery + Redis
- **AI/ML**: Local models via Ollama (air-gapped compatible)
- **Deployment**: Docker Compose
- **GPU**: NVIDIA RTX 5080 (for AI inference)

## Core Requirements

### 1. Input Sources
- **iOS**: `ChatStorage.sqlite` (WhatsApp database)
- **Android**: `msgstore.db` (decrypted WhatsApp database)
- **Media Folder**: Images, audio files (.opus, .m4a), videos, documents

### 2. Extraction Features
Parse and display:
- All chat conversations (private and group)
- Messages with timestamps, sender info, read receipts
- Media files linked to messages
- GPS locations shared in chats
- Blocked contacts list
- Call logs (if available)
- Deleted messages recovery (from database freelist)

### 3. AI Analysis Module
Process all content through these analyzers:

| Analyzer | Engine | Purpose | Mode |
|----------|--------|---------|------|
| Speech-to-Text | Whisper large-v3 | Transcribe voice messages | LOCAL ✅ |
| Image OCR | Tesseract 5 | Extract text from images/screenshots | LOCAL ✅ |
| Image Captioning | LLaVA 13B | AI description of image contents | LOCAL ✅ |
| PII Detection | Presidio + Custom | Find emails, phones, names, IDs | LOCAL ✅ |
| Password Detection | Regex + DeepPass | Identify credentials, PINs, API keys | LOCAL ✅ |
| Crypto Detection | Custom Regex | Bitcoin/Ethereum wallet addresses | LOCAL ✅ |

> **⚠️ IMPORTANT: All analyzers run 100% locally by default (air-gapped compatible).**
> Cloud APIs (OpenAI, Azure, Anthropic) are OPTIONAL and DISABLED by default.

### 3.1 AI Output Verification System

**Every AI output must be verified before use as evidence:**

```python
class AIAnalysisResult:
    value: str                    # The extracted/analyzed content
    confidence: float             # 0.0 to 1.0
    verification_status: str      # 'auto_verified', 'pending_review', 'human_verified', 'rejected'
    verification_method: str      # 'confidence_threshold', 'cross_validation', 'human_review'
    verified_by: Optional[str]    # Examiner ID if human verified
    verified_at: Optional[datetime]
```

**Confidence Thresholds:**
- `≥ 0.85` → Auto-verified (with cross-validation)
- `0.60 - 0.84` → Flagged for human review
- `< 0.60` → Requires manual verification
- `< 0.20` → Auto-rejected

**Cross-Validation:**
- OCR: Compare Tesseract vs EasyOCR results
- PII: Require 2+ engines to agree (Presidio + StarPII + Regex)
- Transcription: Re-process 10% sample, check Word Error Rate

**Human Review Queue:**
- Side-by-side comparison (original vs AI output)
- Edit capability for corrections
- Full audit trail of all reviews

### 4. Custom PII Recognizers (Arabic/GCC)
Create Presidio recognizers for:
- Bahrain CPR (national ID): `\d{2}[01]\d[0-3]\d\d{5}`
- GCC phone numbers: `+973/966/971/968/965/974`
- Arabic names (NER model)
- IBAN for GCC banks
- Arabic keywords: هوية، جوال، رقم، حساب

### 5. Reporting
Generate tamper-proof forensic reports:
- PDF format (court-admissible)
- Excel export for data analysis
- Include hash verification (SHA256, MD5)
- Support Arabic text (RTL layout)
- Chain of custody documentation

### 6. Security Requirements
- Complete audit logging
- Hash verification on evidence access
- Role-based access control
- Air-gapped operation (no internet required)
- Read-only mode for evidence files

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Browser   │────▶│   FastAPI App   │────▶│   PostgreSQL    │
│   (Bootstrap)   │     │   (Python)      │     │   Database      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │ Whisper  │ │ Ollama   │ │ Presidio │
              │ (S2T)    │ │ (LLaVA)  │ │ (PII)    │
              └──────────┘ └──────────┘ └──────────┘
```

## Database Schema (Key Tables)

```sql
-- Cases
CREATE TABLE cases (
    id UUID PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE,
    examiner_name VARCHAR(100),
    created_at TIMESTAMP,
    description TEXT,
    cloud_api_enabled BOOLEAN DEFAULT FALSE  -- Must explicitly enable
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    contact_jid VARCHAR(50),
    contact_name VARCHAR(100),
    is_group BOOLEAN,
    message_count INTEGER
);

-- Messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_session_id INTEGER REFERENCES chat_sessions(id),
    sender_jid VARCHAR(50),
    timestamp TIMESTAMP,
    text_content TEXT,
    media_path VARCHAR(500),
    is_from_me BOOLEAN,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

-- AI Analysis Results (with verification)
CREATE TABLE ai_analysis (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id),
    analyzer_name VARCHAR(50),
    result_text TEXT,
    result_data JSONB,
    confidence DECIMAL(5,4),
    -- Verification fields
    verification_status VARCHAR(20) DEFAULT 'pending',  -- 'auto_verified', 'pending_review', 'human_verified', 'rejected'
    verification_method VARCHAR(30),  -- 'confidence_threshold', 'cross_validation', 'human_review'
    verified_by VARCHAR(100),
    verified_at TIMESTAMP,
    corrected_value TEXT,  -- If human corrected the output
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Human Review Queue
CREATE TABLE ai_review_queue (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    ai_analysis_id INTEGER REFERENCES ai_analysis(id),
    content_type VARCHAR(50),  -- 'transcription', 'ocr', 'pii', 'caption'
    original_content TEXT,
    ai_output TEXT,
    confidence DECIMAL(5,4),
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PII Findings (with verification)
CREATE TABLE pii_findings (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id),
    entity_type VARCHAR(50),
    entity_value TEXT,
    confidence DECIMAL(5,4),
    -- Verification
    detection_engines JSONB,  -- Which engines detected this: ["presidio", "starpii"]
    verified BOOLEAN DEFAULT FALSE,
    false_positive BOOLEAN DEFAULT FALSE
);

-- Analyzer Health/Calibration
CREATE TABLE analyzer_calibration (
    id SERIAL PRIMARY KEY,
    analyzer_name VARCHAR(50),
    test_run_at TIMESTAMP,
    accuracy_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    samples_tested INTEGER,
    status VARCHAR(20),  -- 'healthy', 'degraded', 'failed'
    details JSONB
);
```

## API Endpoints Required

```yaml
# Case Management
POST   /api/cases                          # Create case
GET    /api/cases                          # List cases
POST   /api/cases/{id}/upload              # Upload database + media
PUT    /api/cases/{id}/settings            # Update case settings (incl. cloud API toggle)

# Chat Analysis
GET    /api/cases/{id}/chats               # List all chats
GET    /api/cases/{id}/chats/{cid}/messages # Get messages
GET    /api/cases/{id}/locations           # GPS locations
GET    /api/cases/{id}/search?q={query}    # Full-text search

# AI Analysis
POST   /api/cases/{id}/analyze             # Start AI analysis
GET    /api/cases/{id}/analyze/status      # Check progress
GET    /api/cases/{id}/pii                 # PII findings
GET    /api/cases/{id}/passwords           # Detected passwords

# AI Verification (NEW)
GET    /api/cases/{id}/review-queue        # Items pending human review
GET    /api/cases/{id}/review-queue/{rid}  # Single item for review
POST   /api/cases/{id}/review-queue/{rid}/approve   # Approve AI output
POST   /api/cases/{id}/review-queue/{rid}/correct   # Correct and approve
POST   /api/cases/{id}/review-queue/{rid}/reject    # Reject as false positive
GET    /api/cases/{id}/verification-stats  # Accuracy metrics
GET    /api/analyzers/health               # Analyzer calibration status

# Reports
POST   /api/cases/{id}/reports/pdf         # Generate PDF
GET    /api/cases/{id}/reports/{rid}       # Download report
```

## Docker Services Required

```yaml
services:
  app:           # FastAPI application
  db:            # PostgreSQL 15
  redis:         # Task queue backend
  celery:        # Background workers
  ollama:        # LLaVA for image captioning
  whisper:       # Whisper ASR for transcription
  presidio:      # PII detection service
```

## UI Screens Needed

1. **Dashboard**: Case list, recent activity, system status
2. **Case View**: Evidence files, database info, hash verification
3. **Chat List**: All conversations with preview
4. **Chat Viewer**: WhatsApp-style message bubbles with media
5. **AI Analysis**: Progress, results by category, PII findings
6. **GPS Map**: Interactive map with location markers
7. **Report Generator**: Options, preview, download

## Implementation Priority

### Phase 1 (MVP)
- iOS database parser (ChatStorage.sqlite)
- Basic chat viewer
- Message search
- PDF report generation

### Phase 2
- Android database support
- AI analysis (Whisper + OCR)
- PII detection
- GPS map view

### Phase 3
- Image captioning (LLaVA)
- Custom Arabic recognizers
- Advanced reporting
- Performance optimization

## Specific Coding Tasks

When I ask you to help build this, please:

1. **Use Pydantic models** for all data structures
2. **Include proper error handling** with logging
3. **Write async code** where beneficial (FastAPI async endpoints)
4. **Add type hints** to all functions
5. **Include docstrings** explaining forensic relevance
6. **Handle Arabic text** properly (UTF-8, RTL)
7. **Generate tests** for critical functions

## Sample First Task

"Create the iOS WhatsApp database parser module that:
1. Connects to ChatStorage.sqlite
2. Extracts all chat sessions from ZWACHATSESSION
3. Extracts messages from ZWAMESSAGE with proper timestamp conversion
4. Links media items from ZWAMEDIAITEM
5. Returns Pydantic models for ChatSession and Message
6. Handles iOS 14-18 schema variations"

## Sample Task: AI Verification Module

"Create the AI output verification module that:
1. Receives AI analysis results with confidence scores
2. Applies confidence thresholds to auto-verify or queue for review
3. Implements cross-validation for OCR (Tesseract vs EasyOCR comparison)
4. Implements cross-validation for PII (require 2+ engines agreement)
5. Creates human review queue entries for medium/low confidence items
6. Provides API endpoints for reviewers to approve/correct/reject
7. Maintains full audit trail of all verification actions
8. Calculates accuracy metrics (correction rate, false positive rate)
9. Includes ground truth calibration runner that tests against known samples on startup"

## Sample Task: Settings & Cloud API Toggle

"Create the settings module that:
1. Allows enabling/disabling cloud APIs per case (disabled by default)
2. Shows clear warning when enabling cloud APIs about data leaving the system
3. Requires explicit confirmation checkbox before enabling
4. Logs all settings changes to audit trail
5. Provides master switch to disable all cloud APIs system-wide
6. Validates API keys when cloud services are enabled
7. Falls back to local-only mode if cloud APIs fail"

---

## Reference: iOS WhatsApp Tables

| Table | Key Columns |
|-------|------------|
| ZWACHATSESSION | Z_PK, ZCONTACTJID, ZPARTNERNAME, ZLASTMESSAGEDATE |
| ZWAMESSAGE | Z_PK, ZCHATSESSION, ZFROMJID, ZMESSAGEDATE, ZTEXT, ZMEDIAITEM |
| ZWAMEDIAITEM | Z_PK, ZMEDIALOCALPATH, ZMEDIAURL, ZLATITUDE, ZLONGITUDE |
| ZWAGROUPMEMBER | Z_PK, ZCHATSESSION, ZMEMBERJID |
| ZWAGROUPINFO | Z_PK, ZCHATSESSION, ZGROUPNAME |

## Reference: iOS Timestamp Conversion

iOS uses Core Data timestamps (seconds since 2001-01-01):

```python
from datetime import datetime, timedelta

def ios_timestamp_to_datetime(timestamp):
    """Convert iOS Core Data timestamp to datetime."""
    if timestamp is None:
        return None
    # Core Data reference date: 2001-01-01
    reference_date = datetime(2001, 1, 1)
    return reference_date + timedelta(seconds=timestamp)
```

---

*Use this prompt as context when asking Claude to help build specific components.*
