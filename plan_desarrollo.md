# Wui v2: Plan de Desarrollo

> Archivo centralizado de planificación y tracking de fases.

---

## Fase 1: Stack Tecnológico y Arquitectura Simplificada

### 1.1. Stack Tecnológico Propuesto

| Componente | Tecnología | Razón de Elección |
|-----------|-----------|------------------|
| **Backend** | Python 3.x | Lenguaje versátil, amplio ecosistema. |
| **Framework Web** | FastAPI | Alto rendimiento, tipado estático con Pydantic, generación automática de documentación OpenAPI. Facilita la comprensión de la API para la IA. |
| **Servidor Web** | Uvicorn | Servidor ASGI rápido y compatible con FastAPI. |
| **Validación de Datos** | Pydantic | Define esquemas de datos claros y robustos para la entrada/salida de la API y la estructura de los JSON. Crucial para que la IA entienda los contratos de datos. |
| **Persistencia** | Archivos JSON | Requisito del usuario. Se gestionará de forma estructurada para evitar la complejidad de una base de datos relacional. |
| **Tareas en Segundo Plano** | asyncio / concurrent.futures | Para tareas asíncronas y no bloqueantes, evitando la complejidad de APScheduler y sus problemas de sincronización. |
| **Autenticación** | JWT (JSON Web Tokens) | Más seguro y escalable que Basic Auth. Permite una gestión de sesiones más robusta. |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) | Mantener la simplicidad y evitar frameworks complejos, reduciendo la superficie de error para la IA. |

### 1.2. Principios de Arquitectura Simplificada

1. **Separación de Responsabilidades (SRP):** Cada módulo o servicio tiene una única responsabilidad bien definida (negocio, persistencia, APIs externas).
2. **Modularidad:** Sistema dividido en módulos independientes, desarrollables y probables de forma aislada.
3. **Contratos Explícitos:** Todos los datos fluyen entre módulos y API definidos por esquemas Pydantic claros. Elimina inconsistencias de contratos.
4. **Gestión Centralizada de Datos JSON:** Capa DAL que abstrae lectura/escritura de archivos JSON, asegurando consistencia y evitando duplicación.
5. **Un Único Scheduler:** Si se requiere, una única instancia bien definida y accesible globalmente, evitando duplicación y problemas de sincronización.
6. **Manejo de Errores Robusto:** Mecanismos claros y consistentes en toda la API, con mensajes útiles para depuración y desarrollo por parte de la IA.
7. **Configuración Externa:** Configuración sensible y específica del entorno mediante variables de entorno (`.env`), con archivos de ejemplo (`.env.example`) siguiendo buenas prácticas de seguridad.

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

## Fase 3: Roadmap de Implementación Paso a Paso (Modular)

Este roadmap desglosa el desarrollo de Wui v2 en módulos y pasos incrementales, diseñados para ser abordados por una IA de bajo nivel. Cada paso es autocontenido y tiene objetivos claros, minimizando la necesidad de comprender el sistema completo de una vez. La implementación seguirá un enfoque de abajo hacia arriba y de adentro hacia afuera, comenzando por la infraestructura básica y la persistencia, para luego construir la lógica de negocio y la interfaz de usuario.

### 3.1. Módulos y Dependencias

Se definen los siguientes módulos principales, con sus dependencias:

| Módulo Principal | Dependencias | Descripción |
|---|---|---|
| **Infraestructura Base** | Ninguna | Configuración del entorno, main.py, json_data_manager.py. |
| **Autenticación** | Infraestructura Base | Gestión de usuarios y sesiones. |
| **Canales** | Infraestructura Base | CRUD de canales, integración con YouTube API. |
| **Contenido** | Infraestructura Base, Canales | Gestión del ciclo de vida del contenido (ideas, scripts, videos). |
| **Automatización** | Infraestructura Base, Canales, Contenido | Definición y ejecución de tareas programadas. |
| **Analíticas** | Infraestructura Base, Canales | Recopilación y visualización de métricas. |
| **Prompts** | Infraestructura Base | Gestión de plantillas de prompts para LLMs. |
| **Configuración** | Infraestructura Base | Gestión de la configuración global del sistema. |
| **Frontend (UI)** | Todos los módulos API | Interfaz de usuario para interactuar con el backend. |

