# Hoja de Ruta del Proyecto (Roadmap) - WUI v2

Este documento describe las metas alcanzadas y los próximos pasos planificados para la evolución de la plataforma **WUI v2**.

## ✅ Hitos Completados
- [x] **Rediseño Estético Profesional:** Interfaz moderna, comercial y profesional.
- [x] **Sistema de Identificación:** Botón "Identifícate" con dropdown funcional.
- [x] **Módulo de Configuración:** Gestión de APIs y endpoints persistentes en JSON.
- [x] **Gestión de Prompts Personalizados:** Creación y asignación de prompts por pestaña.
- [x] **Creación de Personajes:** Sistema completo para definir personajes y usarlos como contexto en la generación de contenido.
- [x] **Integración Funcional de Contexto:** Inyección automática de personajes y prompts en el motor de generación.

## 🚀 Próximos Pasos (Pendientes)

### Fase 1: Conectividad y Ejecución
- [ ] **Integración Real con LLM:** Implementar la llamada real a los endpoints configurados (Ollama, OpenAI, Qwen) para procesar los prompts.
- [ ] **Generación de Imágenes (Flux 2.0):** Conectar con la API de Flux para mostrar las imágenes generadas directamente en la UI.
- [ ] **Generación de Video (Wan 2.2):** Implementar el flujo de envío de prompts a Wan 2.2 y previsualización de clips.

### Fase 2: Gestión de Contenido y Archivo
- [ ] **Historial de Generaciones:** Crear una base de datos (o archivos JSON) para guardar cada prompt generado y su resultado.
- [ ] **Sistema de Favoritos:** Permitir marcar guiones o ideas generadas como favoritas para acceso rápido.
- [ ] **Exportación Avanzada:** Botones para exportar guiones a PDF, TXT o directamente a descripciones de YouTube.

### Fase 3: Automatización y Canales
- [ ] **Sincronización con YouTube:** Usar la YouTube API Key para obtener datos de canales reales y sugerir temas basados en tendencias del canal.
- [ ] **Programador de Tareas:** Interfaz para programar la generación automática de ideas o guiones en fechas específicas.

### Fase 4: Colaboración y Multi-usuario
- [ ] **Perfiles de Usuario:** Soporte para múltiples cuentas con sus propios personajes y configuraciones aisladas.
- [ ] **Compartir Recursos:** Opción para exportar/importar packs de personajes y prompts entre usuarios.

---
*Este roadmap es dinámico y se actualizará conforme avance el desarrollo.*
