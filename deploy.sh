#!/bin/bash
# WhatsApp Forensic Analyzer - Quick Deployment Script
# Run this in GitHub Codespaces terminal after creating the codespace

set -e  # Exit on any error

echo "=========================================="
echo "WhatsApp Forensic Analyzer - Deployment"
echo "=========================================="
echo ""

# Step 1: Setup environment
echo "[1/6] Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.codespaces .env
    echo "✅ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit .env with secure keys!"
    echo ""
    echo "Run these commands to generate secure keys:"
    echo "  python3 -c \"import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))\""
    echo "  python3 -c \"import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(64))\""
    echo ""
    read -p "Press Enter after you've updated .env file with secure keys..."
else
    echo "✅ .env file already exists"
fi

# Step 2: Start Docker containers
echo ""
echo "[2/6] Starting Docker containers..."
docker-compose up -d
echo "✅ Docker containers started"

# Step 3: Wait for services to be ready
echo ""
echo "[3/6] Waiting for services to initialize (15 seconds)..."
sleep 15
echo "✅ Services should be ready"

# Step 4: Check service health
echo ""
echo "[4/6] Checking service health..."
docker-compose ps
echo ""

# Step 5: Run database migrations
echo "[5/6] Running database migrations..."
docker-compose exec -T app alembic upgrade head
echo "✅ Database migrations applied"

# Step 6: Create admin user
echo ""
echo "[6/6] Creating admin user..."
docker-compose exec -T app python scripts/create_admin.py
echo "✅ Admin user created"

# Final status
echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Find your Codespace URL in the PORTS tab (bottom panel)"
echo "2. Open: https://<your-codespace>-80.app.github.dev/docs"
echo "3. Test authentication endpoints"
echo ""
echo "To run automated tests:"
echo "  pip3 install requests"
echo "  python3 scripts/test_auth.py"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f app"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
