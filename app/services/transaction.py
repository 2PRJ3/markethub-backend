from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ForbiddenActionError,
    NotFoundError,
    OrderAlreadyPaidError,
    OrderNotPayableError,
    PaymentAmountMismatchError,
    PaymentDeclinedError,
    UserSuspendedError,
)
from app.models.order import Order
from app.models.transaction import Transaction
from app.repositories.order import OrderRepository
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.schemas.transaction import PaymentRequest
from app.services.payment_simulator import simulate_payment
from app.utils.enums import OrderStatus, TransactionStatus, TransactionType


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.user_repo = UserRepository(db)

    def pay_order(
        self, order_id: int, user_id: int, payment: PaymentRequest, idempotency_key: UUID | None
    ) -> tuple[Transaction, Order]:
        if idempotency_key is not None:
            verify_idempotency = self.transaction_repo.get_by_idempotency_key(
                user_id, idempotency_key
            )
            if verify_idempotency is not None:
                order = self.order_repo.get_by_id(verify_idempotency.order_id)
                return verify_idempotency, order

        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Utilisateur introuvable")
        if user.is_suspended:
            raise UserSuspendedError("Votre compte est suspendu")

        order = self.order_repo.get_with_items(order_id)
        if order is None:
            raise NotFoundError("Commande introuvable")

        if order.buyer_id != user_id:
            raise ForbiddenActionError("Vous ne pouvez pas payer cette commande")

        if order.status in (OrderStatus.PAID, OrderStatus.COMPLETED):
            raise OrderAlreadyPaidError("Cette commande a déjà été payé")

        if order.status != OrderStatus.PENDING:
            raise OrderNotPayableError("Cette commande ne peut être payée dans état actuel")

        items_total = sum((item.unit_price for item in order.items), start=0)

        if items_total != order.total_amount:
            raise PaymentAmountMismatchError("Incohérence déctectée sur le montant de la commande")

        transaction = Transaction(
            order_id=order.id,
            user_id=user_id,
            amount=order.total_amount,
            type=TransactionType.PAYMENT,
            status=TransactionStatus.PENDING,
            reference=f"txn_{uuid4().hex}",
            idempotency_key=idempotency_key,
        )
        self.transaction_repo.create(transaction)

        failure = simulate_payment(payment.card_number)

        if failure is not None:
            self.transaction_repo.mark_failed(transaction, failure)
            self.db.commit()
            raise PaymentDeclinedError(reason=failure, transaction_id=transaction.id)

        self.transaction_repo.mark_success(transaction)
        self.order_repo.update_status(order, OrderStatus.PAID)
        self.db.commit()

        return transaction, order

    def get_transaction(self, transaction_id: int, user_id: int) -> Transaction:
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if transaction is None or transaction.user_id != user_id:
            raise NotFoundError("Transaction introuvable")
        return transaction

    def list_user_transaction(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Transaction], int]:
        transactions = self.transaction_repo.list_by_user(user_id, skip=skip, limit=limit)
        total = self.transaction_repo.count_by_user(user_id)
        return transactions, total
