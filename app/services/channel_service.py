"""
app/services/channel_service.py
Servicio de gestión de canales: CRUD + sincronización con YouTube API.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.json_data_manager import (
    read_json_file,
    write_json_file,
    list_json_files,
    delete_json_file,
    update_json_file,
)
from app.schemas.channel import ChannelResponse
from app.services.youtube_service import extract_channel_id, get_channel_info


def _fetch_channel_data_sync(channel_id: str) -> Optional[dict[str, Any]]:
    """
    Wrapper síncrono para get_channel_info (que es async).
    Usa asyncio.run en un hilo separado para evitar bloquear el event loop.
    """
    loop = None
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        pass

    if loop is not None and loop.is_running():
        # Estamos en un event loop, usar nest_asyncio o thread
        try:
            import nest_asyncio
            nest_asyncio.apply()
            return asyncio.run(_fetch(channel_id))
        except ImportError:
            # Si nest_asyncio no está disponible, simplemente retornamos None
            # y la info se obtiene en el sync manual
            return None
    else:
        return asyncio.run(_fetch(channel_id))


async def _fetch(channel_id: str) -> Optional[dict[str, Any]]:
    """Fetch channel data from YouTube API."""
    try:
        return await get_channel_info(channel_id)
    except Exception as e:
        print(f"[ChannelService] Error fetching YouTube info: {e}")
        return None


def _get_channel_data(channel_id: str) -> Optional[dict[str, Any]]:
    """
    Intenta obtener datos del canal. Primero intenta de forma asíncrona,
    si no es posible (fuera del event loop) retorna None y se completará
    manualmente o con sync.
    """
    # En FastAPI todo es async, así que normalmente estaremos en un event loop
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            return asyncio.get_event_loop().run_until_complete(
                _fetch(channel_id)
            )
    except Exception:
        pass
    return None


async def create_channel(name: str, url: str) -> ChannelResponse:
    """
    Crea un nuevo canal.
    1. Extrae el channel_id de la URL
    2. Llama a la YouTube API para obtener info del canal
    3. Guarda en JSON
    """
    channel_id = extract_channel_id(url)
    if not channel_id:
        raise ValueError(f"No se pudo extraer channel_id de la URL: {url}")

    now = datetime.now(timezone.utc).isoformat()

    # Obtener info de YouTube API (async)
    channel_data = await _fetch(channel_id)

    data = {
        "id": str(uuid.uuid4()),
        "name": name,
        "url": url,
        "channel_id": channel_id,
        "thumbnail": "",
        "subscribers": 0,
        "description": "",
        "status": "active",
        "last_sync": None,
        "created_at": now,
        "updated_at": now,
    }

    if channel_data:
        data.update({
            "channel_id": channel_data.get("id", channel_id),
            "thumbnail": channel_data.get("thumbnail", ""),
            "subscribers": channel_data.get("subscribers", 0),
            "description": channel_data.get("description", ""),
        })

    write_json_file("channels", data["id"], data)
    return ChannelResponse(**data)


def get_channel(channel_id: str) -> Optional[ChannelResponse]:
    """Obtiene un canal por su ID."""
    data = read_json_file("channels", channel_id)
    if data is None:
        return None
    return ChannelResponse(**data)


def list_channels() -> list[ChannelResponse]:
    """Lista todos los canales."""
    items = list_json_files("channels")
    return [ChannelResponse(**item) for item in items]


async def update_channel(channel_id: str, updates: dict[str, Any]) -> Optional[ChannelResponse]:
    """Actualiza un canal existente."""
    # Validar campos permitidos
    allowed_fields = {"name", "status", "url"}
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

    if not filtered_updates:
        return None

    existing = read_json_file("channels", channel_id)
    if existing is None:
        return None

    # Si se cambia la URL, re-extract channel_id y re-fetch info
    if "url" in filtered_updates:
        new_channel_id = extract_channel_id(filtered_updates["url"])
        if new_channel_id:
            filtered_updates["channel_id"] = new_channel_id
            channel_data = await _fetch(new_channel_id)
            if channel_data:
                filtered_updates.update({
                    "thumbnail": channel_data.get("thumbnail", ""),
                    "subscribers": channel_data.get("subscribers", 0),
                    "description": channel_data.get("description", ""),
                })

    result = update_json_file("channels", channel_id, filtered_updates)
    if result is None:
        return None
    return ChannelResponse(**result)


def delete_channel(channel_id: str) -> bool:
    """Elimina un canal."""
    return delete_json_file("channels", channel_id)


async def sync_channel(channel_id: str) -> Optional[ChannelResponse]:
    """
    Sincroniza un canal con la YouTube API.
    Actualiza thumbnail, subscribers, description.
    """
    existing = read_json_file("channels", channel_id)
    if existing is None:
        return None

    # Obtener info actualizada de YouTube
    channel_data = await _fetch(existing.get("channel_id", ""))
    if not channel_data:
        raise ValueError(f"No se pudo obtener info del canal para sincronizar: {channel_id}")

    updates = {
        "thumbnail": channel_data.get("thumbnail", ""),
        "subscribers": channel_data.get("subscribers", 0),
        "description": channel_data.get("description", ""),
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    }

    result = update_json_file("channels", channel_id, updates)
    if result is None:
        return None
    return ChannelResponse(**result)


def search_local_channels(query: str, max_results: int = 50) -> list[ChannelResponse]:
    """Busca canales en la base de datos local por nombre o channel_id."""
    items = list_json_files("channels")
    query_lower = query.lower()
    results = []
    for item in items:
        name = item.get("name", "").lower()
        channel_id = str(item.get("channel_id", "")).lower()
        if query_lower in name or query_lower in channel_id:
            results.append(ChannelResponse(**item))
            if len(results) >= max_results:
                break
    return results
