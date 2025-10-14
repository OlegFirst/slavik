# 🚀 Realtime WebSocket Service

**Port:** 8050
**Version:** 1.0.0
**Status:** ✅ Adapted for production

Real-time WebSocket service for live communications, chat, notifications, and collaborative features.

---

## 🎯 Features

### Core Capabilities:
1. **💬 Real-time Chat** - Multi-channel messaging
2. **📡 Live Notifications** - System alerts and updates
3. **👥 User Presence** - Online/offline status tracking
4. **📝 Message History** - PostgreSQL persistence
5. **⚡ Redis Caching** - Fast message retrieval (optional)
6. **🔄 Connection Management** - Auto-cleanup, max connections per user
7. **🎨 10 Message Types** - user_message, notification, alert, typing, heartbeat, etc.
8. **🧪 Built-in Test Page** - HTML UI for testing

### Channel Types:
- **general** - General discussions
- **incidents** - Incident response coordination
- **processes** - Process execution updates
- **alerts** - System alerts
- **training** - Training sessions
- **compliance** - Compliance discussions
- **private** - Private channels

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Supabase and Redis credentials
```

### 3. Run Service

```bash
python main.py
```

Service will start on **http://localhost:8050**

### 4. Test WebSocket

Open browser: **http://localhost:8050/**

---

## 📊 Database Schema

Service automatically creates 3 tables:

### 1. `chat_messages`
```sql
- id (UUID)
- channel_id (String, Indexed)
- user_id (String, Indexed)
- username (String)
- message_type (String)
- content (Text)
- message_metadata (JSON)
- created_at (DateTime, Indexed)
- updated_at (DateTime)
- is_deleted (Boolean)
```

### 2. `user_sessions`
```sql
- id (UUID)
- user_id (String, Indexed)
- username (String)
- session_id (String, Unique, Indexed)
- channel_id (String)
- status (String: online, away, busy, offline)
- ip_address (String)
- user_agent (String)
- connected_at (DateTime)
- last_seen (DateTime)
- is_active (Boolean)
```

### 3. `notification_logs`
```sql
- id (UUID)
- notification_type (String)
- channel_id (String)
- sender (String)
- recipients (JSON)
- content (JSON)
- sent_at (DateTime)
- delivered_count (Integer)
- read_count (Integer)
```

---

## 📡 WebSocket Protocol

### Connect to WebSocket

```javascript
const ws = new WebSocket(
  'ws://localhost:8050/ws/general?user_id=user123&username=John'
);

ws.onopen = () => {
  console.log('Connected!');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### Send Message

```javascript
ws.send(JSON.stringify({
  type: 'user_message',
  content: 'Hello World!',
  metadata: {}
}));
```

### Message Types

1. **user_message** - Regular chat message
2. **system_notification** - System notification
3. **process_update** - Process execution update
4. **incident_alert** - Incident alert
5. **status_change** - User status change
6. **heartbeat** - Keep-alive ping
7. **user_joined** - User joined channel
8. **user_left** - User left channel
9. **typing** - Typing indicator
10. **file_upload** - File upload notification

### Message Format

```json
{
  "type": "user_message",
  "channel_id": "general",
  "user_id": "user123",
  "username": "John",
  "content": "Hello!",
  "timestamp": "2025-10-02T12:00:00",
  "message_id": "uuid-here",
  "metadata": {}
}
```

---

## 📡 REST API Endpoints

### 1. Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "realtime-websocket",
  "timestamp": "2025-10-02T12:00:00",
  "version": "1.0.0",
  "connections": {
    "total_connections": 15,
    "unique_users": 8,
    "active_channels": 3
  },
  "redis_connected": true
}
```

### 2. Broadcast Notification
```bash
POST /api/v1/notifications/broadcast
Content-Type: application/json

{
  "notification_type": "incident_alert",
  "channel_id": "incidents",
  "recipients": ["user123", "user456"],  // Empty = broadcast to all
  "content": {
    "title": "Critical Incident",
    "message": "Server down!",
    "severity": "critical"
  },
  "priority": "high"
}

Response:
{
  "status": "success",
  "message": "Notification sent",
  "delivered_count": 2,
  "notification_id": "uuid-here"
}
```

### 3. Get Channel Users
```bash
GET /api/v1/channels/general/users

Response:
{
  "channel_id": "general",
  "users": [
    {
      "user_id": "user123",
      "username": "John",
      "status": "online"
    }
  ],
  "user_count": 1
}
```

### 4. Get Message History
```bash
GET /api/v1/channels/general/messages?limit=50&before=2025-10-02T12:00:00

Response:
{
  "channel_id": "general",
  "messages": [
    {
      "id": "uuid",
      "user_id": "user123",
      "username": "John",
      "type": "user_message",
      "content": "Hello!",
      "metadata": {},
      "created_at": "2025-10-02T11:00:00",
      "updated_at": "2025-10-02T11:00:00"
    }
  ],
  "limit": 50,
  "has_more": false
}
```

### 5. Get Statistics
```bash
GET /api/v1/stats

