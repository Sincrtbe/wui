"""Router de canales."""
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.channel import ChannelCreate, ChannelUpdate, ChannelResponse
from app.services.channel_service import ChannelService

router = APIRouter(prefix="/api/channels", tags=["channels"])


@router.post("", response_model=ChannelResponse)
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    """Crea un nuevo canal."""
    return ChannelService.create(db, channel)


@router.get("", response_model=list[ChannelResponse])
def get_channels(db: Session = Depends(get_db)):
    """Obtiene todos los canales."""
    return ChannelService.get_all(db)


@router.get("/{channel_id}", response_model=ChannelResponse)
def get_channel(channel_id: int, db: Session = Depends(get_db)):
    """Obtiene un canal por ID."""
    channel = ChannelService.get_by_id(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    return channel


@router.put("/{channel_id}", response_model=ChannelResponse)
def update_channel(channel_id: int, channel_update: ChannelUpdate, db: Session = Depends(get_db)):
    """Actualiza un canal."""
    channel = ChannelService.update(db, channel_id, channel_update)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    return channel


@router.delete("/{channel_id}")
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    """Elimina un canal."""
    success = ChannelService.delete(db, channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    return {"detail": "Canal eliminado"}


@router.post("/tools/create-files")
def create_channel_files(name: str):
    """Ejecuta el script de tools para crear los archivos del canal."""
    from tools.script_runner import run_script
    import json
    
    # El script espera el nombre del canal como primer argumento
    result = run_script("creacionDcanal.py", args=[name])
    
    if result.success:
        return {"detail": "Archivos creados correctamente", "stdout": result.stdout}
    else:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar script: {result.error or result.stderr}")


@router.get("/{channel_id}/thumbnail", response_class=FileResponse)
def get_channel_thumbnail(channel_id: int, db: Session = Depends(get_db)):
    """Obtiene la imagen de miniatura de un canal."""
    channel = ChannelService.get_by_id(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    if not channel.thumbnail_file:
        raise HTTPException(status_code=404, detail="No hay imagen de miniatura")
    
    # La ruta thumbnail_file es relativa al directorio channels_data (sin subcarpeta)
    channels_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "channels_data")
    full_path = os.path.join(channels_data_dir, channel.thumbnail_file)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Archivo de imagen no encontrado")
    
    # Determinar el tipo de contenido según la extensión
    ext = os.path.splitext(full_path)[1].lower()
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    content_type = content_types.get(ext, "application/octet-stream")
    
    return FileResponse(full_path, media_type=content_type)
