from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class ReviewCreate(BaseModel):
    order_item_id: int = Field(..., gt=0, examples=[42])
    rating: int = Field(..., ge=1, le=5, examples=[5])
    comment: str | None = Field(None, max_length=1000, examples=["Excellent travail"])


class ReviewResponse(BaseModel):
    id: int
    order_item_id: int
    service_id: int
    buyer_id: int
    rating: int
    comment: str | None
    created_at: datetime

    buyer: UserPublic

    model_config = {"from_attributes": True}


class ReviewSummary(BaseModel):
    id: int
    rating: int
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminReviewResponse(BaseModel):
    id: int
    order_item_id: int
    service_id: int
    buyer_id: int
    rating: int
    comment: str | None
    created_at: datetime

    buyer: UserPublic

    model_config = {"from_attributes": True}
