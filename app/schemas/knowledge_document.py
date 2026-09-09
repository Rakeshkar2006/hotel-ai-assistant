from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=255,
    )

    file_name: str = Field(
        min_length=1,
        max_length=255,
    )


class KnowledgeDocumentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    is_approved: bool | None = None


class KnowledgeDocumentResponse(BaseModel):
    id: int
    title: str
    file_name: str
    file_path: str
    is_approved: bool
    created_at: datetime

    model_config = {"from_attributes": True}