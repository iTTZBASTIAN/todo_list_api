from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexión (SQLite creará el archivo todo_list.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo_list.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


# SQLite no respeta las claves foráneas por defecto: se activan en cada conexión
@event.listens_for(engine, "connect")
def _activar_claves_foraneas(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
