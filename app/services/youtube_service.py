"""
app/services/youtube_service.py
Servicio para interactuar con la YouTube Data API v3.
"""

import re
from typing import Any, Optional

import httpx

from app.core.config import settings


def extract_channel_id(url: str) -> Optional[str]:
    """
    Extrae el channel_id de una URL de YouTube.
    Soporta formatos:
      - https://www.youtube.com/channel/UCxxxx
      - https://www.youtube.com/@handle
      - https://www.youtube.com/user/username
      - https://www.youtube.com/c/customname

    Para @handle y /user/ y /c/ devuelve None porque se necesita
    una llamada a la API para obtener el channel_id real.
    """
    patterns = [
        # /channel/ID
        r"youtube\.com/channel/([A-Za-z0-9_-]{1,})",
        # youtu.be/... no es channel
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # @handle: necesita API call para resolver
    handle_match = re.search(r"youtube\.com/@([A-Za-z0-9_-]+)", url)
    if handle_match:
        return f"@{handle_match.group(1)}"

    # /user/username: necesita API call
    user_match = re.search(r"youtube\.com/user/([^/?]+)", url)
    if user_match:
        return f"user:{user_match.group(1)}"

    # /c/customname: necesita API call
    custom_match = re.search(r"youtube\.com/c/([^/?]+)", url)
    if custom_match:
        return f"c:{custom_match.group(1)}"

    return None


async def get_channel_info(channel_id: str) -> Optional[dict[str, Any]]:
    """
    Obtiene información detallada de un canal usando la YouTube Data API v3.
    Retorna un dict con: id, snippet.title, snippet.description,
    snippet.thumbnails, statistics.subscriberCount, etc.
    Retorna None si hay error o API key no configurada.
    """
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        return None

    # Determinar el tipo de ID
    if channel_id.startswith("@") or channel_id.startswith("user:") or channel_id.startswith("c:"):
        # Primero hay que buscar el channel ID real
        real_id = await _resolve_channel_handle(channel_id, api_key)
        if not real_id:
            return None
        channel_id = real_id

    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,statistics,contentDetails,brandingSettings",
        "id": channel_id,
        "key": api_key,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get("items") or not data["items"]:
                return None

            item = data["items"][0]
            return _parse_channel_data(item)

        except httpx.HTTPStatusError as e:
            print(f"[YouTube API] Error HTTP: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except httpx.RequestError as e:
            print(f"[YouTube API] Error de red: {e}")
            return None
        except Exception as e:
            print(f"[YouTube API] Error inesperado: {e}")
            return None


async def _resolve_channel_handle(handle: str, api_key: str) -> Optional[str]:
    """
    Resuelve un @handle, /user/, o /c/ a un channel_id real.
    """
    url = "https://www.googleapis.com/youtube/v3/channels"

    if handle.startswith("@"):
        params = {"part": "id", "forHandle": handle.lstrip("@"), "key": api_key}
    elif handle.startswith("user:"):
        params = {"part": "id", "forUsername": handle.lstrip("user:"), "key": api_key}
    elif handle.startswith("c:"):
        params = {"part": "id", "forUsername": handle.lstrip("c:"), "key": api_key}
    else:
        return None

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("items"):
                return data["items"][0]["id"]
            return None
        except Exception as e:
            print(f"[YouTube API] Error resolviendo handle {handle}: {e}")
            return None


async def search_channels(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Busca canales en YouTube.
    Nota: La API v3 no tiene búsqueda directa de canales,
    pero podemos buscar videos y extraer canales únicos.
    """
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": min(max_results, 50),
        "key": api_key,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", [])[:max_results]:
                snippet = item.get("snippet", {})
                channel_id = item.get("id", {}).get("channelId", "")
                results.append({
                    "channel_id": channel_id,
                    "name": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                    "url": f"https://www.youtube.com/channel/{channel_id}" if channel_id else "",
                })
            return results

        except Exception as e:
            print(f"[YouTube API] Error buscando canales '{query}': {e}")
            return []


def _parse_channel_data(item: dict) -> dict[str, Any]:
    """Parsea la respuesta de la API de channels a nuestro formato."""
    snippet = item.get("snippet", {})
    statistics = item.get("statistics", {})
    branding = item.get("brandingSettings", {})
    thumbnail_data = snippet.get("thumbnails", {})

    thumbnails = thumbnail_data.get("high", thumbnail_data.get("medium", thumbnail_data.get("default", {})))

    return {
        "id": item.get("id"),
        "name": snippet.get("title", ""),
        "description": snippet.get("description", ""),
        "thumbnail": thumbnails.get("url", ""),
        "subscribers": int(statistics.get("subscriberCount", 0)),
        "video_count": int(statistics.get("videoCount", 0)),
        "view_count": int(statistics.get("viewCount", 0)),
        "country": snippet.get("country", ""),
        "custom_url": branding.get("channel", {}).get("customUrl", ""),
    }
