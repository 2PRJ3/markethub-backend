from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)

class CategoryCreate(CategoryBase):
    slug: Optional[str] = Field(None, min_length=2, max_length=50)

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    slug: Optional[str] = Field(None, min_length=2, max_length=50)

class CategoryResponse(CategoryBase):
    id: int
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}