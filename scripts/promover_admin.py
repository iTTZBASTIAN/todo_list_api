"""Promueve a administrador a un usuario ya registrado.

Uso (desde la raíz del proyecto, con el venv activo):
    python -m scripts.promover_admin correo@dominio.com
"""
import sys

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models import category_model, todo_model  # noqa: F401
from app.models.user_model import User


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python -m scripts.promover_admin correo@dominio.com")
        sys.exit(1)

    email = sys.argv[1].lower()
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            print(f"No existe un usuario con el correo {email}")
            sys.exit(1)
        user.role = "admin"
        db.commit()
        print(f"{email} ahora tiene el rol admin")
    finally:
        db.close()


if __name__ == "__main__":
    main()
