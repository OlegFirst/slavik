#!/usr/bin/env python3
"""
Real-time WebSocket Service
Real-time communications, live updates, and collaborative features for BCM Platform
"""

import os
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, JSON, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("DATABASE_URL not set, using fallback for development")
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/bcm_realtime"

REDIS_URL = os.getenv("UPSTASH_REDIS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379")
MAX_CONNECTIONS_PER_USER = int(os.getenv("MAX_CONNECTIONS_PER_USER", "5"))
MESSAGE_RETENTION_HOURS = int(os.getenv("MESSAGE_RETENTION_HOURS", "24"))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Global connection manager and Redis client
connections: Dict[str, Set[WebSocket]] = {}
user_sessions: Dict[str, Dict[str, WebSocket]] = {}
redis_client: Optional[redis.Redis] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events"""
    global redis_client

    # Startup
    try:
        redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Connected to Redis")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}. Running without Redis.")
        redis_client = None

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

    yield

    # Shutdown
    if redis_client:
        await redis_client.close()

# FastAPI app with lifespan
app = FastAPI(
    title="Real-time WebSocket Service",
    description="Real-time communications and live updates for BCM Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class MessageType(str, Enum):
    USER_MESSAGE = "user_message"
    SYSTEM_NOTIFICATION = "system_notification"
    PROCESS_UPDATE = "process_update"
    INCIDENT_ALERT = "incident_alert"
    STATUS_CHANGE = "status_change"
    HEARTBEAT = "heartbeat"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    TYPING = "typing"
    FILE_UPLOAD = "file_upload"

class ChannelType(str, Enum):
    GENERAL = "general"
    INCIDENTS = "incidents"
    PROCESSES = "processes"
    ALERTS = "alerts"
    TRAINING = "training"
    COMPLIANCE = "compliance"
    PRIVATE = "private"

class UserStatus(str, Enum):
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"

# Database Models
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=False)
    session_id = Column(String, nullable=False, unique=True, index=True)
    channel_id = Column(String, nullable=False)
    status = Column(String, default=UserStatus.ONLINE)
    ip_address = Column(String)
    user_agent = Column(String)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_type = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    recipients = Column(JSON)  # List of user IDs
    content = Column(JSON, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)

# Pydantic Models
@dataclass
class WebSocketMessage:
    type: str
    channel_id: str
    user_id: str
    username: str
    content: Any
    timestamp: str = None
    message_id: str = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.metadata is None:
            self.metadata = {}

class ChatMessageRequest(BaseModel):
    channel_id: str
    content: str
    message_type: MessageType = MessageType.USER_MESSAGE
    metadata: Dict[str, Any] = {}

class NotificationRequest(BaseModel):
    notification_type: str
    channel_id: str
    recipients: List[str] = []  # If empty, broadcast to all users in channel
    content: Dict[str, Any]
    priority: str = "normal"

class UserStatusUpdate(BaseModel):
    user_id: str
    status: UserStatus

# Connection Manager
class ConnectionManager:
    """Manages WebSocket connections and message routing"""

    def __init__(self):
        # Channel -> Set of WebSockets
        self.channels: Dict[str, Set[WebSocket]] = {}
        # WebSocket -> User info
        self.connections: Dict[WebSocket, Dict[str, str]] = {}
        # User ID -> Set of WebSockets (for multiple tabs/devices)
        self.user_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, username: str, channel_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()

        # Initialize channel if not exists
        if channel_id not in self.channels:
            self.channels[channel_id] = set()

        # Add connection to channel
        self.channels[channel_id].add(websocket)

        # Store connection info
        self.connections[websocket] = {
            "user_id": user_id,
            "username": username,
            "channel_id": channel_id,
            "session_id": str(uuid.uuid4()),
            "connected_at": datetime.utcnow().isoformat()
        }

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

        # Limit connections per user
        if len(self.user_connections[user_id]) > MAX_CONNECTIONS_PER_USER:
            oldest_connection = min(
                self.user_connections[user_id],
                key=lambda ws: self.connections[ws]["connected_at"]
            )
            await self.disconnect(oldest_connection)

        logger.info(f"✅ User {username} ({user_id}) connected to channel {channel_id}")

        # Notify channel about new user
        await self.broadcast_to_channel(
            channel_id,
            WebSocketMessage(
                type=MessageType.USER_JOINED,
                channel_id=channel_id,
                user_id=user_id,
                username=username,
                content={"message": f"{username} joined the channel"}
            ),
            exclude=websocket
        )

        # Send welcome message to user
        await self.send_to_connection(
            websocket,
            WebSocketMessage(
                type=MessageType.SYSTEM_NOTIFICATION,
                channel_id=channel_id,
                user_id="system",
                username="System",
                content={"message": f"Welcome to {channel_id}!", "type": "welcome"}
            )
        )

    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        if websocket not in self.connections:
            return

        user_info = self.connections[websocket]
        user_id = user_info["user_id"]
        username = user_info["username"]
        channel_id = user_info["channel_id"]

        # Remove from all tracking structures
        if channel_id in self.channels:
            self.channels[channel_id].discard(websocket)
            if not self.channels[channel_id]:  # Remove empty channels
                del self.channels[channel_id]

        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:  # Remove if no more connections
                del self.user_connections[user_id]

        del self.connections[websocket]

        logger.info(f"❌ User {username} ({user_id}) disconnected from channel {channel_id}")

        # Notify channel about user leaving
        if channel_id in self.channels:
            await self.broadcast_to_channel(
                channel_id,
                WebSocketMessage(
                    type=MessageType.USER_LEFT,
                    channel_id=channel_id,
                    user_id=user_id,
                    username=username,
                    content={"message": f"{username} left the channel"}
                )
            )

    async def send_to_connection(self, websocket: WebSocket, message: WebSocketMessage):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(asdict(message)))
        except Exception as e:
            logger.error(f"Failed to send message to connection: {e}")
            await self.disconnect(websocket)

    async def broadcast_to_channel(self, channel_id: str, message: WebSocketMessage, exclude: WebSocket = None):
        """Broadcast message to all connections in a channel"""
        if channel_id not in self.channels:
            logger.warning(f"Attempted to broadcast to non-existent channel: {channel_id}")
            return

        disconnected = []
        for websocket in self.channels[channel_id]:
            if websocket == exclude:
                continue

            try:
                await websocket.send_text(json.dumps(asdict(message)))
            except Exception as e:
                logger.error(f"Failed to send to websocket in channel {channel_id}: {e}")
                disconnected.append(websocket)

        # Clean up disconnected sockets
        for websocket in disconnected:
            await self.disconnect(websocket)

    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to all connections of a specific user"""
        if user_id not in self.user_connections:
            logger.warning(f"User {user_id} not connected")
            return False

        sent_count = 0
        disconnected = []

        for websocket in self.user_connections[user_id]:
            try:
                await websocket.send_text(json.dumps(asdict(message)))
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send to user {user_id}: {e}")
                disconnected.append(websocket)

        # Clean up disconnected sockets
        for websocket in disconnected:
            await self.disconnect(websocket)

        return sent_count > 0

    def get_channel_users(self, channel_id: str) -> List[Dict[str, str]]:
        """Get list of users in a channel"""
        if channel_id not in self.channels:
            return []

        users = []
        seen_users = set()

        for websocket in self.channels[channel_id]:
            if websocket in self.connections:
                user_info = self.connections[websocket]
                user_id = user_info["user_id"]

                if user_id not in seen_users:
                    users.append({
                        "user_id": user_id,
                        "username": user_info["username"],
                        "status": "online"
                    })
                    seen_users.add(user_id)

        return users

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.connections),
            "unique_users": len(self.user_connections),
            "active_channels": len(self.channels),
            "channels": {
                channel_id: len(connections)
                for channel_id, connections in self.channels.items()
            }
        }

