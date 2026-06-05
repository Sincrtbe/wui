"""Modelo de estadísticas diarias."""
from datetime import date
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.core.database import Base


class DailyStat(Base):
    """Modelo para guardar estadísticas diarias de canales."""

    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    channel_name = Column(String, nullable=True)
    view_count = Column(Integer, default=0)
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    stat_date = Column(Date, default=date.today)
    fecha_ejecucion = Column(String, nullable=True)  # Fecha en formato ISO como string
