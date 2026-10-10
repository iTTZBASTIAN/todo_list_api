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

DESCRIPCION = """
API RESTful de lista de tareas. Cada usuario registrado gestiona **sus propias** tareas.

* Autenticación con **JWT**: regístrate en `/auth/register` o inicia sesión en
  `/auth/login` y usa el botón **Authorize** para enviar el token.
* Las tareas se pueden **filtrar, ordenar y paginar**.
* Las rutas de `/admin` solo están disponibles para usuarios con rol `admin`.
* Códigos clave: **401** si no hay token válido, **403** si no tienes permiso,
  **404** si el recurso no existe y **429** si superas el límite de peticiones.
"""

TAGS_METADATA = [
    {"name": "Auth", "description": "Registro, inicio de sesión y datos del usuario autenticado."},
    {"name": "Categories", "description": "Categorías propias para organizar las tareas."},
    {"name": "Todos", "description": "CRUD de tareas del usuario, con paginación, filtros y orden."},
    {"name": "Admin", "description": "Consultas exclusivas del rol admin."},
]

app = FastAPI(
    title="Todo List API",
    description=DESCRIPCION,
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
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
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(todo_routes.router, prefix="/todos", tags=["Todos"])
app.include_router(category_routes.router, prefix="/categories", tags=["Categories"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])

@app.get("/", summary="Estado de la API", description="Comprueba que la API está en ejecución.")
def root():
    return {"mensaje": "API ejecutándose correctamente"}
