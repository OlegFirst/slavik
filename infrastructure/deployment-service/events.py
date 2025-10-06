"""
Deployment Service EventBus Integration
=======================================

Publishes deployment events to the platform EventBus.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from infrastructure.eventbus.core.events import Event, EventPriority
from infrastructure.eventbus.factory import create_eventbus_from_env
from config import config

logger = logging.getLogger(__name__)


class DeploymentEventPublisher:
    """
    Publishes deployment-related events to EventBus.

    Events published:
    - deployment.started
    - deployment.completed
    - deployment.failed
    - deployment.service_started
    - deployment.service_failed
    - deployment.rollback_started
    - deployment.rollback_completed
    """

    def __init__(self):
        """Initialize EventBus connection"""
        try:
            self.eventbus = create_eventbus_from_env()
            logger.info(f"EventBus initialized with backend: {config.EVENTBUS_BACKEND}")
        except Exception as e:
            logger.error(f"Failed to initialize EventBus: {e}")
            self.eventbus = None

    async def publish_deployment_started(
        self,
        deployment_id: str,
        tenant_id: str,
        services: list,
        strategy: str,
        correlation_id: Optional[str] = None
    ):
        """Publish deployment started event"""
        await self._publish_event(
            event_type="deployment.started",
            data={
                "deployment_id": deployment_id,
                "services": services,
                "strategy": strategy,
                "started_at": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            correlation_id=correlation_id
        )

    async def publish_deployment_completed(
        self,
        deployment_id: str,
        tenant_id: str,
        deployed_services: list,
        failed_services: list,
        duration_seconds: int,
        correlation_id: Optional[str] = None
    ):
        """Publish deployment completed event"""
        await self._publish_event(
            event_type="deployment.completed",
            data={
                "deployment_id": deployment_id,
                "deployed_services": deployed_services,
                "failed_services": failed_services,
                "duration_seconds": duration_seconds,
                "success": len(failed_services) == 0,
                "completed_at": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            correlation_id=correlation_id
        )

    async def publish_deployment_failed(
        self,
        deployment_id: str,
        tenant_id: str,
        error_message: str,
        failed_service: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Publish deployment failed event"""
        await self._publish_event(
            event_type="deployment.failed",
            data={
                "deployment_id": deployment_id,
                "error_message": error_message,
                "failed_service": failed_service,
                "failed_at": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id,
            priority=EventPriority.CRITICAL,
            correlation_id=correlation_id
        )

    async def publish_service_started(
        self,
        service_name: str,
        deployment_id: str,
        tenant_id: str,
        correlation_id: Optional[str] = None
    ):
        """Publish service started event"""
        await self._publish_event(
            event_type="deployment.service_started",
            data={
                "service_name": service_name,
                "deployment_id": deployment_id,
                "started_at": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL,
            correlation_id=correlation_id
        )

    async def publish_service_failed(
        self,
        service_name: str,
        deployment_id: str,
        tenant_id: str,
        error_message: str,
        correlation_id: Optional[str] = None
    ):
        """Publish service failed event"""
        await self._publish_event(
            event_type="deployment.service_failed",
            data={
                "service_name": service_name,
                "deployment_id": deployment_id,
                "error_message": error_message,
                "failed_at": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            correlation_id=correlation_id
        )

    async def publish_rollback_started(
        self,
        deployment_id: str,
        tenant_id: str,
        reason: str,
        correlation_id: Optional[str] = None
    ):
        """Publish rollback started event"""
        await self._publish_event(
            event_type="deployment.rollback_started",
            data={
                "deployment_id": deployment_id,
                "reason": reason,
                "started_at": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id,
            priority=EventPriority.CRITICAL,
            correlation_id=correlation_id
        )

    async def publish_rollback_completed(
        self,
        deployment_id: str,
        tenant_id: str,
        success: bool,
        correlation_id: Optional[str] = None
    ):
        """Publish rollback completed event"""
        await self._publish_event(
            event_type="deployment.rollback_completed",
            data={
                "deployment_id": deployment_id,
                "success": success,
                "completed_at": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id,
            priority=EventPriority.CRITICAL,
            correlation_id=correlation_id
        )

    async def _publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        tenant_id: str,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None
    ):
        """Internal method to publish event"""
        if not self.eventbus:
            logger.warning(f"EventBus not available, skipping event: {event_type}")
            return

        try:
            event = Event.create(
                event_type=event_type,
                data=data,
                source=config.SERVICE_NAME,
                tenant_id=tenant_id,
                priority=priority,
                correlation_id=correlation_id
            )

            await self.eventbus.publish(event)
            logger.info(f"Published event: {event_type} (tenant: {tenant_id})")

        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
