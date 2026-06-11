# Wui - Plataforma de Automatización de YouTube

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-blue)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.x-green)](https://www.python.org)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgray)](https://www.sqlite.org)

## 📋 Descripción

Wui es una plataforma local de automatización para la gestión de múltiples canales de YouTube. Permite gestionar canales, crear contenido, programar publicaciones, analizar métricas, automatizar flujos de trabajo y gestionar una biblioteca de prompts con IA.

## ✨ Funcionalidades

- **Gestión de Canales** - CRUD completo con datos extendidos, thumbnails, colores personalizados
- **Programación de Publicaciones** - Videos largos, Shorts y artículos con frecuencia configurable
- **Gestión de Contenido** - Flujo de trabajo: Idea → Guión → Desarrollo → Video
- **Análisis y Métricas** - Suscriptores, vistas, gráficos de evolución e historial
- **Biblioteca de Prompts** - Creación, gestión y rating de prompts con detección de variables
- **Automatización** - Tareas programadas con APScheduler y workflows programables
- **Dashboard** - Resumen general con calendario bimensual y filtros por canal
- **Configuración Segura** - API keys almacenadas en `.env`, nunca en base de datos
- **System Tray** - Icono en bandeja del sistema para control rápido

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## 🏃 Inicio

### Opción 1: Batch file
```cmd
.\run_server.bat
```

### Opción 2: Manual
```bash
uvicorn app.main:app --reload --port 9080
```

### Acceso
- **UI Web:** http://127.0.0.1:9080/ui
- **API Base:** http://127.0.0.1:9080
- **Health Check:** http://127.0.0.1:9080/health

## 📖 Flujo de Trabajo Recomendado

1. **Configurar API Key** → Configuración → Servicios → YouTube API Key
2. **Crear canal** → Canales → Introducir nombre → Guardar
3. **Configurar programación** → Seleccionar canal → Activar tipos → Configurar frecuencia
4. **Generar calendario** → "Generar Mes Actual" y "Generar Mes Siguiente"
5. **Gestionar contenido** → Crear ideas → Generar guiones → Asociar a publicaciones

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python 3.x + FastAPI 0.104.1 |
| **Base de datos** | SQLite + SQLAlchemy 2.0.23 |
| **Frontend** | HTML5 + CSS3 + JavaScript vanilla |
| **Servidor** | Uvicorn 0.24.0 |
| **Tareas cron** | APScheduler 3.10.4 |
| **API YouTube** | google-api-python-client 2.197.0 |

## 📁 Estructura del Proyecto

```
Wui/
├── app/                    # Aplicación principal
│   ├── routers/            # Endpoints API REST
│   ├── models/             # Modelos SQLAlchemy
│   ├── services/           # Lógica de negocio
│   ├── static/             # Archivos frontend
│   └── tasks/              # Tareas programadas
├── channels_data/          # Datos de canales
├── prompts/                # Plantillas de prompts
├── tools/                  # Herramientas utilitarias
└── skills/                 # Skills de desarrollo
```

## 📚 Documentación Adicional

| Archivo | Contenido |
|---------|-----------|
| `inprogress.md` | Documento principal del proyecto |
| `bug.md` | Historial de bugs y correcciones |
| `projectinfo.md` | Ficha técnica resumida |

## 🔗 Repositorio

- **GitHub:** https://github.com/Sincrtbe/wui.git
- **Rama:** master

## ⚠️ Notas

- Reiniciar el servidor después de cambios de código (comportamiento esperado de Uvicorn)
- La API Key de YouTube se almacena de forma segura en `.env`