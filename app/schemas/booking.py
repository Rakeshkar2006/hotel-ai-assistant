from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    guest_id: int = Field(gt=0)
    room_id: int = Field(gt=0)
    check_in: date
    check_out: date


class BookingUpdate(BaseModel):
    check_in: date | None = None
    check_out: date | None = None
    status: str | None = Field(default=None, max_length=30)


class BookingResponse(BaseModel):
    id: int
    guest_id: int
    room_id: int
    check_in: date
    check_out: date
    total_price: Decimal
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}