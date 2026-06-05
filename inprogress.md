# Wui - Plataforma de Automatización Multimedia

## Estado del Proyecto
En desarrollo activo. Este fichero documenta todo lo que se está haciendo y corrigiendo en el proyecto.

---

## 📋 Resumen del Proyecto

**Wui** es una plataforma local de automatización multimedia construida con FastAPI (Python) que permite:
- Gestionar múltiples canales de YouTube
- Automatizar la creación de contenido (videos, shorts, artículos)
- Programar publicaciones con calendarios visuales
- Analizar métricas de rendimiento
- Automatizar flujos de trabajo con IA

---

## 🏗️ Arquitectura

### Backend
- **Framework**: FastAPI
- **Base de datos**: SQLite (SQLAlchemy ORM)
- **Tareas en segundo plano**: APScheduler
- **System Tray**: Icono de sistema para control del servidor

### Frontend
- **Tecnología**: HTML + CSS + JavaScript vanilla
- **Estilos**: CSS moderno con Grid y Flexbox
- **Componentes**: Dialogs nativos (modales HTML)

---

## 📁 Estructura del Proyecto

```
Wui/
├── app/
│   ├── core/
│   │   ├── database.py          # Configuración de base de datos
│   │   └── system_tray.py       # Icono de system tray
│   ├── models/
│   │   ├── __init__.py          # Modelos base
│   │   ├── channel.py           # Modelo Canal
│   │   ├── channel_schedule.py  # Programación de canal
│   │   ├── daily_stat.py        # Estadísticas diarias
│   │   ├── prompt.py            # Biblioteca de prompts
│   │   ├── publication_schedule.py # Programación de publicaciones
│   │   └── script.py            # Guiones
│   ├── routers/
│   │   ├── analytics.py         # API de análisis
│   │   ├── automation.py        # Automatización
│   │   ├── channels.py          # Gestión de canales
│   │   ├── config.py            # Configuración global
│   │   ├── content.py           # Gestión de contenido
│   │   ├── dashboard.py         # Dashboard API
│   │   ├── logs.py              # Logs de tareas
│   │   ├── prompts.py           # API de prompts
│   │   ├── publications.py      # Publicaciones
│   │   ├── schedule.py          # Programación de publicaciones
│   │   ├── scripts.py           # Guiones
│   │   ├── scripts_tools.py     # Herramientas de scripts
│   │   └── videos.py            # Videos
│   ├── schemas/
│   │   ├── channel.py           # Esquemas Pydantic de canales
│   │   └── dashboard.py         # Esquemas de dashboard
│   ├── services/
│   │   ├── analytics_service.py # Lógica de análisis
│   │   ├── channel_service.py   # Lógica de canales
│   │   ├── prompt_service.py    # Lógica de prompts
│   │   └── schedule_service.py  # Lógica de programación
│   ├── static/
│   │   ├── index.html           # Interfaz web principal
│   │   ├── app.js               # JavaScript de la UI
│   │   └── styles.css           # Estilos CSS
│   ├── tasks/
│   │   └── scheduler.py         # Tareas programadas
│   └── main.py                  # Aplicación FastAPI
├── tools/
│   ├── creacionDcanal.py        # Creación de canales
│   ├── DatosDiarios.py          # Datos diarios
│   └── script_runner.py         # Ejecutor de scripts
├── channels_data/               # Datos de canales
├── app.db                       # Base de datos SQLite
├── requirements.txt             # Dependencias
├── run_server.bat               # Script de inicio
└── inprogress.md                # Este fichero
```

---

## 🆕 Funcionalidades Recientes Añadidas

### Sistema de Programación de Publicaciones

#### 1. Modelo ChannelSchedule (`app/models/channel_schedule.py`)
Define la programación recurrente por tipo de contenido para cada canal:
- **long_video_enabled**: Activar/desactivar videos largos
- **long_video_frequency**: Frecuencia de videos largos (días)
- **short_video_enabled**: Activar/desactivar shorts
- **short_video_frequency**: Frecuencia de shorts (días)
- **article_enabled**: Activar/desactivar artículos
- **article_frequency**: Frecuencia de artículos (días)
- **start_date**: Fecha de inicio de la programación
- **timezone**: Zona horaria
- **is_active**: Estado de la programación

#### 2. Modelo PublicationSchedule (`app/models/publication_schedule.py`)
Define las publicaciones individuales programadas:
- **channel_id**: Canal al que pertenece
- **content_type**: Tipo de contenido (long_video, short, article)
- **scheduled_datetime**: Fecha/hora programada
- **status**: Estado (planned, published, cancelled, error)
- **script_id**: Guion asociado (opcional)
- **notes**: Notas adicionales

#### 3. Servicio de Programación (`app/services/schedule_service.py`)
Funcionalidades:
- `get_or_create_channel_schedule()`: Obtiene o crea programación de canal
- `update_channel_schedule()`: Actualiza programación de canal
- `generate_publication_dates()`: Genera fechas de publicación basadas en frecuencia
- `create_publication_schedules()`: Crea programaciones para un período
- `get_calendar_events()`: Obtiene eventos del calendario para un mes
- `get_upcoming_publications()`: Obtiene próximas publicaciones

