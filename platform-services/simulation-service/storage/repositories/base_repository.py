"""
Base repository with common CRUD operations

Provides generic database operations with caching support.
"""

import logging
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from storage.database import DatabaseManager

logger = logging.getLogger(__name__)

T = TypeVar('T')  # ORM Model type
P = TypeVar('P')  # Pydantic Model type


class BaseRepository(Generic[T, P]):
    """
    Base repository with CRUD operations

    Provides:
    - CRUD operations
    - Caching with Redis
    - Pagination
    - Filtering
    """

    def __init__(
        self,
        db_manager: DatabaseManager,
        orm_model: Type[T],
        pydantic_model: Type[P],
        cache_prefix: str
    ):
        """
        Initialize repository

        Args:
            db_manager: Database manager instance
            orm_model: SQLAlchemy ORM model class
            pydantic_model: Pydantic model class
            cache_prefix: Redis key prefix for caching
        """
        self.db_manager = db_manager
        self.orm_model = orm_model
        self.pydantic_model = pydantic_model
        self.cache_prefix = cache_prefix

    def _cache_key(self, entity_id: str) -> str:
        """Generate cache key for entity"""
        return f"{self.cache_prefix}:{entity_id}"

    async def create(self, session: AsyncSession, entity: P) -> T:
        """
        Create new entity

        Args:
            session: Database session
            entity: Pydantic model instance

        Returns:
            ORM model instance
        """
        # Convert Pydantic to ORM
        entity_dict = entity.model_dump()

        # Handle metadata field name conversion
        if "metadata" in entity_dict:
            entity_dict["metadata_"] = entity_dict.pop("metadata")

        orm_entity = self.orm_model(**entity_dict)

        session.add(orm_entity)
        await session.flush()
        await session.refresh(orm_entity)

        # Cache the entity
        await self._cache_entity(orm_entity)

        logger.info(f"Created {self.orm_model.__name__}: {orm_entity.id}")
        return orm_entity

    async def get_by_id(self, session: AsyncSession, entity_id: str) -> Optional[T]:
        """
        Get entity by ID

        Args:
            session: Database session
            entity_id: Entity ID

        Returns:
            ORM model instance or None
        """
        # Try cache first
        cached = await self._get_cached(entity_id)
        if cached:
            return cached

        # Query database
        stmt = select(self.orm_model).where(self.orm_model.id == entity_id)
        result = await session.execute(stmt)
        orm_entity = result.scalar_one_or_none()

        if orm_entity:
            # Cache the entity
            await self._cache_entity(orm_entity)

        return orm_entity

    async def update(
        self,
        session: AsyncSession,
        entity_id: str,
        updates: Dict[str, Any]
    ) -> Optional[T]:
        """
        Update entity

        Args:
            session: Database session
            entity_id: Entity ID
            updates: Fields to update

        Returns:
            Updated ORM model instance or None
        """
        # Handle metadata field name
        if "metadata" in updates:
            updates["metadata_"] = updates.pop("metadata")

        stmt = (
            update(self.orm_model)
            .where(self.orm_model.id == entity_id)
            .values(**updates)
            .returning(self.orm_model)
        )

        result = await session.execute(stmt)
        orm_entity = result.scalar_one_or_none()

        if orm_entity:
            await session.refresh(orm_entity)

            # Invalidate cache
            await self._invalidate_cache(entity_id)

            # Re-cache
            await self._cache_entity(orm_entity)

            logger.info(f"Updated {self.orm_model.__name__}: {entity_id}")

        return orm_entity

    async def delete(self, session: AsyncSession, entity_id: str) -> bool:
        """
        Delete entity

        Args:
            session: Database session
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        stmt = delete(self.orm_model).where(self.orm_model.id == entity_id)
        result = await session.execute(stmt)

        deleted = result.rowcount > 0

        if deleted:
            # Invalidate cache
            await self._invalidate_cache(entity_id)
            logger.info(f"Deleted {self.orm_model.__name__}: {entity_id}")

        return deleted

    async def list_all(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """
        List all entities with pagination

        Args:
            session: Database session
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of ORM model instances
        """
        stmt = (
            select(self.orm_model)
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, session: AsyncSession) -> int:
        """
        Count total entities

        Args:
            session: Database session

        Returns:
            Total count
        """
        stmt = select(func.count()).select_from(self.orm_model)
        result = await session.execute(stmt)
        return result.scalar() or 0

    # Cache operations
    async def _cache_entity(self, orm_entity: T) -> None:
        """Cache entity in Redis"""
        try:
            # Convert to Pydantic and then to JSON
            entity_dict = {}
            for column in orm_entity.__table__.columns:
                column_name = column.name
                if column_name == "metadata":
                    entity_dict["metadata"] = getattr(orm_entity, "metadata_")
                else:
                    entity_dict[column_name] = getattr(orm_entity, column_name)

            pydantic_entity = self.pydantic_model(**entity_dict)
            json_str = pydantic_entity.model_dump_json()

            cache_key = self._cache_key(orm_entity.id)
            await self.db_manager.cache_set(cache_key, json_str)

        except Exception as e:
            logger.warning(f"Failed to cache entity: {e}")

    async def _get_cached(self, entity_id: str) -> Optional[T]:
        """Get entity from cache"""
        try:
            cache_key = self._cache_key(entity_id)
            json_str = await self.db_manager.cache_get(cache_key)

            if json_str:
                # Parse JSON to Pydantic, then convert to ORM
                pydantic_entity = self.pydantic_model.model_validate_json(json_str)
                entity_dict = pydantic_entity.model_dump()

                if "metadata" in entity_dict:
                    entity_dict["metadata_"] = entity_dict.pop("metadata")

                return self.orm_model(**entity_dict)

        except Exception as e:
            logger.warning(f"Failed to get cached entity: {e}")

        return None

    async def _invalidate_cache(self, entity_id: str) -> None:
        """Invalidate entity cache"""
        try:
            cache_key = self._cache_key(entity_id)
            await self.db_manager.cache_delete(cache_key)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache: {e}")
