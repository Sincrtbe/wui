"""Router de vídeos."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.video import VideoCreate, VideoUpdate, VideoResponse
from app.services.video_service import VideoService

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("", response_model=VideoResponse)
def create_video(video: VideoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo vídeo."""
    return VideoService.create(db, video)


@router.get("", response_model=list[VideoResponse])
def get_videos(
    channel_id: int | None = Query(None),
    script_id: int | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Obtiene vídeos con filtros opcionales."""
    return VideoService.get_all(db, channel_id, script_id, status)


@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    """Obtiene un vídeo por ID."""
    video = VideoService.get_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo no encontrado")
    return video


@router.put("/{video_id}", response_model=VideoResponse)
def update_video(video_id: int, video_update: VideoUpdate, db: Session = Depends(get_db)):
    """Actualiza un vídeo."""
    video = VideoService.update(db, video_id, video_update)
    if not video:
        raise HTTPException(status_code=404, detail="Vídeo no encontrado")
    return video


@router.delete("/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)):
    """Elimina un vídeo."""
    success = VideoService.delete(db, video_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vídeo no encontrado")
    return {"detail": "Vídeo eliminado"}
