from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.service import ServiceSummary
from app.schemas.user import UserPublic
from app.utils.enums import OrderItemStatus, OrderStatus
from app.utils.validators import validate_unique_service_ids


class OrderItemCreate(BaseModel):
    service_id: int = Field(..., gt=0, examples=[42])


class OrderItemStatusUpdate(BaseModel):
    status: OrderItemStatus = Field(..., examples=[OrderItemStatus.DELIVERED])


class OrderItemResponse(BaseModel):
    id: int
    service_id: int
    seller_id: int
    unit_price: Decimal
    status: OrderItemStatus
    created_at: datetime

    service: ServiceSummary
    seller: UserPublic

    model_config = {"from_attributes": True}


class OrderBase(BaseModel):
    brief: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        examples=["Je souhaite un logo minimaliste pour mon association étudiante..."],
    )


class OrderCreate(OrderBase):
    idempotency_key: UUID = Field(..., examples=["a3f1c8e2-1234-4abc-9def-0123456789ab"])
    items: list[OrderItemCreate] = Field(..., min_length=1, max_length=20)

    @field_validator("items")
    @classmethod
    def no_duplicate_services(cls, items: list[OrderItemCreate]) -> list[OrderItemCreate]:
        return validate_unique_service_ids(items)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(..., examples=[OrderStatus.PAID])


class OrderResponse(OrderBase):
    id: int
    buyer_id: int
    total_amount: Decimal
    status: OrderStatus
    idempotency_key: UUID
    created_at: datetime
    updated_at: datetime

    items: list[OrderItemResponse]
    buyer: UserPublic

    model_config = {"from_attributes": True}


class OrderSummary(BaseModel):
    id: int
    total_amount: Decimal
    status: OrderStatus
    items_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
