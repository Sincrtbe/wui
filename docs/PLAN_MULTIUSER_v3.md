# WUI v3 — Plan de Desarrollo Multi-Usuario

> **Fecha:** 22/Jun/2026
> **Proyecto:** WUI — Plataforma SaaS de Automatización Multimedia para YouTube
> **Objetivo:** Transformar WUI en un producto comercial multi-usuario con gestión de canales, prompts parametrizables, scoring de contenido y notas colaborativas.

---

## 1. Nueva Arquitectura de Datos

### 1.1 Entidades Principales

```
User (Usuario)
├── id: UUID
├── email: string (único)
├── password_hash: string
├── name: string
├── plan: "free" | "pro" | "enterprise"
├── created_at / updated_at / deleted_at
└── settings: JSON (preferencias globales)

Channel (Canal — 1 a N por usuario)
├── id: UUID
├── user_id: UUID (FK → User)
├── name: string
├── platform: "youtube" | "tiktok" | "instagram" | "none"
├── platform_id: string | null (ej: UCxxxxx, @handle)
├── platform_token: string (encrypted, para API de la red social)
├── status: "active" | "paused" | "syncing"
├── voice_sample_path: string | null (ruta al archivo de voz del TTS)
├── created_at / updated_at
└── settings: JSON (configuraciones específicas del canal)

Prompt (Plantilla — por usuario, reusable)
├── id: UUID
├── user_id: UUID (FK → User)
├── name: string
├── description: string
├── category: "storming" | "development" | "scene_graphic" | "scene_video" | "tts" | "custom"
├── content: string (template con {{{variables}}})
├── variables_schema: JSON (definición de variables esperadas)
├── assigned_pipeline_stage: string | null (etapa del pipeline donde se usa)
├── is_default: bool (si es prompt del sistema)
├── created_at / updated_at
└── tags: list[string] (búsqueda y categorización)

ContentItem (Idea/Guion/Proyecto — 1 a N por canal)
├── id: UUID
├── user_id: UUID (FK → User)
├── channel_id: UUID (FK → Channel)
├── parent_id: UUID | null (para versionado en árbol)
├── title: string
├── stage: "idea" | "script" | "graphic" | "video" | "published"
├── status: "draft" | "in_progress" | "completed" | "archived"
├── current_version_id: UUID (puntero a la versión activa)
├── tags: list[string]
├── created_at / updated_at
└── metadata: JSON (datos adicionales)

ContentVersion (Versión — cualquier cambio genera una nueva versión)
├── id: UUID
├── content_item_id: UUID (FK → ContentItem)
├── version_number: int (secuencial por content_item)
├── stage_snapshot: string (copia del stage en que estaba)
├── data: JSON (contenido completo de esa versión)
│   ├── idea_notes: string
│   ├── script_content: string
│   ├── scene_prompts: list[{scene_id, prompt, model}]
│   ├── generated_images: list[{scene_id, url, flux_prompt}]
│   ├── generated_videos: list[{scene_id, url, wan_prompt}]
│   └── tts_result: {audio_path, duration, script_used}
├── prompt_version_id: UUID | null (qué prompt se usó para generarla)
├── created_at
└── created_by: "user" | "ai"

Score (Puntuación — 1 a N por ContentVersion)
├── id: UUID
├── content_version_id: UUID (FK → ContentVersion)
├── source: "manual" | "youtube_api" | "ai_predicted"
├── metric_type: "views" | "ctr" | "retention" | "likes_ratio" | "ai_score"
├── value: float
├── recorded_at: datetime
└── notes: JSON (datos adicionales del metric)

Note (Nota — 1 a N por ContentVersion, del usuario)
├── id: UUID
├── content_version_id: UUID (FK → ContentVersion)
├── user_id: UUID (FK → User)
├── type: "strength" | "weakness" | "improvement" | "general"
├── content: string
├── created_at / updated_at
└── resolved: bool

PipelineAssignment (Asignación de prompt → etapa)
├── id: UUID
├── user_id: UUID (FK → User)
├── channel_id: UUID | null (FK → Channel, null = global del usuario)
├── pipeline_stage: "idea_generation" | "script_writing" | "scene_graphic" | "scene_video" | "tts"
├── prompt_id: UUID (FK → Prompt)
├── is_active: bool
└── priority: int (orden de ejecución si hay múltiples)
```

