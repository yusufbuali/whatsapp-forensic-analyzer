# WhatsApp Forensic Analysis Tool - Technical Specification

## Project Overview

**Project Name:** Forensic WhatsApp Analyzer (FWA)  
**Version:** 1.0  
**Target Users:** Digital Forensics Examiners, Law Enforcement Forensic Labs  
**Author:** [Your Lab Name]  
**Date:** January 2026

---

## 1. Executive Summary

A multi-threaded, AI-powered forensic tool for analyzing WhatsApp data extracted from mobile devices (iOS and Android). The tool processes WhatsApp SQLite databases and media folders to extract, analyze, and report on chat conversations, media content, GPS locations, contacts, and automatically detect sensitive information (PII, passwords, credentials) using AI/ML analyzers.

---

## 2. Core Objectives

1. **Parse WhatsApp databases** from both iOS (`ChatStorage.sqlite`) and Android (`msgstore.db`)
2. **Extract and display** all chat conversations (private and group)
3. **Process media files** (images, audio, video) with AI analysis
4. **Detect sensitive information** (PII, passwords, crypto wallets, credentials)
5. **Generate court-admissible reports** with hash verification (tamper-proof)
6. **Support multi-language** including Arabic (RTL support)
7. **Provide web-based interface** for ease of use across workstations

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INPUT SOURCES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Oxygen Forensics Export                                                   │
│  • Cellebrite UFED Export                                                    │
│  • MSAB XRY Export                                                           │
│  • Magnet Axiom Export                                                       │
│  • Manual Database + Media Folder Upload                                     │
│  • iTunes/iMazing Backup (iOS)                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROCESSING LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Database   │    │    Media     │    │     AI       │                   │
│  │   Parser     │    │  Processor   │    │  Analyzers   │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                   │                            │
│         ▼                   ▼                   ▼                            │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                    Analysis Engine                            │           │
│  │  • Text Analysis    • Image Captioning    • OCR               │           │
│  │  • Speech-to-Text   • PII Detection       • Password Detection│           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            STORAGE LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                         PostgreSQL Database                                  │
│  • Case metadata        • Extracted messages      • Analysis results         │
│  • Media references     • PII findings            • Audit logs               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                      Web Interface (Flask/FastAPI)                           │
│  • Dashboard           • Chat Viewer              • GPS Map View             │
│  • AI Analysis Results • Report Generator         • Case Management          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Backend** | Python 3.11+ | Rich forensic libraries, AI/ML ecosystem |
| **Web Framework** | FastAPI | Async support, modern, auto-documentation |
| **Frontend** | Bootstrap 5 + HTMX | Simple, responsive, minimal JS complexity |
| **Database** | PostgreSQL 15+ | Robust, JSON support, full-text search |
| **AI/ML Runtime** | Ollama (local) | Air-gapped operation, data sovereignty |
| **Task Queue** | Celery + Redis | Multi-threaded background processing |
| **Containerization** | Docker Compose | Easy deployment, reproducible environments |

---

## 4. Functional Requirements

### 4.1 Case Management

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| CM-01 | Create Case | HIGH | Create new forensic case with metadata |
| CM-02 | Case Details | HIGH | Case number, examiner, date, notes, evidence hash |
| CM-03 | Upload Evidence | HIGH | Upload database file + media folder |
| CM-04 | Hash Verification | HIGH | Auto-calculate SHA256/MD5 on upload |
| CM-05 | Multi-Case Support | MEDIUM | Work on multiple cases simultaneously |
| CM-06 | Case Export | MEDIUM | Export entire case with all artifacts |
| CM-07 | Chain of Custody | HIGH | Log all access and actions |

### 4.2 Database Parsing

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| DP-01 | iOS Support | HIGH | Parse `ChatStorage.sqlite` (iOS 14-18) |
| DP-02 | Android Support | HIGH | Parse `msgstore.db` (crypt12-15 if decrypted) |
| DP-03 | Schema Detection | HIGH | Auto-detect database version/schema |
| DP-04 | Message Extraction | HIGH | All messages with timestamps, sender, status |
| DP-05 | Deleted Messages | MEDIUM | Recover deleted messages from freelist |
| DP-06 | Media References | HIGH | Link messages to media files |
| DP-07 | Contact Mapping | HIGH | Map phone numbers to contact names |

