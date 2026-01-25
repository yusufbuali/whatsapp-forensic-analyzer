# Authentication System - Testing Checklist

**Test Date**: _______________
**Tester**: _______________
**Environment**: Local / Codespaces

---

## ✅ Pre-Test Setup

### 1. Environment Configuration

- [ ] Copy `.env.example` to `.env`
- [ ] Generate secure keys:
  ```bash
  python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
  python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))"
  ```
- [ ] Add keys to `.env`
- [ ] Set `ADMIN_PASSWORD` to secure password
- [ ] Set `DATABASE_PASSWORD` to secure password

### 2. Start Services

```bash
# Start all containers
docker-compose up -d

# Wait 15 seconds for services to initialize
sleep 15

# Check status
docker-compose ps
```

**Expected**: All services should be "Up" or "healthy"

- [ ] ✅ `postgres` - Up
- [ ] ✅ `redis` - Up
- [ ] ✅ `app` - Up (healthy)
- [ ] ✅ `celery_worker` - Up
- [ ] ✅ `celery_beat` - Up

### 3. Database Setup

```bash
# Apply migrations
docker-compose exec app alembic upgrade head
```

**Expected**: No errors, migrations applied successfully

- [ ] ✅ Migrations completed without errors
- [ ] ✅ All 13 tables created

**Verify Tables**:
```bash
docker-compose exec postgres psql -U forensic_user -d forensic_wa -c "\dt"
```

Expected tables:
- [ ] users
- [ ] sessions
- [ ] cases
- [ ] evidence_files
- [ ] chat_sessions
- [ ] messages
- [ ] contacts
- [ ] media_files
- [ ] pii_findings
- [ ] ai_analyses
- [ ] review_queue
- [ ] audit_log
- [ ] reports

### 4. Create Admin User

```bash
docker-compose exec app python scripts/create_admin.py
```

**Expected Output**:
```
✓ Admin user created successfully!
Username: admin
User ID: <uuid>
```

- [ ] ✅ Admin user created
- [ ] ✅ Note the username and password

---

## 🧪 Test Suite 1: Basic API Access

### Test 1.1: Health Check (Public)

```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "1.0.0"
}
```

- [ ] ✅ Status: healthy
- [ ] ✅ Database: connected
- [ ] ✅ Redis: connected

### Test 1.2: API Root

```bash
curl http://localhost:8000/
```

**Expected**:
```json
{
  "name": "WhatsApp Forensic Analyzer",
  "version": "1.0.0",
  "status": "operational"
}
```

- [ ] ✅ API responding
- [ ] ✅ Correct app name

### Test 1.3: API Documentation

Open in browser: `http://localhost:8000/docs`

**Expected**:
- [ ] ✅ Swagger UI loads
- [ ] ✅ Shows all endpoints
- [ ] ✅ Shows "Authorize" button

---

## 🔐 Test Suite 2: Authentication

### Test 2.1: Login (Success)

**Method 1 - Swagger UI**:
1. Open `http://localhost:8000/docs`
2. Expand `POST /api/auth/login`
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "username": "admin",
     "password": "YOUR_ADMIN_PASSWORD"
   }
   ```
5. Click "Execute"

**Expected Response** (Status 200):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": "...",
    "username": "admin",
    "email": "admin@forensics.local",
    "role": "admin",
    "is_active": true
  }
}
```

- [ ] ✅ Status code: 200
- [ ] ✅ Received access_token
- [ ] ✅ Received refresh_token
- [ ] ✅ User object returned
- [ ] ✅ Role is "admin"

**Copy the `access_token` for next tests!**

**Method 2 - cURL**:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "YOUR_ADMIN_PASSWORD"
  }'
```

- [ ] ✅ Same result as Swagger UI

### Test 2.2: Login (Failure - Wrong Password)

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "WrongPassword123!"
  }'
```

**Expected Response** (Status 401):
```json
{
  "detail": "Incorrect username or password"
}
```

- [ ] ✅ Status code: 401
- [ ] ✅ Error message shown

### Test 2.3: Login (Failure - Rate Limiting)

Try logging in with wrong password **6 times in a row**.

**Expected**:
- After 5 attempts: Status 429 "Too many login attempts"

