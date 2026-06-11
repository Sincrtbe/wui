"""Wui v2 - Main Application Entry Point"""
import sys
import os

# Add the project root to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.channels import router as channels_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización (crear archivos JSON si no existen, cargar config, etc.)
    print("Aplicación Wui v2 iniciada correctamente")
    yield
    # Limpieza al apagado
    print("Aplicación Wui v2 apagada")

app = FastAPI(
    title="Wui v2: Plataforma de Automatización Multimedia",
    description="API para gestionar y automatizar creación de videos e imágenes (JSON-based)",
    version="2.0.0",
    lifespan=lifespan,
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ajustar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(channels_router)

# Montar archivos estáticos para el frontend
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")

@app.get("/")
async def read_root():
    return RedirectResponse(url="/ui/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0"}
