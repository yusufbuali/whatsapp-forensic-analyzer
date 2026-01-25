"""
Case management schemas
"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field
from uuid import UUID


class CaseCreate(BaseModel):
    """Create case request schema"""

    case_number: str = Field(..., min_length=1, max_length=50, pattern=r"^[A-Z0-9\-]+$")
    case_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    device_type: str = Field(..., pattern="^(iOS|Android|Unknown)$")
    device_model: Optional[str] = None
    device_serial: Optional[str] = None
    device_owner: Optional[str] = None
    examiner_name: str = Field(..., min_length=1, max_length=100)
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")

    # Legal fields
    case_officer: Optional[str] = None
    warrant_number: Optional[str] = None
    court_order_date: Optional[date] = None
    legal_authority: Optional[str] = None

    # Chain of custody
    acquisition_date: Optional[datetime] = None
    acquisition_location: Optional[str] = None
    acquisition_method: Optional[str] = None

    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CaseUpdate(BaseModel):
    """Update case request schema"""

    case_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(
        None, pattern="^(created|uploaded|processing|analyzed|completed|archived)$"
    )
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CaseResponse(BaseModel):
    """Case response schema"""

    id: UUID
    case_number: str
    case_name: str
    description: Optional[str] = None
    device_type: str
    device_model: Optional[str] = None
    examiner_id: UUID
    examiner_name: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
