import uuid
from pathlib import Path
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

in_memory_db = "sqlite+pysqlite:///:memory:"

default_db_dir = "db"
default_db_filename = "providers.sqlite"
default_db_path = f"{default_db_dir}/{default_db_filename}"
default_db_uri = f"sqlite+pysqlite:///{default_db_path}"

if not Path(default_db_dir).exists():
    Path(default_db_dir).mkdir(parents=True, exist_ok=True)

SQLALCHEMY_DATABASE_URI = default_db_uri

## connect_args only necessary for SQLite database
engine = create_engine(
    SQLALCHEMY_DATABASE_URI, echo=True, connect_args={"check_same_thread": False}
)

SessionLocal = Session(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db(engine=engine) -> Session:
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        raise Exception(
            f"Unhandled exception getting DB connection. Exception details: {exc}"
        )
    finally:
        db.close()


def generate_uuid() -> uuid.UUID:
    """Generate a UUID. Return string if string=True."""
    _uuid = uuid.uuid4()

    return _uuid


def generate_uuid_str() -> str:
    _uuid = generate_uuid()

    return str(_uuid)
