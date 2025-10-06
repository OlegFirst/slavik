# Unified Workflow API

REST API for BPMN workflow management with gateway support, AI recommendations, and full observability.

## Features

- ✅ **BPMN 2.0** - Full support including gateways (XOR, AND, OR)
- ✅ **PostgreSQL** - Persistent storage via Supabase
- ✅ **Redis** - Caching for visual state
- ✅ **EventBus** - Pub/sub for workflow events
- ✅ **Prometheus** - Metrics collection
- ✅ **Multi-tenancy** - Header-based tenant isolation
- ✅ **Rate Limiting** - Built-in protection
- ✅ **AI Ready** - Framework for Workflow Intelligence integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export REDIS_HOST="localhost"
export REDIS_PORT=6379
```

### 3. Run Server

```bash
python main.py
```

Server runs on `http://localhost:8010`

### 4. View API Docs

- Swagger UI: http://localhost:8010/docs
- ReDoc: http://localhost:8010/redoc

## API Endpoints

### Processes

#### Start Workflow
```bash
POST /processes
Headers: X-Tenant-ID: acme-corp
Body:
{
  "bpmn_xml": "<?xml version=\"1.0\"?>...",
  "process_name": "BIA Assessment",
  "initial_variables": {
    "org_id": "org-123",
    "org_context": {"industry": "healthcare"}
  },
  "started_by": "john@acme.com"
}

Response:
{
  "instance_id": "uuid",
  "status": "started",
  "message": "Workflow 'BIA Assessment' started successfully"
}
```

#### List Processes
```bash
GET /processes?module=bia
Headers: X-Tenant-ID: acme-corp

Response:
{
  "processes": [...],
  "count": 5
}
```

### Instances

#### Get Visual State (for UI)
```bash
GET /instances/{instance_id}/visual-state
Headers: X-Tenant-ID: acme-corp

Response:
{
  "type": "bpmn",
  "bpmn_xml": "<?xml version...",
  "current_activities": ["Task_Analyze"],
  "active_tasks": [
    {
      "id": "uuid",
      "name": "Analyze Business Impact",
      "assignee": "john@acme.com",
      "ai_recommendations": [...]
    }
  ],
  "workflow_context": {...},
  "predictions": {...}
}
```

#### List Instances
```bash
GET /instances?status_filter=ACTIVE
Headers: X-Tenant-ID: acme-corp
```

#### Terminate Instance
```bash
DELETE /instances/{instance_id}?reason=User+cancelled
Headers: X-Tenant-ID: acme-corp
```

### Tasks

#### Complete Task
```bash
POST /tasks/{task_id}/complete
Headers: X-Tenant-ID: acme-corp
Body:
{
  "variables": {
    "processes_identified": 5,
    "critical_processes": [...]
  },
  "completed_by": "john@acme.com"
}

Response:
{
  "status": "completed",
  "task_id": "uuid",
  "message": "Task completed successfully"
}
```

**Note:** Gateway evaluation happens automatically when task completes!

#### Assign Task
```bash
POST /tasks/{task_id}/assign
Headers: X-Tenant-ID: acme-corp
Body:
{
  "assignee": "jane@acme.com"
}
```

#### Get User's Tasks (Inbox)
```bash
GET /users/john@acme.com/tasks?status_filter=ACTIVE
Headers: X-Tenant-ID: acme-corp

Response:
{
  "user": "john@acme.com",
  "tasks": [
    {
      "id": "uuid",
      "name": "Analyze Impact",
      "process_name": "BIA Assessment",
      "ai_recommendations": [...],
      "estimated_hours": 2.5
    }
  ],
  "count": 1
}
```

## Monitoring

### Health Check
```bash
curl http://localhost:8010/health

{
  "status": "healthy",
  "service": "unified-workflow-api",
  "version": "2.0.0",
  "timestamp": "2025-10-05T...",
  "eventbus": true,
  "cache": true,
  "rate_limiter": true
}
```

