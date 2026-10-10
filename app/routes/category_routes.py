# app/routes/category_routes.py
from fastapi import APIRouter, Depends, Response, status as http_status
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.schemas.category_schema import CategoryCreate, CategoryResponse
from app.schemas.error_schema import (
    R401,
    R403,
    R403_INACTIVO,
    R404_CATEGORIA,
    R409_CATEGORIA_TAREAS,
    R409_NOMBRE,
)
from app.services import category_service

router = APIRouter()  # Debe llamarse 'router'


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Crear una categoría",
    description="Crea una categoría propia. El nombre debe ser único para cada usuario.",
    responses={401: R401, 403: R403_INACTIVO, 409: R409_NOMBRE},
)
def crear_categoria(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return category_service.create_category(db, current_user, data)


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="Listar mis categorías",
    description="Devuelve las categorías del usuario autenticado, ordenadas por nombre.",
    responses={401: R401, 403: R403_INACTIVO},
)
def listar_categorias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return category_service.list_categories(db, current_user)


@router.delete(
    "/{category_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría",
    description=(
        "Elimina una categoría propia. Responde 409 si todavía tiene tareas asociadas "
        "y 403 si pertenece a otro usuario."
    ),
    responses={401: R401, 403: R403, 404: R404_CATEGORIA, 409: R409_CATEGORIA_TAREAS},
)
def eliminar_categoria(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    category_service.delete_category(db, current_user, category_id)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
