"""Schemas de guión."""
from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import datetime


class ScriptCreate(BaseModel):
    channel_id: int
    title: str
    description: str | None = None
    voice_script: str | None = None
    graphic_script: str | None = None
    tags: list[str] = []


class ScriptUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    voice_script: str | None = None
    graphic_script: str | None = None
    status: str | None = None
    tags: list[str] | None = None


class ScriptResponse(BaseModel):
    id: int
    channel_id: int
    title: str
    description: str | None
    voice_script: str | None
    graphic_script: str | None
    status: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
