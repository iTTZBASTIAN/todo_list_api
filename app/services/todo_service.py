from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status as http_status
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.models.category_model import Category
from app.models.todo_model import Todo
from app.models.user_model import User
from app.schemas.todo_schema import TodoCreate, TodoReplace, TodoUpdate


# ---------------- utilidades ----------------

def _comprobar_categoria(db: Session, category_id: Optional[int], user: User) -> None:
    """La categoría debe existir (404) y ser del usuario (409)."""
    if category_id is None:
        return
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    if category.user_id != user.id:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="La categoría no pertenece al usuario",
        )


def _escapar_like(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _filtros(
    user_id: int,
    status: Optional[str],
    priority: Optional[str],
    category_id: Optional[int],
    search: Optional[str],
    due_before: Optional[datetime],
) -> list:
    filtros = [Todo.owner_id == user_id]
    if status is not None:
        filtros.append(Todo.status == status)
    if priority is not None:
        filtros.append(Todo.priority == priority)
    if category_id is not None:
        filtros.append(Todo.category_id == category_id)
    if search and search.strip():
        patron = f"%{_escapar_like(search.strip())}%"
        filtros.append(
            or_(
                Todo.title.ilike(patron, escape="\\"),
                Todo.description.ilike(patron, escape="\\"),
            )
        )
    if due_before is not None:
        filtros.append(Todo.due_date < due_before)
    return filtros


def _orden(sort_by: str, order: str) -> list:
    if sort_by == "priority":
        # low < medium < high (orden por importancia, no alfabético)
        columna = case(
            (Todo.priority == "low", 1),
            (Todo.priority == "medium", 2),
            (Todo.priority == "high", 3),
            else_=0,
        )
    elif sort_by == "title":
        columna = func.lower(Todo.title)
    elif sort_by == "due_date":
        columna = Todo.due_date
    else:
        columna = Todo.created_at

    descendente = order == "desc"
    direccion = columna.desc() if descendente else columna.asc()
    desempate = Todo.id.desc() if descendente else Todo.id.asc()

    if sort_by == "due_date":
        # las tareas sin fecha límite siempre quedan al final
        return [Todo.due_date.is_(None), direccion, desempate]
    return [direccion, desempate]


# ---------------- consultas ----------------

def list_todos(
    db: Session,
    user: User,
    *,
    page: int,
    limit: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    due_before: Optional[datetime] = None,
    sort_by: str = "created_at",
    order: str = "desc",
) -> tuple[list[Todo], int]:
    """Tareas del usuario con filtros, orden y paginación. Devuelve (tareas de la página, total)."""
    filtros = _filtros(user.id, status, priority, category_id, search, due_before)

    total = db.scalar(select(func.count()).select_from(Todo).where(*filtros)) or 0

    stmt = (
        select(Todo)
        .options(joinedload(Todo.category))
        .where(*filtros)
        .order_by(*_orden(sort_by, order))
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return list(db.scalars(stmt).all()), total


def list_todos_admin(
    db: Session,
    *,
    page: int,
    limit: int,
    owner_email: Optional[str] = None,
) -> tuple[list[Todo], int]:
    """Tareas de todos los usuarios con los datos del dueño (join con users)."""
    filtros = []
    if owner_email and owner_email.strip():
        filtros.append(User.email == owner_email.strip().lower())

    count_stmt = select(func.count()).select_from(Todo).join(Todo.owner)
    stmt = (
        select(Todo)
        .join(Todo.owner)
        .options(contains_eager(Todo.owner), joinedload(Todo.category))
    )
    if filtros:
        count_stmt = count_stmt.where(*filtros)
        stmt = stmt.where(*filtros)

    total = db.scalar(count_stmt) or 0
    stmt = (
        stmt.order_by(Todo.created_at.desc(), Todo.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return list(db.scalars(stmt).all()), total


# ---------------- escritura ----------------

def create_todo(db: Session, user: User, data: TodoCreate) -> Todo:
    _comprobar_categoria(db, data.category_id, user)
    todo = Todo(**data.model_dump(), owner_id=user.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def replace_todo(db: Session, todo: Todo, user: User, data: TodoReplace) -> Todo:
    """PUT: reemplaza todos los campos editables."""
    _comprobar_categoria(db, data.category_id, user)
    for campo, valor in data.model_dump().items():
        setattr(todo, campo, valor)
    db.commit()
    db.refresh(todo)
    return todo


def patch_todo(db: Session, todo: Todo, user: User, data: TodoUpdate) -> Todo:
    """PATCH: actualiza solo los campos enviados; 400 si el cuerpo va vacío."""
    cambios = data.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )
    for campo in ("title", "status", "priority"):
        if campo in cambios and cambios[campo] is None:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El campo {campo} no puede ser nulo",
            )

    _comprobar_categoria(db, cambios.get("category_id"), user)
    for campo, valor in cambios.items():
        setattr(todo, campo, valor)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()
