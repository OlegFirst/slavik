# BCM Platform - External Service Adapters

## Architecture Overview

All external service integrations follow the **Event-Driven Adapter Pattern**:

```
EventBus ← publish ← Adapter ← call → External Service
   ↓                   ↑
subscribe           subscribe
   ↓                   ↑
Adapter → call → External Service → publish → EventBus
```

## Adapter Structure

Each adapter is a standalone microservice with:

### Standard Files
```
adapters/{service}/
├── app.py              # FastAPI application
├── config.py           # Configuration management
├── models.py           # Pydantic schemas
├── services/
│   ├── eventbus.py     # EventBus integration
│   ├── {service}.py    # External service client
│   └── processor.py    # Business logic
├── Dockerfile
├── requirements.txt
└── docker-compose.yml
```

### Event Pattern
1. **Subscribe** to BCM events via Redis pub/sub
2. **Process** event data and call external service
3. **Publish** result event back to EventBus
4. **Handle** tenant isolation via tenant_id

## Implemented Adapters

### 1. Document Processor (`/adapters/document-processor/`)
**Events**: `bcm.doc.uploaded` → `bcm.doc.analyzed`
**Purpose**: Document analysis, compliance scoring, ISO clause extraction

### 2. TheHive Adapter (`/adapters/thehive/`)
**Events**: `bcm.incident.opened` → `bcm.incident.updated`
**Purpose**: Security incident case management integration

### 3. Simulation Adapter (`/adapters/simulation/`)
**Events**: `bcm.exercise.scheduled` → `bcm.exercise.resulted`
**Purpose**: Business continuity exercise simulation and metrics

### 4. Training Adapter (`/adapters/training/`)
**Events**: `bcm.training.sync` → `bcm.training.updated`
**Purpose**: LMS integration for training status synchronization

### 5. Notifications Worker (`/adapters/notifications/`)
**Events**: Multiple subscriptions → notification delivery
**Purpose**: Multi-channel notifications (email, SMS, Telegram, WebPush)

### 6. SSO Integration (`/adapters/keycloak/`)
**Purpose**: OIDC authentication, JWT token validation, role mapping

## Configuration

### Environment Variables
```bash
# Common to all adapters
REDIS_URL=redis://localhost:6379
EVENTBUS_URL=http://localhost:8001
TENANT_ID=demo_hospital

# Service-specific
DOCUMENT_PROCESSOR_URL=http://document-processor:8000
THEHIVE_URL=http://thehive:9000
THEHIVE_API_KEY=xxx
SIMULATION_ENGINE=jaamsim
LMS_URL=http://moodle.local
LMS_TOKEN=xxx
KEYCLOAK_URL=http://keycloak:8080
```

### Multi-Tenancy
All adapters enforce tenant isolation:
- Events filtered by `tenant_id`
- External service calls include tenant context
- Configuration per tenant supported
- Data segregation maintained

## Development Guidelines

### 1. Event Handling
```python
@app.on_event("startup")
async def startup():
    await eventbus.subscribe("bcm.*", process_event)

async def process_event(event_data: dict):
    tenant_id = event_data.get("tenant_id")
    if not tenant_id:
        logger.warning("Event missing tenant_id, skipping")
        return
    
    # Process event...
    result = await external_service.process(event_data, tenant_id)
    
    # Publish result
    await eventbus.publish({
        "event_type": "bcm.result.event",
        "tenant_id": tenant_id,
        "data": result
    })
```

### 2. Error Handling
- Retry logic with exponential backoff
- Dead letter queue for failed events
- Comprehensive logging and monitoring
- Graceful degradation

### 3. Testing
- Unit tests for business logic
- Integration tests with mock services
- End-to-end tests with real services
- Performance testing under load

## Deployment

### Docker Compose
```yaml
# docker-compose.adapters.yml
version: '3.8'
services:
  document-processor:
    build: ./adapters/document-processor
    depends_on: [eventbus, redis]
    
  thehive-adapter:
    build: ./adapters/thehive
    depends_on: [eventbus, redis]
    
  # ... other adapters
```

### Kubernetes
```yaml
# k8s/adapters-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: document-processor
spec:
  replicas: 2
  selector:
    matchLabels:
      app: document-processor
  template:
    spec:
      containers:
      - name: document-processor
        image: bcm/document-processor:latest
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
```

## Monitoring

### Health Checks
All adapters expose `/health` endpoint:
```json
{
  "status": "healthy",
  "service": "document-processor",
  "version": "1.0.0",
  "dependencies": {
    "eventbus": "healthy",
    "external_service": "healthy"
  }
}
```

### Metrics
- Event processing rate
- External service response times
- Error rates and retry counts
- Tenant-specific metrics

### Logging
Structured JSON logging with:
- Correlation IDs for event tracing
- Tenant ID in all log entries
- Performance metrics
- Error details and stack traces
