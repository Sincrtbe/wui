"""
app/api/v3/__init__.py
API Router principal v3 — registra todos los sub-routers.
"""

from fastapi import APIRouter

from app.api.v3.auth import router as auth_router
from app.api.v3.channels import router as channels_router
from app.api.v3.prompts import router as prompts_router
from app.api.v3.content import router as content_router
from app.api.v3.pipeline import router as pipeline_router
from app.api.v3.config import router as config_router
from app.api.v3.brainstorming import router as brainstorming_router
from app.api.v3.generation import router as generation_router

router = APIRouter(prefix="/api/v3")

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(channels_router, prefix="/channels", tags=["channels"])
router.include_router(prompts_router, prefix="/prompts", tags=["prompts"])
router.include_router(content_router, prefix="/content", tags=["content"])
router.include_router(pipeline_router, prefix="/pipeline", tags=["pipeline"])
router.include_router(config_router, tags=["config"])
router.include_router(brainstorming_router, tags=["brainstorming"])
router.include_router(generation_router, prefix="/generation", tags=["generation"])
