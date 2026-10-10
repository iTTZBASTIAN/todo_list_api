# app/routes/admin_routes.py
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import require_admin
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.schemas.todo_schema import TodoAdminPage, TodoAdminResponse
from app.services import todo_service

router = APIRouter()  # Debe llamarse 'router'


@router.get("/todos", response_model=TodoAdminPage)
def listar_todos_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    owner_email: Optional[str] = None,
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
