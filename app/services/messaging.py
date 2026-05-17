from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenActionError, NotFoundError
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.repositories.user import UserRepository


class MessagingService:
    def __init__(self, db: Session):
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.msg_repo = MessageRepository(db)
        self.user_repo = UserRepository(db)

    # --- Conversations ---

    def get_or_create_conversation(self, current_user_id: int, recipient_id: int) -> Conversation:
        if current_user_id == recipient_id:
            raise ForbiddenActionError("Impossible de créer une conversation avec soi-même.")

        recipient = self.user_repo.get_by_id(recipient_id)
        if recipient is None or not recipient.is_active:
            raise NotFoundError("Utilisateur introuvable.")

        existing = self.conv_repo.get_by_pair(current_user_id, recipient_id)
        if existing is not None:
            return existing

        low, high = sorted((current_user_id, recipient_id))
        new_conv = Conversation(user_one_id=low, user_two_id=high)

        try:
            created = self.conv_repo.create(new_conv)
            self.db.commit()
            self.db.refresh(created)
            return created
        except IntegrityError:
            self.db.rollback()
            existing = self.conv_repo.get_by_pair(current_user_id, recipient_id)
            if existing is None:
                raise
            return existing

    def list_conversations(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[tuple[Conversation, User, Message | None, int]], int]:
        rows = self.conv_repo.list_for_user(user_id, skip=skip, limit=limit)
        total = self.conv_repo.count_for_user(user_id)
        return rows, total

    def get_conversation(self, conversation_id: int, current_user_id: int) -> Conversation:
        return self._ensure_participant(conversation_id, current_user_id)

    def _ensure_participant(self, conversation_id: int, user_id: int) -> Conversation:
        conv = self.conv_repo.get_by_id(conversation_id)
        if conv is None:
            raise NotFoundError("Conversation introuvable.")
        if user_id not in (conv.user_one_id, conv.user_two_id):
            raise ForbiddenActionError("Accès à la conversation refusé.")
        return conv

    # --- Messages ---

    def list_messages(
        self,
        conversation_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Message], int]:
        self._ensure_participant(conversation_id, current_user_id)

        messages = self.msg_repo.list_by_conversation(conversation_id, skip=skip, limit=limit)
        total = self.msg_repo.count_by_conversation(conversation_id)
        return messages, total

    def send_message(
        self,
        conversation_id: int,
        sender_id: int,
        content: str,
    ) -> tuple[Message, int]:

        conv = self._ensure_participant(conversation_id, sender_id)

        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
        )
        created = self.msg_repo.create(message)

        self.conv_repo.update(conv, {"last_message_at": created.created_at})

        self.db.commit()
        self.db.refresh(created)

        recipient_id = conv.user_two_id if sender_id == conv.user_one_id else conv.user_one_id
        return created, recipient_id

    def mark_conversation_as_read(
        self, conversation_id: int, reader_id: int
    ) -> tuple[datetime | None, int]:

        conv = self._ensure_participant(conversation_id, reader_id)

        read_at = self.msg_repo.mark_as_read(conversation_id, reader_id)
        self.db.commit()

        other_user_id = conv.user_two_id if reader_id == conv.user_one_id else conv.user_one_id
        return read_at, other_user_id
