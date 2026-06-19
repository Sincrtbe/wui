"""
app/api/auth.py
Endpoints de autenticación (login).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import AuthRequest, TokenResponse
from app.services.auth_service import verify_password, create_access_token, hash_password
from app.core.json_data_manager import read_global_config, write_global_config
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
async def login(credentials: AuthRequest):
    """Iniciar sesión y obtener token JWT."""
    config = read_global_config()
    stored_user = config.get("admin_user", "admin")
    stored_hash = config.get("admin_pass_hash", "")

    # Si no hay hash válido configurado, crear uno por defecto
    if not stored_hash or stored_hash.startswith("$2b$12$EXAMPLE"):
        stored_hash = hash_password("admin")
        stored_user = "admin"
        config["admin_pass_hash"] = stored_hash
        config["admin_user"] = stored_user
        write_global_config(config)

    # Verificar que el usuario existe y es el correcto
    if credentials.username != stored_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar contraseña
    if not verify_password(credentials.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": credentials.username})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=1800,  # 30 minutos
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtener información del usuario actual (valida el token)."""
    return current_user


@router.post("/register")
async def register(credentials: AuthRequest):
    """Registrar un nuevo administrador (solo en debug)."""
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registro deshabilitado en producción",
        )

    # Verificar que el usuario no exista ya
    existing = read_global_config()
    if existing.get("admin_user") == credentials.username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario ya existe",
        )

    # Crear nuevo hash
    new_hash = hash_password(credentials.password)

    # Actualizar configuración
    existing["admin_user"] = credentials.username
    existing["admin_pass_hash"] = new_hash
    write_global_config(existing)

    return {"message": "Usuario registrado exitosamente"}
