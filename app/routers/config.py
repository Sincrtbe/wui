"""Router de configuración global."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.config import GlobalConfig
from pydantic import BaseModel
from app.services.automation_service_sync import sync_analytics_schedule

router = APIRouter(prefix="/api/config", tags=["config"])

class ConfigUpdate(BaseModel):
    key: str
    value: str
    description: str | None = None

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
