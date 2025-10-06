"""
Governance Service - Event Publishers
Publishes events for key governance actions to EventBus
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from typing import Optional, Dict, Any
from datetime import datetime
from shared.eventbus.client import get_eventbus
import logging

logger = logging.getLogger(__name__)


class GovernanceEventPublisher:
    """
    Event publisher for Governance Service

    Publishes events for:
    - Policy lifecycle (created, approved, published, updated, deleted)
    - Role assignments (created, assigned, updated)
    - Resource allocation (created, allocated, updated)
    - Competence records (recorded, gap identified, assessment completed)
    - Objectives (created, updated, progress recorded)
    - Stakeholders (created, updated)
    - Context analysis (created, updated)
    """

    @staticmethod
    async def publish_event(
        event_type: str,
        data: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Generic event publisher

        Args:
            event_type: Event type (e.g., "governance.policy.created")
            data: Event payload
            tenant_id: Tenant identifier

        Returns:
            bool: True if published successfully
        """
        try:
            eventbus = get_eventbus()
            await eventbus.publish(event_type, data, tenant_id=tenant_id)
            logger.info(f"Published event: {event_type} for tenant {tenant_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False

    # ========================================================================
    # POLICY EVENTS
    # ========================================================================

    @staticmethod
    async def policy_created(
        policy_id: int,
        tenant_id: str,
        title: str,
        policy_type: str
    ) -> bool:
        """Policy created event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.policy.created",
            {
                "policy_id": policy_id,
                "title": title,
                "policy_type": policy_type,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def policy_approved(
        policy_id: int,
        tenant_id: str,
        approved_by: str
    ) -> bool:
        """Policy approved event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.policy.approved",
            {
                "policy_id": policy_id,
                "approved_by": approved_by,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def policy_published(
        policy_id: int,
        tenant_id: str
    ) -> bool:
        """Policy published event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.policy.published",
            {
                "policy_id": policy_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def policy_updated(
        policy_id: int,
        tenant_id: str
    ) -> bool:
        """Policy updated event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.policy.updated",
            {
                "policy_id": policy_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def policy_deleted(
        policy_id: int,
        tenant_id: str
    ) -> bool:
        """Policy deleted event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.policy.deleted",
            {
                "policy_id": policy_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    # ========================================================================
    # ROLE EVENTS
    # ========================================================================

    @staticmethod
    async def role_created(
        role_id: int,
        tenant_id: str,
        role_name: str
    ) -> bool:
        """Role created event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.role.created",
            {
                "role_id": role_id,
                "role_name": role_name,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def role_assigned(
        role_id: int,
        tenant_id: str,
        assigned_to: str,
        assigned_to_name: str
    ) -> bool:
        """Role assigned event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.role.assigned",
            {
                "role_id": role_id,
                "assigned_to": assigned_to,
                "assigned_to_name": assigned_to_name,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    # ========================================================================
    # RESOURCE EVENTS
    # ========================================================================

    @staticmethod
    async def resource_created(
        resource_id: int,
        tenant_id: str,
        resource_name: str,
        is_critical: bool
    ) -> bool:
        """Resource created event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.resource.created",
            {
                "resource_id": resource_id,
                "resource_name": resource_name,
                "is_critical": is_critical,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def resource_allocated(
        resource_id: int,
        tenant_id: str,
        availability: str
    ) -> bool:
        """Resource allocated event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.resource.allocated",
            {
                "resource_id": resource_id,
                "availability": availability,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    # ========================================================================
    # COMPETENCE EVENTS
    # ========================================================================

    @staticmethod
    async def competence_recorded(
        competence_id: int,
        tenant_id: str,
        person_id: str,
        gap_exists: bool
    ) -> bool:
        """Competence record created event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.competence.recorded",
            {
                "competence_id": competence_id,
                "person_id": person_id,
                "gap_exists": gap_exists,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def competence_gap_identified(
        competence_id: int,
        tenant_id: str,
        person_id: str,
        competence_area: str
    ) -> bool:
        """Competence gap identified event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.competence.gap_identified",
            {
                "competence_id": competence_id,
                "person_id": person_id,
                "competence_area": competence_area,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    # ========================================================================
    # OBJECTIVE EVENTS
    # ========================================================================

    @staticmethod
    async def objective_created(
        objective_id: int,
        tenant_id: str,
        title: str
    ) -> bool:
        """Objective created event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.objective.created",
            {
                "objective_id": objective_id,
                "title": title,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def objective_updated(
        objective_id: int,
        tenant_id: str,
        progress_percentage: int
    ) -> bool:
        """Objective updated event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.objective.updated",
            {
                "objective_id": objective_id,
                "progress_percentage": progress_percentage,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )

    @staticmethod
    async def objective_completed(
        objective_id: int,
        tenant_id: str
    ) -> bool:
        """Objective completed event"""
        return await GovernanceEventPublisher.publish_event(
            "governance.objective.completed",
            {
                "objective_id": objective_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            tenant_id=tenant_id
        )
