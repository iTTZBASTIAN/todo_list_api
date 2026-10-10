from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

# Importar los modelos para que Alembic y SQLAlchemy los registren.
# Las tablas ya NO se crean aquí: las crean las migraciones (alembic upgrade head).
from app.models import user_model, category_model, todo_model  # noqa: F401

# Importar los routers
from app.auth import auth_routes
from app.routes import category_routes, todo_routes, admin_routes

# Middlewares y límite de peticiones
from app.middlewares.rate_limit import limiter, rate_limit_exceeded_handler
from app.middlewares.request_middleware import RequestMiddleware

app = FastAPI(
    title="Todo List API",
    description="API REST modular con FastAPI y SQLAlchemy",
    version="1.0.0"
)

# Límite de peticiones (slowapi): los límites se declaran en cada ruta con @limiter.limit
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS: solo los frontends de desarrollo permitidos
ORIGENES_PERMITIDOS = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time", "X-App-Name"],
)

# Se agrega al final para quedar como capa más externa:
# así sus cabeceras llegan también a las respuestas de CORS y a los errores 429
app.add_middleware(RequestMiddleware)

# Incluir los routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Autenticación"])
app.include_router(todo_routes.router, prefix="/todos", tags=["Tareas"])
app.include_router(category_routes.router, prefix="/categories", tags=["Categorías"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Administración"])

@app.get("/")
def root():
    return {"mensaje": "API ejecutándose correctamente"}