#### 4. Router de Programación (`app/routers/schedule.py`)
Endpoints API:
- `GET /api/schedules/channel/{channel_id}`: Obtener programación de canal
- `POST /api/schedules/channel/{channel_id}`: Crear programación de canal
- `PUT /api/schedules/channel/{channel_id}`: Actualizar programación de canal
- `GET /api/schedules/channel/{channel_id}/calendar`: Calendario mensual
- `GET /api/schedules/channel/{channel_id}/calendar/months`: Calendario 2 meses
- `POST /api/schedules/channel/{channel_id}/generate`: Generar programaciones
- `GET /api/schedules/channel/{channel_id}/upcoming`: Próximas publicaciones
- `POST /api/schedules/publication/{id}/assign-script`: Asociar guión
- `PUT /api/schedules/publication/{id}`: Actualizar publicación
- `DELETE /api/schedules/publication/{id}`: Eliminar publicación

#### 5. UI de Programación (`app/static/`)
- **HTML**: Secciones de programación, calendario y próximas publicaciones
- **JavaScript**: Funciones para cargar, guardar y generar programaciones
- **CSS**: Estilos para tarjetas de configuración, toggle switches y calendarios

---

## 🐛 Correcciones de Errores

### Error: PublicationSchedule no tiene campo 'video_id'
**Problema**: El servicio intentaba acceder a `video_id` en PublicationSchedule, pero ese campo no existía.

**Solución**: 
- Eliminado el campo `video_id` del modelo
- Añadido campo `content_type` para distinguir entre tipos de contenido (long_video, short, article)

### Error: Modelo ChannelSchedule inexistente
**Problema**: No había modelo para definir la programación recurrente de canales.

**Solución**: 
- Creado modelo `ChannelSchedule` con campos para cada tipo de contenido
- Frecuencias configurables en días
- Estado activo/inactivo

### Error: Falta de interfaz de programación
**Problema**: No había forma visual de configurar o ver la programación.

**Solución**: 
- Añadidas secciones de programación en la página de canales
- Calendario visual de 2 meses (actual + siguiente)
- Lista de próximas publicaciones
- Formularios de configuración por tipo de contenido

---

## 🔄 Correcciones Pendientes

### Por hacer:
1. [ ] Validar que las frecuencias sean números positivos
2. [ ] Añadir soporte para zonas horarias configurables
3. [ ] Implementar notificaciones de publicaciones próximas
4. [ ] Añadir exportación de calendario (ICS/CSV)
5. [ ] Implementar reprogramación automática tras errores
6. [ ] Añadir historial de publicaciones pasadas
7. [ ] Mejorar manejo de errores en la UI

---

## 🐛 Corrección: Migración de base de datos para columnas faltantes

### Error: Columna `content_type` no existe en la base de datos existente
**Problema**: Al iniciar el servidor, la tabla `publication_schedules` no tenía la columna `content_type`, causando error `sqlite3.OperationalError: no such column: publication_schedules.content_type`.

**Causa**: El modelo `PublicationSchedule` fue actualizado con el campo `content_type` pero la base de datos existente no fue migrada automáticamente. SQLAlchemy `create_all` no añade columnas a tablas existentes.

**Solución**:
1. Añadida función `init_db()` en `app/core/database.py` con migraciones manuales usando `PRAGMA table_info()` para verificar columnas existentes
2. Actualizado `app/main.py` para incluir migraciones de:
   - Tabla `channel_schedules` (nueva tabla)
   - Tabla `publication_schedules` (nueva tabla con columna `content_type`)
   - Verificación y adición de columnas `content_type` y `is_active` si no existen

**Archivos modificados**:
- `app/core/database.py`: Añadida función `init_db()` con migraciones
- `app/main.py`: Añadidas migraciones de tablas y columnas en `lifespan()`


---

## 🚀 Cómo Ejecutar

### Requisitos
- Python 3.8+
- Dependencias en `requirements.txt`

### Inicio rápido
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
.\run_server.bat
```

O directamente:
```bash
python app/main.py
```

El servidor se inicia en `http://127.0.0.1:9080`

---

## 📝 Notas Técnicas

### Base de Datos
- SQLite con SQLAlchemy ORM
- Migraciones automáticas al iniciar (create_all)
- Tablas principales:
  - `channels`: Canales de YouTube
  - `channel_schedules`: Programación por canal
  - `publication_schedules`: Publicaciones individuales
  - `scripts`: Guiones
  - `daily_stats`: Estadísticas diarias
  - `prompts`: Biblioteca de prompts
  - `content_items`: Contenido en desarrollo
  - `task_logs`: Logs de automatización

### API Endpoints Principales
- `/api/channels`: Gestión de canales
- `/api/schedules/*`: Programación de publicaciones
- `/api/analytics/*`: Análisis y métricas
- `/api/content/*`: Gestión de contenido
- `/api/automation/*`: Automatización
- `/api/prompts/*`: Biblioteca de prompts
- `/api/dashboard/*`: Dashboard
- `/health`: Health check
- `/ui`: Interfaz web

---

## 📅 Historial de Cambios

### 2026-05-06
- ✅ Creado sistema completo de programación de publicaciones
- ✅ Añadido modelo ChannelSchedule
- ✅ Añadido modelo PublicationSchedule (sin campo video_id)
- ✅ Creado servicio schedule_service.py
- ✅ Creado router schedule.py con todos los endpoints
- ✅ Actualizado main.py con nuevo router
- ✅ Actualizada UI con secciones de programación
- ✅ Añadido calendario visual de 2 meses
- ✅ Añadido CSS para la nueva UI
- ✅ Corregido error de campo 'video_id' inexistente

---

## 🔧 Configuración

### Variables de Entorno
- `LLM_URL`: URL del API de LLM
- `LLM_KEY`: API Key del LLM
- `ANALYTICS_SCHEDULE`: Cron para analíticas

### Archivos de Datos
- `app.db`: Base de datos principal
- `channels_data/`: Datos JSON por canal

---

*Última actualización: 2026-05-06*