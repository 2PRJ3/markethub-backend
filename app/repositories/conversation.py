from sqlalchemy import and_, case, desc, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, db: Session):
        super().__init__(Conversation, db)

    def get_by_pair(self, user_a_id: int, user_b_id: int) -> Conversation | None:
        low, high = sorted((user_a_id, user_b_id))
        stmt = select(Conversation).where(
            Conversation.user_one_id == low,
            Conversation.user_two_id == high,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def user_is_participant(self, conversation_id: int, user_id: int) -> bool:
        stmt = select(Conversation.id).where(
            Conversation.id == conversation_id,
            or_(
                Conversation.user_one_id == user_id,
                Conversation.user_two_id == user_id,
            ),
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def list_for_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[tuple[Conversation, User, Message | None, int]]:
        last_msg_subq = (
            select(
                Message.conversation_id,
                func.max(Message.created_at).label("max_created_at"),
            )
            .group_by(Message.conversation_id)
            .subquery()
        )

        LastMessage = aliased(Message)

        unread_subq = (
            select(
                Message.conversation_id,
                func.count(Message.id).label("unread_count"),
            )
            .where(
                Message.sender_id != user_id,
                Message.read_at.is_(None),
            )
            .group_by(Message.conversation_id)
            .subquery()
        )

        other_user_id = case(
            (Conversation.user_one_id == user_id, Conversation.user_two_id),
            else_=Conversation.user_one_id,
        )

        stmt = (
            select(
                Conversation,
                User,
                LastMessage,
                func.coalesce(unread_subq.c.unread_count, 0),
            )
            .join(User, User.id == other_user_id)
            .outerjoin(
                last_msg_subq,
                last_msg_subq.c.conversation_id == Conversation.id,
            )
            .outerjoin(
                LastMessage,
                and_(
                    LastMessage.conversation_id == Conversation.id,
                    LastMessage.created_at == last_msg_subq.c.max_created_at,
                ),
            )
            .outerjoin(
                unread_subq,
                unread_subq.c.conversation_id == Conversation.id,
            )
            .where(
                or_(
                    Conversation.user_one_id == user_id,
                    Conversation.user_two_id == user_id,
                )
            )
            .order_by(desc(Conversation.last_message_at).nulls_last())
            .offset(skip)
            .limit(limit)
        )

        return list(self.db.execute(stmt).all())

    def count_for_user(self, user_id: int) -> int:
        stmt = select(func.count(Conversation.id)).where(
            or_(
                Conversation.user_one_id == user_id,
                Conversation.user_two_id == user_id,
            )
        )
        return self.db.execute(stmt).scalar_one()
