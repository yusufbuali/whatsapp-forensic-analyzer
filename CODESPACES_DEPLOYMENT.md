# GitHub Codespaces Deployment Guide

**WhatsApp Forensic Analyzer**
**Version**: 1.0.0
**Last Updated**: 2026-01-21

---

## 🎯 Why GitHub Codespaces?

✅ **Advantages**:
- No local Docker installation required (saves disk space)
- Pre-configured development environment
- Access from anywhere via browser
- Automatic HTTPS with corporate firewall support (port 80)
- No impact on your C: drive
- Isolated environment (safe for forensic tools)
- Built-in VS Code editor
- Free tier: 60 hours/month for personal accounts

❌ **Limitations**:
- Requires internet connection
- Limited to Codespaces hours/month
- Less control than local environment

---

## 📋 Prerequisites

1. **GitHub Account** (free or paid)
2. **Repository**: https://github.com/yusufbuali/whatsapp-forensic-analyzer
3. **Browser**: Chrome, Edge, Firefox, or Safari
4. **Internet Connection**: Required

---

## 🚀 Quick Start (5 Minutes)

### **Step 1: Create Codespace**

1. Go to your repository:
   ```
   https://github.com/yusufbuali/whatsapp-forensic-analyzer
   ```

2. Click the **green "Code"** button

3. Click **"Codespaces"** tab

4. Click **"Create codespace on main"**

5. Wait 2-3 minutes while Codespace initializes

**Expected**: VS Code interface opens in browser

---

### **Step 2: Configure Environment**

In the Codespace terminal:

```bash
# Copy Codespaces environment template
cp .env.codespaces .env

# Generate secure keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"

# Edit .env file (in VS Code)
# Replace these values:
# - SECRET_KEY=<paste-generated-key>
# - JWT_SECRET_KEY=<paste-generated-key>
# - ADMIN_PASSWORD=YourSecurePassword123!
# - DATABASE_PASSWORD=SecureDBPassword456!
```

**Tip**: Click on `.env` file in left sidebar to edit

---

### **Step 3: Start Services**

```bash
# Start all Docker containers
docker-compose up -d

# Wait 15 seconds for services to initialize
sleep 15

# Check status
docker-compose ps
```

**Expected**: All services showing as "Up" or "healthy"

---

### **Step 4: Initialize Database**

```bash
# Run database migrations
docker-compose exec app alembic upgrade head

# Create admin user
docker-compose exec app python scripts/create_admin.py
```

**Expected**: Admin user created with credentials shown

---

### **Step 5: Access the Application**

Codespaces will automatically forward port 80. Look for the notification:

**"Your application running on port 80 is available"**

Click the notification or:

1. Go to **"PORTS"** tab (bottom panel in VS Code)
2. Find port **80**
3. Click the **globe icon** (🌐) or copy the URL
4. Open in new browser tab

**URL Format**: `https://<codespace-name>-80.app.github.dev`

---

### **Step 6: Test Authentication**

Open the Codespace URL and append `/docs`:

```
https://<your-codespace>-80.app.github.dev/docs
```

1. Click **"Authorize"** button (lock icon, top right)
2. Click **"POST /api/auth/login"**
3. Click **"Try it out"**
4. Enter credentials:
   ```json
   {
     "username": "admin",
     "password": "YourSecurePassword123!"
   }
   ```
5. Click **"Execute"**

**Expected**: Status 200, access_token received

---

## 🛠️ Common Tasks in Codespaces

### **View Logs**

```bash
# Application logs
docker-compose logs -f app

# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
```

### **Restart Services**

```bash
# Restart all
docker-compose restart

# Restart app only
docker-compose restart app
```

### **Access Database**

```bash
docker-compose exec postgres psql -U forensic_user -d forensic_wa

# Example queries:
SELECT * FROM users;
SELECT * FROM audit_log ORDER BY performed_at DESC LIMIT 10;
\q  # to exit
```

