"""
app/services/config_service.py
Servicio para gestionar configuración de APIs y prompts personalizados.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from app.core.json_data_manager import (
    read_json_file,
    write_json_file,
    list_json_files,
    delete_json_file,
    update_json_file,
    read_global_config,
    write_global_config,
)

# Directorios de datos
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
PROMPTS_DIR = DATA_DIR / "custom_prompts"
CHARACTERS_DIR = DATA_DIR / "characters"


def _ensure_dirs():
    """Asegura que los directorios existan."""
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)


# ── GESTIÓN DE APIs ──────────────────────────────────────────────────────────

def get_api_config() -> Dict[str, Any]:
    """Obtiene la configuración de APIs guardada."""
    config = read_global_config()
    return {
        "youtube_api_key": config.get("youtube_api_key", ""),
        "llm_api_key": config.get("llm_api_key", ""),
        "llm_endpoint": config.get("llm_endpoint", "http://localhost:11434/api/generate"),
        "llm_model": config.get("llm_model", "llama2"),
        "flux_endpoint": config.get("flux_endpoint", "http://localhost:7860"),
        "wan_endpoint": config.get("wan_endpoint", "http://localhost:7861"),
        "qwen_endpoint": config.get("qwen_endpoint", "http://localhost:8080"),
    }


def update_api_config(api_config: Dict[str, Any]) -> Dict[str, Any]:
    """Actualiza la configuración de APIs."""
    config = read_global_config()
    config.update({
        "youtube_api_key": api_config.get("youtube_api_key", ""),
        "llm_api_key": api_config.get("llm_api_key", ""),
        "llm_endpoint": api_config.get("llm_endpoint", ""),
        "llm_model": api_config.get("llm_model", ""),
        "flux_endpoint": api_config.get("flux_endpoint", ""),
        "wan_endpoint": api_config.get("wan_endpoint", ""),
        "qwen_endpoint": api_config.get("qwen_endpoint", ""),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    write_global_config(config)
    return get_api_config()


# ── GESTIÓN DE PROMPTS PERSONALIZADOS ────────────────────────────────────────

def create_custom_prompt(
    name: str,
    content: str,
    category: str = "general",
    assigned_to: List[str] = None,
    description: str = "",
) -> Dict[str, Any]:
    """Crea un nuevo prompt personalizado."""
    _ensure_dirs()
    
    prompt_id = str(uuid.uuid4())
    prompt_data = {
        "id": prompt_id,
        "name": name,
        "content": content,
        "category": category,
        "description": description,
        "assigned_to": assigned_to or [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    write_json_file("custom_prompts", prompt_id, prompt_data)
    return prompt_data


def get_custom_prompt(prompt_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene un prompt personalizado por ID."""
    return read_json_file("custom_prompts", prompt_id)


def list_custom_prompts() -> List[Dict[str, Any]]:
    """Lista todos los prompts personalizados."""
    _ensure_dirs()
    return list_json_files("custom_prompts")


def update_custom_prompt(
    prompt_id: str,
    name: Optional[str] = None,
    content: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Actualiza un prompt personalizado."""
    updates = {}
    if name is not None:
        updates["name"] = name
    if content is not None:
        updates["content"] = content
    if category is not None:
        updates["category"] = category
    if assigned_to is not None:
        updates["assigned_to"] = assigned_to
    if description is not None:
        updates["description"] = description
    
    if updates:
        return update_json_file("custom_prompts", prompt_id, updates)
    return get_custom_prompt(prompt_id)


def delete_custom_prompt(prompt_id: str) -> bool:
    """Elimina un prompt personalizado."""
    return delete_json_file("custom_prompts", prompt_id)


def assign_prompt_to_tab(prompt_id: str, tab_name: str) -> Optional[Dict[str, Any]]:
    """Asigna un prompt a una pestaña específica."""
    prompt = get_custom_prompt(prompt_id)
    if not prompt:
        return None
    
    assigned_to = prompt.get("assigned_to", [])
    if tab_name not in assigned_to:
        assigned_to.append(tab_name)
    
    return update_custom_prompt(prompt_id, assigned_to=assigned_to)


def unassign_prompt_from_tab(prompt_id: str, tab_name: str) -> Optional[Dict[str, Any]]:
    """Desasigna un prompt de una pestaña."""
    prompt = get_custom_prompt(prompt_id)
    if not prompt:
        return None
    
    assigned_to = prompt.get("assigned_to", [])
    if tab_name in assigned_to:
        assigned_to.remove(tab_name)
    
    return update_custom_prompt(prompt_id, assigned_to=assigned_to)


def get_prompts_for_tab(tab_name: str) -> List[Dict[str, Any]]:
    """Obtiene todos los prompts asignados a una pestaña."""
    prompts = list_custom_prompts()
    return [p for p in prompts if tab_name in p.get("assigned_to", [])]


# ── GESTIÓN DE PERSONAJES ────────────────────────────────────────────────────

def create_character(
    name: str,
    description: str,
    personality: str = "",
    appearance: str = "",
    background: str = "",
    associated_prompts: List[str] = None,
) -> Dict[str, Any]:
    """Crea un nuevo personaje."""
    _ensure_dirs()
    
    character_id = str(uuid.uuid4())
    character_data = {
        "id": character_id,
        "name": name,
        "description": description,
        "personality": personality,
        "appearance": appearance,
        "background": background,
        "associated_prompts": associated_prompts or [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    
    write_json_file("characters", character_id, character_data)
    return character_data


def get_character(character_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene un personaje por ID."""
    return read_json_file("characters", character_id)


def list_characters() -> List[Dict[str, Any]]:
    """Lista todos los personajes."""
    _ensure_dirs()
    return list_json_files("characters")


def update_character(
    character_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    personality: Optional[str] = None,
    appearance: Optional[str] = None,
    background: Optional[str] = None,
    associated_prompts: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Actualiza un personaje."""
    updates = {}
    if name is not None:
        updates["name"] = name
    if description is not None:
        updates["description"] = description
    if personality is not None:
        updates["personality"] = personality
    if appearance is not None:
        updates["appearance"] = appearance
    if background is not None:
        updates["background"] = background
    if associated_prompts is not None:
        updates["associated_prompts"] = associated_prompts
    
    if updates:
        return update_json_file("characters", character_id, updates)
    return get_character(character_id)


def delete_character(character_id: str) -> bool:
    """Elimina un personaje."""
    return delete_json_file("characters", character_id)


def add_prompt_to_character(character_id: str, prompt_id: str) -> Optional[Dict[str, Any]]:
    """Añade un prompt a un personaje."""
    character = get_character(character_id)
    if not character:
        return None
    
    associated_prompts = character.get("associated_prompts", [])
    if prompt_id not in associated_prompts:
        associated_prompts.append(prompt_id)
    
    return update_character(character_id, associated_prompts=associated_prompts)


def remove_prompt_from_character(character_id: str, prompt_id: str) -> Optional[Dict[str, Any]]:
    """Elimina un prompt de un personaje."""
    character = get_character(character_id)
    if not character:
        return None
    
    associated_prompts = character.get("associated_prompts", [])
    if prompt_id in associated_prompts:
        associated_prompts.remove(prompt_id)
    
    return update_character(character_id, associated_prompts=associated_prompts)


def get_character_with_prompts(character_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene un personaje con sus prompts asociados."""
    character = get_character(character_id)
    if not character:
        return None
    
    prompts = []
    for prompt_id in character.get("associated_prompts", []):
        prompt = get_custom_prompt(prompt_id)
        if prompt:
            prompts.append(prompt)
    
    character["prompts"] = prompts
    return character
