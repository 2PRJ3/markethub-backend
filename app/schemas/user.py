from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.utils.enums import UserRole
from app.utils.validators import validate_password


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    university: str
    bio: str | None = None
    avatar_url: str | None = None
    study_sector: str | None = None


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return validate_password(value)


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    university: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    study_sector: str | None = None


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
    bio: str | None = None
    avatar_url: str | None = None
    study_sector: str | None = None

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return validate_password(value)


class UserAdminResponse(UserResponse):
    study_sector: str | None = None
