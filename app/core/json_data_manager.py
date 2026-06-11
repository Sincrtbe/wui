"""
app/core/json_data_manager.py
Capa de acceso a datos (DAL) para persistencia en archivos JSON.
Centraliza toda la interacción con el sistema de archivos para evitar
corrupción o inconsistencias de datos.
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar("T")

# Directorio base de datos
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Lock para concurrencia segura en escrituras
_write_lock = threading.Lock()


def _get_entity_path(entity_name: str, item_id: Optional[str] = None) -> Path:
    """Obtiene la ruta completa para un entidad JSON."""
    path = DATA_DIR / entity_name
    path.mkdir(parents=True, exist_ok=True)
    if item_id:
        return path / f"{item_id}.json"
    return path


def _serialize_datetime(obj: Any) -> Any:
    """Serializa objetos datetime a strings ISO."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def _deserialize_datetime(obj: Any) -> Any:
    """Deserializa strings ISO a objetos datetime."""
    if isinstance(obj, str) and "T" in obj:
        try:
            return datetime.fromisoformat(obj)
        except ValueError:
            pass
    return obj


def read_json_file(entity_name: str, item_id: str) -> Optional[Dict[str, Any]]:
    """Lee un archivo JSON individual de una entidad."""
    file_path = _get_entity_path(entity_name, item_id)
    if not file_path.exists():
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(
    entity_name: str, item_id: str, data: Dict[str, Any]
) -> None:
    """Escribe un archivo JSON individual de forma segura."""
    file_path = _get_entity_path(entity_name, item_id)
    with _write_lock:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=_serialize_datetime)


def list_json_files(entity_name: str) -> List[Dict[str, Any]]:
    """Lista todos los archivos JSON de una entidad."""
    path = _get_entity_path(entity_name)
    items = []
    if not path.exists():
        return items
    for filename in sorted(path.iterdir()):
        if filename.is_file() and filename.suffix == ".json":
            item_id = filename.stem
            item_data = read_json_file(entity_name, item_id)
            if item_data:
                items.append(item_data)
    return items


def delete_json_file(entity_name: str, item_id: str) -> bool:
    """Elimina un archivo JSON de una entidad."""
    file_path = _get_entity_path(entity_name, item_id)
    if file_path.exists():
        with _write_lock:
            file_path.unlink()
        return True
    return False


def update_json_file(
    entity_name: str, item_id: str, updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Actualiza un archivo JSON existente con los campos proporcionados."""
    existing = read_json_file(entity_name, item_id)
    if existing is None:
        return None
    existing.update(updates)
    existing["updated_at"] = datetime.now(timezone.utc).isoformat()
    write_json_file(entity_name, item_id, existing)
    return existing


def count_json_files(entity_name: str) -> int:
    """Cuenta el número de archivos JSON en una entidad."""
    path = _get_entity_path(entity_name)
    if not path.exists():
        return 0
    return sum(1 for f in path.iterdir() if f.is_file() and f.suffix == ".json")


# ── Configuración global (archivo único) ────────────────────────────────────


def read_global_config() -> Dict[str, Any]:
    """Lee la configuración global del sistema."""
    config_path = DATA_DIR / "config.json"
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_global_config(config_data: Dict[str, Any]) -> None:
    """Escribe la configuración global del sistema."""
    config_path = DATA_DIR / "config.json"
    with _write_lock:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2, default=_serialize_datetime)


def init_default_config() -> Dict[str, Any]:
    """Inicializa la configuración global con valores por defecto si no existe."""
    config = read_global_config()
    if not config:
        config = {
            "youtube_api_key": "",
            "llm_api_key": "",
            "llm_endpoint": "http://localhost:11434/api/generate",
            "llm_model": "llama2",
            "admin_user": "admin",
            "admin_pass_hash": "",
            "analytics_schedule": "0 2 * * *",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        write_global_config(config)
    return config