### 4.3 Chat Analysis Features

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| CA-01 | Chat List | HIGH | List all conversations with preview |
| CA-02 | Private Chat View | HIGH | Full conversation with media inline |
| CA-03 | Group Chat View | HIGH | Group conversations with member info |
| CA-04 | GPS Locations | HIGH | Extract and map shared locations |
| CA-05 | Blocked Contacts | MEDIUM | List blocked phone numbers |
| CA-06 | Call Logs | MEDIUM | Voice/video call history |
| CA-07 | Status/Stories | LOW | Viewed statuses (if available) |
| CA-08 | Timeline View | HIGH | Chronological activity timeline |
| CA-09 | Search | HIGH | Full-text search across all messages |
| CA-10 | Filters | HIGH | Filter by date, contact, type, keywords |

### 4.4 Media Processing

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| MP-01 | Image Gallery | HIGH | Grid view of all images |
| MP-02 | Video Player | HIGH | In-browser video playback |
| MP-03 | Audio Player | HIGH | In-browser audio playback |
| MP-04 | Document Preview | MEDIUM | PDF, Office docs preview |
| MP-05 | Media Export | HIGH | Export selected media with metadata |
| MP-06 | Thumbnail Generation | HIGH | Auto-generate thumbnails |
| MP-07 | EXIF Extraction | HIGH | Extract GPS, camera info from images |

### 4.5 AI Analysis Module

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| AI-01 | Image Captioning | HIGH | AI description of image contents |
| AI-02 | Image OCR | HIGH | Extract text from images (screenshots, docs) |
| AI-03 | Speech-to-Text | HIGH | Transcribe voice messages |
| AI-04 | PII Detection | HIGH | Detect names, emails, phones, addresses |
| AI-05 | Password Detection | HIGH | Identify passwords, PINs, credentials |
| AI-06 | Crypto Wallet Detection | MEDIUM | Bitcoin, Ethereum wallet addresses |
| AI-07 | ID Document Detection | MEDIUM | Passports, IDs, credit cards in images |
| AI-08 | Sentiment Analysis | LOW | Emotional tone of conversations |
| AI-09 | Language Detection | MEDIUM | Auto-detect message language |
| AI-10 | Keyword Extraction | HIGH | Important terms, names, places |

### 4.6 Reporting

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| RP-01 | PDF Report | HIGH | Court-ready PDF with formatting |
| RP-02 | Excel Export | HIGH | Spreadsheet with all data |
| RP-03 | HTML Report | MEDIUM | Interactive HTML report |
| RP-04 | Selective Export | HIGH | Export specific chats/date ranges |
| RP-05 | Hash Verification | HIGH | Report includes verification hashes |
| RP-06 | Report Templates | MEDIUM | Customizable report templates |
| RP-07 | Arabic Support | HIGH | RTL layout, Arabic fonts in reports |
| RP-08 | Digital Signature | LOW | Optional digital signing of reports |

---

## 5. AI Analyzers Specification

### 5.1 Open-Source/Local Analyzers (Air-Gapped Compatible) ✅ PRIMARY

> **All local analyzers work offline without internet connection. This is the DEFAULT mode.**

```yaml
analyzers:
  speech_to_text:
    engine: "Whisper AI (OpenAI)"
    model: "whisper-large-v3"
    deployment: "Local via Docker"
    requires_internet: false
    supported_formats: [".opus", ".ogg", ".wav", ".m4a", ".mp3"]
    languages: ["ar", "en", "multi"]
    gpu_required: true  # Recommended for speed
    
  image_ocr:
    engine: "Tesseract OCR"
    version: "5.x"
    deployment: "Local"
    requires_internet: false
    languages: ["ara", "eng", "ara+eng"]
    preprocessing: "OpenCV (deskew, denoise)"
    gpu_required: false
    
  image_captioning:
    engine: "LLaVA / BLIP-2"
    deployment: "Local via Ollama"
    model: "llava:13b"
    requires_internet: false
    gpu_required: true
    
  pii_detection:
    primary: "Presidio (Microsoft)"
    deployment: "Local Docker"
    requires_internet: false
    custom_recognizers:
      - bitcoin_address
      - ethereum_address
      - bahrain_cpr  # National ID
      - arabic_names
      - iban_gcc
    secondary: "StarPII (BigCode NER)"
    
  password_detection:
    engine: "DeepPass (GhostPack)"
    deployment: "Local Docker container"
    requires_internet: false
    regex_patterns:
      - "password patterns"
      - "PIN patterns"
      - "API key patterns"
```

