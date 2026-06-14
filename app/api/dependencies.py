"""
app/api/dependencies.py
Dependencias de FastAPI para autenticación y autorización.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import decode_token

# Esquema de seguridad para Bearer tokens
security = HTTPBearer()

# Usuario por defecto (en producción, usar base de datos)
DEFAULT_USERS = {
    "admin": "$2b$12$EXAMPLEHASHFORADMINPASS",
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependencia para obtener el usuario actual desde el token JWT.
    Retorna un dict con 'username' y 'sub'.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene nombre de usuario",
        )

    return {"username": username, "sub": username}


def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Dependencia para verificar que el usuario está activo.
    En producción, verificar estado en base de datos.
    """
    return current_user
