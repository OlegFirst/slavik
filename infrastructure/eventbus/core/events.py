"""
Event System - Type-safe Events
================================

Core event model used across the entire platform.
Transport-agnostic (can be sent via any backend).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum
import uuid


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """
    Base event class - used everywhere in platform.

    Transport-agnostic: can be serialized and sent via any backend.

    Attributes:
        id: Unique event identifier
        type: Event type (e.g., 'workflow.stage_changed', 'bia.process_added')
        data: Event payload (must be JSON-serializable)
        source: Event source (e.g., 'workflow-engine', 'ai-advisor')
        tenant_id: Tenant identifier for multi-tenancy
        correlation_id: For tracing related events
        timestamp: When event was created
        priority: Event priority
        retry_count: Number of retry attempts
        max_retries: Maximum retry attempts

    Example:
        ```python
        event = Event.create(
            event_type='bia.process_created',
            data={'process_id': 123, 'name': 'IT Systems'},
            source='bia-service',
            tenant_id='tenant_456'
        )
        ```
    """

    # Identity
    id: str
    type: str

    # Payload
    data: Dict[str, Any]

    # Context
    source: str
    tenant_id: str
    correlation_id: Optional[str] = None

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL

    # Retry
    retry_count: int = 0
    max_retries: int = 3

    @classmethod
    def create(
        cls,
        event_type: str,
        data: Dict[str, Any],
        source: str,
        tenant_id: str,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> 'Event':
        """
        Factory method for creating events.

        Args:
            event_type: Event type (dot-separated, e.g., 'workflow.stage_changed')
            data: Event payload (must be JSON-serializable)
            source: Event source identifier
            tenant_id: Tenant ID
            priority: Event priority (default: NORMAL)
            correlation_id: Optional correlation ID for tracing

        Returns:
            Event: New event instance

        Example:
            ```python
            event = Event.create(
                event_type='risk.assessment_completed',
                data={'assessment_id': 789, 'score': 8.5},
                source='risk-service',
                tenant_id='tenant_123',
                priority=EventPriority.HIGH
            )
            ```
        """
        return cls(
            id=str(uuid.uuid4()),
            type=event_type,
            data=data,
            source=source,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow(),
            priority=priority
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize event to dictionary.

        Returns:
            dict: Event as dictionary (JSON-serializable)
        """
        return {
            'id': self.id,
            'type': self.type,
            'data': self.data,
            'source': self.source,
            'tenant_id': self.tenant_id,
            'correlation_id': self.correlation_id,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """
        Deserialize event from dictionary.

        Args:
            data: Event dictionary

        Returns:
            Event: Reconstructed event
        """
        return cls(
            id=data['id'],
            type=data['type'],
            data=data['data'],
            source=data['source'],
            tenant_id=data['tenant_id'],
            correlation_id=data.get('correlation_id'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            priority=EventPriority(data['priority']),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3)
        )
