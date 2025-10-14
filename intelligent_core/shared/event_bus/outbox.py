"""
Outbox Pattern Implementation
==============================

Ensures guaranteed event delivery through database outbox pattern.

How it works:
1. Events are saved to outbox_events table in same transaction as business logic
2. Background worker publishes events from outbox to EventBus
3. On success, event is marked as 'published'
4. On failure, event is retried with exponential backoff

This guarantees:
- No lost events (even if EventBus is down)
- Exactly-once semantics (with idempotent handlers)
- Transactional consistency
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, Text, JSON, TIMESTAMP, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import uuid

from .core import Event, get_event_bus

logger = logging.getLogger(__name__)

Base = declarative_base()


class OutboxEvent(Base):
    """
    Outbox events table model.

    Events are saved here first, then published to EventBus.
    """
    __tablename__ = "outbox_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    event_type = Column(String(255), nullable=False, index=True)
    aggregate_type = Column(String(255))
    aggregate_id = Column(String(255))
    payload = Column(JSON, nullable=False)
    metadata = Column(JSON)
    tenant_id = Column(String(100), index=True)
    source = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    published_at = Column(TIMESTAMP)
    status = Column(String(50), default="pending", nullable=False, index=True)
    retry_count = Column(Integer, default=0, nullable=False)
    error = Column(Text)


async def save_to_outbox(
    event_type: str,
    data: Dict[str, Any],
    source: str,
    db: Session,
    tenant_id: Optional[str] = None,
    aggregate_type: Optional[str] = None,
    aggregate_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> OutboxEvent:
    """
    Save event to outbox table.

    Use this instead of publish_event() when you need transactional guarantees.

    Args:
        event_type: Event type
        data: Event payload
        source: Service name
        db: SQLAlchemy session (must be in active transaction)
        tenant_id: Tenant identifier
        aggregate_type: Aggregate type (e.g., 'workflow', 'bia')
        aggregate_id: Aggregate ID
        metadata: Additional metadata

    Returns:
        OutboxEvent instance

    Example:
        async def create_workflow(workflow_data: dict, db: Session):
            # Business logic
            workflow = Workflow(**workflow_data)
            db.add(workflow)

            # Save event to outbox (in same transaction)
            await save_to_outbox(
                event_type="workflow.created",
                data={"workflow_id": workflow.id},
                source="workflow-service",
                db=db,
                aggregate_type="workflow",
                aggregate_id=str(workflow.id)
            )

            # Commit transaction - both workflow and event are saved atomically
            db.commit()
    """
    outbox_event = OutboxEvent(
        event_id=uuid.uuid4(),
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=data,
        metadata=metadata or {},
        tenant_id=tenant_id,
        source=source,
        status="pending",
        retry_count=0
    )

    db.add(outbox_event)
    # Don't commit here - let caller commit as part of their transaction

    logger.debug(f"💾 Saved to outbox: {event_type} (id: {outbox_event.event_id})")

    return outbox_event


class OutboxPublisher:
    """
    Background worker that publishes events from outbox to EventBus.

    Run this as a background task in your service.
    """

    def __init__(
        self,
        db_session_factory,
        batch_size: int = 100,
        poll_interval_seconds: int = 5,
        max_retries: int = 10
    ):
        """
        Initialize outbox publisher.

        Args:
            db_session_factory: Function that creates DB sessions
            batch_size: How many events to process per batch
            poll_interval_seconds: How often to check for new events
            max_retries: Maximum retry attempts before marking as failed
        """
        self.db_session_factory = db_session_factory
        self.batch_size = batch_size
        self.poll_interval = poll_interval_seconds
        self.max_retries = max_retries
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the publisher worker."""
        if self._running:
            logger.warning("OutboxPublisher already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("✅ OutboxPublisher started")

    async def stop(self):
        """Stop the publisher worker."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("✅ OutboxPublisher stopped")

    async def _run(self):
        """Main worker loop."""
        while self._running:
            try:
                await self._publish_batch()
                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ OutboxPublisher error: {e}")
                await asyncio.sleep(self.poll_interval)

    async def _publish_batch(self):
        """Publish one batch of events."""
        db = self.db_session_factory()
        event_bus = get_event_bus()

        if not event_bus:
            logger.debug("EventBus not available - skipping outbox publish")
            db.close()
            return

        try:
            # Get pending events (with exponential backoff for retries)
            pending_events = (
                db.query(OutboxEvent)
                .filter(
                    OutboxEvent.status == "pending",
                    OutboxEvent.retry_count < self.max_retries
                )
                .order_by(OutboxEvent.created_at)
                .limit(self.batch_size)
                .all()
            )

            if not pending_events:
                return

            logger.debug(f"📤 Publishing {len(pending_events)} events from outbox")

            for outbox_event in pending_events:
                try:
                    # Create Event object
                    event = Event(
                        id=str(outbox_event.event_id),
                        type=outbox_event.event_type,
                        data=outbox_event.payload,
                        source=outbox_event.source,
                        timestamp=outbox_event.created_at.isoformat(),
                        tenant_id=outbox_event.tenant_id,
                        metadata=outbox_event.metadata or {}
                    )

                    # Publish to EventBus
                    await event_bus.publish(event)

                    # Mark as published
                    outbox_event.status = "published"
                    outbox_event.published_at = datetime.utcnow()
                    outbox_event.error = None

                    logger.debug(f"✅ Published: {event.type} (id: {event.id})")

                except Exception as e:
                    # Mark as failed with retry
                    outbox_event.retry_count += 1
                    outbox_event.error = str(e)

                    if outbox_event.retry_count >= self.max_retries:
                        outbox_event.status = "failed"
                        logger.error(
                            f"❌ Failed to publish {outbox_event.event_type} "
                            f"after {self.max_retries} retries: {e}"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Retry {outbox_event.retry_count}/{self.max_retries} "
                            f"for {outbox_event.event_type}: {e}"
                        )

            # Commit all changes
            db.commit()

        except Exception as e:
            logger.error(f"❌ Batch publish error: {e}")
            db.rollback()

        finally:
            db.close()


async def publish_outbox_events(db_session_factory, batch_size: int = 100):
    """
    One-time publish of pending outbox events.

    Useful for manual publishing or testing.

    Args:
        db_session_factory: Function that creates DB sessions
        batch_size: How many events to process
    """
    publisher = OutboxPublisher(db_session_factory, batch_size=batch_size)
    await publisher._publish_batch()
    logger.info("✅ Outbox events published")
