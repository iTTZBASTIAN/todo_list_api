from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

Status = Literal["pending", "in_progress", "done"]
Priority = Literal["low", "medium", "high"]


def _fecha_no_pasada(due_date: Optional[datetime]) -> None:
    if due_date is not None and due_date.date() < date.today():
        raise ValueError("due_date no puede ser anterior a hoy")


# ---------- Entrada ----------

class TodoCreate(BaseModel):
    """POST /todos"""

    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Status = "pending"
    priority: Priority = "medium"
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

    @model_validator(mode="after")
    def validar_fecha(self):
        _fecha_no_pasada(self.due_date)
        return self


class TodoReplace(BaseModel):
    """PUT /todos/{id}: reemplaza todos los campos.

    title, status y priority son obligatorios; description, due_date y
    category_id que no se envíen quedan en None.
    """

    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Status
    priority: Priority
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

    @model_validator(mode="after")
    def validar_fecha(self):
        _fecha_no_pasada(self.due_date)
        return self


class TodoUpdate(BaseModel):
    """PATCH /todos/{id}: solo los campos enviados.

    Un cuerpo vacío debe responder 400 en la ruta o el service
    (se detecta con model_dump(exclude_unset=True)).
    """

    title: Optional[str] = Field(default=None, min_length=3, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

    @model_validator(mode="after")
    def validar_fecha(self):
        _fecha_no_pasada(self.due_date)
        return self


# ---------- Salida ----------

class CategoryInTodo(BaseModel):
    """Categoría anidada dentro de una tarea."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: Status
    priority: Priority
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryInTodo] = None


class TodoPage(BaseModel):
    """Respuesta paginada de GET /todos."""

    data: list[TodoResponse]
    page: int
    limit: int
    total: int


class OwnerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class TodoAdminResponse(TodoResponse):
    """Tarea con los datos de su dueño (GET /admin/todos)."""

    owner: OwnerInfo


class TodoAdminPage(BaseModel):
    data: list[TodoAdminResponse]
    page: int
    limit: int
    total: int
