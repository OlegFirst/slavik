"""
EventBus service integration for Compliance Module

Migrated from: /services/BCM_1/document_processor-обьедененный/events/eventbus.py
Date: 2025-10-01
Changes: source changed from 'document-processor' to 'compliance'
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EventBusService:
    """EventBus integration service for Compliance Module"""

    def __init__(self, config):
        self.config = config
        self.redis_client: Optional[Any] = None
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.subscriptions: Dict[str, Callable] = {}
        self.running = False

    async def connect(self):
        """Connect to Redis and HTTP services"""
        try:
            # Connect to Redis for pub/sub
            import redis.asyncio as aioredis
            self.redis_client = aioredis.from_url(
                self.config.REDIS_URL,
                decode_responses=True,
                max_connections=20
            )

            # Create HTTP session for EventBus API calls
            timeout = aiohttp.ClientTimeout(total=30)
            self.http_session = aiohttp.ClientSession(timeout=timeout)

            # Test connections
            await self.redis_client.ping()
            await self._test_eventbus_connection()

            logger.info("Connected to EventBus services")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to EventBus: {str(e)}")
            return False

    async def disconnect(self):
        """Disconnect from services"""
        self.running = False

        if self.redis_client:
            await self.redis_client.close()

        if self.http_session:
            await self.http_session.close()

        logger.info("Disconnected from EventBus services")

    def is_connected(self) -> bool:
        """Check if connected to services"""
        return (
            self.redis_client is not None and
            self.http_session is not None and
            not self.http_session.closed
        )

    async def subscribe(self, pattern: str, handler: Callable):
        """Subscribe to events matching pattern"""
        if pattern in self.subscriptions:
            logger.warning(f"Already subscribed to pattern: {pattern}")
            return

        self.subscriptions[pattern] = handler
        logger.info(f"Subscribed to event pattern: {pattern}")

        # Start listening if not already running
        if not self.running:
            self.running = True
            asyncio.create_task(self._listen_for_events())

    async def _listen_for_events(self):
        """Listen for events from Redis pub/sub"""
        try:
            pubsub = self.redis_client.pubsub()

            # Subscribe to all BCM events
            await pubsub.psubscribe("bcm.*")

            logger.info("Started listening for events")

            while self.running:
                try:
                    message = await pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'pmessage':
                        await self._handle_message(message)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")

        except Exception as e:
            logger.error(f"Error in event listener: {str(e)}")
        finally:
            if pubsub:
                await pubsub.unsubscribe()
                await pubsub.close()

    async def _handle_message(self, message):
        """Handle incoming event message"""
        try:
            channel = message['channel']
            data = json.loads(message['data'])

            event_type = data.get('event_type')
            if not event_type:
                logger.warning("Received message without event_type")
                return

            # Find matching subscription handlers
            for pattern, handler in self.subscriptions.items():
                if self._pattern_matches(pattern, event_type):
                    try:
                        await handler(data)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {str(e)}")

        except json.JSONDecodeError:
            logger.error("Received invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")

    def _pattern_matches(self, pattern: str, event_type: str) -> bool:
        """Check if event type matches subscription pattern"""
        if pattern == "*":
            return True

        pattern_parts = pattern.split(".")
        event_parts = event_type.split(".")

        if len(pattern_parts) != len(event_parts):
            return False

        for pattern_part, event_part in zip(pattern_parts, event_parts):
            if pattern_part != "*" and pattern_part != event_part:
                return False

        return True

    async def publish(self, event_data: Dict[str, Any]):
        """Publish event to EventBus"""
        try:
            # Validate required fields
            if 'event_type' not in event_data:
                raise ValueError("Event must have 'event_type' field")

            if 'tenant_id' not in event_data:
                raise ValueError("Event must have 'tenant_id' field")

            # Add timestamp if not present
            if 'timestamp' not in event_data:
                event_data['timestamp'] = datetime.utcnow().isoformat()

            # Add source information (CHANGED from 'document-processor' to 'compliance')
            event_data['source'] = 'compliance'

            # Publish via HTTP API
            async with self.http_session.post(
                f"{self.config.EVENTBUS_URL}/api/events/publish",
                json=event_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status in [200, 201, 202]:
                    logger.info(f"Published event: {event_data['event_type']}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to publish event: {response.status} - {error_text}")
                    return False

        except Exception as e:
            logger.error(f"Error publishing event: {str(e)}")
            return False

    async def get_event_history(self, tenant_id: str, event_type: Optional[str] = None, limit: int = 100):
        """Get event history from EventBus"""
        try:
            params = {
                'tenant_id': tenant_id,
                'limit': limit
            }

            if event_type:
                params['event_type'] = event_type

            async with self.http_session.get(
                f"{self.config.EVENTBUS_URL}/api/events/history",
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get event history: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error getting event history: {str(e)}")
            return None

    async def _test_eventbus_connection(self):
        """Test connection to EventBus API"""
        try:
            async with self.http_session.get(
                f"{self.config.EVENTBUS_URL}/health"
            ) as response:
                if response.status == 200:
                    logger.info("EventBus API connection verified")
                else:
                    raise Exception(f"EventBus health check failed: {response.status}")

        except Exception as e:
            logger.error(f"EventBus connection test failed: {str(e)}")
            raise
