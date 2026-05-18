from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic
from app.utils.enums import ServiceStatus


class ServiceBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=20, max_length=2000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    category_id: int


class ServiceCreate(ServiceBase):
    image_url: str | None = None


class ServiceUpdate(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=100)
    description: str | None = Field(None, min_length=20, max_length=2000)
    price: Decimal | None = Field(None, gt=0, decimal_places=2)
    category_id: int | None = None
    image_url: str | None = None
    status: ServiceStatus | None = None


class ServiceResponse(ServiceBase):
    id: int
    seller_id: int
    status: ServiceStatus
    image_url: str | None = None
    average_rating: float | None = None
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
    image_url: str | None = None
    average_rating: float | None = None
    reviews_count: int = 0
    created_at: datetime
    seller: UserPublic

    model_config = {"from_attributes": True}


class ServiceSearchParams(BaseModel):
    q: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        description="Texte de recherche full-text sur le titre et la description",
    )
    category_id: int | None = Field(None, gt=0, description="Filtrer par catégorie")
