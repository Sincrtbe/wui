"""Servicio de gestión de prompts y variables basado en archivos JSON."""
import re
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Ruta base para los prompts (carpeta prompts/ en la raíz del proyecto)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# Categorías por defecto
DEFAULT_CATEGORIES = ["seo", "guion", "lluvia_ideas", "audio", "video", "otro"]

# Extensiones soportadas
PROMPT_EXTENSION = ".json"


class PromptService:
    """Servicio para gestionar prompts en archivos JSON."""

    @staticmethod
    def ensure_prompts_dir():
        """Asegura que existe la carpeta prompts/ y las subcarpetas de categorías."""
        PROMPTS_DIR.mkdir(exist_ok=True)
        for category in DEFAULT_CATEGORIES:
            (PROMPTS_DIR / category).mkdir(exist_ok=True)

    @staticmethod
    def ensure_category(category: str) -> str:
        """Asegura que existe la subcarpeta de la categoría y normaliza el nombre."""
        category = category.lower().replace(" ", "_").replace("-", "_")
        category_path = PROMPTS_DIR / category
        category_path.mkdir(exist_ok=True)
        if category not in DEFAULT_CATEGORIES:
            DEFAULT_CATEGORIES.append(category)
        return category

    @staticmethod
    def get_categories() -> list[str]:
        """Obtiene todas las categorías disponibles (subcarpetas)."""
        PromptService.ensure_prompts_dir()
        categories = []
        for item in PROMPTS_DIR.iterdir():
            if item.is_dir():
                categories.append(item.name)
        return sorted(set(categories + DEFAULT_CATEGORIES))

    @staticmethod
    def delete_category(category: str) -> bool:
        """Elimina una categoría (subcarpeta) y su contenido."""
        category = category.lower().replace(" ", "_").replace("-", "_")
        category_path = PROMPTS_DIR / category
        if not category_path.exists():
            return False
        # Eliminar todos los archivos en la categoría
        for file in category_path.iterdir():
            if file.is_file():
                file.unlink()
        # Eliminar la carpeta
        category_path.rmdir()
        if category in DEFAULT_CATEGORIES:
            DEFAULT_CATEGORIES.remove(category)
        return True

    @staticmethod
    def generate_filename(title: str) -> str:
        """Genera un nombre de archivo único basado en el título."""
        # Convertir a slug
        slug = title.lower().replace(" ", "_").replace("-", "_")
        # Eliminar caracteres no válidos
        slug = re.sub(r'[^a-z0-9_áéíóúñü]', '', slug)
        # Evitar duplicados
        counter = 1
        base_filename = f"{slug}{PROMPT_EXTENSION}"
        filename = base_filename
        while (PROMPTS_DIR / "otro" / filename).exists():  # Default a "otro" category
            filename = f"{slug}_{counter}{PROMPT_EXTENSION}"
            counter += 1
        return filename

    @staticmethod
    def extract_variables(content: str) -> list[str]:
        """Extrae las variables de un prompt (formato {{variable}})."""
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, content)
        return list(set(matches))

    @staticmethod
    def substitute_variables(content: str, variables: dict) -> str:
        """Sustituye las variables en un prompt con los valores proporcionados."""
        result = content
        for key, value in variables.items():
            pattern = r'\{\{' + key + r'\}\}'
            result = re.sub(pattern, str(value), result)
        return result

    @staticmethod
    def validate_variables(content: str, provided_vars: dict) -> dict:
        """Valida que todas las variables requeridas estén proporcionadas."""
        required = PromptService.extract_variables(content)
        provided = set(provided_vars.keys())

        missing = set(required) - provided
        extra = provided - set(required)

        return {
            "valid": len(missing) == 0,
            "required": required,
            "missing": list(missing),
            "extra": list(extra)
        }

    @staticmethod
    def get_prompt_path(category: str, filename: str) -> Path:
        """Obtiene la ruta completa de un prompt."""
        category = category.lower().replace(" ", "_").replace("-", "_")
        return PROMPTS_DIR / category / filename

    @staticmethod
    def create_prompt(
        title: str,
        content: str,
        category: str = "otro",
        description: str = None,
        prompt_type: str = None
    ) -> dict:
        """Crea un nuevo prompt como archivo JSON."""
        PromptService.ensure_prompts_dir()
        category = PromptService.ensure_category(category)

        filename = PromptService.generate_filename(title)
        variables = PromptService.extract_variables(content)

        prompt_data = {
            "id": datetime.now().timestamp(),
            "title": title,
            "description": description,
            "category": category,
            "prompt_type": prompt_type or category,
            "content": content,
            "variables": variables,
            "rating": 0.0,
            "usage_count": 0,
            "version": 1,
            "is_active": "active",
            "meta_data": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        prompt_path = PromptService.get_prompt_path(category, filename)
        with open(prompt_path, "w", encoding="utf-8") as f:
            json.dump(prompt_data, f, ensure_ascii=False, indent=4)

        return prompt_data

    @staticmethod
    def get_all_prompts(category: str = None) -> list[dict]:
        """Obtiene todos los prompts, opcionalmente filtrados por categoría."""
        PromptService.ensure_prompts_dir()
        prompts = []

        categories = [category] if category else PromptService.get_categories()

        for cat in categories:
            cat_path = PROMPTS_DIR / cat
            if not cat_path.exists():
                continue
            for file in cat_path.iterdir():
                if file.is_file() and file.suffix == PROMPT_EXTENSION:
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if data.get("is_active", "active") == "active":
                            prompts.append(data)
                    except (json.JSONDecodeError, IOError):
                        continue

        # Ordenar por rating (desc) y usage_count (desc)
        prompts.sort(key=lambda p: (p.get("rating", 0), p.get("usage_count", 0)), reverse=True)
        return prompts

    @staticmethod
    def get_prompt_by_id(prompt_id) -> Optional[dict]:
        """Obtiene un prompt por su ID (timestamp)."""
        PromptService.ensure_prompts_dir()
        try:
            target_id = float(prompt_id) if not isinstance(prompt_id, float) else prompt_id
        except (ValueError, TypeError):
            return None

        for cat_path in PROMPTS_DIR.iterdir():
            if not cat_path.is_dir():
                continue
            for file in cat_path.iterdir():
                if file.is_file() and file.suffix == PROMPT_EXTENSION:
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if data.get("id") == target_id and data.get("is_active", "active") == "active":
                            return data
                    except (json.JSONDecodeError, IOError):
                        continue
        return None

    @staticmethod
    def get_prompt_by_filename(category: str, filename: str) -> Optional[dict]:
        """Obtiene un prompt por categoría y nombre de archivo."""
        prompt_path = PromptService.get_prompt_path(category, filename)
        if not prompt_path.exists():
            return None
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    @staticmethod
    def update_prompt(
        category: str,
        filename: str,
        title: str = None,
        content: str = None,
        description: str = None,
        new_category: str = None
    ) -> Optional[dict]:
        """Actualiza un prompt existente."""
        current = PromptService.get_prompt_by_filename(category, filename)
        if not current:
            return None

        # Si cambia la categoría, mover el archivo
        if new_category and new_category != current.get("category"):
            old_path = PromptService.get_prompt_path(current["category"], filename)
            old_path.unlink(missing_ok=True)
            current["category"] = PromptService.ensure_category(new_category)

        if title:
            current["title"] = title
        if content:
            current["content"] = content
            current["variables"] = PromptService.extract_variables(content)
            current["version"] = current.get("version", 1) + 1
        if description is not None:
            current["description"] = description

        current["updated_at"] = datetime.utcnow().isoformat()

        # Guardar
        prompt_path = PromptService.get_prompt_path(current["category"], filename)
        with open(prompt_path, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=4)

        return current

    @staticmethod
    def rate_prompt(prompt_id, rating: float) -> Optional[dict]:
        """Califica un prompt."""
        prompt = PromptService.get_prompt_by_id(prompt_id)
        if not prompt:
            return None

        rating = max(0.0, min(5.0, rating))
        if prompt.get("rating", 0) > 0:
            prompt["rating"] = (prompt["rating"] + rating) / 2
        else:
            prompt["rating"] = rating

        # Encontrar y actualizar el archivo
        for cat_path in PROMPTS_DIR.iterdir():
            if not cat_path.is_dir():
                continue
            for file in cat_path.iterdir():
                if file.is_file() and file.suffix == PROMPT_EXTENSION:
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if data.get("id") == float(prompt_id):
                            with open(file, "w", encoding="utf-8") as f:
                                json.dump(prompt, f, ensure_ascii=False, indent=4)
                            return prompt
                    except (json.JSONDecodeError, IOError):
                        continue
        return None

    @staticmethod
    def increment_usage(prompt_id) -> Optional[dict]:
        """Incrementa el contador de uso de un prompt."""
        prompt = PromptService.get_prompt_by_id(prompt_id)
        if not prompt:
            return None

        prompt["usage_count"] = prompt.get("usage_count", 0) + 1

        # Actualizar en disco
        for cat_path in PROMPTS_DIR.iterdir():
            if not cat_path.is_dir():
                continue
            for file in cat_path.iterdir():
                if file.is_file() and file.suffix == PROMPT_EXTENSION:
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if data.get("id") == float(prompt_id):
                            with open(file, "w", encoding="utf-8") as f:
                                json.dump(prompt, f, ensure_ascii=False, indent=4)
                            return prompt
                    except (json.JSONDecodeError, IOError):
                        continue
        return None

    @staticmethod
    def delete_prompt(category: str, filename: str) -> bool:
        """Elimina (borra el archivo) un prompt."""
        prompt_path = PromptService.get_prompt_path(category, filename)
        if not prompt_path.exists():
            return False
        prompt_path.unlink()
        return True

    @staticmethod
    def search_prompts(query: str, category: str = None) -> list[dict]:
        """Busca prompts por título, descripción o contenido."""
        all_prompts = PromptService.get_all_prompts(category)
        query_lower = query.lower()
        return [
            p for p in all_prompts
            if query_lower in p.get("title", "").lower()
            or query_lower in p.get("description", "").lower()
            or query_lower in p.get("content", "").lower()
        ]