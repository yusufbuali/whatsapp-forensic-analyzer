# WhatsApp Forensic Analyzer

A comprehensive forensic analysis tool for WhatsApp chat databases with AI-powered verification, evidence integrity tracking, and chain of custody management.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-Proprietary-red)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Backup & Recovery](#backup--recovery)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Legal & Compliance](#legal--compliance)

---

## Features

### Core Capabilities

- **Multi-Platform Support**: Parse iOS and Android WhatsApp databases
- **Evidence Integrity**: SHA-256 hashing and verification at every step
- **Chain of Custody**: Complete audit trail for legal compliance
- **AI Verification**: Multi-layer AI analysis with confidence scoring
- **PII Detection**: Automatic detection of personal information (GCC/Bahrain-specific)
- **Audio Transcription**: Whisper-based voice message transcription
- **Media Analysis**: Extract and analyze images, videos, and documents
- **Timeline Visualization**: Interactive chat timeline with filtering
- **Report Generation**: Professional forensic reports with certifications

### Security Features

- **Role-Based Access Control (RBAC)**: Admin, Examiner, Viewer roles
- **JWT Authentication**: Secure token-based authentication
- **Audit Logging**: Every action logged with user, timestamp, and IP
- **Encrypted Storage**: Support for encrypted evidence files
- **Rate Limiting**: Protection against brute-force attacks

### AI/ML Features

- **Local-First AI**: Works offline (air-gapped environments)
- **Confidence Scoring**: All AI analyses include confidence metrics
- **Human Review Queue**: Flagging of low-confidence results
- **Cross-Validation**: Multiple models verify each other
- **Calibration Tracking**: Monitor AI model performance over time

---

## Architecture

```
whatsapp-forensic-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── parsers/      # WhatsApp parsers
│   │   └── utils/        # Utilities
│   ├── alembic/          # Database migrations
│   └── tests/            # Test suite
├── frontend/
│   ├── templates/        # Jinja2 HTML templates
│   └── static/           # CSS, JS, images
├── uploads/              # Evidence storage
│   ├── evidence/         # Original files (read-only)
│   └── working/          # Processing workspace
├── backups/              # Automated backups
├── logs/                 # Application logs
└── docs/                 # Documentation
```

### Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery
- **AI/ML**: Whisper, spaCy, Presidio
- **Frontend**: Bootstrap 5, Jinja2
- **Deployment**: Docker Compose

---

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Redis 7 or higher
- Docker & Docker Compose (recommended)
- 8GB RAM minimum (16GB recommended for AI models)

### Quick Start (Docker - Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/your-org/whatsapp-forensic-analyzer.git
cd whatsapp-forensic-analyzer
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration (see Configuration section)
nano .env
```

3. **Generate security keys**
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"
# Add these to your .env file
```

4. **Start the application**
```bash
docker-compose up -d
```

5. **Initialize the database**
```bash
docker-compose exec app alembic upgrade head
```

6. **Create first admin user**
```bash
docker-compose exec app python scripts/create_admin.py
```

7. **Access the application**
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

### Manual Installation (Development)

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download AI models**
```bash
python -m spacy download en_core_web_trf
```

4. **Set up database**
```bash
# Create PostgreSQL database
createdb forensic_wa

# Run migrations
alembic upgrade head
```

5. **Start services**
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Start FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Configuration

### Critical Configuration Standards

**See [CONFIG_MASTER.md](CONFIG_MASTER.md) for complete configuration reference.**

#### Key Settings

- **Port**: 8000 (standard, do not change)
- **Database Name**: `forensic_wa` (standard, do not change)
- **Authentication**: JWT with 8-hour expiry
- **File Storage**: `uploads/evidence/{case_id}/`
- **Backups**: Daily at 2:00 AM, 30-day retention

### Environment Variables

Copy `.env.example` to `.env` and configure:

**Required Settings**:
```env
SECRET_KEY=<64-char-random-string>
JWT_SECRET_KEY=<64-char-random-string>
DATABASE_URL=postgresql://forensic_user:password@localhost:5432/forensic_wa
ADMIN_PASSWORD=<secure-password>
```

**Optional Settings**:
```env
USE_CLOUD_AI=False          # Enable OpenAI integration
OPENAI_API_KEY=sk-...       # If using cloud AI
WHISPER_DEVICE=cpu          # Change to 'cuda' for GPU
```

---

## Usage

### 1. Creating a Case

```bash
curl -X POST "http://localhost:8000/api/cases" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "case_number": "2026-001",
    "case_name": "Investigation Alpha",
    "examiner_name": "John Doe",
    "device_type": "iOS"
  }'
```

### 2. Uploading Evidence

```bash
curl -X POST "http://localhost:8000/api/cases/{case_id}/upload" \
  -H "Authorization: Bearer <your-token>" \
  -F "database=@ChatStorage.sqlite" \
  -F "media_folder=@media.zip"
```

### 3. Processing Evidence

The system automatically:
- Verifies file integrity (SHA-256)
- Parses WhatsApp database
- Extracts messages, media, contacts
- Runs AI analysis (async via Celery)
- Flags items for human review if needed

### 4. Viewing Results

Access the web UI at http://localhost:8000:
- Dashboard with case overview
- Chat timeline viewer
- Contact list
- Media gallery
- PII findings
- AI verification queue

### 5. Generating Reports

```bash
curl -X POST "http://localhost:8000/api/cases/{case_id}/reports" \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "full",
    "include_chain_of_custody": true,
    "include_media": false
  }'
```

---

## API Documentation

### Authentication

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "examiner1",
  "password": "secure-password"
}