### 5.2 Cloud/API Analyzers (⚠️ OPTIONAL - Disabled by Default)

> **Cloud APIs are 100% OPTIONAL and DISABLED by default.**
> - Enable only for non-sensitive cases with explicit approval
> - Requires configuration in settings with API keys
> - All features work fully without cloud APIs

```yaml
cloud_analyzers:
  # DISABLED BY DEFAULT - Enable in Settings > Cloud APIs
  
  enabled: false  # Master switch - default OFF
  require_case_approval: true  # Must approve per-case
  
  openai:
    enabled: false
    model: "gpt-4o-mini"
    use_case: "Complex entity extraction (optional enhancement)"
    api_key_required: true
    data_warning: "Data sent to OpenAI servers"
    
  azure_cognitive:
    enabled: false
    services:
      - "PII Extraction"
      - "Speech-to-Text (Arabic enhanced)"
      - "OCR (Arabic handwriting)"
    api_key_required: true
    data_warning: "Data sent to Microsoft Azure"
    
  anthropic_claude:
    enabled: false
    model: "claude-sonnet-4-20250514"
    use_case: "Conversation summarization (optional)"
    api_key_required: true
    data_warning: "Data sent to Anthropic servers"

# Settings UI should show:
# ┌─────────────────────────────────────────────────────────┐
# │ ⚠️ CLOUD API SETTINGS                                   │
# │                                                         │
# │ [ ] Enable Cloud APIs (sends data to external servers) │
# │                                                         │
# │ WARNING: Enabling cloud APIs will send case data to    │
# │ third-party servers. Only enable for non-sensitive     │
# │ cases with proper authorization.                       │
# │                                                         │
# │ All features work fully in offline/local mode.         │
# └─────────────────────────────────────────────────────────┘
```

### 5.3 LLM Output Verification & Quality Assurance

> **Critical: AI outputs must be verified before being used as evidence.**

#### 5.3.1 Confidence Scoring System

```yaml
confidence_thresholds:
  high_confidence: 0.85      # Auto-accept, mark as verified
  medium_confidence: 0.60    # Flag for human review
  low_confidence: 0.40       # Require manual verification
  reject_threshold: 0.20     # Auto-reject, do not display

# Every AI output includes:
ai_result:
  value: "extracted text or entity"
  confidence: 0.87
  verification_status: "auto_verified" | "pending_review" | "human_verified" | "rejected"
  verification_method: "confidence_threshold" | "cross_validation" | "human_review"
  verified_by: null | "examiner_id"
  verified_at: null | "timestamp"
```

#### 5.3.2 Cross-Validation Between Analyzers

```yaml
cross_validation_rules:
  # OCR verification: Compare multiple engines
  ocr_validation:
    primary: "tesseract"
    secondary: "easyocr"  # Run both, compare results
    similarity_threshold: 0.90  # Levenshtein similarity
    action_on_mismatch: "flag_for_review"
    
  # PII verification: Multiple detectors must agree
  pii_validation:
    engines: ["presidio", "starpii", "regex"]
    minimum_agreement: 2  # At least 2 engines must detect
    action_on_single_detection: "lower_confidence"
    
  # Speech-to-text verification
  transcription_validation:
    # Re-transcribe sample segments
    sample_percentage: 10  # Re-process 10% of audio
    compare_with_original: true
    max_word_error_rate: 0.15  # Flag if WER > 15%
```

#### 5.3.3 Human Review Queue

```sql
-- Review queue table
CREATE TABLE ai_review_queue (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    ai_analysis_id INTEGER REFERENCES ai_analysis(id),
    
    -- What needs review
    content_type VARCHAR(50),  -- 'transcription', 'ocr', 'pii', 'caption'
    original_content TEXT,      -- Source (image path, audio path, text)
    ai_output TEXT,             -- What AI produced
    confidence DECIMAL(5,4),
    
    -- Review status
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'approved', 'corrected', 'rejected'
    priority INTEGER DEFAULT 5,  -- 1=urgent, 10=low
    
    -- Review result
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    corrected_value TEXT,       -- If examiner corrects the output
    review_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for quick queue retrieval
CREATE INDEX idx_review_queue_status ON ai_review_queue(case_id, status, priority);
```

