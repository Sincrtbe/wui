"""Servicio de canales."""
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Channel
from app.schemas.channel import ChannelCreate, ChannelUpdate

# Directorio donde se guardarán los archivos del script creacionDcanal.py
CHANNELS_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "channels_data")
os.makedirs(CHANNELS_DATA_DIR, exist_ok=True)


def _find_channel_file_by_name(channel_name: str) -> tuple[str | None, str | None]:
    """Busca archivos del canal por nombre en channels_data (insensible a mayúsculas).
    
    Retorna (ruta_json, ruta_jpg) o (None, None) si no se encuentra.
    """
    nombre_base = "".join(c for c in channel_name if c.isalnum() or c in (' ', '_', '-')).strip()
    nombre_base = nombre_base.replace(" ", "_").lower()
    
    # Buscar archivo JSON insensible a mayúsculas
    for f in os.listdir(CHANNELS_DATA_DIR):
        if f.lower() == f"{nombre_base}.json":
            json_path = os.path.join(CHANNELS_DATA_DIR, f)
            nombre_sin_ext = os.path.splitext(f)[0]
            # Buscar archivo JPG con el mismo nombre base
            jpg_path = None
            for jf in os.listdir(CHANNELS_DATA_DIR):
                if jf.lower() == f"{nombre_sin_ext}.jpg":
                    jpg_path = os.path.join(CHANNELS_DATA_DIR, jf)
                    break
            return json_path, jpg_path
    return None, None


def _load_channel_data_from_file(json_path: str) -> dict | None:
    """Carga la información de un canal desde su archivo JSON generado por creacionDcanal.py."""
    if not os.path.exists(json_path):
        return None
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


class ChannelService:
    """Servicio de gestión de canales."""

    @staticmethod
    def create(db: Session, channel: ChannelCreate) -> Channel:
        """Crea un nuevo canal y busca sus datos en channels_data."""
        json_path, jpg_path = _find_channel_file_by_name(channel.title)
        
        channel_data = {}
        thumbnail_file = None
        
        if json_path:
            channel_data = _load_channel_data_from_file(json_path)
        
        if jpg_path:
            thumbnail_file = os.path.basename(jpg_path)

        db_channel = Channel(
            title=channel_data.get("title", channel.title),
            description=channel_data.get("description"),
            custom_url=channel_data.get("customUrl"),
            published_at=datetime.fromisoformat(channel_data["publishedAt"]) if channel_data.get("publishedAt") else None,
            topic_ids=channel_data.get("topicIds", []),
            topic_categories=channel_data.get("topicCategories", []),
            thumbnail_file=thumbnail_file,
            color=channel.color,
        )
        db.add(db_channel)
        db.commit()
        db.refresh(db_channel)
        return db_channel

    @staticmethod
    def get_all(db: Session) -> list[Channel]:
        """Obtiene todos los canales."""
        return db.query(Channel).all()

    @staticmethod
    def get_by_id(db: Session, channel_id: int) -> Channel | None:
        """Obtiene un canal por ID."""
        return db.query(Channel).filter(Channel.id == channel_id).first()

    @staticmethod
    def update(db: Session, channel_id: int, channel_update: ChannelUpdate) -> Channel | None:
        """Actualiza un canal."""
        db_channel = db.query(Channel).filter(Channel.id == channel_id).first()
        if not db_channel:
            return None

        update_data = channel_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(db_channel, key, value)

        db.commit()
        db.refresh(db_channel)
        return db_channel

    @staticmethod
    def delete(db: Session, channel_id: int) -> bool:
        """Elimina un canal."""
        db_channel = db.query(Channel).filter(Channel.id == channel_id).first()
        if not db_channel:
            return False

        db.delete(db_channel)
        db.commit()
        return True