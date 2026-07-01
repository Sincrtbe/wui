"""
pipeline_service.py
Orquestador principal del pipeline de generación Flux 2 + Wan 2.2.
Gestiona la cola de jobs (filesystem), comunicación con ComfyUI y guardado de resultados.

Flujo:
  1. Job se crea en cola (content_id + scene_prompts)
  2. Worker procesa: imagen → video
  3. Resultado se guarda en content.json del content item
  4. Job file se borra al completar
"""

import json
import random
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from app.core.config import settings
from app.core.json_data_manager import DATA_DIR
from app.services.pipeline.comfyui_client import ComfyUIClient
from app.services.pipeline.workflow_modifier import WorkflowModifier


class PipelineService:
    """Gestión del pipeline de generación de imágenes y videos via ComfyUI."""

    # Estados de cada escena
    STATUS_PENDING = "pending"
    STATUS_IMAGE = "image"
    STATUS_VIDEO = "video"
    STATUS_DONE = "done"
    STATUS_ERROR = "error"

    def __init__(self, comfyui_url: Optional[str] = None, comfyui_api_key: Optional[str] = None):
        self.comfyui_url = comfyui_url or settings.COMFYUI_URL
        self.comfyui_api_key = comfyui_api_key or settings.COMFYUI_API_KEY
        self.comfy = ComfyUIClient(self.comfyui_url, self.comfyui_api_key)
        self.modifier = WorkflowModifier()

        # Directorios
        self.queue_dir = DATA_DIR / settings.PIPELINE_QUEUE_DIR
        self.output_dir = DATA_DIR / settings.PIPELINE_OUTPUT_DIR
        self.references_dir = DATA_DIR / settings.PIPELINE_REFERENCES_DIR

        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.references_dir.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────────────────
    # COLA DE JOBS (filesystem)
    # ─────────────────────────────────────────────────────────────────────────

    def create_job(self, content_id: str, scene: Dict, workflow_image_path: Path, workflow_video_path: Path) -> str:
        """Crea un job en la cola. Devuelve el job_id."""
        job_id = f"{content_id}_{scene.get('scene_id', 'S01')}_{int(time.time())}"
        job_path = self.queue_dir / f"job_{job_id}.json"
        job_data = {
            "job_id": job_id,
            "content_id": content_id,
            "scene": scene,
            "status": self.STATUS_PENDING,
            "workflow_image": str(workflow_image_path),
            "workflow_video": str(workflow_video_path),
            "created_at": datetime.now().isoformat(),
            "image_result": None,
            "video_result": None,
            "error": None,
        }
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)
        return job_id

    def create_jobs_from_scenes(
        self,
        content_id: str,
        scenes: List[Dict],
        workflow_image_path: Path,
        workflow_video_path: Path,
    ) -> List[str]:
        """Crea jobs para una lista de escenas. Devuelve lista de job_ids."""
        job_ids = []
        for scene in scenes:
            job_id = self.create_job(content_id, scene, workflow_image_path, workflow_video_path)
            job_ids.append(job_id)
        return job_ids

    def get_pending_jobs(self) -> List[Dict]:
        """Devuelve todos los jobs pendientes."""
        jobs = []
        for job_file in sorted(self.queue_dir.glob("job_*.json")):
            try:
                with open(job_file, "r", encoding="utf-8") as f:
                    jobs.append(json.load(f))
            except Exception:
                pass
        return jobs

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Devuelve un job por su ID."""
        job_path = self.queue_dir / f"job_{job_id}.json"
        if not job_path.exists():
            return None
        with open(job_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_job(self, job_id: str, updates: Dict) -> bool:
        """Actualiza campos de un job."""
        job = self.get_job(job_id)
        if not job:
            return False
        job.update(updates)
        job_path = self.queue_dir / f"job_{job_id}.json"
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(job, f, indent=2, ensure_ascii=False)
        return True

    def delete_job(self, job_id: str) -> bool:
        """Borra un job (al completar o error)."""
        job_path = self.queue_dir / f"job_{job_id}.json"
        if job_path.exists():
            job_path.unlink()
            return True
        return False

    # ─────────────────────────────────────────────────────────────────────────
    # PROCESAMIENTO
    # ─────────────────────────────────────────────────────────────────────────

    def process_next_job(self, comfyui_url: Optional[str] = None, comfyui_api_key: Optional[str] = None) -> Optional[Dict]:
        """Procesa el siguiente job pendiente. Devuelve el job actualizado o None si no hay."""
        jobs = self.get_pending_jobs()
        if not jobs:
            return None

        job = jobs[0]
        return self.process_job(job["job_id"], comfyui_url, comfyui_api_key)

    def process_job(
        self,
        job_id: str,
        comfyui_url: Optional[str] = None,
        comfyui_api_key: Optional[str] = None,
    ) -> Optional[Dict]:
        """Procesa un job específico: imagen + video."""
        job = self.get_job(job_id)
        if not job:
            return None

        scene = job["scene"]
        title = scene.get("title", job_id)
        comfy = ComfyUIClient(comfyui_url or self.comfyui_url, comfyui_api_key or self.comfyui_api_key)

        # ── PASO 1: Imagen ───────────────────────────────────────────────
        if job.get("status") == self.STATUS_PENDING:
            self.update_job(job_id, {"status": self.STATUS_IMAGE})

            image_ref = scene.get("imagenref", "")
            prompt = scene.get("prompt", "")

            if not image_ref or not prompt:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "Falta image_ref o prompt"})
                return self.get_job(job_id)

            # Buscar imagen de referencia local
            ref_path = self.references_dir / image_ref
            if not ref_path.exists():
                # Buscar en output (generada previamente)
                ref_path = self.output_dir / image_ref

            if not ref_path.exists():
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": f"Imagen de referencia no encontrada: {image_ref}"})
                return self.get_job(job_id)

            # Subir a ComfyUI
            comfy.upload_image(ref_path)

            # Modificar y enviar workflow de imagen
            seed = random.randint(1, 2**31 - 1)
            try:
                workflow = self.modifier.modify_image_workflow(
                    Path(job["workflow_image"]), image_ref, prompt, seed
                )
            except FileNotFoundError:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "Workflow de imagen no encontrado"})
                return self.get_job(job_id)

            prompt_id = comfy.submit_workflow(workflow)
            if not prompt_id:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "ComfyUI rechazó el workflow de imagen"})
                return self.get_job(job_id)

            # Esperar
            history = comfy.wait_for_completion(
                prompt_id,
                settings.PIPELINE_TIMEOUT,
                settings.PIPELINE_POLL_INTERVAL,
                initial_wait=0,
            )

            if not history:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "Timeout esperando imagen"})
                return self.get_job(job_id)

            # Extraer output
            out_filename, out_subfolder = self._extract_image(history, prompt_id)
            if not out_filename:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "No se encontró imagen en outputs"})
                return self.get_job(job_id)

            # Descargar
            dest_path = self.output_dir / f"{title}.png"
            if not comfy.download_file(out_filename, out_subfolder, "output", dest_path):
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "Fallo descarga de imagen"})
                return self.get_job(job_id)

            # Re-subir a ComfyUI para video
            comfy.upload_image(dest_path)

            self.update_job(job_id, {
                "status": self.STATUS_IMAGE,
                "image_result": str(dest_path),
            })

            # Continuar a video
            job = self.get_job(job_id)

        # ── PASO 2: Video ─────────────────────────────────────────────────
        if job.get("status") == self.STATUS_IMAGE:
            promptv = scene.get("promptv", "")
            if not promptv:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "Falta promptv para video"})
                return self.get_job(job_id)

            # La imagen ya está en ComfyUI de paso anterior
            image_name = f"{title}.png"
            seed = random.randint(1, 2**31 - 1)

            try:
                workflow = self.modifier.modify_video_workflow(
                    Path(job["workflow_video"]), image_name, promptv, seed
                )
            except FileNotFoundError:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "Workflow de video no encontrado"})
                return self.get_job(job_id)

            prompt_id = comfy.submit_workflow(workflow)
            if not prompt_id:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "ComfyUI rechazó el workflow de video"})
                return self.get_job(job_id)

            # Wan 2.2 tarda 3 min aprox
            history = comfy.wait_for_completion(
                prompt_id,
                settings.PIPELINE_TIMEOUT,
                settings.PIPELINE_POLL_INTERVAL,
                initial_wait=180,
            )

            if not history:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "Timeout esperando video"})
                return self.get_job(job_id)

            out_filename, out_subfolder = self._extract_video(history, prompt_id)
            if not out_filename:
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "No se encontró video en outputs"})
                return self.get_job(job_id)

            # Descargar con timestamp
            timestamp = datetime.now().strftime("%H%M%S")
            video_filename = f"{title}-{timestamp}.mp4"
            video_path = self.output_dir / video_filename

            if not comfy.download_file(out_filename, out_subfolder, "output", video_path):
                self.update_job(job_id, {"status": self.STATUS_ERROR, "error": "Fallo descarga de video"})
                return self.get_job(job_id)

            self.update_job(job_id, {
                "status": self.STATUS_DONE,
                "video_result": str(video_path),
            })

        return self.get_job(job_id)

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_image(history: Dict, prompt_id: str) -> tuple:
        """Extrae (filename, subfolder) de una imagen generada."""
        outputs = history.get("outputs", {})
        for node_id, node_output in outputs.items():
            images = node_output.get("images", [])
            if images:
                img = images[0]
                return img.get("filename"), img.get("subfolder", "")
        return None, None

    @staticmethod
    def _extract_video(history: Dict, prompt_id: str) -> tuple:
        """Extrae (filename, subfolder) de un video generado."""
        outputs = history.get("outputs", {})
        for node_id, node_output in outputs.items():
            for key in ("gifs", "videos", "images"):
                items = node_output.get(key, [])
                if items:
                    return items[0].get("filename"), items[0].get("subfolder", "")
        return None, None

    def check_ffmpeg(self) -> Dict[str, Any]:
        """Verifica si FFmpeg está instalado y qué versión."""
        import subprocess
        try:
            result = subprocess.run(
                [settings.FFMPEG_PATH, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version_line = result.stdout.split("\n")[0]
            return {"installed": True, "version": version_line}
        except FileNotFoundError:
            return {"installed": False, "version": None}
        except Exception as e:
            return {"installed": False, "error": str(e)}

    def check_comfyui(self) -> Dict[str, Any]:
        """Verifica conexión con ComfyUI."""
        alive = self.comfy.is_alive()
        queue = self.comfy.get_queue_status() if alive else {}
        return {"connected": alive, "queue": queue}
