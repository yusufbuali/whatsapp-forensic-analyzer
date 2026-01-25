# WhatsApp Forensic Analyzer

Forensic analysis tool for WhatsApp data extraction from iOS and Android devices.

## Quick Start (GitHub Codespaces)

### 1. Start the application

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 2. Access the application

Once running, Codespaces will show a popup to open port 80.
Click "Open in Browser" to see the dashboard.

Or manually: Go to PORTS tab → Click the globe icon next to port 80

### 3. Check health

```bash
curl http://localhost/health
```

## Project Structure

```
whatsapp-forensic-analyzer/
├── docker-compose.yml      # Docker services config
├── Dockerfile              # App container build
├── requirements.txt        # Python dependencies
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── config.py          # Settings (TODO)
│   ├── database.py        # DB connection (TODO)
│   ├── models/            # SQLAlchemy models (TODO)
│   ├── parsers/           # iOS/Android parsers (TODO)
│   ├── routers/           # API endpoints (TODO)
│   ├── services/          # Business logic (TODO)
│   └── templates/         # Jinja2 HTML templates
│       └── dashboard.html
├── static/                # CSS, JS files
└── uploads/               # Evidence storage
```

## Development Commands

```bash
# View logs
docker-compose logs -f app

# Restart app after code changes
docker-compose restart app

# Stop everything
docker-compose down

# Reset database (delete all data)
docker-compose down -v
docker-compose up --build
```

## Next Steps

1. Add database models (cases, messages, etc.)
2. Create iOS parser for ChatStorage.sqlite
3. Build case management API
4. Add chat viewer UI

See phase prompts for detailed instructions.
