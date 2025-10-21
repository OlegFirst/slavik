#!/usr/bin/env python3
"""
Database initialization and session management for MIO Manager
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import logging

from models.database import Base

logger = logging.getLogger(__name__)


# Database URL
DATABASE_URL = "sqlite:///./mio_manager.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Only for SQLite
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """
    Initialize database - create all tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(" Database initialized successfully")
    except Exception as e:
        logger.error(f" Failed to initialize database: {e}")
        raise


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Get database session (context manager)

    Usage:
        with get_db() as db:
            db.add(...)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (manual management)

    Usage:
        db = get_db_session()
        try:
            db.add(...)
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()
