# Wui - Plataforma de Automatización de Canales YouTube

## Estado del Proyecto
**Fecha última actualización:** 2026-05-06  
**Estado:** En desarrollo activo

---

## Descripción del Proyecto

Wui es una plataforma local de automatización para la gestión de múltiples canales de YouTube. Permite:
- Gestionar múltiples canales de YouTube
- Crear y organizar contenido (ideas, guiones, artículos, videos)
- Programar publicaciones (videos largos, shorts, artículos)
- Analizar métricas de rendimiento
- Automatizar flujos de trabajo
- Gestionar una biblioteca de prompts con IA

---

## Estructura del Proyecto

```
Wui/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application principal
│   ├── core/
│   │   ├── database.py            # Configuración de base de datos SQLite
│   │   └── config.py              # Configuración de la aplicación
│   ├── models/
│   │   ├── __init__.py            # Imports de modelos
│   │   ├── channel.py             # Modelo Channel (canales de YouTube)
│   │   ├── channel_schedule.py    # Modelo ChannelSchedule (programación por canal)
│   │   ├── publication_schedule.py # Modelo PublicationSchedule (publicaciones programadas)
│   │   ├── script.py              # Modelo Script (guiones)
│   │   ├── prompt.py              # Modelo Prompt (biblioteca de prompts)
│   │   └── daily_stat.py          # Modelo DailyStat (estadísticas diarias)
│   ├── routers/
│   │   ├── channels.py            # CRUD de canales
│   │   ├── schedule.py            # Programación de publicaciones
│   │   ├── prompts.py             # Biblioteca de prompts
│   │   ├── analytics.py           # Análisis de métricas
│   │   └── dashboard.py           # Dashboard general
│   ├── schemas/
│   │   ├── channel.py             # Esquemas Pydantic para canales
│   │   └── dashboard.py           # Esquemas para dashboard
│   ├── services/
│   │   ├── channel_service.py     # Lógica de negocio de canales
│   │   ├── schedule_service.py    # Lógica de programación
│   │   ├── analytics_service.py   # Lógica de análisis
│   │   └── prompt_service.py      # Lógica de prompts
│   ├── tasks/
│   │   └── scheduler.py           # Tareas programadas (APScheduler)
│   └── static/
│       ├── index.html             # Interfaz principal
│       ├── app.js                 # JavaScript frontend
│       └── styles.css             # Estilos CSS
├── tools/
│   ├── creacionDcanal.py          # Script de creación de canales
│   ├── DatosDiarios.py            # Script de datos diarios
│   └── script_runner.py           # Ejecutor de scripts
├── channels_data/                 # Datos de canales (JSON, imágenes)
├── app.db                         # Base de datos SQLite
├── requirements.txt               # Dependencias Python
├── run_server.bat                 # Script de inicio del servidor
└── iniciar.bat                    # Script de inicio rápido
```

---

## Funcionalidades Implementadas

### 1. Gestión de Canales
- CRUD completo de canales de YouTube
- Almacenamiento de thumbnail/imagen del canal
- Color personalizado por canal
- URL personalizada
- Estado de scraping (éxito/error)
- Fecha de última actualización

### 2. Programación de Publicaciones
- Configuración de periodicidad por canal:
  - Videos largos (frecuencia configurable en días)
  - Shorts (frecuencia configurable en días)
  - Artículos (frecuencia configurable en días)
- Fecha de inicio configurable
- Estado activo/inactivo por canal
- Calendario bimensual (mes actual + siguiente)
- Generación automática de publicaciones basadas en la programación
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

### 7. Configuración
- Servicios externos (API keys, URLs)
- Programación de analíticas (cron)
- Configuración de video (transiciones, subtítulos)

---

## Base de Datos (SQLite)

### Tablas principales:

1. **channels** - Canales de YouTube
   - id, title, customUrl, publishedAt, description
   - thumbnail, channel_color, last_scraped_at
   - last_scrape_status, created_at, updated_at

2. **channel_schedules** - Programación por canal
   - id, channel_id (FK)
   - long_video_enabled, long_video_frequency
   - short_video_enabled, short_video_frequency
   - article_enabled, article_frequency
   - start_date, timezone, is_active
   - created_at, updated_at

3. **publication_schedules** - Publicaciones programadas
   - id, channel_id (FK), script_id (FK)
   - content_type (long_video, short, article)
   - scheduled_datetime, status (planned, published, cancelled)
   - notes, created_at, updated_at

4. **scripts** - Guiones
   - id, channel_id (FK)
   - title, description, script_content
   - article_content, voice_script, graphic_script
   - tags, status, created_at, updated_at

5. **prompts** - Biblioteca de prompts
   - id, title, description, content
   - prompt_type, variables (JSON)
   - rating, usage_count, version
   - created_at, updated_at

6. **daily_stats** - Estadísticas diarias
   - id, channel_id (FK)
   - stat_date, subscriber_count, view_count
   - video_count, created_at, updated_at

