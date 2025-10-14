"""
WebSocket Manager for BCM API Gateway
Handles real-time connections and live data updates
"""

from typing import Dict, Set, List, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Store active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Store client subscriptions by topic
        self.subscriptions: Dict[str, Set[str]] = {}
        # Store client metadata
        self.client_metadata: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str, metadata: Dict = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_metadata[client_id] = metadata or {}
        logger.info(f"Client {client_id} connected")

        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)

    def disconnect(self, client_id: str):
        """Remove client connection and clean up subscriptions"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Remove from all subscriptions
        for topic in self.subscriptions:
            self.subscriptions[topic].discard(client_id)

        if client_id in self.client_metadata:
            del self.client_metadata[client_id]

        logger.info(f"Client {client_id} disconnected")

    async def subscribe(self, client_id: str, topics: List[str]):
        """Subscribe client to specific topics"""
        for topic in topics:
            if topic not in self.subscriptions:
                self.subscriptions[topic] = set()
            self.subscriptions[topic].add(client_id)

        if client_id in self.active_connections:
            await self.send_personal_message({
                "type": "subscription",
                "status": "subscribed",
                "topics": topics,
                "timestamp": datetime.utcnow().isoformat()
            }, self.active_connections[client_id])

    async def unsubscribe(self, client_id: str, topics: List[str]):
        """Unsubscribe client from specific topics"""
        for topic in topics:
            if topic in self.subscriptions:
                self.subscriptions[topic].discard(client_id)

    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")

    async def broadcast_to_topic(self, topic: str, message: Dict):
        """Broadcast message to all clients subscribed to topic"""
        if topic in self.subscriptions:
            disconnected = []
            for client_id in self.subscriptions[topic]:
                if client_id in self.active_connections:
                    try:
                        await self.active_connections[client_id].send_json(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to {client_id}: {e}")
                        disconnected.append(client_id)

            # Clean up disconnected clients
            for client_id in disconnected:
                self.disconnect(client_id)

    async def broadcast_all(self, message: Dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)


class LiveDataManager:
    """Manages live data streams for different BCM components"""

    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.update_tasks: Dict[str, asyncio.Task] = {}

    async def start_metrics_stream(self, interval: int = 5):
        """Stream system metrics at regular intervals"""
        async def stream_metrics():
            while True:
                try:
                    # Get current metrics (mock for now, replace with real data)
                    metrics = {
                        "type": "metrics_update",
                        "data": {
                            "cpu": 45.2,
                            "memory": 62.8,
                            "disk": 38.5,
                            "network": 125.6,
                            "active_users": 42,
                            "response_time": 0.234
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }

                    await self.manager.broadcast_to_topic("metrics", metrics)
                    await asyncio.sleep(interval)

                except Exception as e:
                    logger.error(f"Error in metrics stream: {e}")
                    await asyncio.sleep(interval)

        if "metrics" not in self.update_tasks:
            self.update_tasks["metrics"] = asyncio.create_task(stream_metrics())

    async def start_service_health_stream(self, interval: int = 10):
        """Stream service health status"""
        async def stream_health():
            while True:
                try:
                    # Get service health (mock for now)
                    health = {
                        "type": "health_update",
                        "data": {
                            "services": [
                                {"name": "Odoo", "status": "healthy", "uptime": "3h 45m"},
                                {"name": "AI Orchestrator", "status": "healthy", "uptime": "3h 45m"},
                                {"name": "Document Processor", "status": "warning", "uptime": "2h 12m"}
                            ]
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }

                    await self.manager.broadcast_to_topic("health", health)
                    await asyncio.sleep(interval)

                except Exception as e:
                    logger.error(f"Error in health stream: {e}")
                    await asyncio.sleep(interval)

        if "health" not in self.update_tasks:
            self.update_tasks["health"] = asyncio.create_task(stream_health())

    async def send_notification(self, notification: Dict):
        """Send real-time notification"""
        message = {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_topic("notifications", message)

    async def send_alert(self, alert: Dict):
        """Send real-time alert"""
        message = {
            "type": "alert",
            "data": alert,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.manager.broadcast_to_topic("alerts", message)

    def stop_all_streams(self):
        """Stop all active data streams"""
        for task_name, task in self.update_tasks.items():
            task.cancel()
            logger.info(f"Stopped {task_name} stream")
        self.update_tasks.clear()


# WebSocket endpoint handlers
async def websocket_endpoint(websocket: WebSocket, client_id: str, manager: ConnectionManager, live_data: LiveDataManager):
    """Main WebSocket endpoint handler"""
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "subscribe":
                topics = data.get("topics", [])
                await manager.subscribe(client_id, topics)

                # Start relevant streams if needed
                if "metrics" in topics:
                    await live_data.start_metrics_stream()
                if "health" in topics:
                    await live_data.start_service_health_stream()

            elif message_type == "unsubscribe":
                topics = data.get("topics", [])
                await manager.unsubscribe(client_id, topics)

            elif message_type == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

            elif message_type == "command":
                # Handle specific commands
                command = data.get("command")
                if command == "refresh_metrics":
                    # Trigger immediate metrics update
                    await live_data.send_notification({
                        "message": "Metrics refresh triggered",
                        "level": "info"
                    })

            else:
                # Echo unknown messages back
                await manager.send_personal_message({
                    "type": "echo",
                    "original": data,
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


# Create global instances
connection_manager = ConnectionManager()
live_data_manager = LiveDataManager(connection_manager)