# Initialize connection manager
manager = ConnectionManager()

# Utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def save_message_to_db(db: Session, message: WebSocketMessage):
    """Save chat message to database"""
    try:
        chat_message = ChatMessage(
            channel_id=message.channel_id,
            user_id=message.user_id,
            username=message.username,
            message_type=message.type,
            content=str(message.content),
            message_metadata=message.metadata
        )
        db.add(chat_message)
        db.commit()
        return str(chat_message.id)
    except Exception as e:
        logger.error(f"Failed to save message to database: {e}")
        db.rollback()
        return None

async def cache_message_to_redis(message: WebSocketMessage):
    """Cache message to Redis for quick retrieval"""
    if not redis_client:
        return

    try:
        key = f"channel:{message.channel_id}:messages"
        message_data = json.dumps(asdict(message))

        # Add to sorted set with timestamp as score
        timestamp = datetime.utcnow().timestamp()
        await redis_client.zadd(key, {message_data: timestamp})

        # Keep only last 1000 messages per channel
        await redis_client.zremrangebyrank(key, 0, -1001)

        # Set expiration
        await redis_client.expire(key, MESSAGE_RETENTION_HOURS * 3600)

    except Exception as e:
        logger.error(f"Failed to cache message to Redis: {e}")

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = manager.get_connection_stats()
    return {
        "status": "healthy",
        "service": "realtime-websocket",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "connections": stats,
        "redis_connected": redis_client is not None
    }

