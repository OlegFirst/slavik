"""
EventBus Integration for AI Event Manager

Provides event-driven architecture capabilities:
- Publish events when gaps are detected
- Subscribe to platform-wide events
- Real-time event propagation
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Callable, Optional

# Add infrastructure to path
sys.path.insert(0, str(Path(__file__).parents[4]))

from infrastructure.eventbus import create_eventbus, Event, EventPriority

logger = logging.getLogger(__name__)


class EventBusIntegration:
    """
    EventBus integration for AI Event Manager

    Features:
    - Publish event gap detections
    - Subscribe to relevant platform events
    - Support for event priorities
    """

    def __init__(self, backend: str = 'memory', redis_url: str = 'redis://localhost:6379'):
        """
        Initialize EventBus integration

        Args:
            backend: EventBus backend ('memory' or 'redis')
            redis_url: Redis connection URL (for redis backend)
        """
        self.backend = backend
        self.redis_url = redis_url
        self.eventbus = None
        self.subscriptions = []

        # Statistics
        self.events_published = 0
        self.events_received = 0

    async def initialize(self):
        """Initialize EventBus connection"""
        logger.info(f"Initializing EventBus ({self.backend})...")

        try:
            self.eventbus = create_eventbus(
                backend=self.backend,
                redis_url=self.redis_url
            )
            logger.info(" EventBus connection established")

            # Subscribe to relevant events
            await self._setup_subscriptions()

        except Exception as e:
            logger.error(f" EventBus initialization failed: {e}")
            raise

    async def _setup_subscriptions(self):
        """Setup event subscriptions"""
        # Subscribe to workflow events
        sub_id_1 = await self.eventbus.subscribe(
            'workflow.*',
            self._handle_workflow_event
        )
        self.subscriptions.append(sub_id_1)
        logger.info("Subscribed to workflow.* events")

        # Subscribe to DevOps events
        sub_id_2 = await self.eventbus.subscribe(
            'devops.*',
            self._handle_devops_event
        )
        self.subscriptions.append(sub_id_2)
        logger.info("Subscribed to devops.* events")

        # Subscribe to infrastructure events
        sub_id_3 = await self.eventbus.subscribe(
            'infrastructure.*',
            self._handle_infrastructure_event
        )
        self.subscriptions.append(sub_id_3)
        logger.info("Subscribed to infrastructure.* events")

    async def publish(self, event_name: str, data: Dict, priority: str = "normal"):
        """
        Publish event to EventBus

        Args:
            event_name: Event name (e.g., 'event.gap.detected')
            data: Event data
            priority: Event priority (low, normal, high, critical)
        """
        if not self.eventbus:
            logger.warning("EventBus not initialized")
            return

        try:
            # Map priority string to EventPriority enum
            priority_map = {
                'low': EventPriority.LOW,
                'normal': EventPriority.NORMAL,
                'high': EventPriority.HIGH,
                'critical': EventPriority.CRITICAL
            }

            event = Event.create(
                event_type=event_name,
                data=data,
                source='ai-event-manager',
                tenant_id='platform',
                priority=priority_map.get(priority, EventPriority.NORMAL)
            )

            await self.eventbus.publish(event)
            self.events_published += 1

            logger.info(f" Published event: {event_name} (priority: {priority})")

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    async def publish_gap_detected(self, gap: Dict):
        """
        Publish event when gap is detected

        Args:
            gap: Gap details (event_name, severity, recommendations)
        """
        severity = gap.get('severity', 'medium')

        # Map severity to priority
        priority_map = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'normal',
            'low': 'low'
        }

        await self.publish(
            event_name='event.gap.detected',
            data={
                'event_name': gap.get('event_name'),
                'gap_type': gap.get('gap_type'),
                'severity': severity,
                'description': gap.get('description'),
                'recommendations': gap.get('recommendations', []),
                'detected_at': gap.get('detected_at')
            },
            priority=priority_map.get(severity, 'normal')
        )

    async def publish_analysis_complete(self, analysis_results: Dict):
        """
        Publish event when analysis is complete

        Args:
            analysis_results: Complete analysis results
        """
        await self.publish(
            event_name='event.analysis.completed',
            data={
                'total_events_analyzed': analysis_results.get('total_events', 0),
                'gaps_found': analysis_results.get('gaps_count', 0),
                'critical_gaps': analysis_results.get('critical_gaps', 0),
                'recommendations_count': analysis_results.get('recommendations_count', 0),
                'analysis_timestamp': analysis_results.get('timestamp')
            },
            priority='normal'
        )

    async def _handle_workflow_event(self, event: Event):
        """Handle workflow events"""
        self.events_received += 1
        logger.info(f" Received workflow event: {event.event_type}")

        # Process workflow events if needed
        # For now, just log

    async def _handle_devops_event(self, event: Event):
        """Handle DevOps events"""
        self.events_received += 1
        logger.info(f" Received DevOps event: {event.event_type}")

        # Could trigger analysis if DevOps agent detects issues

    async def _handle_infrastructure_event(self, event: Event):
        """Handle infrastructure events"""
        self.events_received += 1
        logger.info(f" Received infrastructure event: {event.event_type}")

    def get_stats(self) -> Dict:
        """Get EventBus statistics"""
        return {
            'backend': self.backend,
            'events_published': self.events_published,
            'events_received': self.events_received,
            'subscriptions_active': len(self.subscriptions)
        }

    async def close(self):
        """Close EventBus connection"""
        if self.eventbus:
            # Unsubscribe from all
            for sub_id in self.subscriptions:
                try:
                    await self.eventbus.unsubscribe(sub_id)
                except:
                    pass

            await self.eventbus.close()
            logger.info("EventBus connection closed")
