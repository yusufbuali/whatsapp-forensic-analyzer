# WhatsApp Forensic Analyzer - Phase 2 Build

## Development Environment
- **Primary Environment**: GitHub Codespaces
- **Repository**: https://github.com/yusufbuali/whatsapp-forensic-analyzer
- **Port**: 80
- **Working Method**: All code changes made directly in Codespace

## Common Commands
```bash
docker-compose up --build          # Start all services
docker-compose logs -f app         # View logs
docker-compose restart app         # Restart after changes
docker-compose exec db psql -U postgres -d forensic  # Access DB
```

## Context
This continues from Phase 1 where we built:
- Docker Compose setup (app, db, redis, celery)
- iOS ChatStorage.sqlite parser
- Basic FastAPI backend with case/evidence/chat endpoints
- Simple web UI (dashboard, case view, chat list, chat viewer)

## Phase 2 Deliverables

### 1. Android Database Parser
Parse `msgstore.db` (decrypted Android WhatsApp backup):

**Key Tables:**
```sql
-- chat: Conversations
-- Key columns: _id, jid_row_id, subject, created_timestamp

-- messages: All messages
-- Key columns: _id, chat_row_id, from_me, timestamp, text_data, message_type

-- message_media: Media attachments
-- Key columns: message_row_id, file_path, mime_type, file_size

-- jid: Contact JID mapping
-- Key columns: _id, raw_string, user, server
```

**Android Timestamp**: Milliseconds since Unix epoch (divide by 1000)

### 2. Full-Text Search
```sql
-- Add PostgreSQL full-text search
ALTER TABLE messages ADD COLUMN search_vector tsvector;
CREATE INDEX idx_messages_search ON messages USING GIN(search_vector);

-- Update trigger for auto-indexing
CREATE OR REPLACE FUNCTION messages_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', COALESCE(NEW.text_content, ''));
    RETURN NEW;
END
$$ LANGUAGE plpgsql;
```

API: `GET /api/cases/{id}/search?q={query}&chat_id={optional}&date_from={}&date_to={}`

### 3. GPS Map View
- Extract all messages with latitude/longitude
- Display on Leaflet.js map (OpenStreetMap - works offline with tiles)
- Timeline slider to filter by date range
- Click marker to see message context
- Export to KML for Google Earth

API: `GET /api/cases/{id}/locations?date_from={}&date_to={}`

UI: New page `/cases/{id}/map` with:
- Full-screen map
- Sidebar with location list
- Date range picker
- KML export button

### 4. Media Gallery
- Grid view of all media (images, videos, documents)
- Thumbnail generation for images/videos
- Filter by type, date, chat
- Click to view full size with message context

API: `GET /api/cases/{id}/media?type={image|video|audio|document}&chat_id={}`

### 5. Contact Management
- List all unique contacts across chats
- Show contact stats (message count, first/last message)
- Merge duplicate contacts
- Add investigator notes to contacts

```sql
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    evidence_id INTEGER REFERENCES evidence_items(id),
    jid VARCHAR(100),
    display_name VARCHAR(100),
    phone_number VARCHAR(20),
    message_count INTEGER,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    investigator_notes TEXT
);
```

### 6. PDF Report Generator
Generate court-admissible PDF reports with:
- Case metadata (number, examiner, dates)
- Evidence integrity (SHA256/MD5 hashes)
- Chat summary statistics
- Selected conversations (filtered by date/contact)
- Media thumbnails with captions
- GPS locations with map snapshot
- Audit trail excerpt

Use **WeasyPrint** (HTML to PDF, works offline):
```python
from weasyprint import HTML, CSS

def generate_report(case_id, options):
    html_content = render_template('report_template.html', data=report_data)
    pdf = HTML(string=html_content).write_pdf(
        stylesheets=[CSS('report_styles.css')]
    )
    return pdf
```

API:
- `POST /api/cases/{id}/reports` - Generate report (returns job ID)
- `GET /api/cases/{id}/reports/{rid}/status` - Check generation status
- `GET /api/cases/{id}/reports/{rid}/download` - Download PDF

### 7. Excel Export
Export data to XLSX for analysis:
- All messages (with metadata)
- Contact list
- Media inventory
- Location data

Use **openpyxl**:
```python
from openpyxl import Workbook

def export_messages_xlsx(case_id, chat_ids=None):
    wb = Workbook()
    ws = wb.active
    ws.title = "Messages"
    # Headers
    ws.append(['Timestamp', 'Chat', 'Sender', 'Message', 'Type', 'Media'])
    # Data rows...
```

API: `GET /api/cases/{id}/export/excel?include=messages,contacts,media,locations`

## Updated File Structure
```
app/
├── parsers/
│   ├── ios_parser.py      # Existing
│   ├── android_parser.py  # NEW
│   └── base_parser.py
├── routers/
│   ├── search.py          # Enhanced
│   ├── locations.py       # NEW
│   ├── media.py           # NEW
│   ├── contacts.py        # NEW
│   └── reports.py         # NEW
├── services/
│   ├── search_service.py  # NEW
│   ├── map_service.py     # NEW
│   ├── report_service.py  # NEW
│   └── export_service.py  # NEW
└── templates/
    ├── map_view.html      # NEW
    ├── media_gallery.html # NEW
    ├── contacts.html      # NEW
    └── reports/
        └── pdf_template.html  # NEW
```

## Dependencies to Add
```
weasyprint==60.1
openpyxl==3.1.2
Pillow==10.2.0  # Thumbnail generation
python-magic==0.4.27  # MIME type detection
```

## First Task
Start with the Android parser, then implement full-text search since these are core features. After that, add the map view and reports.