#### 5.3.4 Ground Truth Validation (Calibration)

```yaml
ground_truth_validation:
  # Periodically test analyzers against known samples
  
  test_datasets:
    ocr_test:
      location: "/app/validation/ocr_samples/"
      samples: 50  # Images with known text
      run_frequency: "on_startup"
      minimum_accuracy: 0.95
      
    transcription_test:
      location: "/app/validation/audio_samples/"
      samples: 20  # Audio files with known transcripts
      run_frequency: "on_startup"
      minimum_accuracy: 0.90
      
    pii_test:
      location: "/app/validation/pii_samples/"
      samples: 100  # Text with known PII entities
      run_frequency: "on_startup"
      minimum_f1_score: 0.85

  # Actions on validation failure
  on_failure:
    - log_warning
    - send_admin_alert
    - mark_analyzer_degraded
    - increase_human_review_percentage
```

#### 5.3.5 Anomaly Detection

```python
# Detect unusual AI outputs that need review

anomaly_detection_rules:
  # Unusually high PII density
  - name: "high_pii_density"
    condition: "pii_count > 10 per message"
    action: "flag_for_review"
    reason: "Unusually high number of PII entities detected"
    
  # Very long transcriptions
  - name: "transcription_length_anomaly"
    condition: "transcription_length > audio_duration * 50"  # ~50 chars/sec max
    action: "flag_for_review"
    reason: "Transcription length exceeds expected ratio"
    
  # OCR gibberish detection
  - name: "ocr_gibberish"
    condition: "dictionary_word_ratio < 0.30"
    action: "flag_for_review"
    reason: "OCR output contains mostly non-dictionary words"
    
  # Confidence variance
  - name: "confidence_instability"
    condition: "confidence_stddev > 0.25 across similar inputs"
    action: "log_warning"
    reason: "Model showing inconsistent confidence levels"
```

#### 5.3.6 Verification UI Components

```yaml
ui_verification_features:
  # Side-by-side comparison
  ocr_verification_view:
    left_panel: "Original image"
    right_panel: "Extracted text (editable)"
    actions: ["Approve", "Edit & Approve", "Reject", "Skip"]
    
  # Audio player with transcript
  transcription_verification_view:
    audio_player: "Waveform with playback controls"
    transcript_panel: "Editable transcript with timestamps"
    sync_highlight: true  # Highlight text as audio plays
    actions: ["Approve", "Edit & Approve", "Reject", "Re-transcribe"]
    
  # PII highlight review
  pii_verification_view:
    text_display: "Original text with PII highlighted"
    entity_list: "Detected entities with confidence"
    actions_per_entity: ["Confirm", "Remove", "Change Type"]
    bulk_actions: ["Approve All High Confidence", "Review Low Confidence"]

  # Dashboard metrics
  verification_dashboard:
    - total_pending_reviews
    - reviews_by_confidence_level
    - average_review_time
    - correction_rate_by_analyzer
    - accuracy_trend_over_time
```

#### 5.3.7 Verification Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI ANALYSIS VERIFICATION FLOW                         │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │  AI Analyzer │
     │   Output     │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │  Confidence  │
     │   Scoring    │
     └──────┬───────┘
            │
     ┌──────┴──────┬────────────────┐
     ▼             ▼                ▼
┌─────────┐  ┌──────────┐    ┌───────────┐
│ ≥ 0.85  │  │ 0.60-0.84│    │  < 0.60   │
│  HIGH   │  │  MEDIUM  │    │   LOW     │
└────┬────┘  └────┬─────┘    └─────┬─────┘
     │            │                │
     ▼            ▼                ▼
┌─────────┐  ┌──────────┐    ┌───────────┐
│  Cross  │  │  Human   │    │  Require  │
│Validate │  │  Review  │    │  Manual   │
│ (auto)  │  │  Queue   │    │  Review   │
└────┬────┘  └────┬─────┘    └─────┬─────┘
     │            │                │
     ▼            ▼                ▼
