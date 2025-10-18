"""
Event Store - Event Sourcing Storage
=====================================

PostgreSQL-based event store for CQRS architecture.

Features:
- Persistent event storage
- Event versioning
- Aggregate stream management
- Event replay capability
- Snapshot support
- Optimistic concurrency control

Event Stream:
    All events for an aggregate are stored in a stream identified by:
    - aggregate_type: Type of aggregate (e.g., "BIAProcess")
    - aggregate_id: Unique identifier for the aggregate
    - version: Sequential version number for ordering
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncIterator
from uuid import uuid4
import asyncpg
from asyncpg import Pool

logger = logging.getLogger(__name__)


@dataclass
class EventMetadata:
    """
    Event metadata.

    Contains information about the event context.
    """
    tenant_id: str
    user_id: str = "system"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventMetadata':
        """Create from dictionary."""
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class Event:
    """
    Domain Event.

    Represents something that happened in the domain.

    Example:
        ```python
        event = Event(
            event_id="evt_123",
            event_type="BIAProcessCreated",
            aggregate_type="BIAProcess",
            aggregate_id="bia_456",
            version=1,
            data={
                "name": "Payment Processing",
                "criticality": "CRITICAL",
                "rto_hours": 2
            },
            metadata=EventMetadata(
                tenant_id="tenant_123",
                user_id="user_456"
            )
        )
        ```
    """
    event_id: str = field(default_factory=lambda: f"evt_{uuid4().hex}")
    event_type: str = ""
    aggregate_type: str = ""
    aggregate_id: str = ""
    version: int = 1
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: EventMetadata = field(default_factory=lambda: EventMetadata(tenant_id=""))
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "version": self.version,
            "data": self.data,
            "metadata": self.metadata.to_dict(),
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        metadata = EventMetadata.from_dict(data.get('metadata', {}))
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            event_id=data['event_id'],
            event_type=data['event_type'],
            aggregate_type=data['aggregate_type'],
            aggregate_id=data['aggregate_id'],
            version=data['version'],
            data=data.get('data', {}),
            metadata=metadata,
            created_at=created_at or datetime.utcnow()
        )


class EventStore:
    """
    PostgreSQL-based Event Store.

    Stores domain events with optimistic concurrency control.

    Example:
        ```python
        # Initialize
        event_store = EventStore(database_url)
        await event_store.connect()
        await event_store.ensure_schema()

        # Save event
        event = Event(
            event_type="BIAProcessCreated",
            aggregate_type="BIAProcess",
            aggregate_id="bia_123",
            version=1,
            data={"name": "Critical Process"},
            metadata=EventMetadata(tenant_id="tenant_123")
        )
        await event_store.save_event(event)

        # Load events
        events = await event_store.get_events("BIAProcess", "bia_123")

        # Get all events since position
        all_events = await event_store.get_all_events(from_position=100)
        ```
    """

    def __init__(self, database_url: str):
        """
        Initialize Event Store.

        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.pool: Optional[Pool] = None

    async def connect(self) -> None:
        """Connect to PostgreSQL."""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("Event Store connected to PostgreSQL")

    async def close(self) -> None:
        """Close PostgreSQL connection."""
        if self.pool:
            await self.pool.close()
            logger.info("Event Store connection closed")

    async def ensure_schema(self) -> None:
        """
        Create event store schema.

        Creates:
        - events table: Main event storage
        - snapshots table: Aggregate snapshots for faster loading
        """
        async with self.pool.acquire() as conn:
            # Events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cqrs_events (
                    id BIGSERIAL PRIMARY KEY,
                    event_id VARCHAR(255) UNIQUE NOT NULL,
                    event_type VARCHAR(255) NOT NULL,
                    aggregate_type VARCHAR(255) NOT NULL,
                    aggregate_id VARCHAR(255) NOT NULL,
                    version INTEGER NOT NULL,
                    data JSONB NOT NULL,
                    metadata JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

                    -- Optimistic concurrency control
                    UNIQUE(aggregate_type, aggregate_id, version)
                )
            """)

            # Indexes for performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_aggregate
                ON cqrs_events(aggregate_type, aggregate_id, version)
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_type
                ON cqrs_events(event_type)
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_tenant
                ON cqrs_events((metadata->>'tenant_id'))
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_created
                ON cqrs_events(created_at DESC)
            """)

            # Snapshots table for aggregate state caching
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cqrs_snapshots (
                    id BIGSERIAL PRIMARY KEY,
                    aggregate_type VARCHAR(255) NOT NULL,
                    aggregate_id VARCHAR(255) NOT NULL,
                    version INTEGER NOT NULL,
                    state JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

                    UNIQUE(aggregate_type, aggregate_id)
                )
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_snapshots_aggregate
                ON cqrs_snapshots(aggregate_type, aggregate_id)
            """)

            logger.info("Event Store schema created")

    async def save_event(
        self,
        event: Event,
        expected_version: Optional[int] = None
    ) -> Event:
        """
        Save event to store.

        Args:
            event: Event to save
            expected_version: Expected current version (for optimistic locking)

        Returns:
            Saved event with assigned ID

        Raises:
            ConcurrencyError: If version conflict detected

        Example:
            ```python
            # Save first event
            event1 = Event(
                event_type="BIAProcessCreated",
                aggregate_type="BIAProcess",
                aggregate_id="bia_123",
                version=1,
                data={"name": "Process"}
            )
            await event_store.save_event(event1)

            # Save next event with version check
            event2 = Event(
                event_type="BIAProcessUpdated",
                aggregate_type="BIAProcess",
                aggregate_id="bia_123",
                version=2,
                data={"rto_hours": 4}
            )
            await event_store.save_event(event2, expected_version=1)
            ```
        """
        async with self.pool.acquire() as conn:
            # Optimistic concurrency check
            if expected_version is not None:
                current_version = await conn.fetchval("""
                    SELECT MAX(version)
                    FROM cqrs_events
                    WHERE aggregate_type = $1 AND aggregate_id = $2
                """, event.aggregate_type, event.aggregate_id)

                if current_version and current_version != expected_version:
                    raise ConcurrencyError(
                        f"Version conflict: expected {expected_version}, "
                        f"but current is {current_version}"
                    )

            try:
                await conn.execute("""
                    INSERT INTO cqrs_events (
                        event_id, event_type, aggregate_type, aggregate_id,
                        version, data, metadata, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                    event.event_id,
                    event.event_type,
                    event.aggregate_type,
                    event.aggregate_id,
                    event.version,
                    json.dumps(event.data),
                    json.dumps(event.metadata.to_dict()),
                    event.created_at
                )

                logger.debug(
                    f"Event saved: {event.event_type} for "
                    f"{event.aggregate_type}/{event.aggregate_id} v{event.version}"
                )

                return event

            except asyncpg.UniqueViolationError as e:
                if "aggregate_type, aggregate_id, version" in str(e):
                    raise ConcurrencyError(
                        f"Event version {event.version} already exists for "
                        f"{event.aggregate_type}/{event.aggregate_id}"
                    )
                raise

    async def save_events(
        self,
        events: List[Event],
        expected_version: Optional[int] = None
    ) -> List[Event]:
        """
        Save multiple events atomically.

        Args:
            events: List of events to save
            expected_version: Expected current version before saving

        Returns:
            List of saved events

        Example:
            ```python
            events = [
                Event(event_type="Created", version=1, ...),
                Event(event_type="Updated", version=2, ...),
                Event(event_type="Completed", version=3, ...)
            ]
            await event_store.save_events(events, expected_version=0)
            ```
        """
        if not events:
            return []

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Optimistic concurrency check
                if expected_version is not None:
                    aggregate_type = events[0].aggregate_type
                    aggregate_id = events[0].aggregate_id

                    current_version = await conn.fetchval("""
                        SELECT MAX(version)
                        FROM cqrs_events
                        WHERE aggregate_type = $1 AND aggregate_id = $2
                    """, aggregate_type, aggregate_id)

                    if current_version and current_version != expected_version:
                        raise ConcurrencyError(
                            f"Version conflict: expected {expected_version}, "
                            f"but current is {current_version}"
                        )

                # Insert all events
                for event in events:
                    await conn.execute("""
                        INSERT INTO cqrs_events (
                            event_id, event_type, aggregate_type, aggregate_id,
                            version, data, metadata, created_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                        event.event_id,
                        event.event_type,
                        event.aggregate_type,
                        event.aggregate_id,
                        event.version,
                        json.dumps(event.data),
                        json.dumps(event.metadata.to_dict()),
                        event.created_at
                    )

                logger.info(f"Saved {len(events)} events atomically")
                return events

    async def get_events(
        self,
        aggregate_type: str,
        aggregate_id: str,
        from_version: int = 1,
        to_version: Optional[int] = None
    ) -> List[Event]:
        """
        Get events for an aggregate.

        Args:
            aggregate_type: Type of aggregate (e.g., "BIAProcess")
            aggregate_id: Aggregate identifier
            from_version: Start version (inclusive, default: 1)
            to_version: End version (inclusive, default: latest)

        Returns:
            List of events ordered by version

        Example:
            ```python
            # Get all events
            events = await event_store.get_events("BIAProcess", "bia_123")

            # Get events from version 5 onwards
            recent = await event_store.get_events("BIAProcess", "bia_123", from_version=5)

            # Get events in range
            range_events = await event_store.get_events(
                "BIAProcess", "bia_123",
                from_version=5,
                to_version=10
            )
            ```
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT event_id, event_type, aggregate_type, aggregate_id,
                       version, data, metadata, created_at
                FROM cqrs_events
                WHERE aggregate_type = $1 AND aggregate_id = $2
                  AND version >= $3
            """
            params = [aggregate_type, aggregate_id, from_version]

            if to_version:
                query += " AND version <= $4"
                params.append(to_version)

            query += " ORDER BY version ASC"

            rows = await conn.fetch(query, *params)

            events = []
            for row in rows:
                event = Event(
                    event_id=row['event_id'],
                    event_type=row['event_type'],
                    aggregate_type=row['aggregate_type'],
                    aggregate_id=row['aggregate_id'],
                    version=row['version'],
                    data=json.loads(row['data']) if isinstance(row['data'], str) else row['data'],
                    metadata=EventMetadata.from_dict(
                        json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                    ),
                    created_at=row['created_at']
                )
                events.append(event)

            return events

    async def get_all_events(
        self,
        from_position: int = 0,
        batch_size: int = 1000,
        event_types: Optional[List[str]] = None
    ) -> AsyncIterator[Event]:
        """
        Get all events from a position.

        Used for rebuilding projections.

        Args:
            from_position: Start position (event ID)
            batch_size: Number of events per batch
            event_types: Filter by event types (optional)

        Yields:
            Events in order of creation

        Example:
            ```python
            # Replay all events
            async for event in event_store.get_all_events():
                await projection_builder.apply_event(event)

            # Replay from position 1000
            async for event in event_store.get_all_events(from_position=1000):
                await projection_builder.apply_event(event)

            # Replay specific event types
            async for event in event_store.get_all_events(
                event_types=["BIAProcessCreated", "BIAProcessUpdated"]
            ):
                await projection_builder.apply_event(event)
            ```
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT event_id, event_type, aggregate_type, aggregate_id,
                       version, data, metadata, created_at
                FROM cqrs_events
                WHERE id > $1
            """
            params = [from_position]

            if event_types:
                query += " AND event_type = ANY($2)"
                params.append(event_types)

            query += " ORDER BY id ASC LIMIT $" + str(len(params) + 1)
            params.append(batch_size)

            current_position = from_position

            while True:
                params[0] = current_position
                rows = await conn.fetch(query, *params)

                if not rows:
                    break

                for row in rows:
                    event = Event(
                        event_id=row['event_id'],
                        event_type=row['event_type'],
                        aggregate_type=row['aggregate_type'],
                        aggregate_id=row['aggregate_id'],
                        version=row['version'],
                        data=json.loads(row['data']) if isinstance(row['data'], str) else row['data'],
                        metadata=EventMetadata.from_dict(
                            json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                        ),
                        created_at=row['created_at']
                    )
                    yield event
                    current_position = max(current_position, row['id'])

                if len(rows) < batch_size:
                    break

    async def save_snapshot(
        self,
        aggregate_type: str,
        aggregate_id: str,
        version: int,
        state: Dict[str, Any]
    ) -> None:
        """
        Save aggregate snapshot.

        Snapshots allow faster aggregate loading by avoiding full event replay.

        Args:
            aggregate_type: Type of aggregate
            aggregate_id: Aggregate identifier
            version: Snapshot version
            state: Aggregate state

        Example:
            ```python
            # After processing 100 events, save snapshot
            await event_store.save_snapshot(
                "BIAProcess",
                "bia_123",
                version=100,
                state={
                    "name": "Payment Processing",
                    "criticality": "CRITICAL",
                    "rto_hours": 2
                }
            )
            ```
        """
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO cqrs_snapshots (aggregate_type, aggregate_id, version, state)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (aggregate_type, aggregate_id)
                DO UPDATE SET version = $3, state = $4, created_at = NOW()
            """,
                aggregate_type,
                aggregate_id,
                version,
                json.dumps(state)
            )

            logger.debug(
                f"Snapshot saved: {aggregate_type}/{aggregate_id} v{version}"
            )

    async def get_snapshot(
        self,
        aggregate_type: str,
        aggregate_id: str
    ) -> Optional[tuple[int, Dict[str, Any]]]:
        """
        Get latest snapshot for aggregate.

        Returns:
            Tuple of (version, state) or None if no snapshot

        Example:
            ```python
            snapshot = await event_store.get_snapshot("BIAProcess", "bia_123")
            if snapshot:
                version, state = snapshot
                # Load events after snapshot version
                events = await event_store.get_events(
                    "BIAProcess", "bia_123",
                    from_version=version + 1
                )
            ```
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT version, state
                FROM cqrs_snapshots
                WHERE aggregate_type = $1 AND aggregate_id = $2
            """, aggregate_type, aggregate_id)

            if row:
                state = json.loads(row['state']) if isinstance(row['state'], str) else row['state']
                return (row['version'], state)

            return None

    async def get_latest_version(
        self,
        aggregate_type: str,
        aggregate_id: str
    ) -> int:
        """
        Get latest version for aggregate.

        Returns:
            Latest version number (0 if aggregate doesn't exist)

        Example:
            ```python
            current_version = await event_store.get_latest_version(
                "BIAProcess", "bia_123"
            )
            # Use for optimistic concurrency
            await event_store.save_event(event, expected_version=current_version)
            ```
        """
        async with self.pool.acquire() as conn:
            version = await conn.fetchval("""
                SELECT MAX(version)
                FROM cqrs_events
                WHERE aggregate_type = $1 AND aggregate_id = $2
            """, aggregate_type, aggregate_id)

            return version or 0


class ConcurrencyError(Exception):
    """Raised when optimistic concurrency check fails."""
    pass
