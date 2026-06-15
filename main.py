"""
WUI v2 - Plataforma de Automatización Multimedia
Punto de entrada principal de la aplicación FastAPI.
"""

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.json_data_manager import init_default_config
from app.api.auth import router as auth_router
from app.api.channels import router as channels_router
from app.api.creative import router as creative_router
from app.api.config import router as config_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Inicialización: crear configuración por defecto si no existe
    init_default_config()
    print(f"[WUI v2] Aplicación iniciada en {settings.HOST}:{settings.PORT}")
    yield
    # Limpieza al cerrar
    print("[WUI v2] Aplicación apagada")


app = FastAPI(
    title=settings.APP_NAME,
    description="API para gestionar y automatizar creación de videos e imágenes",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS (ajustar en producción) ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9080", "http://127.0.0.1:9080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Archivos estáticos para el frontend ───────────────────────────────────────
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")


@app.get("/")
async def read_root():
    return RedirectResponse(url="/ui/index.html")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": app.version}


@app.get("/api/ready")
async def api_ready():
    return {
        "ready": True,
        "version": app.version,
        "debug": settings.DEBUG,
    }


# ── Registro de routers ──────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(channels_router)
app.include_router(creative_router)
app.include_router(config_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "Something went wrong",
        },
    )
