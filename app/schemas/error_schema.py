from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Formato de todos los errores de la API (HTTPException)."""

    detail: str


def _error(descripcion: str) -> dict:
    return {"model": ErrorResponse, "description": descripcion}


# Respuestas reutilizables para documentar los códigos de estado en /docs
R400_EMAIL = _error("El correo ya está registrado")
R400_VACIO = _error("Debe enviar al menos un campo para actualizar")
R401 = _error("Token ausente, inválido o vencido (Unauthorized)")
R401_LOGIN = _error("Correo o contraseña incorrectos")
R403_INACTIVO = _error("Usuario inactivo")
R403 = _error("Usuario inactivo, o el recurso pertenece a otro usuario (Forbidden)")
R403_ADMIN = _error("Usuario inactivo o sin rol admin (Forbidden)")
R404_TAREA = _error("Tarea no encontrada")
R404_CATEGORIA = _error("Categoría no encontrada")
R409_NOMBRE = _error("Ya existe una categoría con ese nombre")
R409_CATEGORIA_TAREAS = _error("La categoría tiene tareas asociadas")
R409_CATEGORIA_AJENA = _error("La categoría no pertenece al usuario")
R429 = _error("Límite de peticiones superado (Rate limit exceeded)")
