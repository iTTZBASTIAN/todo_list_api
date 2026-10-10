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
