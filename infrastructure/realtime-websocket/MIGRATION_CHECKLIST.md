# 🚀 Realtime WebSocket Service - Migration Checklist

**Service:** realtime_websocket
**Lines:** 812
**Status:** STEP 1 - ANALYZE ✅

---

## 📊 SERVICE ANALYSIS

### Purpose:
Real-time WebSocket service for:
- Live chat and messaging
- Real-time notifications
- Process updates streaming
- Incident alerts
- Collaborative features
- User presence tracking

### Technology Stack:
- **Framework:** FastAPI with WebSocket support
- **Database:** PostgreSQL (SQLAlchemy)
- **Cache:** Redis (async, optional)
- **Features:**
  - Multi-channel support
  - User presence management
  - Message persistence
  - Redis caching
  - Connection pooling
  - Built-in test page

### Key Components:
1. **ConnectionManager:** WebSocket connection management
2. **Message Types:** 10 types (user_message, notification, alert, etc.)
3. **Database Models:** 3 tables (chat_messages, user_sessions, notification_logs)
4. **Redis Cache:** Optional caching layer

---

## 🔧 REQUIRED CHANGES

### 1. **Port Configuration** ⚠️ CRITICAL
- **Current:** Port 8084 (hardcoded in line 813, test page line 729)
- **Change to:** Port 8050
- **Action:** Make port configurable via environment variable

### 2. **Database URL**
- **Current:** `postgresql://postgres:postgres@localhost:5432/bcm_realtime` (line 28)
- **Change to:** Use production Supabase URL
- **Action:** Update to Supabase connection string

### 3. **Redis URL**
- **Current:** `redis://localhost:6379` (line 29)
- **Change to:** Upstash Redis for production
- **Action:** Update to UPSTASH_REDIS_URL

### 4. **Test Page WebSocket URL**
- **Current:** `ws://localhost:8084` (line 729)
- **Change to:** Make port dynamic
- **Action:** Update to use window.location or config

### 5. **Environment Variables**
- **Add:**
  - `PORT=8050`
  - `DATABASE_URL` (Supabase PostgreSQL)
  - `UPSTASH_REDIS_URL` or `REDIS_URL`
  - `MAX_CONNECTIONS_PER_USER=5`
  - `MESSAGE_RETENTION_HOURS=24`
  - `CORS_ORIGINS=*` (for production)

### 6. **Requirements.txt Missing**
- **Issue:** No requirements.txt file
- **Action:** Create based on imports:
  - fastapi
  - uvicorn[standard]
  - websockets
  - sqlalchemy
  - psycopg2-binary
  - redis[asyncio]
  - python-multipart

### 7. **Redis Optional Handling** ✅
- **Current:** Already handles Redis failure gracefully
- **Good:** Service works without Redis
- **Action:** No changes needed

### 8. **Database Tables Auto-Creation** ✅
- **Current:** Automatically creates tables on startup
- **Good:** 3 tables (chat_messages, user_sessions, notification_logs)
- **Action:** No changes needed

### 9. **CORS Configuration**
- **Current:** allow_origins=["*"]
- **Action:** Keep for now, document for production security review

### 10. **Integration Points**
- **Add:** EventBus integration for broadcasting events
- **Add:** Coordination Center registration
- **Document:** Integration with other services

---

## 📝 MIGRATION STEPS

### STEP 1: ANALYZE ✅ (CURRENT)
- [x] Read main.py (812 lines)
- [x] Check for requirements.txt (missing)
- [x] Identify dependencies
- [x] Identify required changes
- [x] Create migration checklist

### STEP 2: ADAPT (NEXT)
- [ ] Create BCM_1_MIGRATED/realtime_websocket/
- [ ] Copy main.py
- [ ] Fix port configuration (8084 → 8050)
- [ ] Update DATABASE_URL for Supabase
- [ ] Update REDIS_URL for Upstash
- [ ] Fix test page WebSocket URL
- [ ] Create requirements.txt
- [ ] Create .env.example
- [ ] Create README.md with:
  - API documentation
  - WebSocket protocol
  - Message types
  - Integration guide
  - Test instructions
- [ ] Test WebSocket connection
- [ ] Test Redis cache (optional)