### 3.2. Pasos de Implementación Detallados

**Paso 1: Configuración del Proyecto y Servicios Base**
- 1.1. Inicialización del Proyecto: Crear la estructura de carpetas (app/, data/, tools/, etc.).
- 1.2. main.py: Configurar la aplicación FastAPI, CORS, manejo de errores básicos y el lifespan para inicialización/cierre.
- 1.3. app/core/config.py: Definir la configuración de la aplicación usando Pydantic Settings y dotenv para cargar variables de entorno.
- 1.4. app/core/json_data_manager.py: Implementar la capa de acceso a datos para JSON (CRUD genérico y específico para config.json).
- 1.5. app/schemas/base.py: Definir un esquema base para entidades con id, created_at, updated_at.

**Paso 2: Módulo de Autenticación**
- 2.1. app/schemas/auth.py: Definir esquemas para UserLogin y Token.
- 2.2. app/services/auth_service.py: Implementar lógica de autenticación (validación de credenciales, generación/validación de JWT).
- 2.3. app/routers/auth.py: Crear endpoints para /login, /logout, /check.
- 2.4. Middleware de Autenticación: Integrar el middleware de JWT en main.py para proteger rutas.
- 2.5. data/config.json: Almacenar admin_user y admin_pass_hash.

**Paso 3: Módulo de Canales**
- 3.1. app/schemas/channel.py: Definir esquemas ChannelCreate, ChannelUpdate, ChannelResponse.
- 3.2. app/services/channel_service.py: Implementar lógica de negocio para canales (CRUD, interacción con YouTube API para obtener datos iniciales).
- 3.3. app/routers/channels.py: Crear endpoints para CRUD de canales (/api/channels).
- 3.4. Integración con YouTube API: Implementar la lógica para buscar y obtener detalles de canales de YouTube, guardando los datos en data/channels/{id}.json.

**Paso 4: Módulo de Contenido**
- 4.1. app/schemas/content.py: Definir esquemas para ContentItem en sus diferentes etapas.
- 4.2. app/services/content_service.py: Implementar lógica de negocio para el ciclo de vida del contenido (creación, actualización, avance de etapa, generación de guiones con LLM).
- 4.3. app/routers/content.py: Crear endpoints para CRUD de ContentItem y acciones de flujo de trabajo (/api/content).
- 4.4. Integración con LLM: Implementar un servicio app/services/llm_service.py para interactuar con modelos de lenguaje, utilizando la configuración de data/config.json.

**Paso 5: Módulo de Automatización (Scheduler)**
- 5.1. app/schemas/automation.py: Definir esquemas para AutomationTask, AutomationRun, AutomationRunStep.
- 5.2. app/core/scheduler.py: Implementar un único scheduler basado en apscheduler (o similar), que lea las tareas de data/automations/ y las ejecute. Debe ser robusto y manejar la persistencia de jobs.
- 5.3. app/services/automation_service.py: Lógica de negocio para crear, actualizar, eliminar y ejecutar tareas de automatización. Debe interactuar con el scheduler centralizado.
- 5.4. app/routers/automation.py: Endpoints para gestionar tareas de automatización y ver el historial de ejecuciones (/api/automations).

**Paso 6: Módulo de Analíticas**
- 6.1. app/schemas/analytics.py: Definir esquemas para DailyStat.
- 6.2. app/services/analytics_service.py: Lógica para recopilar métricas diarias de canales (usando YouTube API o scripts externos controlados) y almacenarlas en data/daily_stats/{id}.json.
- 6.3. app/routers/analytics.py: Endpoints para acceder a los datos analíticos (/api/analytics).

