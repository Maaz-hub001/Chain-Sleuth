"""
Database session and connection management supporting PostgreSQL and SQLite.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes database tables."""
    try:
        logger.info(f"Initializing database at: {settings.DATABASE_URL}")
        # Import all models before create_all so metadata is populated
        import app.models.investigation  # noqa: F401
        import app.models.transaction  # noqa: F401
        import app.models.graph  # noqa: F401
        import app.models.finding  # noqa: F401
        import app.models.evidence  # noqa: F401
        import app.models.intelligence  # noqa: F401
        import app.models.report  # noqa: F401

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
