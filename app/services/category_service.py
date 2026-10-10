from fastapi import HTTPException, status as http_status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category_model import Category
from app.models.todo_model import Todo
from app.models.user_model import User
from app.schemas.category_schema import CategoryCreate


def list_categories(db: Session, user: User) -> list[Category]:
    """Categorías del usuario, ordenadas por nombre."""
    stmt = select(Category).where(Category.user_id == user.id).order_by(Category.name, Category.id)
    return list(db.scalars(stmt).all())


def create_category(db: Session, user: User, data: CategoryCreate) -> Category:
    """Crea una categoría propia. El nombre es único por usuario (sin distinguir mayúsculas)."""
    name = data.name.strip()
    if not name:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El nombre no puede estar vacío",
        )

    existente = db.scalar(
        select(Category).where(
            Category.user_id == user.id,
            func.lower(Category.name) == name.lower(),
        )
    )
    if existente is not None:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Ya existe una categoría con ese nombre",
        )

    category = Category(name=name, user_id=user.id)
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Ya existe una categoría con ese nombre",
        )
    db.refresh(category)
    return category


def delete_category(db: Session, user: User, category_id: int) -> None:
    """404 si no existe, 403 si es de otro usuario, 409 si aún tiene tareas."""
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    if category.user_id != user.id:
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Forbidden")

    tareas = db.scalar(
        select(func.count()).select_from(Todo).where(Todo.category_id == category_id)
    )
    if tareas:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="La categoría tiene tareas asociadas",
        )

    db.delete(category)
    db.commit()
