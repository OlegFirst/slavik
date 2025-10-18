"""
Projection Builder - CQRS Read Model Builder
============================================

Builds optimized read models (projections) from event streams.

Features:
- Denormalized read models
- Automatic event replay
- Multiple projection types
- Incremental updates
- Projection rebuilding

Projection Types:
1. **List Projections**: Optimized for queries (e.g., all BIA processes)
2. **Detail Projections**: Single entity details
3. **Summary Projections**: Aggregated statistics
4. **Index Projections**: Search/filter indexes

Architecture:
    Events → Projection Builder → Read Models (PostgreSQL/Redis)
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import asyncpg
from asyncpg import Pool

from .event_store import Event, EventStore

logger = logging.getLogger(__name__)


@dataclass
class Projection(ABC):
    """
    Base Projection class.

    Projections are denormalized read models optimized for queries.

    Attributes:
        projection_name: Unique projection name
        version: Current version (last event processed)
        enabled: Whether projection is active

    Example:
        ```python
        class BIAProcessListProjection(Projection):
            def __init__(self):
                super().__init__("bia_process_list")

            async def handle_event(self, event: Event, conn):
                if event.event_type == "BIAProcessCreated":
                    await conn.execute('''
                        INSERT INTO read_bia_processes (
                            id, tenant_id, name, criticality, rto_hours
                        ) VALUES ($1, $2, $3, $4, $5)
                    ''',
                        event.aggregate_id,
                        event.metadata.tenant_id,
                        event.data["name"],
                        event.data["criticality"],
                        event.data["rto_hours"]
                    )
        ```
    """

    projection_name: str
    version: int = 0
    enabled: bool = True

    @abstractmethod
    async def handle_event(self, event: Event, conn: asyncpg.Connection) -> None:
        """
        Handle event and update projection.

        Args:
            event: Event to process
            conn: Database connection
        """
        pass

    @abstractmethod
    async def ensure_schema(self, conn: asyncpg.Connection) -> None:
        """
        Create projection tables/indexes.

        Args:
            conn: Database connection
        """
        pass

    async def rebuild(self, event_store: EventStore, conn: asyncpg.Connection) -> None:
        """
        Rebuild projection from all events.

        Args:
            event_store: Event store for loading events
            conn: Database connection
        """
        logger.info(f"Rebuilding projection: {self.projection_name}")

        # Clear existing data
        await self.clear(conn)

        # Replay all events
        event_count = 0
        async for event in event_store.get_all_events():
            await self.handle_event(event, conn)
            event_count += 1

            if event_count % 1000 == 0:
                logger.info(f"Processed {event_count} events for {self.projection_name}")

        logger.info(
            f"Projection {self.projection_name} rebuilt with {event_count} events"
        )

    @abstractmethod
    async def clear(self, conn: asyncpg.Connection) -> None:
        """
        Clear projection data.

        Args:
            conn: Database connection
        """
        pass


class ProjectionBuilder:
    """
    Projection Builder.

    Manages multiple projections and keeps them updated.

    Example:
        ```python
        # Initialize
        builder = ProjectionBuilder(event_store, database_url)
        await builder.connect()

        # Register projections
        builder.register_projection(BIAProcessListProjection())
        builder.register_projection(BIAProcessSummaryProjection())

        # Ensure schemas
        await builder.ensure_schemas()

        # Start processing events
        await builder.start()

        # Or rebuild specific projection
        await builder.rebuild_projection("bia_process_list")
        ```
    """

    def __init__(
        self,
        event_store: EventStore,
        database_url: str
    ):
        """
        Initialize Projection Builder.

        Args:
            event_store: Event store for loading events
            database_url: PostgreSQL connection URL
        """
        self.event_store = event_store
        self.database_url = database_url
        self.pool: Optional[Pool] = None
        self.projections: Dict[str, Projection] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Connect to PostgreSQL."""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("Projection Builder connected to PostgreSQL")

    async def close(self) -> None:
        """Close connections."""
        # Stop processing
        await self.stop()

        # Close pool
        if self.pool:
            await self.pool.close()
            logger.info("Projection Builder connection closed")

    def register_projection(self, projection: Projection) -> None:
        """
        Register projection.

        Args:
            projection: Projection to register

        Example:
            ```python
            builder.register_projection(BIAProcessListProjection())
            ```
        """
        self.projections[projection.projection_name] = projection
        logger.info(f"Registered projection: {projection.projection_name}")

    async def ensure_schemas(self) -> None:
        """
        Create schemas for all projections.

        Call this during startup.
        """
        async with self.pool.acquire() as conn:
            # Create projection tracking table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cqrs_projection_state (
                    projection_name VARCHAR(255) PRIMARY KEY,
                    last_event_id BIGINT DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT NOW(),
                    enabled BOOLEAN DEFAULT TRUE
                )
            """)

            # Create schemas for each projection
            for projection in self.projections.values():
                await projection.ensure_schema(conn)

                # Initialize tracking
                await conn.execute("""
                    INSERT INTO cqrs_projection_state (projection_name, enabled)
                    VALUES ($1, $2)
                    ON CONFLICT (projection_name) DO NOTHING
                """, projection.projection_name, projection.enabled)

        logger.info(f"Projection schemas created for {len(self.projections)} projections")

    async def apply_event(
        self,
        event: Event,
        projection_names: Optional[List[str]] = None
    ) -> None:
        """
        Apply event to projections.

        Args:
            event: Event to apply
            projection_names: Specific projections (None = all)

        Example:
            ```python
            # Apply to all projections
            await builder.apply_event(event)

            # Apply to specific projection
            await builder.apply_event(event, ["bia_process_list"])
            ```
        """
        target_projections = (
            [self.projections[name] for name in projection_names]
            if projection_names
            else list(self.projections.values())
        )

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for projection in target_projections:
                    if not projection.enabled:
                        continue

                    try:
                        await projection.handle_event(event, conn)

                        # Update projection state
                        await conn.execute("""
                            UPDATE cqrs_projection_state
                            SET last_event_id = $1, last_updated = NOW()
                            WHERE projection_name = $2
                        """, event.version, projection.projection_name)

                    except Exception as e:
                        logger.error(
                            f"Error applying event {event.event_type} to "
                            f"projection {projection.projection_name}: {e}",
                            exc_info=True
                        )
                        raise

    async def rebuild_projection(self, projection_name: str) -> None:
        """
        Rebuild projection from scratch.

        Args:
            projection_name: Name of projection to rebuild

        Example:
            ```python
            await builder.rebuild_projection("bia_process_list")
            ```
        """
        projection = self.projections.get(projection_name)
        if not projection:
            raise ValueError(f"Projection not found: {projection_name}")

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await projection.rebuild(self.event_store, conn)

                # Reset projection state
                await conn.execute("""
                    UPDATE cqrs_projection_state
                    SET last_event_id = 0, last_updated = NOW()
                    WHERE projection_name = $1
                """, projection_name)

        logger.info(f"Projection {projection_name} rebuilt successfully")

    async def rebuild_all(self) -> None:
        """
        Rebuild all projections.

        Example:
            ```python
            await builder.rebuild_all()
            ```
        """
        for projection_name in self.projections.keys():
            await self.rebuild_projection(projection_name)

        logger.info("All projections rebuilt")

    async def start(self, poll_interval: float = 1.0) -> None:
        """
        Start projection update loop.

        Continuously processes new events.

        Args:
            poll_interval: Seconds between polls

        Example:
            ```python
            # Start in background
            await builder.start()
            ```
        """
        if self._running:
            logger.warning("Projection Builder already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._process_events_loop(poll_interval))
        logger.info("Projection Builder started")

    async def stop(self) -> None:
        """Stop projection update loop."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Projection Builder stopped")

    async def _process_events_loop(self, poll_interval: float) -> None:
        """Process events loop (internal)."""
        while self._running:
            try:
                # Get last processed event ID
                async with self.pool.acquire() as conn:
                    min_event_id = await conn.fetchval("""
                        SELECT MIN(last_event_id)
                        FROM cqrs_projection_state
                        WHERE enabled = TRUE
                    """)

                # Process new events
                event_count = 0
                async for event in self.event_store.get_all_events(
                    from_position=min_event_id or 0,
                    batch_size=100
                ):
                    await self.apply_event(event)
                    event_count += 1

                if event_count > 0:
                    logger.debug(f"Processed {event_count} new events")

                # Wait before next poll
                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error in projection processing loop: {e}", exc_info=True)
                await asyncio.sleep(poll_interval * 5)  # Wait longer on error

    async def get_projection_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all projections.

        Returns:
            List of projection status dictionaries

        Example:
            ```python
            status = await builder.get_projection_status()
            for proj in status:
                print(f"{proj['name']}: {proj['last_updated']}")
            ```
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT projection_name, last_event_id, last_updated, enabled
                FROM cqrs_projection_state
                ORDER BY projection_name
            """)

            return [
                {
                    "name": row["projection_name"],
                    "last_event_id": row["last_event_id"],
                    "last_updated": row["last_updated"],
                    "enabled": row["enabled"]
                }
                for row in rows
            ]


# Example Projections for BIA

class BIAProcessListProjection(Projection):
    """
    BIA Process List Projection.

    Optimized for listing BIA processes with filters.
    """

    def __init__(self):
        super().__init__()
        self.projection_name = "bia_process_list"

    async def ensure_schema(self, conn: asyncpg.Connection) -> None:
        """Create read model table."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS read_bia_processes (
                id VARCHAR(255) PRIMARY KEY,
                tenant_id VARCHAR(255) NOT NULL,
                name VARCHAR(500) NOT NULL,
                criticality VARCHAR(50) NOT NULL,
                rto_hours INTEGER NOT NULL,
                rpo_hours INTEGER NOT NULL,
                mtpd_hours INTEGER NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        # Indexes for performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_read_bia_tenant
            ON read_bia_processes(tenant_id)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_read_bia_criticality
            ON read_bia_processes(criticality)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_read_bia_status
            ON read_bia_processes(status)
        """)

    async def handle_event(self, event: Event, conn: asyncpg.Connection) -> None:
        """Handle BIA events."""
        if event.event_type == "BIAProcessCreated":
            await conn.execute("""
                INSERT INTO read_bia_processes (
                    id, tenant_id, name, criticality,
                    rto_hours, rpo_hours, mtpd_hours, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (id) DO NOTHING
            """,
                event.aggregate_id,
                event.metadata.tenant_id,
                event.data["name"],
                event.data["criticality"],
                event.data["rto_hours"],
                event.data["rpo_hours"],
                event.data["mtpd_hours"],
                event.data.get("status", "DRAFT")
            )

        elif event.event_type == "BIAProcessRTOUpdated":
            await conn.execute("""
                UPDATE read_bia_processes
                SET rto_hours = $1, rpo_hours = $2, updated_at = NOW()
                WHERE id = $3
            """,
                event.data["rto_hours"],
                event.data["rpo_hours"],
                event.aggregate_id
            )

        elif event.event_type == "BIAProcessCompleted":
            await conn.execute("""
                UPDATE read_bia_processes
                SET status = 'COMPLETED', updated_at = NOW()
                WHERE id = $1
            """, event.aggregate_id)

    async def clear(self, conn: asyncpg.Connection) -> None:
        """Clear projection data."""
        await conn.execute("TRUNCATE TABLE read_bia_processes")


class BIAProcessSummaryProjection(Projection):
    """
    BIA Process Summary Projection.

    Aggregated statistics per tenant.
    """

    def __init__(self):
        super().__init__()
        self.projection_name = "bia_process_summary"

    async def ensure_schema(self, conn: asyncpg.Connection) -> None:
        """Create summary table."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS read_bia_summary (
                tenant_id VARCHAR(255) PRIMARY KEY,
                total_processes INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0,
                high_count INTEGER DEFAULT 0,
                medium_count INTEGER DEFAULT 0,
                low_count INTEGER DEFAULT 0,
                completed_count INTEGER DEFAULT 0,
                draft_count INTEGER DEFAULT 0,
                avg_rto_hours FLOAT DEFAULT 0,
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

    async def handle_event(self, event: Event, conn: asyncpg.Connection) -> None:
        """Handle BIA events and update summary."""
        if event.event_type == "BIAProcessCreated":
            # Increment counts
            criticality = event.data["criticality"]
            status = event.data.get("status", "DRAFT")

            await conn.execute("""
                INSERT INTO read_bia_summary (tenant_id, total_processes)
                VALUES ($1, 1)
                ON CONFLICT (tenant_id)
                DO UPDATE SET
                    total_processes = read_bia_summary.total_processes + 1,
                    updated_at = NOW()
            """, event.metadata.tenant_id)

            # Update criticality count
            criticality_col = f"{criticality.lower()}_count"
            await conn.execute(f"""
                UPDATE read_bia_summary
                SET {criticality_col} = {criticality_col} + 1
                WHERE tenant_id = $1
            """, event.metadata.tenant_id)

            # Update status count
            status_col = f"{status.lower()}_count"
            await conn.execute(f"""
                UPDATE read_bia_summary
                SET {status_col} = {status_col} + 1
                WHERE tenant_id = $1
            """, event.metadata.tenant_id)

            # Recalculate average RTO
            await self._recalculate_avg_rto(conn, event.metadata.tenant_id)

        elif event.event_type == "BIAProcessCompleted":
            await conn.execute("""
                UPDATE read_bia_summary
                SET completed_count = completed_count + 1,
                    draft_count = draft_count - 1,
                    updated_at = NOW()
                WHERE tenant_id = $1
            """, event.metadata.tenant_id)

    async def _recalculate_avg_rto(
        self,
        conn: asyncpg.Connection,
        tenant_id: str
    ) -> None:
        """Recalculate average RTO for tenant."""
        avg_rto = await conn.fetchval("""
            SELECT AVG(rto_hours)
            FROM read_bia_processes
            WHERE tenant_id = $1
        """, tenant_id)

        if avg_rto:
            await conn.execute("""
                UPDATE read_bia_summary
                SET avg_rto_hours = $1, updated_at = NOW()
                WHERE tenant_id = $2
            """, float(avg_rto), tenant_id)

    async def clear(self, conn: asyncpg.Connection) -> None:
        """Clear projection data."""
        await conn.execute("TRUNCATE TABLE read_bia_summary")
