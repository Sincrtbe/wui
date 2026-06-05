"""Aplicación principal FastAPI."""
from contextlib import asynccontextmanager
import multiprocessing
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.database import Base, engine, SessionLocal
from app.routers import channels, scripts, videos, publications, automation, dashboard, config, analytics, content_tools, scripts, config, analytics
from app.tasks.scheduler import init_scheduler, shutdown_scheduler

# Variable global para el proceso del servidor
_server_process = None



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
        conn.execute(text("CREATE TABLE IF NOT EXISTS daily_stats (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id INTEGER, view_count INTEGER, subscriber_count INTEGER, video_count INTEGER, stat_date DATE, FOREIGN KEY(channel_id) REFERENCES channels(id))"))
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

    init_scheduler()
    
    # Iniciar system tray en un proceso separado
    from app.core.system_tray import start_tray_from_lifespan
    start_tray_from_lifespan()
    
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Plataforma de Automatización Multimedia",
    description="API para gestionar y automatizar creación de videos e imágenes",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")


@app.get("/")
def root():
    """Redirige a la interfaz web."""
    return RedirectResponse(url="/ui")


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
