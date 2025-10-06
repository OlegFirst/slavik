"""
Planning Service Event Publishers
Publish events to EventBus
"""

import httpx
from typing import Dict, Any

from ..config import settings


async def publish_event(topic: str, data: Dict[str, Any]):
    """
    Publish event to EventBus

    Args:
        topic: Event topic (e.g., "planning.strategy.created")
        data: Event payload
    """
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.EVENTBUS_URL}/events/publish",
                json={
                    "topic": topic,
                    "data": data,
                    "service": settings.SERVICE_NAME,
                },
                timeout=5.0
            )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to publish event {topic}: {e}")
