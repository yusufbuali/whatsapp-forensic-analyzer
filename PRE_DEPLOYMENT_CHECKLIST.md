# Pre-Deployment Checklist

**Complete this checklist before pushing to GitHub and creating Codespace**

---

## ✅ Code Status

- [x] All Phase 0 code implemented (authentication system)
- [x] All gemini-comments fixed
- [x] claude.md updated with actual implementation
- [x] Docker security fixes applied (non-root users)
- [x] Redis-based rate limiter implemented
- [x] MD5 + SHA256 hashing implemented
- [x] Logout endpoint fixed
- [x] Environment-based port configuration

**Status**: ✅ **ALL COMPLETE**

---

## ✅ Files to Verify

Before pushing to GitHub, verify these critical files exist:

### Configuration Files
- [x] `.env.example` - Template with all variables
- [x] `.env.codespaces` - Codespaces-specific config (port 80)
- [x] `.env.local` - Local development config (port 8000)
- [ ] `.gitignore` - Verify .env is excluded

### Docker Files
- [x] `docker-compose.yml` - Multi-service orchestration
- [x] `Dockerfile` - Main app (non-root user "forensic")
- [x] `Dockerfile.whisper` - Audio transcription service
- [x] `Dockerfile.spacy` - NER/PII detection service

### Database Files
- [x] `backend/app/models/database_schema.sql` - Complete schema
- [x] `backend/alembic/` - Migration framework
- [x] `alembic.ini` - Alembic config (password fixed)

### Application Files
- [x] `backend/app/main.py` - FastAPI application
- [x] `backend/app/api/auth.py` - 12 authentication endpoints
- [x] `backend/app/core/security.py` - Security utilities
- [x] `backend/app/core/rate_limiter.py` - Redis rate limiter
- [x] `backend/app/middleware/audit.py` - Forensic logging

### Documentation Files
- [x] `README.md` - Project overview
- [x] `QUICKSTART.md` - 5-minute setup guide
- [x] `CODESPACES_DEPLOYMENT.md` - Complete Codespaces guide
- [x] `READY_TO_DEPLOY.md` - Deployment summary
- [x] `CONFIG_MASTER.md` - Configuration reference
- [x] `TESTING_CHECKLIST.md` - 50+ test cases
- [x] `claude.md` - Updated implementation documentation

### Scripts
- [x] `scripts/create_admin.py` - Admin user creation
- [x] `scripts/test_auth.py` - Automated testing
- [x] `deploy.sh` - Linux/Mac deployment script
- [x] `deploy.bat` - Windows deployment script

---

## 📋 Git Repository Checklist

### Step 1: Initialize Git (if not done)

```bash
# Check if git is initialized
git status

# If not initialized:
git init
git branch -M main
```

### Step 2: Verify .gitignore

**CRITICAL**: Ensure `.env` file is NOT committed!

```bash
# Check .gitignore contains:
cat .gitignore | grep -E "^\.env$"

# Should see: .env
```

If missing, add to `.gitignore`:
```
.env
.env.local
.env.production
```

### Step 3: Add All Files

```bash
# Stage all files
git add .

# Verify what will be committed
git status

# ⚠️  VERIFY: .env should NOT appear in the list!
```

### Step 4: Create Initial Commit

```bash
git commit -m "Phase 0 Complete - Authentication System

Features:
- Complete authentication system with JWT tokens
- Role-based access control (admin, examiner, viewer)
- Redis-based rate limiting (production-ready)
- Forensic audit logging (5-year retention)
- SHA256 + MD5 evidence hashing
- Non-root Docker containers
- Environment-based configuration

Security Fixes:
- Fixed hardcoded password in alembic.ini
- Docker containers now run as non-root users
- Replaced in-memory rate limiter with Redis
- Fixed logout endpoint to properly revoke tokens

Documentation:
- Complete Codespaces deployment guide
- 50+ test cases checklist
- Configuration master reference

Ready for: GitHub Codespaces deployment and testing"
```

### Step 5: Create GitHub Repository

**Option A: Via GitHub Web Interface**
1. Go to https://github.com/new
2. Repository name: `whatsapp-forensic-analyzer`
3. **Visibility**: ⚠️  **PRIVATE** (forensic tool - must be private!)
4. ❌ Do NOT initialize with README (we have one)
5. Click "Create repository"

**Option B: Via GitHub CLI**
```bash
gh repo create whatsapp-forensic-analyzer --private --source=. --remote=origin
```

### Step 6: Push to GitHub

```bash
# Add remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/whatsapp-forensic-analyzer.git

# Or if using SSH:
# git remote add origin git@github.com:USERNAME/whatsapp-forensic-analyzer.git

# Push code
git push -u origin main
```

---

## 🚀 GitHub Codespaces Setup

### Step 1: Create Codespace

1. Go to your repository: `https://github.com/USERNAME/whatsapp-forensic-analyzer`
2. Click green **"Code"** button
3. Click **"Codespaces"** tab
4. Click **"Create codespace on main"**
5. Wait 2-3 minutes for initialization

### Step 2: Verify Codespace Environment

In the Codespace terminal:

```bash
# Check Docker is available
docker --version
docker-compose --version

# Check Python is available
python --version
python3 --version

# Verify project files
ls -la
```

### Step 3: Run Deployment Script

**Option A: Automated (Recommended)**
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

**Option B: Manual (Step-by-step)**

Follow the manual steps in `CODESPACES_DEPLOYMENT.md`

---

