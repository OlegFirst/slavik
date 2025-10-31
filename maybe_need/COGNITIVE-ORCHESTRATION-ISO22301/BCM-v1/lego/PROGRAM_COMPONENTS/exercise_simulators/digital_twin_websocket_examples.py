#!/usr/bin/env python3
"""
Digital Twin WebSocket Client Examples
Demonstrates how to connect and interact with the Digital Twin WebSocket service

This file provides examples for:
1. Basic WebSocket connection
2. Subscribing to Digital Twin topics
3. Handling real-time updates
4. Triggering synchronization
5. Performance monitoring
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DigitalTwinWebSocketClient:
    """Example WebSocket client for Digital Twin real-time updates"""

    def __init__(self, client_id: str, websocket_url: str = "ws://localhost:8999/ws/digital-twin/"):
        self.client_id = client_id
        self.websocket_url = f"{websocket_url}{client_id}"
        self.websocket = None
        self.subscribed_topics: List[str] = []

    async def connect(self):
        """Connect to the Digital Twin WebSocket service"""
        try:
            logger.info(f"Connecting to {self.websocket_url}")
            self.websocket = await websockets.connect(self.websocket_url)
            logger.info(f"Connected as client: {self.client_id}")

            # Start message handler
            await self.handle_messages()

        except Exception as e:
            logger.error(f"Connection failed: {e}")

    async def subscribe_to_topics(self, topics: List[str]):
        """Subscribe to specific Digital Twin topics"""
        if not self.websocket:
            logger.error("Not connected to WebSocket")
            return

        message = {
            "type": "subscribe",
            "topics": topics
        }

        await self.websocket.send(json.dumps(message))
        self.subscribed_topics.extend(topics)
        logger.info(f"Subscribed to topics: {topics}")

    async def trigger_sync(self, twin_id: str):
        """Trigger synchronization for a specific Digital Twin"""
        if not self.websocket:
            logger.error("Not connected to WebSocket")
            return

        message = {
            "type": "sync",
            "twin_id": twin_id
        }

        await self.websocket.send(json.dumps(message))
        logger.info(f"Triggered sync for Digital Twin {twin_id}")

    async def refresh_data(self):
        """Request immediate refresh of cached data"""
        if not self.websocket:
            logger.error("Not connected to WebSocket")
            return

        message = {
            "type": "refresh"
        }

        await self.websocket.send(json.dumps(message))
        logger.info("Requested data refresh")

    async def ping(self):
        """Send ping to check connection"""
        if not self.websocket:
            logger.error("Not connected to WebSocket")
            return

        message = {
            "type": "ping"
        }

        await self.websocket.send(json.dumps(message))

    async def handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.process_message(data)

        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error handling messages: {e}")

    async def process_message(self, data: Dict):
        """Process received WebSocket message"""
        message_type = data.get("type")
        timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        if message_type == "connection":
            logger.info(f"Connection established: {data.get('status')}")

        elif message_type == "subscription":
            logger.info(f"Subscription confirmed: {data.get('topics')}")

        elif message_type == "digital_twins_update":
            await self.handle_digital_twins_update(data)

        elif message_type == "organization_metrics_update":
            await self.handle_organization_metrics_update(data)

        elif message_type == "twin_event":
            await self.handle_twin_event(data)

        elif message_type == "performance_metrics":
            await self.handle_performance_metrics(data)

        elif message_type == "predictive_analytics":
            await self.handle_predictive_analytics(data)

        elif message_type == "sync_response":
            await self.handle_sync_response(data)

        elif message_type == "pong":
            logger.info(f"Pong received at {timestamp}")

        else:
            logger.info(f"Unknown message type: {message_type}")

    async def handle_digital_twins_update(self, data: Dict):
        """Handle Digital Twins update messages"""
        twins_data = data.get("data", {})
        digital_twins = twins_data.get("digital_twins", [])
        count = twins_data.get("count", 0)
        cached = twins_data.get("cached", False)

        logger.info(f"📊 Digital Twins Update: {count} twins {'(cached)' if cached else '(live)'}")

        for twin in digital_twins:
            logger.info(
                f"  Twin {twin['id']}: {twin['name']} "
                f"(Health: {twin['health_score']:.2f}, Status: {twin['sync_status']})"
            )

    async def handle_organization_metrics_update(self, data: Dict):
        """Handle organization metrics update messages"""
        metrics = data.get("data", {})
        cached = metrics.get("cached", False)

        logger.info(f"🏢 Organization Metrics {'(cached)' if cached else '(live)'}:")
        logger.info(f"  Overall Health: {metrics.get('overall_health', 0):.2f}")
        logger.info(f"  Active Twins: {metrics.get('active_twins', 0)}/{metrics.get('total_employees', 0)}")
        logger.info(f"  Sync Success Rate: {metrics.get('sync_success_rate', 0):.1%}")

    async def handle_twin_event(self, data: Dict):
        """Handle Digital Twin event messages"""
        event_type = data.get("event_type")
        event_data = data.get("data", {})
        twin_id = event_data.get("twin_id")

        logger.info(f"🎯 Twin Event: {event_type} for Twin {twin_id}")

        if event_type == "sync_triggered":
            logger.info(f"  ✅ Sync started: {event_data.get('event_data', {}).get('message')}")

        elif event_type == "health_change":
            event_info = event_data.get("event_data", {})
            health_delta = event_info.get("health_delta", 0)
            reason = event_info.get("reason", "Unknown")
            logger.info(f"  ❤️ Health changed by {health_delta:+.3f}: {reason}")

        elif event_type == "risk_alert":
            event_info = event_data.get("event_data", {})
            alert_type = event_info.get("alert_type", "unknown")
            severity = event_info.get("severity", "unknown")
            logger.info(f"  ⚠️ Risk Alert: {alert_type} ({severity} severity)")

        elif event_type == "sync_completed":
            event_info = event_data.get("event_data", {})
            duration = event_info.get("duration", 0)
            data_points = event_info.get("data_points_updated", 0)
            logger.info(f"  🔄 Sync completed in {duration:.1f}s, {data_points} data points updated")

    async def handle_performance_metrics(self, data: Dict):
        """Handle performance metrics messages"""
        metrics = data.get("data", {})

        logger.info("📈 Performance Metrics:")
        logger.info(f"  WebSocket Connections: {metrics.get('websocket_connections', 0)}")
        logger.info(f"  Active Subscriptions: {metrics.get('active_subscriptions', 0)}")
        logger.info(f"  Cache Size: {metrics.get('cache_size', 0)}")
        logger.info(f"  API Response Time: {metrics.get('api_response_time', 0):.3f}s")

    async def handle_predictive_analytics(self, data: Dict):
        """Handle predictive analytics messages"""
        analytics = data.get("data", {})
        predictions = analytics.get("predictions", {})
        confidence = analytics.get("confidence_score", 0)

        logger.info(f"🔮 Predictive Analytics (Confidence: {confidence:.1%}):")

        # Burnout forecast
        burnout_forecast = predictions.get("burnout_forecast", [])
        for forecast in burnout_forecast:
            user_id = forecast.get("user_id")
            risk_score = forecast.get("risk_score", 0)
            logger.info(f"  User {user_id} burnout risk: {risk_score:.1%}")

        # Performance trends
        performance_trends = predictions.get("performance_trends", {})
        overall_trend = performance_trends.get("overall", 0)
        logger.info(f"  Overall performance trend: {overall_trend:.1%}")

    async def handle_sync_response(self, data: Dict):
        """Handle sync response messages"""
        twin_id = data.get("twin_id")
        result = data.get("result", {})
        success = result.get("success", False)
        message = result.get("message", "No message")

        status_emoji = "✅" if success else "❌"
        logger.info(f"{status_emoji} Sync Response for Twin {twin_id}: {message}")

    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from WebSocket")


async def example_basic_connection():
    """Example 1: Basic connection and subscription"""
    logger.info("=== Example 1: Basic Connection ===")

    client = DigitalTwinWebSocketClient("example_client_1")

    try:
        # Connect and subscribe to basic topics
        await client.connect()

    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    finally:
        await client.disconnect()


async def example_full_monitoring():
    """Example 2: Full monitoring with all topics"""
    logger.info("=== Example 2: Full Monitoring ===")

    client = DigitalTwinWebSocketClient("monitoring_client")

    try:
        # Connect to WebSocket
        await client.connect()

        # Subscribe to all available topics
        await client.subscribe_to_topics([
            "digital_twins",
            "metrics",
            "twin_events",
            "performance",
            "analytics"
        ])

        # Keep connection alive for monitoring
        while True:
            await asyncio.sleep(60)  # Send ping every minute
            await client.ping()

    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    finally:
        await client.disconnect()


async def example_interactive_client():
    """Example 3: Interactive client with user commands"""
    logger.info("=== Example 3: Interactive Client ===")

    client = DigitalTwinWebSocketClient("interactive_client")

    try:
        # Connect and subscribe to basic topics
        await client.connect()
        await client.subscribe_to_topics(["digital_twins", "twin_events", "metrics"])

        logger.info("\nAvailable commands:")
        logger.info("  sync <twin_id> - Trigger sync for Digital Twin")
        logger.info("  refresh - Refresh cached data")
        logger.info("  ping - Send ping")
        logger.info("  quit - Exit")

        # Simulate interactive commands
        commands = [
            ("refresh", None),
            ("sync", "1"),
            ("ping", None),
            ("sync", "2"),
        ]

        for command, param in commands:
            await asyncio.sleep(3)  # Wait between commands

            if command == "refresh":
                await client.refresh_data()
            elif command == "sync" and param:
                await client.trigger_sync(param)
            elif command == "ping":
                await client.ping()

        # Keep connection alive for a while to see results
        await asyncio.sleep(15)

    except KeyboardInterrupt:
        logger.info("Interactive client stopped")
    finally:
        await client.disconnect()


async def main():
    """Main function to run examples"""
    print("\n" + "="*60)
    print("🎯 DIGITAL TWIN WEBSOCKET CLIENT EXAMPLES")
    print("="*60)
    print("Make sure the Digital Twin WebSocket service is running:")
    print("  python start_digital_twin_websocket.py")
    print()

    try:
        # Run examples
        await example_basic_connection()
        await asyncio.sleep(2)

        await example_interactive_client()
        await asyncio.sleep(2)

        # Uncomment to run full monitoring example
        # await example_full_monitoring()

    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())