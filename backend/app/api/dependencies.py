"""
FastAPI dependencies for authentication and authorization
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token

    Usage:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials

    # Verify session and get user
    user = AuthService.verify_session(db, token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get current active user
    Redundant with get_current_user but kept for clarity
    """
    return current_user


async def require_role(required_role: str):
    """
    Dependency factory to require specific role

    Usage:
        @app.get("/admin-only")
        def admin_route(current_user: User = Depends(require_role("admin"))):
            return {"message": "Admin access"}
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )
        return current_user

    return role_checker


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def require_examiner(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require examiner role (or admin)"""
    if not current_user.is_examiner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Examiner privileges required",
        )
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to optionally get current user
    Returns None if no token provided or token invalid

    Usage:
        @app.get("/public-or-private")
        def route(user: Optional[User] = Depends(get_optional_current_user)):
            if user:
                return {"message": f"Hello {user.username}"}
            return {"message": "Hello guest"}
    """
    if not credentials:
        return None

    token = credentials.credentials
    user = AuthService.verify_session(db, token)

    return user if user and user.is_active else None