Response:
{
  "timestamp": "2025-10-02T12:00:00",
  "service": "realtime-websocket",
  "version": "1.0.0",
  "stats": {
    "total_connections": 15,
    "unique_users": 8,
    "active_channels": 3,
    "channels": {
      "general": 5,
      "incidents": 3,
      "processes": 7
    },
    "redis": {
      "connected": true,
      "memory_used": "2.5M",
      "connected_clients": 1
    }
  }
}
```

---

## 🔧 Configuration

### Required Environment Variables:

```bash
PORT=8050
DATABASE_URL=postgresql://...  # Supabase PostgreSQL
```

### Optional:

```bash
UPSTASH_REDIS_URL=redis://...        # Upstash Redis for caching
MAX_CONNECTIONS_PER_USER=5           # Max WebSocket connections per user
MESSAGE_RETENTION_HOURS=24           # Redis message cache retention
CORS_ORIGINS=*                       # CORS configuration
EVENTBUS_URL=http://localhost:8001   # EventBus integration
LOG_LEVEL=INFO
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Clients (Browser/App)        │
│  WebSocket connections: ws://        │
└────────────────┬────────────────────┘
                 ↓
┌────────────────────────────────────┐
│    Realtime WebSocket:8050          │
│  ┌──────────────────────────────┐  │
│  │  ConnectionManager           │  │
│  │  - Channels (multi)          │  │
│  │  - User tracking             │  │
│  │  - Max 5 connections/user    │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Message Router              │  │
│  │  - Broadcast to channel      │  │
│  │  - Send to specific user     │  │
│  │  - Handle 10 message types   │  │
│  └──────────────────────────────┘  │
└────┬───────┬───────┬───────────────┘
     ↓       ↓       ↓
┌─────────┐ ┌──────┐ ┌──────────┐
│Supabase │ │Redis │ │EventBus  │
│3 tables │ │Cache │ │(optional)│
└─────────┘ └──────┘ └──────────┘
```

---

## 🔗 Integration

### JavaScript/TypeScript Client:
```javascript
class RealtimeClient {
  constructor(serverUrl, userId, username) {
    this.ws = null;
    this.serverUrl = serverUrl;
    this.userId = userId;
    this.username = username;
  }

  connect(channelId) {
    this.ws = new WebSocket(
      `${this.serverUrl}/ws/${channelId}?user_id=${this.userId}&username=${this.username}`
    );

    this.ws.onopen = () => console.log('Connected');
    this.ws.onmessage = (event) => this.handleMessage(JSON.parse(event.data));
    this.ws.onerror = (error) => console.error('WebSocket error:', error);
    this.ws.onclose = () => console.log('Disconnected');
  }

  sendMessage(content, type = 'user_message') {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type,
        content,
        metadata: { timestamp: new Date().toISOString() }
      }));
    }
  }

  handleMessage(message) {
    console.log('Received:', message);
    // Handle different message types
    switch (message.type) {
      case 'user_message':
        // Display chat message
        break;
      case 'system_notification':
        // Show notification
        break;
      case 'incident_alert':
        // Show alert
        break;
      case 'typing':
        // Show typing indicator
        break;
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const client = new RealtimeClient('ws://localhost:8050', 'user123', 'John');
client.connect('incidents');
client.sendMessage('Emergency!', 'incident_alert');
```

### Python Client:
```python
import asyncio
import websockets
import json

async def realtime_client():
    uri = "ws://localhost:8050/ws/general?user_id=bot123&username=Bot"

    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "type": "user_message",
            "content": "Hello from Python!",
            "metadata": {}
        }))

        # Receive messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(realtime_client())
```

### Integration with Services:
```python
# Broadcast notification from any service
import httpx

async def notify_incident(incident_id: str, message: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8050/api/v1/notifications/broadcast",
            json={
                "notification_type": "incident_alert",
                "channel_id": "incidents",
                "recipients": [],  # Broadcast to all
                "content": {
                    "incident_id": incident_id,
                    "message": message,
                    "severity": "critical"
                }
            }
        )
```

---

## 🧪 Testing

### Test with Built-in Page:
```bash
# Start service
python main.py

# Open browser
open http://localhost:8050/

# Enter user details and click Connect
# Send messages and see real-time updates
```

### Test with curl:
```bash
# Get channel users
curl http://localhost:8050/api/v1/channels/general/users

# Get message history
curl http://localhost:8050/api/v1/channels/general/messages?limit=10

# Get stats
curl http://localhost:8050/api/v1/stats

# Broadcast notification
curl -X POST http://localhost:8050/api/v1/notifications/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "test",
    "channel_id": "general",
    "recipients": [],
    "content": {"message": "Test notification"}
  }'
```

---

## 🎓 Use Cases

### 1. Incident Response Coordination
Real-time chat during incidents, instant alerts, status updates.

### 2. Live Process Monitoring
Stream BPMN workflow updates to dashboard in real-time.

### 3. Collaborative BIA Assessment
Multiple users collaborating on Business Impact Analysis.

### 4. Training Sessions
Live instructor-student communication during training.

### 5. System Alerts Broadcasting
Instant system-wide notifications for critical events.

### 6. Compliance Discussions
Real-time compliance team communication.

---

## 🐳 Docker

```bash
docker build -t realtime-websocket .
docker run -p 8050:8050 --env-file .env realtime-websocket
```

---

## 📝 TODO

### High Priority:
- [ ] Add JWT authentication for WebSocket
- [ ] Integrate with EventBus for event publishing
- [ ] Add message encryption for private channels
- [ ] Implement read receipts

### Medium Priority:
- [ ] Add file upload support
- [ ] Implement typing indicators persistence
- [ ] Add user presence heartbeat
- [ ] Create React/Vue component library

### Low Priority:
- [ ] Add video/audio call signaling
- [ ] Implement message search
- [ ] Add emoji reactions
- [ ] Create mobile SDK

---

**Ready for production!** ✅

**Note:** Redis is optional. Service works without it, but caching improves performance.
