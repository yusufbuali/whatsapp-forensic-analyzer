"""
Message and chat schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class MessageResponse(BaseModel):
    """Message response schema"""

    id: UUID
    case_id: UUID
    chat_session_id: UUID
    sender_jid: Optional[str] = None
    sender_name: Optional[str] = None
    message_text: Optional[str] = None
    message_type: str
    timestamp: datetime
    is_from_me: bool
    is_deleted: bool

    model_config = {"from_attributes": True}
