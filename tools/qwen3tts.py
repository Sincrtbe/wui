import sys
import subprocess
import argparse

def asegurar_entorno():
    """Verifica e instala las librerías dentro del propio script si no existen."""
    paquetes_requeridos = {
        "torch": "torch", 
        "soundfile": "soundfile", 
        "qwen_tts": "qwen-tts"
    }
    faltantes = []
    
    for modulo, paquete in paquetes_requeridos.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(paquete)
            
    if faltantes:
        print(f"[*] Instalando dependencias faltantes: {', '.join(faltantes)}...")
        # Usa el ejecutable de Python actual para instalar paquetes automáticamente
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U"] + faltantes)
        print("[*] Dependencias instaladas correctamente.\n")

# 1. Ejecutamos la auto-instalación antes de importar las librerías pesadas
asegurar_entorno()

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

def main():
    parser = argparse.ArgumentParser(description="Clonador de Voz Qwen3-TTS (Local)")
    parser.add_argument("texto", type=str, help="El texto nuevo que quieres generar")
    parser.add_argument("ref_audio", type=str, help="Ruta al archivo de audio de referencia (.wav)")
    parser.add_argument("--ref_text", type=str, default="", help="Transcripción exacta del audio de referencia (mejora la calidad enormemente)")
    parser.add_argument("--lang", type=str, default="Spanish", help="Idioma de salida (default: Spanish)")
    parser.add_argument("--out", type=str, default="resultado_qwen3.wav", help="Archivo de salida")
    
    args = parser.parse_args()

    print("\n[1/3] Cargando Qwen3-TTS-12Hz-1.7B-Base en memoria...")
    
    # Asignación automática de hardware
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    # Descarga (si es la primera vez) e instancia automática del modelo
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map=device,
        dtype=dtype,
    )

    print("\n[2/3] Extrayendo características y clonando voz...")
    
    # Parámetros oficiales requeridos para el Base Model
    kwargs = {
        "text": args.texto,
        "language": args.lang,
        "ref_audio": args.ref_audio,
    }
    
    if args.ref_text:
        kwargs["ref_text"] = args.ref_text
    else:
        # Modo x-vector si no transcribes el audio de referencia (reduce un poco la calidad)
        kwargs["x_vector_only_mode"] = True

    wavs, sr = model.generate_voice_clone(**kwargs)

    print(f"\n[3/3] Guardando audio generado en: {args.out}")
    sf.write(args.out, wavs[0], sr)
    print("¡Listo! Proceso terminado.")

if __name__ == "__main__":
    main()