# Wui - Plataforma de Automatización de YouTube

## Estado del Proyecto
**Fecha última actualización:** 2026-09-06  
**Estado:** En desarrollo activo  
**Versión:** 1.0.0

---

## Descripción

Wui es una plataforma local de automatización para la gestión de múltiples canales de YouTube. Permite gestionar canales, crear contenido, programar publicaciones, analizar métricas, automatizar flujos de trabajo y gestionar una biblioteca de prompts con IA.

---

## Stack Tecnológico

### Lenguajes
- **Python** 3.x (backend principal)
- **JavaScript** (frontend)
- **HTML5/CSS3** (frontend)

### Frameworks y Librerías
- **FastAPI** 0.104.1 (backend API REST)
- **SQLAlchemy** 2.0.23 (ORM)
- **Uvicorn** 0.24.0 (servidor ASGI)
- **APScheduler** 3.10.4 (tareas programadas/cron)
- **pydantic** 2.5.0 (validación de datos)
- **google-api-python-client** 2.197.0 (API de YouTube)
- **pystray** 0.19.5 (system tray icon)
- **Pillow** 10.1.0 (manipulación de imágenes)
- **python-dotenv** 1.0.0 (variables de entorno)
- **alembic** 1.13.1 (migraciones de base de datos)

### Base de Datos
- **SQLite** (app.db)

---

## Estructura del Proyecto

```
Wui/
├── .env                          # Variables de entorno (API keys, etc.)
├── .gitignore                    # Archivos a ignorar por git
├── app.db                        # Base de datos SQLite
├── requirements.txt              # Dependencias Python
├── run_server.bat                # Launcher del servidor
├── iniciar.bat                   # Launcher Windows
├── systemtray.py                 # System tray icon
├── README.md                     # Documentación principal
│
├── app/
│   ├── __init__.py
│   ├── main.py                   # Aplicación FastAPI principal
│   ├── core/
│   │   ├── config.py             # Configuración de la app
│   │   └── database.py           # Configuración de base de datos
│   ├── models/                   # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── channel.py
│   │   ├── channel_schedule.py
│   │   ├── daily_stat.py
│   │   ├── prompt.py
│   │   ├── publication_schedule.py
│   │   ├── script.py
│   │   ├── video.py
│   │   └── ...
│   ├── routers/                  # Endpoints de la API REST
│   │   ├── channels.py           # CRUD canales
│   │   ├── schedule.py           # Gestión de horarios
│   │   ├── dashboard.py          # Dashboard API
│   │   ├── analytics.py          # Analytics
│   │   ├── prompts.py            # Gestión prompts
│   │   └── ...
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
│
├── channels_data/                # Datos de canales (imágenes, JSON)
├── prompts/                      # Plantillas de prompts por categoría
│   ├── audio/
│   ├── guion/
│   ├── lluvia_ideas/
│   ├── otro/
│   ├── seo/
│   └── video/
├── skills/                       # Skills de desarrollo
│   └── desarrollosoftware/
└── tools/                        # Herramientas utilitarias
    ├── creacionDcanal.py
    ├── DatosDiarios.py
    ├── qwen3tts.py
    └── script_runner.py
```

---

## Funcionalidades Implementadas

### 1. Gestión de Canales
- CRUD completo de canales de YouTube
- Datos extendidos: email, social_links, checkpoints, color personalizado
- Thumbnail/imagen del canal
- URL personalizada
- Estado de scraping (éxito/error)
- Fecha de última actualización
- Generación de ficheros por canal

### 2. Programación de Publicaciones
- Configuración de periodicidad por canal:
  - Videos largos (frecuencia configurable en días)
  - Shorts (frecuencia configurable en días)
  - Artículos (frecuencia configurable en días)
- Fecha de inicio configurable
- Estado activo/inactivo por canal
- Calendario bimensual (mes actual + siguiente)
- Generación automática de publicaciones
- Próximas publicaciones con indicador de guión

