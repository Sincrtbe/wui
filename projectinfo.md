# ProjectInfo - Wui

## 1. Datos Generales
- **Nombre:** Wui
- **Versión:** 1.0.0
- **Descripción:** Plataforma local para gestionar y automatizar flujos de trabajo de video/audio/imagen/subtítulos para múltiples canales de YouTube.
- **Propósito:** Automatización de creación de contenido multimedia para canales de YouTube con UI web propia y ejecución local.
- **Fecha de creación:** 2026-05-06
- **Última actualización:** 2026-07-06

## 2. Stack Tecnológico
### Lenguajes
- **Python** (principal)
- **JavaScript** (frontend)
- **HTML/CSS** (frontend)

### Frameworks
- **FastAPI** 0.104.1 (backend API)
- **SQLAlchemy** 2.0.23 (ORM)
- **Uvicorn** 0.24.0 (servidor ASGI)

### Bases de Datos
- **SQLite** (app.db)

### Librerías Principales
- **pydantic** 2.5.0 (validación de datos)
- **pydantic-settings** 2.1.0 (gestión de configuración)
- **apscheduler** 3.10.4 (tareas programadas/cron)
- **google-api-python-client** 2.197.0 (API de YouTube)
- **requests** 2.34.2 (peticiones HTTP)
- **pystray** 0.19.5 (system tray icon)
- **Pillow** 10.1.0 (manipulación de imágenes)
- **python-dotenv** 1.0.0 (variables de entorno)
- **alembic** 1.13.1 (migraciones de base de datos)
- **python-dateutil** 2.8.2 (manipulación de fechas)

### Herramientas de Desarrollo
- **uvicorn** (servidor)
- **SQLite** (base de datos embebida)

## 3. Repositorio
- **Tipo:** git
- **URL:** https://github.com/Sincrtbe/wui.git
- **Rama principal:** main
- **Último commit:** fb906a277e30f8d194bbd304a5b54e7ec63a10d7
- **Remote origin:** origin: https://github.com/Sincrtbe/wui.git

## 4. Datos de Uso
### Puertos
- **Puerto principal:** 9080
- **Host:** 127.0.0.1

### Líneas de Lanzamiento
```bash
# Iniciar el servidor
python run_server.bat
# o
python systemtray.py
# o
uvicorn app.main:app --host 127.0.0.1 --port 9080 --reload

# Iniciar con launcher
iniciar.bat
```