- [ ] ✅ Rate limiting activated after 5 attempts

---

## 🔒 Test Suite 3: Protected Endpoints

### Test 3.1: Get Current User (Success)

**Method 1 - Swagger UI**:
1. Click "Authorize" button (top right)
2. Paste your access_token
3. Click "Authorize"
4. Expand `GET /api/auth/me`
5. Click "Try it out"
6. Click "Execute"

**Expected Response** (Status 200):
```json
{
  "id": "...",
  "username": "admin",
  "email": "admin@forensics.local",
  "full_name": "System Administrator",
  "role": "admin",
  "is_active": true,
  "is_verified": true,
  "created_at": "2026-01-21T...",
  "last_login": "2026-01-21T..."
}
```

- [ ] ✅ Status code: 200
- [ ] ✅ User info returned
- [ ] ✅ Last login timestamp updated

**Method 2 - cURL**:
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

- [ ] ✅ Same result as Swagger UI

### Test 3.2: Access Without Token (Failure)

```bash
curl -X GET "http://localhost:8000/api/auth/me"
```

**Expected Response** (Status 403):
```json
{
  "detail": "Not authenticated"
}
```

- [ ] ✅ Status code: 401 or 403
- [ ] ✅ Access denied

### Test 3.3: Access With Invalid Token (Failure)

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer invalid_token_12345"
```

**Expected Response** (Status 401):
```json
{
  "detail": "Invalid authentication credentials"
}
```

- [ ] ✅ Status code: 401
- [ ] ✅ Invalid token rejected

---

## 👥 Test Suite 4: User Management (Admin)

### Test 4.1: Create New User

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

**Expected Response** (Status 200):
```json
{
  "id": "...",
  "username": "examiner1",
  "email": "examiner@forensics.local",
  "full_name": "Jane Doe",
  "role": "examiner",
  "is_active": true
}
```

- [ ] ✅ Status code: 200
- [ ] ✅ User created
- [ ] ✅ Role is "examiner"

### Test 4.2: List All Users

```bash
curl -X GET "http://localhost:8000/api/auth/users" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response**:
```json
{
  "users": [
    {
      "id": "...",
      "username": "admin",
      "role": "admin"
    },
    {
      "id": "...",
      "username": "examiner1",
      "role": "examiner"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 100
}
```

- [ ] ✅ Both users listed
- [ ] ✅ Total count correct

### Test 4.3: Login as New User

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "examiner1",
    "password": "SecurePass123!"
  }'
```

- [ ] ✅ Status code: 200
- [ ] ✅ New user can login
- [ ] ✅ Role is "examiner"

---

## 🔄 Test Suite 5: Token Refresh

### Test 5.1: Refresh Token

```bash
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Expected Response** (Status 200):
```json
{
  "access_token": "new_token...",
  "refresh_token": "new_refresh_token...",
  "token_type": "bearer",
  "expires_in": 28800
}
```

- [ ] ✅ New tokens received
- [ ] ✅ Old token is different from new token

---

## 🔐 Test Suite 6: Password Change

### Test 6.1: Change Password (Success)

```bash
curl -X POST "http://localhost:8000/api/auth/change-password" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "YOUR_CURRENT_PASSWORD",
    "new_password": "NewSecurePass456!",
    "confirm_password": "NewSecurePass456!"
  }'
```

**Expected Response** (Status 200):
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

- [ ] ✅ Password changed
- [ ] ✅ Can login with new password
- [ ] ✅ Cannot login with old password

---

## 📊 Test Suite 7: Audit Logging

### Test 7.1: Verify Audit Logs

```bash
docker-compose exec postgres psql -U forensic_user -d forensic_wa
```

```sql
SELECT
  action,
  username,
  status,
  performed_at
FROM audit_log
ORDER BY performed_at DESC
LIMIT 10;
```

**Expected**: All actions logged (login, user creation, password change, etc.)

- [ ] ✅ Login actions logged
- [ ] ✅ User creation logged
- [ ] ✅ Username captured
- [ ] ✅ IP address captured
- [ ] ✅ Timestamp accurate

### Test 7.2: Check Audit Log Counts