### 3. Gestión de Contenido
- Flujo de trabajo: Idea → Guión → Desarrollo → Video
- Lluvia de ideas con notas
- Generación de guiones con IA
- Gestión de artículos
- Avance de etapas

### 4. Análisis y Métricas
- Suscriptores, vistas, videos
- Evolución de vistas en gráfico
- Historial de publicaciones
- Importación de datos diarios
- Botón "Comprobar Datos de Hoy"

### 5. Biblioteca de Prompts
- Creación y gestión de prompts
- Tipos: lluvia_ideas, guion, audio, video, seo
- Variables detectadas automáticamente (`{{variable}}`)
- Sistema de rating (0-5)
- Conteo de usos
- Búsqueda y filtrado por tipo

### 6. Automatización
- Tareas programadas con cron
- Ejecución de workflows
- Historial de ejecuciones
- Sincronización con APScheduler

### 7. Dashboard
- Resumen general con métricas
- Filtros por canal
- Calendario de publicaciones con día actual marcado
- Colores por canal
- Resumen de guiones y vídeos por estado

### 8. Configuración
- Servicios externos (API keys, URLs)
- YouTube API Key segura (almacenamiento en .env)
- Programación de analíticas (cron)
- Configuración de video (transiciones, subtítulos)

### 9. System Tray
- Icono en bandeja del sistema
- Control del servidor desde la bandeja

---

## Base de Datos (SQLite)

### Tablas principales

| Tabla | Descripción |
|-------|-------------|
| **channels** | Canales de YouTube (id, title, customUrl, thumbnail, channel_color, email, social_links, checkpoints, last_scraped_at, last_scrape_status, created_at, updated_at) |
| **channel_schedules** | Programación por canal (id, channel_id, long_video_enabled/frequency, short_video_enabled/frequency, article_enabled/frequency, start_date, timezone, is_active, created_at, updated_at) |
| **publication_schedules** | Publicaciones programadas (id, channel_id, script_id, content_type, scheduled_datetime, status, notes, created_at, updated_at) |
| **scripts** | Guiones (id, channel_id, title, description, script_content, article_content, voice_script, graphic_script, tags, status, created_at, updated_at) |
| **prompts** | Biblioteca de prompts (id, title, description, content, prompt_type, variables, rating, usage_count, version, created_at, updated_at) |
| **daily_stats** | Estadísticas diarias (id, channel_id, stat_date, subscriber_count, view_count, video_count, created_at, updated_at) |
| **config** | Configuración del sistema (id, key, value, updated_at) |

---

## API Endpoints

### Canales
- `GET /api/channels` - Listar todos los canales
- `POST /api/channels` - Crear canal
- `GET /api/channels/{id}` - Obtener canal
- `PATCH /api/channels/{id}` - Actualizar canal
- `DELETE /api/channels/{id}` - Eliminar canal
- `GET /api/channels/{id}/thumbnail` - Obtener thumbnail
- `POST /api/channels/tools/create-files` - Crear ficheros del canal

### Programación
- `GET /api/schedules/channel/{channel_id}` - Obtener programación
- `POST /api/schedules/channel/{channel_id}` - Crear programación
- `PUT /api/schedules/channel/{channel_id}` - Actualizar programación
- `GET /api/schedules/channel/{channel_id}/calendar/months` - Calendario bimensual
- `POST /api/schedules/channel/{channel_id}/generate` - Generar publicaciones
- `GET /api/schedules/channel/{channel_id}/upcoming` - Próximas publicaciones
- `POST /api/schedules/publication/{id}/assign-script` - Asignar guión
- `PUT /api/schedules/publication/{id}` - Actualizar publicación
- `DELETE /api/schedules/publication/{id}` - Eliminar publicación

