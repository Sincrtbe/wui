# Wui - Ficha Técnica del Proyecto

## Información General
| Campo | Valor |
|-------|-------|
| **Nombre** | Wui |
| **Versión** | 1.0.0 |
| **Tipo** | Plataforma de automatización de contenido |
| **Plataforma objetivo** | YouTube |
| **Licencia** | Interna |

## Stack Tecnológico
- **Backend:** Python 3.x + FastAPI 0.104.1
- **Frontend:** HTML5 + CSS3 + JavaScript vanilla
- **Base de datos:** SQLite (app.db)
- **ORM:** SQLAlchemy 2.0.23
- **Servidor:** Uvicorn 0.24.0
- **Tareas programadas:** APScheduler 3.10.4
- **Validación:** pydantic 2.5.0
- **API YouTube:** google-api-python-client 2.197.0

## Arquitectura
```
Monolito tradicional con separación clara de responsabilidades:
- API REST (FastAPI routers)
- Modelos (SQLAlchemy)
- Vistas/Estáticas (static/)
- Tareas en segundo plano (APScheduler)
```

## Endpoints Principales
- `/ui` → Interfaz web
- `/api/channels` → CRUD canales YouTube
- `/api/schedules` → Programación publicaciones
- `/api/prompts` → Biblioteca de prompts
- `/api/analytics` → Métricas y estadísticas
- `/api/dashboard` → Resumen general
- `/api/config` → Configuración del sistema
- `/health` → Health check

## Puertos y Acceso
- **UI:** http://127.0.0.1:9080/ui
- **API:** http://127.0.0.1:9080
- **Health:** http://127.0.0.1:9080/health

## Repositorio
- **Remote:** https://github.com/Sincrtbe/wui.git
- **Último commit:** fb906a27e7e30f8d194bbd304a5b54e7ec63a10d7
- **Rama:** master

## Documentación
| Archivo | Propósito |
|---------|-----------|
| `inprogress.md` | Documento principal del proyecto |
| `bug.md` | Historial de bugs y correcciones |
| `projectinfo.md` | Ficha técnica (este archivo) |

## Lanzamiento
- `run_server.bat` → Inicia el servidor FastAPI
- `iniciar.bat` → Launcher Windows
- `systemtray.py` → Icono en bandeja del sistema