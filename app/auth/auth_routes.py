# app/auth/auth_routes.py
from fastapi import APIRouter

# Crear la instancia del router (¡debe llamarse 'router'!)
router = APIRouter()

@router.post("/login")
def login():
    return {"mensaje": "Inicio de sesión"}