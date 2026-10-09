# todo_list_api

API RESTful de lista de tareas con FastAPI. Cada usuario registrado gestiona
sus propias tareas. El proyecto se construye por fases (tags v0.1 a v1.0.0).

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
