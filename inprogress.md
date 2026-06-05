# Proyecto Wui - Documentación en Progreso

## Descripción
Plataforma local para gestionar y automatizar flujos de trabajo de video/audio/imagen/subtítulos para múltiples canales de YouTube, con UI web propia y ejecución local.

## Objetivo
Construir una plataforma local para gestionar y automatizar flujos de trabajo de video/audio/imagen/subtítulos para múltiples canales, con UI web propia y ejecución local.

## Requisitos
- UI web usable en local.
- API CRUD para canales, guiones, vídeos, publicaciones y automatización.
- Dashboard con gráficos y datos importantes.
- Dashboard segmentado por canal y posibilidad de ver todos los elementos o solo los de cada canal.
- Calendario de publicaciones con el día actual marcado.
- Publicaciones coloreadas por canal.
- Canales con información extendida: correo, redes sociales, checkpoints.
- Tarea cron diaria para scrapear información del canal.
- Configuración e información del canal con distintos puntos de control para saber qué redes funcionan.
- Sistema de analytics con estadísticas diarias guardadas en BBDD.
- Sistema de prompts para generación de contenido con LLM.
- Sistema de logs para seguimiento de eventos.
- Ejecución de scripts externos desde `tools/`.

## Estructura del Proyecto
```
Wui/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principal + migraciones
│   ├── core/
│   │   ├── config.py         # Configuración
│   │   └── database.py       # SessionLocal, Engine
│   ├── models/
│   │   ├── channel.py        # Modelo Channel (extendido)
│   │   ├── script.py         # Modelo Script
│   │   ├── video.py          # Modelo Video
│   │   ├── publication.py    # Modelo Publication
│   │   ├── automation.py     # Modelo AutomationRule
│   │   ├── config.py         # Modelo SystemConfig
│   │   ├── daily_stat.py     # Modelo DailyStat (analytics)
│   │   ├── content.py        # Modelo Content
│   │   ├── log.py            # Modelo LogEntry
│   │   ├── prompt.py         # Modelo Prompt
│   │   └── schedule.py       # Modelo PublicationSchedule
│   ├── routers/
│   │   ├── channels.py       # CRUD canales
│   │   ├── scripts.py        # CRUD scripts
│   │   ├── videos.py         # CRUD videos
│   │   ├── publications.py   # CRUD publicaciones
│   │   ├── automation.py     # CRUD automatización
│   │   ├── dashboard.py      # Dashboard summary + calendar
│   │   ├── analytics.py      # Analytics + import daily stats
│   │   ├── config.py         # CRUD config
│   │   ├── content.py        # CRUD content
│   │   ├── logs.py           # CRUD logs
│   │   ├── prompts.py        # CRUD prompts
│   │   └── scripts_tools.py  # Ejecución de scripts
│   ├── schemas/
│   │   ├── channel.py        # Esquemas Pydantic Channel
│   │   ├── dashboard.py      # Esquemas dashboard
│   │   └── ...
│   ├── services/
│   │   ├── channel_service.py
│   │   ├── dashboard_service.py
│   │   ├── analytics_service.py  # Scraping + guardado BBDD
│   │   ├── automation_service.py
│   │   ├── automation_sync.py
│   │   ├── file_service.py
│   │   ├── llm_service.py
│   │   ├── log_service.py
│   │   └── prompt_service.py
│   ├── static/              # UI web (HTML, CSS, JS)
│   │   ├── index.html
│   │   ├── app.js
│   │   └── styles.css
│   └── tasks/
│       ├── scheduler.py     # APScheduler config + tareas cron
│       └── scrape_tasks.py
├── channels_data/           # Datos de canales (JSON)
├── tools/                   # Herramientas auxiliares
│   ├── DatosDiarios.py      # Scraping stats YouTube
│   ├── creacionDcanal.py    # Creación de canales
│   └── script_runner.py     # Ejecutor de scripts
├── metricas/                # Estadísticas diarias (JSON)
├── app.db                   # Base de datos SQLite
├── requirements.txt
├── run_server.bat
├── iniciar.bat
├── .gitignore
├── inprogress.md            # Este fichero
└── project.md               # Descripción original
```

