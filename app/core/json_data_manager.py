"""
Centralized Data Access Layer (DAL) for JSON persistence.
Provides generic functions to read, write, update and delete JSON records.
"""
import json
import os
from typing import Dict, Any, List, Optional

# Base directory for all data files (relative to project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def _get_entity_path(entity_name: str, item_id: Optional[str] = None) -> str:
    """
    Returns the path to the entity directory or specific item file.
    """
    path = os.path.join(DATA_DIR, entity_name)
    os.makedirs(path, exist_ok=True)
    if item_id:
        return os.path.join(path, f"{item_id}.json")
    return path

def read_json_file(entity_name: str, item_id: str) -> Optional[Dict[str, Any]]:
    """
    Reads a JSON file for a specific item.
    Returns None if the file does not exist.
    """
    file_path = _get_entity_path(entity_name, item_id)
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {file_path}: {e}")
        return None

def write_json_file(entity_name: str, item_id: str, data: Dict[str, Any]) -> bool:
    """
    Writes data to a JSON file.
    Returns True on success, False on failure.
    """
    file_path = _get_entity_path(entity_name, item_id)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Error writing to {file_path}: {e}")
        return False

def list_json_files(entity_name: str) -> List[Dict[str, Any]]:
    """
    Lists all JSON files in an entity directory and returns their content.
    """
    path = _get_entity_path(entity_name)
    items = []
    if not os.path.exists(path):
        return items
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            item_id = os.path.splitext(filename)[0]
            item_data = read_json_file(entity_name, item_id)
            if item_data:
                items.append(item_data)
    return items

def delete_json_file(entity_name: str, item_id: str) -> bool:
    """
    Deletes a JSON file.
    Returns True if deleted, False if not found or on error.
    """
    file_path = _get_entity_path(entity_name, item_id)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except IOError as e:
            print(f"Error deleting {file_path}: {e}")
    return False

def read_global_config() -> Dict[str, Any]:
    """
    Reads the global configuration file (data/config.json).
    Returns an empty dictionary if the file does not exist.
    """
    config_path = os.path.join(DATA_DIR, "config.json")
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading global config: {e}")
        return {}

def write_global_config(config_data: Dict[str, Any]) -> bool:
    """
    Writes data to the global configuration file (data/config.json).
    """
    config_path = os.path.join(DATA_DIR, "config.json")
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Error writing global config: {e}")
        return False