### 1.2 Estructura de Carpetas (Física)

```
/opt/data/wui/
├── data/
│   ├── users/                          # Carpeta raíz de usuarios
│   │   └── {user_uuid}/
│   │       ├── profile.json             # Datos del usuario
│   │       ├── settings.json           # Preferencias
│   │       ├── prompts/                # Plantillas de prompts del usuario
│   │       │   └── {prompt_uuid}.json
│   │       └── channels/               # Canales del usuario
│   │           └── {channel_uuid}/
│   │               ├── channel.json    # Metadata del canal
│   │               ├── voice_sample/   # Muestra de voz para TTS
│   │               │   └── sample.mp3
│   │               └── content/        # Ideas/guiones de este canal
│   │                   └── {content_uuid}/
│   │                       ├── content.json  # Metadata del content item
│   │                       ├── versions/     # Versiones
│   │                       │   └── {version_uuid}.json
│   │                       └── assets/       # Archivos generados
│   │                           ├── images/
│   │                           ├── videos/
│   │                           └── audio/
│   └── system/                     # Datos del sistema (prompts default)
│       └── default_prompts/
│           └── {prompt_uuid}.json
```

### 1.3 Sistema de Etiquetas {{{x}}}

Los prompts usan un sistema de variables estilo Mustache/Twig:

```
{{{tema}}}              → Tema principal del video
{{{titulo}}}            → Título generado o proporcionado
{{{concepto}}}          → Concepto del video
{{{nombre_canal}}}      → Nombre del canal
{{{descripcion_canal}}}  → Descripción del canal
{{{audiencia}}}         → Descripción de la audiencia objetivo
{{{tono}}}              → Tono del video (educativo, entretenido, etc.)
{{{duracion_objetivo}}} → Duración objetivo en segundos
{{{escena_num}}}        → Número de escena actual
{{{total_escenas}}}     → Total de escenas planned
{{{nombre_personaje}}}  → Nombre del personaje (si se usa)
{{{personalidad_personaje}}} → Personalidad del personaje
{{{fecha_actual}}}      → Fecha actual ISO
```

**Variables especiales de scoring (disponibles después de publicar):**
```
{{{score_vistas}}}         → Vistas totales
{{{score_ctr}}}            → CTR (Click-Through Rate)
{{{score_retention}}}      → Retención media
{{{score_likes_ratio}}}    → Ratio de likes
{{{score_ai}}}             → Puntuación predicha por IA
```

### 1.4 Pipeline de Etapas

```
idea_generation  →  script_writing  →  scene_graphic  →  scene_video  →  tts
     ↓                  ↓                  ↓                ↓            ↓
  Prompt de           Prompt de         Prompt de        Prompt de    Prompt de
  Lluvia de Ideas     Desarrollo        Escena Gráfica   Escena Video TTS
```

Cada etapa tiene:
1. **Prompt asignado** (del usuario o default del sistema)
2. **Variables disponibles** (las {{{x}}} que se resuelven con datos del canal/contenido)
3. **Output esperado** (estructura JSON o texto libre)
4. **Modelo sugerido** (qwen para texto, flux para imagen, wan para video)

---

## 2. Plan de Desarrollo Detallado (Fases)

### Fase 0: Reestructuración del Proyecto
**Objetivo:** Preparar la base de datos, esquemas y DAL para multi-usuario.

