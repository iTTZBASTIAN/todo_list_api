# app/routes/todo_routes.py
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, Response, status as http_status
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.dependencies.todo_dependency import get_owned_todo_or_404
from app.models.todo_model import Todo
from app.models.user_model import User
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


@router.post("", response_model=TodoResponse, status_code=http_status.HTTP_201_CREATED)
def crear_todo(
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return todo_service.create_todo(db, current_user, data)


@router.get("", response_model=TodoPage)
def listar_todos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    status: Optional[Status] = None,
    priority: Optional[Priority] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    due_before: Optional[datetime] = None,
    sort_by: Literal["created_at", "due_date", "title", "priority"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
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


@router.get("/{todo_id}", response_model=TodoResponse)
def obtener_todo(todo: Todo = Depends(get_owned_todo_or_404)):
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def reemplazar_todo(
    data: TodoReplace,
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return todo_service.replace_todo(db, todo, current_user, data)


@router.patch("/{todo_id}", response_model=TodoResponse)
def actualizar_todo(
    data: TodoUpdate,
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return todo_service.patch_todo(db, todo, current_user, data)


@router.delete("/{todo_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def eliminar_todo(
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
):
    todo_service.delete_todo(db, todo)
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
