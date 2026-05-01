import logging
from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Using relative import if possible, but standard is absolute in FastAPI
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_recycle=300,
    pool_size=settings.DB_MAX_CONNECTIONS,
    max_overflow=20,
    echo=settings.DB_ECHO,
    connect_args={
        "connect_timeout": settings.DB_TIMEOUT,
        "application_name": settings.APP_NAME
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency function to get database session for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_sync_db_session() -> Generator[Session, None, None]:
    """Context manager to get synchronous database session."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database sync session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
