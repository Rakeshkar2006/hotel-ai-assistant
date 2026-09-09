from datetime import datetime

from pydantic import BaseModel, Field


class ServiceRequestCreate(BaseModel):
    guest_id: int = Field(gt=0)
    request_type: str = Field(min_length=2, max_length=100)
    description: str | None = Field(
        default=None,
        max_length=500,
    )


class ServiceRequestUpdate(BaseModel):
    request_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    status: str | None = Field(
        default=None,
        max_length=30,
    )


class ServiceRequestResponse(BaseModel):
    id: int
    guest_id: int
    request_type: str
    description: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}