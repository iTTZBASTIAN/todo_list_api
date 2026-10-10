# todo_list_api

API REST de tareas con FastAPI y SQLAlchemy.

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

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

Documentación interactiva en http://127.0.0.1:8000/docs
