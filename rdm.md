# WUI v2 - Creative Studio

[![FastAPI](https://img.shields.io/badge/FastAPI-latest-blue)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-lightgray)](LICENSE)

## 📋 Descripción

**WUI v2** es una plataforma moderna y profesional de automatización creativa para YouTube. Diseñada para creadores de contenido, permite generar ideas, guiones, prompts para imágenes (Flux 2.0) y videos (Wan 2.2) — todo integrado en un único flujo de trabajo intuitivo.

## ✨ Funcionalidades Principales

### 🎬 Generación Creativa
- **💡 Lluvia de Ideas** - Genera conceptos creativos innovadores basados en temas específicos
- **📊 Clasificación Inteligente** - Evalúa y ordena ideas por potencial viral y esfuerzo de producción
- **📝 Desarrollo de Guion** - Convierte ideas en guiones estructurados por duración
- **🎨 Escenas Gráficas** - Genera prompts optimizados para Flux 2.0 (imágenes IA)
- **🎬 Escenas de Video** - Crea prompts para Wan 2.2 (video IA) a partir de imágenes base
- **🔄 Texto a Visual** - Traduce narración en prompts visuales listos para generar

### 👥 Gestión de Personajes
- Crear y definir personajes con personalidad, apariencia y trasfondo
- Asociar prompts a personajes para reutilización consistente
- Gestión completa con interfaz intuitiva

### ⚙️ Configuración Avanzada
- **Gestión de APIs** - Configura claves y endpoints para YouTube, LLM, Flux, Wan y Qwen
- **Prompts Personalizados** - Crea, edita y asigna prompts a pestañas específicas
- **Persistencia en JSON** - Todos los datos se guardan en archivos JSON organizados por entidad
- **Interfaz Moderna** - Diseño limpio y profesional con UX mejorada

## 🚀 Instalación y Uso

### Requisitos
- Python 3.11+
- FastAPI 0.104.1+
- Uvicorn 0.24.0+

### Instalación
```bash
git clone https://github.com/Sincrtbe/wui.git
cd wui
pip install -r requirements.txt
```

### Inicio del Servidor
```bash
uvicorn main:app --reload --port 9080
```

### Acceso
- **UI Web:** http://127.0.0.1:9080/ui
- **API Base:** http://127.0.0.1:9080
- **Health Check:** http://127.0.0.1:9080/health
- **Documentación API:** http://127.0.0.1:9080/docs

## 📖 Flujo de Trabajo

1. **Autenticación** - Inicia sesión con el botón "Identifícate" en la esquina superior izquierda
2. **Configuración** - Accede a la pestaña ⚙️ para configurar tus APIs y crear prompts personalizados
3. **Creación de Personajes** - Define personajes en la pestaña 👥 para usarlos en tus videos
4. **Generación Creativa** - Usa cualquiera de las 6 pestañas de generación para crear contenido
5. **Exportación** - Copia los prompts generados y úsalos en tus herramientas de IA favoritas

## 🏗️ Arquitectura

### Backend
- **FastAPI** - Framework web moderno y rápido
- **JWT** - Autenticación segura con tokens
- **JSON** - Persistencia de datos en archivos estructurados

### Frontend
- **HTML5 + CSS3** - Interfaz moderna y responsive
- **JavaScript Vanilla** - Sin dependencias externas
- **Diseño Comercial** - Colores profesionales, tipografía clara, UX intuitiva

### Estructura de Datos
```
data/
├── config.json              # Configuración global (APIs, credenciales)
├── custom_prompts/          # Prompts personalizados (JSON por prompt)
├── characters/              # Personajes (JSON por personaje)
├── channels/                # Canales (JSON por canal)
├── content_items/           # Items de contenido
├── automations/             # Automatizaciones
└── prompts/                 # Plantillas de prompts base
```

## 📚 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario

### Generación Creativa
- `GET /api/creative/templates` - Listar plantillas disponibles
- `POST /api/creative/generate` - Generar prompt rellenando plantilla

### Configuración
- `GET /api/config/api-config` - Obtener configuración de APIs
- `POST /api/config/api-config` - Actualizar configuración de APIs
- `POST /api/config/prompts` - Crear prompt personalizado
- `GET /api/config/prompts` - Listar prompts personalizados
- `PUT /api/config/prompts/{id}` - Actualizar prompt
- `DELETE /api/config/prompts/{id}` - Eliminar prompt

### Personajes
- `POST /api/config/characters` - Crear personaje
- `GET /api/config/characters` - Listar personajes
- `GET /api/config/characters/{id}` - Obtener personaje
- `PUT /api/config/characters/{id}` - Actualizar personaje
- `DELETE /api/config/characters/{id}` - Eliminar personaje
- `POST /api/config/characters/{id}/prompts/{prompt_id}` - Asociar prompt a personaje

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| **Backend** | Python 3.11+ + FastAPI |
| **Autenticación** | JWT + bcrypt |
| **Base de Datos** | JSON (sin servidor) |
| **Frontend** | HTML5 + CSS3 + JavaScript |
| **Servidor** | Uvicorn |
| **Modelos IA** | Qwen 3.5B, Flux 2.0, Wan 2.2 |

## 📁 Estructura del Proyecto

```
wui/
├── app/
│   ├── api/
│   │   ├── auth.py              # Endpoints de autenticación
│   │   ├── creative.py          # Endpoints de generación creativa
│   │   ├── config.py            # Endpoints de configuración
│   │   ├── channels.py          # Endpoints de canales
│   │   └── dependencies.py      # Dependencias de FastAPI
│   ├── services/
│   │   ├── auth_service.py      # Lógica de autenticación
│   │   ├── creative_service.py  # Lógica de generación
│   │   ├── config_service.py    # Lógica de configuración
│   │   └── channel_service.py   # Lógica de canales
│   ├── core/
│   │   ├── config.py            # Configuración de la app
│   │   └── json_data_manager.py # Gestor de persistencia JSON
│   ├── schemas/                 # Modelos Pydantic
│   └── static/
│       └── index.html           # Interfaz web
├── data/                        # Datos persistidos en JSON
├── main.py                      # Punto de entrada
├── requirements.txt             # Dependencias
└── README.md                    # Este archivo
```

## 🔐 Seguridad

- **Autenticación JWT** - Tokens seguros con expiración configurable
- **Contraseñas Hasheadas** - Uso de bcrypt para almacenamiento seguro
- **CORS Configurado** - Solo permite acceso desde localhost en desarrollo
- **Validación de Entrada** - Todos los datos se validan con Pydantic

## 📝 Credenciales por Defecto

- **Usuario:** `admin`
- **Contraseña:** `admin`

⚠️ **Importante:** Cambia estas credenciales en producción modificando `data/config.json`

## 🎨 Características de Diseño

- **Interfaz Moderna** - Colores profesionales (blanco, grises, azul índigo)
- **Responsive Design** - Funciona en desktop, tablet y móvil
- **Accesibilidad** - Contraste adecuado, navegación clara
- **Animaciones Suaves** - Transiciones y hover effects profesionales
- **Carga Rápida** - Sin dependencias externas, solo HTML/CSS/JS vanilla

## 🚀 Próximas Mejoras

- [ ] Integración con APIs reales de YouTube
- [ ] Soporte para múltiples usuarios
- [ ] Dashboard con estadísticas
- [ ] Exportación a múltiples formatos
- [ ] Historial de generaciones
- [ ] Colaboración en tiempo real

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para reportar bugs o sugerir mejoras, abre un issue en GitHub.

---

**Desarrollado con ❤️ para creadores de contenido**
