# Events Catalog - BCM Platform

## Event Flow Matrix

| Event Type | Source | Consumer | Payload Example | Required Fields |
|------------|--------|----------|-----------------|-----------------|
| **bcm.bia.started** | Odoo BIA Module | Orchestrator | `{"bia_id": 1, "process_id": 5}` | bia_id, process_id |
| **bcm.bia.completed** | Odoo BIA Module | Orchestrator, EventBus | `{"bia_id": 1, "rto": 4, "rpo": 15, "critical_processes": [1,2,3]}` | bia_id, rto, rpo, critical_processes |
| **bcm.plan.draft_requested** | Odoo Plans Module | Orchestrator | `{"plan_id": 10, "plan_type": "disaster_recovery"}` | plan_id, plan_type |
| **bcm.plan.draft_generated** | Orchestrator | Odoo, EventBus | `{"plan_id": 10, "ai_generated": true, "steps": [...]}` | plan_id, ai_generated |
| **bcm.plan.versioned** | Odoo Plans Module | EventBus, Portal | `{"plan_id": 10, "version": "2.0", "status": "published"}` | plan_id, version |
| **bcm.plan.approved** | Odoo Plans Module | Orchestrator, EventBus | `{"plan_id": 10, "approved_by": 2, "date": "2024-01-15"}` | plan_id |
| **bcm.plan.rejected** | Odoo Plans Module | Orchestrator, EventBus | `{"plan_id": 10, "reason": "Incomplete procedures"}` | plan_id |
| **bcm.incident.reported** | Portal/Odoo | Orchestrator | `{"incident_id": 20, "severity": "critical"}` | incident_id, severity |
| **bcm.incident.opened** | Odoo Incident Module | Orchestrator, EventBus | `{"incident_id": 20, "type": "system_failure"}` | incident_id |
| **bcm.incident.response_generated** | Orchestrator | Odoo, EventBus | `{"incident_id": 20, "checklist_items": [...]}` | incident_id, checklist_items |
| **bcm.incident.escalated** | Odoo Incident Module | EventBus, Notifications | `{"incident_id": 20, "escalation_level": 2}` | incident_id |
| **bcm.incident.resolved** | Odoo Incident Module | EventBus, KPI Calculator | `{"incident_id": 20, "resolution_time": 4.5}` | incident_id |
| **bcm.kpi.calculated** | Odoo KPI Module | Orchestrator, Frontend | `{"period": "2024-01", "bia_coverage": 0.85, "plans_up_to_date": 0.72, "capa_on_time": 0.90}` | period, bia_coverage, plans_up_to_date, capa_on_time |
| **bcm.kpi.threshold_breach** | Odoo KPI Module | Orchestrator, Notifications | `{"kpi": "bia_coverage", "value": 0.65, "threshold": 0.80}` | kpi, value |
| **bcm.exercise.scheduled** | Odoo Exercise Module | EventBus, Calendar | `{"exercise_id": 5, "date": "2024-02-01"}` | exercise_id |
| **bcm.exercise.completed** | Odoo Exercise Module | Orchestrator, KPI | `{"exercise_id": 5, "results": {...}}` | exercise_id, results |
| **bcm.training.scheduled** | Odoo Training Module | EventBus, Notifications | `{"training_id": 8, "attendees": [1,2,3]}` | training_id |
| **bcm.training.completed** | Odoo Training Module | Orchestrator, KPI | `{"training_id": 8, "attendees": [1,2,3], "completion_rate": 0.95}` | training_id, attendees |
| **bcm.audit.scheduled** | Odoo Audit Module | EventBus, Calendar | `{"audit_id": 3, "date": "2024-03-01"}` | audit_id |
| **bcm.audit.started** | Odoo Audit Module | Orchestrator | `{"audit_id": 3, "scope": "full"}` | audit_id |
| **bcm.audit.findings** | Odoo Audit Module | Orchestrator | `{"audit_id": 3, "findings": [...]}` | audit_id |
| **bcm.audit.gap_found** | Odoo Audit Module | Orchestrator, CAPA | `{"finding_id": 15, "severity": "high", "capa_required": true}` | finding_id |
| **bcm.audit.completed** | Odoo Audit Module | EventBus, Reports | `{"audit_id": 3, "result": "passed"}` | audit_id |
| **bcm.client.created** | Odoo Clients Module | Orchestrator, EventBus | `{"client_id": 100, "name": "Demo Hospital", "sector": "healthcare"}` | client_id |
| **bcm.client.updated** | Odoo Clients Module | Orchestrator | `{"client_id": 100, "changes": ["status", "dpa_signed"]}` | client_id |
| **bcm.context.imported** | Odoo Context Module | Orchestrator | `{"context_id": 1, "type": "organizational"}` | context_id |
| **bcm.context.updated** | Odoo Context Module | EventBus | `{"context_id": 1, "changes": [...]}` | context_id |
| **bcm.process.identified** | Orchestrator | Odoo | `{"process_name": "EHR", "criticality": "high"}` | process_name |
| **bcm.critical_process.detected** | Orchestrator | Odoo, Notifications | `{"process_id": 5, "rto": 2, "priority": 1}` | process_id |
| **bcm.governance.review_scheduled** | Odoo Governance | EventBus | `{"review_id": 2, "date": "2024-04-01"}` | review_id |
| **bcm.governance.review_completed** | Odoo Governance | EventBus | `{"review_id": 2, "decisions": [...]}` | review_id |
| **bcm.governance.policy_updated** | Odoo Governance | EventBus | `{"policy_id": 7, "version": "3.0"}` | policy_id |
| **bcm.ai.decision.created** | Orchestrator | Frontend | `{"decision_id": "dec_123", "type": "bcp_generation"}` | decision_id |
| **bcm.ai.decision.approved** | Orchestrator | Odoo, EventBus | `{"decision_id": "dec_123", "executed": true}` | decision_id |
| **bcm.ai.decision.rejected** | Orchestrator | EventBus | `{"decision_id": "dec_123", "reason": "manual_override"}` | decision_id |

