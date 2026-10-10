# app/auth/auth_routes.py
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import auth_service
from app.auth.security import create_access_token
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.middlewares.rate_limit import limiter
from app.models.user_model import User
from app.schemas.auth_schema import RegisterResponse, Token
from app.schemas.error_schema import R400_EMAIL, R401, R401_LOGIN, R403_INACTIVO, R429
from app.schemas.user_schema import UserCreate, UserResponse

router = APIRouter()  # Debe llamarse 'router'


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un usuario",
    description=(
        "Crea un usuario con rol `user` y la contraseña guardada como hash. "
        "La contraseña debe tener al menos 8 caracteres, con mayúscula, minúscula y número, "
        "sin espacios. Devuelve los datos públicos del usuario y un token de acceso. "
        "Límite: 3 peticiones por minuto."
    ),
    responses={400: R400_EMAIL, 429: R429},
)
@limiter.limit("3/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, data)
    return RegisterResponse(
        user=UserResponse.model_validate(user),
        access_token=create_access_token(user.id),
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description=(
        "Recibe el correo (en el campo `username`) y la contraseña como formulario "
        "OAuth2 y devuelve el token JWT. Límite: 5 peticiones por minuto."
    ),
    responses={401: R401_LOGIN, 403: R403_INACTIVO, 429: R429},
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm usa el campo 'username' para el correo
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    return Token(access_token=create_access_token(user.id))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Usuario autenticado",
    description="Devuelve los datos públicos del usuario dueño del token (sin contraseña).",
    responses={401: R401, 403: R403_INACTIVO},
)
def me(current_user: User = Depends(get_current_active_user)):
    return current_user
