WhatsApp Forensic Analyzer — Claude Code Instructions (Updated)

PURPOSE OF THIS FILE
This file defines strict development rules for Claude Code when working on the WhatsApp Forensic Analyzer project.
Claude must follow these instructions exactly when generating, modifying, or testing code.

LAST UPDATED: 2026-01-21
Changes: Aligned with actual implementation while preserving forensic requirements


PROJECT OVERVIEW
WhatsApp Forensic Analyzer is a digital forensic application designed for air-gapped and sensitive environments.

Key priorities:
- Evidence integrity
- Auditability
- Offline operation
- Deterministic, explainable AI


DEVELOPMENT ENVIRONMENTS (SUPPORTED)

1) GitHub Codespaces (Primary for collaboration)
- Repository:
  https://github.com/yusufbuali/whatsapp-forensic-analyzer
- All changes must be compatible with Codespaces
- Containers are managed via Docker Compose
- Web access uses port 80 (externally) mapped to port 8000 (internally)

2) Local Docker (Primary for air-gapped deployment)
- Same docker-compose.yml
- No cloud dependencies required
- Web access uses port 8000 (externally and internally)

Claude must ensure changes work in BOTH environments.


NETWORK & PORT REQUIREMENTS (CRITICAL)

Internal Application Port
- FastAPI runs on port 8000 internally
- Do NOT change FastAPI's internal port unless explicitly instructed

External / Published Port

Codespaces:
- Publish port 80 -> container port 8000
- Reason: corporate firewall blocks non-standard ports
- Configure via: EXTERNAL_PORT=80 in .env.codespaces

Local Docker:
- Publish port 8000 -> container port 8000
- Configure via: EXTERNAL_PORT=8000 in .env.local

Claude must never hardcode hostnames or ports in application logic.

Docker Compose Rule

Environment-based port mapping:
ports:
  - "${EXTERNAL_PORT:-8000}:8000"

Default is 8000, override with EXTERNAL_PORT environment variable.


TECH STACK (FIXED — DO NOT CHANGE)

Backend:
- Python 3.11 + FastAPI

Database:
- PostgreSQL 15
- Database name: forensic_wa (STANDARD - DO NOT CHANGE)

Frontend:
- Bootstrap 5
- HTMX
- Server-rendered (Jinja2)
- Minimal JavaScript

Task Queue:
- Celery + Redis

AI:
- Primary: Local models (offline, air-gapped)
  - Whisper (audio transcription)
  - spaCy (NER/PII detection)
  - Ollama (LLM tasks - optional, Phase 3)
- Optional: Cloud/API (must be explicitly configurable)
  - OpenAI (disabled by default)

Deployment:
- Docker Compose only


PROJECT STRUCTURE (DO NOT BREAK)

whatsapp-forensic-analyzer/
├── backend/              ← Backend code in subfolder
│   ├── app/
│   │   ├── main.py
│   │   ├── core/         ← config, security, database
│   │   ├── models/       ← SQLAlchemy models
│   │   ├── schemas/      ← Pydantic schemas
│   │   ├── api/          ← API endpoints (not "routers")
│   │   ├── services/     ← Business logic
│   │   ├── parsers/      ← WhatsApp parsers
│   │   ├── middleware/   ← Audit logging, etc.
│   │   └── utils/
│   ├── alembic/          ← Database migrations
│   └── tests/            ← Unit and integration tests
├── frontend/
│   ├── static/           ← CSS, JS, images
│   └── templates/        ← Jinja2 templates
├── scripts/              ← Utility scripts
├── uploads/              ← Evidence storage
├── logs/                 ← Application logs
├── backups/              ← Backup storage
├── docs/                 ← Documentation
└── docker-compose.yml

Claude must respect this structure.


AIR-GAPPED OPERATION (MANDATORY)

Claude must ensure:
- The system runs 100% offline
- No mandatory external API calls
- AI features function using local models only
- Cloud AI is optional and disabled by default

Any cloud integration must be:
- Feature-flagged
- Disabled by default
- Clearly documented


