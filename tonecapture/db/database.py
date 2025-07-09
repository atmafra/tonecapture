"""tonecapture.db.database"""

import re

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from tonecapture.db.exceptions import DatabaseError, DuplicateRecordError
from tonecapture.db.models import Base

SQLALCHEMY_DATABASE_URL = (
    "sqlite:////home/amafra/projects/lab/tonecapture/data/tonecapture.db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes the database and creates tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Returns a new database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _handle_database_error(e: Exception) -> Exception:
    """
    Maps a database exception to a custom application exception.
    """
    if isinstance(e, IntegrityError):
        match = re.search(r"UNIQUE constraint failed: (\w+)\.(\w+)", str(e))
        if match:
            model_name, field = match.groups()
            return DuplicateRecordError(model_name.capitalize(), field, "Unknown")
        return DuplicateRecordError()
    if isinstance(e, SQLAlchemyError):
        return DatabaseError(f"A database error occurred: {e}")
    return e


def _handle_database_read_error(e: Exception) -> Exception:
    """
    Maps a database read exception to a custom application exception.
    """
    if isinstance(e, SQLAlchemyError):
        return DatabaseError(f"A database read error occurred: {e}")
    return e