**Tareas:**
- [ ] Crear directorio `data/users/` y `data/system/`
- [ ] Rediseñar `json_data_manager.py` para soportar la nueva estructura de carpetas
- [ ] Crear módulo `app/schemas/v3/` con todos los schemas Pydantic nuevos
- [ ] Crear servicio `app/services/user_service.py` (CRUD de usuarios)
- [ ] Crear servicio `app/services/pipeline_service.py` (gestión de asignaciones)
- [ ] Crear migrador `tools/migrate_to_v3.py` que mueva los datos existentes a la nueva estructura
- [ ] Actualizar `main.py` para registrar los nuevos routers
- [ ] Actualizar `.gitignore` para excluir `data/users/*` pero incluir `data/users/.gitkeep`
- [ ] Commit: "feat: v3 multi-user architecture base"

### Fase 1: Sistema de Usuarios y Autenticación
**Objetivo:** Sistema de auth completo con registros, login, gestión de sesiones.

**Tareas:**
- [ ] Endpoint `POST /api/auth/register` (crear usuario)
- [ ] Endpoint `POST /api/auth/login` → JWT
- [ ] Endpoint `POST /api/auth/logout`
- [ ] Endpoint `GET /api/auth/me`
- [ ] Endpoint `PUT /api/auth/me` (actualizar perfil)
- [ ] Middleware de autenticación actualizado para verificar `user_id` en cada request
- [ ] Sistema de planes básico: free (3 canales máx), pro (10), enterprise (∞)
- [ ] Probar: registro → login → acceso a recursos propios
- [ ] Commit: "feat: user authentication system"

### Fase 2: Sistema de Canales
**Objetivo:** CRUD de canales vinculados a usuarios, con soporte para conexión a YouTube.

**Tareas:**
- [ ] Endpoint `GET/POST /api/channels` (listar/crear para el usuario)
- [ ] Endpoint `GET/PUT/DELETE /api/channels/{channel_id}`
- [ ] Endpoint `POST /api/channels/{channel_id}/sync` (sincronizar con YouTube API)
- [ ] Endpoint `POST /api/channels/{channel_id}/connect` (conectar canal a red social)
- [ ] Gestión de `voice_sample` (subir archivo de audio para TTS)
- [ ] Permisos: un usuario solo ve/administra sus propios canales
- [ ] Probar: crear canal → sincronizar → verificar datos en JSON
- [ ] Commit: "feat: channel management system"

### Fase 3: Sistema de Prompts Parametrizables
**Objetivo:** Crear, editar, asignar y usar prompts con {{{variables}}}.

**Tareas:**
- [ ] Endpoint `GET/POST /api/prompts` (listar/crear para el usuario)
- [ ] Endpoint `GET/PUT/DELETE /api/prompts/{prompt_id}`
- [ ] Endpoint `POST /api/prompts/validate` (validar que las {{{variables}}} sean correctas)
- [ ] Endpoint `GET /api/prompts/templates` (prompts default del sistema)
- [ ] Sistema de renderizado: resolver {{{variables}}} con datos del canal/contenido
- [ ] Endpoint `POST /api/prompts/render` (renderizar un prompt con variables)
- [ ] Probar: crear prompt con {{{tema}}} → renderizar con {tema: "IA"} → verificar salida
- [ ] Migrar los prompts markdown actuales (`static/js/prompts/visual/`) a JSON en `data/system/default_prompts/`
- [ ] Commit: "feat: parameterized prompt system with {{{variables}}}"

### Fase 4: Pipeline de Asignaciones
**Objetivo:** Asignar qué prompt se usa en cada etapa del pipeline por canal/usuario.

**Tareas:**
- [ ] Endpoint `GET/POST /api/pipeline/assignments`
- [ ] Endpoint `PUT/DELETE /api/pipeline/assignments/{assignment_id}`
- [ ] Endpoint `GET /api/pipeline/stages` (listar etapas disponibles)
- [ ] Lógica: si un canal no tiene asignación para una etapa, usar la global del usuario
- [ ] Si el usuario no tiene, usar el prompt default del sistema para esa etapa
- [ ] Probar: asignar prompt "custom_storming" a "idea_generation" para un canal específico
- [ ] Commit: "feat: pipeline assignment system"

