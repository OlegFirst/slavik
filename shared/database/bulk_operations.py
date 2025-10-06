"""
Database Bulk Operations Utilities

Optimized bulk database operations for high-performance batch processing:
- Bulk inserts using bulk_insert_mappings
- Bulk updates using bulk_update_mappings
- Batch commit strategies
- Connection pooling configuration
"""

import logging
from typing import List, Dict, Any, Optional, Type, TypeVar
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DeclarativeBase)


class BulkDatabaseOperations:
    """
    Optimized bulk database operations with batching and connection pooling.

    Provides high-performance batch operations for large datasets.
    """

    def __init__(
        self,
        session: AsyncSession,
        batch_size: int = 100,
        commit_interval: int = 500
    ):
        """
        Initialize bulk operations handler.

        Args:
            session: SQLAlchemy async session
            batch_size: Number of records to process per batch (default: 100)
            commit_interval: Commit every N records (default: 500)
        """
        self.session = session
        self.batch_size = batch_size
        self.commit_interval = commit_interval
        self._operation_count = 0

    async def bulk_insert(
        self,
        model_class: Type[T],
        data: List[Dict[str, Any]],
        return_defaults: bool = False
    ) -> int:
        """
        Bulk insert records using bulk_insert_mappings for maximum performance.

        Args:
            model_class: SQLAlchemy model class
            data: List of dicts with record data
            return_defaults: Whether to return database defaults (slower)

        Returns:
            Number of records inserted

        Example:
            await bulk_ops.bulk_insert(
                BIAProcessModel,
                [
                    {"name": "Process 1", "tenant_id": "t1"},
                    {"name": "Process 2", "tenant_id": "t1"}
                ]
            )
        """
        if not data:
            return 0

        total_inserted = 0

        # Process in batches
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]

            # Use bulk_insert_mappings for performance
            await self.session.run_sync(
                lambda sync_session: sync_session.bulk_insert_mappings(
                    model_class,
                    batch,
                    return_defaults=return_defaults
                )
            )

            total_inserted += len(batch)
            self._operation_count += len(batch)

            # Commit at intervals
            if self._operation_count >= self.commit_interval:
                await self.session.commit()
                self._operation_count = 0
                logger.debug(f"Committed batch: {total_inserted} records inserted so far")

        # Final commit
        if self._operation_count > 0:
            await self.session.commit()
            self._operation_count = 0

        logger.info(f"Bulk insert completed: {total_inserted} records inserted")
        return total_inserted

    async def bulk_update(
        self,
        model_class: Type[T],
        data: List[Dict[str, Any]],
        id_field: str = "id"
    ) -> int:
        """
        Bulk update records using bulk_update_mappings.

        Each dict in data must contain the id_field to identify the record.

        Args:
            model_class: SQLAlchemy model class
            data: List of dicts with update data (must include id_field)
            id_field: Name of the primary key field (default: "id")

        Returns:
            Number of records updated

        Example:
            await bulk_ops.bulk_update(
                BIAProcessModel,
                [
                    {"id": 1, "rto_hours": 4},
                    {"id": 2, "rto_hours": 8}
                ]
            )
        """
        if not data:
            return 0

        # Validate all records have id_field
        for record in data:
            if id_field not in record:
                raise ValueError(f"All records must have '{id_field}' field for bulk update")

        total_updated = 0

        # Process in batches
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]

            # Use bulk_update_mappings for performance
            await self.session.run_sync(
                lambda sync_session: sync_session.bulk_update_mappings(
                    model_class,
                    batch
                )
            )

            total_updated += len(batch)
            self._operation_count += len(batch)

            # Commit at intervals
            if self._operation_count >= self.commit_interval:
                await self.session.commit()
                self._operation_count = 0
                logger.debug(f"Committed batch: {total_updated} records updated so far")

        # Final commit
        if self._operation_count > 0:
            await self.session.commit()
            self._operation_count = 0

        logger.info(f"Bulk update completed: {total_updated} records updated")
        return total_updated

    async def bulk_delete(
        self,
        model_class: Type[T],
        ids: List[Any],
        id_field: str = "id"
    ) -> int:
        """
        Bulk delete records by IDs.

        Args:
            model_class: SQLAlchemy model class
            ids: List of IDs to delete
            id_field: Name of the primary key field (default: "id")

        Returns:
            Number of records deleted

        Example:
            await bulk_ops.bulk_delete(BIAProcessModel, [1, 2, 3, 4, 5])
        """
        if not ids:
            return 0

        total_deleted = 0

        # Process in batches
        for i in range(0, len(ids), self.batch_size):
            batch_ids = ids[i:i + self.batch_size]

            # Build delete statement
            stmt = delete(model_class).where(
                getattr(model_class, id_field).in_(batch_ids)
            )

            result = await self.session.execute(stmt)
            batch_deleted = result.rowcount

            total_deleted += batch_deleted
            self._operation_count += batch_deleted

            # Commit at intervals
            if self._operation_count >= self.commit_interval:
                await self.session.commit()
                self._operation_count = 0
                logger.debug(f"Committed batch: {total_deleted} records deleted so far")

        # Final commit
        if self._operation_count > 0:
            await self.session.commit()
            self._operation_count = 0

        logger.info(f"Bulk delete completed: {total_deleted} records deleted")
        return total_deleted

    async def bulk_upsert(
        self,
        model_class: Type[T],
        data: List[Dict[str, Any]],
        unique_fields: List[str],
        update_fields: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        Bulk upsert (insert or update) records.

        If record with unique_fields exists, update it. Otherwise, insert.

        Args:
            model_class: SQLAlchemy model class
            data: List of dicts with record data
            unique_fields: Fields to check for uniqueness
            update_fields: Fields to update on conflict (None = all fields)

        Returns:
            Dict with counts: {"inserted": N, "updated": M}

        Note: This is a simplified implementation. For production use with
        PostgreSQL, consider using ON CONFLICT DO UPDATE.
        """
        if not data:
            return {"inserted": 0, "updated": 0}

        inserted_count = 0
        updated_count = 0

        # Process in batches
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]

            for record in batch:
                # Build filter for unique fields
                filters = [
                    getattr(model_class, field) == record[field]
                    for field in unique_fields
                ]

                # Check if record exists
                stmt = select(model_class).where(*filters)
                result = await self.session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing record
                    update_data = {
                        field: record[field]
                        for field in (update_fields or record.keys())
                        if field in record and field not in unique_fields
                    }

                    for field, value in update_data.items():
                        setattr(existing, field, value)

                    updated_count += 1
                else:
                    # Insert new record
                    new_record = model_class(**record)
                    self.session.add(new_record)
                    inserted_count += 1

            # Commit at intervals
            if (inserted_count + updated_count) % self.commit_interval == 0:
                await self.session.commit()
                logger.debug(
                    f"Committed batch: {inserted_count} inserted, {updated_count} updated"
                )

        # Final commit
        await self.session.commit()

        logger.info(
            f"Bulk upsert completed: {inserted_count} inserted, {updated_count} updated"
        )

        return {"inserted": inserted_count, "updated": updated_count}


@asynccontextmanager
async def bulk_operation_context(
    session: AsyncSession,
    batch_size: int = 100,
    commit_interval: int = 500
):
    """
    Context manager for bulk database operations.

    Ensures proper cleanup and commit on exit.

    Args:
        session: SQLAlchemy async session
        batch_size: Batch size for operations
        commit_interval: Commit interval

    Yields:
        BulkDatabaseOperations instance

    Example:
        async with bulk_operation_context(session) as bulk_ops:
            await bulk_ops.bulk_insert(Model, data)
    """
    bulk_ops = BulkDatabaseOperations(
        session=session,
        batch_size=batch_size,
        commit_interval=commit_interval
    )

    try:
        yield bulk_ops
    finally:
        # Ensure final commit
        if bulk_ops._operation_count > 0:
            await session.commit()
            logger.debug("Final commit on context exit")


# ==================== CONNECTION POOL CONFIGURATION ====================

def get_optimized_pool_config(
    max_concurrent_operations: int = 10,
    max_overflow: int = 20
) -> Dict[str, Any]:
    """
    Get optimized connection pool configuration for bulk operations.

    Args:
        max_concurrent_operations: Expected max concurrent operations
        max_overflow: Max overflow connections beyond pool size

    Returns:
        Dict of SQLAlchemy pool configuration

    Example:
        engine = create_async_engine(
            database_url,
            **get_optimized_pool_config(max_concurrent_operations=20)
        )
    """
    # Pool size should be at least equal to max concurrent operations
    pool_size = max(max_concurrent_operations, 10)

    return {
        "pool_size": pool_size,
        "max_overflow": max_overflow,
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 3600,   # Recycle connections after 1 hour
        "echo_pool": False,      # Don't log pool events
        "pool_timeout": 30,      # Timeout waiting for connection (seconds)
    }


# ==================== BATCH PROCESSING HELPERS ====================

def calculate_optimal_batch_size(
    total_records: int,
    max_concurrency: int,
    target_batch_time_ms: int = 1000
) -> int:
    """
    Calculate optimal batch size for bulk operations.

    Args:
        total_records: Total number of records to process
        max_concurrency: Maximum concurrent operations
        target_batch_time_ms: Target time per batch in milliseconds

    Returns:
        Optimal batch size

    Example:
        batch_size = calculate_optimal_batch_size(
            total_records=10000,
            max_concurrency=10,
            target_batch_time_ms=1000
        )
    """
    # Heuristic: aim for batches that complete within target time
    # Assuming ~10ms per record for simple operations
    records_per_batch = target_batch_time_ms // 10

    # Ensure at least max_concurrency batches for parallelization
    min_batch_size = total_records // (max_concurrency * 2)

    # Clamp between reasonable values
    batch_size = max(min(records_per_batch, 1000), max(min_batch_size, 10))

    logger.debug(
        f"Calculated optimal batch size: {batch_size} "
        f"(total={total_records}, concurrency={max_concurrency})"
    )

    return batch_size
