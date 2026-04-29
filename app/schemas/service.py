from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.enums import ServiceStatus
from app.schemas.user import UserPublic

class ServiceBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=50)
    description: str = Field(..., min_length=20, max_length=2000)
    price: Decimal = Field(...,gt=0, decimal_places=2)
    category_id: int

class ServiceCreate(ServiceBase):
    image_url: Optional[str] = None

class ServiceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    status: Optional[ServiceStatus] = None

class ServiceResponse(ServiceBase):
    id: int
    seller_id: int
    status: ServiceStatus
    image_url: Optional[str] = None
    average_rating: Optional[float] = None
    reviews_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ServiceDetail(ServiceResponse):
    seller: UserPublic


class ServiceSummary(BaseModel):
    id: int
    title: str
    price: Decimal
    image_url: Optional[str] = None
    average_rating: Optional[float] = None
    reviews_count: int = 0
    created_at: datetime
    seller: UserPublic

    model_config = {"from_attributes": True}