**Paso 7: Módulo de Prompts**
- 7.1. app/schemas/prompt.py: Definir esquemas para Prompt.
- 7.2. app/services/prompt_service.py: Lógica para gestionar prompts (CRUD, búsqueda, versionado), almacenándolos en data/prompts/{id}.json.
- 7.3. app/routers/prompts.py: Endpoints para gestionar prompts (/api/prompts).

**Paso 8: Módulo de Configuración**
- 8.1. app/schemas/config.py: Definir esquemas para GlobalConfig.
- 8.2. app/services/config_service.py: Lógica para leer y escribir la configuración global en data/config.json.
- 8.3. app/routers/config.py: Endpoints para acceder y modificar la configuración (/api/config).

**Paso 9: Frontend (UI)**
- 9.1. app/static/index.html: Estructura principal de la interfaz.
- 9.2. app/static/styles.css: Estilos globales.
- 9.3. app/static/app.js: Lógica JavaScript para interactuar con las APIs del backend, renderizar datos y gestionar la navegación. Implementar la autenticación JWT en el cliente.
- 9.4. Vistas Específicas: Implementar las vistas para Dashboard, Canales, Contenido, Automatización, Analíticas y Configuración, consumiendo los endpoints de la API.

Este roadmap proporciona una secuencia lógica y modular para el desarrollo, permitiendo que la IA aborde cada componente de forma independiente, con contratos claros y un sistema de persistencia simplificado.

---

## Fase 4: Guías de Implementación

Para que una IA de bajo nivel (4B) pueda desarrollar el código de Wui v2 de manera efectiva, es crucial proporcionarle instrucciones extremadamente claras, atómicas y sin ambigüedades. Cada tarea debe ser un paso discreto con un objetivo verificable, minimizando la necesidad de razonamiento complejo o de mantener un contexto amplio del sistema. La IA debe poder ejecutar cada instrucción y verificar su cumplimiento antes de pasar a la siguiente.

### 4.1. Principios para la Creación de Guías de Implementación

Las siguientes directrices deben aplicarse al redactar las instrucciones para la IA:

- **Atomicidad de Tareas:** Cada instrucción debe corresponder a la creación o modificación de un único archivo, o a la adición de una función específica. Evitar instrucciones que impliquen cambios en múltiples lugares simultáneamente.
- **Especificidad Extrema:** Indicar el nombre exacto del archivo, la ruta completa y el contenido preciso a insertar. Para modificaciones, especificar la línea o el patrón a buscar y el texto de reemplazo.
- **Uso de Schemas Pydantic:** Siempre que se manejen datos, se debe hacer referencia a los esquemas Pydantic definidos en `app/schemas/`. Esto refuerza el contrato de datos y guía a la IA en la estructura esperada.
- **Interacción con json_data_manager:** Todas las operaciones de persistencia (lectura, escritura, actualización, eliminación de JSON) deben realizarse a través de las funciones proporcionadas por `app/core/json_data_manager.py`. La IA no debe manipular directamente los archivos JSON.
- **Verificación Explícita:** Incluir pasos de verificación simples, como ejecutar un linter, un test básico o un curl a un endpoint, para que la IA pueda confirmar el éxito de su tarea.
- **Contexto Mínimo:** Asumir que la IA tiene una memoria limitada del contexto general del proyecto. Cada instrucción debe ser lo más autosuficiente posible.

### 4.2. Ejemplo de Guía de Implementación: Módulo de Infraestructura Base

A continuación, se presenta un ejemplo detallado de cómo se estructurarían las instrucciones para la IA para el primer paso del roadmap, la configuración de la infraestructura base.

**Tarea: Configuración Inicial del Proyecto**

**Objetivo:** Establecer la estructura de directorios básica y los archivos de configuración iniciales para el proyecto Wui v2.

