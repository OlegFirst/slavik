"""
SQLAlchemy Base Model
=====================

Base declarative model for all database models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All database models should inherit from this class.

    Example:
        ```python
        from shared.database.base import Base
        from sqlalchemy import Column, Integer, String

        class User(Base):
            __tablename__ = "users"

            id = Column(Integer, primary_key=True)
            email = Column(String, unique=True, nullable=False)
        ```
    """
    pass
