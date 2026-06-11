"""Configuración de la aplicación."""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Settings(BaseSettings):
    """Configuración global de la app."""
    DATABASE_URL: str = "sqlite:///./app.db"
    DEBUG: bool = False
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "admin123"
    
    # Forzar DEBUG=False en producción (solo se puede activar con WUI_DEBUG=true)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Si no está explícitamente activado por env var, forzar DEBUG=False
        if os.getenv("WUI_DEBUG", "").lower() not in ("true", "1", "yes"):
            self.DEBUG = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


def get_youtube_api_key() -> str:
    """Obtiene la API Key de YouTube desde las variables de entorno.
    
    Returns:
        str: La API key o cadena vacía si no está configurada.
    """
    return os.getenv("YOUTUBE_API_KEY", "")


def is_youtube_api_key_configured() -> bool:
    """Verifica si la API Key de YouTube está configurada."""
    return bool(get_youtube_api_key().strip())


def mask_api_key(key: str, visible_start: int = 2, visible_end: int = 2) -> str:
    """Enmascara una API key mostrando solo los primeros y últimos caracteres.
    
    Args:
        key: La API key a enmascarar.
        visible_start: Número de caracteres visibles al inicio.
        visible_end: Número de caracteres visibles al final.
        
    Returns:
        str: La API key enmascarada (ej: "sk-****...b3x")
    """
    if not key or len(key) <= visible_start + visible_end:
        return "****"
    return key[:visible_start] + "*" * (len(key) - visible_start - visible_end) + key[-visible_end:]
