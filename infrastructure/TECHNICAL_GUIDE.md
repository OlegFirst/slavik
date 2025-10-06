# Infrastructure Technical Guide

**Обновлено:** 2025-10-06
**Для:** Developers & DevOps

---

## 📋 Содержание

1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [Service Configuration](#service-configuration)
4. [Development Workflow](#development-workflow)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
```bash
# Required
- Docker 24.0+
- Docker Compose 2.20+
- Python 3.11+
- PostgreSQL client (psql)
- Redis CLI

# Recommended
- git
- curl/httpie
- jq (JSON processing)
```

### 1. Clone & Setup
```bash
# Clone repository
git clone <repo-url>
cd AI-Platform-ISO

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 2. Start Core Services
```bash
# Start database & redis
docker-compose up -d postgres redis

# Verify
docker-compose ps
psql $DATABASE_URL -c "SELECT version();"
redis-cli -u $REDIS_URL ping
```

### 3. Initialize Infrastructure
```bash
# Apply database migrations
cd infrastructure/database
python apply_migrations_simple.py

# Initialize Qdrant collections
cd ../vector-db
pip install -r requirements.txt
python test_connection.py
python qdrant/init_collections.py

# Start EventBus
cd ../eventbus
python -m eventbus.main
```

### 4. Verify Services
```bash
# Health checks
curl http://localhost:3001/health  # API Gateway
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:6333/  # Qdrant

# Service discovery
curl http://localhost:8500/v1/catalog/services  # Consul
```

---

## Environment Setup

### .env Configuration

#### Core Infrastructure
```bash
# Database (Supabase)
DATABASE_URL=postgresql://postgres.xxx:password@xxx.supabase.co:5432/postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=bcm_platform

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=  # Optional
```

#### Qdrant Vector DB
```bash
# Qdrant Cloud
QDRANT_URL=https://xxx.eu-west-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
QDRANT_CLUSTER_ID=xxx

# Collection settings
QDRANT_EMBEDDING_DIMENSION=1536  # OpenAI ada-002
QDRANT_DISTANCE_METRIC=Cosine
```

#### Authentication
```bash
# JWT
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Keycloak SSO (optional)
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=bcm-platform
KEYCLOAK_CLIENT_ID=bcm-client
KEYCLOAK_CLIENT_SECRET=your-keycloak-secret
```

#### AI Services
```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229
```

#### Services URLs
```bash
# Internal services
API_GATEWAY_URL=http://api-gateway:3001
EXECUTION_ENGINE_URL=http://execution-engine:8000
INTELLIGENT_CORE_URL=http://intelligent-core:9000

# External services
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001
```

#### Notifications
```bash
# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@bcm-platform.com

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
SLACK_CHANNEL=#alerts

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

#### Message Queue
```bash
# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost/
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
RABBITMQ_MANAGEMENT_URL=http://localhost:15672
```

#### Monitoring
```bash
# Prometheus
PROMETHEUS_URL=http://prometheus:9090

# Grafana
GRAFANA_URL=http://grafana:3002
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=changeme

# Sentry (optional)
SENTRY_DSN=https://xxx@sentry.io/xxx
```

#### Secrets Manager
```bash
# HashiCorp Vault
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=root-token
VAULT_ROOT_TOKEN=root-token
VAULT_NAMESPACE=bcm-platform
```

#### General
```bash
# Environment
ENVIRONMENT=development  # development, staging, production
DEBUG=true
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Application
APP_NAME=BCM Platform
APP_VERSION=1.0.0
```

---

## Service Configuration

### 1. Database Service

**Location:** `infrastructure/database/`

#### Initialize Migrations
```bash
cd infrastructure/database

# Apply all migrations
python apply_migrations_simple.py

# Or manually
psql $DATABASE_URL -f migrations_source/006_bia_risk_schemas.sql
psql $DATABASE_URL -f migrations_source/007_governance_audit_schemas.sql
# ... etc
```

#### Test Connection
```python
from infrastructure.database.managers.supabase_client import get_supabase_client

client = get_supabase_client()
result = client.table('users').select('*').execute()
print(result.data)
```

---

### 2. EventBus Service

**Location:** `infrastructure/eventbus/`

#### Start EventBus
```bash
cd infrastructure/eventbus

# Development (Memory transport)
export EVENTBUS_TRANSPORT=memory
python -m eventbus.main

# Production (Redis transport)
export EVENTBUS_TRANSPORT=redis
export REDIS_URL=redis://localhost:6379
python -m eventbus.main
```

#### Publish Event
```python
from infrastructure.eventbus import EventBus

eventbus = EventBus()
await eventbus.connect()

await eventbus.publish(
    topic="bia.risk.created",
    data={"risk_id": "R-001", "severity": "high"}
)
```

#### Subscribe to Events
```python
async def handle_risk_created(event):
    print(f"Risk created: {event['data']['risk_id']}")

await eventbus.subscribe(
    topic="bia.risk.created",
    handler=handle_risk_created
)
```

**Документация:** [eventbus/QUICKSTART.md](eventbus/QUICKSTART.md)

---

### 3. Vector DB Service

**Location:** `infrastructure/vector-db/`

#### Test Connection
```bash
cd infrastructure/vector-db
pip install -r requirements.txt
python test_connection.py
```

#### Initialize Collections
```bash
# Create all collections
python qdrant/init_collections.py

# Reset collections (delete + recreate)
python qdrant/init_collections.py reset
```

#### Use in Code
```python
from infrastructure.vector_db.qdrant import QdrantVectorDB

# Initialize client
db = QdrantVectorDB(collection="knowledge_base")

# Upsert vectors
db.upsert(
    vectors=[[0.1, 0.2, ..., 0.5]],  # 1536-dim
    payloads=[{
        "text": "ISO 22301 requires BIA...",
        "source": "ISO 22301:2019",
        "category": "standard"
    }],
    ids=["doc-001"]
)

# Search
results = db.search(
    query_vector=[0.1, 0.2, ..., 0.5],
    limit=5,
    filters={"category": "standard"},
    min_score=0.7
)

for hit in results:
    print(f"{hit['score']:.3f}: {hit['payload']['text']}")
```

**Документация:** [vector-db/QUICKSTART.md](vector-db/QUICKSTART.md)

---

### 4. API Gateway

**Location:** `infrastructure/security/api-gateway/`

#### Start Gateway
```bash
cd infrastructure/security/api-gateway
uvicorn main:app --host 0.0.0.0 --port 3001
```

#### Configuration
```python
# config.py
RATE_LIMIT_REQUESTS = 100  # per minute
RATE_LIMIT_WINDOW = 60  # seconds

CORS_ORIGINS = [
    "http://localhost:3000",
    "https://your-domain.com"
]

JWT_SECRET = os.getenv("JWT_SECRET")
```

#### Add Route
```python
# routes/bia_routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/bia", tags=["BIA"])

@router.get("/risks")
async def get_risks():
    return {"risks": [...]}
```

---

### 5. Monitoring Service

**Location:** `infrastructure/monitoring/`

#### Start Monitoring Stack
```bash
cd infrastructure/monitoring
docker-compose up -d
```

#### Access Dashboards
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3002 (admin/changeme)

#### Add Metrics
```python
from prometheus_client import Counter, Histogram

# Define metrics
request_counter = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency'
)

# Use metrics
request_counter.labels(method='GET', endpoint='/api/risks', status='200').inc()
request_duration.observe(0.5)  # 500ms
```

---

### 6. Notification Service

**Location:** `infrastructure/notification-service/`

#### Configuration
```bash
# .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
TELEGRAM_BOT_TOKEN=your-bot-token
```

#### Send Notification
```python
from infrastructure.notification_service import NotificationService

notifier = NotificationService()

# Email
await notifier.send_email(
    to="user@example.com",
    subject="Risk Alert",
    body="High severity risk detected"
)

# Slack
await notifier.send_slack(
    channel="#alerts",
    message="🚨 High severity risk detected"
)

# Telegram
await notifier.send_telegram(
    chat_id="123456789",
    message="🚨 High severity risk detected"
)
```

---

### 7. WebSocket Service

**Location:** `infrastructure/realtime-websocket/`

#### Start WebSocket Server
```bash
cd infrastructure/realtime-websocket
uvicorn main:app --host 0.0.0.0 --port 8001
```

#### Client Connection
```javascript
// Frontend
const ws = new WebSocket('ws://localhost:8001/ws');

ws.onopen = () => {
    console.log('Connected');
    ws.send(JSON.stringify({ type: 'subscribe', topic: 'risks' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

#### Server-side Broadcast
```python
from infrastructure.realtime_websocket import WebSocketManager

manager = WebSocketManager()

# Broadcast to all clients
await manager.broadcast({
    "type": "risk.created",
    "data": {"risk_id": "R-001"}
})

# Send to specific client
await manager.send_personal(
    connection_id="client-123",
    message={"type": "notification", "text": "Hello"}
)
```

---

## Development Workflow

### 1. Local Development

```bash
# Terminal 1: Database & Redis
docker-compose up postgres redis

# Terminal 2: EventBus
cd infrastructure/eventbus
python -m eventbus.main

# Terminal 3: API Gateway
cd infrastructure/security/api-gateway
uvicorn main:app --reload

# Terminal 4: Your service
cd platform-services/bia-service
uvicorn main:app --reload --port 8002
```

### 2. Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Infrastructure tests
cd infrastructure/database
python test_db_managers.py

cd ../eventbus
pytest tests/
```

### 3. Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy .

# Format
black .
ruff format .
```

---

## Production Deployment

### 1. Docker Compose (Simple)

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Scale service
docker-compose up -d --scale bia-service=3
```

### 2. Kubernetes (Advanced)

```bash
# Apply manifests
kubectl apply -f infrastructure/kubernetes/

# Check pods
kubectl get pods -n bcm-platform

# Logs
kubectl logs -f deployment/api-gateway -n bcm-platform
```

### 3. Health Checks

```bash
# API Gateway
curl http://api-gateway:3001/health

# EventBus
curl http://eventbus:8000/health

# Prometheus
curl http://prometheus:9090/-/healthy

# Qdrant
curl http://qdrant-cloud-url/
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check permissions
psql $DATABASE_URL -c "SHOW search_path;"

# List tables
psql $DATABASE_URL -c "\dt"
```

**Fix:** Verify `DATABASE_URL` in `.env`, check firewall, verify Supabase project is active.

---

### Redis Connection Issues

```bash
# Test connection
redis-cli -u $REDIS_URL ping

# Check keys
redis-cli -u $REDIS_URL KEYS "*"

# Monitor commands
redis-cli -u $REDIS_URL MONITOR
```

**Fix:** Verify `REDIS_URL`, check Redis server is running (`docker-compose ps`).

---

### EventBus Not Receiving Events

```bash
# Check EventBus logs
docker-compose logs eventbus

# Test publish
python -c "
from infrastructure.eventbus import EventBus
import asyncio

async def test():
    eb = EventBus()
    await eb.connect()
    await eb.publish('test.topic', {'msg': 'hello'})

asyncio.run(test())
"
```

**Fix:** Check `EVENTBUS_TRANSPORT` (should be `redis` for production), verify Redis connection.

---

### Qdrant Connection Failed

```bash
# Test connection
python infrastructure/vector-db/test_connection.py

# Check credentials
echo $QDRANT_URL
echo $QDRANT_API_KEY
```

**Fix:** Verify Qdrant Cloud credentials in `.env`, check Qdrant dashboard for cluster status.

---

### API Gateway 401 Unauthorized

```bash
# Generate JWT token
python -c "
import jwt
import os
from datetime import datetime, timedelta

payload = {
    'sub': 'user-123',
    'exp': datetime.utcnow() + timedelta(hours=24)
}
token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')
print(token)
"

# Test with token
curl -H "Authorization: Bearer <token>" http://localhost:3001/api/risks
```

**Fix:** Verify `JWT_SECRET` in `.env`, check token expiration.

---

### High Memory Usage

```bash
# Check container stats
docker stats

# Check Python memory
py-spy top --pid <pid>

# Check Redis memory
redis-cli -u $REDIS_URL INFO memory
```

**Fix:** Increase container limits in `docker-compose.yml`, optimize queries, add caching.

---

## Next Steps

1. **Configure remaining services:** notification, websocket, message-queue
2. **Setup monitoring dashboards** in Grafana
3. **Add integration tests** for critical flows
4. **Setup CI/CD pipeline** with GitHub Actions
5. **Production hardening:** secrets management, SSL, rate limiting

---

## Resources

- [OVERVIEW.md](OVERVIEW.md) - Architecture overview
- [README.md](README.md) - Main infrastructure README
- Service-specific READMEs in each service folder
- [Shared Library](../shared/) - Common code

---

**Questions?** See service-specific documentation or check [архив/](архив/) for historical context.