EVIDENCE HANDLING RULES (NON-NEGOTIABLE)

Claude must enforce:
1. Never modify original evidence
2. Compute and store SHA256 AND MD5 hashes (both required for legacy tool compatibility)
3. Create verified working copies
4. Validate hashes before every operation
5. Maintain chain of custody

Any feature that touches evidence must log actions.


AUDIT & LOGGING REQUIREMENTS

- Append-only audit logs
- Track:
  - User
  - Action
  - Timestamp
  - Target object (case, evidence, report)
  - IP address
  - Status (success/failure)
- Logs must be immutable at application level
- Retention: 5 years minimum (legal requirement)

Claude must never introduce destructive log operations.


AI OUTPUT GOVERNANCE

All AI features must:
- Clearly label output as "AI-generated"
- Provide confidence score (if available)
- Require human verification for low-confidence results
- Never overwrite examiner conclusions
- Support review queue for flagged items

Claude must not present AI results as facts.


HARDWARE ASSUMPTIONS

- GPU available: RTX 5080
- CUDA-capable local inference
- GPU acceleration is optional but assumed available
- CPU fallback must be supported


CODING STANDARDS (STRICT)

Claude must:
- Use Python type hints everywhere
- Write Google-style docstrings
- Follow existing architectural patterns
- Use SQLAlchemy for all database access
- Follow RESTful API conventions
- Add unit tests for critical logic
- Use Pydantic for validation
- Use FastAPI dependency injection

No shortcuts. No mock-only implementations.


DATABASE STANDARDS

- Database name: forensic_wa (STANDARD - DO NOT CHANGE)
- User: forensic_user
- Port: 5432 (internal)
- All queries via SQLAlchemy ORM
- Migrations via Alembic
- Proper indexes on all foreign keys
- Audit logging for all data access


APPROVED WORKFLOW FOR CLAUDE CODE

When making changes, Claude must:
1. Modify files directly in the repository
2. Show full file contents for any changed file
3. Assume Docker Compose is the runtime
4. Provide required commands after changes
5. Indicate whether a restart is required
6. Update tests when changing logic


COMMON COMMANDS (REFERENCE)

# Start services
docker-compose up --build

# View logs
docker-compose logs -f app

# Restart app
docker-compose restart app

# Database access
docker-compose exec postgres psql -U forensic_user -d forensic_wa

# Run tests
docker-compose exec app pytest

# Run migrations
docker-compose exec app alembic upgrade head

# Create admin user
docker-compose exec app python scripts/create_admin.py

# Check status
docker-compose ps


IMPORTANT CONSTRAINTS FOR CLAUDE

- Do NOT invent infrastructure
- Do NOT assume internet access
- Do NOT introduce SaaS dependencies
- Do NOT bypass forensic controls
- Do NOT simplify security requirements
- Do NOT change standard ports (8000 internal, configurable external)
- Do NOT change database name (forensic_wa)
- Do NOT skip audit logging

If unsure, ask before changing behavior.


SECURITY REQUIREMENTS

- Passwords hashed with bcrypt (cost 12)
- JWT tokens (8-hour expiry)
- Refresh tokens (30-day expiry)
- Rate limiting (5 attempts per 15 minutes)
- Account locking after 5 failed attempts
- Role-based access control (admin, examiner, viewer)
- All sensitive actions require authentication
- Audit logging for all actions
- HTTPS in production (nginx reverse proxy)
- CORS restricted to same domain
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)


TESTING REQUIREMENTS

- pytest framework
- 80% code coverage target
- 90% coverage for critical modules (auth, parsers, integrity)
- Unit tests for all services
- Integration tests for API endpoints
- Test fixtures for sample data
- Automated testing in CI/CD


DOCUMENTATION REQUIREMENTS

- README.md with setup instructions
- QUICKSTART.md for 5-minute setup
- API documentation via FastAPI/Swagger
- Code comments for complex logic
- Docstrings for all functions
- Configuration documented in CONFIG_MASTER.md


End of Claude Instructions
