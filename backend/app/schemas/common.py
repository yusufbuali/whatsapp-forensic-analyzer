"""
Common schemas used across the application
"""

from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Standard success response"""

    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = False
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = "healthy"
    database: str = "connected"
    redis: str = "connected"
    version: str
    timestamp: str


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""

    items: List[T]
    total: int
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        """Helper method to create paginated response"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
        )
