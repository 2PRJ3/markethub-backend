from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.order_item import OrderItem
    from app.models.service import Service
    from app.models.user import User


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating_range"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)

    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    order_item: Mapped["OrderItem"] = relationship(foreign_keys=[order_item_id])
    buyer: Mapped["User"] = relationship(foreign_keys=[buyer_id], lazy="joined")
    service: Mapped["Service"] = relationship(foreign_keys=[service_id], back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review id={self.id} service_id={self.service_id} buyer_id={self.buyer_id} rating={self.rating}>"
