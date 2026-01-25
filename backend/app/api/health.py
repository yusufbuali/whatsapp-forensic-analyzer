"""
Health check and monitoring endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import redis

from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import HealthCheckResponse

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint

    Checks:
    - API is responding
    - Database connection
    - Redis connection (if available)

    Returns:
        Health status information
    """
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Check database
    try:
        db.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"] = f"disconnected: {str(e)}"

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["redis"] = f"disconnected: {str(e)}"

    return health_status


@router.get("/health/live")
async def liveness():
    """
    Kubernetes liveness probe
    Returns 200 if API is running
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe
    Returns 200 if API is ready to serve requests
    """
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}, 503
