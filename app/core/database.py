"""Configuración de la base de datos."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Inicializar base de datos con migraciones."""
    import sqlite3
    from pathlib import Path
    
    # Parsear la URL de la base de datos
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_file = Path(db_path)
    
    if db_file.exists():
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Verificar y añadir columna content_type si no existe
        cursor.execute("PRAGMA table_info(publication_schedules)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "content_type" not in columns:
            cursor.execute("ALTER TABLE publication_schedules ADD COLUMN content_type VARCHAR")
            print("✅ Columna 'content_type' añadida a publication_schedules")
        
        # Verificar y añadir columna is_active en channel_schedules si no existe
        cursor.execute("PRAGMA table_info(channel_schedules)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "is_active" not in columns:
            cursor.execute("ALTER TABLE channel_schedules ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("✅ Columna 'is_active' añadida a channel_schedules")
        
        conn.commit()
        conn.close()
    
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")


def get_db():
    """Generador de sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
