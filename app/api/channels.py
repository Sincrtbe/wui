"""
app/api/channels.py
Router API para el módulo de Canales (CRUD + YouTube).
"""

from typing import Any

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.channel import (
    APIError,
    ChannelCreate,
    ChannelListResponse,
    ChannelResponse,
    ChannelSearch,
    ChannelSearchResponse,
    ChannelUpdate,
)
from app.services.channel_service import (
    create_channel,
    delete_channel,
    get_channel,
    list_channels,
    update_channel,
    sync_channel,
    search_local_channels,
)
from app.services.youtube_service import search_channels, extract_channel_id
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/api/channels", tags=["Canales"])


@router.post(
    "/",
    response_model=ChannelResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": APIError, "description": "URL inválida"},
    },
)
async def create_new_channel(
    data: ChannelCreate,
    _user: dict = Depends(get_current_active_user),
):
    """Crea un nuevo canal de YouTube."""
    try:
        return await create_channel(name=data.name, url=data.url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=ChannelListResponse,
)
async def get_channels(_user: dict = Depends(get_current_active_user)):
    """Lista todos los canales registrados."""
    channels = list_channels()
    return ChannelListResponse(channels=channels, total=len(channels))


@router.get(
    "/{channel_id}",
    response_model=ChannelResponse,
    responses={404: {"model": APIError}},
)
async def get_channel_by_id(
    channel_id: str,
    _user: dict = Depends(get_current_active_user),
):
    """Obtiene un canal por su ID."""
    channel = get_channel(channel_id)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canal no encontrado: {channel_id}",
        )
    return channel


@router.put(
    "/{channel_id}",
    response_model=ChannelResponse,
    responses={404: {"model": APIError}},
)
async def update_channel_by_id(
    channel_id: str,
    data: ChannelUpdate,
    _user: dict = Depends(get_current_active_user),
):
    """Actualiza un canal existente."""
    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay campos para actualizar",
        )

    result = await update_channel(channel_id, updates)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canal no encontrado: {channel_id}",
        )
    return result


@router.delete(
    "/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": APIError}},
)
async def delete_channel_by_id(
    channel_id: str,
    _user: dict = Depends(get_current_active_user),
):
    """Elimina un canal."""
    if not delete_channel(channel_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canal no encontrado: {channel_id}",
        )


@router.post(
    "/{channel_id}/sync",
    response_model=ChannelResponse,
    responses={
        404: {"model": APIError},
        500: {"model": APIError},
    },
)
async def sync_channel_by_id(
    channel_id: str,
    _user: dict = Depends(get_current_active_user),
):
    """Sincroniza un canal con la YouTube API."""
    try:
        result = await sync_channel(channel_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Canal no encontrado: {channel_id}",
        )
    return result


@router.post(
    "/search",
    response_model=ChannelSearchResponse,
    responses={500: {"model": APIError}},
)
async def search_youtube_channels(
    data: ChannelSearch,
    _user: dict = Depends(get_current_active_user),
):
    """Busca canales — primero en la DB local, luego en YouTube."""
    # 1. Búsqueda local
    local_results = search_local_channels(data.query, data.max_results)
    channel_responses = [
        ChannelResponse(
            id=r.id, name=r.name, url=r.url, channel_id=r.channel_id,
            thumbnail=r.thumbnail, description=r.description,
            subscribers=r.subscribers, created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in local_results
    ]

    # 2. Si hay API key, también buscar en YouTube
    from app.core.config import settings
    if settings.YOUTUBE_API_KEY:
        yt_results = await search_channels(data.query, data.max_results)
        seen_ids = {c.channel_id for c in channel_responses if c.channel_id}
        for r in yt_results:
            if r.get("channel_id") not in seen_ids:
                channel_responses.append(ChannelResponse(
                    id=r.get("channel_id", ""),
                    name=r.get("name", ""),
                    url=r.get("url", ""),
                    channel_id=r.get("channel_id"),
                    thumbnail=r.get("thumbnail"),
                    description=r.get("description", ""),
                    subscribers=0,
                    created_at=datetime.now(timezone.utc).isoformat(),
                    updated_at=datetime.now(timezone.utc).isoformat(),
                ))
                seen_ids.add(r.get("channel_id", ""))

    return ChannelSearchResponse(results=channel_responses, total=len(channel_responses))


@router.get("/validate-url")
async def validate_youtube_url(
    url: str,
    _user: dict = Depends(get_current_active_user),
):
    """Valida una URL de YouTube y extrae el channel_id."""
    channel_id = extract_channel_id(url)
    if not channel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo extraer channel_id de la URL: {url}",
        )
    return {"valid": True, "channel_id": channel_id}