### Variables de Entorno
- **YOUTUBE_API_KEY:** API Key para acceder a la API de YouTube
- **DATABASE_URL:** URL de conexión a base de datos (default: sqlite:///./app.db)
- **DEBUG:** Modo debug (default: True)

### Acceso
- **UI Web:** http://127.0.0.1:9080/ui
- **API Base:** http://127.0.0.1:9080
- **Health Check:** http://127.0.0.1:9080/health
- **Root:** http://127.0.0.1:9080 (redirige a /ui)

## 5. Estructura del Proyecto
```
Wui/
├── .env                          # Variables de entorno
├── .gitignore                    # Archivos a ignorar por git
├── app.db                        # Base de datos SQLite
├── bug.md                        # Registro de bugs y reparaciones
├── iniciar.bat                   # Launcher Windows
├── inprogress.md                 # Estado actual del desarrollo
├── project.md                    # Documentación del proyecto
├── requirements.txt              # Dependencias Python
├── run_server.bat                # Launcher del servidor
├── systemtray.py                 # System tray icon
├── test_find.py                  # Tests
├── app/
│   ├── __init__.py
│   ├── main.py                   # Aplicación FastAPI principal
│   ├── core/
│   │   ├── config.py             # Configuración de la app
│   │   ├── database.py           # Configuración de base de datos
│   │   └── system_tray.py        # System tray implementation
│   ├── models/                   # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── channel.py            # Modelo Channel
│   │   ├── channel_schedule.py   # Modelo ChannelSchedule
│   │   ├── daily_stat.py         # Modelo DailyStat
│   │   ├── log.py                # Modelo TaskLog
│   │   ├── prompt.py             # Modelo Prompt
│   │   ├── publication_schedule.py # Modelo PublicationSchedule
│   │   ├── automation.py         # Modelos de automatización
│   │   ├── config.py             # Modelo GlobalConfig
│   │   ├── content.py            # Modelo ContentItem
│   │   ├── script.py             # Modelo Script
│   │   ├── tag.py                # Modelo Tag
│   │   └── video.py              # Modelo Video
│   ├── routers/                  # Endpoints de la API
│   │   ├── channels.py           # CRUD canales
│   │   ├── scripts.py            # CRUD guiones
│   │   ├── videos.py             # CRUD vídeos
│   │   ├── publications.py       # CRUD publicaciones
│   │   ├── automation.py         # Gestión automatización
│   │   ├── dashboard.py          # Dashboard API
│   │   ├── config.py             # Configuración global
│   │   ├── analytics.py          # Analytics
│   │   ├── content.py            # Gestión contenido
│   │   ├── logs.py               # Logs de tareas
│   │   ├── prompts.py            # Gestión prompts
│   │   ├── scripts_tools.py      # Herramientas de scripts
│   │   └── schedule.py           # Gestión de horarios
│   ├── schemas/                  # Esquemas Pydantic
│   ├── services/                 # Lógica de negocio
│   │   ├── channel_service.py
│   │   ├── schedule_service.py
│   │   ├── analytics_service.py
│   │   └── prompt_service.py
│   ├── static/                   # Archivos frontend
│   │   ├── index.html            # UI principal
│   │   ├── app.js                # JavaScript frontend
│   │   └── styles.css            # Estilos CSS
│   └── tasks/                    # Tareas programadas
│       └── scheduler.py          # APScheduler initialization
├── channels_data/                # Datos de canales
│   ├── cosastqpensar.jpg
│   └── cosastqpensar.json
├── prompts/                      # Plantillas de prompts
│   ├── audio/
│   ├── guion/
│   ├── lluvia_ideas/
│   ├── otro/
│   ├── seo/
│   └── video/
└── tools/                        # Herramientas utilitarias
    ├── __init__.py
    ├── creacionDcanal.py
    ├── DatosDiarios.py
    ├── example.py
    └── script_runner.py
```

### Descripción de Directorios
- **`app/`:** Código principal de la aplicación FastAPI
- **`app/core/`:** Configuración central (database, config, system_tray)
- **`app/models/`:** Modelos de base de datos SQLAlchemy
- **`app/routers/`:** Endpoints de la API REST
- **`app/schemas/`:** Esquemas Pydantic para validación
- **`app/services/`:** Lógica de negocio y servicios
- **`app/static/`:** Archivos estáticos del frontend (HTML, CSS, JS)
- **`app/tasks/`:** Tareas programadas con APScheduler
- **`channels_data/`:** Datos almacenados de canales (imágenes, JSON)
- **`prompts/`:** Plantillas JSON de prompts organizadas por categoría
- **`tools/`:** Herramientas utilitarias y scripts auxiliares

### Contenido de Ficheros Clave
- **`app/main.py`:** Aplicación FastAPI principal, routers, middleware, lifespan, endpoints de admin (shutdown/restart)
- **`app/core/database.py`:** Configuración de SQLAlchemy, motor de base de datos, sesiones
- **`app/core/config.py`:** Configuración de la app desde variables de entorno, funciones de utilidad para API key
- **`app/models/__init__.py`:** Exportación de todos los modelos
- **`app/routers/channels.py`:** CRUD completo de canales (CRUDL)
- **`app/routers/schedule.py`:** Gestión de horarios de canales y publicaciones
- **`app/routers/dashboard.py`:** Endpoint de dashboard con resumen y calendario
- **`app/static/index.html`:** Interfaz web principal
- **`app/static/app.js`:** Lógica del frontend
- **`app/tasks/scheduler.py`:** Inicialización de APScheduler para tareas cron

## 6. Funcionalidades de la Aplicación
### Funcionalidades Principales
1. **Gestión de Canales:** CRUD completo de canales de YouTube con datos extendidos (email, redes sociales, checkpoints, color)
2. **Scraping de Datos:** Tarea diaria automática para obtener métricas de canales (views, subscribers, videos)
3. **Gestión de Guiones:** CRUD de guiones con tags y estados
4. **Gestión de Vídeos:** CRUD de vídeos con metadatos
5. **Publicaciones Programadas:** Calendario de publicaciones con estados y fechas programadas
6. **Automatización:** Tareas de automatización configurables con runs y steps
7. **Dashboard:** Panel con resumen de métricas, gráficos y datos importantes
8. **Analytics:** Análisis de datos de canales
9. **Gestión de Prompts:** Biblioteca de prompts con rating, uso y versiones
10. **Logs de Tareas:** Registro de eventos y errores de tareas automatizadas
11. **Configuración Global:** Gestión de configuraciones clave-valor
12. **System Tray:** Icono en bandeja del sistema para control del servidor
13. **Horarios:** Configuración de frecuencia de contenido por canal (videos largos, shorts, artículos)

### API Endpoints
- **Canales:** `/api/channels` (GET, POST, PUT, DELETE)
- **Guiones:** `/api/scripts` (GET, POST, PUT, DELETE)
- **Vídeos:** `/api/videos` (GET, POST, PUT, DELETE)
- **Publicaciones:** `/api/publications` (GET, POST, PUT, DELETE)
- **Automatización:** `/api/automation` (GET, POST, PUT, DELETE)
- **Dashboard:** `/api/dashboard/summary` (GET con filtro `channel_id`)
- **Analytics:** `/api/analytics` (GET)
- **Contenido:** `/api/content` (GET, POST, PUT, DELETE)
- **Logs:** `/api/logs` (GET, POST)
- **Prompts:** `/api/prompts` (GET, POST, PUT, DELETE)
- **Configuración:** `/api/config` (GET, POST, PUT, DELETE)
- **Horarios:** `/api/schedule` (GET, POST, PUT, DELETE)
- **Scripts Tools:** `/api/scripts-tools` (GET, POST)
- **Admin:** `/admin/shutdown` (POST), `/admin/restart` (POST)
- **Health:** `/health` (GET)
- **Root:** `/` (redirige a `/ui`)

### Tareas Automatizadas
- **Scraping diario:** Tarea APScheduler que obtiene métricas diarias de todos los canales configurados (view_count, subscriber_count, video_count)
- **Sincronización de horarios:** Gestión de frecuencias de publicación por canal

## 7. Estado Actual
### ✅ Cosas Hechas y Funcionando
- Backend FastAPI con modelos SQLAlchemy y todos los routers
- UI web con dashboard, filtros por canal, resumen de guiones/vídeos
- Calendario de publicaciones con día actual marcado y colores de canal
- Modelo Channel extendido con email, social_links, checkpoints, last_scraped_at, last_scrape_status, scrape_data, color
- Servicio de canal actualizado para soportar los nuevos campos
- Esquemas Pydantic extendidos para ChannelCreate, ChannelUpdate, ChannelResponse
- Servicio de dashboard con overview por canal y calendario de publicaciones
- Scheduler APScheduler configurado para tareas cron
- Tarea diaria de scrapping como workflow básico
- Fix de `/api/scripts` para serializar tags como strings (field_serializer)
- Migración ligera en app/main.py para agregar columnas nuevas
- Router `/api/scripts` creado con CRUD completo
- Sincronización de scheduler con cambios en tareas
- Dependencias añadidas (pystray, Pillow)
- Validación de expresiones cron mejorada
- System tray con icono en bandeja del sistema
- Modelos ChannelSchedule y PublicationSchedule para horarios
- Gestión de prompts con rating, versioning y usage tracking
- Tabla de task_logs para seguimiento de eventos

### ⚠️ Fallos Notificados
- **Reinicio de servidor:** El servidor debe reiniciarse para que los cambios de código carguen correctamente en el proceso de Uvicorn (comportamiento esperado de desarrollo)

### 📋 Tareas Pendientes
- [No hay tareas pendientes registradas en los documentos actuales]
- Mejoras potenciales:
  - Mejorar validación de formularios en la UI
  - Añadir más tipos de contenido para desarrollo
  - Implementar autenticación de usuarios
  - Añadir soporte para más plataformas además de YouTube
  - Implementar exportación/importación de configuración

## 8. Notas Adicionales
- La base de datos es SQLite (app.db) con migraciones automáticas en el lifespan de la aplicación
- El proyecto usa YouTube API para obtener métricas de canales (requiere YOUTUBE_API_KEY en .env)
- Hay un sistema de system tray que permite controlar el servidor desde la bandeja del sistema
- Los prompts están organizados por categoría en la carpeta `prompts/`
- Los datos de canales se almacenan en `channels_data/`
- La UI se accede desde `/ui` y consume la API REST en `/api/`
- El proyecto está en GitHub: https://github.com/Sincrtbe/wui.git