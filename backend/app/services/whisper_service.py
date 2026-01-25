"""
Whisper Audio Transcription Service (Placeholder)
Phase 2/3: Will use OpenAI Whisper for audio message transcription
"""

from celery import Celery
import os

# Celery configuration
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

celery_app = Celery(
    "whisper_service",
    broker=f"redis://{redis_host}:{redis_port}/0",
    backend=f"redis://{redis_host}:{redis_port}/1",
)


@celery_app.task(name="whisper.transcribe")
def transcribe_audio(audio_path: str):
    """
    Transcribe audio file using Whisper

    Phase 2/3 Implementation - Currently placeholder
    """
    # TODO: Implement audio transcription
    # - Load Whisper model
    # - Transcribe audio file
    # - Return transcription with timestamps
    return {
        "status": "placeholder",
        "message": "Audio transcription will be implemented in Phase 2/3",
        "audio_path": audio_path,
        "transcription": "",
        "language": None,
    }


if __name__ == "__main__":
    celery_app.start()