### STEP 3: TRANSFER
- [ ] Copy to /Users/MD/AI-Platform-ISO/infrastructure/realtime-websocket/
- [ ] Update Tool Registry with 5 actions:
  - broadcast_notification
  - get_channel_users
  - get_channel_messages
  - get_stats
  - websocket_connect (special)
- [ ] Update SERVICES_INVENTORY.md (15th service)
- [ ] Create integration documentation

---

## 🎯 UNIQUE FEATURES

This is a **CRITICAL and UNIQUE** service:

✅ **Real-time Communications:** WebSocket-based chat and messaging
✅ **Multi-channel Support:** Multiple channels (general, incidents, processes, etc.)
✅ **User Presence:** Track online/offline status
✅ **Message Persistence:** PostgreSQL storage with history
✅ **Redis Caching:** Optional fast message retrieval
✅ **Connection Management:** Max connections per user, auto-cleanup
✅ **10 Message Types:** user_message, notification, alert, typing, heartbeat, etc.
✅ **Built-in Test Page:** HTML UI for testing WebSocket
✅ **Broadcast Notifications:** API endpoint for system notifications
✅ **3 Database Tables:** Full message/session/notification tracking

**No equivalent in production!** Must transfer!

---

## ⚠️ CRITICAL CHANGES NEEDED

### Change 1: Port Configuration
**Lines:** 729 (test page), 813 (server)

**Current (test page):**
```javascript
const wsUrl = `ws://localhost:8084/ws/${channelId}?user_id=${userId}&username=${encodeURIComponent(username)}`;
```

**Fix:**
```javascript
const wsUrl = `ws://${window.location.hostname}:${window.location.port}/ws/${channelId}?user_id=${userId}&username=${encodeURIComponent(username)}`;
```

**Current (server):**
```python
uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8084")))
```

**Fix:**
```python
uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8050")))
```

### Change 2: Database URL
**Line:** 28

**Current:**
```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bcm_realtime")
```

**Fix:**
```python
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("DATABASE_URL not set, using fallback")
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/bcm_realtime"
```

### Change 3: Redis URL (Upstash Support)
**Line:** 29

**Current:**
```python
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
```

**Fix:**
```python
REDIS_URL = os.getenv("UPSTASH_REDIS_URL") or os.getenv("REDIS_URL", "redis://localhost:6379")
```

---

## 📡 API ENDPOINTS (5 ACTIONS + 1 WEBSOCKET)

### WebSocket:
1. `WS /ws/{channel_id}` - Main WebSocket endpoint for real-time chat

### REST API:
2. `POST /api/v1/notifications/broadcast` - Broadcast notification to channel/users
3. `GET /api/v1/channels/{channel_id}/users` - Get users in channel
4. `GET /api/v1/channels/{channel_id}/messages` - Get message history
5. `GET /api/v1/stats` - Get connection statistics
6. `GET /health` - Health check
7. `GET /` - WebSocket test page

---

## 📊 DATABASE SCHEMA (3 TABLES)

### 1. `chat_messages`
```sql
- id (UUID, Primary Key)
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
- id (UUID, Primary Key)
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
- id (UUID, Primary Key)
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

## 🔗 INTEGRATION WITH EXISTING SERVICES

### 1. EventBus (Port 8001)
Publish events:
- `websocket.user_connected`
- `websocket.user_disconnected`
- `websocket.message_sent`

### 2. Coordination Center (Port 8004)
Register as tool for WebSocket notifications.

### 3. Monitoring Service (Port 8045)
Push logs and metrics for WebSocket connections.

### 4. Notification Service (Port 8035)
Integrate for sending WebSocket notifications triggered by external events.

### 5. All Services
Any service can broadcast real-time updates via WebSocket API.

---

## 🎓 USE CASES

### 1. Incident Response Chat
Real-time communication during incidents.

### 2. Live Process Monitoring
Stream process updates to dashboard.

### 3. System Alerts
Real-time alert notifications.

### 4. Collaborative BIA Assessment
Multiple users collaborating on BIA in real-time.

### 5. Training Sessions
Live training with instructor-student chat.

---

## 📦 DEPENDENCIES TO CREATE

### requirements.txt:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis[asyncio]==5.0.1
python-multipart==0.0.6
pydantic==2.5.0
```

---

**STATUS: READY FOR STEP 2 (ADAPT)** 🚀
