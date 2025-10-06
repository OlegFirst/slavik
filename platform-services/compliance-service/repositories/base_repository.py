"""
Base Repository for Compliance Module
"""

from typing import Optional, Generic, TypeVar, Type, List
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class ConcurrencyError(Exception):
    """Raised when optimistic lock fails due to concurrent modification"""
    pass


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations"""

    def __init__(self, db: AsyncSession, model_class: Type[T]):
        self.db = db
        self.model_class = model_class

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID"""
        result = await self.db.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, tenant_id: str, limit: int = 100) -> List[T]:
        """Get all entities for tenant"""
        result = await self.db.execute(
            select(self.model_class)
            .where(self.model_class.tenant_id == tenant_id)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        """Create new entity"""
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_status(
        self,
        id: UUID,
        status: str,
        expected_version: Optional[int] = None
    ) -> Optional[T]:
        """
        Update entity status with optimistic locking.

        Args:
            id: Entity ID
            status: New status
            expected_version: Expected version (for concurrency control)

        Returns:
            Updated entity or None if not found

        Raises:
            ConcurrencyError: If version mismatch (concurrent modification detected)
        """
        # Build update statement with version increment
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == id)
            .values(status=status, version=self.model_class.version + 1)
        )

        # Add version check if provided
        if expected_version is not None:
            stmt = stmt.where(self.model_class.version == expected_version)

        result = await self.db.execute(stmt)

        # Check if update was successful
        if result.rowcount == 0:
            # Either entity not found OR version mismatch
            existing = await self.get_by_id(id)
            if existing and expected_version is not None:
                raise ConcurrencyError(
                    f"Entity {id} was modified by another user. "
                    f"Expected version {expected_version}, got {existing.version}"
                )
            return None

        await self.db.commit()
        return await self.get_by_id(id)

    async def update_field(self, id: UUID, field_name: str, value) -> Optional[T]:
        """Update single field"""
        await self.db.execute(
            update(self.model_class)
            .where(self.model_class.id == id)
            .values(**{field_name: value})
        )
        await self.db.commit()
        return await self.get_by_id(id)

    async def delete(self, id: UUID) -> bool:
        """Delete entity"""
        result = await self.db.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def create_audit_log(
        self,
        entity_id: UUID,
        action: str,
        changed_by: str,
        changes: dict
    ):
        """Create audit log entry"""
        # TODO: Implement when AuditLog model is ready
        import logging
        logging.info(f"Audit: {action} on {entity_id} by {changed_by}")
