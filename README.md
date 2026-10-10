# todo_list_api

API RESTful de lista de tareas con FastAPI. Cada usuario registrado gestiona
sus propias tareas. El proyecto se construye por fases (tags v0.1 a v1.0.0).

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración (.env)

Copia `.env.example` como `.env` y define una `SECRET_KEY` propia:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

El archivo `.env` no se sube al repositorio.

## Base de datos y migraciones (Alembic)

Las tablas las crean las migraciones, no la aplicación:

```bash
alembic upgrade head      # crea/actualiza las tablas
alembic current           # muestra la versión aplicada
alembic revision --autogenerate -m "mensaje"   # nueva migración tras cambiar un modelo
```

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Autenticación

| Endpoint | Acceso | Descripción |
|---|---|---|
| POST /auth/register | Público | Crea el usuario (201) y devuelve sus datos y el token |
| POST /auth/login | Público | Recibe correo (campo `username`) y contraseña; devuelve el token |
| GET /auth/me | Autenticado | Devuelve el usuario del token |

El token se envía en la cabecera `Authorization: Bearer <token>`.

Para probar el rol admin, promueve un usuario ya registrado:

```bash
python -m scripts.promover_admin correo@dominio.com
```

## Categorías y tareas

| Endpoint | Acceso | Éxito | Descripción |
|---|---|---|---|
| POST /categories | Autenticado | 201 | Crea una categoría propia (nombre único por usuario) |
| GET /categories | Autenticado | 200 | Lista las categorías propias |
| DELETE /categories/{id} | Dueño | 204 | Elimina la categoría; 409 si tiene tareas |
| POST /todos | Autenticado | 201 | Crea una tarea del usuario |
| GET /todos | Autenticado | 200 | Lista paginada con filtros y orden |
| GET /todos/{id} | Dueño | 200 | Consulta una tarea con su categoría |
| PUT /todos/{id} | Dueño | 200 | Reemplaza los campos de la tarea |
| PATCH /todos/{id} | Dueño | 200 | Actualiza solo los campos enviados (400 si va vacío) |
| DELETE /todos/{id} | Dueño | 204 | Elimina la tarea |
| GET /admin/todos | Solo admin | 200 | Tareas de todos los usuarios con datos del dueño |

Parámetros de `GET /todos`: `page`, `limit` (1 a 50), `status`, `priority`,
`category_id`, `search`, `due_before`, `sort_by` (`created_at`, `due_date`,
`title`, `priority`) y `order` (`asc`, `desc`).

## Seguridad: middleware, CORS y límite de peticiones

- Cada respuesta incluye `X-Request-ID`, `X-Process-Time` y `X-App-Name: todo_list_api`,
  y la consola registra método, ruta y código de cada petición.
- CORS permitido solo para `http://localhost:5173` y `http://localhost:3000`.
- Límites por IP (slowapi), con respuesta 429 `Rate limit exceeded`:

| Ruta | Límite |
|---|---|
| POST /auth/login | 5 por minuto |
| POST /auth/register | 3 por minuto |
| POST /todos | 20 por minuto |
| GET /todos | 60 por minuto |
