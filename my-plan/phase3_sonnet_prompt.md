# WhatsApp Forensic Analyzer - Phase 3 Build (AI Integration)

## Development Environment
- **Primary Environment**: GitHub Codespaces
- **Repository**: https://github.com/yusufbuali/whatsapp-forensic-analyzer
- **Port**: 80
- **Working Method**: All code changes made directly in Codespace
- **GPU for Local Deployment**: RTX 5080 (16GB VRAM)

## Common Commands
```bash
docker-compose up --build          # Start all services
docker-compose logs -f app         # View logs
docker-compose restart app         # Restart after changes
docker-compose exec db psql -U postgres -d forensic  # Access DB
```

## Context
Phases 1-2 completed:
- iOS + Android parsers
- Full-text search
- GPS map view
- Media gallery
- PDF/Excel reports
- All running in Docker

## Phase 3: AI Analysis Module

> **AI runs LOCAL by default (air-gapped compatible).**
> **Cloud APIs are OPTIONAL and disabled by default - enable only for non-sensitive environments.**
> **All AI outputs must be flagged as "AI-generated" with confidence scores and require human verification.**

### Hardware Available (Local Deployment)
- NVIDIA RTX 5080 GPU (16GB VRAM)
- Can run Whisper large-v3 + LLaVA 13B simultaneously

### 1. Docker Services to Add

```yaml
# Add to docker-compose.yml

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    # Pre-pull: ollama pull llava:13b

  whisper:
    build: ./services/whisper
    volumes:
      - ./uploads:/data
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  presidio:
    image: mcr.microsoft.com/presidio-analyzer:latest
    environment:
      - ANALYZER_CONF_FILE=/app/conf/analyzer_config.yaml
    volumes:
      - ./config/presidio:/app/conf
```

### 2. Speech-to-Text (Whisper)

Transcribe voice messages (.opus, .m4a, .ogg):

```python
# services/whisper/transcribe.py
import whisper
from pathlib import Path

model = whisper.load_model("large-v3", device="cuda")

def transcribe_audio(file_path: str, language: str = None) -> dict:
    """
    Returns:
        {
            "text": "full transcription",
            "segments": [{"start": 0.0, "end": 2.5, "text": "..."}],
            "language": "ar",
            "confidence": 0.92
        }
    """
    result = model.transcribe(
        file_path,
        language=language,  # None = auto-detect
        task="transcribe",
        word_timestamps=True
    )
    return {
        "text": result["text"],
        "segments": result["segments"],
        "language": result["language"],
        "confidence": calculate_confidence(result)
    }
```

API: `POST /api/cases/{id}/analyze/transcribe`

### 3. Image OCR (Tesseract)

Extract text from screenshots/documents:

```python
# app/services/ocr_service.py
import pytesseract
from PIL import Image
import cv2
import numpy as np

def preprocess_image(image_path: str) -> np.ndarray:
    """Deskew, denoise, enhance contrast"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray)
    # Adaptive threshold for better text extraction
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    return binary

def extract_text(image_path: str, languages: str = "eng+ara") -> dict:
    """
    Returns:
        {
            "text": "extracted text",
            "confidence": 0.87,
            "word_boxes": [{"text": "word", "bbox": [x,y,w,h], "conf": 0.9}]
        }
    """
    processed = preprocess_image(image_path)
    data = pytesseract.image_to_data(
        processed, 
        lang=languages,
        output_type=pytesseract.Output.DICT
    )
    # Calculate average confidence
    confidences = [c for c in data['conf'] if c > 0]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    
    return {
        "text": pytesseract.image_to_string(processed, lang=languages),
        "confidence": avg_conf / 100,
        "word_boxes": build_word_boxes(data)
    }
```

### 4. Image Captioning (LLaVA via Ollama)

Generate AI descriptions of images:

```python
# app/services/caption_service.py
import ollama
import base64

def caption_image(image_path: str) -> dict:
    """
    Returns:
        {
            "caption": "A screenshot of a WhatsApp conversation...",
            "confidence": 0.85,
            "objects_detected": ["phone", "text", "profile picture"]
        }
    """
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    response = ollama.chat(
        model="llava:13b",
        messages=[{
            "role": "user",
            "content": "Describe this image in detail for forensic analysis. "
                      "List any visible text, people, objects, locations, or "
                      "identifying information.",
            "images": [image_data]
        }]
    )
    
    return {
        "caption": response["message"]["content"],
        "confidence": 0.85,  # LLaVA doesn't provide confidence
        "model": "llava:13b"
    }
```

### 5. PII Detection (Presidio + Custom)

Detect sensitive information:

