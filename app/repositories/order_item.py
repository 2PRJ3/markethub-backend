from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.order_item import OrderItem
from app.repositories.base import BaseRepository
from app.utils.enums import OrderItemStatus


class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self, db: Session):
        super().__init__(OrderItem, db)

    def get_with_relations(self, item_id: int) -> OrderItem | None:
        stmt = (
            select(OrderItem)
            .where(OrderItem.id == item_id)
            .options(
                joinedload(OrderItem.order),
                joinedload(OrderItem.service),
                joinedload(OrderItem.seller),
            )
        )

        return self.db.execute(stmt).scalar_one_or_none()

    def update_status(self, item: OrderItem, new_status: OrderItemStatus) -> OrderItem:
        item.status = new_status
        self.db.flush()
        self.db.refresh(item)
        return item
