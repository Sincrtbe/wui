# Proyecto Wui - Documentación en Progreso

## Descripción
Plataforma local para gestionar y automatizar flujos de trabajo de video/audio/imagen/subtítulos para múltiples canales, con UI web propia y ejecución local.

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

## Estructura del Proyecto
```
Wui/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principal
│   ├── core/
│   ├── models/
│   │   └── channel.py       # Modelo Channel extendido
│   ├── routers/
│   │   └── channels.py      # CRUD canales
│   ├── schemas/
│   │   ├── channel.py       # Esquemas Pydantic
│   │   └── dashboard.py     # Esquemas dashboard
│   ├── services/
│   │   ├── channel_service.py
│   │   └── dashboard_service.py
│   ├── static/              # UI web (HTML, CSS, JS)
│   └── tasks/               # Tareas cron APScheduler
├── channels_data/           # Datos de canales (JSON)
├── tools/                   # Herramientas auxiliares
├── app.db                   # Base de datos SQLite
├── requirements.txt
├── run_server.bat
└── iniciar.bat
```

## Qué hay hecho
- Backend FastAPI con modelos SQLAlchemy y routers para: `channels`, `scripts`, `videos`, `publications`, `automation`, `dashboard`, `analytics`, `config`, `content`, `logs`, `prompts`, `scripts_tools`.
- UI estática simple en `app/static/index.html`, `app/static/app.js`, `app/static/styles.css`.
- Dashboard actualizado con:
  - filtros por canal.
  - resumen de guiones por estado.
  - resumen de vídeos por estado.
  - resumen por canal con color, email, redes sociales, checkpoints, últimos scrapes.
  - calendario de publicaciones con día actual marcado y colores de canal.
- Modelo `Channel` extendido con `email`, `social_links`, `checkpoints`, `last_scraped_at`, `last_scrape_status`, `scrape_data`.
- Servicio de canal actualizado para soportar los nuevos campos.
- Esquemas Pydantic extendidos para `ChannelCreate`, `ChannelUpdate`, `ChannelResponse`.
- Servicio de dashboard actualizado para mostrar overview por canal y calendario de publicaciones.
- Scheduler APScheduler configurado para tareas cron.
- Tarea diaria de scrapping añadido como workflow básico `scrape_channel_info`.
- Fix de `/api/scripts` para serializar correctamente tags como strings.
- Migración ligera en `app/main.py` para agregar columnas nuevas a la tabla de canales cuando existe la base de datos.
- Sistema de Prompts con CRUD completo.
- Sistema de Logs con seguimiento de eventos.
- Sistema de Analytics con estadísticas diarias y historial de publicaciones.
- Herramientas de ejecución de scripts desde `tools/`.

## Estado actual
- El servidor arranca y los archivos Python compilan sin errores de sintaxis.
- `GET /api/dashboard/summary` soporta filtro opcional por `channel_id`.
- UI carga en `/ui` y el dashboard consume el API.
- Los canales ahora incluyen datos ampliados y la interfaz de creación acepta esos campos.
- Endpoint `/api/analytics/publications-history/1` funciona correctamente.
- DatosDiarios.py ejecutado correctamente para canal Cosasqpensar (UC2QFapkF39LMe_0yXJ_TsZw).
- Carpeta `metricas/` creada con ficheros de estadísticas diarias.

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
   - Por defecto: `vistas_diarias/{channel_id}_stats.json`
   - La ruta se puede personalizar con el segundo argumento

### Integración con la API
El servicio `analytics_service.py` llama a este script vía `script_runner.run_script()`:
1. Ejecuta `python DatosDiarios.py {youtube_id} vistas_diarias`
2. Lee el JSON generado desde el fichero `tools/vistas_diarias/{youtube_id}_stats.json`
3. Importa los datos a la tabla `daily_stats` de la base de datos
4. Evita duplicados para la misma fecha

## Bugs y estado de la reparación