```python
# app/services/pii_service.py
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer

# Custom recognizers for GCC region
class BahrainCPRRecognizer(PatternRecognizer):
    """Bahrain Central Population Register (CPR) number"""
    def __init__(self):
        patterns = [Pattern("CPR", r"\b\d{2}[01]\d[0-3]\d\d{5}\b", 0.85)]
        super().__init__(
            supported_entity="BAHRAIN_CPR",
            patterns=patterns,
            supported_language="en"
        )

class GCCPhoneRecognizer(PatternRecognizer):
    """GCC phone numbers (+973, +966, +971, +968, +965, +974)"""
    def __init__(self):
        patterns = [
            Pattern("GCC_PHONE", r"\+?(973|966|971|968|965|974)\d{8}", 0.9)
        ]
        super().__init__(
            supported_entity="GCC_PHONE",
            patterns=patterns,
            supported_language="en"
        )

class CryptoWalletRecognizer(PatternRecognizer):
    """Bitcoin and Ethereum addresses"""
    def __init__(self):
        patterns = [
            Pattern("BTC", r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b", 0.9),
            Pattern("ETH", r"\b0x[a-fA-F0-9]{40}\b", 0.95),
        ]
        super().__init__(
            supported_entity="CRYPTO_WALLET",
            patterns=patterns,
            supported_language="en"
        )

def create_analyzer() -> AnalyzerEngine:
    analyzer = AnalyzerEngine()
    analyzer.registry.add_recognizer(BahrainCPRRecognizer())
    analyzer.registry.add_recognizer(GCCPhoneRecognizer())
    analyzer.registry.add_recognizer(CryptoWalletRecognizer())
    return analyzer

def detect_pii(text: str, language: str = "en") -> list:
    """
    Returns list of:
        {
            "entity_type": "PHONE_NUMBER",
            "text": "+97312345678",
            "start": 10,
            "end": 22,
            "confidence": 0.95
        }
    """
    analyzer = create_analyzer()
    results = analyzer.analyze(
        text=text,
        language=language,
        entities=[
            "PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", 
            "LOCATION", "CREDIT_CARD", "IBAN_CODE",
            "BAHRAIN_CPR", "GCC_PHONE", "CRYPTO_WALLET"
        ]
    )
    return [
        {
            "entity_type": r.entity_type,
            "text": text[r.start:r.end],
            "start": r.start,
            "end": r.end,
            "confidence": r.score
        }
        for r in results
    ]
```

### 6. AI Output Verification System

**Critical: All AI outputs must be verified before use as evidence.**

```python
# app/services/verification_service.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import easyocr  # Secondary OCR for cross-validation

class VerificationStatus(Enum):
    AUTO_VERIFIED = "auto_verified"
    PENDING_REVIEW = "pending_review"
    HUMAN_VERIFIED = "human_verified"
    REJECTED = "rejected"

@dataclass
class AIResult:
    value: str
    confidence: float
    verification_status: VerificationStatus
    verification_method: str
    verified_by: Optional[str] = None
    corrected_value: Optional[str] = None

# Confidence thresholds
HIGH_CONFIDENCE = 0.85    # Auto-verify with cross-validation
MEDIUM_CONFIDENCE = 0.60  # Queue for human review
LOW_CONFIDENCE = 0.40     # Require manual review
REJECT_THRESHOLD = 0.20   # Auto-reject

def verify_ocr_result(image_path: str, tesseract_result: dict) -> AIResult:
    """Cross-validate OCR using EasyOCR"""
    confidence = tesseract_result["confidence"]
    
    if confidence >= HIGH_CONFIDENCE:
        # Cross-validate with EasyOCR
        reader = easyocr.Reader(['en', 'ar'])
        easy_result = reader.readtext(image_path, detail=0)
        easy_text = " ".join(easy_result)
        
        similarity = calculate_similarity(tesseract_result["text"], easy_text)
        
        if similarity >= 0.90:
            return AIResult(
                value=tesseract_result["text"],
                confidence=confidence,
                verification_status=VerificationStatus.AUTO_VERIFIED,
                verification_method="cross_validation_easyocr"
            )
        else:
            # Mismatch - queue for review
            return AIResult(
                value=tesseract_result["text"],
                confidence=confidence,
                verification_status=VerificationStatus.PENDING_REVIEW,
                verification_method="cross_validation_mismatch"
            )
    
    elif confidence >= MEDIUM_CONFIDENCE:
        return AIResult(
            value=tesseract_result["text"],
            confidence=confidence,
            verification_status=VerificationStatus.PENDING_REVIEW,
            verification_method="confidence_threshold"
        )
    
    elif confidence >= LOW_CONFIDENCE:
        return AIResult(
            value=tesseract_result["text"],
            confidence=confidence,
            verification_status=VerificationStatus.PENDING_REVIEW,
            verification_method="low_confidence_manual"
        )
    
    else:
        return AIResult(
            value=tesseract_result["text"],
            confidence=confidence,
            verification_status=VerificationStatus.REJECTED,
            verification_method="below_threshold"
        )

def verify_pii_result(entities: list) -> list:
    """Require multiple detection methods to agree"""
    verified = []
    for entity in entities:
        if entity["confidence"] >= HIGH_CONFIDENCE:
            # High confidence from Presidio - verify with regex
            if regex_confirms(entity["text"], entity["entity_type"]):
                entity["verification_status"] = "auto_verified"
                entity["verification_method"] = "presidio_regex_agreement"
            else:
                entity["verification_status"] = "pending_review"
                entity["verification_method"] = "single_detector"
        else:
            entity["verification_status"] = "pending_review"
            entity["verification_method"] = "low_confidence"
        verified.append(entity)
    return verified
```

