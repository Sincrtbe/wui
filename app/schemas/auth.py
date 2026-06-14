"""
app/schemas/auth.py
Schemas Pydantic para autenticación JWT.
"""

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    """Credenciales de login."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Respuesta con token JWT."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos
