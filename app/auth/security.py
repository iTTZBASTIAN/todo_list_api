import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

# El .env está en la raíz del proyecto (dos carpetas por encima de este archivo)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise RuntimeError(
        "Falta SECRET_KEY. Copia .env.example como .env y define SECRET_KEY "
        "(ver README, sección Configuración)."
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de la contraseña (nunca se guarda en texto plano)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un JWT cuyo 'sub' es el id del usuario (como texto) y que vence en el tiempo indicado."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Valida firma y vencimiento. Lanza jose.JWTError si el token no es válido."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
