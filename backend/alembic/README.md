# Database Migrations with Alembic

This directory contains database migrations for the WhatsApp Forensic Analyzer.

## Setup

Alembic is already configured. The configuration is in `alembic.ini` at the project root.

## Common Commands

### Create a new migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration (for data migrations)
alembic revision -m "description of changes"
```

### Apply migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Go to specific revision
alembic upgrade <revision_id>
```

### Check migration status

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

## Migration Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Test migrations on a copy of production data** before deploying
3. **Include both upgrade and downgrade** operations
4. **Keep migrations small and focused** - one logical change per migration
5. **Never edit applied migrations** - create a new migration instead
6. **Document complex migrations** with comments in the migration file

## Database URL

The database URL is read from the `DATABASE_URL` environment variable. Default:
```
postgresql://forensic_user:password@localhost:5432/forensic_wa
```

## Initial Setup

For a new installation:

```bash
# Create all tables
alembic upgrade head

# Or run the SQL schema directly
psql -U forensic_user -d forensic_wa -f backend/app/models/database_schema.sql
```

## Forensic Considerations

- All migrations are **logged** for audit purposes
- Migrations that affect evidence data require **special approval**
- **Backup the database** before running migrations in production
- Verify **data integrity** (hash verification) after migrations
- Document any **schema changes** in the case audit log

## Troubleshooting

### Migration conflicts

If you get version conflicts, check:
```bash
alembic history
alembic current
```

### Reset to a clean state (DESTRUCTIVE)

```bash
# Drop all tables
alembic downgrade base

# Recreate all tables
alembic upgrade head
```

### Manual SQL

If you need to run manual SQL:
```bash
alembic upgrade head --sql > migration.sql
# Review and edit migration.sql
psql -U forensic_user -d forensic_wa -f migration.sql
```

## Migration Naming Convention

Format: `YYYYMMDD_HHMM_<revision>_<slug>`

Example: `20260121_1400_abc123_add_user_authentication`

## Directory Structure

```
alembic/
├── versions/          # Migration files (auto-generated)
├── env.py            # Alembic environment configuration
├── script.py.mako    # Template for new migrations
└── README.md         # This file
```

## Important Notes

- **Database name**: `forensic_wa` (standard - do not change)
- **Port**: 5432 (PostgreSQL default)
- Migrations run inside Docker container: `docker-compose exec app alembic upgrade head`