### Fallos actuales conocidos
- `app/static/app.js` no se puede validar con `py_compile` porque es JavaScript, pero el resto de los archivos Python compilan sin error.
- El servidor debe reiniciarse para que los cambios de código carguen correctamente en el proceso de Uvicorn.
- El endpoint de dashboard puede necesitar más mejoras visuales en la UI, pero la lógica de datos está implementada.
- La tarea de scraping diario está implementada de forma simulada y puede necesitar una integración real de scraping externo.
- No se ha añadido todavía un sistema real de autenticación/autorización para el dashboard.

### Fallos reparados
- `GET /api/scripts` devolvía error 500 por serializar objetos `Tag` en vez de strings en el campo `tags`.
- Se extendió el modelo `Channel` y los esquemas para incluir `email`, `social_links`, `checkpoints`, `last_scraped_at`, `last_scrape_status` y `scrape_data`.
- Se actualizó el dashboard para filtrar por canal y mostrar información de cada canal.
- Se añadió un calendario de publicaciones con el día actual marcado y color por canal.
- Se arregló la semilla inicial para crear canales con los nuevos campos usando `ChannelCreate`.
- Se agregó una migración ligera en `app/main.py` para extender la tabla `channels` cuando ya existe la base de datos.
- **Error 'metadata' reservado en SQLAlchemy**: El campo `metadata` del modelo `Prompt` se cambió a `meta_data` porque `metadata` es un atributo reservado de SQLAlchemy.
- **Import circular automation_service ↔ scheduler**: Se rompió el ciclo moviendo los imports de `AutomationService` y `run_daily_stats_import` dentro de las funciones `_run_automation_task` y `_run_daily_analytics` en `scheduler.py`.
- **scripts_tools no importado en main.py**: Se añadió la importación de `scripts_tools` al router y se registró en `main.py`.
- **PublicationSchedule.scheduled_at no existe**: Se corrigió a `scheduled_datetime` en `analytics.py`.

## Correcciones pendientes
- [ ] Implementar scraping real en lugar de la versión simulada
- [ ] Añadir sistema de autenticación/autorización
- [ ] Mejorar visuales del dashboard en la UI
- [ ] Configurar .gitignore para excluir app.db y archivos binarios
- [ ] Añadir documentación de API con OpenAPI/Swagger

## Historial de cambios
| Fecha | Cambio | Estado |
|-------|--------|--------|
| 2026-05-06 | Creación del repositorio con documentación inprogress.md | Hecho |
| 2026-05-06 | Fix de serialización de tags en `/api/scripts` | Reparado |
| 2026-05-06 | Extensión del modelo Channel con campos adicionales | Reparado |
| 2026-05-06 | Dashboard con filtros por canal y calendario | Reparado |
| 2026-05-06 | Migración ligera para columnas nuevas en canales | Reparado |
| 2026-05-06 | Sincronización desde GitHub - nuevos routers (analytics, config, scripts), modelos (config, daily_stat), servicios (analytics, automation_sync), actualizaciones masivas de UI | Hecho |
| 2026-05-06 | Sincronización desde GitHub - nuevos modelos (content, log, prompt), routers (content, logs, prompts), servicios (file, llm, log, prompt), actualizaciones de UI | Hecho |
| 2026-05-06 | Corrección de campo 'metadata' → 'meta_data' en Prompt model | Reparado |
| 2026-05-06 | Corrección de import circular automation_service ↔ scheduler | Reparado |
| 2026-05-06 | Corrección de scripts_tools no importado en main.py | Reparado |
| 2026-05-06 | Corrección de PublicationSchedule.scheduled_at → scheduled_datetime | Reparado |
| 2026-05-06 | Ejecución de DatosDiarios.py para canal Cosasqpensar, creación de carpeta metricas/ | Hecho |

## Nuevas carpetas
- `metricas/` - Estadísticas diarias de canales (ficheros JSON con viewCount, subscriberCount, videoCount, fecha_ejecucion)

## Tecnologías usadas
- **Backend**: Python, FastAPI, SQLAlchemy
- **Base de datos**: SQLite
- **Scheduler**: APScheduler
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Dependencias**: Ver `requirements.txt`