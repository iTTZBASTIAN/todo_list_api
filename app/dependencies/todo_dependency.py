from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.models import category_model, user_model  # noqa: F401
from app.models.todo_model import Todo
from app.models.user_model import User


def get_owned_todo_or_404(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Todo:
    """Busca la tarea: 404 si no existe, 403 si pertenece a otro usuario."""
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    if todo.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return todo
