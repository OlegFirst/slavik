"""
Database Session Utilities
===========================

Additional session management utilities.
"""

from typing import AsyncGenerator, TypeVar, Type, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions.custom import ResourceNotFoundException

T = TypeVar("T")


async def get_or_404(
    db: AsyncSession,
    model: Type[T],
    id_value: int,
    id_field: str = "id"
) -> T:
    """
    Get object by ID or raise 404 exception.

    Args:
        db: Database session
        model: SQLAlchemy model class
        id_value: ID value to search for
        id_field: Name of ID field (default: "id")

    Returns:
        Model instance

    Raises:
        ResourceNotFoundException: If object not found

    Example:
        ```python
        user = await get_or_404(db, User, user_id)
        ```
    """
    stmt = select(model).where(getattr(model, id_field) == id_value)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()

    if obj is None:
        raise ResourceNotFoundException(
            f"{model.__name__} with {id_field}={id_value} not found"
        )

    return obj


async def commit_or_rollback(db: AsyncSession) -> None:
    """
    Commit transaction or rollback on error.

    Args:
        db: Database session

    Example:
        ```python
        try:
            db.add(user)
            await commit_or_rollback(db)
        except Exception as e:
            logger.error(f"Failed to save user: {e}")
            raise
        ```
    """
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
