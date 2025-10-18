"""
Read Model Updater - Real-time Projection Updates
=================================================

Subscribes to events and updates read models in real-time.

Features:
- Event subscription
- Automatic projection updates
- Cache invalidation
- Error handling and retry
- Performance monitoring

Architecture:
    EventBus → Read Model Updater → Projections + Cache Invalidation
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Callable
import redis.asyncio as redis

from .event_store import Event, EventStore, EventMetadata
from .projection_builder import ProjectionBuilder

logger = logging.getLogger(__name__)


@dataclass
class ReadModelConfig:
    """
    Read Model Configuration.

    Defines which events trigger which projections.

    Attributes:
        projection_name: Name of projection to update
        event_types: Event types that trigger updates
        cache_patterns: Cache key patterns to invalidate
        enabled: Whether this config is active
        retry_on_error: Whether to retry on failures
        max_retries: Maximum retry attempts

    Example:
        ```python
        config = ReadModelConfig(
            projection_name="bia_process_list",
            event_types=[
                "BIAProcessCreated",
                "BIAProcessUpdated",
                "BIAProcessCompleted"
            ],
            cache_patterns=[
                "cqrs:query:get_bia_processes:*",
                "cqrs:query:get_bia_summary:*"
            ]
        )
        ```
    """
    projection_name: str
    event_types: List[str] = field(default_factory=list)
    cache_patterns: List[str] = field(default_factory=list)
    enabled: bool = True
    retry_on_error: bool = True
    max_retries: int = 3


class ReadModelUpdater:
    """
    Read Model Updater.

    Listens to events and updates projections in real-time.

    Example:
        ```python
        # Initialize
        updater = ReadModelUpdater(
            event_store=event_store,
            projection_builder=projection_builder,
            redis_url="redis://localhost:6379/0"
        )

        await updater.connect()

        # Register configurations
        updater.register_config(ReadModelConfig(
            projection_name="bia_process_list",
            event_types=["BIAProcessCreated", "BIAProcessUpdated"],
            cache_patterns=["cqrs:query:get_bia_*"]
        ))

        # Start processing
        await updater.start()
        ```
    """

    def __init__(
        self,
        event_store: EventStore,
        projection_builder: ProjectionBuilder,
        redis_url: str = "redis://localhost:6379/0"
    ):
        """
        Initialize Read Model Updater.

        Args:
            event_store: Event store for loading events
            projection_builder: Projection builder for applying events
            redis_url: Redis URL for cache invalidation
        """
        self.event_store = event_store
        self.projection_builder = projection_builder
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.configs: Dict[str, ReadModelConfig] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._event_handlers: Dict[str, List[Callable]] = {}

        # Metrics
        self._events_processed = 0
        self._events_failed = 0
        self._cache_invalidations = 0

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False
            )
            await self.redis.ping()
            logger.info("Read Model Updater connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.redis = None

    async def close(self) -> None:
        """Close connections and stop processing."""
        await self.stop()

        if self.redis:
            await self.redis.close()
            logger.info("Read Model Updater Redis connection closed")

    def register_config(self, config: ReadModelConfig) -> None:
        """
        Register read model configuration.

        Args:
            config: Read model configuration

        Example:
            ```python
            updater.register_config(ReadModelConfig(
                projection_name="bia_process_list",
                event_types=["BIAProcessCreated"],
                cache_patterns=["cqrs:query:get_bia_*"]
            ))
            ```
        """
        self.configs[config.projection_name] = config

        # Register event handlers
        for event_type in config.event_types:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []

            self._event_handlers[event_type].append(
                lambda event, cfg=config: self._handle_event(event, cfg)
            )

        logger.info(
            f"Registered read model config: {config.projection_name} "
            f"for {len(config.event_types)} event types"
        )

    def register_event_handler(
        self,
        event_type: str,
        handler: Callable
    ) -> None:
        """
        Register custom event handler.

        Args:
            event_type: Event type to handle
            handler: Async handler function

        Example:
            ```python
            async def handle_bia_created(event: Event):
                # Custom processing
                print(f"BIA created: {event.aggregate_id}")

            updater.register_event_handler(
                "BIAProcessCreated",
                handle_bia_created
            )
            ```
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(handler)
        logger.info(f"Registered custom handler for {event_type}")

    async def _handle_event(
        self,
        event: Event,
        config: ReadModelConfig
    ) -> None:
        """
        Handle event for specific configuration.

        Args:
            event: Event to handle
            config: Read model configuration
        """
        if not config.enabled:
            return

        retry_count = 0
        max_retries = config.max_retries if config.retry_on_error else 0

        while retry_count <= max_retries:
            try:
                # Apply event to projection
                await self.projection_builder.apply_event(
                    event,
                    projection_names=[config.projection_name]
                )

                # Invalidate cache
                if self.redis and config.cache_patterns:
                    await self._invalidate_cache(
                        config.cache_patterns,
                        event.metadata.tenant_id
                    )

                self._events_processed += 1

                logger.debug(
                    f"Event {event.event_type} applied to "
                    f"{config.projection_name}"
                )
                break

            except Exception as e:
                retry_count += 1

                if retry_count > max_retries:
                    self._events_failed += 1
                    logger.error(
                        f"Failed to handle event {event.event_type} "
                        f"for {config.projection_name} after {max_retries} retries: {e}",
                        exc_info=True
                    )
                    break

                logger.warning(
                    f"Error handling event, retrying {retry_count}/{max_retries}: {e}"
                )
                await asyncio.sleep(0.1 * retry_count)  # Exponential backoff

    async def _invalidate_cache(
        self,
        patterns: List[str],
        tenant_id: Optional[str] = None
    ) -> None:
        """
        Invalidate cache by patterns.

        Args:
            patterns: List of cache key patterns
            tenant_id: Optional tenant filter
        """
        if not self.redis:
            return

        for pattern in patterns:
            try:
                # Add tenant filter if provided
                full_pattern = pattern
                if tenant_id and "*" in pattern:
                    full_pattern = pattern.replace("*", f"*{tenant_id}*")

                # Delete matching keys
                deleted = 0
                async for key in self.redis.scan_iter(match=full_pattern):
                    await self.redis.delete(key)
                    deleted += 1

                if deleted > 0:
                    self._cache_invalidations += deleted
                    logger.debug(
                        f"Invalidated {deleted} cache keys matching {full_pattern}"
                    )

            except Exception as e:
                logger.warning(f"Cache invalidation error for {pattern}: {e}")

    async def process_event(self, event: Event) -> None:
        """
        Process single event.

        Args:
            event: Event to process

        Example:
            ```python
            event = Event(
                event_type="BIAProcessCreated",
                aggregate_type="BIAProcess",
                aggregate_id="bia_123",
                data={...}
            )
            await updater.process_event(event)
            ```
        """
        event_type = event.event_type

        # Get handlers for this event type
        handlers = self._event_handlers.get(event_type, [])

        if not handlers:
            logger.debug(f"No handlers registered for {event_type}")
            return

        # Execute all handlers
        await asyncio.gather(
            *[handler(event) for handler in handlers],
            return_exceptions=True
        )

    async def process_events_from_store(
        self,
        from_position: int = 0,
        batch_size: int = 100
    ) -> int:
        """
        Process events from event store.

        Used for catching up after downtime.

        Args:
            from_position: Start position (event ID)
            batch_size: Batch size

        Returns:
            Number of events processed

        Example:
            ```python
            # Process events from position 1000
            count = await updater.process_events_from_store(from_position=1000)
            print(f"Processed {count} events")
            ```
        """
        event_count = 0

        async for event in self.event_store.get_all_events(
            from_position=from_position,
            batch_size=batch_size
        ):
            await self.process_event(event)
            event_count += 1

            if event_count % 100 == 0:
                logger.info(f"Processed {event_count} events from store")

        logger.info(f"Processed {event_count} total events from store")
        return event_count

    async def start(
        self,
        poll_interval: float = 1.0,
        catch_up: bool = True
    ) -> None:
        """
        Start read model updater.

        Args:
            poll_interval: Seconds between event store polls
            catch_up: Whether to catch up from last position

        Example:
            ```python
            # Start with catch-up
            await updater.start(poll_interval=1.0, catch_up=True)
            ```
        """
        if self._running:
            logger.warning("Read Model Updater already running")
            return

        self._running = True

        # Catch up if requested
        if catch_up:
            logger.info("Catching up read models from event store...")
            last_position = await self._get_last_position()
            await self.process_events_from_store(from_position=last_position)

        # Start polling loop
        self._task = asyncio.create_task(self._poll_events_loop(poll_interval))
        logger.info("Read Model Updater started")

    async def stop(self) -> None:
        """Stop read model updater."""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Read Model Updater stopped")

    async def _poll_events_loop(self, poll_interval: float) -> None:
        """Poll events loop (internal)."""
        while self._running:
            try:
                # Get last processed position
                last_position = await self._get_last_position()

                # Process new events
                event_count = 0
                async for event in self.event_store.get_all_events(
                    from_position=last_position,
                    batch_size=100
                ):
                    await self.process_event(event)
                    event_count += 1

                    # Update last position
                    await self._save_last_position(event.version)

                if event_count > 0:
                    logger.debug(f"Processed {event_count} new events")

                # Wait before next poll
                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error in event polling loop: {e}", exc_info=True)
                await asyncio.sleep(poll_interval * 5)  # Wait longer on error

    async def _get_last_position(self) -> int:
        """Get last processed event position."""
        if not self.redis:
            return 0

        try:
            position = await self.redis.get("cqrs:read_model_updater:last_position")
            return int(position) if position else 0
        except Exception as e:
            logger.warning(f"Error getting last position: {e}")
            return 0

    async def _save_last_position(self, position: int) -> None:
        """Save last processed event position."""
        if not self.redis:
            return

        try:
            await self.redis.set("cqrs:read_model_updater:last_position", position)
        except Exception as e:
            logger.warning(f"Error saving last position: {e}")

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get updater metrics.

        Returns:
            Metrics dictionary

        Example:
            ```python
            metrics = await updater.get_metrics()
            print(f"Events processed: {metrics['events_processed']}")
            print(f"Success rate: {metrics['success_rate']:.2%}")
            ```
        """
        total_events = self._events_processed + self._events_failed
        success_rate = (
            self._events_processed / total_events
            if total_events > 0
            else 1.0
        )

        return {
            "events_processed": self._events_processed,
            "events_failed": self._events_failed,
            "total_events": total_events,
            "success_rate": success_rate,
            "cache_invalidations": self._cache_invalidations,
            "registered_configs": len(self.configs),
            "event_handlers": sum(len(h) for h in self._event_handlers.values()),
            "running": self._running
        }

    async def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self._events_processed = 0
        self._events_failed = 0
        self._cache_invalidations = 0
        logger.info("Metrics reset")

    async def get_config_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all configurations.

        Returns:
            List of config status dictionaries

        Example:
            ```python
            status = await updater.get_config_status()
            for config in status:
                print(f"{config['name']}: {'enabled' if config['enabled'] else 'disabled'}")
            ```
        """
        return [
            {
                "name": config.projection_name,
                "enabled": config.enabled,
                "event_types": config.event_types,
                "cache_patterns": config.cache_patterns,
                "retry_on_error": config.retry_on_error,
                "max_retries": config.max_retries
            }
            for config in self.configs.values()
        ]


