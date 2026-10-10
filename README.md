# todo_list_api

API RESTful de lista de tareas construida con FastAPI. Cada usuario registrado
gestiona **sus propias** tareas: puede crearlas, consultarlas, actualizarlas y
eliminarlas, organizarlas en categorías, y listarlas con paginación, filtros y orden.
Incluye autenticación con JWT, un rol `admin`, middleware, CORS y límite de peticiones.

## Tecnologías

Python, FastAPI, Uvicorn, SQLAlchemy 2, Alembic, Pydantic v2, passlib (bcrypt),
python-jose (JWT), slowapi y SQLite.

## Estructura del proyecto

```
todo_list_api/
│── app/
│   │── main.py
│   │── auth/            (auth_routes.py, auth_service.py, security.py)
│   │── database/        (connection.py)
│   │── models/          (user_model.py, category_model.py, todo_model.py)
│   │── schemas/         (auth_schema.py, user_schema.py, category_schema.py, todo_schema.py, error_schema.py)
│   │── routes/          (category_routes.py, todo_routes.py, admin_routes.py)
│   │── services/        (category_service.py, todo_service.py)
│   │── dependencies/    (database_dependency.py, auth_dependency.py, todo_dependency.py)
│   │── middlewares/     (request_middleware.py, rate_limit.py)
│── alembic/versions/
│── scripts/             (promover_admin.py)
│── alembic.ini
│── .env.example
│── requirements.txt
│── README.md
```

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Variables de entorno

