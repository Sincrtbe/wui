"""Router de configuración global."""
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.config import GlobalConfig
from pydantic import BaseModel
from app.services.automation_service_sync import sync_analytics_schedule
from app.core.config import get_youtube_api_key, mask_api_key, is_youtube_api_key_configured
from dotenv import load_dotenv

router = APIRouter(prefix="/api/config", tags=["config"])

class ConfigUpdate(BaseModel):
    key: str
    value: str
    description: str | None = None

# Fichero .env para la API key de YouTube
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")


@router.get("")
def get_all_config(db: Session = Depends(get_db)):
    """Obtiene toda la configuración."""
    return db.query(GlobalConfig).all()

@router.post("")
def update_config(config: ConfigUpdate, db: Session = Depends(get_db)):
    """Crea o actualiza una configuración."""
    db_config = db.query(GlobalConfig).filter(GlobalConfig.key == config.key).first()
    if db_config:
        db_config.value = config.value
        if config.description:
            db_config.description = config.description
    else:
        db_config = GlobalConfig(key=config.key, value=config.value, description=config.description)
        db.add(db_config)
    
    db.commit()
    db.refresh(db_config)
    
    # Si se actualiza la programación de analíticas, sincronizar el scheduler
    if config.key == "analytics_schedule":
        sync_analytics_schedule(config.value)
        
    return db_config

@router.get("/{key}")
def get_config(key: str, db: Session = Depends(get_db)):
    """Obtiene una configuración por clave."""
    config = db.query(GlobalConfig).filter(GlobalConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config


# ===== YouTube API Key Endpoints =====

class YoutubeKeyUpdate(BaseModel):
    api_key: str


@router.get("/youtube-key")
def get_youtube_key_status():
    """Obtiene el estado de la YouTube API Key (siempre devuelve la key enmascarada).
    
    Returns:
        dict: Estado de la API key con información enmascarada.
    """
    key = get_youtube_api_key()
    configured = is_youtube_api_key_configured()
    masked = mask_api_key(key) if configured else None
    
    return {
        "configured": configured,
        "masked_key": masked,
        "display_key": f"{masked[:2]}****{masked[-2:]}" if masked and len(masked) > 4 else masked
    }


@router.post("/youtube-key")
def update_youtube_key(config: YoutubeKeyUpdate):
    """Guarda la YouTube API Key en el fichero .env.
    
    La key se almacena en texto plano en .env (que está en .gitignore).
    """
    api_key = config.api_key.strip()
    
    if not api_key:
        raise HTTPException(status_code=400, detail="La API key no puede estar vacía")
    
    # Leer el .env actual
    load_dotenv(ENV_FILE)
    env_vars = {}
    
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
    
    # Actualizar la key
    env_vars["YOUTUBE_API_KEY"] = api_key
    
    # Escribir de vuelta
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")
    
    # Recargar las variables de entorno
    os.environ["YOUTUBE_API_KEY"] = api_key
    
    return {
        "success": True,
        "message": "YouTube API Key guardada correctamente",
        "masked_key": mask_api_key(api_key)
    }
