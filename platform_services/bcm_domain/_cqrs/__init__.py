"""
CQRS (Command Query Responsibility Segregation) Infrastructure
===============================================================

Complete CQRS implementation for BCM Domain services.

Features:
- Event Sourcing with Event Store
- Command/Query Separation
- Optimized Read Models (Projections)
- Event-Driven Architecture
- Saga Pattern Support
- Event Replay and Projection Rebuilding

Components:
- CommandHandler: Handles write operations, generates events
- QueryHandler: Handles read operations from optimized projections
- EventStore: Persistent event storage with PostgreSQL
- ProjectionBuilder: Creates denormalized read models
- ReadModelUpdater: Updates projections in real-time

Usage Example:
    ```python
    from _cqrs import CommandHandler, QueryHandler, EventStore
    from _cqrs import init_cqrs, get_command_handler, get_query_handler

    # Initialize at startup
    await init_cqrs(database_url, eventbus_client)

    # Use in service
    command_handler = get_command_handler()
    query_handler = get_query_handler()

    # Execute command (write)
    result = await command_handler.handle(CreateBIACommand(...))

    # Execute query (read)
    processes = await query_handler.handle(GetBIAProcessesQuery(...))
    ```

Architecture:

    Command Side (Write):
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   Command   │───>│   Handler   │───>│  Aggregate  │
    └─────────────┘    └─────────────┘    └─────────────┘
                                                  │
                                                  v
                                          ┌─────────────┐
                                          │   Events    │
                                          └─────────────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                    v                           v
                            ┌─────────────┐           ┌─────────────┐
                            │ Event Store │           │  EventBus   │
                            └─────────────┘           └─────────────┘

    Query Side (Read):
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │    Query    │───>│   Handler   │───>│  Read Model │
    └─────────────┘    └─────────────┘    └─────────────┘
                                                  ^
                                                  │
                                          ┌─────────────┐
                                          │ Projection  │
                                          │  Builder    │
                                          └─────────────┘
                                                  ^
                                                  │
                                          ┌─────────────┐
                                          │   Events    │
                                          └─────────────┘
"""

from typing import Optional
from .command_handler import CommandHandler, Command
from .query_handler import QueryHandler, Query
from .event_store import EventStore, Event, EventMetadata
from .projection_builder import ProjectionBuilder, Projection
from .read_model_updater import ReadModelUpdater, ReadModelConfig

# Global instances
_command_handler: Optional[CommandHandler] = None
_query_handler: Optional[QueryHandler] = None
_event_store: Optional[EventStore] = None
_projection_builder: Optional[ProjectionBuilder] = None
_read_model_updater: Optional[ReadModelUpdater] = None


async def init_cqrs(
    database_url: str,
    eventbus_client=None,
    redis_url: str = "redis://localhost:6379/0"
) -> tuple[CommandHandler, QueryHandler]:
    """
    Initialize CQRS infrastructure.

    Args:
        database_url: PostgreSQL connection URL
        eventbus_client: EventBus client for publishing events
        redis_url: Redis URL for caching read models

    Returns:
        Tuple of (CommandHandler, QueryHandler)

    Example:
        ```python
        @app.on_event("startup")
        async def startup():
            cmd_handler, query_handler = await init_cqrs(
                database_url=settings.DATABASE_URL,
                eventbus_client=get_eventbus(),
                redis_url=settings.REDIS_URL
            )
        ```
    """
    global _command_handler, _query_handler, _event_store
    global _projection_builder, _read_model_updater

    # Initialize Event Store
    _event_store = EventStore(database_url)
    await _event_store.connect()
    await _event_store.ensure_schema()

    # Initialize Projection Builder
    _projection_builder = ProjectionBuilder(
        event_store=_event_store,
        database_url=database_url
    )
    await _projection_builder.connect()

    # Initialize Read Model Updater
    _read_model_updater = ReadModelUpdater(
        event_store=_event_store,
        projection_builder=_projection_builder,
        redis_url=redis_url
    )
    await _read_model_updater.connect()

    # Initialize Command Handler
    _command_handler = CommandHandler(
        event_store=_event_store,
        eventbus_client=eventbus_client
    )

    # Initialize Query Handler
    _query_handler = QueryHandler(
        projection_builder=_projection_builder,
        redis_url=redis_url
    )

    return _command_handler, _query_handler


def get_command_handler() -> CommandHandler:
    """Get global CommandHandler instance."""
    if _command_handler is None:
        raise RuntimeError("CQRS not initialized. Call init_cqrs() during startup.")
    return _command_handler


def get_query_handler() -> QueryHandler:
    """Get global QueryHandler instance."""
    if _query_handler is None:
        raise RuntimeError("CQRS not initialized. Call init_cqrs() during startup.")
    return _query_handler


def get_event_store() -> EventStore:
    """Get global EventStore instance."""
    if _event_store is None:
        raise RuntimeError("CQRS not initialized. Call init_cqrs() during startup.")
    return _event_store


def get_projection_builder() -> ProjectionBuilder:
    """Get global ProjectionBuilder instance."""
    if _projection_builder is None:
        raise RuntimeError("CQRS not initialized. Call init_cqrs() during startup.")
    return _projection_builder


def get_read_model_updater() -> ReadModelUpdater:
    """Get global ReadModelUpdater instance."""
    if _read_model_updater is None:
        raise RuntimeError("CQRS not initialized. Call init_cqrs() during startup.")
    return _read_model_updater


async def shutdown_cqrs():
    """
    Shutdown CQRS infrastructure.

    Call during application shutdown.

    Example:
        ```python
        @app.on_event("shutdown")
        async def shutdown():
            await shutdown_cqrs()
        ```
    """
    global _command_handler, _query_handler, _event_store
    global _projection_builder, _read_model_updater

    if _read_model_updater:
        await _read_model_updater.close()

    if _projection_builder:
        await _projection_builder.close()

    if _event_store:
        await _event_store.close()

    _command_handler = None
    _query_handler = None
    _event_store = None
    _projection_builder = None
    _read_model_updater = None


__all__ = [
    # Core handlers
    "CommandHandler",
    "QueryHandler",
    "Command",
    "Query",

    # Event sourcing
    "EventStore",
    "Event",
    "EventMetadata",

    # Projections
    "ProjectionBuilder",
    "Projection",
    "ReadModelUpdater",
    "ReadModelConfig",

    # Initialization
    "init_cqrs",
    "shutdown_cqrs",

    # Getters
    "get_command_handler",
    "get_query_handler",
    "get_event_store",
    "get_projection_builder",
    "get_read_model_updater",
]
