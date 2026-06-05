# Bugs y estado de la reparación

## Fallos actuales conocidos
- `app/static/app.js` no se puede validar con `py_compile` porque es JavaScript, pero el resto de los archivos Python compilados sin error.
- El servidor debe reiniciarse para que los cambios de código carguen correctamente en el proceso de Uvicorn.
- El endpoint de dashboard puede necesitar más mejoras visuales en la UI, pero la lógica de datos está implementada.
- La tarea de scraping diario está implementada de forma simulada y puede necesitar una integración real de scraping externo.
- No se ha añadido todavía un sistema real de autenticación/autorización para el dashboard.

## Fallos reparados
- `GET /api/scripts` devolvía error 500 por serializar objetos `Tag` en vez de strings en el campo `tags`.
- Se extendió el modelo `Channel` y los esquemas para incluir `email`, `social_links`, `checkpoints`, `last_scraped_at`, `last_scrape_status` y `scrape_data`.
- Se actualizó el dashboard para filtrar por canal y mostrar información de cada canal.
- Se añadió un calendario de publicaciones con el día actual marcado y color por canal.
- Se arregló la semilla inicial para crear canales con los nuevos campos usando `ChannelCreate`.
- Se agregó una migración ligera en `app/main.py` para extender la tabla `channels` cuando ya existe la base de datos.
