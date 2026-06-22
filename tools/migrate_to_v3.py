"""
tools/migrate_to_v3.py
Script de migración de datos WUI v2 → v3.
Uso: python tools/migrate_to_v3.py [--dry-run] [--user-id USER_ID]
"""

import argparse
import sys
from pathlib import Path

# Asegurar que el path incluye el proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.multiuser_dal import (
    init_system_dirs,
    seed_default_prompts,
    migrate_from_v2,
    USERS_DIR,
    SYSTEM_DIR,
    create_user,
    get_user_by_email,
)


def main():
    parser = argparse.ArgumentParser(description="Migra datos WUI v2 a v3")
    parser.add_argument("--dry-run", action="store_true", help="Simula la migración sin escribir nada")
    parser.add_argument("--user-id", type=str, default=None, help="User ID destino (crea usuario si no existe)")
    parser.add_argument("--user-email", type=str, default="d4ytacop@gmail.com", help="Email del usuario destino")
    parser.add_argument("--user-name", type=str, default="David", help="Nombre del usuario destino")
    parser.add_argument("--v2-data-dir", type=str, default=None, help="Ruta al directorio data v2 (default: ../wui-v2-data)")
    args = parser.parse_args()

    print("=" * 60)
    print(" WUI v2 → v3 Migration Tool")
    print("=" * 60)

    # Determinar directorio v2
    if args.v2_data_dir:
        v2_dir = Path(args.v2_data_dir)
    else:
        v2_dir = Path(__file__).parent.parent / "wui-v2-data"

    print(f"\n📁 Directorio v2 detectado: {v2_dir}")

    if not v2_dir.exists():
        print(f"⚠️  El directorio v2 no existe. Se creará la estructura v3 vacía.")
        v2_dir = None

    # Inicializar estructura v3
    print("\n📦 Inicializando estructura v3...")
    init_system_dirs()
    print("  ✅ directorios creados")

    # Seed default prompts
    print("\n📝 Creando prompts default del sistema...")
    seed_default_prompts()
    print("  ✅ prompts default creados")

    # Crear o usar usuario existente
    print(f"\n👤 Preparando usuario destino: {args.user_email}")
    existing = get_user_by_email(args.user_email)
    if existing:
        print(f"  ✅ Usuario ya existe (ID: {existing['id']})")
        user_id = existing["id"]
    else:
        if args.dry_run:
            print(f"  🔄 [DRY-RUN] Se crearía usuario: {args.user_name} <{args.user_email}>")
            user_id = "mock-user-id"
        else:
            print(f"  ➕ Creando usuario...")
            # Para migración real, necesitamos password_hash (no se puede inferir)
            # Creamos con password temporal que el usuario deberá cambiar
            user = create_user(
                name=args.user_name,
                email=args.user_email,
                password_hash="MIGRATED_DO_NOT_USE",
            )
            user_id = user["id"]
            print(f"  ✅ Usuario creado (ID: {user_id})")
            print("  ⚠️  IMPORTANTE: El usuario tiene password temporal 'MIGRATED_DO_NOT_USE'")
            print("     Cambia el password inmediatamente tras el primer login.")

    # Migrar datos v2
    if v2_dir and v2_dir.exists():
        print(f"\n🔄 Migrando datos desde {v2_dir}...")
        if args.dry_run:
            print("  🔄 [DRY-RUN] Simulando migración...")
        else:
            stats = migrate_from_v2(v2_dir, user_id)
            print(f"  ✅ Canales migrados: {stats['channels_migrated']}")
            print(f"  ✅ Content items migrados: {stats['content_items_migrated']}")
            if stats["errors"]:
                print(f"  ⚠️  Errores: {len(stats['errors'])}")
                for err in stats["errors"]:
                    print(f"     - {err}")
    else:
        print("\n  ℹ️  No hay datos v2 que migrar")

    print("\n" + "=" * 60)
    print(" ✅ Migración completada")
    print("=" * 60)
    print(f"\n📂 Datos v3 en: {USERS_DIR}")
    print(f"📂 Sistema en: {SYSTEM_DIR}")


if __name__ == "__main__":
    main()
