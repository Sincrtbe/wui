"""Configuration settings for Wui v2"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Wui v2"
    ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS_HASH: str = os.getenv("ADMIN_PASS_HASH", "$2b$12$EXAMPLEHASHFORADMINPASS") # Reemplazar con un hash real
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production") # Generar una clave segura en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # YouTube API
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")

    # LLM Config
    LLM_ENDPOINT: str = os.getenv("LLM_ENDPOINT", "http://localhost:11434/api/generate")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama2")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
