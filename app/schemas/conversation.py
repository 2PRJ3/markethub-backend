from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    recipient_id: int = Field(..., gt=0)


class ConversationParticipant(BaseModel):
    id: int
    first_name: str
    last_name: str
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class ConversationRead(BaseModel):
    id: int
    user_one_id: int
    user_two_id: int
    last_message_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationListItem(BaseModel):
    id: int
    other_user: ConversationParticipant
    last_message_content: str | None = None
    last_message_at: datetime | None = None
    unread_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
