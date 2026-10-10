from pydantic import BaseModel

from app.schemas.user_schema import UserResponse


class Token(BaseModel):
    """Respuesta de POST /auth/login."""

    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Respuesta de POST /auth/register: datos públicos del usuario más el token."""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"
