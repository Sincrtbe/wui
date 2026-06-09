import sys
import os
import json
import datetime
from pathlib import Path
from googleapiclient.discovery import build

# --- CONFIGURACIÓN ---
API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
if not API_KEY:
    print(json.dumps({"error": "Falta la variable de entorno YOUTUBE_API_KEY"}, indent=4))
    sys.exit(1)

# Ruta absoluta a la carpeta metricas desde el script
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()
DEFAULT_OUTPUT_DIR = str(PROJECT_ROOT / "metricas")

# Validación: Al menos necesitamos el ID del canal
if len(sys.argv) < 2:
    error_msg = {
        "error": "Falta el ID del canal.",
        "uso_1": "python script2.py UC_xxxx",
        "uso_2": "python script2.py UC_xxxx 'nueva_ruta_carpeta'"
    }
    print(json.dumps(error_msg, indent=4))
    sys.exit(1)

channel_id = sys.argv[1]

# Lógica de la ruta: Si pasan un 2º parámetro, sobrescribe la ruta por defecto
if len(sys.argv) >= 3:
    OUTPUT_DIR = sys.argv[2]
else:
    OUTPUT_DIR = DEFAULT_OUTPUT_DIR

# Crear la carpeta automáticamente (sea la de por defecto o la sobrescrita)
os.makedirs(OUTPUT_DIR, exist_ok=True)

youtube = build('youtube', 'v3', developerKey=API_KEY)

try:
    # Consultar las estadísticas públicas del canal
    response = youtube.channels().list(
        part="statistics",
        id=channel_id
    ).execute()

    if not response.get("items"):
        print(json.dumps({"error": f"No se encontró ningún canal con el ID: {channel_id}"}, indent=4))
        sys.exit(1)

    stats = response["items"][0]["statistics"]

    # Construir el JSON de salida con la fecha de hoy
    resultado = {
        "viewCount": int(stats.get("viewCount", 0)),
        "subscriberCount": int(stats.get("subscriberCount", 0)),
        "videoCount": int(stats.get("videoCount", 0)),
        "fecha_ejecucion": datetime.date.today().isoformat()
    }

    # Definir la ruta del archivo utilizando la carpeta correspondiente
    ruta_stats = os.path.join(OUTPUT_DIR, f"{channel_id}_stats.json")

    # Guardar el JSON en la carpeta
    with open(ruta_stats, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)

    # Imprimir por consola el JSON puro para tu herramienta
    print(json.dumps(resultado, ensure_ascii=False, indent=4))

except Exception as e:
    print(json.dumps({"error": str(e)}, indent=4))