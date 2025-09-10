"""
Database connection and session management.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator

from .settings import settings

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600,   # Recycle connections every hour
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base
Base = declarative_base()

def get_db_session() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI or other frameworks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Database session context manager for direct usage.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """
    Initialize database with extensions and tables.
    """
    from ..models import Base  # Import all models
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Enable extensions if needed
    if settings.TIMESCALEDB_ENABLED or settings.POSTGIS_ENABLED:
        with engine.connect() as conn:
            if settings.POSTGIS_ENABLED:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            if settings.TIMESCALEDB_ENABLED:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            conn.commit()