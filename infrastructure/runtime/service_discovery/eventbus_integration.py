"""
EventBus Integration for Service Discovery

Integrates Service Registry with EventBus for immediate detection of:
- Services connecting/disconnecting
- Service heartbeats
- Service health changes

This addresses the requirement: "нахождение в системе но не участие в не
не подротсетность долдна определяться сразу" (being in the system but not
participating, not being connected should be detected immediately)
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta

from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry, Service

logger = logging.getLogger(__name__)


class ServiceDiscoveryEventBusIntegration:
    """
    Integrates Service Registry with EventBus for real-time service monitoring

    Features:
    1. Automatic service registration when services connect to EventBus
    2. Heartbeat monitoring - detect disconnected services immediately
    3. Health status updates via EventBus events
    4. Alerts when services become unresponsive
    """

    def __init__(self, service_registry: ServiceRegistry, eventbus,
                 heartbeat_timeout: int = 60):
        """
        Initialize EventBus integration

        Args:
            service_registry: ServiceRegistry instance
            eventbus: EventBus instance
            heartbeat_timeout: Timeout in seconds before service is considered dead
        """
        self.registry = service_registry
        self.eventbus = eventbus
        self.heartbeat_timeout = heartbeat_timeout

        # Track when services last sent heartbeat
        self.last_heartbeat: Dict[str, datetime] = {}

        # Background task for monitoring
        self._monitoring_task: Optional[asyncio.Task] = None

        # Callbacks for events
        self.on_service_connect: Optional[Callable] = None
        self.on_service_disconnect: Optional[Callable] = None
        self.on_service_unhealthy: Optional[Callable] = None

    async def start(self) -> None:
        """Start EventBus integration"""
        logger.info("Starting Service Discovery EventBus Integration")

        # Subscribe to service events
        await self._subscribe_to_events()

        # Start heartbeat monitoring
        self._monitoring_task = asyncio.create_task(self._monitor_heartbeats())

        logger.info("Service Discovery EventBus Integration started")

    async def stop(self) -> None:
        """Stop EventBus integration"""
        logger.info("Stopping Service Discovery EventBus Integration")

        # Stop monitoring task
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Service Discovery EventBus Integration stopped")

    async def _subscribe_to_events(self) -> None:
        """Subscribe to EventBus events"""

        # Service lifecycle events
        await self.eventbus.subscribe(
            'platform.service.started',
            self._handle_service_started
        )

        await self.eventbus.subscribe(
            'platform.service.stopped',
            self._handle_service_stopped
        )

        await self.eventbus.subscribe(
            'platform.service.heartbeat',
            self._handle_service_heartbeat
        )

        await self.eventbus.subscribe(
            'platform.service.health',
            self._handle_service_health
        )

        logger.info("Subscribed to service events")

    async def _handle_service_started(self, event: Dict[str, Any]) -> None:
        """
        Handle service started event

        Event format:
        {
            'service_name': 'planning-service',
            'orchestrator': 'docker-compose',
            'port': 8011,
            'metadata': {...}
        }
        """
        service_name = event.get('service_name')
        if not service_name:
            logger.warning("Received service.started event without service_name")
            return

        orchestrator = event.get('orchestrator', 'unknown')
        port = event.get('port')
        metadata = event.get('metadata', {})
        dependencies = event.get('dependencies', [])

        # Register service
        service = await self.registry.register(
            service_name=service_name,
            orchestrator=orchestrator,
            metadata=metadata,
            dependencies=dependencies
        )

        # Set port if provided
        if port:
            service.port = port
            await self.registry.update_status(service_name, 'running')

        # Update heartbeat
        self.last_heartbeat[service_name] = datetime.utcnow()

        logger.info(
            f" Service CONNECTED: {service_name} "
            f"(orchestrator: {orchestrator}, port: {port})"
        )

        # Call callback if set
        if self.on_service_connect:
            await self.on_service_connect(service)

        # Publish alert to multiple interested services
        registration_event = {
            'type': 'platform.service_discovery.service_connected',
            'data': {
                'service_name': service_name,
                'orchestrator': orchestrator,
                'port': port,
                'metadata': metadata,
                'dependencies': dependencies,
                'timestamp': datetime.utcnow().isoformat(),
                'registry_id': service_name,  # Registry ID for tracking
                'capabilities': metadata.get('capabilities', []),
                'kpis': metadata.get('kpis', [])
            }
        }

        # Broadcast to all interested services
        await self.eventbus.publish(registration_event)

        # Also publish to specific topics for targeted consumption
        interested_services = [
            'platform.monitoring.service_registered',      # For MIO Manager
            'platform.analytics.new_service',              # For Analytics Specialist
            'platform.policy.service_registered',          # For Policy Engine
            'platform.balancer.service_available',         # For Balancer Service
            'platform.ai_events.service_registered'        # For AI Event Manager
        ]

        for topic in interested_services:
            await self.eventbus.publish({
                'type': topic,
                'data': registration_event['data']
            })

        logger.info(f" Broadcasted registration to {len(interested_services)} interested services")

    async def _handle_service_stopped(self, event: Dict[str, Any]) -> None:
        """
        Handle service stopped event

        Event format:
        {
            'service_name': 'planning-service',
            'reason': 'shutdown'
        }
        """
        service_name = event.get('service_name')
        if not service_name:
            logger.warning("Received service.stopped event without service_name")
            return

        reason = event.get('reason', 'unknown')

        # Update service status
        await self.registry.update_status(service_name, 'stopped')

        # Remove heartbeat tracking
        if service_name in self.last_heartbeat:
            del self.last_heartbeat[service_name]

        logger.warning(
            f"️  Service DISCONNECTED: {service_name} (reason: {reason})"
        )

        # Call callback if set
        if self.on_service_disconnect:
            service = await self.registry.get_service(service_name)
            if service:
                await self.on_service_disconnect(service, reason)

        # Publish disconnect alert to multiple interested services
        disconnect_event = {
            'type': 'platform.service_discovery.service_disconnected',
            'data': {
                'service_name': service_name,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat(),
                'registry_id': service_name
            }
        }

        # Broadcast to all
        await self.eventbus.publish(disconnect_event)

        # Notify interested services
        interested_topics = [
            'platform.monitoring.service_disconnected',    # MIO Manager
            'platform.analytics.service_down',             # Analytics
            'platform.policy.service_failed',              # Policy Engine (for recovery)
            'platform.balancer.service_unavailable',       # Balancer
            'platform.ai_events.service_disconnected'      # AI Event Manager
        ]

        for topic in interested_topics:
            await self.eventbus.publish({
                'type': topic,
                'data': disconnect_event['data']
            })

        logger.info(f" Broadcasted disconnect to {len(interested_topics)} interested services")

    async def _handle_service_heartbeat(self, event: Dict[str, Any]) -> None:
        """
        Handle service heartbeat event

        Event format:
        {
            'service_name': 'planning-service',
            'timestamp': '2025-10-09T12:00:00'
        }
        """
        service_name = event.get('service_name')
        if not service_name:
            return

        # Update heartbeat timestamp
        self.last_heartbeat[service_name] = datetime.utcnow()

        # Update last_seen in registry
        service = await self.registry.get_service(service_name)
        if service:
            service.last_seen = datetime.utcnow()

        logger.debug(f" Heartbeat received from {service_name}")

    async def _handle_service_health(self, event: Dict[str, Any]) -> None:
        """
        Handle service health event

        Event format:
        {
            'service_name': 'planning-service',
            'health_status': 'healthy'  # healthy, unhealthy, degraded
        }
        """
        service_name = event.get('service_name')
        health_status = event.get('health_status')

        if not service_name or not health_status:
            return

        # Update health in registry
        await self.registry.update_health(service_name, health_status)

        logger.info(f" Health update: {service_name} -> {health_status}")

        # Alert if unhealthy
        if health_status in ('unhealthy', 'degraded'):
            if self.on_service_unhealthy:
                service = await self.registry.get_service(service_name)
                if service:
                    await self.on_service_unhealthy(service, health_status)

            # Publish alert
            await self.eventbus.publish({
                'type': 'platform.service_discovery.service_unhealthy',
                'data': {
                    'service_name': service_name,
                    'health_status': health_status,
                    'timestamp': datetime.utcnow().isoformat()
                }
            })

    async def _monitor_heartbeats(self) -> None:
        """
        Background task to monitor service heartbeats

        Detects services that haven't sent heartbeat in heartbeat_timeout seconds
        """
        logger.info(
            f"Starting heartbeat monitor (timeout: {self.heartbeat_timeout}s)"
        )

        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                now = datetime.utcnow()
                timeout = timedelta(seconds=self.heartbeat_timeout)

                # Check all services in registry
                services = await self.registry.list_services()

                for service in services:
                    # Skip if service is already marked as stopped
                    if service.status in ('stopped', 'stopping'):
                        continue

                    # Check heartbeat
                    last_heartbeat = self.last_heartbeat.get(service.name)

                    if last_heartbeat:
                        time_since_heartbeat = now - last_heartbeat

                        if time_since_heartbeat > timeout:
                            # Service hasn't sent heartbeat - mark as failed
                            logger.error(
                                f" CRITICAL: {service.name} hasn't sent heartbeat "
                                f"for {time_since_heartbeat.total_seconds():.0f}s "
                                f"(timeout: {self.heartbeat_timeout}s)"
                            )

                            await self.registry.update_status(service.name, 'failed')
                            await self.registry.update_health(service.name, 'unhealthy')

                            # Call callback
                            if self.on_service_disconnect:
                                await self.on_service_disconnect(
                                    service,
                                    f'Heartbeat timeout ({time_since_heartbeat.total_seconds():.0f}s)'
                                )

                            # Publish critical alert to all interested services
                            timeout_event = {
                                'type': 'platform.service_discovery.heartbeat_timeout',
                                'data': {
                                    'service_name': service.name,
                                    'last_heartbeat': last_heartbeat.isoformat(),
                                    'timeout_seconds': self.heartbeat_timeout,
                                    'timestamp': now.isoformat(),
                                    'registry_id': service.name,
                                    'severity': 'critical'
                                }
                            }

                            # Broadcast main event
                            await self.eventbus.publish(timeout_event)

                            # CRITICAL: Notify all interested services immediately
                            critical_topics = [
                                'platform.monitoring.critical_timeout',        # MIO Manager (immediate action)
                                'platform.analytics.service_timeout',          # Analytics
                                'platform.policy.service_timeout',             # Policy Engine (trigger recovery!)
                                'platform.balancer.service_timeout',           # Balancer (remove from pool)
                                'platform.ai_events.critical_timeout',         # AI Event Manager
                                'platform.alerts.critical'                     # General alerts
                            ]

                            for topic in critical_topics:
                                await self.eventbus.publish({
                                    'type': topic,
                                    'data': timeout_event['data']
                                })

                            logger.error(
                                f" CRITICAL: Broadcasted timeout alert for {service.name} "
                                f"to {len(critical_topics)} services"
                            )

                            # Remove from heartbeat tracking
                            del self.last_heartbeat[service.name]

            except asyncio.CancelledError:
                logger.info("Heartbeat monitor cancelled")
                break

            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}", exc_info=True)
                # Continue monitoring even if error occurs
                await asyncio.sleep(5)


# ============================================================================
# Helper functions for services to use
# ============================================================================

async def publish_service_started(eventbus, service_name: str, orchestrator: str,
                                  port: Optional[int] = None,
                                  metadata: Optional[Dict[str, Any]] = None,
                                  dependencies: Optional[list] = None) -> None:
    """
    Publish service started event

    Services should call this when they start

    Args:
        eventbus: EventBus instance
        service_name: Name of the service
        orchestrator: Orchestrator managing this service
        port: Port number (optional)
        metadata: Additional metadata (optional)
        dependencies: List of dependencies (optional)
    """
    await eventbus.publish({
        'type': 'platform.service.started',
        'data': {
            'service_name': service_name,
            'orchestrator': orchestrator,
            'port': port,
            'metadata': metadata or {},
            'dependencies': dependencies or [],
            'timestamp': datetime.utcnow().isoformat()
        }
    })


async def publish_service_heartbeat(eventbus, service_name: str) -> None:
    """
    Publish service heartbeat event

    Services should call this periodically (every 30s recommended)

    Args:
        eventbus: EventBus instance
        service_name: Name of the service
    """
    await eventbus.publish({
        'type': 'platform.service.heartbeat',
        'data': {
            'service_name': service_name,
            'timestamp': datetime.utcnow().isoformat()
        }
    })


async def publish_service_health(eventbus, service_name: str, health_status: str) -> None:
    """
    Publish service health event

    Args:
        eventbus: EventBus instance
        service_name: Name of the service
        health_status: 'healthy', 'unhealthy', or 'degraded'
    """
    await eventbus.publish({
        'type': 'platform.service.health',
        'data': {
            'service_name': service_name,
            'health_status': health_status,
            'timestamp': datetime.utcnow().isoformat()
        }
    })


async def publish_service_stopped(eventbus, service_name: str, reason: str = 'shutdown') -> None:
    """
    Publish service stopped event

    Services should call this when they stop

    Args:
        eventbus: EventBus instance
        service_name: Name of the service
        reason: Reason for stopping
    """
    await eventbus.publish({
        'type': 'platform.service.stopped',
        'data': {
            'service_name': service_name,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
    })