### Fase 5: Content Items y Versionado
**Objetivo:** Sistema de ideas/guiones con versionado completo.

**Tareas:**
- [ ] Endpoint `GET/POST /api/channels/{channel_id}/content` (listar/crear content items)
- [ ] Endpoint `GET/PUT/DELETE /api/content/{content_id}`
- [ ] Endpoint `POST /api/content/{content_id}/advance` (avanzar etapa: idea → script → graphic → video → published)
- [ ] Endpoint `POST /api/content/{content_id}/versions` (crear nueva versión)
- [ ] Endpoint `GET /api/content/{content_id}/versions` (listar versiones)
- [ ] Endpoint `GET /api/content/{content_id}/versions/{version_id}` (obtener versión específica)
- [ ] Endpoint `POST /api/content/{content_id}/revert/{version_id}` (revertir a versión anterior)
- [ ] Cada versión guarda snapshot completo de `data` (idea_notes, script, scenes, etc.)
- [ ] Probar: crear idea → avanzar a script → crear nueva versión → revertir a idea
- [ ] Commit: "feat: content items with full versioning"

### Fase 6: Scoring y Notas
**Objetivo:** Sistema de puntuación multi-fuente y notas del usuario.

**Tareas:**
- [ ] Endpoint `POST /api/content/{content_id}/versions/{version_id}/scores` (registrar score)
- [ ] Endpoint `GET /api/content/{content_id}/versions/{version_id}/scores`
- [ ] Endpoint `POST /api/content/{content_id}/versions/{version_id}/notes` (crear nota)
- [ ] Endpoint `GET/PUT/DELETE /api/notes/{note_id}`
- [ ] Endpoint `GET /api/content/{content_id}/scores-history` (historial de scores de todas las versiones)
- [ ] Endpoint `GET /api/content/{content_id}/analytics` (agregados: promedio de score, mejor versión, etc.)
- [ ] Integración con YouTube API para traer `views`, `ctr`, `retention` automáticamente (si channel conectado)
- [ ] Probar: crear nota "strength" → crear score "views: 15000" → consultar analytics
- [ ] Commit: "feat: scoring and notes system"

### Fase 7: Migración a Vue 3
**Objetivo:** Reemplazar el frontend vanilla JS por Vue 3 con components.

**Estructura del frontend Vue:**
```
app/frontend/
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/
│   │   └── index.js
│   ├── stores/           # Pinia stores
│   │   ├── auth.js
│   │   ├── channels.js
│   │   ├── content.js
│   │   └── prompts.js
│   ├── components/
│   │   ├── common/      # Botones, inputs, cards
│   │   ├── layout/      # Header, Sidebar, Nav
│   │   ├── channels/
│   │   ├── content/
│   │   ├── prompts/
│   │   └── scoring/
│   ├── views/
│   │   ├── Login.vue
│   │   ├── Dashboard.vue
│   │   ├── Channels.vue
│   │   ├── ChannelDetail.vue
│   │   ├── ContentItem.vue
│   │   ├── PromptEditor.vue
│   │   └── PipelineConfig.vue
│   └── api/
│       └── index.js     # Axios instance con interceptors de auth
├── index.html
└── vite.config.js
```

**Tareas:**
- [ ] Inicializar proyecto Vue 3 con Vite
- [ ] Configurar router con guards de autenticación
- [ ] Implementar stores de Pinia
- [ ] Migrar componentes uno por uno:
  - [ ] Login/Auth
  - [ ] Dashboard
  - [ ] ChannelList → ChannelDetail
  - [ ] ContentItemEditor (con version history)
  - [ ] PromptEditor (con preview de {{{variables}}})
  - [ ] ScoringDashboard