### 7. Human Review Queue

```sql
-- Add to schema
CREATE TABLE ai_review_queue (
    id SERIAL PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    ai_analysis_id INTEGER REFERENCES ai_analysis(id),
    content_type VARCHAR(50),  -- 'transcription', 'ocr', 'pii', 'caption'
    original_content TEXT,      -- Path to source file or original text
    ai_output TEXT,
    confidence DECIMAL(5,4),
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    corrected_value TEXT,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

API Endpoints:
```python
GET  /api/cases/{id}/review-queue              # List pending reviews
GET  /api/cases/{id}/review-queue/{rid}        # Get single item
POST /api/cases/{id}/review-queue/{rid}/approve
POST /api/cases/{id}/review-queue/{rid}/correct  # Body: {"corrected_value": "..."}
POST /api/cases/{id}/review-queue/{rid}/reject
GET  /api/cases/{id}/verification-stats        # Accuracy metrics
```

UI: Review interface with:
- Side-by-side comparison (image/audio vs AI output)
- Audio player with waveform for transcriptions
- Editable text field for corrections
- Approve/Reject buttons
- Batch operations for high-confidence items

### 8. Celery Tasks for AI Pipeline

```python
# app/tasks/ai_tasks.py
from celery import chain, group
from app.tasks.celery_app import celery

@celery.task(bind=True)
def analyze_evidence(self, evidence_id: int):
    """Main orchestrator - runs all analyzers"""
    # Get all media items
    media_items = get_media_for_evidence(evidence_id)
    messages = get_messages_for_evidence(evidence_id)
    
    # Group tasks by type
    audio_tasks = group([
        transcribe_audio.s(m.id, m.file_path) 
        for m in media_items if m.mime_type.startswith('audio/')
    ])
    
    image_tasks = group([
        process_image.s(m.id, m.file_path)
        for m in media_items if m.mime_type.startswith('image/')
    ])
    
    text_tasks = group([
        detect_pii.s(msg.id, msg.text_content)
        for msg in messages if msg.text_content
    ])
    
    # Execute in parallel
    workflow = group(audio_tasks, image_tasks, text_tasks)
    workflow.apply_async()

@celery.task
def transcribe_audio(message_id: int, file_path: str):
    result = whisper_transcribe(file_path)
    verified = verify_transcription(result)
    save_ai_analysis(message_id, "transcription", verified)
    if verified.verification_status == VerificationStatus.PENDING_REVIEW:
        create_review_queue_item(message_id, "transcription", verified)

@celery.task
def process_image(message_id: int, file_path: str):
    # Run OCR
    ocr_result = extract_text(file_path)
    ocr_verified = verify_ocr_result(file_path, ocr_result)
    save_ai_analysis(message_id, "ocr", ocr_verified)
    
    # Run image captioning
    caption_result = caption_image(file_path)
    save_ai_analysis(message_id, "caption", caption_result)
    
    # Queue for review if needed
    if ocr_verified.verification_status == VerificationStatus.PENDING_REVIEW:
        create_review_queue_item(message_id, "ocr", ocr_verified)
```

### 9. AI Analysis Dashboard UI

New page: `/cases/{id}/analysis`

Components:
- **Job Queue**: Running/pending/completed analysis jobs
- **Progress Bar**: Real-time progress via WebSocket
- **Results Summary**: 
  - Total items analyzed
  - By type (audio, images, text)
  - Verification status breakdown
- **PII Alerts**: Highlighted findings requiring attention
- **Review Queue**: Items pending human verification

## Dependencies to Add

```
# requirements.txt additions
openai-whisper==20231117
pytesseract==0.3.10
easyocr==1.7.1
presidio-analyzer==2.2.354
ollama==0.1.7
opencv-python-headless==4.9.0.80
```

## First Task

1. Add the new Docker services (ollama, whisper container)
2. Implement the Whisper transcription service
3. Implement the OCR service with preprocessing
4. Add the verification system with confidence thresholds
5. Create the review queue table and API endpoints
6. Build the review UI for human verification

Start with transcription since voice messages are common in WhatsApp.
