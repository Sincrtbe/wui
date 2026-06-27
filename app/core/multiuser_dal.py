"""
app/core/multiuser_dal.py
Capa de Acceso a Datos (DAL) para WUI v3 — Arquitectura multi-usuario.
Gestiona la jerarquía: data/users/{user_id}/ → channels/ → content/
con versionado completo y thread-safety.
"""

import json
import os
import re
import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

BASE_DATA = Path(__file__).parent.parent.parent / "data"
USERS_DIR = BASE_DATA / "users"
SYSTEM_DIR = BASE_DATA / "system"
SYSTEM_PROMPTS_DIR = SYSTEM_DIR / "default_prompts"

_write_lock = threading.Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de ruta
# ─────────────────────────────────────────────────────────────────────────────

def _user_dir(user_id: str) -> Path:
    p = USERS_DIR / user_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _channel_dir(user_id: str, channel_id: str) -> Path:
    p = _user_dir(user_id) / "channels" / channel_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _content_dir(user_id: str, channel_id: str, content_id: str) -> Path:
    p = _channel_dir(user_id, channel_id) / "content" / content_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _versions_dir(user_id: str, channel_id: str, content_id: str) -> Path:
    p = _content_dir(user_id, channel_id, content_id) / "versions"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _assets_dir(user_id: str, channel_id: str, content_id: str, asset_type: str) -> Path:
    p = _content_dir(user_id, channel_id, content_id) / "assets" / asset_type
    p.mkdir(parents=True, exist_ok=True)
    return p


# ─────────────────────────────────────────────────────────────────────────────
# helpers de serialización
# ─────────────────────────────────────────────────────────────────────────────

def _serialize(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def _dump(data: dict, path: Path) -> None:
    with _write_lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=_serialize)


