"""
Pydantic schemas for request/response validation
"""

from .auth import (
    UserLogin,
    UserCreate,
    UserUpdate,
    UserResponse,
    Token,
    TokenData,
    PasswordChange,
)
from .case import CaseCreate, CaseUpdate, CaseResponse
from .message import MessageResponse
from .common import SuccessResponse, ErrorResponse, PaginatedResponse

__all__ = [
    # Auth
    "UserLogin",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    "PasswordChange",
    # Case
    "CaseCreate",
    "CaseUpdate",
    "CaseResponse",
    # Message
    "MessageResponse",
    # Common
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
]
