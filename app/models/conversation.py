from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.user import User


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_one_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_two_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user_one: Mapped["User"] = relationship(
        foreign_keys=[user_one_id],
        back_populates="conversations_as_user_one",
    )
    user_two: Mapped["User"] = relationship(
        foreign_keys=[user_two_id],
        back_populates="conversations_as_user_two",
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    __table_args__ = (
        CheckConstraint(
            "user_one_id < user_two_id",
            name="ck_conversations_user_order",
        ),
        UniqueConstraint(
            "user_one_id",
            "user_two_id",
            name="uq_conversations_pair",
        ),
        Index("ix_conversations_last_message_at", "last_message_at"),
    )