7. **config** - Configuración del sistema
   - id, key, value, updated_at

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

---

## Correcciones Realizadas

### 4. Calendario no muestra eventos (Bug en renderCalendarView)
**Fecha:** 2026-06-06  
**Problema:** Las programaciones generadas no aparecían en el calendario del detalle de canal. La API devolvía los datos correctamente (`/api/schedules/channel/1/calendar/months` retornaba eventos con fechas como `"2026-06-04"`), pero el frontend no los filtraba correctamente por día.

**Causa:** La función `renderCalendarView` en `app/static/app.js` usaba `new Date(e.date).getDate()` para filtrar eventos por día. Las fechas ISO `"YYYY-MM-DD"` pueden interpretarse incorrectamente dependiendo de la zona horaria (se interpretan como UTC y al aplicar `getDate()` puede dar un día diferente en zonas UTC+2).

**Solución:** Cambiar el filtrado de fechas para usar parsing directo de la cadena ISO en lugar de `new Date()`:
```javascript
// ANTES (incorrecto por zona horaria):
const dayEvents = eventsCurrent.filter(e => new Date(e.date).getDate() === currentDay);

// DESPUÉS (correcto, parsing directo):
const dayEvents = eventsCurrent.filter(e => {
  const parts = e.date.split('-');
  return parseInt(parts[2]) === currentDay;
});
```

**Archivos modificados:**
- `app/static/app.js` - Función `renderCalendarView` (líneas de filtrado de `dayEvents` en mes actual y siguiente)

### 1. Conflicto de nombres en routers/schedule.py
**Problema:** La función del router `update_channel_schedule` tenía el mismo nombre que la función del servicio importada, causando un `TypeError` al intentar guardar la configuración de periodicidad.

**Error:**
```
TypeError: 'function' object has no attribute 'channel_id'
```

**Solución:** Renombrar la importación del servicio como `service_update_channel_schedule` y la función del router como `put_channel_schedule`.

### 2. Calendario bimensual
**Problema:** El calendario solo mostraba un mes y no estaba correctamente alineado.

**Solución:** 
- Implementar `renderCalendarView` que muestra mes actual y siguiente
- Usar grid de 7 columnas (Lunes a Domingo)
- Calcular correctamente el primer día del mes
- Usar 42 celdas (6 semanas) para cubrir todos los casos

### 3. Estructura de la página de canales
**Mejora:** Reorganizar la vista de detalle de canal en secciones:
- Información general
- Estadísticas recientes
- Configuración de periodicidad (con tarjetas para cada tipo de contenido)
- Calendario de publicaciones (bimensual)
- Próximas publicaciones

---

## Tecnologías Utilizadas

- **Backend:** Python 3.x, FastAPI, SQLAlchemy, APScheduler
- **Base de datos:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript vanilla
- **Dependencias:**
  - fastapi
  - uvicorn
  - sqlalchemy
  - aiosqlite
  - apscheduler
  - httpx
  - python-multipart
  - requests

---

## Instrucciones de Uso

### Iniciar el servidor
```bash
.\run_server.bat
```
O manualmente:
```bash
uvicorn app.main:app --reload --port 9080
```

### Acceder a la interfaz
Abrir navegador en: `http://127.0.0.1:9080`

### Flujo de trabajo recomendado
1. **Crear canal:** Ir a "Canales" → Introducir nombre → "Crear Ficheros" → "Guardar Canal en BD"
2. **Configurar programación:** Seleccionar canal → Activar tipos de contenido → Configurar frecuencia → Guardar
3. **Generar calendario:** "Generar Mes Actual" y "Generar Mes Siguiente"
4. **Gestionar contenido:** Seleccionar canal → Gestionar contenido → Crear ideas → Generar guiones
5. **Asociar guiones:** En "Próximas Publicaciones" → Asociar guión a publicación

---

## Próximas Mejoras

- [ ] Integración con IA para generación de contenido
- [ ] Soporte para más plataformas (TikTok, Twitter, etc.)
- [ ] Exportación de contenido a video
- [ ] Notificaciones de publicaciones programadas
- [ ] Sistema de tray icon (systemtray.py existente)
- [ ] Mejorar responsive del calendario
- [ ] Exportar/Importar base de datos
- [ ] Sistema de backups automático

---

## Notas Técnicas

### Modelo de Programación
La programación se basa en frecuencias relativas a la `start_date`:
- Si `start_date` es 2026-05-01 y frecuencia es 3 días
- Las publicaciones se generan en días: 0, 3, 6, 9, 12...
- Cada tipo de contenido tiene su propia frecuencia

### Estados de Publicación
- `planned` - Programada pero no publicada
- `published` - Publicada
- `cancelled` - Cancelada

### Estados de Script
- `idea` - Solo idea
- `script` - Guión generado
- `developed` - Contenido desarrollado
- `video` - Video final

---

## Equipo
Desarrollo activo - Ver historial de git para contribuciones.

## Licencia
Proyecto interno de automatización.