```sql
SELECT action, COUNT(*) as count
FROM audit_log
GROUP BY action
ORDER BY count DESC;
```

- [ ] ✅ AUTH_LOGIN present
- [ ] ✅ USER_CREATE present
- [ ] ✅ USER_VIEW_PROFILE present

---

## 🎯 Test Suite 8: Role-Based Access Control

### Test 8.1: Examiner Cannot Create Users

1. Login as examiner1
2. Try to create a new user

**Expected**: Status 403 "Insufficient permissions"

- [ ] ✅ Access denied for non-admin

### Test 8.2: Viewer Cannot Access Protected Resources

1. Create a viewer user
2. Login as viewer
3. Try to access resources

- [ ] ✅ Viewer can view cases (when implemented)
- [ ] ✅ Viewer cannot modify cases

---

## 🔧 Test Suite 9: Error Handling

### Test 9.1: Duplicate Username

Try creating a user with existing username.

**Expected**: Status 400 "Username already registered"

- [ ] ✅ Duplicate prevented

### Test 9.2: Weak Password

Try creating user with password "12345".

**Expected**: Status 422 validation error

- [ ] ✅ Weak password rejected

### Test 9.3: Invalid Email

Try creating user with invalid email.

**Expected**: Status 422 validation error

- [ ] ✅ Invalid email rejected

---

## 🚀 Automated Test Script

Run the automated test script:

```bash
pip install requests
python scripts/test_auth.py
```

**Expected Output**:
```
✓ PASS - Health Check
✓ PASS - Login
✓ PASS - Get Current User
✓ PASS - List Users (Admin)
✓ PASS - Unauthorized Access
✓ PASS - Invalid Token

Total: 6/6 tests passed
🎉 All tests passed!
```

- [ ] ✅ All automated tests passed

---

## 📋 Final Checklist

### Functionality
- [ ] ✅ Login works
- [ ] ✅ JWT tokens generated
- [ ] ✅ Protected endpoints secured
- [ ] ✅ Admin can create users
- [ ] ✅ RBAC enforced
- [ ] ✅ Password change works
- [ ] ✅ Token refresh works
- [ ] ✅ Rate limiting active
- [ ] ✅ Account locking works

### Security
- [ ] ✅ Passwords hashed (bcrypt)
- [ ] ✅ Invalid tokens rejected
- [ ] ✅ Unauthorized access blocked
- [ ] ✅ Rate limiting prevents brute force
- [ ] ✅ Weak passwords rejected
- [ ] ✅ Sessions tracked in database

### Forensic Compliance
- [ ] ✅ All actions logged to audit_log
- [ ] ✅ User captured in logs
- [ ] ✅ IP address captured
- [ ] ✅ Timestamp accurate
- [ ] ✅ Chain of custody maintained

### Database
- [ ] ✅ All 13 tables created
- [ ] ✅ Foreign keys enforced
- [ ] ✅ Indexes present
- [ ] ✅ Migrations work

### Documentation
- [ ] ✅ Swagger UI accessible
- [ ] ✅ API docs complete
- [ ] ✅ All endpoints documented

---

## ✅ Test Result Summary

**Date Tested**: _______________
**Environment**: _______________
**Total Tests**: 50+
**Tests Passed**: _____ / _____
**Tests Failed**: _____

**Overall Status**: ⬜ PASS  ⬜ FAIL

**Notes**:
```
[Your notes here]
```

**Issues Found**:
```
[List any issues]
```

---

## 🎉 Success Criteria

Authentication system is considered **READY FOR PRODUCTION** if:

- ✅ All automated tests pass
- ✅ All manual tests pass
- ✅ No security vulnerabilities found
- ✅ Audit logging working
- ✅ RBAC enforced correctly
- ✅ Performance acceptable (<100ms response time)

**Current Status**: ⬜ READY  ⬜ NEEDS WORK

---

## 📞 Support

If tests fail, check:
1. Logs: `docker-compose logs -f app`
2. Database: `docker-compose exec postgres psql -U forensic_user -d forensic_wa`
3. Health: `curl http://localhost:8000/health`
4. Docs: See `QUICKSTART.md`

---

**Next Step After All Tests Pass**: Proceed to Phase 1 - WhatsApp Parsers
