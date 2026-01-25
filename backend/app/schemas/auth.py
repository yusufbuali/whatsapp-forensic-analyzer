"""
Authentication and user management schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID

from app.core.security import validate_password_strength


class UserLogin(BaseModel):
    """Login request schema"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    model_config = {
        "json_schema_extra": {
            "examples": [{"username": "examiner1", "password": "SecurePass123!"}]
        }
    }


class UserCreate(BaseModel):
    """Create user request schema"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., pattern="^(admin|examiner|viewer)$")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.lower()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "examiner1",
                    "email": "examiner@forensics.local",
                    "password": "SecurePass123!",
                    "full_name": "John Doe",
                    "role": "examiner",
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    """Update user request schema"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, pattern="^(admin|examiner|viewer)$")
    is_active: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "examples": [{"email": "newemail@forensics.local", "full_name": "Jane Smith"}]
        }
    }


class PasswordChange(BaseModel):
    """Change password request schema"""

    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class UserResponse(BaseModel):
    """User response schema"""

    id: UUID
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token response schema"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # Seconds until expiration
    user: UserResponse

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 28800,
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "examiner1",
                        "email": "examiner@forensics.local",
                        "full_name": "John Doe",
                        "role": "examiner",
                        "is_active": True,
                        "is_verified": True,
                        "created_at": "2026-01-21T10:00:00Z",
                        "last_login": "2026-01-21T12:00:00Z",
                    },
                }
            ]
        }
    }


class TokenData(BaseModel):
    """Token payload data"""

    sub: str  # Subject (user ID)
    username: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None


class TokenRefresh(BaseModel):
    """Refresh token request schema"""

    refresh_token: str


class UserListResponse(BaseModel):
    """User list response schema"""

    users: list[UserResponse]
    total: int
    page: int
    page_size: int


class LoginHistoryResponse(BaseModel):
    """Login history entry"""

    session_id: UUID
    login_time: datetime
    ip_address: str
    user_agent: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}
