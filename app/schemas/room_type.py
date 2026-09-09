from datetime import datetime

from pydantic import BaseModel, Field


class RoomTypeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    base_price: float = Field(ge=0)
    max_guests: int = Field(ge=1, le=20)


class RoomTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    base_price: float | None = Field(default=None, ge=0)
    max_guests: int | None = Field(default=None, ge=1, le=20)


class RoomTypeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    base_price: float
    max_guests: int
    created_at: datetime

    model_config = {"from_attributes": True}