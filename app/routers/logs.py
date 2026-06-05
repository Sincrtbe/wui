"""Router para visualizar logs y auditoría."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.log_service import LogService
from typing import Optional

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/")
def get_logs(
    task_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene logs filtrados."""
    logs = LogService.get_logs(db, task_id, channel_id, event_type, severity, limit)
    return logs

@router.get("/channel/{channel_id}")
def get_channel_logs(channel_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Obtiene logs de un canal específico."""
    logs = LogService.get_logs(db, channel_id=channel_id, limit=limit)
    return logs

@router.get("/task/{task_id}")
def get_task_logs(task_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Obtiene logs de una tarea específica."""
    logs = LogService.get_logs(db, task_id=task_id, limit=limit)
    return logs

@router.get("/errors")
def get_error_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Obtiene todos los logs de error."""
    logs = LogService.get_logs(db, severity="error", limit=limit)
    return logs
