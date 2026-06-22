"""
app/services/v3/config_service.py
Servicio para gestionar configuración global de la app.
"""

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.schemas.v3.config import (
    ApisConfig,
    AppSettingsConfig,
    BackupConfig,
    GlobalConfigOut,
    BackupInfo,
    ApiConfig,
)


CONFIG_PATH = Path("data/config.json")
BACKUP_DIR = Path("data/backups")


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def _save_config(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_config() -> GlobalConfigOut:
    raw = _load_config()
    return GlobalConfigOut(
        app=AppSettingsConfig(**raw.get("app", {})),
        apis=ApisConfig(**raw.get("apis", {})),
        backup=BackupConfig(**raw.get("backup", {})),
    )


def update_app_settings(settings_in: AppSettingsConfig) -> GlobalConfigOut:
    raw = _load_config()
    raw["app"] = settings_in.model_dump()
    _save_config(raw)
    return get_config()


def update_apis(apis_in: ApisConfig) -> GlobalConfigOut:
    raw = _load_config()
    raw["apis"] = apis_in.model_dump()
    _save_config(raw)
    return get_config()


def update_backup(backup_in: BackupConfig) -> GlobalConfigOut:
    raw = _load_config()
    raw["backup"] = backup_in.model_dump()
    _save_config(raw)
    return get_config()


def get_api_credential(key: str, field: str) -> Optional[str]:
    """Devuelve el api_key de una API si está habilitada, sin exponerla completa."""
    raw = _load_config()
    apis = raw.get("apis", {})
    api_conf = apis.get(key, {})
    if api_conf.get("enabled") and api_conf.get(field):
        return api_conf[field]
    return None


def create_backup() -> BackupInfo:
    """Crea un respaldo del directorio de datos."""
    raw = _load_config()
    backup_cfg = BackupConfig(**raw.get("backup", {}))

    backup_id = str(uuid.uuid4())[:8]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"backup_{ts}_{backup_id}"
    backup_path.mkdir(parents=True, exist_ok=True)

    data_dir = Path(raw.get("app", {}).get("data_directory", "data"))

    if data_dir.exists():
        for item in ["channels", "users", "prompts", "content"]:
            src = data_dir / item
            if src.exists():
                dst = backup_path / item
                shutil.copytree(src, dst, dirs_exist_ok=True)

    # Guardar metadata
    meta = {
        "id": backup_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "app_version": "3.0.0",
    }
    with open(backup_path / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    info = BackupInfo(
        id=backup_id,
        path=str(backup_path),
        size_mb=round(sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file()) / 1024 / 1024, 2),
        created_at=meta["created_at"],
        content=list(
            set(
                p.name for p in backup_path.iterdir()
                if p.is_dir() and p.name not in ("__pycache__",)
            )
        ),
    )

    # Rotar backups
    _rotate_backups(backup_cfg.max_backups)

    return info


def _rotate_backups(max_backups: int) -> None:
    backups = sorted(BACKUP_DIR.glob("backup_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in backups[max_backups:]:
        shutil.rmtree(old)


def list_backups() -> list[BackupInfo]:
    backups = []
    for bp in sorted(BACKUP_DIR.glob("backup_*"), key=lambda p: p.stat().st_mtime, reverse=True):
        meta_path = bp / "meta.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            info = BackupInfo(
                id=meta.get("id", bp.name),
                path=str(bp),
                size_mb=round(sum(f.stat().st_size for f in bp.rglob("*") if f.is_file()) / 1024 / 1024, 2),
                created_at=meta.get("created_at", ""),
                content=list(set(p.name for p in bp.iterdir() if p.is_dir())),
            )
            backups.append(info)
    return backups
