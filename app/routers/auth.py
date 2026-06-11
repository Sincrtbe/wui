"""Router de autenticación."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.core.config import settings
from app.core.ratelimit import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBasic()


@limiter.limit("5/minute")
@router.post("/login")
async def login(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    """Valida credenciales de admin."""
    user_ok = credentials.username.encode("utf-8") == settings.ADMIN_USER.encode("utf-8")
    pass_ok = credentials.password.encode("utf-8") == settings.ADMIN_PASS.encode("utf-8")
    
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return {
        "user": credentials.username,
        "message": "Login exitoso"
    }


@router.get("/check")
async def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica si las credenciales son válidas."""
    user_ok = credentials.username.encode("utf-8") == settings.ADMIN_USER.encode("utf-8")
    pass_ok = credentials.password.encode("utf-8") == settings.ADMIN_PASS.encode("utf-8")
    
    if not (user_ok and pass_ok):
        return {"authenticated": False}
    
    return {"authenticated": True}


@router.post("/logout")
async def logout():
    """Cierra la sesión."""
    return {"message": "Sesión cerrada"}
