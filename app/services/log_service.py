"""Servicio de logging y auditoría."""
from sqlalchemy.orm import Session
from app.models.log import TaskLog
from datetime import datetime


class LogService:
    """Servicio para registrar eventos y logs en el sistema."""

    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        message: str,
        severity: str = "info",
        task_id: int = None,
        channel_id: int = None,
        details: str = None
    ) -> TaskLog:
        """Registra un evento en los logs."""
        log_entry = TaskLog(
            event_type=event_type,
            message=message,
            severity=severity,
            task_id=task_id,
            channel_id=channel_id,
            details=details
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_logs(
        db: Session,
        task_id: int = None,
        channel_id: int = None,
        event_type: str = None,
        severity: str = None,
        limit: int = 100
    ) -> list[TaskLog]:
        """Obtiene logs filtrados."""
        query = db.query(TaskLog)
        
        if task_id:
            query = query.filter(TaskLog.task_id == task_id)
        if channel_id:
            query = query.filter(TaskLog.channel_id == channel_id)
        if event_type:
            query = query.filter(TaskLog.event_type == event_type)
        if severity:
            query = query.filter(TaskLog.severity == severity)
        
        return query.order_by(TaskLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def log_automation_start(db: Session, task_id: int, channel_id: int):
        """Registra el inicio de una tarea de automatización."""
        LogService.log_event(
            db,
            event_type="automation_start",
            message=f"Iniciando tarea de automatización {task_id}",
            severity="info",
            task_id=task_id,
            channel_id=channel_id
        )

    @staticmethod
    def log_automation_success(db: Session, task_id: int, channel_id: int, details: str = None):
        """Registra el éxito de una tarea de automatización."""
        LogService.log_event(
            db,
            event_type="automation_success",
            message=f"Tarea de automatización {task_id} completada exitosamente",
            severity="success",
            task_id=task_id,
            channel_id=channel_id,
            details=details
        )

    @staticmethod
    def log_automation_error(db: Session, task_id: int, channel_id: int, error: str):
        """Registra un error en una tarea de automatización."""
        LogService.log_event(
            db,
            event_type="automation_error",
            message=f"Error en tarea de automatización {task_id}: {error}",
            severity="error",
            task_id=task_id,
            channel_id=channel_id,
            details=error
        )

    @staticmethod
    def log_content_created(db: Session, channel_id: int, content_type: str, title: str):
        """Registra la creación de contenido."""
        LogService.log_event(
            db,
            event_type="content_created",
            message=f"Nuevo {content_type} creado: {title}",
            severity="info",
            channel_id=channel_id
        )

    @staticmethod
    def log_content_advanced(db: Session, channel_id: int, title: str, from_stage: str, to_stage: str):
        """Registra el avance de contenido entre etapas."""
        LogService.log_event(
            db,
            event_type="content_advanced",
            message=f"Contenido '{title}' avanzó de {from_stage} a {to_stage}",
            severity="info",
            channel_id=channel_id
        )
