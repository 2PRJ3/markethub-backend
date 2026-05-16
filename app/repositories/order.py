from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, contains_eager, joinedload, selectinload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.base import BaseRepository
from app.utils.enums import OrderStatus


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_idempotency_key(self, key: UUID) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.idempotency_key == key)
            .options(
                selectinload(Order.items).joinedload(OrderItem.service),
                selectinload(Order.items).joinedload(OrderItem.seller),
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_with_items(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items).joinedload(OrderItem.service),
                selectinload(Order.items).joinedload(OrderItem.seller),
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_buyer(self, buyer_id: int, skip: int = 20, limit: int = 20) -> list[Order]:
        stmt = (
            select(Order)
            .where(Order.buyer_id == buyer_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(selectinload(Order.items))
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_by_buyer(self, buyer_id: int) -> int:
        stmt = select(func.count()).select_from(Order).where(Order.buyer_id == buyer_id)
        return self.db.execute(stmt).scalar_one()

    def list_items_by_seller(
        self, seller_id: int, skip: int = 0, limit: int = 20
    ) -> list[OrderItem]:
        stmt = (
            select(OrderItem)
            .join(OrderItem.order)
            .where(OrderItem.seller_id == seller_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
            .options(
                contains_eager(OrderItem.order).joinedload(Order.buyer),
                joinedload(OrderItem.service),
            )
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_items_by_seller(self, seller_id: int) -> int:
        stmt = select(func.count(OrderItem.id)).where(OrderItem.seller_id == seller_id)
        return self.db.execute(stmt).scalar_one()

    def all_items_completed(self, order_id: int) -> bool:
        total = self.db.execute(
            select(func.count(OrderItem.id)).where(OrderItem.order_id == order_id)
        ).scalar_one()

        if total == 0:
            return False

        completed = self.db.execute(
            select(func.count(OrderItem.id)).where(
                OrderItem.order_id == order_id, OrderItem.status == OrderStatus.COMPLETED
            )
        ).scalar_one()
        return total == completed

    def update_status(self, order: Order, new_status: OrderStatus) -> Order:
        order.status = new_status
        self.db.flush()
        self.db.refresh(order)
        return order