### Prometheus Metrics
```bash
curl http://localhost:8010/metrics

# HELP workflow_instances_total Total workflow instances created
# TYPE workflow_instances_total counter
workflow_instances_total{tenant_id="acme-corp",module="bia"} 42.0

# HELP workflow_tasks_completed_total Total tasks completed
# TYPE workflow_tasks_completed_total counter
workflow_tasks_completed_total{tenant_id="acme-corp",module="bia"} 156.0

# HELP workflow_task_duration_seconds Task completion duration
# TYPE workflow_task_duration_seconds histogram
workflow_task_duration_seconds_bucket{tenant_id="acme-corp",module="bia",task_type="user_task",le="0.5"} 10.0
...

# HELP workflow_active_instances Currently active workflow instances
# TYPE workflow_active_instances gauge
workflow_active_instances{tenant_id="acme-corp",module="bia"} 5.0
```

### Configure Prometheus

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'workflow-api'
    static_configs:
      - targets: ['localhost:8010']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

## Integration

### With Frontend (bpmn-js)

```typescript
// React component
import BpmnViewer from 'bpmn-js/lib/Viewer';

const WorkflowMonitor = ({ instanceId }) => {
  const [state, setState] = useState(null);

  useEffect(() => {
    // Fetch visual state
    fetch(`http://localhost:8010/instances/${instanceId}/visual-state`, {
      headers: {'X-Tenant-ID': 'acme-corp'}
    })
    .then(res => res.json())
    .then(data => setState(data));
  }, [instanceId]);

  useEffect(() => {
    if (!state) return;

    // Render BPMN diagram
    const viewer = new BpmnViewer({ container: '#canvas' });
    viewer.importXML(state.bpmn_xml);

    // Highlight active tasks
    state.current_activities.forEach(id => {
      viewer.get('canvas').addMarker(id, 'highlight');
    });

    // Add AI recommendation overlays
    state.active_tasks.forEach(task => {
      viewer.get('overlays').add(task.activity_id, {
        html: `<div class="ai-tip">${task.ai_tip}</div>`
      });
    });
  }, [state]);

  return <div id="canvas" style={{ height: '600px' }} />;
};
```

### With EventBus Subscribers

```python
from infrastructure.eventbus import create_eventbus, Event

# Subscribe to workflow events
bus = create_eventbus('redis')

async def handle_task_completed(event: Event):
    print(f"Task completed: {event.data['task_id']}")
    # Send notification, update dashboard, etc.

await bus.subscribe('workflow.task.completed', handle_task_completed)
```

## Authentication (Production)

Replace header-based auth with JWT:

```python
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def get_tenant_from_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload["tenant_id"]
```

## Rate Limiting

Automatic rate limiting per tenant (using Redis):

- **Default:** 100 requests/minute per tenant
- **Configure:** Set `RATE_LIMIT_PER_MINUTE` env var

## Performance

### Caching

Visual state cached for 30 seconds in Redis:
- Key: `visual_state:{tenant_id}:{instance_id}`
- Reduces DB queries for frequently viewed workflows

### Connection Pooling

Engine creates new instance per request.

**For production**, use connection pool:

```python
from sqlalchemy.pool import NullPool

# In DatabaseManager
engine = create_async_engine(
    database_url,
    poolclass=NullPool,  # Supabase manages pooling
    echo=False
)
```

## Testing

### Unit Test
```bash
pytest tests/test_api.py -v
```

### Integration Test
```bash
# Start API
python main.py &

# Run test
curl -X POST http://localhost:8010/processes \
  -H "X-Tenant-ID: test-tenant" \
  -H "Content-Type: application/json" \
  -d @test_workflow.json
```

### Load Test
```bash
# Use locust or k6
k6 run load_test.js
```

## Troubleshooting

### Database Connection Error

```
Failed to initialize workflow engine: connection refused
```

**Fix:** Check `DATABASE_URL` env var and Supabase connection

### EventBus Not Available

```
⚠️ EventBus not available: Redis connection failed
```

**Impact:** Events not published (workflow still works)
**Fix:** Start Redis or use memory backend

### Cache Miss

```
INFO: Cache miss for visual_state:acme-corp:uuid
```

**Normal:** First request or cache expired (30s TTL)

## Next Steps

1. **Add Authentication** - JWT token validation
2. **Connect Workflow Intelligence** - Enable AI recommendations
3. **Add WebSocket** - Real-time task updates
4. **Write Tests** - Integration test suite
5. **Add YAML Templates** - Template-based workflows

## License

Part of AI-Powered BCM Platform
