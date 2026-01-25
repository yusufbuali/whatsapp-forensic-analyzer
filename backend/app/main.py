"""
WhatsApp Forensic Analyzer - Main FastAPI Application
Version: 1.0.0
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime

from app.core.config import settings
from app.core.database import check_db_connection
from app.api import auth, health
from app.middleware.audit import AuditLogMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Runs on startup and shutdown
    """
    # Startup
    logger.info("=" * 80)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_NAME}")
    logger.info(f"API Port: {settings.API_PORT}")
    logger.info("=" * 80)

    # Check database connection
    if check_db_connection():
        logger.info("✓ Database connection successful")
    else:
        logger.error("✗ Database connection failed")

    # Display configuration warnings
    warnings = settings.validate_config()
    if warnings:
        logger.warning("Configuration Warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")

    logger.info(f"Application started at {datetime.now()}")
    logger.info(f"API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive forensic analysis tool for WhatsApp chat databases with AI-powered verification",
    docs_url=settings.API_DOCS_URL,
    redoc_url=settings.API_REDOC_URL,
    lifespan=lifespan,
    # Swagger UI configuration
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas section
        "persistAuthorization": True,  # Remember auth token
    },
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Audit logging middleware (custom)
app.add_middleware(AuditLogMiddleware)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler for 404 Not Found errors"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": "Not found",
            "detail": f"Resource not found: {request.url.path}",
        },
    )


# ============================================================================
# ROUTERS
# ============================================================================

# Include API routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix=settings.API_BASE_PATH, tags=["Authentication"])

# TODO: Add more routers as they're implemented
# app.include_router(cases.router, prefix=settings.API_BASE_PATH, tags=["Cases"])
# app.include_router(messages.router, prefix=settings.API_BASE_PATH, tags=["Messages"])
# app.include_router(reports.router, prefix=settings.API_BASE_PATH, tags=["Reports"])


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "operational",
        "documentation": f"/docs",
        "redoc": f"/redoc",
        "health": f"/health",
    }


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.RELOAD_ON_CHANGE if settings.is_development() else False,
        log_level=settings.LOG_LEVEL.lower(),
    )
