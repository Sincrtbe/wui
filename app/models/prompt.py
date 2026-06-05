"""Modelo de prompts para la biblioteca."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON
from app.core.database import Base


class Prompt(Base):
    """Modelo para guardar prompts reutilizables con variables."""

    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Información básica
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Tipo de prompt: lluvia_ideas, guion, audio, video, seo, otro
    prompt_type = Column(String, nullable=False)
    
    # Contenido del prompt con variables entre {{}}
    content = Column(Text, nullable=False)
    
    # Variables requeridas (extraídas automáticamente)
    variables = Column(JSON, default=list)  # ["tema", "duracion", "estilo"]
    
    # Puntuación de utilidad (0-5)
    rating = Column(Float, default=0.0)
    
    # Número de veces usado
    usage_count = Column(Integer, default=0)
    
    # Versión del prompt
    version = Column(Integer, default=1)
    
    # Activo/Inactivo
    is_active = Column(String, default="active")
    
    # Metadatos adicionales
    meta_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
