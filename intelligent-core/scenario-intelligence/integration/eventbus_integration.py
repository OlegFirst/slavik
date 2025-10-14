"""
EventBus Integration for Scenario Intelligence

Использует СУЩЕСТВУЮЩИЙ EventBus из infrastructure/eventbus
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add infrastructure to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from infrastructure.eventbus import create_eventbus, Event, EventPriority

logger = logging.getLogger(__name__)


class ScenarioEventPublisher:
    """
    Publisher для событий Scenario Intelligence

    Использует СУЩЕСТВУЮЩИЙ EventBus из infrastructure/eventbus
    """

    def __init__(self, backend: str = 'memory'):
        """
        Initialize event publisher

        Args:
            backend: EventBus backend ('memory', 'redis', 'rabbitmq')
        """
        self.backend = backend
        self.eventbus = None

    async def initialize(self):
        """Initialize EventBus connection"""
        if not self.eventbus:
            self.eventbus = create_eventbus(self.backend)
            logger.info(f"✅ ScenarioEventPublisher initialized with {self.backend} backend")

    async def publish_execution_started(
        self,
        scenario_id: str,
        scenario_data: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """
        Publish: scenario.execution.started

        Args:
            scenario_id: Scenario ID
            scenario_data: Full scenario dict
            context: Execution context
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type='scenario.execution.started',
            data={
                'scenario_id': scenario_id,
                'level': scenario_data.get('meta', {}).get('level'),
                'type': scenario_data.get('meta', {}).get('type'),
                'context': context
            },
            source='scenario-intelligence',
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.debug(f"📤 Published: scenario.execution.started ({scenario_id})")

    async def publish_execution_completed(
        self,
        scenario_id: str,
        result: Dict[str, Any],
        duration_ms: int
    ):
        """
        Publish: scenario.execution.completed

        Args:
            scenario_id: Scenario ID
            result: Execution result
            duration_ms: Duration in milliseconds
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type='scenario.execution.completed',
            data={
                'scenario_id': scenario_id,
                'status': result.get('status'),
                'duration_ms': duration_ms,
                'steps_executed': result.get('steps_executed'),
                'result_summary': {
                    'success': result.get('status') == 'success',
                    'errors': result.get('errors', [])
                }
            },
            source='scenario-intelligence',
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"✅ Published: scenario.execution.completed ({scenario_id}) - {result.get('status')}")

    async def publish_execution_failed(
        self,
        scenario_id: str,
        error: str,
        context: Dict[str, Any]
    ):
        """
        Publish: scenario.execution.failed

        Args:
            scenario_id: Scenario ID
            error: Error message
            context: Execution context
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type='scenario.execution.failed',
            data={
                'scenario_id': scenario_id,
                'error': error,
                'context': context
            },
            source='scenario-intelligence',
            priority=EventPriority.HIGH
        )

        await self.eventbus.publish(event)
        logger.error(f"❌ Published: scenario.execution.failed ({scenario_id})")

    async def publish_pattern_detected(
        self,
        pattern_type: str,
        scenarios_involved: list,
        confidence: float
    ):
        """
        Publish: scenario.pattern.detected

        Args:
            pattern_type: Type of pattern detected
            scenarios_involved: List of scenario IDs
            confidence: Confidence score (0-1)
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type='scenario.pattern.detected',
            data={
                'pattern_type': pattern_type,
                'scenarios': scenarios_involved,
                'confidence': confidence
            },
            source='scenario-intelligence',
            priority=EventPriority.NORMAL
        )

        await self.eventbus.publish(event)
        logger.info(f"🔍 Published: scenario.pattern.detected ({pattern_type})")

    async def publish_learning_updated(
        self,
        scenario_id: str,
        statistics: Dict[str, Any]
    ):
        """
        Publish: scenario.learning.updated

        Args:
            scenario_id: Scenario ID
            statistics: Updated statistics
        """
        if not self.eventbus:
            await self.initialize()

        event = Event.create(
            event_type='scenario.learning.updated',
            data={
                'scenario_id': scenario_id,
                'statistics': statistics
            },
            source='scenario-intelligence',
            priority=EventPriority.LOW
        )

        await self.eventbus.publish(event)
        logger.debug(f"📊 Published: scenario.learning.updated ({scenario_id})")


# Global instance
scenario_event_publisher = ScenarioEventPublisher()


# =====================================================================
# Helper functions
# =====================================================================

async def initialize_eventbus(backend: str = 'memory'):
    """
    Initialize EventBus integration

    Args:
        backend: EventBus backend ('memory', 'redis', 'rabbitmq')
    """
    global scenario_event_publisher
    scenario_event_publisher = ScenarioEventPublisher(backend)
    await scenario_event_publisher.initialize()
    logger.info("✅ Scenario EventBus integration initialized")
