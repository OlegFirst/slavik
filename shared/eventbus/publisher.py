"""
Event Publisher
===============

Helper class for publishing events to EventBus.
"""

from typing import Dict, Any, Optional
from shared.eventbus.client import get_eventbus


class EventPublisher:
    """
    Helper for publishing events.

    Simplifies event publishing with consistent patterns.

    Example:
        ```python
        publisher = EventPublisher(service_name="validation")

        await publisher.publish_created("exercise", exercise_id, exercise_data)
        await publisher.publish_updated("exercise", exercise_id, changes)
        await publisher.publish_deleted("exercise", exercise_id)
        ```
    """

    def __init__(self, service_name: str):
        """
        Initialize event publisher.

        Args:
            service_name: Name of the service (e.g., "validation", "documents")
        """
        self.service_name = service_name

    async def publish(
        self,
        entity: str,
        action: str,
        entity_id: int,
        data: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Publish generic event.

        Args:
            entity: Entity type (e.g., "exercise", "document")
            action: Action performed (e.g., "created", "updated")
            entity_id: Entity identifier
            data: Event data
            tenant_id: Tenant identifier

        Returns:
            bool: True if published successfully
        """
        eventbus = get_eventbus()

        event_type = f"{entity}.{action}"
        event_data = {
            f"{entity}_id": entity_id,
            "tenant_id": tenant_id,
            **data
        }

        return await eventbus.publish(event_type, event_data, tenant_id)

    async def publish_created(
        self,
        entity: str,
        entity_id: int,
        data: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Publish entity created event.

        Example:
            ```python
            await publisher.publish_created(
                "exercise",
                exercise.id,
                {
                    "exercise_type": exercise.exercise_type,
                    "planned_date": exercise.planned_date
                },
                tenant_id=exercise.tenant_id
            )
            ```
        """
        return await self.publish(entity, "created", entity_id, data, tenant_id)

    async def publish_updated(
        self,
        entity: str,
        entity_id: int,
        changes: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Publish entity updated event.

        Example:
            ```python
            await publisher.publish_updated(
                "exercise",
                exercise_id,
                {"status": "IN_PROGRESS"},
                tenant_id=tenant_id
            )
            ```
        """
        return await self.publish(entity, "updated", entity_id, changes, tenant_id)

    async def publish_deleted(
        self,
        entity: str,
        entity_id: int,
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Publish entity deleted event.

        Example:
            ```python
            await publisher.publish_deleted("exercise", exercise_id, tenant_id)
            ```
        """
        return await self.publish(entity, "deleted", entity_id, {}, tenant_id)

    async def publish_status_changed(
        self,
        entity: str,
        entity_id: int,
        old_status: str,
        new_status: str,
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Publish status change event.

        Example:
            ```python
            await publisher.publish_status_changed(
                "exercise",
                exercise_id,
                old_status="PLANNED",
                new_status="IN_PROGRESS",
                tenant_id=tenant_id
            )
            ```
        """
        return await self.publish(
            entity,
            "status_changed",
            entity_id,
            {"old_status": old_status, "new_status": new_status},
            tenant_id
        )
