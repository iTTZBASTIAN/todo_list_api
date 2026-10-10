from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Límite por dirección IP; los contadores viven en memoria
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """429 con el mismo formato de error del resto de la API (clave 'detail')."""
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
