"""
app/api/v3/auth.py
Rutas de autenticación: register, login, me.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.v3.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
)
from app.services.v3.user_service import (
    register_user,
    login_user,
    get_user_safe,
    decode_token,
)

router = APIRouter()
security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency que extrae el user del JWT."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token proporcionado",
        )
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    user = get_user_safe(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate):
    """Registra un nuevo usuario. Solo admin (futuro: restricción por invitación)."""
    try:
        user = register_user(name=body.name, email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    token = login_user(body.email, body.password)["token"]
    safe_user = get_user_safe(user["id"])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut(**safe_user),
    )


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin):
    """Login con email + password. Retorna JWT."""
    try:
        result = login_user(body.email, body.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    safe_user = get_user_safe(result["user"]["id"])
    return TokenResponse(
        access_token=result["token"],
        token_type="bearer",
        user=UserOut(**safe_user),
    )


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    """Obtiene el usuario autenticado actual."""
    return UserOut(**user)


@router.put("/me", response_model=UserOut)
def update_me(body: UserUpdate, user: dict = Depends(get_current_user)):
    """Actualiza el perfil del usuario actual."""
    # Import延迟 para evitar circular
    from app.core.multiuser_dal import update_user
    updated = update_user(user["id"], body.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    safe = get_user_safe(updated["id"])
    return UserOut(**safe)
