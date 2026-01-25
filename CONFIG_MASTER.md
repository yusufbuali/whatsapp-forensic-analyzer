# WhatsApp Forensic Analyzer - Master Configuration

## Version: 1.0.0
## Last Updated: 2026-01-21

---

## Critical Configuration Standards

This document resolves all configuration conflicts and establishes the single source of truth for the project.

### 1. Port Configuration ✅

**STANDARD PORT: 8000**

- **Development**: Port 8000 (FastAPI default)
- **Production**: Port 8000 behind nginx reverse proxy on port 80/443
- **Docker Internal**: Port 8000

**Rationale**: FastAPI default, easier development, industry standard for Python web frameworks.

---

### 2. Database Configuration ✅

**STANDARD DATABASE NAME: forensic_wa**

- **Database**: PostgreSQL 15+
- **Name**: `forensic_wa` (forensic WhatsApp - descriptive)
- **Port**: 5432 (internal Docker network)
- **User**: `forensic_user`
- **Connection Pool**: 5-20 connections

**Rationale**: More descriptive than just "forensic", indicates WhatsApp focus.

---

### 3. Application Configuration

```yaml
Application:
  Name: WhatsApp Forensic Analyzer
  Version: 1.0.0
  Environment: development | staging | production

API:
  Host: 0.0.0.0
  Port: 8000
  Base Path: /api
  Docs Path: /docs

Database:
  Name: forensic_wa
  Host: postgres (Docker) | localhost (local dev)
  Port: 5432
  Pool Size: 10
  Max Overflow: 20

Redis:
  Host: redis
  Port: 6379
  DB: 0

Celery:
  Broker: redis://redis:6379/0
  Backend: redis://redis:6379/1
```

---

### 4. Authentication Configuration ✅

**AUTHENTICATION METHOD: JWT + Session-based**

- **JWT Secret**: Environment variable `JWT_SECRET_KEY`
- **Token Expiry**: 8 hours
- **Refresh Token**: 30 days
- **Password Hash**: bcrypt (cost factor 12)
- **Session Timeout**: 8 hours

**Roles**:
- `admin` - Full system access
- `examiner` - Create/analyze cases
- `viewer` - Read-only access

---

### 5. File Storage Configuration ✅

**Storage Structure**:
```
uploads/
  evidence/
    {case_id}/
      database/
        ChatStorage.sqlite
        ChatStorage.sqlite.sha256
        msgstore.db
        msgstore.db.sha256
      media/
        images/
        audio/
        video/
        documents/
  working/
    {case_id}/
      extracted/
      thumbnails/
      reports/
```

**File Limits**:
- Max upload size: 2GB per file
- Allowed extensions: .sqlite, .db, .crypt14, .jpg, .png, .mp4, .mp3, .pdf

---

### 6. Docker Configuration ✅

**Services**:
- `app` - FastAPI application (port 8000)
- `postgres` - PostgreSQL 15 (port 5432)
- `redis` - Redis 7 (port 6379)
- `celery_worker` - Async task processor
- `whisper` - Audio transcription (optional GPU)
- `spacy` - NER/PII detection

**Networks**:
- `forensic_network` - Internal bridge network

**Volumes**:
- `postgres_data` - Database persistence
- `redis_data` - Cache persistence
- `./uploads` - Evidence storage (bind mount)

---

### 7. AI Model Configuration ✅

**Local Models** (Air-gapped priority):
- Whisper: `base` model (CPU) or `small` (GPU)
- spaCy: `en_core_web_trf` (transformer model)
- Device: CPU fallback if GPU unavailable

**Optional Cloud**:
- OpenAI API (GPT-4) - disabled by default
- Requires explicit user consent per case

---

### 8. Backup Configuration ✅

**Database Backups**:
- Schedule: Daily at 2:00 AM
- Tool: `pg_dump --format=custom`
- Retention: 30 days
- Location: `backups/database/`

**Evidence Backups**:
- Schedule: After each case upload
- Method: rsync to secondary storage
- Verification: SHA-256 checksum comparison
- Location: `backups/evidence/`

**Recovery**:
- Point-in-time recovery enabled (PostgreSQL WAL)
- Recovery testing: Monthly

---

### 9. Security Configuration ✅

**HTTPS/TLS**:
- Development: HTTP on 8000
- Production: HTTPS on 443 (nginx terminates SSL)
- Certificate: Let's Encrypt or internal CA

**Secrets Management**:
- Development: `.env` file (not committed)
- Production: Docker secrets or HashiCorp Vault

**CORS**:
- Allowed Origins: Same domain only
- Credentials: True

**Rate Limiting**:
- Login attempts: 5 per 15 minutes
- API requests: 100 per minute per user

---

### 10. Logging Configuration ✅

**Log Levels**:
- Development: DEBUG
- Staging: INFO
- Production: WARNING

**Audit Log**:
- All user actions logged to `audit_log` table
- Retention: 5 years (legal requirement)
- Format: JSON with timestamp, user, action, IP, details

**Application Log**:
- Format: JSON structured logging
- Rotation: Daily, 30 days retention
- Location: `logs/app.log`

---

### 11. Testing Configuration ✅

**Framework**: pytest + pytest-asyncio

**Coverage Target**: 80% for core modules

**Test Structure**:
```
tests/
  unit/
    parsers/
    services/
    api/
  integration/
    test_full_workflow.py
  fixtures/
    sample_ios.sqlite
    sample_android.db
```

**CI/CD**: GitHub Actions (optional)

---

### 12. Deployment Configuration ✅

**Development**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production** (Docker Compose):
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Health Checks**:
- Endpoint: `/health`
- Interval: 30 seconds
- Timeout: 10 seconds

**Monitoring**:
- Prometheus metrics: `/metrics`
- Grafana dashboard (optional)

---

### 13. Environment Variables ✅

**Required**:
```env
# Application
ENVIRONMENT=development
SECRET_KEY=<random-64-char-string>
JWT_SECRET_KEY=<random-64-char-string>

# Database
DATABASE_URL=postgresql://forensic_user:password@postgres:5432/forensic_wa

# Redis
REDIS_URL=redis://redis:6379/0

# Admin User (first run)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<secure-password>
ADMIN_EMAIL=admin@example.com

# Optional: Cloud AI
OPENAI_API_KEY=<if-using-cloud-models>
```

---

### 14. Legal/Forensic Configuration ✅

**Chain of Custody**:
- Every evidence file hashed on upload
- Hash stored in `evidence_files` table
- Re-verified before processing

**Report Certification**:
- Examiner name and ID on all reports
- Digital signature support (optional)
- Lab accreditation info (configurable)

**Data Retention**:
- Cases: Indefinite (until manual deletion by admin)
- Audit logs: 5 years minimum
- Backups: 30 days

---

## Migration Checklist

When migrating from old configuration:

- [ ] Update all references from port 80 → 8000
- [ ] Update database name from `forensic` → `forensic_wa`
- [ ] Add authentication tables to schema
- [ ] Configure backup scripts
- [ ] Set up Alembic migrations
- [ ] Create production nginx config
- [ ] Generate secure secrets
- [ ] Test backup/recovery procedures

---

## Version History

- **1.0.0** (2026-01-21): Initial master configuration
  - Resolved port conflict (standardized to 8000)
  - Resolved database name conflict (standardized to forensic_wa)
  - Added authentication configuration
  - Added backup strategy
  - Added production deployment guidelines

---

## References

- FastAPI Docs: https://fastapi.tiangolo.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Docker Compose: https://docs.docker.com/compose/
- Alembic: https://alembic.sqlalchemy.org/