## Event Publishing Patterns

### Direct Publishing (Odoo → EventBus)
```python
# Via bcm.webhook.mixin
self.send_event_to_eventbus('bcm.bia.completed', {
    'bia_id': self.id,
    'rto': self.optimized_rto_hours,
    'rpo': self.optimized_rpo_minutes,
    'critical_processes': [p.id for p in self.critical_processes]
})
```

### Orchestrator-Mediated Events
```python
# Orchestrator receives event, processes, publishes new event
async def handle_bia_completed(event_data):
    # Process BIA completion
    decision = create_bcp_generation_decision(event_data)
    # Publish decision event
    await publish_event('bcm.ai.decision.created', decision)
```

### Frontend-Triggered Events
```javascript
// Via EventBus API
await eventBusService.publish({
    event_type: 'bcm.incident.reported',
    tenant_id: currentTenant,
    data: { incident_id: 20, severity: 'critical' }
})
```

## Event Channels (Redis)

### Tenant-Specific Channels
- Pattern: `bcm.{tenant_id}`
- Example: `bcm.demo_hospital`
- Usage: All events for a specific tenant

### Event Type Channels
- Pattern: `bcm.event.{event_type}`
- Example: `bcm.event.bia.completed`
- Usage: All events of specific type across tenants

### Dual Publishing
All events are published to both:
1. Tenant channel for client isolation
2. Event type channel for system-wide monitoring

## Event Validation Rules

### Required Field Validation
EventBus validates required fields for registered event types:
```python
EVENT_VALIDATION_RULES = {
    'bcm.bia.completed': ['bia_id', 'rto', 'rpo', 'critical_processes'],
    'bcm.incident.reported': ['incident_id', 'severity'],
    # ... more rules
}
```

### Schema Validation
- Event type: 3-255 characters
- Tenant ID: Required, non-empty
- Event ID: Optional, used for idempotency
- Correlation ID: Optional, for event chaining

## Event Storage

### PostgreSQL Schema
```sql
events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(255),
    tenant_id VARCHAR(255),
    data JSONB,
    user_id VARCHAR(255),
    correlation_id VARCHAR(255),
    event_id VARCHAR(255) UNIQUE,
    metadata JSONB,
    created_at TIMESTAMP,
    status VARCHAR(50)
)
```

### Retention Policy
- Default: 90 days
- Configurable per event type
- Archive to cold storage after retention

## Event Monitoring

### Real-time Streams
- SSE: `/api/events/stream?tenant_id=xxx`
- WebSocket: `/api/events/ws?tenant_id=xxx`
- Heartbeat: Every 1 second (SSE), 0.5 seconds (WS)

### Historical Queries
- Endpoint: `/api/events/history`
- Filters: tenant_id, event_type, date range, correlation_id
- Pagination: limit, offset

### Statistics
- Endpoint: `/api/events/stats?tenant_id=xxx`
- Metrics: Total events, unique types, top events, event rate

## Integration Points

### Odoo Webhooks
- Configuration: `bcm.config` model
- URL: Stored in `eventbus_url` field
- Authentication: API key (planned)

### Orchestrator Subscriptions
- Pattern: `bcm.*` via Redis pub/sub
- Processing: Async handlers
- Decision creation: Auto-triggered

### Frontend Consumption
- EventMonitor component: SSE subscription
- AIOrchestrator component: Decision events
- PDCADashboard: KPI events
