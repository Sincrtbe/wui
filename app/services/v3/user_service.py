"""
app/services/v3/user_service.py
Servicio de usuarios y autenticación para WUI v3.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from app.core.multiuser_dal import (
    create_user,
    get_user,
    get_user_by_email,
    list_users,
    update_user,
)

# Config —的理想是从 config.yaml pero por ahora hardcodeado
JWT_SECRET = "wui-v3-secret-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24 * 7  # 7 días


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def register_user(name: str, email: str, password: str) -> dict:
    """Crea un usuario. Lanza ValueError si el email ya existe."""
    existing = get_user_by_email(email)
    if existing:
        raise ValueError(f"Ya existe un usuario con email {email}")
    password_hash = hash_password(password)
    return create_user(name=name, email=email, password_hash=password_hash)


def login_user(email: str, password: str) -> dict:
    """
    Autentica un usuario. Retorna dict con user + token.
    Lanza ValueError si credenciales inválidas.
    """
    user = get_user_by_email(email)
    if not user:
        raise ValueError("Credenciales inválidas")
    if not verify_password(password, user["password_hash"]):
        raise ValueError("Credenciales inválidas")
    token = create_token(user["id"], user["email"])
    return {
        "user": user,
        "token": token,
    }


def get_user_safe(user_id: str) -> Optional[dict]:
    """Retorna usuario sin el password_hash."""
    user = get_user(user_id)
    if not user:
        return None
    return {k: v for k, v in user.items() if k != "password_hash"}