- [ ] Mantener backwards compatibility con las APIs existentes
- [ ] Probar flujo completo: login → crear canal → crear idea → avanzar etapa → poner nota → ver score
- [ ] Commit: "feat: Vue 3 frontend migration"

### Fase 8: Testing e Integración
**Objetivo:** Suite de tests completa y deployment.

**Tareas:**
- [ ] Tests unitarios para servicios (`tests/unit/services/`)
- [ ] Tests de integración para APIs (`tests/integration/`)
- [ ] Tests del renderizado de prompts (`tests/unit/test_prompt_renderer.py`)
- [ ] Tests del sistema de versionado
- [ ] Documentación de APIs con OpenAPI (FastAPI ya lo genera)
- [ ] Probar en entorno local con datos de test
- [ ] Commit: "chore: test suite and integration"

---

## 3. Orden de Implementación

```
Semana 1:
  ├── Fase 0: Reestructuración + DAL
  └── Fase 1: Autenticación

Semana 2:
  ├── Fase 2: Canales
  └── Fase 3: Prompts parametrizables

Semana 3:
  ├── Fase 4: Pipeline de asignaciones
  └── Fase 5: Content items + versionado

Semana 4:
  └── Fase 6: Scoring + Notas

Semana 5-6:
  └── Fase 7: Vue 3 Migration

Semana 7:
  └── Fase 8: Testing + Documentación
```

---

## 4. Decisiones de Diseño Pendientes de Confirmación

| # | Pregunta | Opciones |
|---|----------|----------|
| D1 | ¿Los usuarios se registran solos o tú creas las cuentas? | A) Self-register / B) Solo tú creas / C) Self-register + approval |
| D2 | ¿El plan free tiene límite de prompts también? | A) Sí, 10 prompts / B) Unlimited prompts / C) Solo prompts default |
| D3 | ¿Los canales pueden compartir prompts entre sí (dentro del mismo usuario)? | A) Sí, por diseño / B) No, cada canal tiene sus propios |
| D4 | ¿Las notas de scoring se comparten entre versiones (heredan) o son independientes? | A) Independientes por versión / B) Las notas son del ContentItem, scores de la Version |
| D5 | ¿El frontend Vue se sirve desde el mismo FastAPI o es estático separado? | A) Mismo FastAPI (`/ui`) / B) Build estático en CDN/backend |

---

## 5. Resumen de Archivos a Crear/Modificar

### Nuevos archivos:
```
app/schemas/v3/
  ├── user.py
  ├── channel.py
  ├── prompt.py
  ├── content.py
  ├── content_version.py
  ├── score.py
  ├── note.py
  └── pipeline.py

app/services/
  ├── user_service.py
  ├── channel_service.py
  ├── prompt_service.py
  ├── content_service.py
  ├── version_service.py
  ├── score_service.py
  ├── note_service.py
  ├── pipeline_service.py
  └── prompt_renderer.py

app/api/v3/
  ├── auth.py
  ├── channels.py
  ├── prompts.py
  ├── content.py
  ├── scores.py
  ├── notes.py
  └── pipeline.py

tools/
  └── migrate_to_v3.py

tests/
  ├── unit/
  │   ├── test_prompt_renderer.py
  │   ├── test_versioning.py
  │   └── services/
  └── integration/

app/frontend/          # Nuevo proyecto Vue 3
```

### Archivos a modificar:
```
app/core/json_data_manager.py  # Refactorizar para multi-usuario
main.py                       # Registrar nuevos routers
app/api/auth.py              # Actualizar con nuevo schema
app/api/channels.py           # Refactorizar
app/api/creative.py          # Migrar a v3 o reemplazar
app/core/config.py            # Nuevas variables de entorno
.env.example                  # Nuevas vars
```

---

*Última actualización: 2026-06-22*
