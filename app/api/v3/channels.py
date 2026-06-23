"""
app/api/v3/channels.py
Rutas de canales: CRUD + sync YouTube.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.v3.schemas import ChannelCreate, ChannelOut, ChannelUpdate
from app.api.v3.auth import get_current_user
from app.core.multiuser_dal import (
    create_channel,
    get_channel,
    list_channels,
    update_channel,
    delete_channel,
)

router = APIRouter()


@router.get("", response_model=list[ChannelOut])
def list_my_channels(user: dict = Depends(get_current_user)):
    """Lista todos los canales del usuario actual."""
    return [ChannelOut(**c) for c in list_channels(user["id"])]


@router.post("", response_model=ChannelOut, status_code=status.HTTP_201_CREATED)
def create_my_channel(body: ChannelCreate, user: dict = Depends(get_current_user)):
    """Crea un nuevo canal para el usuario actual."""
    channel = create_channel(
        user_id=user["id"],
        name=body.name,
        platform=body.platform,
        platform_id=body.platform_id,
        url=body.url,
        topic=body.topic,
    )
    return ChannelOut(**channel)


@router.get("/{channel_id}", response_model=ChannelOut)
def get_my_channel(channel_id: str, user: dict = Depends(get_current_user)):
    """Obtiene un canal específico del usuario actual."""
    channel = get_channel(user["id"], channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    if channel["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este canal")
    return ChannelOut(**channel)


@router.put("/{channel_id}", response_model=ChannelOut)
def update_my_channel(
    channel_id: str,
    body: ChannelUpdate,
    user: dict = Depends(get_current_user),
):
    """Actualiza un canal del usuario actual."""
    channel = get_channel(user["id"], channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    if channel["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este canal")
    updated = update_channel(user["id"], channel_id, body.model_dump(exclude_unset=True))
    return ChannelOut(**updated)


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_channel(channel_id: str, user: dict = Depends(get_current_user)):
    """Elimina un canal del usuario actual."""
    channel = get_channel(user["id"], channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    if channel["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="No tienes acceso a este canal")
    delete_channel(user["id"], channel_id)
