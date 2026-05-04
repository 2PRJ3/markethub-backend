from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Integer, Numeric, ForeignKey, Enum as SQLEnum, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.enums import ServiceStatus
from app.models.mixins import TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category


class Service(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[ServiceStatus] = mapped_column(
        SQLEnum(ServiceStatus, name="service_status", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ServiceStatus.ACTIVE,
        server_default=ServiceStatus.ACTIVE.value,
        index=True,
    )

    average_rating: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2), nullable=True
    )
    reviews_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )

    seller: Mapped["User"] = relationship(back_populates="services")
    category: Mapped["Category"] = relationship(back_populates="services")

    def __repr__(self) -> str:
        return f"<Service id={self.id} title={self.title} seller_id={self.seller_id}>"