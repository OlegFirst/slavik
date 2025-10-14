"""
EventBus Publisher for Workflow Intelligence

Bridges State Machine events to Platform EventBus.

Usage:
    from infrastructure.eventbus import create_eventbus
    from workflow_intelligence.integration.eventbus_publisher import WorkflowEventPublisher

    eventbus = create_eventbus('redis')
    publisher = WorkflowEventPublisher(eventbus)

    # Inject into State Machine
    sm = StateMachine(event_publisher=publisher)
"""

from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add infrastructure to path for EventBus import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from infrastructure.eventbus import Event, EventPriority
    from infrastructure.eventbus.factory import create_eventbus
except ImportError:
    # Fallback for development
    class Event:
        @staticmethod
        def create(event_type, data, source, tenant_id, priority=None):
            return {
                'event_type': event_type,
                'data': data,
                'source': source,
                'tenant_id': tenant_id,
                'priority': priority
            }

    class EventPriority:
        NORMAL = 'normal'
        HIGH = 'high'
        CRITICAL = 'critical'

    def create_eventbus(backend_type):
        return None


class WorkflowEventPublisher:
    """
    Adapter between State Machine and EventBus

    State Machine generates domain events → Publisher sends to EventBus
    """

    def __init__(self, eventbus=None):
        """
        Initialize publisher

        Args:
            eventbus: EventBus instance (or None for memory backend)
        """
        self.eventbus = eventbus or create_eventbus('memory')

    async def publish_state_changed(
        self,
        workflow_id: str,
        from_state: str,
        to_state: str,
        context: Dict[str, Any],
        tenant_id: str
    ):
        """Publish state transition event"""

        event = Event.create(
            event_type='workflow.state_changed',
            data={
                'workflow_id': workflow_id,
                'from_state': from_state,
                'to_state': to_state,
                'context': context,
                'module': context.get('module', 'unknown')
            },
            source='workflow-engine',
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        if self.eventbus:
            await self.eventbus.publish(event)

    async def publish_action_completed(
        self,
        workflow_id: str,
        action_type: str,
        action_data: Dict[str, Any],
        tenant_id: str
    ):
        """Publish action completion"""

        event = Event.create(
            event_type=f'workflow.action.{action_type}',
            data={
                'workflow_id': workflow_id,
                'action': action_data
            },
            source='workflow-engine',
            tenant_id=tenant_id
        )

        if self.eventbus:
            await self.eventbus.publish(event)

    async def publish_validation_failed(
        self,
        workflow_id: str,
        errors: list,
        tenant_id: str
    ):
        """Publish validation failures"""

        event = Event.create(
            event_type='workflow.validation_failed',
            data={
                'workflow_id': workflow_id,
                'errors': errors
            },
            source='workflow-engine',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH  # High priority for errors
        )

        if self.eventbus:
            await self.eventbus.publish(event)

    async def publish_milestone_reached(
        self,
        workflow_id: str,
        milestone: str,
        tenant_id: str
    ):
        """Publish milestone achievement"""

        event = Event.create(
            event_type='workflow.milestone_reached',
            data={
                'workflow_id': workflow_id,
                'milestone': milestone
            },
            source='workflow-engine',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH
        )

        if self.eventbus:
            await self.eventbus.publish(event)

    async def publish_checkpoint_validated(
        self,
        workflow_id: str,
        checkpoint: str,
        result: Dict[str, Any],
        tenant_id: str
    ):
        """Publish checkpoint validation result"""

        event = Event.create(
            event_type='workflow.checkpoint_validated',
            data={
                'workflow_id': workflow_id,
                'checkpoint': checkpoint,
                'passed': result.get('passed', False),
                'violations': result.get('violations', []),
                'requires_escalation': result.get('requires_escalation', False)
            },
            source='workflow-engine',
            tenant_id=tenant_id,
            priority=EventPriority.HIGH if result.get('requires_escalation') else EventPriority.NORMAL
        )

        if self.eventbus:
            await self.eventbus.publish(event)
