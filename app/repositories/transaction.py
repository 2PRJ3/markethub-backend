from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository
from app.utils.enums import PaymentFailureReason, TransactionStatus


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(Transaction, db)

    def get_by_reference(self, reference: str) -> Transaction | None:
        stmt = select(Transaction).where(Transaction.reference == reference)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_idempotency_key(self, user_id: int, key: UUID) -> Transaction | None:
        stmt = select(Transaction).where(
            Transaction.user_id == user_id, Transaction.idempotency_key == key
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(desc(Transaction.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_by_user(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(Transaction).where(Transaction.user_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def list_by_order(self, order_id: int) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.order_id == order_id)
            .order_by(desc(Transaction.created_at))
        )
        return list(self.db.execute(stmt).scalars().all())

    def mark_success(self, transaction: Transaction) -> Transaction:
        transaction.status = TransactionStatus.SUCCESS
        self.db.flush()
        self.db.refresh(transaction)
        return transaction

    def mark_failed(self, transaction: Transaction, reason: PaymentFailureReason) -> Transaction:
        transaction.status = TransactionStatus.FAILED
        self.db.flush()
        self.db.refresh(transaction)
        return transaction
