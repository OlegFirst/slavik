# EventBus Service Routes Inventory

## Service Information
- **Base URL**: http://localhost:8001
- **Framework**: FastAPI
- **Database**: PostgreSQL (events table)
- **Cache**: Redis (pub/sub channels)

## API Endpoints

### Health & Monitoring
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/health` | Service health check | None |
| GET | `/api/events/stats` | Event statistics by tenant | Query: tenant_id |

### Event Management
| Method | Path | Description | Request/Response |
|--------|------|-------------|------------------|
| POST | `/api/events/publish` | Publish new event | Body: Event schema |
| GET | `/api/events/history` | Query event history | Query: tenant_id, event_type, limit, offset, from_date, to_date |
| POST | `/api/events/validate` | Validate event structure | Body: Event schema |

### Real-time Streaming
| Method | Path | Description | Protocol |
|--------|------|-------------|----------|
| GET | `/api/events/stream` | Server-sent events stream | SSE, Query: tenant_id |
| WS | `/api/events/ws` | WebSocket event stream | WebSocket, Query: tenant_id |

## Request Schemas

### Event Schema
```json
{
  "event_type": "string",        // Required, 3-255 chars
  "tenant_id": "string",         // Required
  "data": {},                    // Event payload
  "user_id": "string",           // Optional
  "correlation_id": "string",    // Optional
  "event_id": "string",          // Optional (idempotency key)
  "metadata": {}                 // Optional metadata
}
```

### EventResponse Schema
```json
{
  "id": "integer",
  "event_type": "string",
  "tenant_id": "string",
  "data": {},
  "user_id": "string",
  "correlation_id": "string",
  "metadata": {},
  "created_at": "datetime",
  "status": "string"
}
```

## Registered Event Types

### BIA Events
- `bcm.bia.started` - Required: [bia_id, process_id]
- `bcm.bia.completed` - Required: [bia_id, rto, rpo, critical_processes]

### Plan Events  
- `bcm.plan.draft_requested` - Required: [plan_id, plan_type]
- `bcm.plan.draft_generated` - Required: [plan_id, ai_generated]
- `bcm.plan.versioned` - Plan published
- `bcm.plan.approved` - Plan approved
- `bcm.plan.rejected` - Plan rejected

### Incident Events
- `bcm.incident.reported` - Required: [incident_id, severity]
- `bcm.incident.response_generated` - Required: [incident_id, checklist_items]
- `bcm.incident.opened` - New incident
- `bcm.incident.escalated` - Incident escalated
- `bcm.incident.resolved` - Incident resolved

### KPI Events
- `bcm.kpi.calculated` - Required: [period, bia_coverage, plans_up_to_date, capa_on_time]
- `bcm.kpi.threshold_breach` - KPI threshold exceeded

### Exercise & Training Events
- `bcm.exercise.completed` - Required: [exercise_id, results]
- `bcm.training.completed` - Required: [training_id, attendees]
- `bcm.exercise.scheduled` - Exercise scheduled
- `bcm.training.scheduled` - Training scheduled

### Audit Events
- `bcm.audit.scheduled` - Audit scheduled
- `bcm.audit.started` - Audit started
- `bcm.audit.findings` - Findings reported
- `bcm.audit.completed` - Audit completed
- `bcm.audit.gap_found` - Gap identified

### Client Events
- `bcm.client.created` - New client
- `bcm.client.updated` - Client updated

### Context Events
- `bcm.context.imported` - Context imported
- `bcm.context.updated` - Context updated
- `bcm.process.identified` - Process identified
- `bcm.critical_process.detected` - Critical process detected

### Governance Events
- `bcm.governance.review_scheduled` - Review scheduled
- `bcm.governance.review_completed` - Review completed
- `bcm.governance.policy_updated` - Policy updated

## Database Schema

### Events Table
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(255) NOT NULL,
    data JSONB,
    user_id VARCHAR(255),
    correlation_id VARCHAR(255),
    event_id VARCHAR(255) UNIQUE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'published'
);

-- Indexes
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_tenant_id ON events(tenant_id);
CREATE INDEX idx_created_at ON events(created_at);
CREATE INDEX idx_correlation_id ON events(correlation_id);
CREATE UNIQUE INDEX idx_event_id ON events(event_id) WHERE event_id IS NOT NULL;
```

## Redis Channels

### Channel Patterns
- `bcm.{tenant_id}` - Tenant-specific channel
- `bcm.event.{event_type}` - Event type channel

### Pub/Sub Features
- Dual publishing to both tenant and event type channels
- Heartbeat mechanism for SSE/WS connections
- Auto-disconnect detection

## Configuration

### Environment Variables
- `REDIS_URL` - Default: redis://localhost:6379
- `POSTGRES_URL` - Default: postgresql://bcm:bcm@localhost/bcm_events  
- `CORS_ORIGINS` - Default: http://localhost:8081,http://localhost:8069

### Connection Pool
- PostgreSQL: 5-20 connections
- Redis: Async client with auto-reconnect

## Key Features

1. **Idempotency**: Via event_id deduplication
2. **Event Validation**: Schema validation for registered types
3. **Filtering**: Rich query parameters for history
4. **Real-time**: Both SSE and WebSocket support
5. **Statistics**: Per-tenant event analytics
6. **CORS**: Configurable cross-origin support
7. **Health Monitoring**: Redis and PostgreSQL checks
