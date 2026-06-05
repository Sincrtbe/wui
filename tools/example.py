"""Script de ejemplo para demostrar la ejecución desde la app."""
import argparse
import json
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Script de ejemplo")
    parser.add_argument("--name", default="Mundo", help="Nombre a saludar")
    parser.add_argument("--count", type=int, default=1, help="Número de saludos")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Formato de salida")
    
    args = parser.parse_args()
    
    print(f"=== Script de ejemplo ===")
    print(f"Ejecutado: {datetime.utcnow().isoformat()}")
    print(f"Python: {sys.version}")
    print()
    
    for i in range(args.count):
        greeting = f"Hola, {args.name}!"
        if args.output == "json":
            print(json.dumps({"message": greeting, "index": i}))
        else:
            print(greeting)
    
    print()
    print("Script completado con éxito.")
    return 0


if __name__ == "__main__":
    sys.exit(main())