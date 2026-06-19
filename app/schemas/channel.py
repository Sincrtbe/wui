"""
app/schemas/channel.py
Schemas Pydantic para el módulo de Canales.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


# ── Requests ──────────────────────────────────────────────────────────────────


class ChannelCreate(BaseModel):
    """Solicitud para crear un canal."""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre del canal")
    url: str = Field(..., description="URL del canal de YouTube")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if "youtube.com" not in v and "youtu.be" not in v:
            raise ValueError("La URL debe ser de YouTube")
        return v


class ChannelUpdate(BaseModel):
    """Solicitud para actualizar un canal."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern="^(active|inactive|syncing)$")


class ChannelSync(BaseModel):
    """Solicitud para sincronizar un canal."""
    pass


class ChannelSearch(BaseModel):
    """Solicitud para buscar canales."""
    query: str = Field(..., min_length=1, max_length=100)
    max_results: int = Field(default=10, ge=1, le=50)


# ── Responses ─────────────────────────────────────────────────────────────────


class ChannelResponse(BaseModel):
    """Respuesta con datos de un canal."""
    id: str
    name: str
    url: str
    channel_id: Optional[str] = None
    thumbnail: Optional[str] = None
    subscribers: int = 0
    description: str = ""
    status: str = "active"
    last_sync: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class ChannelListResponse(BaseModel):
    """Respuesta con lista de canales."""
    channels: list[ChannelResponse]
    total: int


class ChannelSearchResponse(BaseModel):
    """Respuesta con resultados de búsqueda."""
    results: list[ChannelResponse]
    total: int


class APIError(BaseModel):
    """Respuesta de error."""
    error: str
    message: str