def _load(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# User
# ─────────────────────────────────────────────────────────────────────────────

def create_user(name: str, email: str, password_hash: str) -> dict:
    user_id = str(uuid.uuid4())
    data = {
        "id": user_id,
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _dump(data, _user_dir(user_id) / "profile.json")
    _dump({}, _user_dir(user_id) / "settings.json")
    return data


def get_user(user_id: str) -> Optional[dict]:
    return _load(_user_dir(user_id) / "profile.json")


def get_user_by_email(email: str) -> Optional[dict]:
    """Busca un usuario por email escaneando el directorio de usuarios."""
    for d in USERS_DIR.iterdir():
        if d.is_dir():
            p = d / "profile.json"
            u = _load(p)
            if u and u.get("email", "").lower() == email.lower():
                return u
    return None


def update_user(user_id: str, updates: dict) -> Optional[dict]:
    path = _user_dir(user_id) / "profile.json"
    data = _load(path)
    if not data:
        return None
    data.update(updates)
    data["updated_at"] = _utc_now()
    _dump(data, path)
    return data


def list_users() -> list[dict]:
    users = []
    for d in USERS_DIR.iterdir():
        if d.is_dir():
            p = d / "profile.json"
            u = _load(p)
            if u:
                users.append(u)
    return users


def delete_user(user_id: str) -> bool:
    user_path = _user_dir(user_id)
    if not user_path.exists():
        return False
    shutil.rmtree(user_path)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Prompts (compartidos por usuario)
# ─────────────────────────────────────────────────────────────────────────────

def create_prompt(
    user_id: str,
    name: str,
    content: str,
    category: str = "custom",
    description: str = "",
    tags: Optional[list[str]] = None,
    variables_schema: Optional[list[dict]] = None,
) -> dict:
    prompt_id = str(uuid.uuid4())
    data = {
        "id": prompt_id,
        "user_id": user_id,
        "name": name,
        "content": content,
        "category": category,
        "description": description,
        "tags": tags if tags is not None else [],
        "variables_schema": variables_schema if variables_schema is not None else [],
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _dump(data, _user_dir(user_id) / "prompts" / f"{prompt_id}.json")
    return data


def get_prompt(user_id: str, prompt_id: str) -> Optional[dict]:
    return _load(_user_dir(user_id) / "prompts" / f"{prompt_id}.json")


def list_prompts(user_id: str, category: str = None, tag: str = None) -> list[dict]:
    prompts_dir = _user_dir(user_id) / "prompts"
    if not prompts_dir.exists():
        return []
    results = []
    for f in prompts_dir.iterdir():
        if f.suffix != ".json":
            continue
        p = _load(f)
        if not p:
            continue
        if category and p.get("category") != category:
            continue
        if tag and tag not in p.get("tags", []):
            continue
        results.append(p)
    return results


def update_prompt(user_id: str, prompt_id: str, updates: dict) -> Optional[dict]:
    path = _user_dir(user_id) / "prompts" / f"{prompt_id}.json"
    data = _load(path)
    if not data:
        return None
    data.update(updates)
    data["updated_at"] = _utc_now()
    _dump(data, path)
    return data


def delete_prompt(user_id: str, prompt_id: str) -> bool:
    path = _user_dir(user_id) / "prompts" / f"{prompt_id}.json"
    if not path.exists():
        return False
    path.unlink()
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Prompts del sistema (default)
# ─────────────────────────────────────────────────────────────────────────────

def create_system_prompt(
    name: str,
    content: str,
    category: str,
    description: str = "",
    tags: Optional[list[str]] = None,
    variables_schema: Optional[list[dict]] = None,
    is_default: bool = False,
) -> dict:
    prompt_id = str(uuid.uuid4())
    data = {
        "id": prompt_id,
        "name": name,
        "content": content,
        "category": category,
        "description": description,
        "tags": tags if tags is not None else [],
        "variables_schema": variables_schema or [],
        "is_system": True,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    SYSTEM_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    _dump(data, SYSTEM_PROMPTS_DIR / f"{prompt_id}.json")
    return data


def list_system_prompts(category: Optional[str] = None) -> list[dict]:
    if not SYSTEM_PROMPTS_DIR.exists():
        return []
    results = []
    for f in SYSTEM_PROMPTS_DIR.iterdir():
        if f.suffix != ".json":
            continue
        p = _load(f)
        if not p:
            continue
        if category and p.get("category") != category:
            continue
        results.append(p)
    return results


def get_system_prompt(prompt_id: str) -> Optional[dict]:
    return _load(SYSTEM_PROMPTS_DIR / f"{prompt_id}.json")


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Assignments (asignación de prompt → etapa)
# ─────────────────────────────────────────────────────────────────────────────

def _pipeline_path(user_id: str, channel_id: Optional[str] = None) -> Path:
    if channel_id:
        return _channel_dir(user_id, channel_id) / "pipeline_assignments.json"
    return _user_dir(user_id) / "pipeline_assignments.json"


PIPELINE_STAGES = [
    "idea_generation",
    "script_writing",
    "scene_graphic",
    "scene_video",
    "tts",
]


def get_pipeline_assignments(user_id: str, channel_id: Optional[str] = None) -> dict:
    """Retorna un dict {stage: prompt_id} con las asignaciones vigentes."""
    path = _pipeline_path(user_id, channel_id)
    data = _load(path)
    return data if data else {}


def set_pipeline_assignment(
    user_id: str,
    stage: str,
    prompt_id: str,
    channel_id: Optional[str] = None,
) -> dict:
    if stage not in PIPELINE_STAGES:
        raise ValueError(f"Stage inválido: {stage}. Debe ser uno de {PIPELINE_STAGES}")
    path = _pipeline_path(user_id, channel_id)
    data = _load(path) or {}
    data[stage] = prompt_id
    _dump(data, path)
    return data


def remove_pipeline_assignment(
    user_id: str,
    stage: str,
    channel_id: Optional[str] = None,
) -> dict:
    path = _pipeline_path(user_id, channel_id)
    data = _load(path) or {}
    data.pop(stage, None)
    _dump(data, path)
    return data


def resolve_pipeline_prompt(
    user_id: str,
    stage: str,
    channel_id: Optional[str] = None,
) -> Optional[dict]:
    """
    Resuelve qué prompt usar para una etapa:
    1. Si channel_id tiene asignación → usar esa
    2. Si user tiene asignación global → usar esa
    3. Buscar default del sistema para esa categoría de stage
    """
    # 1. Canal
    channel_assignments = get_pipeline_assignments(user_id, channel_id)
    if stage in channel_assignments:
        prompt_id = channel_assignments[stage]
        p = _load(_user_dir(user_id) / "prompts" / f"{prompt_id}.json") if not (SYSTEM_PROMPTS_DIR / f"{prompt_id}.json").exists() else _load(SYSTEM_PROMPTS_DIR / f"{prompt_id}.json")
        return p

    # 2. Usuario global
    user_assignments = get_pipeline_assignments(user_id, None)
    if stage in user_assignments:
        prompt_id = user_assignments[stage]
        p = get_prompt(user_id, prompt_id)
        if p:
            return p
        p = get_system_prompt(prompt_id)
        if p:
            return p

    # 3. Default del sistema según stage → category mapping
    stage_to_category = {
        "idea_generation": "storming",
        "script_writing": "development",
        "scene_graphic": "scene_graphic",
        "scene_video": "scene_video",
        "tts": "tts",
    }
    category = stage_to_category.get(stage)
    system_prompts = list_system_prompts(category=category)
    for sp in system_prompts:
        if sp.get("is_default"):
            return sp
    return system_prompts[0] if system_prompts else None


# ─────────────────────────────────────────────────────────────────────────────
# Channel
# ─────────────────────────────────────────────────────────────────────────────

def create_channel(
    user_id: str,
    name: str,
    platform: str = "youtube",
    platform_id: str = "",
    url: str = "",
    topic: str = "",
) -> dict:
    channel_id = str(uuid.uuid4())
    data = {
        "id": channel_id,
        "user_id": user_id,
        "name": name,
        "platform": platform,
        "platform_id": platform_id,
        "url": url,
        "thumbnail": "",
        "subscribers": 0,
        "description": "",
        "status": "active",
        "voice_sample_path": "",
        "topic": topic,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
        "last_sync": None,
    }
    channel_dir = _channel_dir(user_id, channel_id)
    _dump(data, channel_dir / "channel.json")
    # Crear subdirectorios
    (channel_dir / "voice_sample").mkdir(exist_ok=True)
    (channel_dir / "content").mkdir(exist_ok=True)
    return data


def get_channel(user_id: str, channel_id: str) -> Optional[dict]:
    return _load(_channel_dir(user_id, channel_id) / "channel.json")


def list_channels(user_id: str) -> list[dict]:
    channels_dir = _user_dir(user_id) / "channels"
    if not channels_dir.exists():
        return []
    results = []
    for d in channels_dir.iterdir():
        if not d.is_dir():
            continue
        c = _load(d / "channel.json")
        if c:
            results.append(c)
    return results


def update_channel(user_id: str, channel_id: str, updates: dict) -> Optional[dict]:
    path = _channel_dir(user_id, channel_id) / "channel.json"
    data = _load(path)
    if not data:
        return None
    data.update(updates)
    data["updated_at"] = _utc_now()
    _dump(data, path)
    return data


def delete_channel(user_id: str, channel_id: str) -> bool:
    path = _channel_dir(user_id, channel_id)
    if not path.exists():
        return False
    shutil.rmtree(path)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Content Item (idea/guion/proyecto)
# ─────────────────────────────────────────────────────────────────────────────

def create_content_item(
    user_id: str,
    channel_id: str,
    title: str,
    stage: str = "idea",
    tags: Optional[list[str]] = None,
    idea_notes: str = "",
    structured_ideas: str = "[]",
    parent_id: Optional[str] = None,
) -> dict:
    content_id = str(uuid.uuid4())
    data = {
        "id": content_id,
        "user_id": user_id,
        "channel_id": channel_id,
        "parent_id": parent_id,
        "title": title,
        "stage": stage,
        "status": "draft",
        "tags": tags if tags is not None else [],
        "current_version_id": None,
        "idea_notes": idea_notes,
        "structured_ideas": structured_ideas,
        "script_content": "",
        "scene_prompts": [],
        "generated_images": [],
        "generated_videos": [],
        "tts_result": None,
        "notes": [],  # notas visibles en todos los stages hacia atrás
        "scores": [],  # scores agregados
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    content_dir = _content_dir(user_id, channel_id, content_id)
    _dump(data, content_dir / "content.json")
    (content_dir / "versions").mkdir(parents=True, exist_ok=True)
    (content_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
    (content_dir / "assets" / "videos").mkdir(parents=True, exist_ok=True)
    (content_dir / "assets" / "audio").mkdir(parents=True, exist_ok=True)
    return data


def get_content_item(user_id: str, channel_id: str, content_id: str) -> Optional[dict]:
    return _load(_content_dir(user_id, channel_id, content_id) / "content.json")


def list_content_items(user_id: str, channel_id: Optional[str] = None, stage: Optional[str] = None, status: Optional[str] = None) -> list[dict]:
    """
    Lista content items. Si channel_id es None, busca en todos los canales del usuario.
    """
    if channel_id:
        return _list_content_items_single(user_id, channel_id, stage, status)
    else:
        results = []
        for ch in list_channels(user_id):
            results.extend(_list_content_items_single(user_id, ch["id"], stage, status))
        return results


def _list_content_items_single(user_id: str, channel_id: str, stage: Optional[str], status: Optional[str]) -> list[dict]:
    content_dir = _channel_dir(user_id, channel_id) / "content"
    if not content_dir.exists():
        return []
    results = []
    for d in content_dir.iterdir():
        if not d.is_dir():
            continue
        c = _load(d / "content.json")
        if not c:
            continue
        if stage and c.get("stage") != stage:
            continue
        if status and c.get("status") != status:
            continue
        results.append(c)
    return results


def update_content_item(
    user_id: str,
    channel_id: str,
    content_id: str,
    updates: dict,
) -> Optional[dict]:
    path = _content_dir(user_id, channel_id, content_id) / "content.json"
    data = _load(path)
    if not data:
        return None
    data.update(updates)
    data["updated_at"] = _utc_now()
    _dump(data, path)
    return data


def delete_content_item(user_id: str, channel_id: str, content_id: str) -> bool:
    path = _content_dir(user_id, channel_id, content_id)
    if not path.exists():
        return False
    shutil.rmtree(path)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Notes (visibles en todos los stages hacia atrás)
# ─────────────────────────────────────────────────────────────────────────────

def add_note(
    user_id: str,
    channel_id: str,
    content_id: str,
    note_type: str,  # strength | weakness | improvement | general
    content: str,
) -> Optional[dict]:
    """
    Añade una nota al content_item (visible en todos los stages).
    """
    path = _content_dir(user_id, channel_id, content_id) / "content.json"
    data = _load(path)
    if not data:
        return None
    note = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "note_type": note_type,
        "content": content,
        "resolved": False,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    notes = data.get("notes", [])
    notes.append(note)
    data["notes"] = notes
    data["updated_at"] = _utc_now()
    _dump(data, path)
    return note


def update_note(
    user_id: str,
    channel_id: str,
    content_id: str,
    note_id: str,
    updates: dict,
) -> Optional[dict]:
    path = _content_dir(user_id, channel_id, content_id) / "content.json"
    data = _load(path)
    if not data:
        return None
    notes = data.get("notes", [])
    for n in notes:
        if n["id"] == note_id:
            n.update(updates)
            n["updated_at"] = _utc_now()
            break
    data["updated_at"] = _utc_now()
    _dump(data, path)
    return next((n for n in notes if n["id"] == note_id), None)


def delete_note(
    user_id: str,
    channel_id: str,
    content_id: str,
    note_id: str,
) -> bool:
    path = _content_dir(user_id, channel_id, content_id) / "content.json"
    data = _load(path)
    if not data:
        return False
    notes = data.get("notes", [])
    original_len = len(notes)
    notes = [n for n in notes if n["id"] != note_id]
    if len(notes) == original_len:
        return False
    data["notes"] = notes
    data["updated_at"] = _utc_now()
    _dump(data, path)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Versions (snapshots)
# ─────────────────────────────────────────────────────────────────────────────

def create_version(
    user_id: str,
    channel_id: str,
    content_id: str,
    prompt_id: Optional[str] = None,
    prompt_version_id: Optional[str] = None,
) -> dict:
    """
    Crea un snapshot (versión) del estado actual del content_item.
    Incrementa version_number secuencialmente.
    """
    content = get_content_item(user_id, channel_id, content_id)
    if not content:
        raise ValueError(f"ContentItem no encontrado: {content_id}")

    versions_dir = _versions_dir(user_id, channel_id, content_id)
    existing = [f.stem for f in versions_dir.glob("*.json")]
    existing_numbers = [int(f) for f in existing if f.isdigit()]
    next_number = max(existing_numbers) + 1 if existing_numbers else 1

    version_data = {
        "id": str(uuid.uuid4()),
        "content_item_id": content_id,
        "version_number": next_number,
        "stage_snapshot": content.get("stage", ""),
        "data": {
            "idea_notes": content.get("idea_notes", ""),
            "script_content": content.get("script_content", ""),
            "scene_prompts": content.get("scene_prompts", []),
            "generated_images": content.get("generated_images", []),
            "generated_videos": content.get("generated_videos", []),
            "tts_result": content.get("tts_result"),
        },
        "prompt_id": prompt_id,
        "prompt_version_id": prompt_version_id,
        "created_at": _utc_now(),
    }
    _dump(version_data, versions_dir / f"{next_number}.json")

    # Actualizar current_version_id en el content
    update_content_item(user_id, channel_id, content_id, {
        "current_version_id": version_data["id"]
    })
    return version_data


def get_version(
    user_id: str,
    channel_id: str,
    content_id: str,
    version_number: int,
) -> Optional[dict]:
    return _load(_versions_dir(user_id, channel_id, content_id) / f"{version_number}.json")


def list_versions(
    user_id: str,
    channel_id: str,
    content_id: str,
) -> list[dict]:
    versions_dir = _versions_dir(user_id, channel_id, content_id)
    if not versions_dir.exists():
        return []
    versions = []
    for f in sorted(versions_dir.glob("*.json"), key=lambda x: int(x.stem) if x.stem.isdigit() else 0):
        v = _load(f)
        if v:
            versions.append(v)
    return versions


def revert_to_version(
    user_id: str,
    channel_id: str,
    content_id: str,
    version_number: int,
) -> Optional[dict]:
    """
    Revierte el content_item al estado de la versión especificada.
    No modifica el historial de versiones.
    """
    version = get_version(user_id, channel_id, content_id, version_number)
    if not version:
        return None
    version_data = version["data"]
    updates = {
        "idea_notes": version_data.get("idea_notes", ""),
        "script_content": version_data.get("script_content", ""),
        "scene_prompts": version_data.get("scene_prompts", []),
        "generated_images": version_data.get("generated_images", []),
        "generated_videos": version_data.get("generated_videos", []),
        "tts_result": version_data.get("tts_result"),
    }
    return update_content_item(user_id, channel_id, content_id, updates)


# ─────────────────────────────────────────────────────────────────────────────
# Scores
# ─────────────────────────────────────────────────────────────────────────────

def add_score(
    user_id: str,
    channel_id: str,
    content_id: str,
    metric_type: str,  # views | ctr | retention | likes_ratio | ai_score
    value: float,
    source: str = "manual",  # youtube_api | manual | ai_predicted
    notes: str = "",
) -> Optional[dict]:
    path = _content_dir(user_id, channel_id, content_id) / "content.json"
    data = _load(path)
    if not data:
        return None
    score = {
        "id": str(uuid.uuid4()),
        "metric_type": metric_type,
        "value": value,
        "source": source,
        "notes": notes,
        "recorded_at": _utc_now(),
    }
    scores = data.get("scores", [])
    scores.append(score)
    data["scores"] = scores
    data["updated_at"] = _utc_now()
    _dump(data, path)
    return score


def get_scores(
    user_id: str,
    channel_id: str,
    content_id: str,
) -> list[dict]:
    content = get_content_item(user_id, channel_id, content_id)
    if not content:
        return []
    return content.get("scores", [])


# ─────────────────────────────────────────────────────────────────────────────
# Assets
# ─────────────────────────────────────────────────────────────────────────────

def save_asset_path(
    user_id: str,
    channel_id: str,
    content_id: str,
    asset_type: str,  # images | videos | audio
    filename: str,
    relative_path: str,
) -> str:
    """Registra un asset en el content_item y devuelve la ruta relativa."""
    content = get_content_item(user_id, channel_id, content_id)
    if not content:
        raise ValueError(f"ContentItem no encontrado: {content_id}")
    asset_entry = {
        "id": str(uuid.uuid4()),
        "asset_type": asset_type,
        "filename": filename,
        "relative_path": relative_path,
        "created_at": _utc_now(),
    }
    if asset_type == "images":
        key = "generated_images"
    elif asset_type == "videos":
        key = "generated_videos"
    else:
        key = "tts_result"

    current = content.get(key, [])
    if isinstance(current, list):
        current.append(asset_entry)
    else:
        current = asset_entry
    update_content_item(user_id, channel_id, content_id, {key: current})
    return relative_path


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Renderer (resuelve {{{variables}}})
# ─────────────────────────────────────────────────────────────────────────────

VARIABLE_PATTERN = re.compile(r"\{\{\{([^}]+)\}\}\}")
ALLOWED_VARIABLES = {
    "tema", "titulo", "concepto", "nombre_canal", "descripcion_canal",
    "audiencia", "tono", "duracion_objetivo", "escena_num", "total_escenas",
    "nombre_personaje", "personalidad_personaje", "fecha_actual",
    # Scoring
    "score_vistas", "score_ctr", "score_retention", "score_likes_ratio", "score_ai",
}


def extract_variables(prompt_content: str) -> list[str]:
    """Extrae todas las {{{variable}}} usadas en un prompt."""
    return VARIABLE_PATTERN.findall(prompt_content)


def validate_variables(prompt_content: str) -> tuple[list[str], list[str]]:
    """Retorna (válidas, inválidas)"""
    found = extract_variables(prompt_content)
    valid = [v for v in found if v.strip() in ALLOWED_VARIABLES]
    invalid = [v for v in found if v.strip() not in ALLOWED_VARIABLES]
    return valid, invalid


def render_prompt(prompt_content: str, context: dict) -> str:
    """
    Renderiza un prompt reemplazando {{{variable}}} con valores del contexto.
    Las variables no encontradas se dejan como {{{variable}}}.
    """
    def replacer(match):
        key = match.group(1).strip()
        if key in context:
            val = context[key]
            return str(val) if val is not None else ""
        return match.group(0)

    return VARIABLE_PATTERN.sub(replacer, prompt_content)


def build_render_context(
    user_id: str,
    channel_id: str,
    content_id: Optional[str] = None,
    extra: Optional[dict] = None,
) -> dict:
    """
    Construye el contexto completo para renderizar un prompt.
    Incluye datos del canal, content_item (si se provee), y variables especiales.
    """
    ctx = {
        "fecha_actual": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    if extra:
        ctx.update(extra)
    if channel_id:
        ch = get_channel(user_id, channel_id)
        if ch:
            ctx["nombre_canal"] = ch.get("name", "")
            ctx["descripcion_canal"] = ch.get("description", "")
            ctx["plataforma"] = ch.get("platform", "")
    if content_id:
        c = get_content_item(user_id, channel_id, content_id)
        if c:
            ctx["titulo"] = c.get("title", "")
            ctx["idea_notas"] = c.get("idea_notes", "")
            ctx["guion"] = c.get("script_content", "")
            # Extraer campos de structured_ideas (JSON puede venir como str o list)
            raw_si = c.get("structured_ideas", [])
            if isinstance(raw_si, str):
                try:
                    raw_si = json.loads(raw_si)
                except (json.JSONDecodeError, TypeError):
                    raw_si = []
            # Si es una lista, tomar el primer elemento (idea individual)
            if isinstance(raw_si, list) and len(raw_si) > 0:
                si = raw_si[0] if isinstance(raw_si[0], dict) else {}
            elif isinstance(raw_si, dict):
                si = raw_si
            else:
                si = {}
            ctx["concepto"] = si.get("concepto", si.get("concept", ""))
            ctx["duracion_objetivo"] = si.get("duracion", si.get("duration", "largo"))
            ctx["angulo_viral"] = si.get("angulo_viral", si.get("viral_angle", ""))
            ctx["hook_visual"] = si.get("hook_visual", si.get("visual_hook", ""))
            ctx["formato"] = si.get("formato", si.get("format", ""))
            ctx["score_potencial"] = si.get("score_potencial", si.get("potential_score", ""))
            # Scores si existen
            scores = c.get("scores", [])
            for s in scores:
                mt = s.get("metric_type", "")
                val = s.get("value", 0)
                if mt == "views":
                    ctx["score_vistas"] = val
                elif mt == "ctr":
                    ctx["score_ctr"] = val
                elif mt == "retention":
                    ctx["score_retention"] = val
                elif mt == "likes_ratio":
                    ctx["score_likes_ratio"] = val
                elif mt == "ai_score":
                    ctx["score_ai"] = val
    return ctx


# ─────────────────────────────────────────────────────────────────────────────
# Inicialización del sistema
# ─────────────────────────────────────────────────────────────────────────────

def init_system_dirs():
    """Crea la estructura base de directorios si no existe."""
    USERS_DIR.mkdir(parents=True, exist_ok=True)
    SYSTEM_DIR.mkdir(parents=True, exist_ok=True)
    SYSTEM_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)


def seed_default_prompts():
    """Crea los prompts default del sistema para cada etapa del pipeline."""
    defaults = [
        {
            "name": "Lluvia de Ideas Viral",
            "category": "storming",
            "description": "Genera 5 ideas virales para el tema dado",
            "tags": ["youtube", "viral", "ideas"],
            "variables_schema": [{"name": "tema", "type": "string", "required": True}],
            "content": """Eres un estratega de contenido viral con 10+ años de experiencia.

Genera 5 ideas ÚNICAS para el tema: {{{tema}}}

Formato JSON obligatorio:
{
  "ideas": [
    {
      "titulo": "máximo 60 caracteres",
      "concepto": "una frase que resume la premisa",
      "angulo_viral": "por qué la gente compartirá esto",
      "hook_visual": "qué se ve en los primeros 3 segundos",
      "duracion": "corto|medio|largo",
      "formato": "tutorial|top10|storytelling|experimento|comparacion",
      "score_potencial": 1-10
    }
  ]
}

Reglas:
- Títulos máximo 60 caracteres
- Cada idea debe tener un ÁNGULO DIFERENTE
- Mínimo un elemento de contradicción, dato contraintuitivo o urgencia""",
        },
        {
            "name": "Desarrollo de Guion",
            "category": "development",
            "description": "Desarrolla una idea en guion estructurado",
            "tags": ["youtube", "guion", "desarrollo"],
            "variables_schema": [
                {"name": "titulo", "type": "string", "required": True},
                {"name": "concepto", "type": "string", "required": True},
                {"name": "duracion_objetivo", "type": "string", "required": False},
            ],
            "content": """Eres un escritor de guiones para YouTube.

Desarrolla el siguiente concepto en un guion completo:

Título: {{{titulo}}}
Concepto: {{{concepto}}}
Duración objetivo: {{{duracion_objetivo}}}

Estructura del guion:
1. HOOK (primeros 10 segundos) - gancho visual + pregunta/contradicción
2. CONTEXTO (30 segundos) - información necesaria
3. NÚCLEO (parte principal) - desarrollo con datos, historias, ejemplos
4. CIERRE - conclusión + call to action

Para cada escena incluye:
- Texto del guion
- Descripción visual
- Duración estimada
- Prompt para imagen (si aplica)
- Prompt para video (si aplica)

Devuelve el guion en formato estructurado.""",
        },
        {
            "name": "Escena Gráfica (Flux 2.0)",
            "category": "scene_graphic",
            "description": "Crea prompts optimizados para Flux 2.0",
            "tags": ["flux", "imagen", "scene"],
            "variables_schema": [
                {"name": "titulo", "type": "string", "required": True},
                {"name": "descripcion_escena", "type": "string", "required": True},
                {"name": "momento", "type": "string", "required": False},
            ],
            "content": """Genera 3 prompts OPTIMIZADOS para Flux 2.0.

Contexto: {{{titulo}}}
Escena: {{{descripcion_escena}}}
Momento: {{{momento}}}

Estructura del prompt Flux 2.0:
[Estilo visual], [Sujeto], [Acción], [Entorno], [Iluminación], [Cámara], [Atmósfera] --ar 16:9 --v 2

Incluye siempre:
- Prompt negativo: blurry, deformed, ugly, bad anatomy, cartoon
- 3 variaciones con diferentes estilos (cinematic, photorealistic, illustration)

Ejemplo de salida:
{
  "prompts": [
    {"prompt": "..., --ar 16:9 --v 2", "estilo": "cinematic", "negativo": "..."},
    ...
  ]
}""",
        },
        {
            "name": "Escena de Video (Wan 2.2)",
            "category": "scene_video",
            "description": "Crea prompts para Wan 2.2",
            "tags": ["wan", "video", "scene"],
            "variables_schema": [
                {"name": "descripcion_escena", "type": "string", "required": True},
                {"name": "titulo", "type": "string", "required": False},
            ],
            "content": """Genera prompts para Wan 2.2 (video AI).

Escena: {{{descripcion_escena}}}
Título del video: {{{titulo}}}

Para cada prompt incluye:
- Descripción de movimiento de cámara
- Transición desde escena anterior
- Descripción de lo que ocurre en pantalla
- Duración sugerida (2-5 segundos)
- Estilo visual (consistente con Flux)

Salida JSON:
{
  "prompts_video": [
    {"prompt": "...", "duracion": "3s", "camara": "tracking shot", "transicion": "cut"}
  ]
}""",
        },
        {
            "name": "TTS Narración",
            "category": "tts",
            "description": "Prepara texto para text-to-speech",
            "tags": ["tts", "narracion", "audio"],
            "variables_schema": [
                {"name": "guion", "type": "string", "required": True},
                {"name": "tono", "type": "string", "required": False},
            ],
            "content": """Prepara el siguiente guion para text-to-speech.

Guion: {{{guion}}}
Tono deseado: {{{tono}}}

Instrucciones:
- Divide en bloques de 2-3 oraciones para pausas naturales
- Añade marcas de entonación: [PAUSA], [ÉNFASTS], [PREGUNTA]
- Mantén oraciones cortas para lectura fluida
- Elimina muletillas y repetición de palabras
- Verifica que no haya caracteres especiales problemáticos

Salida:
{
  "bloques_tts": [
    {"texto": "...", "duracion_estimada": "5s", "entonacion": "neutral"},
    ...
  ],
  "duracion_total": "X minutos"
}""",
        },
    ]

    for d in defaults:
        # Solo crear si no existe ya un default para esa categoría
        existing = list_system_prompts(category=d["category"])
        has_default = any(sp.get("is_default") for sp in existing)
        if not has_default:
            d_copy = dict(d)
            d_copy["is_default"] = d_copy.get("category") == "storming"
            prompt_data = create_system_prompt(**d_copy)
            SYSTEM_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
            p_path = SYSTEM_PROMPTS_DIR / f"{prompt_data['id']}.json"
            _dump(prompt_data, p_path)


# ─────────────────────────────────────────────────────────────────────────────
# Migración v2 → v3
# ─────────────────────────────────────────────────────────────────────────────

def migrate_from_v2(v2_data_dir: Path, user_id: str) -> dict:
    """
    Migra datos del formato v2 (channels/*.json) al formato v3.
    Asume que los canales v2 están en v2_data_dir/channels/.
    Crea un canal v3 por cada canal v2 encontrado.
    """
    stats = {"channels_migrated": 0, "content_items_migrated": 0, "errors": []}
    v2_channels_dir = v2_data_dir / "channels"

    if not v2_channels_dir.exists():
        return stats

    for v2_file in v2_channels_dir.glob("*.json"):
        try:
            v2_channel = _load(v2_file)
            if not v2_channel:
                continue

            # Crear canal v3
            v3_channel = create_channel(
                user_id=user_id,
                name=v2_channel.get("name", "Migrado"),
                platform="youtube",
                platform_id=v2_channel.get("channel_id", ""),
                url=v2_channel.get("url", ""),
            )
            stats["channels_migrated"] += 1

            # Si hay content items en el canal v2 (no existían en v2 original pero los migramos)
            # No había content items en v2, se saltan

        except Exception as e:
            stats["errors"].append(f"{v2_file.name}: {str(e)}")

    return stats