### **Run Tests**

```bash
# Install requests library (for test script)
pip3 install requests

# Run automated tests
python3 scripts/test_auth.py
```

### **Stop Services**

```bash
docker-compose down
```

### **View Resource Usage**

```bash
# Container stats
docker stats

# Disk usage
df -h

# Codespace details
gh codespace view
```

---

## 🔐 Security Best Practices for Codespaces

### **1. Use Codespaces Secrets**

Instead of `.env` file, use Codespaces secrets:

1. Go to GitHub → **Settings** → **Codespaces** → **Secrets**
2. Add secrets:
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `DATABASE_PASSWORD`
   - `ADMIN_PASSWORD`

These are automatically available as environment variables.

### **2. Don't Commit .env**

The `.gitignore` file already excludes `.env`, but verify:

```bash
# Check if .env is ignored
git status

# Should NOT see .env file listed
```

### **3. Use Private Repository**

Ensure your repository is **private** if it contains forensic tools:

1. Go to repository → **Settings**
2. Scroll to **Danger Zone**
3. Verify **visibility is Private**

### **4. Stop Codespace When Not in Use**

**Important**: Codespaces consume hours even when idle!

- Click **Codespaces** menu (bottom left)
- Click **"Stop Current Codespace"**

Or via CLI:
```bash
gh codespace stop
```

### **5. Delete Codespace After Testing**

If done testing:

1. Go to https://github.com/codespaces
2. Find your codespace
3. Click **"..."** → **"Delete"**

---

## 🐛 Troubleshooting

### **Port 80 Not Accessible**

**Problem**: Can't access application on port 80

**Solution**:
```bash
# Check if port is forwarded
docker-compose ps

# Verify port mapping
docker-compose logs app | grep "port"

# Check Codespaces ports
# Go to PORTS tab (bottom panel)
# Ensure port 80 shows as "Forwarded"
```

### **Database Connection Failed**

**Problem**: App can't connect to PostgreSQL

**Solution**:
```bash
# Check if postgres is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### **Out of Disk Space**

**Problem**: "No space left on device"

**Solution**:
```bash
# Clean up Docker
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Check space
df -h
```

Codespaces default: 32GB storage (upgradeable to 64GB)

### **Codespace Won't Start**

**Problem**: Codespace creation fails

**Solution**:
1. Try creating a new codespace
2. Check GitHub Status: https://www.githubstatus.com/
3. Contact GitHub Support if issue persists

### **Performance Issues**

**Problem**: Slow response times

**Solution**:
```bash
# Check resource usage
docker stats

# Reduce running services
docker-compose stop whisper spacy celery_beat

# Keep only essential:
docker-compose up -d postgres redis app
```

### **Can't Find Codespace URL**

**Problem**: Lost the URL to access application

**Solution**:
```bash
# List forwarded ports
gh codespace ports

# Or check in PORTS tab (bottom panel in VS Code)
```

---

## 📊 Resource Usage

### **Typical Usage**:
- **CPU**: 2-4 cores
- **RAM**: 4-8 GB
- **Disk**: 10-15 GB (with Docker images)
- **Network**: Minimal after initial setup

### **Codespace Sizes**:
- **2-core** (Free tier): Sufficient for testing
- **4-core**: Better performance
- **8-core**: Production-like performance

Change size: Repository → Settings → Codespaces → Change machine type

---

## 🔄 Updating Code in Codespaces

### **Method 1: Git Pull**

```bash
git pull origin main
docker-compose restart app
```

### **Method 2: Edit in Codespace**

1. Make changes in VS Code
2. Files auto-save
3. Restart to apply:
   ```bash
   docker-compose restart app
   ```

### **Method 3: Sync from GitHub**

If you edit files on GitHub directly:

```bash
# In Codespace:
git fetch origin
git reset --hard origin/main
docker-compose up -d --build
```

---

## 💰 Cost Considerations

### **Free Tier** (Personal Account):
- 60 hours/month
- 2-core, 4GB RAM, 32GB storage

### **Pro** ($4/month):
- 180 hours/month
- Same specs as free

### **Tips to Save Hours**:
1. **Stop codespace** when not in use (doesn't count hours)
2. **Delete** old codespaces
3. **Use prebuilds** (faster startup, uses fewer hours)

### **Check Usage**:
```
https://github.com/settings/billing
→ Codespaces tab
→ View usage
```

---

## 🎓 Advanced Configuration

### **Prebuilds** (Faster Startup)

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "WhatsApp Forensic Analyzer",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/app",
  "postCreateCommand": "alembic upgrade head && python scripts/create_admin.py",
  "forwardPorts": [80, 8000, 5432],
  "portsAttributes": {
    "80": {
      "label": "Application",
      "onAutoForward": "notify"
    }
  }
}
```

