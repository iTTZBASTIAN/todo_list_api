import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

APP_NAME = "todo_list_api"

# Logger propio: uvicorn solo configura sus loggers, así que se le da un handler
logger = logging.getLogger("todo_list_api.request")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


class RequestMiddleware(BaseHTTPMiddleware):
    """Añade X-Request-ID, X-Process-Time y X-App-Name a cada respuesta
    y registra método, ruta y código de estado de cada petición."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        inicio = time.perf_counter()

        response = await call_next(request)

        duracion = time.perf_counter() - inicio
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duracion:.4f}"
        response.headers["X-App-Name"] = APP_NAME

        logger.info(
            "%s %s -> %s (%.1f ms) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            duracion * 1000,
            request_id,
        )
        return response