Response:
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "expires_in": 28800
}
```

### Core Endpoints

- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/logout` - Logout user
- `GET /api/users/me` - Get current user info
- `POST /api/cases` - Create new case
- `GET /api/cases` - List all cases
- `GET /api/cases/{id}` - Get case details
- `POST /api/cases/{id}/upload` - Upload evidence
- `GET /api/cases/{id}/messages` - Get messages
- `GET /api/cases/{id}/contacts` - Get contacts
- `POST /api/cases/{id}/reports` - Generate report
- `GET /api/review-queue` - Get AI review queue

**Full API documentation available at**: http://localhost:8000/docs

---

## Security

### Authentication & Authorization

- **JWT Tokens**: Expire after 8 hours
- **Role-Based Access**:
  - `admin`: Full system access
  - `examiner`: Create/analyze cases
  - `viewer`: Read-only access
- **Password Requirements**: 8+ chars, uppercase, lowercase, digit, special
- **Rate Limiting**: 5 login attempts per 15 minutes

### Evidence Integrity

1. **Upload**: SHA-256 hash computed and stored
2. **Verification**: Hash re-verified before processing
3. **Immutability**: Original files are read-only
4. **Chain of Custody**: Every access logged

### Audit Trail

Every action is logged with:
- User ID and username
- Action performed
- Timestamp (UTC)
- IP address
- Case/evidence ID
- Status (success/failure)

View audit logs: `GET /api/audit-log?case_id={id}`

---

## Backup & Recovery

### Automated Backups

**Database**:
- Schedule: Daily at 2:00 AM
- Command: `pg_dump --format=custom forensic_wa > backup.dump`
- Retention: 30 days
- Location: `./backups/database/`

**Evidence Files**:
- Trigger: After each upload
- Method: rsync to secondary storage
- Verification: SHA-256 checksum comparison
- Location: `./backups/evidence/`

### Manual Backup

```bash
# Database
docker-compose exec postgres pg_dump -U forensic_user -Fc forensic_wa > backup_$(date +%Y%m%d).dump

# Evidence
rsync -avz ./uploads/evidence/ /backup/location/evidence/
```

### Recovery

```bash
# Restore database
docker-compose exec -T postgres pg_restore -U forensic_user -d forensic_wa < backup.dump

# Restore evidence
rsync -avz /backup/location/evidence/ ./uploads/evidence/
```

**Test your backups monthly!**

---

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific module
pytest tests/unit/parsers/

# Integration tests
pytest tests/integration/
```

### Test Structure

```
tests/
├── unit/
│   ├── parsers/
│   │   ├── test_ios_parser.py
│   │   └── test_android_parser.py
│   ├── services/
│   │   ├── test_auth_service.py
│   │   └── test_case_service.py
│   └── api/
│       └── test_endpoints.py
├── integration/
│   └── test_full_workflow.py
└── fixtures/
    ├── sample_ios.sqlite
    └── sample_android.db
```

### Coverage Target

- **Overall**: 80%
- **Critical Modules** (parsers, auth, integrity): 90%
- **API Endpoints**: 85%

---

## Deployment

### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Docker Compose)

1. **Update production config**
```bash
cp docker-compose.yml docker-compose.prod.yml
# Edit docker-compose.prod.yml:
# - Remove port 5432 exposure
# - Add nginx reverse proxy
# - Use Docker secrets for sensitive data
```

2. **Deploy**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Enable HTTPS** (nginx config)
```nginx
server {
    listen 443 ssl http2;
    server_name forensics.example.com;

    ssl_certificate /etc/ssl/certs/forensics.crt;
    ssl_certificate_key /etc/ssl/private/forensics.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Health Checks

- **Endpoint**: `GET /health`
- **Expected**: `{"status": "healthy", "database": "connected", "redis": "connected"}`
- **Monitoring**: Prometheus metrics at `/metrics`

---

## Contributing

This is a proprietary forensic tool. Contact the development team for contribution guidelines.

---

## Legal & Compliance

### Forensic Standards

- **Evidence Handling**: Follows NIST SP 800-86 guidelines
- **Hash Algorithm**: SHA-256 for integrity verification
- **Chain of Custody**: Complete audit trail maintained
- **Report Certification**: Examiner signature and lab accreditation

### Data Retention

- **Cases**: Indefinite (manual deletion by admin only)
- **Audit Logs**: 5 years minimum
- **Backups**: 30 days

### Certifications

Reports include:
- Examiner certification statement
- Tool validation and methodology
- Lab accreditation information
- Chain of custody documentation

### Legal Disclaimer

This tool is for authorized forensic investigation only. Unauthorized access to devices or data may be illegal in your jurisdiction.

---

## Support

- **Documentation**: [docs/](docs/)
- **Issue Tracker**: [GitHub Issues](https://github.com/your-org/whatsapp-forensic-analyzer/issues)
- **Contact**: forensics-support@example.com

---

## License

Proprietary - All Rights Reserved

Copyright (c) 2026 Forensic Analysis Laboratory

---

## Acknowledgments

- WhatsApp encryption research: Open Whisper Systems
- AI Models: OpenAI (Whisper), Explosion AI (spaCy)
- PII Detection: Microsoft (Presidio)

---

**Version**: 1.0.0
**Last Updated**: 2026-01-21
**Status**: Development