**Paso 1: Crear la Estructura de Directorios Principal**
- **Instrucción:** Crear los siguientes directorios en la raíz del proyecto `wui_v2/`:
  - `app/`
  - `app/api/`
  - `app/core/`
  - `app/services/`
  - `app/schemas/`
  - `app/static/`
  - `data/`
  - `data/channels/`
  - `data/automations/`
  - `data/content_items/`
  - `data/prompts/`
  - `tools/`
- **Verificación:** Ejecutar `ls -R wui_v2/` y confirmar que todos los directorios existen.

**Paso 2: Crear el Archivo `main.py`**
- **Instrucción:** Crear el archivo `wui_v2/main.py` con el siguiente contenido:
```python
# wui_v2/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de inicialización (ej: crear archivos JSON de configuración si no existen)
    print("Aplicación iniciada")
    yield
    # Lógica de limpieza (ej: cerrar recursos)
    print("Aplicación apagada")

app = FastAPI(
    title="Wui v2: Plataforma de Automatización Multimedia",
    description="API para gestionar y automatizar creación de videos e imágenes (JSON-based)",
    version="2.0.0",
    lifespan=lifespan,
)

# Configuración CORS (ajustar en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"], # Permitir solo orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
 )

# Montar archivos estáticos para el frontend
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")
@app.get("/")
async def read_root():
    return RedirectResponse(url="/ui/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": app.version}
```
- **Verificación:** Ejecutar `python -m uvicorn main:app --reload --port 8000` en el directorio `wui_v2/` y verificar que el servidor se inicia sin errores y que `http://localhost:8000/health` devuelve `{"status": "ok", "version": "2.0.0"}`.

**Paso 3: Crear el Archivo `app/core/config.py`**
- **Instrucción:** Crear el archivo `wui_v2/app/core/config.py` con el siguiente contenido:
```python
# wui_v2/app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Wui v2"
    ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASS_HASH: str = os.getenv("ADMIN_PASS_HASH", "$2b$12$EXAMPLEHASHFORADMINPASS") # Reemplazar con un hash real
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key") # Generar una clave segura en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # YouTube API
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")

    # LLM Config
    LLM_ENDPOINT: str = os.getenv("LLM_ENDPOINT", "http://localhost:11434/api/generate" )
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama2")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
```
- **Verificación:** No hay verificación directa en este paso, pero la IA debe asegurarse de que el archivo se haya creado correctamente.

**Paso 4: Crear el Archivo `.env.example`**
- **Instrucción:** Crear el archivo `wui_v2/.env.example` con el siguiente contenido:
```text
# .env.example
ADMIN_USER="admin"
ADMIN_PASS_HASH="$2b$12$EXAMPLEHASHFORADMINPASS" # Usar un hash de bcrypt real para la contraseña de admin
SECRET_KEY="super-secret-key" # Cambiar por una clave aleatoria y segura
YOUTUBE_API_KEY="TU_CLAVE_API_YOUTUBE"
LLM_ENDPOINT="http://localhost:11434/api/generate"
LLM_API_KEY="TU_CLAVE_API_LLM" # Opcional, si tu LLM lo requiere
LLM_MODEL="llama2"
```
- **Verificación:** Confirmar la existencia del archivo.

**Paso 5: Crear el Archivo `app/core/json_data_manager.py`**
- **Instrucción:** Crear el archivo `wui_v2/app/core/json_data_manager.py` con el contenido exacto proporcionado en la Fase 2, sección 2.3.
- **Verificación:** No hay verificación directa en este paso, pero la IA debe asegurarse de que el archivo se haya creado correctamente.

Este nivel de detalle y granularidad permitirá a la IA de bajo nivel avanzar en el desarrollo del proyecto de forma controlada y con alta probabilidad de éxito, minimizando los errores y la necesidad de intervención humana.

---

*Última actualización: 2026-06-11*
