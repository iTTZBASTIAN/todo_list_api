from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    # máximo 72: bcrypt solo usa los primeros 72 bytes
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        if any(c.isspace() for c in v):
            raise ValueError("La contraseña no puede contener espacios")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: Literal["user", "admin"]
    # hashed_password NO se incluye a propósito
