from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MessageRead(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    read_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WSMessageIn(BaseModel):
    type: Literal["message"]
    conversation_id: int = Field(..., gt=0)
    content: str = Field(..., min_length=1, max_length=2000)


class WSMessageOut(BaseModel):
    type: Literal["message"] = "message"
    conversation_id: int
    message: MessageRead


class WSReadReceipt(BaseModel):
    type: Literal["read_receipt"] = "read_receipt"
    conversation_id: int
    reader_id: int
    read_at: datetime


class WSError(BaseModel):
    type: Literal["error"] = "error"
    code: str
    message: str
