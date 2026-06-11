"""Servicio de vídeos."""
from sqlalchemy.orm import Session
from app.models import Video
from app.schemas.video import VideoCreate, VideoUpdate


class VideoService:
    """Servicio de gestión de vídeos."""

    @staticmethod
    def create(db: Session, video: VideoCreate) -> Video:
        """Crea un nuevo vídeo."""
        db_video = Video(
            channel_id=video.channel_id,
            script_id=video.script_id,
            title=video.title,
            duration=video.duration,
            status="planned",
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        return db_video

    @staticmethod
    def get_all(db: Session, channel_id: int | None = None, script_id: int | None = None, status: str | None = None) -> list[Video]:
        """Obtiene vídeos con filtros opcionales."""
        query = db.query(Video)

        if channel_id is not None:
            query = query.filter(Video.channel_id == channel_id)

        if script_id is not None:
            query = query.filter(Video.script_id == script_id)

        if status is not None:
            query = query.filter(Video.status == status)

        return query.all()

    @staticmethod
    def get_by_id(db: Session, video_id: int) -> Video | None:
        """Obtiene un vídeo por ID."""
        return db.query(Video).filter(Video.id == video_id).first()

    @staticmethod
    def update(db: Session, video_id: int, video_update: VideoUpdate) -> Video | None:
        """Actualiza un vídeo."""
        db_video = db.query(Video).filter(Video.id == video_id).first()
        if not db_video:
            return None

        update_data = video_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_video, key, value)

        db.commit()
        db.refresh(db_video)
        return db_video

    @staticmethod
    def delete(db: Session, video_id: int) -> bool:
        """Elimina un vídeo."""
        db_video = db.query(Video).filter(Video.id == video_id).first()
        if not db_video:
            return False

        db.delete(db_video)
        db.commit()
        return True
