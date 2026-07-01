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

    # ComfyUI
    COMFYUI_URL: str = os.getenv("COMFYUI_URL", "http://localhost:8188")
    COMFYUI_API_KEY: str = os.getenv("COMFYUI_API_KEY", "")

    # FFmpeg
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")

    # Pipeline
    PIPELINE_QUEUE_DIR: str = os.getenv("PIPELINE_QUEUE_DIR", "data/pipeline_queue")
    PIPELINE_OUTPUT_DIR: str = os.getenv("PIPELINE_OUTPUT_DIR", "data/pipeline_output")
    PIPELINE_REFERENCES_DIR: str = os.getenv("PIPELINE_REFERENCES_DIR", "data/pipeline_references")
    PIPELINE_POLL_INTERVAL: int = int(os.getenv("PIPELINE_POLL_INTERVAL", "5"))
    PIPELINE_TIMEOUT: int = int(os.getenv("PIPELINE_TIMEOUT", "1500"))

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
