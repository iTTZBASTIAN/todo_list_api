from fastapi import FastAPI

# Importar los modelos para que Alembic y SQLAlchemy los registren.
# Las tablas ya NO se crean aquí: las crean las migraciones (alembic upgrade head).
from app.models import user_model, category_model, todo_model  # noqa: F401

# Importar los routers
from app.auth import auth_routes
from app.routes import category_routes, todo_routes, admin_routes

app = FastAPI(
    title="Todo List API",
    description="API REST modular con FastAPI y SQLAlchemy",
    version="1.0.0"
)

# Incluir los routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Autenticación"])
app.include_router(todo_routes.router, prefix="/todos", tags=["Tareas"])
app.include_router(category_routes.router, prefix="/categories", tags=["Categorías"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Administración"])

@app.get("/")
def root():
    return {"mensaje": "API ejecutándose correctamente"}
