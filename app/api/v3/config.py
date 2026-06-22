"""
app/api/v3/config.py
Rutas de configuración global: APIs, respaldos y ajustes de app.
Orden: rutas fijas ANTES de las parametrizadas ({api_key}, {backup_id}).
"""

import shutil
import zipfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.schemas.v3.config import (
    GlobalConfigOut,
    GlobalConfigUpdate,
    ApisConfig,
    AppSettingsConfig,
    BackupConfig,
    BackupInfo,
    ApiConfig,
)
from app.services.v3.config_service import (
    get_config,
    update_app_settings,
    update_apis,
    update_backup,
    create_backup,
    list_backups,
)
from app.api.v3.auth import get_current_user


router = APIRouter(prefix="/config", tags=["config"])


# ── Rutas FIJAS (definidas antes de las parametrizadas) ─────────────────────

@router.get("", response_model=GlobalConfigOut)
def get_global_config(user: dict = Depends(get_current_user)):
    return get_config()


@router.patch("", response_model=GlobalConfigOut)
def patch_global_config(
    payload: GlobalConfigUpdate,
    user: dict = Depends(get_current_user),
):
    if payload.app is not None:
        update_app_settings(payload.app)
    if payload.apis is not None:
        update_apis(payload.apis)
    if payload.backup is not None:
        update_backup(payload.backup)
    return get_config()


# ── Backup: fija antes de {backup_id} ─────────────────────────────────────────

@router.post("/backups", response_model=BackupInfo)
def trigger_backup(user: dict = Depends(get_current_user)):
    return create_backup()


@router.get("/backups", response_model=list[BackupInfo])
def get_backups(user: dict = Depends(get_current_user)):
    return list_backups()


# ── API key: fija antes de {api_key} ─────────────────────────────────────────

@router.put("/apis/{api_key}", response_model=GlobalConfigOut)
def put_api_config(
    api_key: str,
    payload: ApiConfig,
    user: dict = Depends(get_current_user),
):
    cfg = get_config()
    if not hasattr(cfg.apis, api_key):
        raise HTTPException(status_code=404, detail=f"API '{api_key}' no encontrada")
    updated_apis = cfg.apis.model_dump()
    updated_apis[api_key] = payload.model_dump()
    update_apis(ApisConfig(**updated_apis))
    return get_config()


@router.get("/apis/{api_key}", response_model=ApiConfig)
def get_api_config(
    api_key: str,
    user: dict = Depends(get_current_user),
):
    cfg = get_config()
    if not hasattr(cfg.apis, api_key):
        raise HTTPException(status_code=404, detail=f"API '{api_key}' no encontrada")
    return getattr(cfg.apis, api_key)


# ── Backup parametrizadas ─────────────────────────────────────────────────────

@router.get("/backups/{backup_id}/download")
def download_backup(
    backup_id: str,
    user: dict = Depends(get_current_user),
):
    backups = list_backups()
    match = next((b for b in backups if b.id == backup_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Respaldo no encontrado")

    zip_path = Path(tempfile.gettempdir()) / f"wui_backup_{backup_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in Path(match.path).rglob("*"):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(Path(match.path).parent))

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"wui_backup_{backup_id}.zip",
    )


@router.post("/backups/{backup_id}/restore")
def restore_backup(
    backup_id: str,
    user: dict = Depends(get_current_user),
):
    backups = list_backups()
    match = next((b for b in backups if b.id == backup_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Respaldo no encontrado")

    raw = get_config()
    data_dir = Path("data")

    # Safety backup antes de restaurar
    safety_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    from app.services.v3.config_service import BACKUP_DIR
    safety_path = BACKUP_DIR / f"pre_restore_{safety_id}"
    safety_path.mkdir(parents=True, exist_ok=True)
    if data_dir.exists():
        shutil.copytree(data_dir, safety_path / data_dir.name, dirs_exist_ok=True)

    # Restaurar
    backup_src = Path(match.path)
    for item in ["channels", "users", "prompts", "content"]:
        src = backup_src / item
        dst = data_dir / item
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    return {"ok": True, "safety_backup": str(safety_path)}
