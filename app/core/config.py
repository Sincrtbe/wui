"""Configuración de la aplicación."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración global de la app."""
    DATABASE_URL: str = "sqlite:///./app.db"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