┌─────────────────────────────────────────┐
│           Verified Results              │
│  (marked with verification method)      │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  Store in DB with full audit trail      │
│  - Original AI output                   │
│  - Confidence score                     │
│  - Verification method                  │
│  - Reviewer (if human)                  │
│  - Corrections (if any)                 │
│  - Timestamp                            │
└─────────────────────────────────────────┘
```

#### 5.3.8 Verification Reports

```yaml
verification_report_sections:
  - ai_accuracy_summary:
      description: "Overall accuracy metrics for each analyzer"
      metrics:
        - total_items_processed
        - auto_verified_count
        - human_reviewed_count
        - correction_rate
        - average_confidence
        
  - verification_audit_trail:
      description: "Complete log of all verifications"
      fields:
        - item_id
        - analyzer
        - original_output
        - verified_output
        - verification_method
        - reviewer
        - timestamp
        
  - confidence_distribution:
      description: "Distribution of confidence scores"
      visualization: "histogram"
      
  - correction_analysis:
      description: "Types of corrections made by reviewers"
      breakdown_by: ["analyzer", "content_type", "error_type"]
```

### 5.3 Custom Presidio Recognizers for Bahrain/GCC

```python
# Example recognizer configurations
recognizers:
  - name: "Bahrain CPR"
    pattern: r"\b\d{2}[01]\d[0-3]\d\d{5}\b"
    context: ["cpr", "civil", "id", "رقم", "هوية"]
    score: 0.85
    
  - name: "GCC Phone Numbers"
    pattern: r"\+?(973|966|971|968|965|974)\d{8}"
    context: ["phone", "mobile", "رقم", "جوال", "هاتف"]
    score: 0.90
    
  - name: "Arabic Names"
    type: "NER"
    model: "CAMeL-Lab/bert-base-arabic-camelbert-ca-ner"
    
  - name: "IBAN GCC"
    pattern: r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b"
    context: ["iban", "bank", "حساب", "بنك"]
    score: 0.95
```

---

## 6. Database Schema

### 6.1 Case Management Tables

```sql
-- Cases table
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(50) UNIQUE NOT NULL,
    examiner_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB
);

-- Evidence items
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id),
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_type VARCHAR(50),  -- 'database', 'media_folder'
    sha256_hash VARCHAR(64),
    md5_hash VARCHAR(32),
    file_size BIGINT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_info JSONB  -- Device UDID, name, iOS version, etc.
);

-- Audit log
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    user_id VARCHAR(100),
    action VARCHAR(100),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET
);
```

### 6.2 WhatsApp Data Tables

```sql
-- Chat sessions
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    original_pk INTEGER,  -- Z_PK from iOS / _id from Android
    contact_jid VARCHAR(50),  -- WhatsApp ID (phone@s.whatsapp.net)
    contact_name VARCHAR(100),
    is_group BOOLEAN DEFAULT FALSE,
    group_name VARCHAR(200),
    message_count INTEGER DEFAULT 0,
    last_message_time TIMESTAMP,
    archived BOOLEAN DEFAULT FALSE,
    pinned BOOLEAN DEFAULT FALSE
);

-- Messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    chat_session_id INTEGER REFERENCES chat_sessions(id),
    original_pk INTEGER,
    message_type INTEGER,  -- 0=text, 1=image, 2=audio, etc.
    sender_jid VARCHAR(50),
    sender_name VARCHAR(100),
    timestamp TIMESTAMP,
    text_content TEXT,
    media_path VARCHAR(500),
    media_caption TEXT,
    is_from_me BOOLEAN,
    is_deleted BOOLEAN DEFAULT FALSE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    quoted_message_id INTEGER,
    raw_data JSONB  -- Original row data for reference
);

-- Media items
CREATE TABLE media_items (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id),
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    mime_type VARCHAR(100),
    file_size BIGINT,
    sha256_hash VARCHAR(64),
    thumbnail_path VARCHAR(500),
    duration_seconds INTEGER,  -- For audio/video
    exif_data JSONB
);

