# app/routes/todo_routes.py
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, Request, Response, status as http_status
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.dependencies.todo_dependency import get_owned_todo_or_404
from app.middlewares.rate_limit import limiter
from app.models.todo_model import Todo
from app.models.user_model import User
from app.schemas.error_schema import (
    R400_VACIO,
    R401,
    R403,
    R403_INACTIVO,
    R404_CATEGORIA,
    R404_TAREA,
    R409_CATEGORIA_AJENA,
    R429,
)
from app.schemas.todo_schema import (
    Priority,
    Status,
    TodoCreate,
    TodoPage,
    TodoReplace,
    TodoResponse,
    TodoUpdate,
)
from app.services import todo_service

router = APIRouter()  # Debe llamarse 'router'


@router.post(
    "",
    response_model=TodoResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Crear una tarea",
    description=(
        "Crea una tarea asociada al usuario del token. `due_date` no puede ser anterior a hoy "
        "y, si se envía `category_id`, la categoría debe ser del usuario. "
        "Límite: 20 peticiones por minuto."
    ),
    responses={
        401: R401,
        403: R403_INACTIVO,
        404: R404_CATEGORIA,
        409: R409_CATEGORIA_AJENA,
        429: R429,
    },
)
@limiter.limit("20/minute")
def crear_todo(
    request: Request,
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return todo_service.create_todo(db, current_user, data)


@router.get(
    "",
    response_model=TodoPage,
    summary="Listar mis tareas",
    description=(
        "Lista paginada de las tareas del usuario con filtros y orden. "
        "`total` cuenta todas las tareas que cumplen los filtros y `data` nunca trae más "
        "elementos que `limit`. `search` busca en el título y la descripción. "
        "Límite: 60 peticiones por minuto."
    ),
    responses={401: R401, 403: R403_INACTIVO, 429: R429},
)
@limiter.limit("60/minute")
def listar_todos(
    request: Request,
    page: int = Query(1, ge=1, description="Número de página (mínimo 1)"),
    limit: int = Query(10, ge=1, le=50, description="Tareas por página (1 a 50)"),
    status: Optional[Status] = Query(None, description="Filtra por estado"),
    priority: Optional[Priority] = Query(None, description="Filtra por prioridad"),
    category_id: Optional[int] = Query(None, description="Filtra por categoría"),
    search: Optional[str] = Query(None, description="Texto a buscar en título y descripción"),
    due_before: Optional[datetime] = Query(
        None, description="Solo tareas con fecha límite anterior a esta fecha"
    ),
    sort_by: Literal["created_at", "due_date", "title", "priority"] = Query(
        "created_at", description="Campo de orden"
    ),
    order: Literal["asc", "desc"] = Query("desc", description="Sentido del orden"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    todos, total = todo_service.list_todos(
        db,
        current_user,
        page=page,
        limit=limit,
        status=status,
        priority=priority,
        category_id=category_id,
        search=search,
        due_before=due_before,
        sort_by=sort_by,
        order=order,
    )
    return TodoPage(
        data=[TodoResponse.model_validate(t) for t in todos],
        page=page,
        limit=limit,
        total=total,
    )


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Consultar una tarea",
    description="Devuelve una tarea propia con su categoría. 404 si no existe y 403 si es de otro usuario.",
    responses={401: R401, 403: R403, 404: R404_TAREA},
)
def obtener_todo(todo: Todo = Depends(get_owned_todo_or_404)):
    return todo


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Reemplazar una tarea",
    description=(
        "Reemplaza title, description, status, priority, due_date y category_id. "
        "Los campos opcionales que no se envíen quedan vacíos."
    ),
    responses={
        401: R401,
        403: R403,
        404: R404_TAREA,
        409: R409_CATEGORIA_AJENA,
    },
)
def reemplazar_todo(
    data: TodoReplace,
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return todo_service.replace_todo(db, todo, current_user, data)


@router.patch(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Actualizar parcialmente una tarea",
    description="Actualiza solo los campos enviados. Responde 400 si el cuerpo va vacío.",
    responses={
        400: R400_VACIO,
        401: R401,
        403: R403,
        404: R404_TAREA,
        409: R409_CATEGORIA_AJENA,
    },
)
def actualizar_todo(
    data: TodoUpdate,
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return todo_service.patch_todo(db, todo, current_user, data)


@router.delete(
    "/{todo_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Eliminar una tarea",
    description="Elimina una tarea propia. Responde 204 sin cuerpo.",
    responses={401: R401, 403: R403, 404: R404_TAREA},
)
def eliminar_todo(
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
):
    todo_service.delete_todo(db, todo)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
