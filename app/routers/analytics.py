"""Router de análisis y estadísticas."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.daily_stat import DailyStat
from app.models.publication_schedule import PublicationSchedule
from app.models.video import Video
from sqlalchemy import func
from datetime import date, timedelta
from app.services.analytics_service import run_daily_stats_import

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.post("/import/{channel_id}")
def import_channel_stats(channel_id: int, db: Session = Depends(get_db)):
    """Ejecuta la importación de estadísticas para un canal."""
    result = run_daily_stats_import(db, channel_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.get("/daily-stats/{channel_id}")
def get_daily_stats(channel_id: int, db: Session = Depends(get_db)):
    """Obtiene las estadísticas diarias de un canal."""
    stats = db.query(DailyStat).filter(DailyStat.channel_id == channel_id).order_by(DailyStat.stat_date.asc()).all()
    return stats

@router.get("/publications-history/{channel_id}")
def get_publications_history(channel_id: int, db: Session = Depends(get_db)):
    """Obtiene el historial de publicaciones de un canal."""
    # Buscar publicaciones y videos asociados
    history = db.query(
        PublicationSchedule.scheduled_at,
        PublicationSchedule.platform,
        Video.title,
        Video.status
    ).join(Video, PublicationSchedule.video_id == Video.id).filter(Video.channel_id == channel_id).all()
    
    return [
        {
            "date": h.scheduled_at,
            "platform": h.platform,
            "title": h.title,
            "status": h.status
        } for h in history
    ]

@router.get("/summary/{channel_id}")
def get_channel_summary(channel_id: int, db: Session = Depends(get_db)):
    """Resumen de actividad del canal."""
    # Contar videos por estado
    video_stats = db.query(Video.status, func.count(Video.id)).filter(Video.channel_id == channel_id).group_by(Video.status).all()
    
    # Contar publicaciones
    pub_count = db.query(func.count(PublicationSchedule.id)).join(Video).filter(Video.channel_id == channel_id).scalar()
    
    return {
        "video_stats": dict(video_stats),
        "total_publications": pub_count
    }
