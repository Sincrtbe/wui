# Proyecto Wui

## Objetivo
Construir una plataforma local para gestionar y automatizar flujos de trabajo de video/audio/imagen/subtítulos para múltiples canales, con UI web propia y ejecución local.

## Requisitos pedidos
- UI web usable en local.
- API CRUD para canales, guiones, vídeos, publicaciones y automatización.
- Dashboard con gráficos y datos importantes.
- Dashboard segmentado por canal y posibilidad de ver todos los elementos o solo los de cada canal.
- Calendario de publicaciones con el día actual marcado.
- Publicaciones coloreadas por canal.
- Canales con información extendida: correo, redes sociales, checkpoints.
- Tarea cron diaria para scrapear información del canal.
- Configuración e información del canal con distintos puntos de control para saber qué redes funcionan.

## Qué hay hecho
- Backend FastAPI con modelos SQLAlchemy y routers para: `channels`, `scripts`, `videos`, `publications`, `automation`, `dashboard`.
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

## Estado actual
- El servidor arranca y los archivos Python compilados sin errores de sintaxis.
- `GET /api/dashboard/summary` soporta filtro opcional por `channel_id`.
- UI carga en `/ui` y el dashboard consume el API.
- Los canales ahora incluyen datos ampliados y la interfaz de creación acepta esos campos.
