"""Schemas de vídeo."""
from pydantic import BaseModel
from datetime import datetime


class VideoCreate(BaseModel):
    channel_id: int
    script_id: int | None = None
    title: str
    duration: int | None = None


class VideoUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    duration: int | None = None


class VideoResponse(BaseModel):
    id: int
    channel_id: int
    script_id: int | None
    title: str
    duration: int | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
