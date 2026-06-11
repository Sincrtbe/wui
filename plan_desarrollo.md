# Wui v2: Plan de Desarrollo

## 📋 Visión General
Wui v2 es una plataforma de automatización multimedia basada en un stack minimalista, sin dependencias pesadas de bases de datos relacionales, y con persistencia 100% en archivos JSON. El objetivo es una arquitectura modular, segura y fácil de mantener, optimizada para ejecución en entornos headless y para ser desarrollada/asistida por IAs de bajo nivel.

---

## Fase 1: Arquitectura Minimalista y Stack Tecnológico

### 1.1. Stack Tecnológico
- **Backend:** Python 3.x + FastAPI + Uvicorn
- **Persistencia:** Archivos JSON (sin SQLite/PostgreSQL)
- **Modelado:** Pydantic (validación y contratos)
- **Frontend:** HTML5 + CSS3 + JavaScript Vanilla
- **Autenticación:** JWT (JSON Web Tokens)
- **Tareas en segundo plano:** `asyncio` y `concurrent.futures`
- **Configuración:** `.env` + `pydantic-settings`

### 1.2. Principios de Diseño
- **Separación de Responsabilidades (SRP):** Capas estrictas (API, Servicios, DAL, Schemas).
- **Modularidad estricta:** Cada módulo tiene una única razón para cambiar.
- **Contratos explícitos:** Uso obligatorio de modelos Pydantic para entrada/salida de datos.
- **DAL Centralizada:** Un único módulo (`app/core/json_data_manager.py`) maneja toda la interacción con el sistema de archivos para evitar corrupción o inconsistencias.
- **Scheduler Único:** Un gestor de tareas global centralizado para automatizaciones.

---

## Fase 2: Diseño del Esquema de Datos JSON y Estructura de Carpetas

La persistencia de datos en archivos JSON requiere una estructura clara y consistente para evitar la complejidad y fragilidad de la versión anterior. Se definirá un esquema para cada entidad principal y una organización lógica de carpetas para almacenar estos archivos.

### 2.1. Estructura de Carpetas para Datos JSON

Todos los archivos JSON que actúan como "base de datos" se almacenarán en una carpeta dedicada `data/` en la raíz del proyecto. Dentro de esta, cada entidad tendrá su propia subcarpeta para mantener la organización. Cada registro individual se guardará como un archivo JSON separado, utilizando su `id` como nombre de archivo para facilitar el acceso directo.

```text
/wui_v2/
├── app/
│   ├── api/          # Endpoints FastAPI
│   ├── core/         # Configuración, utilidades
│   ├── services/     # Lógica de negocio
│   ├── schemas/      # Modelos Pydantic
│   └── static/       # Frontend (HTML, CSS, JS)
├── data/
│   ├── channels/     # Datos de canales (ej: 1.json, 2.json)
│   ├── automations/  # Tareas de automatización (ej: 1.json, 2.json)
│   ├── content_items/# Elementos de contenido (ej: 1.json, 2.json)
│   ├── prompts/      # Prompts de LLM (ej: 1.json, 2.json)
│   └── config.json   # Configuración global (archivo único)
├── tools/            # Scripts externos (si son absolutamente necesarios)
├── .env.example      # Variables de entorno de ejemplo
├── main.py           # Punto de entrada de la aplicación
└── README.md
```

### 2.2. Esquemas de Datos JSON (Ejemplos)

Cada entidad tendrá un esquema JSON bien definido, que se corresponderá con un modelo Pydantic en la capa `app/schemas/`. Esto asegura que la IA tenga un contrato claro para la lectura y escritura de datos.

#### 2.2.1. Channel (Canal de YouTube)
Representa un canal de YouTube gestionado por el sistema. Cada canal se guardará como `data/channels/{id}.json`.
```json
{
  "id": "string",
  "youtube_id": "string",
  "title": "string",
  "description": "string",
  "custom_url": "string",
  "published_at": "datetime",
  "thumbnail_url": "string",
  "color": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "email": "string",
  "social_links": { "twitter": "string", "instagram": "string" },
  "last_scraped_at": "datetime",
  "last_scrape_status": "string",
  "scrape_data": { "view_count": 0, "subscriber_count": 0, "video_count": 0 }
}
```

