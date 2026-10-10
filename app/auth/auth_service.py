from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Se importan todos los modelos para que las relaciones (User -> Todo, Category)
# queden resueltas aunque este módulo se use sin pasar por app.main
from app.models import category_model, todo_model  # noqa: F401
from app.models.user_model import User
from app.auth.security import hash_password, verify_password
from app.schemas.user_schema import UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.scalar(select(User).where(User.email == email.lower()))


def register_user(db: Session, data: UserCreate) -> User:
    """Crea un usuario con rol 'user' y la contraseña en hash."""
    email = data.email.lower()
    if get_user_by_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    user = User(
        name=data.name,
        email=email,
        hashed_password=hash_password(data.password),
        role="user",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # dos registros simultáneos con el mismo correo
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Valida correo y contraseña. 401 si son incorrectos, 403 si el usuario está inactivo."""
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
        )
    return user
