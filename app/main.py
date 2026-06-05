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
from app.routers import channels, scripts, videos, publications, automation, dashboard, config, analytics, content, logs, prompts, scripts_tools, schedule
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
app.include_router(logs.router)
app.include_router(prompts.router)
app.include_router(schedule.router)

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
