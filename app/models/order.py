from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin
from app.utils.enums import OrderStatus

if TYPE_CHECKING:
    from app.models.order_item import OrderItem
    from app.models.user import User


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    brief: Mapped[str] = mapped_column(Text, nullable=False)

    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_status", values_callable=lambda x: [e.value for e in x]),
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
        index=True,
        nullable=False,
    )

    idempotency_key: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), unique=True, index=True, nullable=False
    )

    buyer: Mapped["User"] = relationship(foreign_keys=[buyer_id], lazy="joined")

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} buyer_id={self.buyer_id} status={self.status.value} total={self.total_amount}>"
