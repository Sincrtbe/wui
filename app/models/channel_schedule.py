"""Modelo de programación recurrente de canales."""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean, Integer
from app.core.database import Base


class ChannelSchedule(Base):
    """Modelo de programación recurrente de publicaciones por tipo de contenido."""

    __tablename__ = "channel_schedules"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False, unique=True)
    
    # Programación de videos largos
    long_video_enabled = Column(Boolean, default=False)
    long_video_frequency = Column(Integer, default=3)  # cada X días
    
    # Programación de Shorts
    short_video_enabled = Column(Boolean, default=False)
    short_video_frequency = Column(Integer, default=1)  # cada X días
    
    # Programación de artículos
    article_enabled = Column(Boolean, default=False)
    article_frequency = Column(Integer, default=2)  # cada X días
    
    # Configuración general
    start_date = Column(DateTime, nullable=True)  # fecha de inicio de la programación
    timezone = Column(String, default="Europe/Madrid")
    is_active = Column(Boolean, default=False)  # si la programación está activa
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)