from datetime import datetime

from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    room_number: str = Field(min_length=1, max_length=20)
    room_type_id: int = Field(gt=0)
    status: str = Field(default="available", max_length=30)
    amenities: dict = Field(default_factory=dict)


class RoomUpdate(BaseModel):
    room_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )
    room_type_id: int | None = Field(default=None, gt=0)
    status: str | None = Field(
        default=None,
        max_length=30,
    )
    amenities: dict | None = None


class RoomResponse(BaseModel):
    id: int
    room_number: str
    room_type_id: int
    status: str
    amenities: dict
    created_at: datetime

    model_config = {"from_attributes": True}