-- AI Analysis results
CREATE TABLE ai_analysis (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    message_id INTEGER REFERENCES messages(id),
    media_id INTEGER REFERENCES media_items(id),
    analyzer_name VARCHAR(50),
    analysis_type VARCHAR(50),  -- 'ocr', 'caption', 'transcription', 'pii'
    result_text TEXT,
    result_data JSONB,
    confidence DECIMAL(5,4),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PII Findings
CREATE TABLE pii_findings (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    message_id INTEGER REFERENCES messages(id),
    ai_analysis_id INTEGER REFERENCES ai_analysis(id),
    entity_type VARCHAR(50),  -- 'EMAIL', 'PHONE', 'PASSWORD', 'BITCOIN', etc.
    entity_value TEXT,
    start_position INTEGER,
    end_position INTEGER,
    confidence DECIMAL(5,4),
    source_text TEXT,
    flagged BOOLEAN DEFAULT FALSE
);
```

---

## 7. API Endpoints

### 7.1 Case Management

```yaml
endpoints:
  # Cases
  POST   /api/cases                    # Create new case
  GET    /api/cases                    # List all cases
  GET    /api/cases/{case_id}          # Get case details
  PUT    /api/cases/{case_id}          # Update case
  DELETE /api/cases/{case_id}          # Delete case (soft delete)
  
  # Evidence Upload
  POST   /api/cases/{case_id}/evidence/upload    # Upload DB + media
  GET    /api/cases/{case_id}/evidence           # List evidence items
  GET    /api/cases/{case_id}/evidence/{id}/hash # Verify hash
```

### 7.2 Chat Analysis

```yaml
endpoints:
  # Chat Sessions
  GET    /api/cases/{case_id}/chats              # List all chats
  GET    /api/cases/{case_id}/chats/{chat_id}    # Get chat details
  GET    /api/cases/{case_id}/chats/{chat_id}/messages  # Get messages
  
  # Groups
  GET    /api/cases/{case_id}/groups             # List groups
  GET    /api/cases/{case_id}/groups/{id}/members  # Group members
  
  # Contacts
  GET    /api/cases/{case_id}/contacts           # All contacts
  GET    /api/cases/{case_id}/contacts/blocked   # Blocked contacts
  
  # Locations
  GET    /api/cases/{case_id}/locations          # All GPS locations
  
  # Search
  GET    /api/cases/{case_id}/search?q={query}   # Full-text search
  POST   /api/cases/{case_id}/search/advanced    # Advanced filters
```

### 7.3 AI Analysis

```yaml
endpoints:
  # Start Analysis
  POST   /api/cases/{case_id}/analyze                    # Start all analyzers
  POST   /api/cases/{case_id}/analyze/ocr               # Run OCR only
  POST   /api/cases/{case_id}/analyze/transcribe        # Transcribe audio
  POST   /api/cases/{case_id}/analyze/pii               # PII detection
  POST   /api/cases/{case_id}/analyze/captions          # Image captions
  
  # Analysis Status
  GET    /api/cases/{case_id}/analyze/status            # Job status
  GET    /api/cases/{case_id}/analyze/results           # All results
  GET    /api/cases/{case_id}/analyze/pii/findings      # PII findings
  GET    /api/cases/{case_id}/analyze/passwords         # Detected passwords
```

### 7.4 Reports

```yaml
endpoints:
  POST   /api/cases/{case_id}/reports/pdf               # Generate PDF
  POST   /api/cases/{case_id}/reports/excel             # Generate Excel
  POST   /api/cases/{case_id}/reports/html              # Generate HTML
  GET    /api/cases/{case_id}/reports                   # List reports
  GET    /api/cases/{case_id}/reports/{id}/download     # Download report
```

---

## 8. User Interface Screens

### 8.1 Dashboard
- Active cases overview
- Recent analysis jobs
- Quick stats (total messages, media, PII findings)
- System status (analyzers health)

### 8.2 Case View
- Case metadata display
- Evidence files with hash verification
- Database summary (tables, record counts)
- Quick actions (Analyze, Export)

### 8.3 Chat List
- Sortable table of all conversations
- Preview of last message
- Message count, date range
- Quick filter (Private/Group)

### 8.4 Chat Viewer
- WhatsApp-style chat bubble layout
- Inline media preview
- Message metadata on hover
- Jump to date functionality
- Export selected messages

### 8.5 AI Analysis Dashboard
- Analysis job queue
- Real-time progress
- Results summary by category
- PII findings with severity
- Password/credential alerts

### 8.6 GPS Map View
- Interactive map (Leaflet/OpenLayers)
- Location markers with timestamps
- Timeline slider
- Export to KML/GPX

### 8.7 Report Generator
- Template selection
- Date range filter
- Include/exclude options
- Preview before generate

---

## 9. Docker Deployment

### 9.1 Docker Compose Structure

```yaml
version: '3.8'

services:
  # Main Application
  app:
    build: ./app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://fwa:password@db:5432/forensic_wa
      - REDIS_URL=redis://redis:6379
      - OLLAMA_HOST=http://ollama:11434
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/media:/app/media
      - ./data/reports:/app/reports
    depends_on:
      - db
      - redis
      - ollama

  # PostgreSQL Database
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=fwa
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=forensic_wa
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis (Task Queue)
  redis:
    image: redis:7-alpine

  # Celery Worker
  celery_worker:
    build: ./app
    command: celery -A app.celery worker -l info -c 4
    environment:
      - DATABASE_URL=postgresql://fwa:password@db:5432/forensic_wa
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  # Ollama (Local LLM)
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Whisper API (Speech-to-Text)
  whisper:
    image: onerahmet/openai-whisper-asr-webservice:latest
    ports:
      - "9000:9000"
    environment:
      - ASR_MODEL=large-v3
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Tesseract OCR Service
  tesseract:
    build: ./services/tesseract
    ports:
      - "9001:8080"

  # Presidio Analyzer
  presidio_analyzer:
    image: mcr.microsoft.com/presidio-analyzer:latest
    ports:
      - "5001:5001"

  # DeepPass Password Detector
  deeppass:
    build: ./services/deeppass
    ports:
      - "5002:5000"

volumes:
  postgres_data:
  ollama_models:
```

---

## 10. Security Requirements

### 10.1 Access Control
- Role-based access (Admin, Examiner, Viewer)
- Session timeout (configurable)
- Login audit logging
- Optional 2FA support

### 10.2 Data Protection
- All data at rest encrypted
- HTTPS only (TLS 1.3)
- Database connection encryption
- Secure file storage with access controls

### 10.3 Forensic Integrity
- Read-only mode for evidence files
- Hash verification on every access
- Complete audit trail
- No modification of original data

### 10.4 Air-Gapped Operation
- Full offline capability
- Local AI models only
- No external API calls required
- USB deployment option

---

## 11. Performance Requirements

| Metric | Target |
|--------|--------|
| Database parsing (100K messages) | < 60 seconds |
| Chat list loading | < 2 seconds |
| Message search (100K records) | < 3 seconds |
| Image OCR (single image) | < 5 seconds |
| Audio transcription (1 min) | < 30 seconds |
| Full AI analysis (10K messages + 1K media) | < 30 minutes |
| Report generation (10K messages) | < 2 minutes |

---

## 12. Implementation Phases

### Phase 1: Core Functionality (4-6 weeks)
- [ ] Project setup (Docker, database, FastAPI)
- [ ] iOS database parser
- [ ] Basic chat viewer
- [ ] Case management
- [ ] Media gallery

### Phase 2: Android Support & Features (3-4 weeks)
- [ ] Android database parser
- [ ] GPS map view
- [ ] Search functionality
- [ ] Contact management
- [ ] Basic reporting (PDF/Excel)

### Phase 3: AI Integration (4-6 weeks)
- [ ] Whisper integration (speech-to-text)
- [ ] Tesseract OCR integration
- [ ] Presidio PII detection
- [ ] Custom recognizers (Arabic, GCC)
- [ ] AI analysis dashboard

### Phase 4: Advanced Features (3-4 weeks)
- [ ] LLaVA image captioning
- [ ] Password detection
- [ ] Advanced reporting templates
- [ ] Arabic language support
- [ ] Performance optimization

### Phase 5: Polish & Deployment (2-3 weeks)
- [ ] Security hardening
- [ ] Documentation
- [ ] User training materials
- [ ] Deployment scripts
- [ ] Testing & bug fixes

---

## 13. Hardware Requirements

### Minimum (Without GPU AI)
- CPU: 4 cores
- RAM: 16 GB
- Storage: 500 GB SSD
- GPU: Not required (CPU inference)

### Recommended (With GPU AI)
- CPU: 8+ cores (Intel i7/i9, AMD Ryzen 7/9)
- RAM: 32 GB
- Storage: 1 TB NVMe SSD
- GPU: NVIDIA RTX 4070 or better (16GB VRAM)

### For Your RTX 5080
- Optimal for all local AI models
- Can run Whisper large-v3 + LLaVA simultaneously
- Fast processing even for large datasets

---

## 14. Dependencies & Licenses

### Open Source Components

| Component | License | Usage |
|-----------|---------|-------|
| Python | PSF | Runtime |
| FastAPI | MIT | Web framework |
| PostgreSQL | PostgreSQL | Database |
| Whisper | MIT | Speech-to-text |
| Tesseract | Apache 2.0 | OCR |
| Presidio | MIT | PII detection |
| Ollama | MIT | Local LLM hosting |
| LLaVA | Apache 2.0 | Image captioning |
| Bootstrap | MIT | UI framework |

---

## 15. Sample Prompts for Development

### Prompt 1: Database Parser

```
Create a Python module for parsing iOS WhatsApp database (ChatStorage.sqlite).

Requirements:
1. Connect to SQLite database and read all tables
2. Extract chat sessions from ZWACHATSESSION table
3. Extract messages from ZWAMESSAGE table
4. Map media references from ZWAMEDIAITEM table
5. Handle iOS timestamp format (Core Data timestamp - seconds since 2001-01-01)
6. Support both iOS 14-18 schema variations
7. Return structured data as Pydantic models
8. Include hash verification of source database

Output structure:
- List of ChatSession objects with messages
- Each message includes: timestamp, sender, content, media_ref, is_deleted
- GPS coordinates when available
```

### Prompt 2: AI Analysis Pipeline

```
Create a Celery task pipeline for AI analysis of WhatsApp media.

Requirements:
1. Task queue with priority levels
2. Image processing pipeline:
   - Resize for analysis
   - Run OCR (Tesseract)
   - Run image captioning (LLaVA via Ollama)
   - Extract EXIF metadata
3. Audio processing pipeline:
   - Convert opus to wav (ffmpeg)
   - Transcribe with Whisper
   - Detect language
4. PII detection on all text:
   - Use Presidio with custom recognizers
   - Flag high-confidence findings
5. Store results in PostgreSQL
6. Real-time progress updates via WebSocket

Handle errors gracefully with retry logic.
```

### Prompt 3: Report Generator

```
Create a PDF report generator for WhatsApp forensic analysis.

Requirements:
1. Use ReportLab or WeasyPrint
2. Professional forensic report layout
3. Include:
   - Case information header
   - Evidence chain of custody
   - Database hash verification
   - Chat statistics summary
   - Selected conversations (with media thumbnails)
   - AI analysis findings (PII, passwords)
   - GPS location map (static image)
   - Examiner signature block
4. Support Arabic text (RTL) with proper fonts
5. Include page numbers and table of contents
6. Tamper-evident features (hash footer per page)
7. Export options: PDF, HTML, DOCX

Generate court-admissible format.
```

---

## 16. Next Steps

1. **Review this specification** and adjust priorities
2. **Choose initial scope** (iOS only vs iOS+Android)
3. **Set up development environment** (Docker, GPU)
4. **Start Phase 1 implementation**
5. **Weekly progress reviews**

---

## Appendix A: WhatsApp Database Reference

### iOS Tables (ChatStorage.sqlite)

| Table | Description |
|-------|-------------|
| ZWACHATSESSION | Chat conversations |
| ZWAMESSAGE | All messages |
| ZWAMEDIAITEM | Media file references |
| ZWAGROUPMEMBER | Group participants |
| ZWAGROUPINFO | Group metadata |
| ZWAPROFILEPUSHNAME | Contact display names |
| ZWABLOCKLISTITEM | Blocked contacts |

### Android Tables (msgstore.db)

| Table | Description |
|-------|-------------|
| chat | Chat conversations |
| messages | All messages |
| message_media | Media references |
| group_participants | Group members |
| jid | Contact JID mapping |

---

*Document Version: 1.0*
*Created: January 2026*
*For: Digital Forensics Laboratory*
