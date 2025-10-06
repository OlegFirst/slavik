# EventBus Service - BCM Platform

**Purpose:** Communication backbone for all platform services

**Technology:** FastAPI + Redis + PostgreSQL

**Port:** 8001

---

## 🎯 Features

### Core Functionality
- ✅ **Publish/Subscribe** - Redis pub/sub for real-time events
- ✅ **Event Store** - PostgreSQL persistence for audit trail
- ✅ **Idempotency** - Prevent duplicate event processing (event_id)
- ✅ **Event History** - Query past events with filters
- ✅ **Real-time Streams** - WebSocket + SSE support
- ✅ **Event Validation** - Schema validation before publishing
- ✅ **Statistics** - Event metrics per tenant

### ISO 22301 Compliance
- ✅ **Evidence Trail** - All events stored for audit (Clause 7.5 - Documented Information)
- ✅ **Traceability** - correlation_id for tracking workflows
- ✅ **Multi-tenancy** - tenant_id isolation

---

## 📡 Event Types

### BIA Events (Clause 8.2.2)
- `bcm.bia.started` - BIA analysis initiated
- `bcm.bia.completed` - BIA analysis completed
- `bcm.bia.updated` - BIA results updated

### Risk Events (Clause 8.2.3)
- `bcm.risk.identified` - New risk identified
- `bcm.risk.assessed` - Risk assessment completed
- `bcm.risk.mitigated` - Mitigation plan executed

### Plan Events (Clause 8.4)
- `bcm.plan.draft_requested` - Plan generation requested
- `bcm.plan.draft_generated` - AI-generated plan ready
- `bcm.plan.approved` - Plan approved
- `bcm.plan.activated` - Plan activated

### Incident Events (Clause 8.5)
- `bcm.incident.reported` - Incident reported
- `bcm.incident.response_generated` - Response checklist generated
- `bcm.incident.resolved` - Incident resolved

### Exercise Events (Clause 9.1.2)
- `bcm.exercise.scheduled` - Exercise scheduled
- `bcm.exercise.started` - Exercise started
- `bcm.exercise.completed` - Exercise completed

### Audit Events (Clause 9.2)
- `bcm.audit.started` - Audit initiated
- `bcm.audit.gap_found` - Gap identified
- `bcm.audit.completed` - Audit completed

### Training Events (Clause 7.2)
- `bcm.training.scheduled` - Training scheduled
- `bcm.training.completed` - Training completed

---

## 🚀 API Endpoints

### Health Check
```bash
GET /health
```

### Publish Event
```bash
POST /api/events/publish
Content-Type: application/json

{
  "event_type": "bcm.bia.completed",
  "tenant_id": "tenant_001",
  "data": {
    "bia_id": 1,
    "rto": 4,
    "rpo": 2,
    "critical_processes": ["patient_care", "emergency_response"]
  },
  "user_id": "user_123",
  "correlation_id": "flow_456",
  "event_id": "evt_789",
  "metadata": {
    "source": "bia_service",
    "version": "1.0"
  }
}
```

### Event History
```bash
GET /api/events/history?tenant_id=tenant_001&event_type=bcm.bia.completed&limit=50
```

Filters:
- `tenant_id` - Filter by tenant
- `event_type` - Filter by event type
- `correlation_id` - Track workflow
- `user_id` - Filter by user
- `from_date` - Start date (ISO 8601)
- `to_date` - End date (ISO 8601)
- `limit` - Max results (default: 100)
- `offset` - Pagination offset

### Event Stream (SSE)
```bash
GET /api/events/stream?tenant_id=tenant_001
```

Returns Server-Sent Events stream for real-time updates.

### WebSocket Stream
```bash
WS /api/events/ws?tenant_id=tenant_001
```

WebSocket connection for real-time event streaming.

### Event Statistics
```bash
GET /api/events/stats?tenant_id=tenant_001
```

Returns:
```json
{
  "tenant_id": "tenant_001",
  "total_events": 1523,
  "unique_event_types": 15,
  "first_event": "2025-01-01T00:00:00",
  "last_event": "2025-01-20T12:30:00",
  "top_event_types": [
    {"type": "bcm.bia.completed", "count": 345},
    {"type": "bcm.plan.approved", "count": 234}
  ]
}
```

### Validate Event
```bash
POST /api/events/validate
Content-Type: application/json

{
  "event_type": "bcm.bia.completed",
  "tenant_id": "tenant_001",
  "data": {
    "bia_id": 1,
    "rto": 4,
    "rpo": 2
  }
}
```

