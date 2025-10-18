"""
Command Handler - CQRS Write Side
==================================

Handles commands (write operations) in CQRS architecture.

Responsibilities:
- Load aggregates from event store
- Execute business logic
- Generate domain events
- Save events to event store
- Publish events to EventBus

Command Flow:
    1. Receive command
    2. Load aggregate (from snapshot + events)
    3. Validate command
    4. Execute business logic on aggregate
    5. Collect generated events
    6. Save events to event store (with optimistic locking)
    7. Publish events to EventBus for projections
    8. Return result
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from uuid import uuid4

from .event_store import Event, EventStore, EventMetadata, ConcurrencyError

logger = logging.getLogger(__name__)

# Type variables for generic command handling
TCommand = TypeVar('TCommand', bound='Command')
TAggregate = TypeVar('TAggregate', bound='Aggregate')
TResult = TypeVar('TResult')


@dataclass
class Command(ABC):
    """
    Base Command class.

    All commands must inherit from this class.

    Attributes:
        command_id: Unique command identifier
        tenant_id: Tenant identifier
        user_id: User executing the command
        metadata: Additional command metadata

    Example:
        ```python
        @dataclass
        class CreateBIAProcessCommand(Command):
            name: str
            criticality: str
            rto_hours: int
            rpo_hours: int
            mtpd_hours: int
            financial_impact: Dict[str, float]
        ```
    """
    command_id: str = field(default_factory=lambda: f"cmd_{uuid4().hex}")
    tenant_id: str = ""
    user_id: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommandResult:
    """
    Result of command execution.

    Attributes:
        success: Whether command succeeded
        aggregate_id: ID of affected aggregate
        version: New version of aggregate
        events: Events generated
        data: Additional result data
        error: Error message if failed
    """
    success: bool
    aggregate_id: Optional[str] = None
    version: Optional[int] = None
    events: List[Event] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class Aggregate(ABC):
    """
    Base Aggregate class.

    Aggregates are the core business entities that enforce business rules.

    Attributes:
        aggregate_id: Unique identifier
        aggregate_type: Type name (e.g., "BIAProcess")
        version: Current version (increments with each event)
        uncommitted_events: Events not yet saved

    Example:
        ```python
        class BIAProcessAggregate(Aggregate):
            def __init__(self, aggregate_id: str):
                super().__init__(aggregate_id, "BIAProcess")
                self.name = None
                self.criticality = None
                self.rto_hours = None
                self.status = "DRAFT"

            def create(self, name: str, criticality: str, rto_hours: int):
                # Validate
                if not name:
                    raise ValueError("Name required")

                # Generate event
                self._apply_event(Event(
                    event_type="BIAProcessCreated",
                    aggregate_type=self.aggregate_type,
                    aggregate_id=self.aggregate_id,
                    version=self.version + 1,
                    data={
                        "name": name,
                        "criticality": criticality,
                        "rto_hours": rto_hours
                    }
                ))

            def _apply_BIAProcessCreated(self, event: Event):
                # Update state
                self.name = event.data["name"]
                self.criticality = event.data["criticality"]
                self.rto_hours = event.data["rto_hours"]
        ```
    """

    def __init__(self, aggregate_id: str, aggregate_type: str):
        """
        Initialize aggregate.

        Args:
            aggregate_id: Unique identifier
            aggregate_type: Type name
        """
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type
        self.version = 0
        self.uncommitted_events: List[Event] = []

    def _apply_event(self, event: Event, is_new: bool = True) -> None:
        """
        Apply event to aggregate.

        Args:
            event: Event to apply
            is_new: Whether this is a new event (True) or replay (False)
        """
        # Find handler method
        handler_name = f"_apply_{event.event_type}"
        handler = getattr(self, handler_name, None)

        if handler and callable(handler):
            handler(event)
        else:
            logger.warning(
                f"No handler for {event.event_type} on {self.aggregate_type}"
            )

        # Update version
        self.version = event.version

        # Track uncommitted events
        if is_new:
            self.uncommitted_events.append(event)

    def load_from_history(self, events: List[Event]) -> None:
        """
        Load aggregate from event history.

        Args:
            events: Historical events to replay
        """
        for event in events:
            self._apply_event(event, is_new=False)

    def get_uncommitted_events(self) -> List[Event]:
        """Get events not yet persisted."""
        return self.uncommitted_events.copy()

    def mark_events_as_committed(self) -> None:
        """Clear uncommitted events after persistence."""
        self.uncommitted_events.clear()

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert aggregate state to dictionary.

        Used for snapshots.
        """
        pass

    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Restore aggregate state from dictionary.

        Used for snapshot restoration.
        """
        pass


class CommandHandler:
    """
    Command Handler for CQRS write operations.

    Coordinates command execution:
    - Loads aggregates
    - Executes commands
    - Saves events
    - Publishes to EventBus

    Example:
        ```python
        # Initialize
        command_handler = CommandHandler(
            event_store=event_store,
            eventbus_client=eventbus_client
        )

        # Register aggregate factory
        command_handler.register_aggregate(
            "BIAProcess",
            lambda id: BIAProcessAggregate(id)
        )

        # Execute command
        command = CreateBIAProcessCommand(
            tenant_id="tenant_123",
            name="Payment Processing",
            criticality="CRITICAL",
            rto_hours=2
        )

        result = await command_handler.handle(
            command,
            lambda aggregate, cmd: aggregate.create(
                cmd.name,
                cmd.criticality,
                cmd.rto_hours
            )
        )
        ```
    """

    def __init__(
        self,
        event_store: EventStore,
        eventbus_client=None
    ):
        """
        Initialize Command Handler.

        Args:
            event_store: Event store for persistence
            eventbus_client: EventBus for publishing events (optional)
        """
        self.event_store = event_store
        self.eventbus_client = eventbus_client
        self._aggregate_factories: Dict[str, callable] = {}
        self._snapshot_threshold = 100  # Save snapshot every N events

    def register_aggregate(
        self,
        aggregate_type: str,
        factory: callable
    ) -> None:
        """
        Register aggregate factory.

        Args:
            aggregate_type: Type name (e.g., "BIAProcess")
            factory: Function to create new aggregate instance

        Example:
            ```python
            command_handler.register_aggregate(
                "BIAProcess",
                lambda aggregate_id: BIAProcessAggregate(aggregate_id)
            )
            ```
        """
        self._aggregate_factories[aggregate_type] = factory
        logger.info(f"Registered aggregate factory: {aggregate_type}")

    async def load_aggregate(
        self,
        aggregate_type: str,
        aggregate_id: str
    ) -> Aggregate:
        """
        Load aggregate from event store.

        Uses snapshots if available for performance.

        Args:
            aggregate_type: Type of aggregate
            aggregate_id: Aggregate identifier

        Returns:
            Loaded aggregate instance

        Example:
            ```python
            aggregate = await command_handler.load_aggregate(
                "BIAProcess",
                "bia_123"
            )
            ```
        """
        # Get aggregate factory
        factory = self._aggregate_factories.get(aggregate_type)
        if not factory:
            raise ValueError(f"No factory registered for {aggregate_type}")

        # Create new instance
        aggregate = factory(aggregate_id)

        # Try to load from snapshot
        snapshot = await self.event_store.get_snapshot(
            aggregate_type,
            aggregate_id
        )

        if snapshot:
            version, state = snapshot
            aggregate.from_dict(state)
            aggregate.version = version

            # Load events after snapshot
            events = await self.event_store.get_events(
                aggregate_type,
                aggregate_id,
                from_version=version + 1
            )

            logger.debug(
                f"Loaded {aggregate_type}/{aggregate_id} from snapshot v{version} "
                f"+ {len(events)} events"
            )
        else:
            # Load all events
            events = await self.event_store.get_events(
                aggregate_type,
                aggregate_id
            )

            logger.debug(
                f"Loaded {aggregate_type}/{aggregate_id} from {len(events)} events"
            )

        # Replay events
        aggregate.load_from_history(events)

        return aggregate

    async def save_aggregate(
        self,
        aggregate: Aggregate,
        metadata: EventMetadata
    ) -> List[Event]:
        """
        Save aggregate events.

        Args:
            aggregate: Aggregate with uncommitted events
            metadata: Event metadata

        Returns:
            List of saved events

        Raises:
            ConcurrencyError: If version conflict detected
        """
        uncommitted_events = aggregate.get_uncommitted_events()

        if not uncommitted_events:
            return []

        # Add metadata to all events
        for event in uncommitted_events:
            event.metadata = metadata

        # Get expected version (before new events)
        expected_version = aggregate.version - len(uncommitted_events)

        try:
            # Save events with optimistic locking
            saved_events = await self.event_store.save_events(
                uncommitted_events,
                expected_version=expected_version if expected_version > 0 else None
            )

            # Mark as committed
            aggregate.mark_events_as_committed()

            # Publish to EventBus
            if self.eventbus_client:
                for event in saved_events:
                    try:
                        await self.eventbus_client.publish(
                            event.event_type,
                            event.to_dict(),
                            tenant_id=metadata.tenant_id
                        )
                    except Exception as e:
                        logger.error(f"Failed to publish event to EventBus: {e}")

            # Save snapshot if threshold reached
            if aggregate.version > 0 and aggregate.version % self._snapshot_threshold == 0:
                await self.event_store.save_snapshot(
                    aggregate.aggregate_type,
                    aggregate.aggregate_id,
                    aggregate.version,
                    aggregate.to_dict()
                )
                logger.info(
                    f"Snapshot saved for {aggregate.aggregate_type}/"
                    f"{aggregate.aggregate_id} v{aggregate.version}"
                )

            logger.info(
                f"Saved {len(saved_events)} events for "
                f"{aggregate.aggregate_type}/{aggregate.aggregate_id}"
            )

            return saved_events

        except ConcurrencyError as e:
            logger.error(f"Concurrency error saving aggregate: {e}")
            raise

    async def handle(
        self,
        command: Command,
        executor: callable,
        aggregate_type: Optional[str] = None,
        aggregate_id: Optional[str] = None,
        create_new: bool = False
    ) -> CommandResult:
        """
        Handle command execution.

        Args:
            command: Command to execute
            executor: Function to execute on aggregate
            aggregate_type: Type of aggregate (required)
            aggregate_id: ID of aggregate (generated if create_new=True)
            create_new: Whether to create new aggregate

        Returns:
            CommandResult with execution details

        Example:
            ```python
            # Create new aggregate
            result = await command_handler.handle(
                command=CreateBIAProcessCommand(...),
                executor=lambda agg, cmd: agg.create(cmd.name, cmd.criticality),
                aggregate_type="BIAProcess",
                create_new=True
            )

            # Update existing aggregate
            result = await command_handler.handle(
                command=UpdateBIAProcessCommand(...),
                executor=lambda agg, cmd: agg.update_rto(cmd.rto_hours),
                aggregate_type="BIAProcess",
                aggregate_id="bia_123"
            )
            ```
        """
        try:
            # Generate aggregate ID if creating new
            if create_new:
                aggregate_id = aggregate_id or f"{aggregate_type.lower()}_{uuid4().hex[:12]}"

            if not aggregate_id:
                raise ValueError("aggregate_id required")

            # Load or create aggregate
            if create_new:
                factory = self._aggregate_factories.get(aggregate_type)
                if not factory:
                    raise ValueError(f"No factory registered for {aggregate_type}")
                aggregate = factory(aggregate_id)
            else:
                aggregate = await self.load_aggregate(aggregate_type, aggregate_id)

            # Execute command on aggregate
            executor(aggregate, command)

            # Prepare metadata
            metadata = EventMetadata(
                tenant_id=command.tenant_id,
                user_id=command.user_id,
                correlation_id=command.command_id,
                timestamp=datetime.utcnow()
            )

            # Save events
            events = await self.save_aggregate(aggregate, metadata)

            # Return success result
            return CommandResult(
                success=True,
                aggregate_id=aggregate_id,
                version=aggregate.version,
                events=events,
                data={"event_count": len(events)}
            )

        except ConcurrencyError as e:
            logger.error(f"Concurrency error handling command: {e}")
            return CommandResult(
                success=False,
                error=f"Concurrency error: {str(e)}"
            )

        except Exception as e:
            logger.error(f"Error handling command: {e}", exc_info=True)
            return CommandResult(
                success=False,
                error=str(e)
            )

    async def handle_batch(
        self,
        commands: List[tuple[Command, callable, str, Optional[str], bool]],
        max_retries: int = 3
    ) -> List[CommandResult]:
        """
        Handle multiple commands.

        Args:
            commands: List of (command, executor, aggregate_type, aggregate_id, create_new)
            max_retries: Maximum retries for concurrency errors

        Returns:
            List of CommandResult

        Example:
            ```python
            commands = [
                (cmd1, executor1, "BIAProcess", None, True),
                (cmd2, executor2, "BIAProcess", "bia_123", False),
                (cmd3, executor3, "BIAProcess", "bia_456", False)
            ]

            results = await command_handler.handle_batch(commands)

            for result in results:
                if result.success:
                    print(f"Success: {result.aggregate_id}")
                else:
                    print(f"Failed: {result.error}")
            ```
        """
        results = []

        for cmd, executor, agg_type, agg_id, create_new in commands:
            retry_count = 0

            while retry_count < max_retries:
                result = await self.handle(
                    command=cmd,
                    executor=executor,
                    aggregate_type=agg_type,
                    aggregate_id=agg_id,
                    create_new=create_new
                )

                # Retry on concurrency errors
                if not result.success and "Concurrency error" in (result.error or ""):
                    retry_count += 1
                    logger.warning(
                        f"Concurrency error, retrying {retry_count}/{max_retries}"
                    )
                    continue

                results.append(result)
                break
            else:
                # Max retries exceeded
                results.append(CommandResult(
                    success=False,
                    error=f"Max retries exceeded ({max_retries})"
                ))

        return results


# Example Aggregate and Commands for BIA

class BIAProcessAggregate(Aggregate):
    """Example BIA Process Aggregate."""

    def __init__(self, aggregate_id: str):
        super().__init__(aggregate_id, "BIAProcess")
        self.name = None
        self.criticality = None
        self.rto_hours = None
        self.rpo_hours = None
        self.mtpd_hours = None
        self.status = "DRAFT"
        self.financial_impact = {}

    def create(
        self,
        name: str,
        criticality: str,
        rto_hours: int,
        rpo_hours: int,
        mtpd_hours: int,
        financial_impact: Dict[str, float]
    ):
        """Create BIA process."""
        # Business rules validation
        if not name:
            raise ValueError("Name is required")

        if rto_hours < rpo_hours:
            raise ValueError("RTO must be >= RPO")

        if mtpd_hours < rto_hours:
            raise ValueError("MTPD must be >= RTO")

        # Generate event
        self._apply_event(Event(
            event_type="BIAProcessCreated",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={
                "name": name,
                "criticality": criticality,
                "rto_hours": rto_hours,
                "rpo_hours": rpo_hours,
                "mtpd_hours": mtpd_hours,
                "financial_impact": financial_impact,
                "status": "DRAFT"
            }
        ))

    def update_rto(self, rto_hours: int, rpo_hours: Optional[int] = None):
        """Update RTO and optionally RPO."""
        rpo = rpo_hours or self.rpo_hours

        if rto_hours < rpo:
            raise ValueError("RTO must be >= RPO")

        self._apply_event(Event(
            event_type="BIAProcessRTOUpdated",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={
                "rto_hours": rto_hours,
                "rpo_hours": rpo,
                "previous_rto": self.rto_hours,
                "previous_rpo": self.rpo_hours
            }
        ))

    def complete(self):
        """Mark as completed."""
        if self.status == "COMPLETED":
            raise ValueError("Already completed")

        self._apply_event(Event(
            event_type="BIAProcessCompleted",
            aggregate_type=self.aggregate_type,
            aggregate_id=self.aggregate_id,
            version=self.version + 1,
            data={
                "previous_status": self.status,
                "completed_at": datetime.utcnow().isoformat()
            }
        ))

    # Event handlers

    def _apply_BIAProcessCreated(self, event: Event):
        """Apply BIAProcessCreated event."""
        self.name = event.data["name"]
        self.criticality = event.data["criticality"]
        self.rto_hours = event.data["rto_hours"]
        self.rpo_hours = event.data["rpo_hours"]
        self.mtpd_hours = event.data["mtpd_hours"]
        self.financial_impact = event.data.get("financial_impact", {})
        self.status = event.data.get("status", "DRAFT")

    def _apply_BIAProcessRTOUpdated(self, event: Event):
        """Apply BIAProcessRTOUpdated event."""
        self.rto_hours = event.data["rto_hours"]
        self.rpo_hours = event.data["rpo_hours"]

    def _apply_BIAProcessCompleted(self, event: Event):
        """Apply BIAProcessCompleted event."""
        self.status = "COMPLETED"

    # Snapshot support

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for snapshot."""
        return {
            "name": self.name,
            "criticality": self.criticality,
            "rto_hours": self.rto_hours,
            "rpo_hours": self.rpo_hours,
            "mtpd_hours": self.mtpd_hours,
            "status": self.status,
            "financial_impact": self.financial_impact
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore from snapshot dictionary."""
        self.name = data.get("name")
        self.criticality = data.get("criticality")
        self.rto_hours = data.get("rto_hours")
        self.rpo_hours = data.get("rpo_hours")
        self.mtpd_hours = data.get("mtpd_hours")
        self.status = data.get("status", "DRAFT")
        self.financial_impact = data.get("financial_impact", {})


# Example Commands

@dataclass
class CreateBIAProcessCommand(Command):
    """Command to create BIA process."""
    name: str = ""
    criticality: str = ""
    rto_hours: int = 0
    rpo_hours: int = 0
    mtpd_hours: int = 0
    financial_impact: Dict[str, float] = field(default_factory=dict)


@dataclass
class UpdateBIARTOCommand(Command):
    """Command to update RTO."""
    aggregate_id: str = ""
    rto_hours: int = 0
    rpo_hours: Optional[int] = None


@dataclass
class CompleteBIAProcessCommand(Command):
    """Command to complete BIA process."""
    aggregate_id: str = ""