@app.websocket("/ws/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel_id: str,
    user_id: str = Query(...),
    username: str = Query(...)
):
    """Main WebSocket endpoint for real-time communications"""
    db = SessionLocal()

    try:
        await manager.connect(websocket, user_id, username, channel_id)

        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Create WebSocket message
                message = WebSocketMessage(
                    type=message_data.get("type", MessageType.USER_MESSAGE),
                    channel_id=channel_id,
                    user_id=user_id,
                    username=username,
                    content=message_data.get("content", ""),
                    metadata=message_data.get("metadata", {})
                )

                # Save to database (async)
                if message.type in [MessageType.USER_MESSAGE, MessageType.SYSTEM_NOTIFICATION]:
                    asyncio.create_task(save_message_to_db(db, message))
                    asyncio.create_task(cache_message_to_redis(message))

                # Handle different message types
                if message.type == MessageType.TYPING:
                    # Don't persist typing indicators, just broadcast
                    await manager.broadcast_to_channel(channel_id, message, exclude=websocket)
                elif message.type == MessageType.HEARTBEAT:
                    # Respond to heartbeat
                    await manager.send_to_connection(
                        websocket,
                        WebSocketMessage(
                            type=MessageType.HEARTBEAT,
                            channel_id=channel_id,
                            user_id="system",
                            username="System",
                            content={"timestamp": datetime.utcnow().isoformat()}
                        )
                    )
                else:
                    # Broadcast message to channel
                    await manager.broadcast_to_channel(channel_id, message)

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_to_connection(
                    websocket,
                    WebSocketMessage(
                        type=MessageType.SYSTEM_NOTIFICATION,
                        channel_id=channel_id,
                        user_id="system",
                        username="System",
                        content={"error": "Invalid JSON format", "type": "error"}
                    )
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await manager.send_to_connection(
                    websocket,
                    WebSocketMessage(
                        type=MessageType.SYSTEM_NOTIFICATION,
                        channel_id=channel_id,
                        user_id="system",
                        username="System",
                        content={"error": f"Server error: {str(e)}", "type": "error"}
                    )
                )

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        await manager.disconnect(websocket)
        db.close()

@app.post("/api/v1/notifications/broadcast")
async def broadcast_notification(
    notification: NotificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Broadcast notification to channel or specific users"""
    try:
        message = WebSocketMessage(
            type=MessageType.SYSTEM_NOTIFICATION,
            channel_id=notification.channel_id,
            user_id="system",
            username="System",
            content=notification.content
        )

        delivered_count = 0

        if notification.recipients:
            # Send to specific users
            for user_id in notification.recipients:
                if await manager.send_to_user(user_id, message):
                    delivered_count += 1
        else:
            # Broadcast to entire channel
            await manager.broadcast_to_channel(notification.channel_id, message)
            delivered_count = len(manager.channels.get(notification.channel_id, []))

        # Log notification
        notification_log = NotificationLog(
            notification_type=notification.notification_type,
            channel_id=notification.channel_id,
            sender="system",
            recipients=notification.recipients,
            content=notification.content,
            delivered_count=delivered_count
        )
        db.add(notification_log)
        db.commit()

        return {
            "status": "success",
            "message": "Notification sent",
            "delivered_count": delivered_count,
            "notification_id": str(notification_log.id)
        }

    except Exception as e:
        logger.error(f"Error broadcasting notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to broadcast notification: {str(e)}")

@app.get("/api/v1/channels/{channel_id}/users")
async def get_channel_users(channel_id: str):
    """Get list of users currently in a channel"""
    users = manager.get_channel_users(channel_id)
    return {
        "channel_id": channel_id,
        "users": users,
        "user_count": len(users)
    }

@app.get("/api/v1/channels/{channel_id}/messages")
async def get_channel_messages(
    channel_id: str,
    limit: int = Query(50, le=1000),
    before: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get recent messages from a channel"""
    try:
        query = db.query(ChatMessage).filter(
            ChatMessage.channel_id == channel_id,
            ChatMessage.is_deleted == False
        )

        if before:
            # Get messages before specific timestamp
            before_date = datetime.fromisoformat(before.replace('Z', '+00:00'))
            query = query.filter(ChatMessage.created_at < before_date)

        messages = query.order_by(ChatMessage.created_at.desc()).limit(limit).all()

        return {
            "channel_id": channel_id,
            "messages": [
                {
                    "id": str(msg.id),
                    "user_id": msg.user_id,
                    "username": msg.username,
                    "type": msg.message_type,
                    "content": msg.content,
                    "metadata": msg.message_metadata,
                    "created_at": msg.created_at.isoformat(),
                    "updated_at": msg.updated_at.isoformat()
                }
                for msg in reversed(messages)  # Return in chronological order
            ],
            "limit": limit,
            "has_more": len(messages) == limit
        }

    except Exception as e:
        logger.error(f"Error getting channel messages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@app.get("/api/v1/stats")
async def get_realtime_stats():
    """Get real-time service statistics"""
    stats = manager.get_connection_stats()

    # Add Redis cache stats if available
    if redis_client:
        try:
            redis_info = await redis_client.info("memory")
            stats["redis"] = {
                "connected": True,
                "memory_used": redis_info.get("used_memory_human", "unknown"),
                "connected_clients": redis_info.get("connected_clients", 0)
            }
        except Exception as e:
            stats["redis"] = {"connected": False, "error": str(e)}
    else:
        stats["redis"] = {"connected": False}

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "realtime-websocket",
        "version": "1.0.0",
        "stats": stats
    }

@app.get("/")
async def get_websocket_test_page():
    """Simple WebSocket test page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BCM Real-time WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #messages { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin: 10px 0; }
            .message { margin: 5px 0; padding: 5px; border-radius: 3px; }
            .user-message { background-color: #e3f2fd; }
            .system-message { background-color: #f3e5f5; }
            input, button { padding: 8px; margin: 5px; }
            #messageInput { width: 300px; }
        </style>
    </head>
    <body>
        <h1>🚀 BCM Real-time WebSocket Test</h1>

        <div>
            <label>User ID: <input type="text" id="userId" value="test-user-001" /></label>
            <label>Username: <input type="text" id="username" value="Test User" /></label>
            <label>Channel: <input type="text" id="channelId" value="general" /></label>
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>

        <div id="status">Status: Disconnected</div>

        <div id="messages"></div>

        <div>
            <input type="text" id="messageInput" placeholder="Type a message..." onkeypress="handleKeyPress(event)" />
            <button onclick="sendMessage()">Send</button>
            <button onclick="sendHeartbeat()">Heartbeat</button>
            <button onclick="clearMessages()">Clear</button>
        </div>

        <script>
            let ws = null;
            let userId = '';
            let username = '';
            let channelId = '';

            function connect() {
                userId = document.getElementById('userId').value;
                username = document.getElementById('username').value;
                channelId = document.getElementById('channelId').value;

                const port = window.location.port || '8050';
                const wsUrl = `ws://${window.location.hostname}:${port}/ws/${channelId}?user_id=${userId}&username=${encodeURIComponent(username)}`;
                ws = new WebSocket(wsUrl);

                ws.onopen = function(event) {
                    document.getElementById('status').textContent = 'Status: Connected';
                    addMessage('System', 'Connected to ' + channelId, 'system-message');
                };

                ws.onmessage = function(event) {
                    const message = JSON.parse(event.data);
                    addMessage(message.username, JSON.stringify(message.content), 'user-message');
                };

                ws.onclose = function(event) {
                    document.getElementById('status').textContent = 'Status: Disconnected';
                    addMessage('System', 'Disconnected', 'system-message');
                };

                ws.onerror = function(error) {
                    addMessage('System', 'Error: ' + error, 'system-message');
                };
            }

            function disconnect() {
                if (ws) {
                    ws.close();
                }
            }

            function sendMessage() {
                const messageInput = document.getElementById('messageInput');
                const content = messageInput.value.trim();

                if (content && ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'user_message',
                        content: content,
                        metadata: { timestamp: new Date().toISOString() }
                    };

                    ws.send(JSON.stringify(message));
                    messageInput.value = '';
                    addMessage('You', content, 'user-message');
                }
            }

            function sendHeartbeat() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        type: 'heartbeat',
                        content: 'ping',
                        metadata: {}
                    };
                    ws.send(JSON.stringify(message));
                    addMessage('You', 'Heartbeat sent', 'system-message');
                }
            }

            function addMessage(sender, content, className) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + className;
                messageDiv.innerHTML = `<strong>${sender}:</strong> ${content}`;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function clearMessages() {
                document.getElementById('messages').innerHTML = '';
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8050"))
    uvicorn.run(app, host="0.0.0.0", port=port)