Returns validation result without publishing.

---

## 🔧 Configuration

### Environment Variables

```bash
# Redis connection
REDIS_URL=redis://localhost:6379

# PostgreSQL connection
POSTGRES_URL=postgresql://bcm:bcm_password@localhost/bcm_events

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8069

# Service port
PORT=8001
```

---

## 🏗️ Database Schema

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,
    data JSONB DEFAULT '{}',
    user_id VARCHAR(255),
    correlation_id VARCHAR(255),
    event_id VARCHAR(255) UNIQUE,  -- For idempotency
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'published'
);

-- Indexes for performance
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_tenant_id ON events(tenant_id);
CREATE INDEX idx_created_at ON events(created_at);
CREATE INDEX idx_correlation_id ON events(correlation_id);
CREATE UNIQUE INDEX idx_event_id ON events(event_id) WHERE event_id IS NOT NULL;
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t bcm-eventbus:latest .

# Run
docker run -d \
  --name bcm-eventbus \
  -p 8001:8001 \
  -e REDIS_URL=redis://redis:6379 \
  -e POSTGRES_URL=postgresql://bcm:bcm_password@postgres/bcm_events \
  bcm-eventbus:latest
```

---

## 📊 Usage Examples

### Python Client
```python
import httpx
import asyncio

async def publish_bia_event():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/events/publish",
            json={
                "event_type": "bcm.bia.completed",
                "tenant_id": "hospital_001",
                "data": {
                    "bia_id": 42,
                    "rto": 4,
                    "rpo": 1,
                    "critical_processes": ["emergency_room", "icu", "surgery"]
                },
                "user_id": "dr_smith",
                "correlation_id": "bia_session_2025_01"
            }
        )
        print(response.json())

asyncio.run(publish_bia_event())
```

### Subscribe to Events (SSE)
```python
import httpx

def stream_events(tenant_id):
    with httpx.stream("GET", f"http://localhost:8001/api/events/stream?tenant_id={tenant_id}") as response:
        for line in response.iter_lines():
            if line.startswith("data:"):
                event_data = line[6:]  # Remove "data: " prefix
                print(f"Event received: {event_data}")

stream_events("hospital_001")
```

### WebSocket Client
```python
import asyncio
import websockets
import json

async def listen_events(tenant_id):
    uri = f"ws://localhost:8001/api/events/ws?tenant_id={tenant_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            event = json.loads(message)
            print(f"Event: {event}")

asyncio.run(listen_events("hospital_001"))
```

---

## 🎯 Integration with Other Services

All BCM services publish events to EventBus:

```
┌─────────────┐
│ BIA Service │──┐
└─────────────┘  │
                 │
┌─────────────┐  │    ┌──────────────┐
│Risk Service │──┼───▶│   EventBus   │
└─────────────┘  │    │(FastAPI+Redis)│
                 │    └──────────────┘
┌─────────────┐  │           │
│Plan Service │──┘           │
└─────────────┘              ▼
                    ┌──────────────────┐
                    │ PostgreSQL Store │
                    │ (Audit Trail)    │
                    └──────────────────┘
```

Services can:
1. **Publish** events when operations complete
2. **Subscribe** to events from other services (via Redis pub/sub or WebSocket)
3. **Query** historical events for analysis

---

## 📋 Monitoring

### Health Check
```bash
curl http://localhost:8001/health
```

Expected response:
```json
{"status": "healthy", "service": "eventbus"}
```

### Event Statistics
```bash
curl http://localhost:8001/api/events/stats?tenant_id=hospital_001
```

---

## 🚀 Next Steps

### Phase 2 Enhancements
- [ ] **Dead Letter Queue** - Failed event handling
- [ ] **Event Replay** - Replay events for recovery
- [ ] **Event Filtering** - Server-side filtering for streams
- [ ] **Rate Limiting** - Prevent event flooding
- [ ] **Event TTL** - Automatic cleanup of old events
- [ ] **Metrics Export** - Prometheus metrics

### ISO 22301 Enhancements
- [ ] **Evidence Tagging** - Tag which events are audit evidence
- [ ] **Compliance Reports** - Generate ISO compliance reports from events
- [ ] **Event Chains** - Visualize causal event chains

---

## 🔗 Links

- **Service Registry:** PLATFORM/gateway
- **Monitoring:** PLATFORM/observability
- **Documentation:** `/knowledge-base/`

---

**Version:** 1.0
**Status:** ✅ Production Ready
**Port:** 8001
**Dependencies:** Redis, PostgreSQL