Copia `.env.example` como `.env` (el archivo `.env` no se sube al repositorio).

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SECRET_KEY` | Clave con la que se firman los JWT. Genera una propia | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | Algoritmo de firma del JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de vida del token | `30` |

## Base de datos y migraciones

Las tablas las crean las migraciones, no la aplicación:

```bash
alembic upgrade head      # crea las tablas users, categories y todos
alembic current           # versión aplicada
alembic history           # historial de migraciones
```

Si cambias un modelo: `alembic revision --autogenerate -m "mensaje"` y luego `alembic upgrade head`.

## Ejecución

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Para probar el rol admin, promueve un usuario ya registrado y vuelve a iniciar sesión:

```bash
python -m scripts.promover_admin correo@dominio.com
```

## Endpoints

| Método y ruta | Acceso | Éxito | Errores posibles |
|---|---|---|---|
| POST /auth/register | Público | 201 | 400 correo repetido, 422 datos inválidos, 429 |
| POST /auth/login | Público | 200 | 401 credenciales incorrectas, 403 usuario inactivo, 429 |
| GET /auth/me | Autenticado | 200 | 401, 403 |
| POST /categories | Autenticado | 201 | 401, 403, 409 nombre repetido, 422 |
| GET /categories | Autenticado | 200 | 401, 403 |
| DELETE /categories/{id} | Dueño | 204 | 401, 403, 404, 409 tiene tareas |
| POST /todos | Autenticado | 201 | 401, 403, 404 categoría inexistente, 409 categoría ajena, 422, 429 |
| GET /todos | Autenticado | 200 | 401, 403, 422, 429 |
| GET /todos/{id} | Dueño | 200 | 401, 403, 404 |
| PUT /todos/{id} | Dueño | 200 | 401, 403, 404, 409, 422 |
| PATCH /todos/{id} | Dueño | 200 | 400 cuerpo vacío, 401, 403, 404, 409, 422 |
| DELETE /todos/{id} | Dueño | 204 | 401, 403, 404 |
| GET /admin/todos | Solo admin | 200 | 401, 403 |

El token viaja en la cabecera `Authorization: Bearer <token>`.

Parámetros de `GET /todos`: `page` (mínimo 1), `limit` (1 a 50), `status`, `priority`,
`category_id`, `search` (título y descripción), `due_before`, `sort_by`
(`created_at`, `due_date`, `title`, `priority`) y `order` (`asc`, `desc`).

Límites de peticiones por IP: login 5 por minuto, register 3, `POST /todos` 20 y `GET /todos` 60.

**401 y 403:** 401 significa que el servidor no sabe quién eres (sin token, inválido o vencido);
403 significa que sabe quién eres y no tienes permiso (tarea de otro usuario, usuario inactivo o ruta de admin).

## Pruebas funcionales

Ejecutadas en Swagger UI. Cada captura muestra el código de estado.

**1. Ejecutar `alembic upgrade head` sobre una base vacía** — esperado: Se crean users, categories y todos

![Prueba 1](docs/capturas/prueba-01.png)

**2. Registrar usuario válido** — esperado: 201 y la BD guarda el hash, no la clave

![Prueba 2](docs/capturas/prueba-02.png)

**3. Registrar con contraseña débil** — esperado: 422

![Prueba 3](docs/capturas/prueba-03.png)

**4. Registrar con correo duplicado** — esperado: 400

![Prueba 4](docs/capturas/prueba-04.png)

**5. Login correcto e incorrecto** — esperado: 200 con token; 401 con clave errónea

![Prueba 5](docs/capturas/prueba-05.png)

**6. GET /auth/me con y sin token** — esperado: 200 sin hashed_password; 401

![Prueba 6](docs/capturas/prueba-06.png)

**7. POST /todos con token** — esperado: 201 con owner_id del usuario

![Prueba 7](docs/capturas/prueba-07.png)

**8. POST /todos sin token o con token alterado** — esperado: 401

![Prueba 8](docs/capturas/prueba-08.png)

**9. GET /todos?page=1&limit=2 con 5 tareas** — esperado: 2 elementos, total 5

![Prueba 9](docs/capturas/prueba-09.png)

**10. GET /todos con status, priority, search y sort_by** — esperado: Solo tareas que cumplen los filtros, en el orden pedido

![Prueba 10](docs/capturas/prueba-10.png)

**11. GET /todos/{id} de un ID inexistente** — esperado: 404

![Prueba 11](docs/capturas/prueba-11.png)

**12. PUT y DELETE sobre una tarea de otro usuario** — esperado: 403

![Prueba 12](docs/capturas/prueba-12.png)

**13. PUT completo y PATCH parcial sobre una tarea propia** — esperado: 200 con datos actualizados

![Prueba 13](docs/capturas/prueba-13.png)

**14. PATCH con cuerpo vacío** — esperado: 400

![Prueba 14](docs/capturas/prueba-14.png)

**15. DELETE de tarea propia y GET posterior** — esperado: 204 y luego 404

![Prueba 15](docs/capturas/prueba-15.png)

**16. GET /admin/todos con usuario user y con admin** — esperado: 403 y 200 con datos del dueño

![Prueba 16](docs/capturas/prueba-16.png)

**17. Cabeceras del middleware** — esperado: X-Request-ID, X-Process-Time y X-App-Name presentes

![Prueba 17](docs/capturas/prueba-17.png)

**18. Preflight CORS desde localhost:5173 y desde otro origen** — esperado: Permitido; el otro origen no recibe Access-Control-Allow-Origin

![Prueba 18](docs/capturas/prueba-18.png)

**19. Seis logins seguidos en un minuto** — esperado: El sexto responde 429

![Prueba 19](docs/capturas/prueba-19.png)

**20. /docs y /redoc** — esperado: Tags, botón Authorize con OAuth2, modelos y códigos de respuesta

![Prueba 20](docs/capturas/prueba-20.png)

### Evidencias adicionales

**Historial de migraciones (`alembic history`)**

![alembic history](docs/capturas/alembic-history.png)

**Tablas en la base de datos**

![Tablas](docs/capturas/tablas-bd.png)

**Swagger con el botón Authorize**

![Swagger Authorize](docs/capturas/swagger-authorize.png)

## Decisiones de diseño

**1. Modelo SQLAlchemy y schema Pydantic son distintos.**
El modelo describe la tabla: columnas, restricciones y relaciones, e incluye `hashed_password`.
El schema describe lo que entra y sale por la API y valida los datos. Mantenerlos separados
evita exponer campos internos (los schemas de salida no incluyen `hashed_password`), permite
una forma distinta para crear, reemplazar y actualizar, y desacopla la API de la base de datos.
`ConfigDict(from_attributes=True)` convierte un objeto del modelo en su schema de salida.

**2. Uso de `Depends()`.**
Las funciones reutilizables se inyectan con `Depends()`: la sesión de base de datos (`get_db`),
el usuario del token (`get_current_user`), el usuario activo (`get_current_active_user`) y el
rol admin (`require_admin`), encadenadas entre sí. `get_owned_todo_or_404` busca la tarea,
responde 404 si no existe y 403 si es de otro usuario, y la reutilizan GET, PUT, PATCH y DELETE
en lugar de repetir la regla en cada ruta. FastAPI además comparte la misma sesión dentro de
una petición.

**3. Por qué no se usa `"*"` en CORS cuando hay credenciales.**
El estándar CORS no permite responder `Access-Control-Allow-Origin: *` cuando la petición lleva
credenciales, y los navegadores la rechazan. Además, permitir cualquier origen dejaría que
cualquier sitio web hiciera peticiones desde el navegador de un usuario autenticado. Por eso
la API lista de forma explícita los orígenes permitidos: `http://localhost:5173` y
`http://localhost:3000`.

## Control de versiones (Git Flow)

| Rama | Uso |
|---|---|
| `main` | Solo versiones estables; aquí se crea el tag `v1.0.0` |
| `develop` | Integración de todas las fases |
| `feature/*` | Una rama por fase, integrada en `develop` con `--no-ff` |
| `release/1.0.0` | Ajustes finales, integrada en `main` y `develop` |

| Tag | Fase |
|---|---|
| v0.1 | F1. Configuración |
| v0.2 | F2. Persistencia y migraciones |
| v0.3 | F3. Schemas y validaciones |
| v0.4 | F4. Autenticación y roles |
| v0.5 | F5. CRUD, paginación y filtros |
| v0.6 | F6. Middleware, CORS y rate limiting |
| v1.0.0 | Versión final (en `main`) |

## Reflexión final

> **Escribe aquí tu reflexión con tus propias palabras.** Algunas preguntas que pueden guiarla:
> ¿Qué fue lo más difícil de diseñar la autenticación? ¿Qué diferencia viste entre un 401 y un 403
> al probar la API? ¿Qué error te enseñó más y cómo lo resolviste? ¿Qué harías distinto en una
> próxima API?
