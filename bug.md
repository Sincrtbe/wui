# Historial de Bugs y Correcciones

## Bugs Reparados ✅

| # | Fecha | Problema | Solución | Estado |
|---|-------|----------|----------|--------|
| 1 | 2026-09-06 | API Key hardcodeada en scripts | Sistema con `.env`, config en `config.py`, endpoints seguros, UI con key enmascarada | ✅ Reparado |
| 2 | 2026-09-06 | Calendario descuadrado (headers dentro del grid) | Headers fuera del grid, eliminar `aspect-ratio: 1` | ✅ Reparado |
| 3 | 2026-09-06 | Calendario no mostraba eventos | Parsing directo de cadena ISO en lugar de `new Date()` | ✅ Reparado |
| 4 | 2026-09-06 | `GET /api/scripts` error 500 por Tag objects | `field_serializer` en `ScriptResponse` | ✅ Reparado |
| 5 | 2026-09-06 | Router `/api/scripts` faltante | Creado `app/routers/scripts.py` con CRUD completo | ✅ Reparado |
| 6 | 2026-09-06 | Scheduler desincronizado | Sincronización en `create()`, `update()` y `delete()` | ✅ Reparado |
| 7 | 2026-09-06 | Sin validación de expresiones cron | Validación de 5 campos y manejo de errores | ✅ Reparado |

## Bugs Conocidos ⚠️

| # | Descripción | Trabajo a realizar | Estado |
|---|-------------|-------------------|--------|
| 1 | Reinicio necesario del servidor para cambios de código | Comportamiento esperado de Uvicorn | ⚠️ Pendiente |

---

> **Nota:** Para más detalles sobre correcciones, ver `inprogress.md` → sección "Correcciones y Bugs Reparados".