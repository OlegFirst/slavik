"""
EventBus Client for Marketplace Service
Publishes marketplace events to the platform EventBus
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")


class EventBusClient:
    """Client for publishing events to EventBus"""

    def __init__(self):
        self.base_url = EVENTBUS_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def publish(
        self,
        event_type: str,
        tenant_id: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Publish event to EventBus"""
        try:
            event = {
                "event_type": event_type,
                "tenant_id": tenant_id,
                "data": data,
                "user_id": user_id,
                "correlation_id": correlation_id,
                "metadata": {
                    "source": "marketplace",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            response = await self.client.post(
                f"{self.base_url}/api/events/publish",
                json=event
            )

            if response.status_code == 200:
                logger.info(f"Event published: {event_type}")
                return response.json()
            else:
                logger.error(f"Failed to publish event: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ========================================================================
    # Specialist Events
    # ========================================================================

    async def specialist_registered(
        self,
        specialist_id: int,
        user_id: str,
        tenant_id: str,
        name: str,
        specializations: list
    ):
        """Specialist registered event"""
        await self.publish(
            event_type="marketplace.specialist.registered",
            tenant_id=tenant_id,
            data={
                "specialist_id": specialist_id,
                "user_id": user_id,
                "name": name,
                "specializations": specializations
            },
            user_id=user_id
        )

    async def specialist_verified(
        self,
        specialist_id: int,
        tenant_id: str,
        verified: bool,
        verified_by: str
    ):
        """Specialist verified event"""
        await self.publish(
            event_type="marketplace.specialist.verified",
            tenant_id=tenant_id,
            data={
                "specialist_id": specialist_id,
                "verified": verified,
                "verified_by": verified_by
            },
            user_id=verified_by
        )

    async def specialist_profile_updated(
        self,
        specialist_id: int,
        tenant_id: str,
        user_id: str,
        updated_fields: list
    ):
        """Specialist profile updated event"""
        await self.publish(
            event_type="marketplace.specialist.profile_updated",
            tenant_id=tenant_id,
            data={
                "specialist_id": specialist_id,
                "updated_fields": updated_fields
            },
            user_id=user_id
        )

    # ========================================================================
    # Project Events
    # ========================================================================

    async def project_created(
        self,
        project_id: int,
        client_id: str,
        tenant_id: str,
        title: str,
        service_type: str,
        budget_range: dict
    ):
        """Project created event"""
        await self.publish(
            event_type="marketplace.project.created",
            tenant_id=tenant_id,
            data={
                "project_id": project_id,
                "client_id": client_id,
                "title": title,
                "service_type": service_type,
                "budget_range": budget_range
            },
            user_id=client_id
        )

    async def project_published(
        self,
        project_id: int,
        tenant_id: str,
        client_id: str,
        title: str
    ):
        """Project published event"""
        await self.publish(
            event_type="marketplace.project.published",
            tenant_id=tenant_id,
            data={
                "project_id": project_id,
                "title": title
            },
            user_id=client_id
        )

    async def project_assigned(
        self,
        project_id: int,
        specialist_id: int,
        tenant_id: str,
        client_id: str
    ):
        """Project assigned to specialist event"""
        await self.publish(
            event_type="marketplace.project.assigned",
            tenant_id=tenant_id,
            data={
                "project_id": project_id,
                "specialist_id": specialist_id
            },
            user_id=client_id
        )

    async def project_completed(
        self,
        project_id: int,
        specialist_id: int,
        tenant_id: str,
        client_id: str
    ):
        """Project completed event"""
        await self.publish(
            event_type="marketplace.project.completed",
            tenant_id=tenant_id,
            data={
                "project_id": project_id,
                "specialist_id": specialist_id
            },
            user_id=client_id
        )

    # ========================================================================
    # Proposal Events
    # ========================================================================

    async def proposal_submitted(
        self,
        proposal_id: int,
        project_id: int,
        specialist_id: int,
        tenant_id: str,
        user_id: str,
        proposed_budget: float
    ):
        """Proposal submitted event"""
        await self.publish(
            event_type="marketplace.proposal.submitted",
            tenant_id=tenant_id,
            data={
                "proposal_id": proposal_id,
                "project_id": project_id,
                "specialist_id": specialist_id,
                "proposed_budget": proposed_budget
            },
            user_id=user_id
        )

    async def proposal_accepted(
        self,
        proposal_id: int,
        project_id: int,
        specialist_id: int,
        tenant_id: str,
        client_id: str
    ):
        """Proposal accepted event"""
        await self.publish(
            event_type="marketplace.proposal.accepted",
            tenant_id=tenant_id,
            data={
                "proposal_id": proposal_id,
                "project_id": project_id,
                "specialist_id": specialist_id
            },
            user_id=client_id
        )

    async def proposal_rejected(
        self,
        proposal_id: int,
        project_id: int,
        tenant_id: str,
        client_id: str,
        reason: str = None
    ):
        """Proposal rejected event"""
        await self.publish(
            event_type="marketplace.proposal.rejected",
            tenant_id=tenant_id,
            data={
                "proposal_id": proposal_id,
                "project_id": project_id,
                "reason": reason
            },
            user_id=client_id
        )

    # ========================================================================
    # Review Events
    # ========================================================================

    async def review_created(
        self,
        review_id: int,
        project_id: int,
        specialist_id: int,
        tenant_id: str,
        reviewer_id: str,
        rating: int,
        title: str = None
    ):
        """Review created event"""
        await self.publish(
            event_type="marketplace.review.created",
            tenant_id=tenant_id,
            data={
                "review_id": review_id,
                "project_id": project_id,
                "specialist_id": specialist_id,
                "rating": rating,
                "title": title
            },
            user_id=reviewer_id
        )

    async def review_responded(
        self,
        review_id: int,
        specialist_id: int,
        tenant_id: str,
        user_id: str,
        response_text: str
    ):
        """Specialist responded to review event"""
        await self.publish(
            event_type="marketplace.review.responded",
            tenant_id=tenant_id,
            data={
                "review_id": review_id,
                "specialist_id": specialist_id,
                "response_length": len(response_text)
            },
            user_id=user_id
        )


# Global instance
eventbus_client = EventBusClient()
