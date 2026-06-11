"""Schemas de canal."""
from pydantic import BaseModel
from datetime import datetime
from typing import Any


class ChannelCreate(BaseModel):
    title: str
    color: str | None = "#3b82f6"


class ChannelUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    custom_url: str | None = None
    published_at: datetime | None = None
    topic_ids: list[str] | None = None
    topic_categories: list[str] | None = None
    thumbnail_file: str | None = None
    color: str | None = None


class ChannelResponse(BaseModel):
    id: int
    title: str
    color: str | None = None
    description: str | None = None
    customUrl: str | None = None
    publishedAt: datetime | None = None
    topicIds: list[str] | None = None
    topicCategories: list[str] | None = None
    thumbnail_file: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True