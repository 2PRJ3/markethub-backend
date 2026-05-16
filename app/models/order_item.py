from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin
from app.utils.enums import OrderItemStatus

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.service import Service
    from app.models.user import User


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    status: Mapped[OrderItemStatus] = mapped_column(
        SQLEnum(
            OrderItemStatus,
            name="order_item_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=OrderItemStatus.PENDING,
        server_default=OrderItemStatus.PENDING.value,
        nullable=False,
    )

    order: Mapped["Order"] = relationship(back_populates="items", foreign_keys=[order_id])

    service: Mapped["Service"] = relationship(foreign_keys=[service_id], lazy="joined")

    seller: Mapped["User"] = relationship(foreign_keys=[seller_id], lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<OrderItem id={self.id} order_id={self.order_id} "
            f"service_id={self.service_id} status={self.status.value}>"
        )
