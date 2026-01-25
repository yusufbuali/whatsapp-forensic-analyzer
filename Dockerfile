# WhatsApp Forensic Analyzer - Main Application Dockerfile
# Python 3.11 with slim base image for smaller size
# Security: Runs as non-root user 'forensic'

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r forensic && useradd -r -g forensic forensic

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    gcc \
    g++ \
    make \
    # PostgreSQL client
    libpq-dev \
    postgresql-client \
    # Image processing
    libmagic1 \
    libmagic-dev \
    # WeasyPrint dependencies
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    # Utilities
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_trf

# Copy application code
COPY backend/ /app/

# Create necessary directories
RUN mkdir -p /app/uploads/evidence /app/uploads/working \
    /app/logs /app/backups \
    /app/alembic/versions

# Set ownership and permissions for non-root user
# App code: read-only (755)
# Data directories: read-write for forensic user (770)
RUN chown -R forensic:forensic /app && \
    chmod -R 755 /app && \
    chmod -R 770 /app/uploads /app/logs /app/backups

# Switch to non-root user
USER forensic

# Expose standard port 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
