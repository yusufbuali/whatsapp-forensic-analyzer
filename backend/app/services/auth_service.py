"""
Authentication service - handles user authentication and session management
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User, Session as UserSession
from app.schemas.auth import UserCreate, UserLogin, UserUpdate, Token, UserResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    login_rate_limiter,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate, created_by_id: Optional[UUID] = None) -> User:
        """
        Create a new user

        Args:
            db: Database session
            user_data: User creation data
            created_by_id: ID of user creating this user (for audit)

        Returns:
            Created user

        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username exists
        existing_user = db.query(User).filter(User.username == user_data.username.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Check if email exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create user
        try:
            db_user = User(
                username=user_data.username.lower(),
                email=user_data.email,
                password_hash=get_password_hash(user_data.password),
                full_name=user_data.full_name,
                role=user_data.role,
                created_by=created_by_id,
                is_active=True,
                is_verified=True,  # Auto-verify for now
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            logger.info(f"User created: {db_user.username} (ID: {db_user.id})")
            return db_user

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating user",
            )

    @staticmethod
    def authenticate_user(
        db: Session, username: str, password: str, ip_address: str, user_agent: Optional[str] = None
    ) -> Tuple[User, UserSession]:
        """
        Authenticate user with username and password

        Args:
            db: Database session
            username: Username
            password: Password
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Tuple of (User, Session)

        Raises:
            HTTPException: If authentication fails or rate limit exceeded
        """
        # Check rate limit
        is_allowed, remaining = login_rate_limiter.check_rate_limit(
            username, settings.LOGIN_RATE_LIMIT_PER_15MIN, 15
        )

        if not is_allowed:
            logger.warning(f"Rate limit exceeded for user: {username} from IP: {ip_address}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
            )

        # Get user
        user = db.query(User).filter(User.username == username.lower()).first()

        if not user:
            login_rate_limiter.record_attempt(username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked until {user.locked_until}",
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1

            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
                logger.warning(f"Account locked for user: {username}")

            db.commit()
            login_rate_limiter.record_attempt(username)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )

        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)
        login_rate_limiter.reset(username)

        # Create session
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        refresh_token = create_refresh_token(str(user.id))

        # Store session in database
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRY_DAYS
        )

        session = UserSession(
            user_id=user.id,
            token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            refresh_expires_at=refresh_expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        logger.info(f"User authenticated: {user.username} from IP: {ip_address}")
        return user, session

    @staticmethod
    def verify_session(db: Session, token: str) -> Optional[User]:
        """
        Verify a session token and return the user

        Args:
            db: Database session
            token: JWT token

        Returns:
            User if valid, None otherwise
        """
        # Verify JWT token
        payload = verify_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Check if session exists and is valid
        session = (
            db.query(UserSession)
            .filter(UserSession.token == token, UserSession.is_revoked == False)
            .first()
        )

        if not session or not session.is_valid:
            return None

        # Get user
        user = db.query(User).filter(User.id == UUID(user_id)).first()

        if not user or not user.is_active:
            return None

        # Update last activity
        session.last_activity = datetime.now(timezone.utc)
        db.commit()

        return user

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token

        Args:
            db: Database session
            refresh_token: Refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token)

        Raises:
            HTTPException: If refresh token is invalid
        """
        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = payload.get("sub")

        # Check if session exists
        session = (
            db.query(UserSession)
            .filter(UserSession.refresh_token == refresh_token, UserSession.is_revoked == False)
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or revoked",
            )

        # Check if refresh token is expired
        if session.refresh_expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
            )

        # Get user
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )

        # Generate new tokens
        new_access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        new_refresh_token = create_refresh_token(str(user.id))

        # Update session
        session.token = new_access_token
        session.refresh_token = new_refresh_token
        session.expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.JWT_EXPIRATION_HOURS
        )
        session.refresh_expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRY_DAYS
        )
        session.last_activity = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Token refreshed for user: {user.username}")
        return new_access_token, new_refresh_token

    @staticmethod
    def logout(db: Session, token: str) -> bool:
        """
        Logout user by revoking session

        Args:
            db: Database session
            token: Access token

        Returns:
            True if successful
        """
        session = db.query(UserSession).filter(UserSession.token == token).first()

        if session:
            session.is_revoked = True
            db.commit()
            logger.info(f"User logged out: session {session.id}")
            return True

        return False

    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> User:
        """
        Update user information

        Args:
            db: Database session
            user_id: User ID
            user_data: Update data

        Returns:
            Updated user

        Raises:
            HTTPException: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Update fields
        if user_data.email:
            user.email = user_data.email
        if user_data.full_name:
            user.full_name = user_data.full_name
        if user_data.role:
            user.role = user_data.role
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        db.commit()
        db.refresh(user)

        logger.info(f"User updated: {user.username}")
        return user

    @staticmethod
    def change_password(
        db: Session, user_id: UUID, current_password: str, new_password: str
    ) -> bool:
        """
        Change user password

        Args:
            db: Database session
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            True if successful

        Raises:
            HTTPException: If current password is incorrect
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Update password
        user.password_hash = get_password_hash(new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Password changed for user: {user.username}")
        return True

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username.lower()).first()

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100):
        """List all users with pagination"""
        users = db.query(User).offset(skip).limit(limit).all()
        total = db.query(User).count()
        return users, total
