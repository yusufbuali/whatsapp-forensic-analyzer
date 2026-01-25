"""
Security utilities: password hashing, JWT tokens, authentication
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import re

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# PASSWORD UTILITIES
# ============================================================================


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password meets security requirements

    Args:
        password: Password to validate

    Returns:
        (is_valid, error_message)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long"

    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if settings.PASSWORD_REQUIRE_DIGITS and not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, None


# ============================================================================
# JWT TOKEN UTILITIES
# ============================================================================


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token

    Args:
        data: Payload data to encode in token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": settings.APP_NAME,
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token

    Args:
        user_id: User ID to encode in token

    Returns:
        Encoded JWT refresh token
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS)
    data = {"sub": str(user_id), "type": "refresh"}
    return create_access_token(data, expires_delta)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token to verify

    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verification (for debugging)

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload
    """
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": False},
        )
    except JWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token

    Args:
        token: JWT token

    Returns:
        User ID if valid, None otherwise
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def is_token_expired(token: str) -> bool:
    """
    Check if a JWT token is expired

    Args:
        token: JWT token to check

    Returns:
        True if expired, False otherwise
    """
    payload = decode_token(token)
    if not payload:
        return True

    exp = payload.get("exp")
    if not exp:
        return True

    return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)


# ============================================================================
# API KEY GENERATION (for service accounts or external integrations)
# ============================================================================


def generate_api_key() -> str:
    """
    Generate a secure random API key

    Returns:
        Random API key
    """
    import secrets

    return secrets.token_urlsafe(32)


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================


def create_session_token() -> str:
    """
    Create a unique session token

    Returns:
        Random session token
    """
    import secrets

    return secrets.token_urlsafe(64)


def validate_session_timeout(last_activity: datetime) -> bool:
    """
    Check if session has timed out

    Args:
        last_activity: Last activity timestamp

    Returns:
        True if session is still valid, False if timed out
    """
    timeout_delta = timedelta(hours=settings.SESSION_TIMEOUT_HOURS)
    return datetime.now(timezone.utc) - last_activity < timeout_delta


# ============================================================================
# FORENSIC SECURITY (Evidence Integrity)
# ============================================================================


def compute_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Compute hash of a file for integrity verification

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hex digest of file hash
    """
    import hashlib

    hash_func = getattr(hashlib, algorithm)()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def compute_file_hashes(file_path: str) -> dict[str, str]:
    """
    Compute both SHA256 and MD5 hashes of a file for forensic compliance

    Per claude.md requirements, forensic evidence must have both hashes
    for maximum compatibility with legacy tools.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with 'sha256' and 'md5' keys
    """
    import hashlib

    sha256_hash = hashlib.sha256()
    md5_hash = hashlib.md5()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256_hash.update(chunk)
            md5_hash.update(chunk)

    return {
        "sha256": sha256_hash.hexdigest(),
        "md5": md5_hash.hexdigest(),
    }


def verify_file_hash(file_path: str, expected_hash: str, algorithm: str = "sha256") -> bool:
    """
    Verify file integrity by comparing hashes

    Args:
        file_path: Path to file
        expected_hash: Expected hash value
        algorithm: Hash algorithm used

    Returns:
        True if hashes match, False otherwise
    """
    actual_hash = compute_file_hash(file_path, algorithm)
    return actual_hash.lower() == expected_hash.lower()


# ============================================================================
# SANITIZATION (prevent injection attacks)
# ============================================================================


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import os
    from pathlib import Path

    # Remove path separators and null bytes
    filename = filename.replace("\0", "")
    filename = os.path.basename(filename)

    # Remove any remaining suspicious characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"

    return filename


def sanitize_case_number(case_number: str) -> str:
    """
    Sanitize case number to prevent injection

    Args:
        case_number: Original case number

    Returns:
        Sanitized case number
    """
    # Only allow alphanumeric, hyphens, and underscores
    return re.sub(r"[^A-Z0-9\-_]", "", case_number.upper())


# ============================================================================
# RATE LIMITING (prevent brute force)
# ============================================================================

# Redis-based rate limiter for production (defined in rate_limiter.py)
# Provides persistence across restarts and consistency across multiple instances
from .rate_limiter import login_rate_limiter

__all__ = [
    "get_password_hash",
    "verify_password",
    "validate_password_strength",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "extract_user_id_from_token",
    "is_token_expired",
    "generate_api_key",
    "create_session_token",
    "validate_session_timeout",
    "compute_file_hash",
    "compute_file_hashes",
    "verify_file_hash",
    "sanitize_filename",
    "sanitize_case_number",
    "login_rate_limiter",
]
