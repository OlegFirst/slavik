"""
Event Publishers
Publish events to the event bus for other services to consume
"""

import httpx
import logging
from typing import Dict, Any
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publish events to event bus"""

    def __init__(self):
        self.eventbus_url = settings.EVENTBUS_URL

    async def publish_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        tenant_id: str,
        source_service: str = "validation"
    ) -> bool:
        """
        Publish event to event bus

        Args:
            event_type: Type of event (e.g., "exercise.completed", "kpi.alert")
            event_data: Event payload
            tenant_id: Tenant ID
            source_service: Source service name

        Returns:
            True if published successfully, False otherwise
        """
        try:
            event_payload = {
                "event_type": event_type,
                "event_data": event_data,
                "tenant_id": tenant_id,
                "source_service": source_service,
                "timestamp": datetime.utcnow().isoformat(),
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.eventbus_url}/api/events/publish",
                    json=event_payload,
                    timeout=5.0
                )

                if response.status_code == 200:
                    logger.info(f"Published event: {event_type}")
                    return True
                else:
                    logger.error(f"Failed to publish event: {event_type}, status: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
            return False

    async def publish_exercise_completed(self, exercise_id: int, exercise_code: str, tenant_id: str):
        """Publish exercise.completed event"""
        await self.publish_event(
            event_type="exercise.completed",
            event_data={
                "exercise_id": exercise_id,
                "exercise_code": exercise_code,
            },
            tenant_id=tenant_id
        )

    async def publish_kpi_alert(self, kpi_code: str, severity: str, tenant_id: str):
        """Publish kpi.alert event"""
        await self.publish_event(
            event_type="kpi.alert",
            event_data={
                "kpi_code": kpi_code,
                "severity": severity,
            },
            tenant_id=tenant_id
        )

    async def publish_audit_finding(self, audit_id: int, finding_id: int, severity: str, tenant_id: str):
        """Publish audit.finding event"""
        await self.publish_event(
            event_type="audit.finding",
            event_data={
                "audit_id": audit_id,
                "finding_id": finding_id,
                "severity": severity,
            },
            tenant_id=tenant_id
        )

    async def publish_capa_closed(self, capa_id: int, capa_number: str, tenant_id: str):
        """Publish capa.closed event"""
        await self.publish_event(
            event_type="capa.closed",
            event_data={
                "capa_id": capa_id,
                "capa_number": capa_number,
            },
            tenant_id=tenant_id
        )


# Singleton instance
event_publisher = EventPublisher()
