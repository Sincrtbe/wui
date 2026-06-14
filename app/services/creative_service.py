"""
app/services/creative_service.py
Servicio para procesar prompts de Creative Studio.
"""

import os
import json
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "js" / "prompts" / "visual"

# Stack de modelos configurado
MODELS = {
    "qwen": "Qwen3-35B-A3B",      # Texto y prompts
    "flux": "Flux 2.0",            # Imágenes
    "wan": "Wan 2.2",              # Video
}


def get_prompt_template(template_name: str) -> Optional[str]:
    """Carga una plantilla de prompt desde el sistema de archivos."""
    template_path = BASE_DIR / f"{template_name}.md"
    if not template_path.exists():
        return None
    
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def list_available_templates() -> list[dict]:
    """Lista todas las plantillas disponibles."""
    templates = []
    for file in BASE_DIR.glob("*.md"):
        name = file.stem
        template = get_prompt_template(name)
        templates.append({
            "name": name,
            "display_name": _get_display_name(name),
            "description": _get_description(name),
            "content": template,
        })
    return templates


def _get_display_name(name: str) -> str:
    """Nombre legible para cada plantilla."""
    names = {
        "storming": "💡 Lluvia de Ideas",
        "development": "📝 Desarrollo de Guion",
        "classification": "📊 Método de Clasificación",
        "scene_graphic": "🎨 Escena Gráfica (Flux 2.0)",
        "scene_video": "🎬 Escena de Video (Wan 2.2)",
        "conversation_to_visual": "🔄 Texto a Imagen/Video",
    }
    return names.get(name, name)


def _get_description(name: str) -> str:
    """Descripción breve."""
    descriptions = {
        "storming": "Genera ideas virales y títulos gancho para tu próximo video.",
        "development": "Desarrolla una idea en un guion estructurado con tiempo y visuales.",
        "classification": "Clasifica ideas por potencial viral, SEO y esfuerzo de producción.",
        "scene_graphic": "Convierte descripciones de escena en prompts optimizados para Flux 2.0.",
        "scene_video": "Crea prompts de movimiento y cámara para Wan 2.2.",
        "conversation_to_visual": "Traduce texto hablado a prompts visuales para imagen y video.",
    }
    return descriptions.get(name, "")


def render_template(template_name: str, variables: dict) -> str:
    """Rellena una plantilla con variables y devuelve el prompt completo."""
    template = get_prompt_template(template_name)
    if not template:
        raise ValueError(f"Plantilla no encontrada: {template_name}")
    
    for key, value in variables.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    
    return template


def get_model_config() -> dict:
    """Devuelve la configuración actual de modelos."""
    return {
        "models": MODELS,
        "endpoints": {
            "qwen": os.getenv("QWEN_ENDPOINT", "http://localhost:8080"),
            "flux": os.getenv("FLUX_ENDPOINT", "http://localhost:7860"),
            "wan": os.getenv("WAN_ENDPOINT", "http://localhost:7861"),
        }
    }
