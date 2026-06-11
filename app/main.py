"""Aplicación principal FastAPI."""
from contextlib import asynccontextmanager
import multiprocessing
import sys
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from functools import wraps
from app.core.database import Base, engine, SessionLocal
from app.core.ratelimit import limiter
from app.routers import channels, scripts, videos, publications, automation, dashboard, config, analytics, content, logs, prompts, scripts_tools, schedule, auth
from app.tasks.scheduler import init_scheduler, shutdown_scheduler
from app.core.config import settings

# Variable global para el proceso del servidor
_server_process = None

# Rutas públicas (sin autenticación)
PUBLIC_ROUTES = [
    "/api/auth/login",
    "/api/auth/check",
    "/api/auth/logout",
    "/health",
]

def require_auth(request: Request):
    """Middleware para verificar autenticación."""
    # Obtener credenciales del header Authorization
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Basic "):
        raise HTTPException(status_code=401, detail="No autenticado")
    
    import base64
    try:
        encoded_credentials = auth_header[6:]  # Quitar "Basic "
        decoded = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Verificar credenciales
    if username != settings.ADMIN_USER or password != settings.ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return True



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Contexto de ciclo de vida de la aplicación."""
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        existing_columns = [row["name"] for row in conn.execute(text("PRAGMA table_info(channels)")).mappings()]
        if "email" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN email VARCHAR"))
        if "social_links" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN social_links JSON"))
        if "checkpoints" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN checkpoints JSON"))
        if "last_scraped_at" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN last_scraped_at DATETIME"))
        if "last_scrape_status" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN last_scrape_status VARCHAR"))
        if "scrape_data" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN scrape_data JSON"))
        if "color" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN color VARCHAR DEFAULT '#3b82f6'"))
        
        # Crear nuevas tablas si no existen
        conn.execute(text("CREATE TABLE IF NOT EXISTS global_configs (key VARCHAR PRIMARY KEY, value TEXT, description VARCHAR)"))
        if "channel_name" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN channel_name VARCHAR"))
        if "fecha_ejecucion" not in existing_columns:
            conn.execute(text("ALTER TABLE channels ADD COLUMN fecha_ejecucion VARCHAR"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS daily_stats (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id INTEGER, channel_name VARCHAR, view_count INTEGER, subscriber_count INTEGER, video_count INTEGER, stat_date DATE, fecha_ejecucion VARCHAR, FOREIGN KEY(channel_id) REFERENCES channels(id))"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS content_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                stage VARCHAR DEFAULT 'idea',
                title VARCHAR NOT NULL,
                idea_notes TEXT,
                script_content TEXT,
                article_content TEXT,
                developed_data JSON,
                video_path VARCHAR,
                video_metadata JSON,
                status VARCHAR DEFAULT 'pending',
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY(channel_id) REFERENCES channels(id)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR NOT NULL,
                description TEXT,
                prompt_type VARCHAR NOT NULL,
                content TEXT NOT NULL,
                variables JSON,
                rating FLOAT DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0,
                version INTEGER DEFAULT 1,
                is_active VARCHAR DEFAULT 'active',
                meta_data JSON,
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                channel_id INTEGER,
                event_type VARCHAR NOT NULL,
                severity VARCHAR DEFAULT 'info',
                message TEXT NOT NULL,
                details TEXT,
                created_at DATETIME,
                FOREIGN KEY(task_id) REFERENCES automation_tasks(id),
                FOREIGN KEY(channel_id) REFERENCES channels(id)
            )
        """))
        
        # Crear tabla channel_schedules si no existe
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS channel_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER UNIQUE,
                long_video_enabled BOOLEAN DEFAULT 0,
                long_video_frequency INTEGER,
                short_video_enabled BOOLEAN DEFAULT 0,
                short_video_frequency INTEGER,
                article_enabled BOOLEAN DEFAULT 0,
                article_frequency INTEGER,
                start_date DATE,
                timezone VARCHAR DEFAULT 'Europe/Madrid',
                is_active BOOLEAN DEFAULT 0,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY(channel_id) REFERENCES channels(id)
            )
        """))
        
        # Crear tabla publication_schedules si no existe
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS publication_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                script_id INTEGER,
                content_type VARCHAR,
                scheduled_datetime DATETIME,
                status VARCHAR DEFAULT 'planned',
                notes TEXT,
                created_at DATETIME,
                FOREIGN KEY(channel_id) REFERENCES channels(id),
                FOREIGN KEY(script_id) REFERENCES scripts(id)
            )
        """))
        
        # Verificar y añadir columnas faltantes en publication_schedules
        pub_columns = [row["name"] for row in conn.execute(text("PRAGMA table_info(publication_schedules)")).mappings()]
        if "content_type" not in pub_columns:
            conn.execute(text("ALTER TABLE publication_schedules ADD COLUMN content_type VARCHAR"))
        if "script_id" not in pub_columns:
            conn.execute(text("ALTER TABLE publication_schedules ADD COLUMN script_id INTEGER"))
        if "created_at" not in pub_columns:
            conn.execute(text("ALTER TABLE publication_schedules ADD COLUMN created_at DATETIME"))
        
        # Verificar y añadir columnas faltantes en channel_schedules
        chan_columns = [row["name"] for row in conn.execute(text("PRAGMA table_info(channel_schedules)")).mappings()]
        if "is_active" not in chan_columns:
            conn.execute(text("ALTER TABLE channel_schedules ADD COLUMN is_active BOOLEAN DEFAULT 0"))
        if "created_at" not in chan_columns:
            conn.execute(text("ALTER TABLE channel_schedules ADD COLUMN created_at DATETIME"))
        if "updated_at" not in chan_columns:
            conn.execute(text("ALTER TABLE channel_schedules ADD COLUMN updated_at DATETIME"))

    init_scheduler()
    
    # Iniciar system tray en un proceso separado (desactivado en headless)
    try:
        from app.core.system_tray import start_tray_from_lifespan
        import os
        if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
            start_tray_from_lifespan()
        else:
            print("System tray desactivado (headless)")
    except Exception as e:
        print(f"System tray desactivado: {e}")
    
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Plataforma de Automatización Multimedia",
    description="API para gestionar y automatizar creación de videos e imágenes",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar rate limiter
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Manejador de errores de límite de tasa."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiados intentos. Espera un momento antes de reintentar."},
    )

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware para verificar autenticación en todas las rutas."""
    # Permitir acceso a rutas públicas
    if request.url.path in PUBLIC_ROUTES or request.url.path.startswith("/ui/") or request.url.path == "/":
        response = await call_next(request)
        return response
    
    # Verificar autenticación para todas las demás rutas
    try:
        require_auth(request)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
            headers={"WWW-Authenticate": 'Basic realm="Login required"'},
        )
    
    response = await call_next(request)
    return response

# CORS: solo permitir orígenes específicos, métodos seguros y headers mínimos
# En producción, ajustar ALLOWED_ORIGINS con los dominios reales
ALLOWED_ORIGINS = os.getenv("WUI_ALLOWED_ORIGINS", "http://localhost:9080,http://127.0.0.1:9080").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["WWW-Authenticate"],
)

# Incluir router de autenticación PRIMERO (antes que las rutas protegidas)
app.include_router(auth.router)

app.include_router(channels.router)
app.include_router(scripts.router)

app.include_router(videos.router)
app.include_router(publications.router)
app.include_router(automation.router)
app.include_router(dashboard.router)
app.include_router(scripts_tools.router)
app.include_router(config.router)
app.include_router(analytics.router)
app.include_router(content.router)
app.include_router(logs.router)
app.include_router(prompts.router)
app.include_router(schedule.router)

app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")


@app.get("/")
def root():
    """Redirige a la página de login."""
    return RedirectResponse(url="/ui/login.html")


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


@app.post("/admin/shutdown")
def admin_shutdown():
    """Apaga el servidor."""
    global _server_process
    
    def stop_self():
        import os
        os._exit(0)
    
    # Programar la parada
    import threading
    threading.Timer(1, stop_self).start()
    
    return {"detail": "Servidor apagándose..."}


@app.post("/admin/restart")
def admin_restart():
    """Reinicia el servidor."""
    global _server_process
    
    def restart():
        import subprocess
        import time
        time.sleep(2)
        # Reiniciar el proceso
        python = sys.executable
        main_file = os.path.join(os.path.dirname(__file__), "main.py")
        os.execv(python, [python, main_file])
    
    # Programar el reinicio
    import threading
    threading.Timer(2, restart).start()
    
    return {"detail": "Servidor reiniciándose..."}


def run_server(host="127.0.0.1", port=9080, reload=False):
    """Ejecuta el servidor con soporte para system tray."""
    global _server_process
    
    # Iniciar el system tray en un hilo separado
    def start_tray():
        try:
            from app.core.system_tray import create_tray_icon
            create_tray_icon()
        except Exception as e:
            pass
    
    import threading
    tray_thread = threading.Thread(target=start_tray, daemon=True)
    tray_thread.start()
    
    # Ejecutar uvicorn directamente
    import uvicorn
    uvicorn.run(app, host=host, port=port, reload=reload)
