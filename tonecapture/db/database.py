"""tonecapture.db.database"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tonecapture.db.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:////home/amafra/projects/lab/tonecapture/data/tonecapture.db"

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
