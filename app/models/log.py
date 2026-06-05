"""Modelo de logs para auditoría y seguimiento."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.core.database import Base


class TaskLog(Base):
    """Modelo para registrar logs de tareas de automatización."""

    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("automation_tasks.id"), nullable=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True)
    
    # Tipo de evento: automation_run, content_created, content_updated, error, etc.
    event_type = Column(String, nullable=False)
    
    # Nivel de severidad: info, warning, error, success
    severity = Column(String, default="info")
    
    # Mensaje descriptivo
    message = Column(Text, nullable=False)
    
    # Detalles adicionales (JSON)
    details = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
