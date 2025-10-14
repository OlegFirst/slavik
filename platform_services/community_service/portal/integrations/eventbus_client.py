"""
EventBus Integration for Portal Service
Emits events for Portal activities (articles, scenarios, forum, reputation)
"""

import httpx
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")


class EventBusClient:
    """Client for publishing Portal events to EventBus"""

    def __init__(self, eventbus_url: str = EVENTBUS_URL):
        self.eventbus_url = eventbus_url
        self.publish_endpoint = f"{eventbus_url}/api/events/publish"

    async def publish_event(
        self,
        event_type: str,
        tenant_id: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        event_id: Optional[str] = None
    ) -> bool:
        """
        Publish event to EventBus

        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            event_payload = {
                "event_type": event_type,
                "tenant_id": tenant_id,
                "data": data,
                "user_id": user_id,
                "correlation_id": correlation_id,
                "event_id": event_id,
                "metadata": {
                    "source": "portal_service",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(self.publish_endpoint, json=event_payload)

                if response.status_code == 200:
                    logger.info(f"Event published: {event_type} for tenant {tenant_id}")
                    return True
                else:
                    logger.warning(f"EventBus returned {response.status_code}: {response.text}")
                    return False

        except httpx.TimeoutException:
            logger.warning(f"EventBus timeout for event {event_type}")
            return False
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            return False

    # ========================================================================
    # Knowledge Hub Events
    # ========================================================================

    async def article_created(
        self,
        tenant_id: str,
        article_id: int,
        title: str,
        category: str,
        author_id: str,
        ai_generated: bool = False
    ):
        """Emit event when article is created"""
        return await self.publish_event(
            event_type="portal.knowledge.article_created",
            tenant_id=tenant_id,
            data={
                "article_id": article_id,
                "title": title,
                "category": category,
                "ai_generated": ai_generated
            },
            user_id=author_id,
            event_id=f"article_created_{article_id}"
        )

    async def article_published(
        self,
        tenant_id: str,
        article_id: int,
        title: str,
        category: str,
        author_id: str
    ):
        """Emit event when article is published"""
        return await self.publish_event(
            event_type="portal.knowledge.article_published",
            tenant_id=tenant_id,
            data={
                "article_id": article_id,
                "title": title,
                "category": category
            },
            user_id=author_id,
            event_id=f"article_published_{article_id}"
        )

    async def article_verified(
        self,
        tenant_id: str,
        article_id: int,
        verifier_id: str,
        verified: bool
    ):
        """Emit event when article is verified"""
        return await self.publish_event(
            event_type="portal.knowledge.article_verified",
            tenant_id=tenant_id,
            data={
                "article_id": article_id,
                "verified": verified
            },
            user_id=verifier_id,
            event_id=f"article_verified_{article_id}"
        )

    # ========================================================================
    # Scenario Events
    # ========================================================================

    async def scenario_deployed(
        self,
        tenant_id: str,
        scenario_id: int,
        scenario_name: str,
        exercise_id: int,
        user_id: str
    ):
        """Emit event when scenario is deployed as exercise"""
        return await self.publish_event(
            event_type="portal.scenarios.deployed",
            tenant_id=tenant_id,
            data={
                "scenario_id": scenario_id,
                "scenario_name": scenario_name,
                "exercise_id": exercise_id
            },
            user_id=user_id,
            correlation_id=f"exercise_{exercise_id}"
        )

    async def scenario_reviewed(
        self,
        tenant_id: str,
        scenario_id: int,
        review_id: int,
        rating: int,
        user_id: str
    ):
        """Emit event when scenario is reviewed"""
        return await self.publish_event(
            event_type="portal.scenarios.reviewed",
            tenant_id=tenant_id,
            data={
                "scenario_id": scenario_id,
                "review_id": review_id,
                "rating": rating
            },
            user_id=user_id
        )

    # ========================================================================
    # Forum Events
    # ========================================================================

    async def topic_created(
        self,
        tenant_id: str,
        topic_id: int,
        title: str,
        category_id: int,
        author_id: str,
        linked_article_id: Optional[int] = None
    ):
        """Emit event when forum topic is created"""
        return await self.publish_event(
            event_type="portal.forum.topic_created",
            tenant_id=tenant_id,
            data={
                "topic_id": topic_id,
                "title": title,
                "category_id": category_id,
                "linked_article_id": linked_article_id
            },
            user_id=author_id,
            event_id=f"topic_created_{topic_id}"
        )

    async def post_created(
        self,
        tenant_id: str,
        post_id: int,
        topic_id: int,
        author_id: str,
        parent_post_id: Optional[int] = None
    ):
        """Emit event when forum post is created"""
        return await self.publish_event(
            event_type="portal.forum.post_created",
            tenant_id=tenant_id,
            data={
                "post_id": post_id,
                "topic_id": topic_id,
                "parent_post_id": parent_post_id
            },
            user_id=author_id
        )

    async def solution_marked(
        self,
        tenant_id: str,
        topic_id: int,
        post_id: int,
        author_id: str
    ):
        """Emit event when post is marked as solution"""
        return await self.publish_event(
            event_type="portal.forum.solution_marked",
            tenant_id=tenant_id,
            data={
                "topic_id": topic_id,
                "post_id": post_id
            },
            user_id=author_id,
            event_id=f"solution_marked_{post_id}"
        )

    # ========================================================================
    # Moderation Events
    # ========================================================================

    async def content_flagged(
        self,
        tenant_id: str,
        flag_id: int,
        content_type: str,  # "topic" or "post"
        content_id: int,
        reason: str,
        reporter_id: str
    ):
        """Emit event when content is flagged"""
        return await self.publish_event(
            event_type="portal.forum.content_flagged",
            tenant_id=tenant_id,
            data={
                "flag_id": flag_id,
                "content_type": content_type,
                "content_id": content_id,
                "reason": reason
            },
            user_id=reporter_id
        )

    async def moderation_action(
        self,
        tenant_id: str,
        flag_id: int,
        action: str,  # "approved", "rejected", "hidden", "deleted"
        moderator_id: str
    ):
        """Emit event when moderation action is taken"""
        return await self.publish_event(
            event_type="portal.forum.moderation_action",
            tenant_id=tenant_id,
            data={
                "flag_id": flag_id,
                "action": action
            },
            user_id=moderator_id
        )

    # ========================================================================
    # Reputation & Gamification Events
    # ========================================================================

    async def reputation_earned(
        self,
        tenant_id: str,
        user_id: str,
        points: int,
        event_type: str,  # "topic_created", "post_upvoted", etc.
        new_level: Optional[str] = None
    ):
        """Emit event when user earns reputation"""
        return await self.publish_event(
            event_type="portal.gamification.reputation_earned",
            tenant_id=tenant_id,
            data={
                "points": points,
                "reason": event_type,
                "new_level": new_level
            },
            user_id=user_id
        )

    async def badge_earned(
        self,
        tenant_id: str,
        user_id: str,
        badge_id: int,
        badge_name: str,
        badge_tier: str
    ):
        """Emit event when user earns a badge"""
        return await self.publish_event(
            event_type="portal.gamification.badge_earned",
            tenant_id=tenant_id,
            data={
                "badge_id": badge_id,
                "badge_name": badge_name,
                "badge_tier": badge_tier
            },
            user_id=user_id,
            event_id=f"badge_earned_{user_id}_{badge_id}"
        )


# Singleton instance
eventbus_client = EventBusClient()