## 🧪 Testing Checklist

### Quick Health Check

```bash
# 1. Check all containers are running
docker-compose ps

# Expected: All services show "Up" or "healthy"

# 2. Test health endpoint
curl http://localhost:8000/health

# Expected: {"status": "healthy"}

# 3. Check database connection
docker-compose exec postgres psql -U forensic_user -d forensic_wa -c "SELECT 1;"

# Expected: 1
```

### Automated Authentication Tests

```bash
# Install dependencies
pip3 install requests

# Run tests
python3 scripts/test_auth.py

# Expected: All 6 tests pass ✅
```

### Manual API Testing

1. Open Codespace port 80 URL in browser
2. Append `/docs` to URL
3. Try the following endpoints:
   - `POST /api/auth/login` - Login with admin credentials
   - `GET /api/auth/me` - Get current user (with JWT token)
   - `GET /api/auth/users` - List users (admin only)

**Expected**: All endpoints return 200 status with correct data

### Database Verification

```bash
# Check admin user exists
docker-compose exec postgres psql -U forensic_user -d forensic_wa -c "SELECT username, role FROM users;"

# Check audit log is working
docker-compose exec postgres psql -U forensic_user -d forensic_wa -c "SELECT action, username, status FROM audit_log ORDER BY performed_at DESC LIMIT 5;"
```

---

## 🔒 Security Verification

### Environment Variables Check

```bash
# Verify SECRET_KEY and JWT_SECRET_KEY are NOT defaults
cat .env | grep -E "SECRET_KEY|JWT_SECRET_KEY"

# ⚠️  Both should be long random strings (64+ characters)
# ❌ NOT "changeme" or "your-secret-key-here"
```

### Docker Security Check

```bash
# Verify containers are NOT running as root
docker-compose exec app whoami
# Expected: forensic (NOT root)

docker-compose exec whisper whoami
# Expected: whisper (NOT root)

docker-compose exec spacy whoami
# Expected: spacy (NOT root)
```

### File Permissions Check

```bash
# Verify uploads directory has correct permissions
docker-compose exec app ls -la /app/uploads
# Expected: drwxrwx--- forensic forensic (NOT 777)
```

---

## 📊 Success Criteria

Before proceeding to Phase 1, verify ALL of these:

- [ ] Repository created on GitHub (PRIVATE)
- [ ] Code pushed to GitHub successfully
- [ ] Codespace created and running
- [ ] All Docker containers running (7 services)
- [ ] Database migrations applied
- [ ] Admin user created
- [ ] Health check endpoint returns 200
- [ ] Login endpoint works (returns JWT token)
- [ ] JWT token can be used to access protected endpoints
- [ ] Audit log is recording actions
- [ ] Automated tests pass (scripts/test_auth.py)
- [ ] Swagger UI accessible at `/docs`
- [ ] Port 80 forwarded and accessible
- [ ] Containers running as non-root users
- [ ] .env file NOT committed to Git
- [ ] SECRET_KEY and JWT_SECRET_KEY are secure random values

---

## 🐛 Common Issues and Fixes

### Issue 1: .env file committed to Git

**Problem**: Git shows `.env` in staged files

**Fix**:
```bash
# Remove from staging
git reset HEAD .env

# Add to .gitignore if missing
echo ".env" >> .gitignore

# Commit .gitignore
git add .gitignore
git commit -m "Add .env to .gitignore"
```

### Issue 2: Port 80 not accessible in Codespaces

**Problem**: Can't access application on port 80

**Fix**:
```bash
# Verify EXTERNAL_PORT is set to 80
cat .env | grep EXTERNAL_PORT
# Should be: EXTERNAL_PORT=80

# Check port forwarding in PORTS tab (bottom panel)
# Port 80 should show as "Forwarded"

# Restart services
docker-compose restart app
```

### Issue 3: Docker containers fail to start

**Problem**: `docker-compose ps` shows containers as "Exited"

**Fix**:
```bash
# Check logs
docker-compose logs app

# Common causes:
# 1. Missing .env file - Run: cp .env.codespaces .env
# 2. Database not ready - Wait 15 seconds and restart
# 3. Port conflict - Check EXTERNAL_PORT in .env
```

### Issue 4: Database migrations fail

**Problem**: `alembic upgrade head` fails

**Fix**:
```bash
# Check database is running
docker-compose ps postgres

# Check database connection
docker-compose exec app python -c "from backend.app.core.database import engine; print(engine.url)"

# If connection fails, verify DATABASE_URL in .env
```

---

## ✅ Final Status

**All fixes from user request completed:**
- ✅ claude.md replaced with updated version
- ✅ All gemini-comments fixed (hardcoded password, Docker root, rate limiter)
- ✅ Ollama deferred to Phase 3 (as user requested)
- ✅ Codespaces recommended over local PC (C: drive space issue addressed)
- ✅ Complete deployment documentation created

**Current Phase**: Phase 0 - Foundation (100% Complete)

**Next Phase**: Phase 1 - WhatsApp Parsers (0% Complete)

**Recommended Action**:
1. Complete this checklist
2. Push to GitHub
3. Create Codespace
4. Test authentication system
5. If all tests pass → Start Phase 1

---

**Questions? Issues?**

See:
- `CODESPACES_DEPLOYMENT.md` - Complete Codespaces guide
- `TESTING_CHECKLIST.md` - 50+ test cases
- `CONFIG_MASTER.md` - Configuration reference
- `READY_TO_DEPLOY.md` - Deployment summary
