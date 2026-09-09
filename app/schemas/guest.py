from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class GuestCreate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)


class GuestUpdate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        max_length=30,
    )


class GuestResponse(BaseModel):
    id: int
    user_id: int | None
    full_name: str
    email: EmailStr
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}