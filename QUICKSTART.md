# WhatsApp Forensic Analyzer - Quick Start Guide

Get the authentication system running in **5 minutes**! 🚀

---

## Prerequisites

- Docker & Docker Compose installed
- Python 3.11+ (for local development)
- 8GB RAM minimum

---

## Option 1: Docker (Recommended - Fastest) 🐳

### Step 1: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set secure passwords
nano .env
```

**CRITICAL**: Change these values in `.env`:
```bash
SECRET_KEY=<generate-with-command-below>
JWT_SECRET_KEY=<generate-with-command-below>
DATABASE_PASSWORD=your-secure-db-password
ADMIN_PASSWORD=YourSecureAdminPassword123!
```

Generate secure keys:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"
```

### Step 2: Start Services

```bash
# Start all services (PostgreSQL, Redis, FastAPI, Celery)
docker-compose up -d

# Check logs
docker-compose logs -f app
```

### Step 3: Run Database Migrations

```bash
# Apply database schema
docker-compose exec app alembic upgrade head
```

### Step 4: Create Admin User

```bash
# Create initial admin user
docker-compose exec app python scripts/create_admin.py
```

You'll see:
```
✓ Admin user created successfully!
Username: admin
Password: YourSecureAdminPassword123!
Login URL: http://localhost:8000/docs
```

### Step 5: Test Authentication

Open browser: **http://localhost:8000/docs**

**Try the API:**

1. Click **"Authorize"** button (top right)
2. Click **"POST /api/auth/login"**
3. Click **"Try it out"**
4. Enter credentials:
```json
{
  "username": "admin",
  "password": "YourSecureAdminPassword123!"
}
```
5. Click **"Execute"**

You should get:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": "...",
    "username": "admin",
    "role": "admin"
  }
}
```

6. Copy the `access_token`
7. Click **"Authorize"** button again
8. Paste token in format: `Bearer <your-token>`
9. Click **"Authorize"**
10. Try **GET /api/auth/me** - should return your user info!

**✅ Authentication is working!**

---

## Option 2: Local Development (Manual) 💻

### Step 1: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_trf
```

### Step 2: Start PostgreSQL & Redis

```bash
# Option A: Use Docker for DB only
docker-compose up -d postgres redis

# Option B: Install locally (Windows)
# Download PostgreSQL: https://www.postgresql.org/download/
# Download Redis: https://github.com/microsoftarchive/redis/releases

# Create database
createdb forensic_wa
```

### Step 3: Configure Environment

```bash
cp .env.example .env

# Edit .env
# Set DATABASE_HOST=localhost (not postgres)
# Set REDIS_HOST=localhost (not redis)
```

### Step 4: Run Migrations

```bash
cd backend
alembic upgrade head
```

### Step 5: Create Admin User

```bash
python scripts/create_admin.py
```

### Step 6: Start FastAPI Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Test

Open: **http://localhost:8000/docs**

Follow same testing steps as Docker option above.

---

## API Endpoints Overview 📋

### Public Endpoints (No Auth Required)
- `GET /` - API info
- `GET /health` - Health check
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token

### Protected Endpoints (Auth Required)
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/me` - Update current user
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/logout` - Logout

### Admin Endpoints (Admin Role Required)
- `POST /api/auth/users` - Create user
- `GET /api/auth/users` - List users
- `GET /api/auth/users/{id}` - Get user by ID
- `PUT /api/auth/users/{id}` - Update user
- `DELETE /api/auth/users/{id}` - Disable user

---

## Testing with cURL 🔧

### 1. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "YourSecureAdminPassword123!"
  }'
```

Save the `access_token` from response.

### 2. Get Current User

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Create New User (Admin Only)

```bash
curl -X POST "http://localhost:8000/api/auth/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "examiner1",
    "email": "examiner@forensics.local",
    "password": "SecurePass123!",
    "full_name": "Jane Doe",
    "role": "examiner"
  }'
```

### 4. List All Users

```bash
curl -X GET "http://localhost:8000/api/auth/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Change Password

```bash
curl -X POST "http://localhost:8000/api/auth/change-password" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "YourSecureAdminPassword123!",
    "new_password": "NewSecurePass456!",
    "confirm_password": "NewSecurePass456!"
  }'
```

---

## Troubleshooting 🔍

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

### "Table does not exist" Error

```bash
# Run migrations
docker-compose exec app alembic upgrade head
```

### "Admin user already exists"

This is normal if you've already run the script. You can login with existing credentials.

### Port 8000 Already in Use

```bash
# Check what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Change port in .env
API_PORT=8001
```

### Can't Access from Other Machines

```bash
# In .env, set:
API_HOST=0.0.0.0

# Add your IP to CORS_ORIGINS:
CORS_ORIGINS=["http://localhost:8000", "http://192.168.1.100:8000"]
```

---

## What's Next? 🎯

Now that authentication is working, you can:

1. **Create Users**: Use admin account to create examiner and viewer users
2. **Test RBAC**: Login as different roles to test permissions
3. **Check Audit Logs**: Query `audit_log` table to see all actions logged
4. **Implement Parsers**: Next step is iOS/Android WhatsApp parsers
5. **Build Frontend**: Create web UI for chat viewing

---

## Security Checklist ✅

Before going to production:

- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY` to random 64-char strings
- [ ] Change `ADMIN_PASSWORD` immediately after first login
- [ ] Change `DATABASE_PASSWORD` to strong password
- [ ] Set `DEBUG=False` in production
- [ ] Enable `USE_HTTPS=True` with valid SSL certificates
- [ ] Remove `localhost` from `CORS_ORIGINS` in production
- [ ] Review all users have strong passwords
- [ ] Test backup/recovery procedures
- [ ] Set up log monitoring

---

## Useful Commands 📝

```bash
# View logs
docker-compose logs -f app

# Restart app
docker-compose restart app

# Access database
docker-compose exec postgres psql -U forensic_user -d forensic_wa

# Access Redis CLI
docker-compose exec redis redis-cli

# Run Python shell in container
docker-compose exec app python

# Stop all services
docker-compose down

# Remove volumes (⚠️ deletes data)
docker-compose down -v
```

---

## Database Access 🗄️

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U forensic_user -d forensic_wa

# Useful queries:
SELECT * FROM users;
SELECT * FROM sessions WHERE is_revoked = false;
SELECT * FROM audit_log ORDER BY performed_at DESC LIMIT 10;

# Check table structure
\d users
\d audit_log
```

---

## Performance Tips ⚡

1. **Indexes**: Database has proper indexes for performance
2. **Connection Pooling**: Configured with 10 connections by default
3. **JWT Tokens**: Cached in database for validation
4. **Rate Limiting**: Login limited to 5 attempts per 15 minutes
5. **Audit Logs**: Written asynchronously to not block requests

---

## Support 🆘

- **Documentation**: See `README.md`
- **Configuration**: See `CONFIG_MASTER.md`
- **Implementation Status**: See `IMPLEMENTATION_PROGRESS.md`
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**You're ready to use the WhatsApp Forensic Analyzer authentication system!** 🎉

Next: Implement WhatsApp parsers to extract messages from databases.