Then enable prebuilds in repository settings.

### **Custom Machine Type**

Edit `.devcontainer/devcontainer.json`:

```json
{
  "hostRequirements": {
    "cpus": 4,
    "memory": "8gb",
    "storage": "64gb"
  }
}
```

### **Environment Variables from Secrets**

In `.devcontainer/devcontainer.json`:

```json
{
  "remoteEnv": {
    "SECRET_KEY": "${localEnv:SECRET_KEY}",
    "JWT_SECRET_KEY": "${localEnv:JWT_SECRET_KEY}"
  }
}
```

---

## 📝 Complete Workflow Example

### **First Time Setup**:

```bash
# 1. Create Codespace (via GitHub UI)

# 2. Configure environment
cp .env.codespaces .env
# Edit .env with secure values

# 3. Start services
docker-compose up -d

# 4. Initialize
docker-compose exec app alembic upgrade head
docker-compose exec app python scripts/create_admin.py

# 5. Test
curl http://localhost/health
python3 scripts/test_auth.py

# 6. Access via browser
# Open forwarded port 80 URL
```

### **Daily Development**:

```bash
# Start codespace (if stopped)
# Edit code in VS Code
# Test changes:
docker-compose restart app
curl http://localhost/health

# Commit changes
git add .
git commit -m "Your message"
git push

# Stop codespace when done
```

---

## ✅ Success Checklist

Before proceeding to Phase 1:

- [ ] Codespace created successfully
- [ ] Services running (docker-compose ps shows all "Up")
- [ ] Database migrations applied
- [ ] Admin user created
- [ ] Can access application on port 80
- [ ] Swagger UI loads at `/docs`
- [ ] Login works (returns JWT token)
- [ ] Automated tests pass (scripts/test_auth.py)
- [ ] Audit logs working (check audit_log table)

---

## 🆘 Getting Help

1. **Check Logs**: `docker-compose logs -f app`
2. **Test Health**: `curl http://localhost/health`
3. **View Documentation**: `/docs` endpoint
4. **GitHub Issues**: Report bugs in repository
5. **Codespaces Docs**: https://docs.github.com/en/codespaces

---

## 📚 Next Steps

After authentication is working:

1. **Phase 1**: Implement WhatsApp parsers (iOS & Android)
2. **Phase 2**: Build frontend with HTMX
3. **Phase 3**: Add AI analysis (Whisper, spaCy, Ollama)
4. **Phase 4**: Production deployment

---

## 🔒 Security Reminder

This is a **forensic tool** handling sensitive evidence:

- Always use **private repository**
- Enable **2FA** on GitHub account
- Use **Codespaces secrets** for sensitive values
- **Stop codespace** when not in use
- **Delete codespace** after testing with real evidence
- Never commit **real evidence files** to Git

---

**You're ready to develop in GitHub Codespaces!** 🎉

**Recommended**: Test authentication system now, then proceed to Phase 1 (WhatsApp parsers).

---

**Status**: ✅ READY FOR CODESPACES DEPLOYMENT
**Next**: Create codespace and follow Quick Start steps
