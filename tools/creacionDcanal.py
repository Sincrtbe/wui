"""Crea un canal en la plataforma Wui y guarda sus datos."""
import sys
import os
import json
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- CONFIGURACIÓN ---
API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SERVER_URL = os.getenv("WUI_SERVER_URL", "http://127.0.0.1:9080")
DEFAULT_OUTPUT_DIR = os.path.join("..", "channels_data")

# Validar API_KEY
if not API_KEY:
    print("ERROR: YOUTUBE_API_KEY no está configurada en las variables de entorno.")
    print("Crea un archivo .env con la clave o ejecuta: export YOUTUBE_API_KEY='tu_clave'")
    sys.exit(1)

# Validación: Al menos necesitamos el nombre del canal
if len(sys.argv) < 2:
    print("Error: Falta el nombre del canal.")
    print("Uso básico:  python creacionDcanal.py 'Nombre Del Canal'")
    print("Uso avanzado: python creacionDcanal.py 'Nombre Del Canal' 'nueva_ruta_carpeta'")
    sys.exit(1)

nombre_canal = sys.argv[1]

# Lógica de la ruta: Si pasan un 2º parámetro, sobrescribe la ruta por defecto
if len(sys.argv) >= 3:
    OUTPUT_DIR = sys.argv[2]
else:
    OUTPUT_DIR = DEFAULT_OUTPUT_DIR

# Crear la carpeta automáticamente
os.makedirs(OUTPUT_DIR, exist_ok=True)

youtube = build('youtube', 'v3', developerKey=API_KEY)

try:
    # 1. Buscar el canal por nombre para obtener su ID real de YouTube
    print(f"Buscando canal: {nombre_canal}...")
    search_response = youtube.search().list(
        q=nombre_canal,
        type="channel",
        part="id",
        maxResults=1
    ).execute()

    if not search_response.get("items"):
        print(f"No se encontró ningún canal con el nombre: {nombre_canal}")
        sys.exit(1)

    channel_id_youtube = search_response["items"][0]["id"]["channelId"]
    print(f"ID de YouTube encontrado: {channel_id_youtube}")

    # 2. Obtener los detalles específicos del canal
    channel_response = youtube.channels().list(
        part="snippet,topicDetails",
        id=channel_id_youtube
    ).execute()

    canal_data = channel_response["items"][0]
    snippet = canal_data.get("snippet", {})
    topic_details = canal_data.get("topicDetails", {})

    # 3. Estructurar la información solicitada
    info_json = {
        "id": channel_id_youtube,
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "customUrl": snippet.get("customUrl"),
        "publishedAt": snippet.get("publishedAt"),
        "topicIds": topic_details.get("topicIds", []),
        "topicCategories": topic_details.get("topicCategories", [])
    }

    # Normalizar el nombre para el archivo
    nombre_fichero = "".join(c for c in nombre_canal if c.isalnum() or c in (' ', '_', '-')).strip()
    nombre_fichero = nombre_fichero.replace(" ", "_")

    # Definir rutas completas dentro de la carpeta final
    ruta_json = os.path.join(OUTPUT_DIR, f"{nombre_fichero}.json")
    ruta_jpg = os.path.join(OUTPUT_DIR, f"{nombre_fichero}.jpg")

    # Guardar el archivo .json con datos de YouTube
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(info_json, f, ensure_ascii=False, indent=4)
    print(f"Datos de YouTube guardados en: {ruta_json}")

    # 4. Descargar el Thumbnail
    thumbnails = snippet.get("thumbnails", {})
    url_foto = thumbnails.get("high", thumbnails.get("default", {})).get("url")

    if url_foto:
        imagen_bytes = requests.get(url_foto).content
        with open(ruta_jpg, "wb") as f_img:
            f_img.write(imagen_bytes)
        print(f"Thumbnail guardado en: {ruta_jpg}")
    else:
        print("Advertencia: No se encontró thumbnail para el canal")

    # 5. Crear el canal en la plataforma Wui mediante la API
    print(f"\nCreando canal en la plataforma Wui...")
    
    # Verificar si el servidor está disponible
    try:
        health = requests.get(f"{SERVER_URL}/health", timeout=5)
        if health.status_code != 200:
            raise Exception("El servidor no está respondiendo correctamente")
    except requests.exceptions.ConnectionError:
        print(f"ERROR: No se pudo conectar con el servidor en {SERVER_URL}")
        print("Asegúrate de que el servidor esté ejecutándose antes de crear el canal.")
        sys.exit(1)
    
    # Crear el canal en la base de datos
    channel_data_api = {
        "name": info_json["title"],
        "color": "#FF6600",  # Color por defecto
        "email": "",
        "social_links": {
            "youtube": f"https://www.youtube.com/channel/{channel_id_youtube}"
        },
        "checkpoints": {}
    }
    
    response = requests.post(
        f"{SERVER_URL}/api/channels",
        json=channel_data_api,
        timeout=10
    )
    
    if response.status_code == 200:
        channel_created = response.json()
        channel_db_id = channel_created["id"]
        print(f"Canal creado correctamente en la plataforma con ID: {channel_db_id}")
        
        # Actualizar el archivo JSON con el ID de la base de datos
        info_json["db_id"] = channel_db_id
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(info_json, f, ensure_ascii=False, indent=4)
        print(f"Archivo JSON actualizado con el ID de base de datos: {channel_db_id}")
    else:
        print(f"ERROR al crear el canal en la plataforma: {response.status_code}")
        print(f"Respuesta: {response.text}")
        sys.exit(1)

    print(f"\n¡Éxito! Canal '{nombre_canal}' creado correctamente.")
    print(f"  - Datos de YouTube: {ruta_json}")
    print(f"  - Thumbnail: {ruta_jpg}")
    print(f"  - Canal en plataforma: ID {channel_created.get('id', 'N/A')}")

except HttpError as e:
    print(f"Error de YouTube API: {e}")
    sys.exit(1)
except requests.exceptions.ConnectionError:
    print(f"ERROR: No se pudo conectar con el servidor en {SERVER_URL}")
    print("Asegúrate de que el servidor esté ejecutándose antes de crear el canal.")
    sys.exit(1)
except Exception as e:
    print(f"Ocurrió un error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)