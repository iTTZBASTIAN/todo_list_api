# app/routes/todo_routes.py
from fastapi import APIRouter

router = APIRouter()  # Debe llamarse 'router'


@router.get("/")
def listar_todos():
    return []
