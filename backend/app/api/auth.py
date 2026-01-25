"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from app.core.database import get_db
from app.core.config import settings
from app.schemas.auth import (
    UserLogin,
    UserCreate,
    UserUpdate,
    UserResponse,
    Token,
    PasswordChange,
    TokenRefresh,
    UserListResponse,
)
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthService
from app.api.dependencies import (
    get_current_user,
    require_admin,
    require_examiner,
    security,
)
from app.models.user import User

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Login with username and password

    Returns JWT access token and refresh token

    **Rate Limited**: 5 attempts per 15 minutes per username
    **Account Lock**: Account locked for 30 minutes after 5 failed attempts
    """
    # Get client IP and user agent
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent")

    # Authenticate user
    try:
        user, session = AuthService.authenticate_user(
            db=db,
            username=credentials.username,
            password=credentials.password,
            ip_address=client_ip,
            user_agent=user_agent,
        )
    except HTTPException:
        raise

    # Return token response
    return Token(
        access_token=session.token,
        refresh_token=session.refresh_token,
        token_type="bearer",
        expires_in=int(timedelta(hours=settings.JWT_EXPIRATION_HOURS).total_seconds()),
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout current user

    Revokes the current session token in the database
    """
    # Extract token from Authorization header
    token = credentials.credentials

    # Revoke the session in database
    AuthService.logout(db, token)

    return SuccessResponse(
        success=True,
        message="Successfully logged out",
        data={"username": current_user.username},
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token

    Refresh tokens are valid for 30 days
    """
    try:
        new_access_token, new_refresh_token = AuthService.refresh_access_token(
            db=db, refresh_token=token_data.refresh_token
        )

        # Get user from new token
        from app.core.security import verify_token
        from uuid import UUID

        payload = verify_token(new_access_token)
        user_id = UUID(payload.get("sub"))
        user = AuthService.get_user_by_id(db, user_id)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=int(timedelta(hours=settings.JWT_EXPIRATION_HOURS).total_seconds()),
            user=UserResponse.model_validate(user),
        )
    except HTTPException:
        raise


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information

    Requires valid JWT token in Authorization header
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user information

    Users can only update their own email and full name
    Role changes require admin privileges
    """
    # Prevent non-admins from changing their role
    if user_data.role and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change user roles",
        )

    updated_user = AuthService.update_user(db, current_user.id, user_data)
    return UserResponse.model_validate(updated_user)


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change current user's password

    Requires current password for verification
    """
    try:
        AuthService.change_password(
            db=db,
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )

        return SuccessResponse(
            success=True,
            message="Password changed successfully",
            data={"username": current_user.username},
        )
    except HTTPException:
        raise


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================


@router.post("/users", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new user (Admin only)

    **Required role**: admin

    Password must meet requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    user = AuthService.create_user(db, user_data, created_by_id=current_user.id)
    return UserResponse.model_validate(user)


@router.get("/users", response_model=UserListResponse, dependencies=[Depends(require_admin)])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List all users (Admin only)

    **Required role**: admin

    **Query Parameters**:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 100)
    """
    users, total = AuthService.list_users(db, skip=skip, limit=limit)

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get(
    "/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)]
)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get user by ID (Admin only)

    **Required role**: admin
    """
    from uuid import UUID

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    user = AuthService.get_user_by_id(db, user_uuid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.put(
    "/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)]
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Update user by ID (Admin only)

    **Required role**: admin
    """
    from uuid import UUID

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    updated_user = AuthService.update_user(db, user_uuid, user_data)
    return UserResponse.model_validate(updated_user)


@router.delete(
    "/users/{user_id}",
    response_model=SuccessResponse,
    dependencies=[Depends(require_admin)],
)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Disable user account (Admin only)

    **Required role**: admin

    Note: Users are not actually deleted, just deactivated
    """
    from uuid import UUID

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    # Prevent admin from disabling themselves
    if user_uuid == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account",
        )

    user = AuthService.get_user_by_id(db, user_uuid)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Deactivate user
    AuthService.update_user(db, user_uuid, UserUpdate(is_active=False))

    return SuccessResponse(
        success=True,
        message="User account disabled",
        data={"user_id": str(user_uuid), "username": user.username},
    )
