from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.enums import UserRole

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.message import Message
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.service import Service
from app.models.mixins import SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
    bio: Mapped[str | None] = mapped_column(String(1000), nullable=True, default=None)
    university: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    study_sector: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.USER,
        server_default=UserRole.USER.value,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    is_suspended: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    services: Mapped[list["Service"]] = relationship(
        back_populates="seller",
        foreign_keys="Service.seller_id",
        passive_deletes=True,
    )
    orders: Mapped[list["Order"]] = relationship(
        foreign_keys="Order.buyer_id", back_populates=None, passive_deletes=True
    )

    sales: Mapped[list["OrderItem"]] = relationship(
        foreign_keys="OrderItem.seller_id", passive_deletes=True
    )
    conversations_as_user_one: Mapped[list["Conversation"]] = relationship(
        foreign_keys="Conversation.user_one_id",
        back_populates="user_one",
        cascade="all, delete-orphan",
    )
    conversations_as_user_two: Mapped[list["Conversation"]] = relationship(
        foreign_keys="Conversation.user_two_id",
        back_populates="user_two",
        cascade="all, delete-orphan",
    )
    sent_messages: Mapped[list["Message"]] = relationship(
        foreign_keys="Message.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role.value}>"
