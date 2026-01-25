"""
PII Detection Service (Placeholder)
Phase 2/3: Will use spaCy + Presidio for PII detection in messages
"""

from celery import Celery
import os

# Celery configuration
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

celery_app = Celery(
    "pii_service",
    broker=f"redis://{redis_host}:{redis_port}/0",
    backend=f"redis://{redis_host}:{redis_port}/1",
)


@celery_app.task(name="pii.detect")
def detect_pii(text: str):
    """
    Detect PII in text using spaCy + Presidio

    Phase 2/3 Implementation - Currently placeholder
    """
    # TODO: Implement PII detection
    # - Load spaCy model
    # - Use Presidio analyzer
    # - Return detected PII entities
    return {
        "status": "placeholder",
        "message": "PII detection will be implemented in Phase 2/3",
        "text": text,
        "entities": [],
    }


if __name__ == "__main__":
    celery_app.start()
