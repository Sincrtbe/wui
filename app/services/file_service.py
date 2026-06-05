"""Servicio de gestión de archivos físicos para contenido."""
import os
import json
from datetime import datetime
from pathlib import Path

# Directorio base de canales
CHANNELS_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "channels_data")


class FileService:
    """Servicio para sincronizar contenido con archivos físicos en las carpetas de canal."""

    @staticmethod
    def get_channel_dir(channel_id: int) -> str:
        """Obtiene la ruta de la carpeta del canal."""
        return os.path.join(CHANNELS_DATA_DIR, f"channel_{channel_id}")

    @staticmethod
    def ensure_channel_dirs(channel_id: int) -> str:
        """Asegura que existan las carpetas del canal."""
        channel_dir = FileService.get_channel_dir(channel_id)
        os.makedirs(channel_dir, exist_ok=True)
        for sub in ["ideas", "scripts", "developed", "videos"]:
            os.makedirs(os.path.join(channel_dir, sub), exist_ok=True)
        return channel_dir

    @staticmethod
    def save_idea(channel_id: int, item_id: int, title: str, notes: str) -> str:
        """Guarda una idea en un archivo .md en la carpeta ideas."""
        channel_dir = FileService.ensure_channel_dirs(channel_id)
        ideas_dir = os.path.join(channel_dir, "ideas")
        
        filename = f"{item_id}_{title[:30].replace(' ', '_')}.md"
        filepath = os.path.join(ideas_dir, filename)
        
        content = f"""# Idea: {title}

**Creado:** {datetime.now().isoformat()}
**ID:** {item_id}

## Notas

{notes}

---
*Archivo generado automáticamente por Wui*
"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath

    @staticmethod
    def save_script(channel_id: int, item_id: int, title: str, script_content: str, article_content: str = None) -> str:
        """Guarda un guion en un archivo .md en la carpeta scripts."""
        channel_dir = FileService.ensure_channel_dirs(channel_id)
        scripts_dir = os.path.join(channel_dir, "scripts")
        
        filename = f"{item_id}_{title[:30].replace(' ', '_')}.md"
        filepath = os.path.join(scripts_dir, filename)
        
        content = f"""# Guión: {title}

**Creado:** {datetime.now().isoformat()}
**ID:** {item_id}

## Guión de Voz

{script_content}

"""
        
        if article_content:
            content += f"""## Artículo

{article_content}

"""
        
        content += "\n---\n*Archivo generado automáticamente por Wui*"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath

    @staticmethod
    def save_developed(channel_id: int, item_id: int, title: str, developed_data: dict) -> str:
        """Guarda datos de desarrollo en un archivo JSON en la carpeta developed."""
        channel_dir = FileService.ensure_channel_dirs(channel_id)
        developed_dir = os.path.join(channel_dir, "developed")
        
        filename = f"{item_id}_{title[:30].replace(' ', '_')}.json"
        filepath = os.path.join(developed_dir, filename)
        
        data = {
            "title": title,
            "id": item_id,
            "created": datetime.now().isoformat(),
            "data": developed_data
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath

    @staticmethod
    def list_files_in_stage(channel_id: int, stage: str) -> list[dict]:
        """Lista los archivos en una carpeta de etapa específica."""
        channel_dir = FileService.get_channel_dir(channel_id)
        stage_dir = os.path.join(channel_dir, stage)
        
        if not os.path.exists(stage_dir):
            return []
        
        files = []
        for filename in os.listdir(stage_dir):
            filepath = os.path.join(stage_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    "name": filename,
                    "path": filepath,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return sorted(files, key=lambda x: x["modified"], reverse=True)

    @staticmethod
    def read_file(filepath: str) -> str:
        """Lee el contenido de un archivo."""
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error al leer archivo: {str(e)}"

    @staticmethod
    def delete_file(filepath: str) -> bool:
        """Elimina un archivo."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception:
            pass
        return False
