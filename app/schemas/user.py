from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

from app.utils.validators import validate_password
from app.utils.enums import UserRole

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    university: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str
    study_sector: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return validate_password(value)

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    university: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    study_sector: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_suspended: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class UserPublic(BaseModel):
    id: int
    first_name: str
    last_name: str
    university: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    study_sector: Optional[str] = None

    model_config = {"from_attributes": True}

class UserAdminResponse(UserResponse):
    study_sector: Optional[str] = None
