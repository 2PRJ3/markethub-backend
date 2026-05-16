from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ForbiddenActionError,
    IdempotencyConflictError,
    InvalidOrderError,
    InvalidStateTransitionError,
    NotFoundError,
)
from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.order import OrderRepository
from app.repositories.order_item import OrderItemRepository
from app.repositories.service import ServiceRepository
from app.schemas.order import OrderCreate
from app.services.order_state_machine import (
    can_transition_item,
    can_transition_order,
)
from app.utils.enums import OrderItemStatus, OrderStatus, ServiceStatus


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.item_repo = OrderItemRepository(db)
        self.service_repo = ServiceRepository(db)

    def create_order(self, buyer_id: int, payload: OrderCreate) -> Order:
        verify_idempotency = self.order_repo.get_by_idempotency_key(payload.idempotency_key)
        if verify_idempotency is not None:
            if verify_idempotency.buyer_id != buyer_id:
                raise IdempotencyConflictError("Cette clé clé d'idempotence est déjà utilisée")
            return verify_idempotency

        service_ids = [item.service_id for item in payload.items]
        services = self.service_repo.get_many_by_ids(service_ids)
        services_by_id = {s.id: s for s in services}

        missing_ids = set(service_ids) - set(services_by_id.keys())

        if missing_ids:
            raise NotFoundError(f"Services introuvables: {sorted(missing_ids)}")

        for service in services:
            if service.status != ServiceStatus.ACTIVE:
                raise InvalidOrderError("Le service n'est plus disponible")
            if service.seller_id == buyer_id:
                raise InvalidOrderError("Vous ne pouvez pas commander vos propres services")
        total_amount = sum(services_by_id[item.service_id].price for item in payload.items)

        order = Order(
            buyer_id=buyer_id,
            brief=payload.brief,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            idempotency_key=payload.idempotency_key,
            items=[
                OrderItem(
                    service_id=item.service_id,
                    seller_id=services_by_id[item.service_id].seller_id,
                    unit_price=services_by_id[item.service_id].price,
                    status=OrderItemStatus.PENDING,
                )
                for item in payload.items
            ],
        )
        try:
            self.order_repo.create(order)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            verify_idempotency = self.order_repo.get_by_idempotency_key(payload.idempotency_key)
            if verify_idempotency is not None:
                return verify_idempotency
            raise
        return self.order_repo.get_with_items(order.id)

    def get_order(self, order_id: int, user_id: int) -> Order:
        order = self.order_repo.get_with_items(order_id)
        if order is None:
            raise NotFoundError("Commande introuvable")
        is_buyer = order.buyer_id == user_id
        is_seller_of_item = any(item.seller_id == user_id for item in order.items)
        if not (is_buyer or is_seller_of_item):
            raise ForbiddenActionError("Vous ne pouvez pas acceder à cette commande")
        return order

    def list_buyer_orders(
        self, buyer_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[Order], int]:
        orders = self.order_repo.list_by_buyer(buyer_id, skip=skip, limit=limit)
        total = self.order_repo.count_by_buyer(buyer_id)
        return orders, total

    def list_seller_sales(
        self, seller_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[list[OrderItem], int]:
        items = self.order_repo.list_items_by_seller(seller_id, skip=skip, limit=limit)
        total = self.order_repo.count_items_by_seller(seller_id)
        return items, total

    def update_item_status(
        self, item_id: int, user_id: int, new_status: OrderItemStatus
    ) -> OrderItem:
        item = self.item_repo.get_with_relations(item_id)
        if item is None:
            raise NotFoundError("Commande introuvable")
        order = item.order

        if not can_transition_item(item.status, new_status):
            raise InvalidStateTransitionError("Transition non autorisée")

        is_buyer = order.buyer_id == user_id
        is_seller = item.seller_id == user_id
        if not (is_buyer or is_seller):
            raise ForbiddenActionError("Vous n'avez pas accès à cette ligne de commande.")

        self._check_item_transition_authorization(
            current=item.status,
            new=new_status,
            is_buyer=is_buyer,
            is_seller=is_seller,
        )

        if new_status == OrderItemStatus.IN_PROGRESS and order.status != OrderStatus.PAID:
            raise InvalidStateTransitionError(
                "Impossible de démarrer une prestation tant que la commande n'est pas payée."
            )

        self.item_repo.update_status(item, new_status)

        if new_status == OrderItemStatus.COMPLETED:
            self._maybe_complete_order(order)

        self.db.commit()

        return item

    def _check_item_transition_authorization(
        self,
        current: OrderItemStatus,
        new: OrderItemStatus,
        is_buyer: bool,
        is_seller: bool,
    ) -> None:
        seller_only = {
            (OrderItemStatus.PENDING, OrderItemStatus.IN_PROGRESS),
            (OrderItemStatus.IN_PROGRESS, OrderItemStatus.DELIVERED),
        }
        buyer_only = {
            (OrderItemStatus.DELIVERED, OrderItemStatus.COMPLETED),
        }

        if (current, new) in seller_only and not is_seller:
            raise ForbiddenActionError("Seul le vendeur peut effectuer cette transition.")

        if (current, new) in buyer_only and not is_buyer:
            raise ForbiddenActionError("Seul l'acheteur peut valider la livraison.")

    def _maybe_complete_order(self, order: Order) -> None:
        if self.order_repo.all_items_completed(order.id) and can_transition_order(
            order.status, OrderStatus.COMPLETED
        ):
            self.order_repo.update_status(order, OrderStatus.COMPLETED)

    def cancel_order(self, order_id: int, user_id: int) -> Order:
        order = self.order_repo.get_with_items(order_id)
        if order is None:
            raise NotFoundError("Commande introuvable.")

        if order.buyer_id != user_id:
            raise ForbiddenActionError("Seul l'acheteur peut annuler sa commande.")

        if order.status != OrderStatus.PENDING:
            raise InvalidStateTransitionError(
                "Une commande déjà payée ne peut pas être annulée par l'acheteur."
            )

        self.order_repo.update_status(order, OrderStatus.CANCELED)

        for item in order.items:
            if can_transition_item(item.status, OrderItemStatus.CANCELED):
                self.item_repo.update_status(item, OrderItemStatus.CANCELED)

        self.db.commit()

        return order