#### 2.2.2. AutomationTask (Tarea de Automatización)
Define una tarea programada para automatizar procesos. `data/automations/{id}.json`.
```json
{
  "id": "string",
  "channel_id": "string",
  "name": "string",
  "description": "string",
  "schedule_expression": "string",
  "is_active": true,
  "workflow_definition": [ { "step_id": "string", "action": "string", "params": {}, "order": 0 } ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### 2.2.3. ContentItem (Elemento de Contenido)
Representa un elemento de contenido en su ciclo de vida (idea, guion, desarrollado, video). `data/content_items/{id}.json`.
```json
{
  "id": "string",
  "channel_id": "string",
  "title": "string",
  "stage": "string",
  "idea_notes": "string",
  "script_content": "string",
  "article_content": "string",
  "developed_data": {},
  "video_path": "string",
  "video_metadata": {},
  "status": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### 2.2.4. GlobalConfig (Configuración Global)
Archivo único `data/config.json` para la configuración global del sistema.
```json
{
  "youtube_api_key": "string",
  "llm_api_key": "string",
  "llm_endpoint": "string",
  "admin_user": "string",
  "admin_pass_hash": "string",
  "analytics_schedule": "string"
}
```

### 2.3. Capa de Acceso a Datos (DAL) para JSON
Se creará un módulo `app/core/json_data_manager.py` que contendrá funciones genéricas para leer, escribir, actualizar y eliminar registros JSON.

```python
# app/core/json_data_manager.py
import json
import os
from typing import TypeVar, Type, List, Dict, Any

T = TypeVar('T')

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

def _get_entity_path(entity_name: str, item_id: str | None = None) -> str:
    path = os.path.join(DATA_DIR, entity_name)
    os.makedirs(path, exist_ok=True)
    if item_id:
        return os.path.join(path, f"{item_id}.json")
    return path

def read_json_file(entity_name: str, item_id: str) -> Dict[str, Any] | None:
    file_path = _get_entity_path(entity_name, item_id)
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(entity_name: str, item_id: str, data: Dict[str, Any]):
    file_path = _get_entity_path(entity_name, item_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_json_files(entity_name: str) -> List[Dict[str, Any]]:
    path = _get_entity_path(entity_name)
    items = []
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            item_id = os.path.splitext(filename)[0]
            item_data = read_json_file(entity_name, item_id)
            if item_data:
                items.append(item_data)
    return items

def delete_json_file(entity_name: str, item_id: str) -> bool:
    file_path = _get_entity_path(entity_name, item_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def read_global_config() -> Dict[str, Any]:
    config_path = os.path.join(DATA_DIR, "config.json")
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_global_config(config_data: Dict[str, Any]):
    config_path = os.path.join(DATA_DIR, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
```

---

## Fase 3: Interfaz de Usuario y Gestión de Estado
*(Nota: Fase 3 añadida para completitud del plan)*
- Diseño de layouts HTML5/CSS3 responsivos y ligeros.
- Gestión de estado del cliente con JS Vanilla y `fetch` API para llamadas a FastAPI.
- Implementación de middleware de autenticación JWT en el frontend para proteger rutas.
- Sistema de notificaciones y feedback visual para acciones asíncronas (scraping, generación de contenido).

---

## Fase 4: Guías de Implementación para IAs de Bajo Nivel

Para que una IA de bajo nivel (4B) pueda desarrollar el código de Wui v2 de manera efectiva, es crucial proporcionarle instrucciones extremadamente claras, atómicas y sin ambigüedades. Cada tarea debe ser un paso discreto con un objetivo verificable, minimizando la necesidad de razonamiento complejo o de mantener un contexto amplio del sistema.

### 4.1. Principios para la Creación de Guías de Implementación
- **Atomicidad de Tareas:** Cada instrucción corresponde a la creación/modificación de un único archivo o función.
- **Especificidad Extrema:** Nombre exacto del archivo, ruta completa y contenido preciso.
- **Uso de Schemas Pydantic:** Referencia obligatoria a `app/schemas/` para validación de datos.
- **Interacción con json_data_manager:** Prohibido manipular archivos JSON directamente. Usar siempre la DAL.
- **Verificación Explícita:** Pasos de validación (linters, tests unitarios, `curl` a endpoints).
- **Contexto Mínimo:** Instrucciones autosuficientes para IAs con memoria de contexto limitada.

### 4.2. Ejemplo de Guía: Módulo de Infraestructura Base

**Tarea:** Configuración Inicial del Proyecto
**Objetivo:** Establecer la estructura de directorios básica y los archivos de configuración iniciales.

**Paso 1:** Crear la Estructura de Directorios Principal
- **Instrucción:** Crear `app/`, `app/api/`, `app/core/`, `app/services/`, `app/schemas/`, `app/static/`, `data/`, `data/channels/`, `data/automations/`, `data/content_items/`, `data/prompts/`, `tools/`.
- **Verificación:** `ls -R` confirma existencia de carpetas.

**Paso 2:** Crear el Archivo `main.py`
- **Instrucción:** Crear `wui_v2/main.py` con configuración de FastAPI, CORS, montaje de `StaticFiles` en `/ui`, y endpoints `/` y `/health`.
- **Verificación:** `uvicorn main:app --reload --port 8000` inicia correctamente y `/health` devuelve `{"status": "ok", "version": "2.0.0"}`.

**Paso 3:** Crear el Archivo `app/core/config.py`
- **Instrucción:** Crear `app/core/config.py` usando `pydantic-settings` para cargar variables de entorno (`ADMIN_USER`, `SECRET_KEY`, `YOUTUBE_API_KEY`, `LLM_ENDPOINT`, etc.).
- **Verificación:** Importación limpia sin errores.

**Paso 4:** Crear el Archivo `.env.example`
- **Instrucción:** Definir las variables de entorno requeridas con valores placeholder.
- **Verificación:** Existencia y formato correcto del archivo.

**Paso 5:** Crear el Archivo `app/core/json_data_manager.py`
- **Instrucción:** Insertar el código de la DAL proporcionado en la Fase 2, Sección 2.3.
- **Verificación:** Importación y llamadas a funciones sin errores de rutas.

---

*Fin del plan de desarrollo inicial. Siguiente paso: Ejecución de la Fase 1 (Skeleton de la aplicación).*