# Example Usage

async def example_usage():
    """
    Example Read Model Updater usage.
    """
    from .event_store import EventStore
    from .projection_builder import ProjectionBuilder, BIAProcessListProjection

    # Initialize components
    database_url = "postgresql://user:pass@localhost/db"
    redis_url = "redis://localhost:6379/0"

    event_store = EventStore(database_url)
    await event_store.connect()
    await event_store.ensure_schema()

    projection_builder = ProjectionBuilder(event_store, database_url)
    await projection_builder.connect()
    projection_builder.register_projection(BIAProcessListProjection())
    await projection_builder.ensure_schemas()

    updater = ReadModelUpdater(
        event_store=event_store,
        projection_builder=projection_builder,
        redis_url=redis_url
    )
    await updater.connect()

    # Register configurations
    updater.register_config(ReadModelConfig(
        projection_name="bia_process_list",
        event_types=[
            "BIAProcessCreated",
            "BIAProcessRTOUpdated",
            "BIAProcessCompleted"
        ],
        cache_patterns=[
            "cqrs:query:get_bia_processes:*",
            "cqrs:query:get_bia_process_detail:*"
        ]
    ))

    # Register custom handler
    async def handle_critical_process(event: Event):
        if event.data.get("criticality") == "CRITICAL":
            logger.info(f"ALERT: Critical process created: {event.aggregate_id}")

    updater.register_event_handler("BIAProcessCreated", handle_critical_process)

    # Start processing
    await updater.start(poll_interval=1.0, catch_up=True)

    # Get metrics
    metrics = await updater.get_metrics()
    logger.info(f"Updater metrics: {metrics}")

    # Run for some time
    await asyncio.sleep(60)

    # Stop
    await updater.stop()
    await updater.close()
    await projection_builder.close()
    await event_store.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
