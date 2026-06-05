# Bugs y estado de la reparación

## Fallos actuales conocidos
- El servidor debe reiniciarse para que los cambios de código carguen correctamente en el proceso de Uvicorn (comportamiento esperado de desarrollo).

## Fallos reparados
- `GET /api/scripts` devolvía error 500 por serializar objetos `Tag` en vez de strings en el campo `tags`. **REPARADO**: Añadido `field_serializer` en `ScriptResponse`.
- Se extendió el modelo `Channel` y los esquemas para incluir `email`, `social_links`, `checkpoints`, `last_scraped_at`, `last_scrape_status` y `scrape_data`.
- Se actualizó el dashboard para filtrar por canal y mostrar información de cada canal.
- Se añadió un calendario de publicaciones con el día actual marcado y color por canal.
- Se arregló la semilla inicial para crear canales con los nuevos campos usando `ChannelCreate`.
- Se agregó una migración ligera en `app/main.py` para extender la tabla `channels` cuando ya existe la base de datos.
- **Router `/api/scripts` faltante**: REPARADO - Creado `app/routers/scripts.py` con CRUD completo para guiones, registrado en `app/main.py`.
- **Falta de sincronización del scheduler**: REPARADO - Creado `app/services/automation_service_sync.py` con funciones de sincronización. Actualizado `AutomationService` para sincronizar tareas con APScheduler en `create()`, `update()` y `delete()`.
- **Dependencias faltantes**: REPARADO - Añadidas `pystray==0.19.5` y `Pillow==10.1.0` a `requirements.txt`.
- **Parser de cron sin validación**: REPARADO - Mejorado `_parse_cron()` en `app/tasks/scheduler.py` con validación de 5 campos y manejo de errores.

## Historial de cambios
| Fecha | Cambio | Estado |
|-------|--------|--------|
| 2026-05-06 | Creación del repositorio con documentación inprogress.md | Hecho |
| 2026-05-06 | Fix de serialización de tags en `/api/scripts` | Reparado |
| 2026-05-06 | Extensión del modelo Channel con campos adicionales | Reparado |
| 2026-05-06 | Dashboard con filtros por canal y calendario | Reparado |
| 2026-05-06 | Migración ligera para columnas nuevas en canales | Reparado |
| 2026-06-05 | Creación del router `/api/scripts` faltante | Reparado |
| 2026-06-05 | Sincronización de scheduler con cambios en tareas | Reparado |
| 2026-06-05 | Adición de dependencias faltantes (pystray, Pillow) | Reparado |
| 2026-06-05 | Validación mejorada de expresiones cron | Reparado |
