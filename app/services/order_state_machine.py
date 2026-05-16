from app.utils.enums import OrderItemStatus, OrderStatus

ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.PAID, OrderStatus.CANCELED},
    OrderStatus.PAID: {OrderStatus.COMPLETED, OrderStatus.CANCELED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELED: set(),
}

ORDER_ITEM_TRANSITIONS: dict[OrderItemStatus, set[OrderItemStatus]] = {
    OrderItemStatus.PENDING: {OrderItemStatus.IN_PROGRESS, OrderItemStatus.CANCELED},
    OrderItemStatus.IN_PROGRESS: {OrderItemStatus.DELIVERED, OrderItemStatus.CANCELED},
    OrderItemStatus.DELIVERED: {OrderItemStatus.COMPLETED},
    OrderItemStatus.COMPLETED: set(),
    OrderItemStatus.CANCELED: set(),
}


def can_transition_order(current: OrderStatus, new: OrderStatus) -> bool:
    return new in ORDER_TRANSITIONS.get(current, set())


def can_transition_item(current: OrderItemStatus, new: OrderItemStatus) -> bool:
    return new in ORDER_ITEM_TRANSITIONS.get(current, set())
