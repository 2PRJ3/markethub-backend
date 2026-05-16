from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.utils.enums import PaymentFailureReason, TransactionStatus, TransactionType
from app.utils.validators import validate_card_number


class PaymentRequest(BaseModel):
    card_number: str
    card_holder: str = Field(min_length=1, max_length=100)
    expiry: str = Field(pattern=r"^\d{4}-\d{2}$")
    cvv: str = Field(pattern=r"^\d{3,4}$")

    _validate_card_number = field_validator("card_number")(validate_card_number)

    def __repr__(self) -> str:
        return f"PaymentRequest(card_holder={self.card_holder!r}, ...)"


class TransactionRead(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    type: TransactionType
    status: TransactionStatus
    reference: str
    failure_reason: PaymentFailureReason | None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderPaymentSummary(BaseModel):
    id: int
    status: str

    model_config = {"from_attributes": True}


class PaymentResponse(BaseModel):
    transaction: TransactionRead
    order: OrderPaymentSummary
