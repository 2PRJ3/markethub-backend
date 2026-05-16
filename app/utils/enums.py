from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class ServiceStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELED = "canceled"


class OrderItemStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELED = "canceled"
