# Decision Center API

FastAPI wrapper над **InfrastructureDecisionCenter** из `policy_engine`.

## Архитектура

```
┌──────────────────────────────────────┐
│   REST API (FastAPI)                 │
│   - POST /api/v1/decisions           │
│   - GET  /api/v1/escalations         │
│   - POST /api/v1/approvals/respond   │
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│   InfrastructureDecisionCenter       │
│   (infrastructure/policy_engine)     │
│   - decide_recovery_action()         │
│   - escalate()                       │
│   - approve_action()                 │
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│   Enhanced Features (Optional)       │
│   - AI Hub                           │
│   - Prometheus Metrics               │
│   - EventBus                         │
└──────────────────────────────────────┘
```

## Быстрый Старт

### Local Development

```bash
cd infrastructure/decision_center_api

# Install dependencies
pip install -r requirements.txt

# Run API
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

API доступен на http://localhost:8080

### Docker Compose

```bash
cd infrastructure/decision_center_api

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f decision-center-api

# Check health
curl http://localhost:8080/health
```

### Kubernetes

```bash
cd infrastructure/decision_center_api

# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n decision-center
kubectl get svc -n decision-center

# Port forward
kubectl port-forward -n decision-center svc/decision-center-api 8080:8080
```

## API Endpoints

### Health & Monitoring

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /stats` - Decision Center statistics

### Decisions

- `POST /api/v1/decisions` - Request decision
- `GET /api/v1/decisions/{id}` - Get decision by ID

### Escalations

- `POST /api/v1/escalations` - Create escalation
- `GET /api/v1/escalations` - List active escalations
- `GET /api/v1/escalations/{id}` - Get escalation by ID

### Approvals

- `GET /api/v1/approvals` - List pending approvals
- `POST /api/v1/approvals/respond` - Approve/reject

## Usage Examples

### Request Decision

```bash
curl -X POST http://localhost:8080/api/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "service": "api-gateway",
    "action": "restart",
    "reason": "High error rate detected",
    "context": {
      "error_rate": 15.5,
      "threshold": 5.0
    },
    "priority": "high",
    "current_attempt": 1
  }'
```

**Response:**
```json
{
  "decision_id": "dec_20251016_123456",
  "outcome": "approved",
  "can_proceed": true,
  "reasoning": "Recovery approved for api-gateway: within policy limits",
  "confidence_score": 1.0,
  "policy_reference": "recovery/api-gateway/restart",
  "requires_approval": false,
  "ai_enhanced": false,
  "decided_at": "2025-10-16T12:34:56.789Z"
}
```

### Create Escalation

```bash
curl -X POST http://localhost:8080/api/v1/escalations \
  -H "Content-Type: application/json" \
  -d '{
    "service": "database",
    "reason": "Repeated failures after 3 restart attempts",
    "severity": "critical",
    "context": {
      "attempts": 3,
      "last_error": "Connection timeout"
    }
  }'
```

### Get Statistics

```bash
curl http://localhost:8080/stats
```

**Response:**
```json
{
  "total_decisions": 150,
  "approved_decisions": 120,
  "rejected_decisions": 25,
  "escalated_decisions": 5,
  "auto_approved": 115,
  "manual_approved": 5,
  "ai_consultations": 12,
  "ai_enhanced_decisions": 10,
  "pending_approvals": 2,
  "active_escalations": 3,
  "approval_rate": 80.0,
  "automation_rate": 95.8
}
```

## Features

### ✅ Production Ready

- FastAPI with async support
- Pydantic models for validation
- Comprehensive error handling
- Health checks
- Prometheus metrics
- Docker & Kubernetes ready

### ✅ Enhanced Decision Center

- AI-assisted decisions (optional)
- Prometheus monitoring (enabled)
- EventBus integration (optional)
- Policy engine
- Audit logging
- Escalation workflow
- Approval workflow

### ✅ Backward Compatible

- Uses proven `InfrastructureDecisionCenter` from `policy_engine`
- All existing logic preserved
- Infrastructure Coordinator continues to work

## Configuration

Environment variables:

```bash
# Redis (EventBus)
REDIS_HOST=localhost
REDIS_PORT=6379

# Logging
LOG_LEVEL=INFO

# AI Hub
AI_HUB_ENABLED=true
AI_HUB_TIER3_ENABLED=true

# Metrics
METRICS_ENABLED=true
```

## Monitoring

### Prometheus Metrics

Available at `/metrics`:

```
# Decision counters
decision_center_decisions_total{outcome="approved",service="api-gateway",action_type="restart"} 45

# Decision duration
decision_center_decision_duration_seconds_sum{service="api-gateway",action_type="restart"} 2.3
decision_center_decision_duration_seconds_count{service="api-gateway",action_type="restart"} 45

# Escalations
decision_center_escalations_total{severity="critical",service="database"} 3

# AI consultations
decision_center_ai_consultations_total{confidence_level="high"} 8

# Pending approvals
decision_center_pending_approvals 2
```

### Health Check

```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-16T12:34:56.789Z",
  "decision_center": "running",
  "ai_hub_available": true,
  "metrics_enabled": true,
  "eventbus_connected": true
}
```

## Deployment

### Docker

```bash
# Build
docker build -t decision-center-api:latest .

# Run
docker run -d \
  -p 8080:8080 \
  -e REDIS_HOST=host.docker.internal \
  decision-center-api:latest
```

### Kubernetes

See `k8s/` directory for manifests:
- `deployment.yaml` - Deployment with 3 replicas
- `service.yaml` - LoadBalancer service
- `hpa.yaml` - Horizontal Pod Autoscaler
- `configmap.yaml` - Configuration
- `secret.yaml` - Secrets

### Production Checklist

- [ ] Configure Redis for EventBus
- [ ] Set up Prometheus scraping
- [ ] Configure Grafana dashboards
- [ ] Set up alerts for escalations
- [ ] Review policy files
- [ ] Configure approval workflows
- [ ] Test health checks
- [ ] Set up logging aggregation

## Integration

### From Infrastructure Coordinator

```python
# Option 1: Direct (existing)
from infrastructure.policy_engine import InfrastructureDecisionCenter

decision_center = InfrastructureDecisionCenter()
decision, can_proceed = await decision_center.decide_recovery_action(...)

# Option 2: HTTP Client (new)
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://decision-center-api:8080/api/v1/decisions",
        json={
            "service": "api-gateway",
            "action": "restart",
            "reason": "High error rate",
            "current_attempt": 1
        }
    )
    decision = response.json()
    can_proceed = decision["can_proceed"]
```

### From External Services

```bash
# Any service can call via HTTP
curl -X POST http://decision-center-api:8080/api/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{"service": "...", "action": "...", "reason": "..."}'
```

## Roadmap

- [x] FastAPI wrapper
- [x] Docker & docker-compose
- [x] Kubernetes manifests
- [x] Prometheus metrics
- [x] AI Hub integration
- [ ] Real AI (Anthropic API)
- [ ] PostgreSQL persistence
- [ ] Authentication & authorization
- [ ] Rate limiting
- [ ] API versioning (v2)

## License

Internal use only.