## Modelos de Base de Datos

### Channel
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| title | VARCHAR | Nombre del canal |
| description | TEXT | Descripción |
| workflow | VARCHAR | Workflow asociado |
| color | VARCHAR | Color identificador |
| youtube_id | VARCHAR | ID de YouTube |
| status | VARCHAR | Activo/inactivo |
| email | VARCHAR | Email del canal |
| social_links | JSON | Redes sociales |
| checkpoints | JSON | Puntos de control |
| last_scraped_at | DATETIME | Último scraping |
| last_scrape_status | VARCHAR | Estado del último scraping |
| scrape_data | JSON | Datos crudos del scraping |

### DailyStat
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| channel_id | Integer (FK) | Canal asociado |
| channel_name | VARCHAR | Nombre del canal |
| view_count | INTEGER | Número de vistas |
| subscriber_count | INTEGER | Suscriptores |
| video_count | INTEGER | Número de vídeos |
| stat_date | DATE | Fecha de la estadística |
| fecha_ejecucion | DATE | Fecha de ejecución del script |

### Script
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| title | VARCHAR | Título del guión |
| content | TEXT | Contenido |
| status | VARCHAR | Estado |
| channel_id | Integer (FK) | Canal asociado |

### Video
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| title | VARCHAR | Título del vídeo |
| status | VARCHAR | Estado |
| script_id | Integer (FK) | Guión asociado |

### Publication
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| title | VARCHAR | Título |
| scheduled_date | DATE | Fecha programada |
| video_id | Integer (FK) | Vídeo asociado |

### AutomationRule
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| name | VARCHAR | Nombre |
| trigger_type | VARCHAR | Tipo de trigger |
| config | JSON | Configuración |
| is_active | BOOLEAN | Activo/inactivo |

### Prompt
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| title | VARCHAR | Título |
| content | TEXT | Contenido |
| prompt_type | VARCHAR | Tipo |
| meta_data | JSON | Metadatos (no 'metadata' por reserva SQLAlchemy) |
| created_at | DATETIME | Fecha creación |

### LogEntry
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| level | VARCHAR | Nivel (INFO, WARNING, ERROR) |
| message | TEXT | Mensaje |
| source | VARCHAR | Fuente |
| created_at | DATETIME | Fecha creación |

### Content
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| title | VARCHAR | Título |
| content_type | VARCHAR | Tipo de contenido |
| file_path | VARCHAR | Ruta del fichero |
| channel_id | Integer (FK) | Canal asociado |

### SystemConfig
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| key | VARCHAR | Clave de configuración |
| value | TEXT | Valor |

### PublicationSchedule
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK) | ID autoincremental |
| title | VARCHAR | Título |
| scheduled_datetime | DATETIME | Fecha/hora programada |
| video_id | Integer (FK) | Vídeo asociado |

## API Endpoints

### Canales
- `GET /api/channels` - Listar canales
- `POST /api/channels` - Crear canal
- `GET /api/channels/{id}` - Obtener canal
- `PUT /api/channels/{id}` - Actualizar canal
- `DELETE /api/channels/{id}` - Eliminar canal

### Scripts
- `GET /api/scripts` - Listar scripts (tags como strings)
- `POST /api/scripts` - Crear script
- `GET /api/scripts/{id}` - Obtener script
- `PUT /api/scripts/{id}` - Actualizar script
- `DELETE /api/scripts/{id}` - Eliminar script

### Videos
- `GET /api/videos` - Listar vídeos
- `POST /api/videos` - Crear vídeo
- `GET /api/videos/{id}` - Obtener vídeo
- `PUT /api/videos/{id}` - Actualizar vídeo
- `DELETE /api/videos/{id}` - Eliminar vídeo

### Publications
- `GET /api/publications` - Listar publicaciones
- `POST /api/publications` - Crear publicación
- `GET /api/publications/{id}` - Obtener publicación
- `PUT /api/publications/{id}` - Actualizar publicación
- `DELETE /api/publications/{id}` - Eliminar publicación

