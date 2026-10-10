from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.dependencies.database_dependency import get_db
from app.models import category_model, todo_model  # noqa: F401
from app.models.user_model import User

# auto_error=False para responder siempre con el mismo 401 ("Unauthorized"),
# tanto si falta el token como si es inválido o está vencido.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _no_autenticado() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Usuario dueño del token. 401 si falta, es inválido o venció."""
    if token is None:
        raise _no_autenticado()
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise _no_autenticado()

    user = db.get(User, user_id)
    if user is None:
        raise _no_autenticado()
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Como get_current_user, pero 403 si el usuario está inactivo."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Solo deja pasar a usuarios con rol 'admin'; los demás reciben 403."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user
