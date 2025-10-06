"""
Delegation Manager
==================

Delegates tasks to specialist agents:
- Workflow Specialist
- BIA Specialist
- Risk Specialist
- Compliance Specialist
- Integration Specialist

Uses EventBus to send delegation events.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from intelligent_core.ai_orchestration.models import Decision
from infrastructure.eventbus import IEventBus, Event, EventPriority

logger = logging.getLogger(__name__)


class DelegationManager:
    """
    Manages delegation to specialist agents.

    Determines which specialist to delegate to based on:
    - Task type
    - Priority level
    - Specialist availability
    - Domain expertise required

    Example:
        ```python
        manager = DelegationManager()
        await manager.initialize(event_bus)

        result = await manager.delegate(decision)
        if result['success']:
            print(f"Delegated to: {result['specialist']}")
        ```
    """

    # Specialist types
    SPECIALISTS = {
        'workflow': 'workflow-specialist',
        'bia': 'bia-specialist',
        'risk': 'risk-specialist',
        'compliance': 'compliance-specialist',
        'integration': 'integration-specialist',
        'general': 'general-specialist'
    }

    def __init__(self):
        self.event_bus: Optional[IEventBus] = None
        self.initialized = False
        self.delegation_stats = {specialist: 0 for specialist in self.SPECIALISTS.values()}

    async def initialize(self, event_bus: IEventBus) -> None:
        """
        Initialize delegation manager.

        Args:
            event_bus: EventBus instance for communication
        """
        self.event_bus = event_bus
        self.initialized = True
        logger.info("DelegationManager initialized")

    async def delegate(
        self,
        decision: Decision,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Delegate task to appropriate specialist.

        Args:
            decision: Decision to delegate
            timeout_seconds: Delegation timeout

        Returns:
            dict: Delegation result

        Example:
            ```python
            result = await manager.delegate(decision)
            if result['success']:
                print(f"Task delegated to {result['specialist']}")
            ```
        """
        if not self.initialized:
            raise RuntimeError("DelegationManager not initialized")

        logger.info(f"Delegating decision: {decision.action.value}")

        try:
            # Determine specialist
            specialist = self._select_specialist(decision)
            logger.info(f"Selected specialist: {specialist}")

            # Create delegation event
            event = self._create_delegation_event(decision, specialist)

            # Publish to event bus
            await self.event_bus.publish(event)

            # Update stats
            self.delegation_stats[specialist] += 1

            logger.info(f"✅ Delegated to {specialist}")

            return {
                'success': True,
                'specialist': specialist,
                'event_id': event.id,
                'delegated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Delegation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _select_specialist(self, decision: Decision) -> str:
        """
        Select appropriate specialist for decision.

        Selection logic:
        - Extract task domain from decision metadata
        - Match to specialist type
        - Return specialist identifier
        """
        # Get situation from metadata
        situation = decision.metadata.get('situation', {})

        # Workflow-related
        if 'workflow' in str(situation).lower():
            return self.SPECIALISTS['workflow']

        # BIA-related
        if 'bia' in str(situation).lower() or 'business_impact' in str(situation).lower():
            return self.SPECIALISTS['bia']

        # Risk-related
        if 'risk' in str(situation).lower() or 'threat' in str(situation).lower():
            return self.SPECIALISTS['risk']

        # Compliance-related
        if 'compliance' in str(situation).lower() or 'audit' in str(situation).lower():
            return self.SPECIALISTS['compliance']

        # Integration-related
        if 'integration' in str(situation).lower() or 'api' in str(situation).lower():
            return self.SPECIALISTS['integration']

        # Default to general specialist
        return self.SPECIALISTS['general']

    def _create_delegation_event(
        self,
        decision: Decision,
        specialist: str
    ) -> Event:
        """Create delegation event for specialist."""
        # Determine event priority
        event_priority = EventPriority.NORMAL
        if decision.priority.value >= 3:  # HIGH or CRITICAL
            event_priority = EventPriority.HIGH
        if decision.priority.value >= 4:  # CRITICAL
            event_priority = EventPriority.CRITICAL

        # Create event
        event = Event.create(
            event_type=f'orchestrator.delegate.{specialist}',
            data={
                'decision': decision.to_dict(),
                'specialist': specialist,
                'delegation_time': datetime.utcnow().isoformat()
            },
            source='ai-orchestrator',
            tenant_id=decision.metadata.get('tenant_id', 'default'),
            priority=event_priority
        )

        return event

    def get_stats(self) -> Dict[str, Any]:
        """Get delegation statistics."""
        total = sum(self.delegation_stats.values())
        return {
            'total_delegations': total,
            'by_specialist': self.delegation_stats,
            'initialized': self.initialized
        }
