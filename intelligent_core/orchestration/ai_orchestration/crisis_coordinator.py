"""
Crisis Coordinator
==================

Coordinates multi-service response during crisis situations.

Features:
- Crisis detection from events and metrics
- BC plan activation
- Multi-service coordination
- Status tracking
- Recovery monitoring

Integration with:
- Response Service (plan activation)
- All platform services (coordination)
- EventBus (notifications)
- AI Orchestrator (decision-making)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .service_registry import ServiceRegistry
from infrastructure.eventbus import IEventBus, Event, EventPriority

logger = logging.getLogger(__name__)


class CrisisLevel(Enum):
    """Crisis severity levels"""
    MINOR = 1       # Minor disruption, single service
    MODERATE = 2    # Multiple services, limited impact
    MAJOR = 3       # Significant business impact
    CRITICAL = 4    # Organization-wide crisis
    CATASTROPHIC = 5  # Existential threat


class CrisisStatus(Enum):
    """Crisis response status"""
    DETECTING = "detecting"
    ACTIVATING = "activating"
    COORDINATING = "coordinating"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    FAILED = "failed"


class CrisisCoordinator:
    """
    Coordinates multi-service response during crisis situations.

    Responsibilities:
    1. Detect crisis from events/metrics
    2. Activate appropriate BC plans
    3. Coordinate multi-service response
    4. Track status and progress
    5. Monitor recovery

    Example:
        ```python
        coordinator = CrisisCoordinator(service_registry, event_bus)
        await coordinator.initialize()

        # Detect crisis
        crisis_id = await coordinator.detect_crisis(situation)

        # Activate response
        result = await coordinator.activate_crisis_response(crisis_id)
        ```
    """

    def __init__(
        self,
        service_registry: ServiceRegistry,
        event_bus: IEventBus
    ):
        """
        Initialize Crisis Coordinator.

        Args:
            service_registry: Service registry for service calls
            event_bus: EventBus for coordination
        """
        self.service_registry = service_registry
        self.event_bus = event_bus

        # Active crises tracking
        self.active_crises: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.stats = {
            'total_crises': 0,
            'active_crises': 0,
            'resolved_crises': 0,
            'failed_responses': 0,
            'avg_resolution_time': 0
        }

        self.initialized = False

        logger.info("Crisis Coordinator created")

    async def initialize(self) -> None:
        """Initialize crisis coordinator."""
        # Subscribe to crisis-related events
        await self.event_bus.subscribe(
            'crisis.*',
            self._handle_crisis_event,
            consumer_group='crisis-coordinator'
        )

        await self.event_bus.subscribe(
            'system.health.critical',
            self._handle_health_critical,
            consumer_group='crisis-coordinator'
        )

        self.initialized = True
        logger.info(" Crisis Coordinator initialized")

    async def detect_crisis(
        self,
        situation: Dict[str, Any],
        source: str = 'orchestrator'
    ) -> Optional[str]:
        """
        Detect if situation represents a crisis.

        Args:
            situation: Situation data
            source: Detection source

        Returns:
            Crisis ID if crisis detected, None otherwise
        """
        logger.info(" Analyzing situation for crisis indicators...")

        # Crisis detection logic
        crisis_level = self._assess_crisis_level(situation)

        if crisis_level.value >= CrisisLevel.MAJOR.value:
            # Crisis detected!
            crisis_id = self._create_crisis_id()

            logger.warning(f" CRISIS DETECTED: {crisis_level.name} (ID: {crisis_id})")

            # Create crisis record
            self.active_crises[crisis_id] = {
                'id': crisis_id,
                'level': crisis_level,
                'status': CrisisStatus.DETECTING,
                'situation': situation,
                'detected_at': datetime.utcnow(),
                'source': source,
                'activated_plans': [],
                'coordinated_services': [],
                'events': []
            }

            self.stats['total_crises'] += 1
            self.stats['active_crises'] += 1

            # Publish crisis detected event
            await self._publish_crisis_event(crisis_id, 'crisis.detected')

            return crisis_id

        else:
            logger.info(f" Situation does not constitute crisis (level: {crisis_level.name})")
            return None

    async def activate_crisis_response(
        self,
        crisis_id: str,
        plan_type: str = 'default'
    ) -> Dict[str, Any]:
        """
        Activate crisis response plan.

        Args:
            crisis_id: Crisis identifier
            plan_type: Type of BC plan to activate

        Returns:
            Activation result
        """
        if crisis_id not in self.active_crises:
            return {'success': False, 'error': 'Crisis not found'}

        crisis = self.active_crises[crisis_id]
        logger.warning(f" Activating crisis response for {crisis_id}")

        try:
            # Update status
            crisis['status'] = CrisisStatus.ACTIVATING
            crisis['activation_started_at'] = datetime.utcnow()

            # Step 1: Call Response Service to activate BC plan
            plan_result = await self._activate_bc_plan(crisis, plan_type)

            if not plan_result['success']:
                raise Exception(f"BC plan activation failed: {plan_result.get('error')}")

            crisis['activated_plans'].append(plan_result['plan_id'])
            logger.info(f" BC Plan activated: {plan_result['plan_id']}")

            # Step 2: Coordinate multi-service response
            coordination_result = await self._coordinate_services(crisis)

            crisis['coordinated_services'] = coordination_result['services']
            logger.info(f" {len(coordination_result['services'])} services coordinated")

            # Step 3: Monitor and track
            crisis['status'] = CrisisStatus.COORDINATING
            crisis['coordination_started_at'] = datetime.utcnow()

            # Publish crisis activated event
            await self._publish_crisis_event(crisis_id, 'crisis.response.activated')

            return {
                'success': True,
                'crisis_id': crisis_id,
                'plan_id': plan_result['plan_id'],
                'coordinated_services': crisis['coordinated_services'],
                'status': crisis['status'].value
            }

        except Exception as e:
            logger.error(f" Crisis response activation failed: {e}", exc_info=True)
            crisis['status'] = CrisisStatus.FAILED
            crisis['error'] = str(e)
            self.stats['failed_responses'] += 1

            return {
                'success': False,
                'error': str(e),
                'crisis_id': crisis_id
            }

    async def monitor_crisis_status(self, crisis_id: str) -> Dict[str, Any]:
        """
        Monitor crisis response status.

        Args:
            crisis_id: Crisis identifier

        Returns:
            Status information
        """
        if crisis_id not in self.active_crises:
            return {'exists': False}

        crisis = self.active_crises[crisis_id]

        # Calculate duration
        started_at = crisis.get('detected_at')
        duration = (datetime.utcnow() - started_at).total_seconds() if started_at else 0

        return {
            'exists': True,
            'crisis_id': crisis_id,
            'level': crisis['level'].name,
            'status': crisis['status'].value,
            'duration_seconds': duration,
            'activated_plans': crisis['activated_plans'],
            'coordinated_services': crisis['coordinated_services'],
            'events_count': len(crisis['events'])
        }

    async def resolve_crisis(self, crisis_id: str) -> Dict[str, Any]:
        """
        Mark crisis as resolved.

        Args:
            crisis_id: Crisis identifier

        Returns:
            Resolution result
        """
        if crisis_id not in self.active_crises:
            return {'success': False, 'error': 'Crisis not found'}

        crisis = self.active_crises[crisis_id]
        crisis['status'] = CrisisStatus.RESOLVED
        crisis['resolved_at'] = datetime.utcnow()

        # Calculate metrics
        duration = (crisis['resolved_at'] - crisis['detected_at']).total_seconds()

        # Update stats
        self.stats['active_crises'] -= 1
        self.stats['resolved_crises'] += 1

        # Update average resolution time
        total_resolved = self.stats['resolved_crises']
        current_avg = self.stats['avg_resolution_time']
        self.stats['avg_resolution_time'] = (
            (current_avg * (total_resolved - 1) + duration) / total_resolved
        )

        # Publish resolution event
        await self._publish_crisis_event(crisis_id, 'crisis.resolved')

        logger.info(f" Crisis {crisis_id} resolved in {duration:.1f}s")

        return {
            'success': True,
            'crisis_id': crisis_id,
            'duration_seconds': duration
        }

    # ========================================================================
    # Private Methods
    # ========================================================================

    def _assess_crisis_level(self, situation: Dict[str, Any]) -> CrisisLevel:
        """
        Assess crisis severity level.

        Logic:
        - CATASTROPHIC: Multiple critical systems down
        - CRITICAL: Single critical system down OR organization-wide impact
        - MAJOR: Significant service degradation
        - MODERATE: Limited service impact
        - MINOR: Single service issue
        """
        # Check for explicit crisis indicators
        if situation.get('crisis_declared', False):
            return CrisisLevel.CRITICAL

        # Check service health
        unhealthy_services = situation.get('unhealthy_services', [])
        critical_services = situation.get('critical_services_affected', [])

        if len(critical_services) >= 2:
            return CrisisLevel.CATASTROPHIC

        if len(critical_services) == 1:
            return CrisisLevel.CRITICAL

        if len(unhealthy_services) >= 3:
            return CrisisLevel.MAJOR

        if len(unhealthy_services) >= 1:
            return CrisisLevel.MODERATE

        # Check error rates
        error_rate = situation.get('error_rate', 0)
        if error_rate > 0.5:  # >50% errors
            return CrisisLevel.CRITICAL
        elif error_rate > 0.2:  # >20% errors
            return CrisisLevel.MAJOR
        elif error_rate > 0.1:  # >10% errors
            return CrisisLevel.MODERATE

        return CrisisLevel.MINOR

    async def _activate_bc_plan(
        self,
        crisis: Dict[str, Any],
        plan_type: str
    ) -> Dict[str, Any]:
        """
        Activate BC plan via Response Service.

        Args:
            crisis: Crisis data
            plan_type: Plan type to activate

        Returns:
            Activation result with plan_id
        """
        try:
            # Call Response Service
            result = await self.service_registry.call_service(
                service_name='response',
                method='POST',
                endpoint='/api/v1/bc-plans/activate',
                data={
                    'crisis_id': crisis['id'],
                    'crisis_level': crisis['level'].name,
                    'plan_type': plan_type,
                    'situation': crisis['situation']
                }
            )

            return {
                'success': True,
                'plan_id': result.get('plan_id', 'unknown'),
                'activation_time': result.get('activated_at')
            }

        except Exception as e:
            logger.error(f"BC plan activation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _coordinate_services(self, crisis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate multi-service response.

        Sends coordination events to relevant services.

        Args:
            crisis: Crisis data

        Returns:
            Coordination result
        """
        coordinated_services = []

        # Determine which services need coordination
        situation = crisis['situation']
        services_to_coordinate = self._identify_services_to_coordinate(situation)

        # Send coordination events
        for service_name in services_to_coordinate:
            try:
                # Publish service-specific coordination event
                await self.event_bus.publish(Event.create(
                    event_type=f'crisis.coordinate.{service_name}',
                    data={
                        'crisis_id': crisis['id'],
                        'crisis_level': crisis['level'].name,
                        'service_name': service_name,
                        'action': 'prepare_for_crisis_mode'
                    },
                    source='crisis-coordinator',
                    priority=EventPriority.CRITICAL
                ))

                coordinated_services.append(service_name)
                logger.info(f" Coordinated: {service_name}")

            except Exception as e:
                logger.error(f"Failed to coordinate {service_name}: {e}")

        return {
            'success': True,
            'services': coordinated_services
        }

    def _identify_services_to_coordinate(self, situation: Dict[str, Any]) -> List[str]:
        """
        Identify which services need crisis coordination.

        Args:
            situation: Crisis situation

        Returns:
            List of service names
        """
        # Always coordinate these core services
        core_services = ['bia', 'risk', 'planning', 'response']

        # Add affected services
        affected_services = situation.get('affected_services', [])

        # Combine and deduplicate
        all_services = list(set(core_services + affected_services))

        return all_services

    def _create_crisis_id(self) -> str:
        """Generate unique crisis ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"crisis_{timestamp}_{self.stats['total_crises'] + 1}"

    async def _publish_crisis_event(
        self,
        crisis_id: str,
        event_type: str
    ) -> None:
        """Publish crisis-related event."""
        crisis = self.active_crises.get(crisis_id)
        if not crisis:
            return

        await self.event_bus.publish(Event.create(
            event_type=event_type,
            data={
                'crisis_id': crisis_id,
                'level': crisis['level'].name,
                'status': crisis['status'].value
            },
            source='crisis-coordinator',
            priority=EventPriority.CRITICAL
        ))

        # Record event in crisis
        crisis['events'].append({
            'type': event_type,
            'timestamp': datetime.utcnow()
        })

    async def _handle_crisis_event(self, event: Event) -> None:
        """Handle crisis-related events."""
        logger.debug(f"Crisis event received: {event.type}")
        # Could implement auto-coordination logic here

    async def _handle_health_critical(self, event: Event) -> None:
        """Handle critical health events."""
        logger.warning(f"Critical health event: {event.type}")

        # Auto-detect crisis from critical health events
        situation = {
            'crisis_declared': False,
            'unhealthy_services': event.data.get('unhealthy_services', []),
            'critical_services_affected': event.data.get('critical_services', []),
            'error_rate': event.data.get('error_rate', 0),
            'source': 'health_monitor'
        }

        crisis_id = await self.detect_crisis(situation, source='health_monitor')

        if crisis_id:
            # Auto-activate if critical
            await self.activate_crisis_response(crisis_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get crisis coordinator statistics."""
        return {
            **self.stats,
            'active_crisis_ids': list(self.active_crises.keys())
        }
