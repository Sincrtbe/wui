# Skill: desarrollosoftware

## Descripción
Esta skill guía la creación y mantenimiento del fichero `projectinfo.md`, un documento centralizado que contiene toda la información relevante del proyecto de software. Cada vez que se empiece una modificación sobre el proyecto, este fichero debe pasarse como contexto para mantener coherencia en el desarrollo.

## Objetivo
Crear y mantener `projectinfo.md` con información estructurada sobre:
- Datos generales del proyecto
- Stack tecnológico
- Repositorio utilizado (o indicación si no usa repositorio)
- Datos de uso (puertos, líneas de lanzamiento)
- Estructura de directorios y contenido de ficheros
- Funcionalidades de la aplicación
- Cosas hechas y funcionando
- Fallos notificados
- Tareas pendientes

## Proceso de Creación del Fichero projectinfo.md

### Paso 1: Exploración del Proyecto
Antes de crear el fichero, explorar todo el proyecto:
1. Listar todos los archivos y directorios
2. Leer ficheros de configuración (requirements.txt, pyproject.toml, package.json, etc.)
3. Leer fichero principal de la aplicación
4. Explorar modelos, servicios, routers, vistas, etc.
5. Verificar repositorio git si existe
6. Leer documentación existente (README.md, project.md, etc.)

### Paso 2: Recopilación de Información

#### Datos Generales del Proyecto
- **Nombre del proyecto**
- **Descripción corta**
- **Descripción larga**
- **Propósito principal**
- **Fecha de creación**
- **Versión actual**

#### Stack Tecnológico
- **Lenguajes principales**
- **Framework principal**
- **Bases de datos**
- **Librerías clave** (extraídas de requirements.txt o similar)
- **Herramientas de desarrollo**
- **Dependencias de frontend** (si aplica)

#### Información del Repositorio
- **URL del repositorio** (extraída de git remote)
- **Tipo de repositorio** (público/privado)
- **rama principal**
- **Último commit**
- **Si no usa repositorio**: indicar "Sin repositorio git configurado"

#### Datos de Uso
- **Puertos utilizados**
- **Líneas de lanzamiento** (comandos para iniciar el proyecto)
- **Variables de entorno necesarias**
- **Rutas de la API**
- **Accesibilidad** (URL de acceso a la UI)

#### Estructura de Directorios
- Listado completo de directorios
- Descripción de qué contiene cada directorio
- Descripción de qué contiene cada fichero importante

#### Funcionalidades
- **Qué hace la aplicación**
- **API endpoints disponibles**
- **Características principales**
- **Tareas automatizadas**

#### Cosas Hechas y Funcionando
- Lista de funcionalidades completadas y verificadas
- Componentes que funcionan correctamente

#### Fallos Notificados
- Bugs conocidos
- Errores reportados
- Problemas pendientes de solución

#### Tareas Pendientes
- Features por implementar
- Mejoras propuestas
- Correcciones pendientes

### Paso 3: Generación del Fichero
Crear `projectinfo.md` con la siguiente estructura exacta:

```markdown
# ProjectInfo - [Nombre del Proyecto]

## 1. Datos Generales
- **Nombre:** [nombre]
- **Versión:** [versión]
- **Descripción:** [descripción corta]
- **Propósito:** [propósito principal]
- **Fecha de creación:** [fecha]
- **Última actualización:** [fecha]

## 2. Stack Tecnológico
### Lenguajes
- [lenguaje 1]
- [lenguaje 2]
...

### Frameworks
- [framework 1]
- [framework 2]
...

### Bases de Datos
- [bd 1]
- [bd 2]
...

### Librerías Principales
- [librería 1]
- [librería 2]
...

## 3. Repositorio
- **Tipo:** [git / sin repositorio]
- **URL:** [url o "N/A"]
- **Rama principal:** [rama]
- **Último commit:** [hash o "N/A"]
- **Remote origin:** [url]

## 4. Datos de Uso
### Puertos
- **Puerto principal:** [puerto]
- **Host:** [host]

### Líneas de Lanzamiento
```bash
[comando 1]
[comando 2]
...
```

### Variables de Entorno
- `[VARIABLE_1]`: [descripción]
- `[VARIABLE_2]`: [descripción]
...

### Acceso
- **UI Web:** [url]
- **API Base:** [url]
- **Health Check:** [url]

## 5. Estructura del Proyecto
```
[estructura de directorios completa]
```

### Descripción de Directorios
- **[directorio/]:** [descripción de contenido]
...

### Contenido de Ficheros Clave
- **[fichero]:** [descripción de propósito y contenido]
...

## 6. Funcionalidades de la Aplicación
### Funcionalidades Principales
1. [funcionalidad 1]
2. [funcionalidad 2]
...

### API Endpoints
- **GET/POST/PUT/DELETE [ruta]:** [descripción]
...

### Tareas Automatizadas
- [tarea 1]: [descripción]
- [tarea 2]: [descripción]
...

## 7. Estado Actual
### ✅ Cosas Hechas y Funcionando
- [feature 1]
- [feature 2]
...

### ⚠️ Fallos Notificados
- **[bug 1]:** [descripción]
- **[bug 2]:** [descripción]
...

### 📋 Tareas Pendientes
- [tarea 1]: [descripción]
- [tarea 2]: [descripción]
...

## 8. Notas Adicionales
[cualquier otra información relevante]
```

### Paso 4: Uso de la Skill

Cuando se solicite modificar el proyecto:
1. **Verificar projectinfo.md** si existe, leerlo como contexto
2. **Actualizar projectinfo.md** después de cualquier cambio significativo
3. **Mantener la coherencia** entre el código y el documento
4. **Registrar nuevos bugs** en la sección de fallos notificados
5. **Actualizar tareas pendientes** después de completarlas o añadirlas

### Paso 5: Mantenimiento
Después de cada modificación al proyecto:
1. Verificar si la estructura de directorios cambió
2. Actualizar funcionalidades completadas
3. Añadir nuevos bugs encontrados
4. Actualizar tareas pendientes
5. Registrar cambios en el stack tecnológico si aplica

## Reglas Importantes

1. **Siempre crear projectinfo.md al inicio** de cualquier proyecto nuevo
2. **Mantener actualizado** después de cada cambio significativo
3. **Pasarlo como contexto** cada vez que se empiece una nueva modificación
4. **Ser conciso pero completo** en las descripciones
5. **Incluir información técnica** relevante para desarrollo
6. **Actualizar la fecha de última actualización** en cada modificación
7. **Documentar fallos notificados** con enough detalle para reproducirlos
8. **Listar líneas de lanzamiento** exactas para ejecutar el proyecto

## Ejemplo de Uso

Cuando el usuario dice: "Crear projectinfo.md para este proyecto"
1. Ejecutar Paso 1 (Exploración)
2. Ejecutar Paso 2 (Recopilación)
3. Ejecutar Paso 3 (Generación)
4. Confirmar que se ha creado el fichero

Cuando el usuario dice: "Actualizar projectinfo.md"
1. Leer el fichero existente
2. Explorar cambios desde la última actualización
3. Actualizar solo las secciones modificadas
4. Actualizar la fecha

Cuando se empieza una nueva tarea de desarrollo:
1. Leer projectinfo.md como contexto
2. Trabajar en la tarea
3. Actualizar projectinfo.md al completar