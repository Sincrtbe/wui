"""
app/schemas/v3/config.py
Schemas para configuración global y APIs externas de WUI v3.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ApiConfig(BaseModel):
    """Configuración de una API externa."""
    enabled: bool = False
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    extra: dict = Field(default_factory=dict)


class ApisConfig(BaseModel):
    """Todas las APIs externas configurables."""
    minimax: ApiConfig = Field(default_factory=ApiConfig)
    openai: ApiConfig = Field(default_factory=ApiConfig)
    elevenlabs: ApiConfig = Field(default_factory=ApiConfig)
    minimax_tts: ApiConfig = Field(default_factory=ApiConfig)
    comfyui: ApiConfig = Field(default_factory=ApiConfig)
    flux: ApiConfig = Field(default_factory=ApiConfig)


class BackupConfig(BaseModel):
    """Configuración de respaldo."""
    enabled: bool = False
    directory: str = Field(default_factory=lambda: "data/backups")
    auto_backup: bool = True
    max_backups: int = 5


class AppSettingsConfig(BaseModel):
    """Configuración general de la aplicación."""
    data_directory: str = Field(default_factory=lambda: "data")
    app_title: str = "WUI"
    log_level: str = "INFO"


class GlobalConfigOut(BaseModel):
    """Configuración global completa (sin secretos por defecto)."""
    app: AppSettingsConfig = Field(default_factory=AppSettingsConfig)
    apis: ApisConfig = Field(default_factory=ApisConfig)
    backup: BackupConfig = Field(default_factory=BackupConfig)


class GlobalConfigUpdate(BaseModel):
    """Payload para actualizar configuración global."""
    app: Optional[AppSettingsConfig] = None
    apis: Optional[ApisConfig] = None
    backup: Optional[BackupConfig] = None


class BackupInfo(BaseModel):
    """Información de un respaldo disponible."""
    id: str
    path: str
    size_mb: float
    created_at: str
    content: list[str]  # canales, usuarios, etc.


class RestoreRequest(BaseModel):
    backup_id: str
