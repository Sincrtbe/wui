"""
comfyui_client.py
Cliente para la API HTTP de ComfyUI.
Adaptado de wan22_pipeline.py (forgotten-pantheons-studio).
"""

import requests
import time
from pathlib import Path
from typing import Optional, Dict, Tuple, Any
from app.core.config import settings


class ComfyUIClient:
    """Cliente para la API REST de ComfyUI."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = (base_url or settings.COMFYUI_URL).rstrip("/")
        self.api_key = api_key or settings.COMFYUI_API_KEY
        self.timeout = timeout
        self._headers = {"Content-Type": "application/json"}
        if self.api_key:
            self._headers["X-API-Key"] = self.api_key

    def is_alive(self) -> bool:
        """Verifica si ComfyUI está corriendo."""
        try:
            r = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def upload_image(self, image_path: Path) -> bool:
        """Sube una imagen al input folder de ComfyUI (idempotente)."""
        url = f"{self.base_url}/upload/image"
        try:
            with open(image_path, "rb") as f:
                files = {"image": (image_path.name, f, "application/octet-stream")}
                r = requests.post(url, files=files, timeout=60, headers={} if not self.api_key else self._headers)
            return r.status_code in [200, 201]
        except Exception:
            return False

    def submit_workflow(self, workflow: Dict) -> Optional[str]:
        """Envía un workflow. Devuelve prompt_id o None."""
        url = f"{self.base_url}/prompt"
        try:
            r = requests.post(
                url,
                json={"prompt": workflow},
                headers=self._headers,
                timeout=self.timeout,
            )
            if r.status_code == 200:
                data = r.json()
                return data.get("prompt_id")
        except Exception:
            pass
        return None

    def wait_for_completion(
        self,
        prompt_id: str,
        timeout: int,
        poll_interval: int,
        initial_wait: int = 0,
    ) -> Optional[Dict]:
        """Espera hasta que la generación termine. Devuelve history[prompt_id] o None."""
        url = f"{self.base_url}/history/{prompt_id}"
        elapsed = 0

        if initial_wait > 0:
            time.sleep(initial_wait)
            elapsed += initial_wait

        while elapsed < timeout:
            time.sleep(poll_interval)
            elapsed += poll_interval
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    history = r.json()
                    if prompt_id in history and "outputs" in history[prompt_id]:
                        return history[prompt_id]
            except Exception:
                pass

        return None

    def download_file(
        self,
        filename: str,
        subfolder: str,
        file_type: str,
        dest_path: Path,
    ) -> bool:
        """Descarga un archivo de output/input/temp de ComfyUI."""
        url = f"{self.base_url}/view?filename={filename}&type={file_type}"
        if subfolder:
            url += f"&subfolder={subfolder}"
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "wb") as f:
                    f.write(r.content)
                return True
        except Exception:
            pass
        return False

    def get_queue_status(self) -> Dict[str, Any]:
        """Devuelve estado actual de la cola de ComfyUI."""
        try:
            r = requests.get(f"{self.base_url}/queue", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return {}