### Dashboard
- `GET /api/dashboard/summary?channel_id=X` - Resumen del dashboard
- `GET /api/dashboard/calendar?channel_id=X&year=2026&month=5` - Calendario de publicaciones

### Analytics
- `GET /api/analytics/daily-stats?channel_id=X` - Estadísticas diarias
- `GET /api/analytics/daily-stats/{id}` - Obtener estadística
- `POST /api/analytics/daily-stats?channel_id=X` - Importar estadísticas
- `GET /api/analytics/publications-history/{channel_id}` - Historial de publicaciones
- `POST /api/analytics/import/{channel_id}` - Importar datos de DatosDiarios.py

### Prompts
- `GET /api/prompts` - Listar prompts
- `POST /api/prompts` - Crear prompt
- `GET /api/prompts/{id}` - Obtener prompt
- `PUT /api/prompts/{id}` - Actualizar prompt
- `DELETE /api/prompts/{id}` - Eliminar prompt

### Logs
- `GET /api/logs` - Listar logs
- `POST /api/logs` - Crear log
- `GET /api/logs/{id}` - Obtener log
- `DELETE /api/logs` - Limpiar logs antiguos

### Config
- `GET /api/config` - Listar configuraciones
- `POST /api/config` - Crear configuración
- `PUT /api/config/{id}` - Actualizar configuración
- `DELETE /api/config/{id}` - Eliminar configuración

### Scripts Tools
- `POST /api/scripts/run` - Ejecutar script externo

## DatosDiarios.py - Cómo funciona

### Entrada
Recibe el `channel_id` de YouTube como argumento de línea de comandos, y opcionalmente una ruta de salida:
```bash
python DatosDiarios.py UC_xxxx
python DatosDiarios.py UC_xxxx 'ruta/personalizada'
```

### Salida
1. **Por consola (stdout)**: Imprime un JSON con los datos:
```json
{
    "viewCount": 12345,
    "subscriberCount": 1000,
    "videoCount": 50,
    "fecha_ejecucion": "2026-05-06"
}
```

2. **En un fichero**: Guarda el mismo JSON en `{OUTPUT_DIR}/{channel_id}_stats.json`
   - Por defecto: `metricas/{channel_id}_stats.json`
   - La ruta se puede personalizar con el segundo argumento

### Integración con la API
El servicio `analytics_service.py` llama a este script vía `script_runner.run_script()`:
1. Ejecuta `python DatosDiarios.py {youtube_id} metricas`
2. Lee el JSON generado desde el fichero `metricas/{youtube_id}_stats.json`
3. Importa los datos a la tabla `daily_stats` de la base de datos
4. Evita duplicados para la misma fecha
5. **Borra el fichero JSON** después de guardar en BBDD

### Ejecución automática
- **Al crear un canal**: Se ejecuta scraping inicial automáticamente
- **Tarea diaria programada**: Cada canal tiene una tarea APScheduler programada para las 2:00 AM
- **Scheduler global**: Se inicializa automáticamente al crear el primer canal

## Bugs y estado de la reparación

### Fallos actuales conocidos
- `app/static/app.js` no se puede validar con `py_compile` porque es JavaScript, pero el resto de los archivos Python compilan sin error.
- El servidor debe reiniciarse para que los cambios de código carguen correctamente en el proceso de Uvicorn.
- El endpoint de dashboard puede necesitar más mejoras visuales en la UI, pero la lógica de datos está implementada.
- La tarea de scraping diario está implementada de forma simulada y puede necesitar una integración real de scraping externo.
- No se ha añadido todavía un sistema real de autenticación/autorización para el dashboard.

