from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)


class CategoryCreate(CategoryBase):
    slug: str | None = Field(None, min_length=2, max_length=50)


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=50)
    slug: str | None = Field(None, min_length=2, max_length=50)


class CategoryResponse(CategoryBase):
    id: int
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}
