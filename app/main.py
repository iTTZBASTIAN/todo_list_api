from fastapi import FastAPI

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
