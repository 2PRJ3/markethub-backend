from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self, db: Session):
        super().__init__(Message, db)

    def list_by_conversation(
        self, conversation_id: int, skip: int = 0, limit: int = 50
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_by_conversation(self, conversation_id: int) -> int:
        stmt = select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
        return self.db.execute(stmt).scalar_one()

    def mark_as_read(self, conversation_id: int, reader_id: int) -> datetime | None:
        now = datetime.now(UTC)
        stmt = (
            update(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.sender_id != reader_id,
                Message.read_at.is_(None),
            )
            .values(read_at=now)
        )
        result = self.db.execute(stmt)
        return now if result.rowcount > 0 else None
