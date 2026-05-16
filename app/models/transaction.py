from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy import Enum as SEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.order import Order
from app.models.user import User
from app.utils.enums import PaymentFailureReason, TransactionStatus, TransactionType


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    type: Mapped[TransactionType] = mapped_column(
        SEnum(TransactionType, name="transaction_type", native_enum=False), nullable=False
    )
    status: Mapped[TransactionStatus] = mapped_column(
        SEnum(TransactionStatus, name="transaction_status", native_enum=False),
        default=TransactionStatus.PENDING,
        nullable=False,
    )

    reference: Mapped[str] = mapped_column(String(64), nullable=False)

    idempotency_key: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    failure_reason: Mapped[PaymentFailureReason | None] = mapped_column(
        SEnum(PaymentFailureReason, name="payment_failure_reason", native_enum=False), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="transactions")
    user: Mapped["User"] = relationship()

    __table_args__ = (
        Index(
            "ix_transactions_user_idempotency",
            "user_id",
            "idempotency_key",
            unique=True,
            postgresql_where="idempotency_key IS NOT NULL",
        ),
    )
