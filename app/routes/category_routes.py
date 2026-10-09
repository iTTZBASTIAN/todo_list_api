# app/routes/category_routes.py
from fastapi import APIRouter

router = APIRouter()  # Debe llamarse 'router'


@router.get("/")
def listar_categorias():
    return []