### Fallos reparados
| Fecha | Bug | Solución |
|-------|-----|----------|
| 2026-05-06 | `GET /api/scripts` devolvía error 500 | Serializar tags como strings en vez de objetos Tag |
| 2026-05-06 | Modelo Channel incompleto | Añadir campos: email, social_links, checkpoints, last_scraped_at, last_scrape_status, scrape_data |
| 2026-05-06 | Dashboard sin filtros | Añadir filtro por channel_id y mostrar info por canal |
| 2026-05-06 | Sin calendario de publicaciones | Añadir calendario con día actual marcado y colores de canal |
| 2026-05-06 | Migración de columnas canales | Añadir migración ligera en main.py con ALTER TABLE |
| 2026-05-06 | Campo 'metadata' reservado en SQLAlchemy | Cambiar a 'meta_data' en modelo Prompt |
| 2026-05-06 | Import circular automation_service ↔ scheduler | Mover imports dentro de funciones en scheduler.py |
| 2026-05-06 | scripts_tools no importado en main.py | Añadir import y registro de router en main.py |
| 2026-05-06 | PublicationSchedule.scheduled_at no existe | Corregir a scheduled_datetime en analytics.py |
| 2026-05-06 | DailyStat sin channel_name | Añadir campo channel_name y fecha_ejecucion al modelo |
| 2026-05-06 | analytics_service no guardaba en BBDD | Actualizar para usar script_runner y guardar en daily_stats |

## Correcciones pendientes
- [ ] Implementar scraping real en lugar de la versión simulada
- [ ] Añadir sistema de autenticación/autorización
- [ ] Mejorar visuales del dashboard en la UI
- [ ] Añadir documentación de API con OpenAPI/Swagger
- [ ] Añadir tests unitarios
- [ ] Implementar sistema de notificaciones

## Historial de cambios
| Fecha | Cambio | Estado |
|-------|--------|--------|
| 2026-05-06 | Creación del repositorio con documentación inprogress.md | Hecho |
| 2026-05-06 | Fix de serialización de tags en `/api/scripts` | Reparado |
| 2026-05-06 | Extensión del modelo Channel con campos adicionales | Reparado |
| 2026-05-06 | Dashboard con filtros por canal y calendario | Reparado |
| 2026-05-06 | Migración ligera para columnas nuevas en canales | Reparado |
| 2026-05-06 | Sincronización desde GitHub - routers (analytics, config, scripts) | Hecho |
| 2026-05-06 | Sincronización desde GitHub - modelos (content, log, prompt) | Hecho |
| 2026-05-06 | Corrección de campo 'metadata' → 'meta_data' en Prompt | Reparado |
| 2026-05-06 | Corrección de import circular automation_service ↔ scheduler | Reparado |
| 2026-05-06 | Corrección de scripts_tools no importado en main.py | Reparado |
| 2026-05-06 | Corrección de PublicationSchedule.scheduled_at → scheduled_datetime | Reparado |
| 2026-05-06 | Modelo DailyStat extendido con channel_name y fecha_ejecucion | Hecho |
| 2026-05-06 | analytics_service.py guarda métricas en BBDD | Hecho |
| 2026-05-06 | Endpoint POST /api/analytics/import/{channel_id} | Hecho |
| 2026-05-06 | DatosDiarios.py ejecutado y datos guardados en BBDD | Hecho |
| 2026-05-06 | Corrección: PublicationSchedule no tiene campo 'platform' | Reparado |
| 2026-05-06 | analytics_service.py borra fichero JSON después de guardar en BBDD | Hecho |
| 2026-05-06 | Ficheros de métricas se guardan en metricas/ (no tools/metricas/) | Hecho |
| 2026-05-06 | Scraping automático al crear canal (ejecución + programación diaria) | Hecho |
| 2026-05-06 | Tarea diaria programada por canal con APScheduler (2:00 AM) | Hecho |
| 2026-05-06 | Repositorio creado y subido a GitHub | Hecho |

## Nuevas carpetas
- `metricas/` - Estadísticas diarias de canales (ficheros JSON con viewCount, subscriberCount, videoCount, fecha_ejecucion)

## Tecnologías usadas
- **Backend**: Python, FastAPI, SQLAlchemy
- **Base de datos**: SQLite
- **Scheduler**: APScheduler
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Dependencias**: Ver `requirements.txt`

## Cómo ejecutar
```bash
# Iniciar el servidor
.\run_server.bat

# O directamente
python -m uvicorn app.main:app --reload --port 9080
```

## UI Web
Acceder en: `http://127.0.0.1:9080/ui`