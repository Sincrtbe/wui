"""Modelo de configuración global."""
from sqlalchemy import Column, String, Text
from app.core.database import Base


class GlobalConfig(Base):
    """Modelo para guardar pares clave-valor de configuración."""

    __tablename__ = "global_configs"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(String, nullable=True)