### Prompts
- `GET /api/prompts` - Listar prompts
- `POST /api/prompts` - Crear prompt
- `GET /api/prompts/{id}` - Obtener prompt
- `PATCH /api/prompts/{id}` - Actualizar prompt
- `DELETE /api/prompts/{id}` - Eliminar prompt
- `POST /api/prompts/{id}/rate?rating=X` - Calificar prompt

### Análisis
- `GET /api/analytics/daily-stats/{channel_id}` - Estadísticas diarias
- `GET /api/analytics/publications-history/{channel_id}` - Historial
- `POST /api/analytics/import/{channel_id}` - Importar datos

### Dashboard
- `GET /api/dashboard/summary?channel_id=X` - Resumen general

### Configuración
- `GET /api/config` - Listar configuración
- `POST /api/config` - Guardar configuración
- `GET /api/config/youtube-key` - Estado de la API Key (enmascarada)
- `POST /api/config/youtube-key` - Guardar API Key

### Otros
- `GET /health` - Health check
- `/` - Redirige a `/ui`
- `POST /admin/shutdown` - Apagar servidor
- `POST /admin/restart` - Reiniciar servidor

---

## Correcciones y Bugs Reparados

### YouTube API Key segura
- **Problema:** API Key hardcodeada en los scripts
- **Solución:** Sistema completo con `.env`, configuración en `config.py`, endpoints seguros, UI con key enmascarada
- **Seguridad:** La key nunca se almacena en BD, nunca se muestra en claro, nunca se sube a git

### Calendario descuadrado
- **Problema:** Headers insertados dentro del CSS grid
- **Solución:** Reordenar estructura HTML (headers fuera del grid), eliminar `aspect-ratio: 1`

### Calendario no mostraba eventos
- **Problema:** Zona horaria causaba errores en filtrado de fechas
- **Solución:** Parsing directo de cadena ISO en lugar de `new Date()`

### Serialización de tags
- **Problema:** `GET /api/scripts` devolvía error 500 por Tag objects
- **Solución:** Añadido `field_serializer` en `ScriptResponse`

### Router `/api/scripts` faltante
- **Problema:** No existía el router de scripts
- **Solución:** Creado `app/routers/scripts.py` con CRUD completo

### Scheduler sincronización
- **Problema:** Desincronización entre APScheduler y tareas
- **Solución:** Sincronización en `create()`, `update()` y `delete()`

### Parser de cron
- **Problema:** Sin validación de expresiones cron
- **Solución:** Validación de 5 campos y manejo de errores

---

## Instrucciones de Uso

### Instalación
```bash
pip install -r requirements.txt
```

### Iniciar el servidor
```bash
# Opción 1: Batch file
.\run_server.bat

# Opción 2: Manual
uvicorn app.main:app --reload --port 9080
```

### Acceder
- **UI Web:** http://127.0.0.1:9080/ui
- **API Base:** http://127.0.0.1:9080
- **Health Check:** http://127.0.0.1:9080/health

### Flujo de trabajo recomendado
1. **Configurar API Key:** Configuración → Servicios → YouTube API Key
2. **Crear canal:** Canales → Introducir nombre → Guardar
3. **Configurar programación:** Seleccionar canal → Activar tipos → Configurar frecuencia
4. **Generar calendario:** "Generar Mes Actual" y "Generar Mes Siguiente"
5. **Gestionar contenido:** Crear ideas → Generar guiones → Asociar a publicaciones

---

## Próximas Mejoras

- [ ] Integración con IA para generación de contenido
- [ ] Soporte para más plataformas (TikTok, Twitter, etc.)
- [ ] Exportación de contenido a video
- [ ] Notificaciones de publicaciones programadas
- [ ] Sistema de autenticación de usuarios
- [ ] Exportar/Importar base de datos
- [ ] Sistema de backups automático
- [ ] Mejorar responsive del calendario

---

## Repositorio

- **Remote:** https://github.com/Sincrtbe/wui.git
- **Rama:** master
- **Estado:** Activo

---

## Licencia
Proyecto interno de automatización.