"""
app/api/v3/generation.py
API del pipeline de generación de imágenes y videos via ComfyUI.

Flujo:
  POST /generate  → Crea jobs en cola (sin enviar a ComfyUI aún)
  GET  /queue     → Lista jobs pendientes
  POST /process   → Procesa siguiente job (worker llama esto)
  GET  /status/{job_id} → Estado de un job
  POST /ffmpeg-install → Instala FFmpeg en el servidor
  GET  /ffmpeg-status   → Estado de FFmpeg
  GET  /comfyui-status → Estado de ComfyUI
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.v3.auth import get_current_user
from app.core.config import settings
from app.services.pipeline import PipelineService


router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class SceneGenerateItem(BaseModel):
    scene_id: str
    title: str
    prompt: str
    imagenref: str
    promptv: str


class GenerateRequest(BaseModel):
    content_id: str
    scenes: list[SceneGenerateItem]
    workflow_image: str  # path al workflow JSON
    workflow_video: str  # path al workflow JSON


class GenerateResponse(BaseModel):
    job_ids: list[str]
    count: int


class JobStatus(BaseModel):
    job_id: str
    content_id: str
    scene_id: str
    status: str
    image_result: Optional[str] = None
    video_result: Optional[str] = None
    error: Optional[str] = None


class SystemStatus(BaseModel):
    comfyui_url: str
    comfyui_connected: bool
    comfyui_queue: dict
    ffmpeg_installed: bool
    ffmpeg_version: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS PÚBLICOS (usados desde UI)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
def create_generation_jobs(
    body: GenerateRequest,
    user: dict = Depends(get_current_user),
):
    """
    Crea jobs en la cola de generación.
    Los jobs quedan pendientes hasta que un worker los procese.
    """
    svc = PipelineService()

    scenes_data = [scene.model_dump() for scene in body.scenes]
    job_ids = svc.create_jobs_from_scenes(
        content_id=body.content_id,
        scenes=scenes_data,
        workflow_image_path=Path(body.workflow_image),
        workflow_video_path=Path(body.workflow_video),
    )

    return GenerateResponse(job_ids=job_ids, count=len(job_ids))


@router.get("/queue", response_model=list[JobStatus])
def list_queue(
    user: dict = Depends(get_current_user),
):
    """Lista todos los jobs pendientes en la cola."""
    svc = PipelineService()
    jobs = svc.get_pending_jobs()
    return [
        JobStatus(
            job_id=j["job_id"],
            content_id=j["content_id"],
            scene_id=j["scene"].get("scene_id", ""),
            status=j["status"],
            image_result=j.get("image_result"),
            video_result=j.get("video_result"),
            error=j.get("error"),
        )
        for j in jobs
    ]


@router.get("/status/{job_id}", response_model=JobStatus)
def get_job_status(
    job_id: str,
    user: dict = Depends(get_current_user),
):
    """Estado de un job específico."""
    svc = PipelineService()
    job = svc.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return JobStatus(
        job_id=job["job_id"],
        content_id=job["content_id"],
        scene_id=job["scene"].get("scene_id", ""),
        status=job["status"],
        image_result=job.get("image_result"),
        video_result=job.get("video_result"),
        error=job.get("error"),
    )


@router.delete("/job/{job_id}")
def cancel_job(
    job_id: str,
    user: dict = Depends(get_current_user),
):
    """Cancela y elimina un job pendiente."""
    svc = PipelineService()
    job = svc.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    svc.delete_job(job_id)
    return {"ok": True, "job_id": job_id}


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS DE SISTEMA (llamados por worker o cron)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/process")
def process_next(
    comfyui_url: Optional[str] = Query(None),
    comfyui_api_key: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
):
    """
    Procesa el siguiente job de la cola.
    Un worker/cron debe llamar a este endpoint periódicamente.
    """
    svc = PipelineService()
    job = svc.process_next_job(comfyui_url, comfyui_api_key)
    if not job:
        return {"ok": True, "message": "No hay jobs pendientes", "job": None}
    return {"ok": True, "job": job}


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO DEL SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/system-status", response_model=SystemStatus)
def system_status(
    user: dict = Depends(get_current_user),
):
    """Estado de ComfyUI y FFmpeg."""
    svc = PipelineService()
    comfy_status = svc.check_comfyui()
    ffmpeg_status = svc.check_ffmpeg()

    return SystemStatus(
        comfyui_url=svc.comfyui_url,
        comfyui_connected=comfy_status["connected"],
        comfyui_queue=comfy_status.get("queue", {}),
        ffmpeg_installed=ffmpeg_status["installed"],
        ffmpeg_version=ffmpeg_status.get("version"),
    )


@router.post("/ffmpeg-install")
def install_ffmpeg(
    user: dict = Depends(get_current_user),
):
    """
    Instala FFmpeg en el servidor.
    Soporta: Ubuntu/Debian (apt), CentOS/RHEL (yum/dnf), macOS (brew).
    """
    system = subprocess.check_output(["uname", "-s"]).decode().strip().lower()

    if system in ("linux",):
        # Detectar distro
        if Path("/etc/debian_version").exists():
            pkg_manager = "apt-get"
        elif Path("/etc/redhat-release").exists():
            pkg_manager = "yum"
        else:
            pkg_manager = None

        if pkg_manager:
            try:
                subprocess.run(["sudo", pkg_manager, "update", "-y"],
                             capture_output=True, timeout=120)
                subprocess.run(["sudo", pkg_manager, "install", "-y", "ffmpeg"],
                             capture_output=True, timeout=180)
                return {"ok": True, "method": pkg_manager, "message": "FFmpeg instalado"}
            except subprocess.TimeoutExpired:
                raise HTTPException(status_code=500, detail="Timeout durante instalación")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error instalando: {e}")
        else:
            raise HTTPException(status_code=400, detail="Distribucion Linux no soportada para auto-install")
    elif system == "darwin":
        try:
            subprocess.run(["brew", "install", "ffmpeg"], capture_output=True, timeout=300)
            return {"ok": True, "method": "brew", "message": "FFmpeg instalado"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error brew: {e}")
    else:
        raise HTTPException(status_code=400, detail=f"Sistema {system} no soportado")


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG (ComfyUI URL configurable por usuario)
# ─────────────────────────────────────────────────────────────────────────────

class ComfyUIConfig(BaseModel):
    comfyui_url: str
    comfyui_api_key: Optional[str] = None


@router.post("/config")
def save_comfyui_config(
    body: ComfyUIConfig,
    user: dict = Depends(get_current_user),
):
    """Guarda la configuración de ComfyUI para el usuario."""
    # Por ahora guarda en .env del servidor (modo single-user)
    # En multi-user futuro: guardar en user_settings de la DB
    env_path = Path(".env")
    env_lines = []
    if env_path.exists():
        env_lines = env_path.read_text().splitlines()

    # Actualizar o añadir líneas
    updated = False
    new_lines = []
    for line in env_lines:
        if line.startswith("COMFYUI_URL="):
            new_lines.append(f"COMFYUI_URL={body.comfyui_url}")
            updated = True
        elif line.startswith("COMFYUI_API_KEY="):
            if body.comfyui_api_key:
                new_lines.append(f"COMFYUI_API_KEY={body.comfyui_api_key}")
                updated = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"COMFYUI_URL={body.comfyui_url}")
        if body.comfyui_api_key:
            new_lines.append(f"COMFYUI_API_KEY={body.comfyui_api_key}")

    env_path.write_text("\n".join(new_lines) + "\n")
    return {"ok": True, "message": "Config guardada. Reinicia el servidor para aplicar."}


@router.get("/config", response_model=ComfyUIConfig)
def get_comfyui_config(
    user: dict = Depends(get_current_user),
):
    """Devuelve la config actual de ComfyUI."""
    return ComfyUIConfig(
        comfyui_url=settings.COMFYUI_URL,
        comfyui_api_key=settings.COMFYUI_API_KEY if settings.COMFYUI_API_KEY else None,
    )
