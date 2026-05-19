from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.ws_manager import manager
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationListItem,
    ConversationParticipant,
    ConversationRead,
)
from app.schemas.message import MessageRead, WSReadReceipt
from app.services.messaging import MessagingService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationRead, status_code=status.HTTP_200_OK)
def create_or_get_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationRead:

    service = MessagingService(db)
    conversation = service.get_or_create_conversation(
        current_user_id=current_user.id,
        recipient_id=payload.recipient_id,
    )
    return ConversationRead.model_validate(conversation)


@router.get("", response_model=list[ConversationListItem])
def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConversationListItem]:
    service = MessagingService(db)
    rows, _total = service.list_conversations(user_id=current_user.id, skip=skip, limit=limit)

    return [
        ConversationListItem(
            id=conv.id,
            other_user=ConversationParticipant.model_validate(other_user),
            last_message_content=last_msg.content if last_msg else None,
            last_message_at=conv.last_message_at,
            unread_count=unread,
            created_at=conv.created_at,
        )
        for conv, other_user, last_msg, unread in rows
    ]


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationRead:

    service = MessagingService(db)
    conversation = service.get_conversation(
        conversation_id=conversation_id,
        current_user_id=current_user.id,
    )
    return ConversationRead.model_validate(conversation)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def list_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageRead]:
    service = MessagingService(db)
    messages, _total = service.list_messages(
        conversation_id=conversation_id,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return [MessageRead.model_validate(m) for m in messages]


@router.post("/{conversation_id}/read", status_code=status.HTTP_204_NO_CONTENT, summary="")
async def mark_as_read(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service = MessagingService(db)
    service.mark_conversation_as_read(conversation_id=conversation_id, reader_id=current_user.id)
    service = MessagingService(db)
    read_at, other_user_id = service.mark_conversation_as_read(
        conversation_id=conversation_id, reader_id=current_user.id
    )
    if read_at is not None:
        receipt = WSReadReceipt(
            conversation_id=conversation_id,
            reader_id=current_user.id,
            read_at=read_at,
        )
        await manager.send_to_user(other_user_id, receipt)
    return None
