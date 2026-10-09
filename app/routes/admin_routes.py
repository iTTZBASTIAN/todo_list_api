# app/routes/admin_routes.py
from fastapi import APIRouter

router = APIRouter()  # Debe llamarse 'router'


@router.get("/todos")
def listar_todos_admin():
    return []
