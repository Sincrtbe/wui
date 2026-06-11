"""Modelo de contenido para el flujo de trabajo."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from app.core.database import Base


class ContentItem(Base):
    """Modelo que representa una pieza de contenido en cualquier etapa del flujo."""

    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    
    # Etapa actual: idea, script, developed, video
    stage = Column(String, default="idea") 
    
    title = Column(String, nullable=False)
    
    # Datos de la idea (lluvia de ideas)
    idea_notes = Column(Text, nullable=True)
    
    # Datos del guion / artículo
    script_content = Column(Text, nullable=True)
    article_content = Column(Text, nullable=True)
    
    # Datos desarrollados (recursos, prompts usados, etc.)
    developed_data = Column(JSON, nullable=True) 
    
    # Datos del video (ruta del archivo, duración, etc.)
    video_path = Column(String, nullable=True)
    video_metadata = Column(JSON, nullable=True)
    
    status = Column(String, default="pending") # pending, in_progress, completed, discarded
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
