"""Schemas de publicación."""
from pydantic import BaseModel
from datetime import datetime


class PublicationCreate(BaseModel):
    channel_id: int
    script_id: int | None = None
    scheduled_datetime: datetime
    notes: str | None = None


class PublicationUpdate(BaseModel):
    scheduled_datetime: datetime | None = None
    status: str | None = None
    notes: str | None = None


class PublicationResponse(BaseModel):
    id: int
    channel_id: int
    script_id: int | None
    scheduled_datetime: datetime
    status: str
    notes: str | None

    class Config:
        from_attributes = True
