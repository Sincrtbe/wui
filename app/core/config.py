# app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Wui v2"
    ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS_HASH: str = os.getenv(
        "ADMIN_PASS_HASH", "$2b$12$WApznUPhDubN0oeveSXHp.s7DS3MijWjj5KqZaMLi.ODqO8JOgmAi"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # YouTube API
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")

    # LLM Config
    LLM_ENDPOINT: str = os.getenv("LLM_ENDPOINT", "http://localhost:11434/api/generate")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama2")

    # Server
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "9080"))

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
