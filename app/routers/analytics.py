"""Router de análisis y estadísticas."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.daily_stat import DailyStat
from app.models.publication_schedule import PublicationSchedule
from app.models.video import Video
from app.models.script import Script
from sqlalchemy import func, Date
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
    # Convertir objetos SQLAlchemy a diccionarios para serialización JSON
    return [
        {
            "id": s.id,
            "channel_id": s.channel_id,
            "channel_name": s.channel_name,
            "view_count": s.view_count,
            "subscriber_count": s.subscriber_count,
            "video_count": s.video_count,
            "stat_date": s.stat_date.isoformat() if s.stat_date else None,
            "fecha_ejecucion": s.fecha_ejecucion
        }
        for s in stats
    ]

@router.get("/publications-history/{channel_id}")
def get_publications_history(channel_id: int, db: Session = Depends(get_db)):
    """Obtiene el historial de publicaciones de un canal."""
    # Buscar publicaciones y scripts asociados
    history = db.query(
        PublicationSchedule.scheduled_datetime,
        PublicationSchedule.status,
        PublicationSchedule.notes,
        PublicationSchedule.content_type,
        Script.title
    ).outerjoin(Script, PublicationSchedule.script_id == Script.id).filter(
        PublicationSchedule.channel_id == channel_id
    ).order_by(PublicationSchedule.scheduled_datetime.desc()).all()
    
    return [
        {
            "date": h.scheduled_datetime.isoformat() if h.scheduled_datetime else None,
            "content_type": h.content_type or "unknown",
            "title": h.title or "Sin guion asociado",
            "status": h.status or "planned"
        } for h in history
    ]

@router.post("/check-today/{channel_id}")
async def check_and_fetch_today_stats(channel_id: int, db: Session = Depends(get_db)):
    """Verifica si hay datos de hoy para el canal. Si no los hay, ejecuta DatosDiarios.py y los guarda."""
    from datetime import date
    today = date.today()
    
    # Buscar datos de hoy
    existing = db.query(DailyStat).filter(
        DailyStat.channel_id == channel_id,
        DailyStat.stat_date == today
    ).first()
    
    if existing:
        return {
            "has_today_data": True,
            "data": {
                "view_count": existing.view_count,
                "subscriber_count": existing.subscriber_count,
                "video_count": existing.video_count,
                "fecha_ejecucion": existing.fecha_ejecucion
            }
        }
    
    # No hay datos de hoy, ejecutar DatosDiarios.py
    from app.services.analytics_service import run_daily_stats_import
    result = run_daily_stats_import(db, channel_id)
    
    if "error" in result:
        return {"has_today_data": False, "error": result["error"]}
    
    return {
        "has_today_data": True,
        "data": result.get("data", {}),
        "fetched": True
    }


@router.get("/summary/{channel_id}")
def get_channel_summary(channel_id: int, db: Session = Depends(get_db)):
    """Resumen de actividad del canal."""
    # Contar videos por estado
    video_stats = db.query(Video.status, func.count(Video.id)).filter(Video.channel_id == channel_id).group_by(Video.status).all()
    
    # Contar publicaciones
    pub_count = db.query(func.count(PublicationSchedule.id)).filter(PublicationSchedule.channel_id == channel_id).scalar()
    
    return {
        "video_stats": dict(video_stats),
        "total_publications": pub_count
    }
