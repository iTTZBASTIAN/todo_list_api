# app/routes/admin_routes.py
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import require_admin
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.schemas.error_schema import R401, R403_ADMIN
from app.schemas.todo_schema import TodoAdminPage, TodoAdminResponse
from app.services import todo_service

router = APIRouter()  # Debe llamarse 'router'


@router.get(
    "/todos",
    response_model=TodoAdminPage,
    summary="Listar las tareas de todos los usuarios",
    description=(
        "Solo para administradores. Lista paginada de las tareas de todos los usuarios, "
        "con los datos del dueño. Se puede filtrar por el correo del dueño con `owner_email`."
    ),
    responses={401: R401, 403: R403_ADMIN},
)
def listar_todos_admin(
    page: int = Query(1, ge=1, description="Número de página (mínimo 1)"),
    limit: int = Query(10, ge=1, le=50, description="Tareas por página (1 a 50)"),
    owner_email: Optional[str] = Query(None, description="Correo exacto del dueño de las tareas"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    todos, total = todo_service.list_todos_admin(
        db, page=page, limit=limit, owner_email=owner_email
    )
    return TodoAdminPage(
        data=[TodoAdminResponse.model_validate(t) for t in todos],
        page=page,
        limit=limit,
        total=total,
    )
