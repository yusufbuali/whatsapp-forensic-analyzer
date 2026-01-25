"""
Application configuration using Pydantic Settings
Resolves all configuration conflicts from CONFIG_MASTER.md
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    """
    Application settings with validation
    All settings can be overridden by environment variables
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    APP_NAME: str = "WhatsApp Forensic Analyzer"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True

    # Security Keys
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64))
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64))
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 8

    # ============================================================================
    # DATABASE CONFIGURATION (STANDARD: forensic_wa)
    # ============================================================================
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = Field(default="forensic_wa", frozen=True)  # DO NOT CHANGE
    DATABASE_USER: str = "forensic_user"
    DATABASE_PASSWORD: str = "forensic_password_change_me"

    # Connection pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection URL"""
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Construct async PostgreSQL connection URL"""
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    # ============================================================================
    # REDIS CONFIGURATION
    # ============================================================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis connection URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ============================================================================
    # CELERY CONFIGURATION
    # ============================================================================
    @property
    def CELERY_BROKER_URL(self) -> str:
        """Celery broker (Redis)"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Celery result backend (Redis)"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/1"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    # ============================================================================
    # API CONFIGURATION (STANDARD: 8000)
    # ============================================================================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = Field(default=8000, frozen=True)  # DO NOT CHANGE
    API_BASE_PATH: str = "/api"
    API_DOCS_URL: str = "/docs"
    API_REDOC_URL: str = "/redoc"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    LOGIN_RATE_LIMIT_PER_15MIN: int = 5

    # ============================================================================
    # FILE STORAGE CONFIGURATION
    # ============================================================================
    UPLOAD_DIR: str = "./uploads"
    EVIDENCE_DIR: str = "./uploads/evidence"
    WORKING_DIR: str = "./uploads/working"
    MAX_UPLOAD_SIZE_MB: int = 2048
    ALLOWED_EXTENSIONS: List[str] = [
        ".sqlite",
        ".db",
        ".crypt14",
        ".jpg",
        ".jpeg",
        ".png",
        ".mp4",
        ".mp3",
        ".pdf",
        ".opus",
        ".m4a",
    ]

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        """Convert MB to bytes"""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # ============================================================================
    # AUTHENTICATION CONFIGURATION
    # ============================================================================
    # Password Requirements
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # Session Configuration
    SESSION_TIMEOUT_HOURS: int = 8
    REFRESH_TOKEN_EXPIRY_DAYS: int = 30

    # First Admin User (Created on first run)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "ChangeThisSecurePassword123!"
    ADMIN_EMAIL: str = "admin@forensics.local"
    ADMIN_FULL_NAME: str = "System Administrator"

    # ============================================================================
    # AI MODEL CONFIGURATION
    # ============================================================================
    # Local AI (Default - works offline)
    USE_LOCAL_AI: bool = True
    WHISPER_MODEL: str = Field(default="base", pattern="^(tiny|base|small|medium|large)$")
    WHISPER_DEVICE: str = Field(default="cpu", pattern="^(cpu|cuda)$")
    SPACY_MODEL: str = "en_core_web_trf"

    # Optional: Cloud AI (requires internet)
    USE_CLOUD_AI: bool = False
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 2000

    # PII Detection
    PII_CONFIDENCE_THRESHOLD: float = Field(default=0.65, ge=0.0, le=1.0)
    PII_VERIFY_WITH_HUMAN: bool = True
    AI_REVIEW_THRESHOLD: float = Field(default=0.80, ge=0.0, le=1.0)

    @field_validator("PII_CONFIDENCE_THRESHOLD", "AI_REVIEW_THRESHOLD")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v

    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = "json"
    LOG_DIR: str = "./logs"
    LOG_ROTATION_DAYS: int = 30

    # Audit Logging
    AUDIT_LOG_RETENTION_YEARS: int = 5

    # ============================================================================
    # BACKUP CONFIGURATION
    # ============================================================================
    BACKUP_ENABLED: bool = True
    BACKUP_DIR: str = "./backups"
    BACKUP_SCHEDULE_CRON: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30

    # Backup Method
    DB_BACKUP_FORMAT: str = "custom"
    EVIDENCE_BACKUP_METHOD: str = "rsync"

    # ============================================================================
    # SECURITY CONFIGURATION
    # ============================================================================
    # HTTPS (Production only)
    USE_HTTPS: bool = False
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None

    # Security Headers
    ENABLE_HSTS: bool = True
    HSTS_MAX_AGE: int = 31536000

    # ============================================================================
    # MONITORING & HEALTH CHECKS
    # ============================================================================
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL_SECONDS: int = 30

    # ============================================================================
    # FORENSIC SETTINGS
    # ============================================================================
    # Chain of Custody
    ENABLE_CHAIN_OF_CUSTODY: bool = True
    REQUIRE_EXAMINER_SIGNATURE: bool = False
    LAB_ACCREDITATION_INFO: str = "Forensic Analysis Laboratory"

    # Evidence Verification
    VERIFY_HASH_ON_UPLOAD: bool = True
    VERIFY_HASH_BEFORE_PROCESSING: bool = True
    HASH_ALGORITHM: str = "sha256"

    # Report Generation
    REPORT_INCLUDE_METADATA: bool = True
    REPORT_INCLUDE_CHAIN_OF_CUSTODY: bool = True
    REPORT_WATERMARK: str = "FORENSIC EVIDENCE - CONFIDENTIAL"

    # ============================================================================
    # DEVELOPMENT SETTINGS
    # ============================================================================
    RELOAD_ON_CHANGE: bool = False
    ENABLE_PROFILER: bool = False
    ENABLE_QUERY_LOGGING: bool = False
    TEST_MODE: bool = False

    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"

    def get_log_config(self) -> dict:
        """Get logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json" if self.LOG_FORMAT == "json" else "default",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "json" if self.LOG_FORMAT == "json" else "default",
                    "filename": f"{self.LOG_DIR}/app.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": self.LOG_ROTATION_DAYS,
                },
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console", "file"],
            },
            "loggers": {
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "sqlalchemy": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of warnings"""
        warnings = []

        # Check for default passwords
        if "change" in self.DATABASE_PASSWORD.lower():
            warnings.append("Database password is still default - change in production")

        if "change" in self.ADMIN_PASSWORD.lower():
            warnings.append("Admin password is still default - change immediately")

        # Check for weak secrets
        if len(self.SECRET_KEY) < 32:
            warnings.append("SECRET_KEY is too short - should be at least 64 characters")

        if len(self.JWT_SECRET_KEY) < 32:
            warnings.append("JWT_SECRET_KEY is too short - should be at least 64 characters")

        # Production checks
        if self.is_production():
            if self.DEBUG:
                warnings.append("DEBUG should be False in production")

            if not self.USE_HTTPS:
                warnings.append("HTTPS should be enabled in production")

            if "localhost" in self.CORS_ORIGINS:
                warnings.append("Remove localhost from CORS_ORIGINS in production")

        return warnings


# Create global settings instance
settings = Settings()

# Validate on startup
config_warnings = settings.validate_config()
if config_warnings:
    import warnings as py_warnings

    for warning in config_warnings:
        py_warnings.warn(f"Configuration Warning: {warning}", UserWarning)
