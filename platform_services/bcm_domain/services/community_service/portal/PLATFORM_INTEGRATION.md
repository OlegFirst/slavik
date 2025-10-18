# Portal Service - Platform Integration Guide

**Status:** ✅ Fully Integrated with BCM Platform
**Version:** 1.0.0
**Date:** 2025-10-02

---

## 🎯 Overview

Portal Service is now fully integrated with the BCM Platform, providing:

1. **Gateway Registration** - Accessible through Platform Gateway (Port 8000)
2. **EventBus Integration** - Emits events for all Portal activities
3. **Service Discovery** - Registered in Gateway's service registry
4. **Docker Orchestration** - Part of Platform docker-compose stack

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     BCM Platform Gateway (8000)                  │
│                                                                   │
│  Routes:                                                          │
│  - /api/community/portal/* → Portal Service (8031)               │
│  - /api/community/clients/* → Clients Service (8030)             │
│  - /api/platform/events/* → EventBus (8001)                      │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Portal Service (8031)                        │
│                                                                   │
│  Components:                                                      │
│  - Knowledge Hub (articles, AI generation, search)               │
│  - Scenario Marketplace (catalog, deployment, reviews)           │
│  - Community Forum (topics, posts, moderation, gamification)     │
│                                                                   │
│  Integrations:                                                    │
│  → Clients Service (8030) - Authentication, user profiles        │
│  → Validation Module (8022) - Exercise integration               │
│  → EventBus (8001) - Event publishing                            │
│  → PostgreSQL - Database (portal.* schema)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📡 Gateway Integration

### Service Registry

Portal is registered in `/Users/MD/ISO-22301—копия/services/SERVICES/PLATFORM/gateway/main.py`:

```python
SERVICE_REGISTRY = {
    # ... other services ...

    "portal": {
        "url": os.getenv("PORTAL_URL", "http://localhost:8031"),
        "health": "/health",
        "prefix": "/api/community/portal"
    },
    "clients": {
        "url": os.getenv("CLIENTS_URL", "http://localhost:8030"),
        "health": "/health",
        "prefix": "/api/community/clients"
    }
}
```

### Routing

Gateway automatically routes requests:

| Gateway Endpoint | Portal Endpoint | Description |
|-----------------|-----------------|-------------|
| `GET /api/community/portal/knowledge/articles` | `GET /api/portal/knowledge/articles` | List articles |
| `POST /api/community/portal/forum/topics` | `POST /api/portal/forum/topics` | Create topic |
| `GET /api/community/portal/scenarios` | `GET /api/portal/scenarios` | List scenarios |

**Example:**

```bash
# Direct access (development)
curl http://localhost:8031/api/portal/knowledge/articles

# Through Gateway (production)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/community/portal/knowledge/articles
```

---

## 🔔 EventBus Integration

### Event Types

Portal emits the following events (registered in EventBus):

#### Knowledge Hub Events

| Event Type | Required Fields | Description |
|-----------|----------------|-------------|
| `portal.knowledge.article_created` | `article_id`, `title`, `category` | Article created |
| `portal.knowledge.article_published` | `article_id`, `title`, `category` | Article published |
| `portal.knowledge.article_verified` | `article_id`, `verified` | Article verified by expert |

#### Scenario Events

| Event Type | Required Fields | Description |
|-----------|----------------|-------------|
| `portal.scenarios.deployed` | `scenario_id`, `scenario_name`, `exercise_id` | Scenario deployed as exercise |
| `portal.scenarios.reviewed` | `scenario_id`, `review_id`, `rating` | Scenario reviewed |

#### Forum Events

| Event Type | Required Fields | Description |
|-----------|----------------|-------------|
| `portal.forum.topic_created` | `topic_id`, `title`, `category_id` | Topic created |
| `portal.forum.post_created` | `post_id`, `topic_id` | Post created |
| `portal.forum.solution_marked` | `topic_id`, `post_id` | Post marked as solution |
| `portal.forum.content_flagged` | `flag_id`, `content_type`, `content_id`, `reason` | Content flagged |
| `portal.forum.moderation_action` | `flag_id`, `action` | Moderation action taken |

#### Gamification Events

| Event Type | Required Fields | Description |
|-----------|----------------|-------------|
| `portal.gamification.reputation_earned` | `points`, `reason` | Reputation earned |
| `portal.gamification.badge_earned` | `badge_id`, `badge_name`, `badge_tier` | Badge earned |

### EventBus Client

Portal uses `/integrations/eventbus_client.py` for publishing events:

```python
from integrations.eventbus_client import eventbus_client

# Example: Publish article created event
await eventbus_client.article_created(
    tenant_id="org-123",
    article_id=42,
    title="How to conduct BIA",
    category="BIA",
    author_id="user_456",
    ai_generated=False
)
```

### Subscribing to Portal Events

Other services can subscribe to Portal events via EventBus:

```python
# Subscribe to article creation events
import httpx

async def subscribe_to_articles():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "GET",
            "http://localhost:8001/api/events/stream?tenant_id=org-123"
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    event = json.loads(line[6:])
                    if event["event_type"] == "portal.knowledge.article_created":
                        print(f"New article: {event['data']['title']}")
```

---

## 🐳 Docker Deployment

### Full Platform Stack

Use the Platform docker-compose to run the entire stack:

```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/PLATFORM

# Start all services (Gateway, EventBus, Portal, Clients, Database, Redis)
docker-compose -f docker-compose.platform.yml up -d

# Check logs
docker-compose -f docker-compose.platform.yml logs -f portal

# Check service health
curl http://localhost:8000/api/services

# Stop all services
docker-compose -f docker-compose.platform.yml down
```

### Services Included

The platform stack includes:

```yaml
services:
  - postgres (5432)      # PostgreSQL database
  - redis (6379)         # Redis cache
  - gateway (8000)       # API Gateway
  - eventbus (8001)      # EventBus service
  - portal (8031)        # Portal service (Knowledge Hub + Forum + Scenarios)
  - clients (8030)       # Clients service (Authentication)
```

### Environment Variables

Create `.env` file in Platform directory:

```bash
# Database
POSTGRES_USER=bcm_user
POSTGRES_PASSWORD=bcm_password
POSTGRES_DB=bcm_platform

# Security
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Debug
DEBUG=false
```

---

## 🧪 Testing Integration

### 1. Health Checks

```bash
# Gateway health
curl http://localhost:8000/health

# Portal health (direct)
curl http://localhost:8031/health

# EventBus health
curl http://localhost:8001/health
```

### 2. Service Registry

```bash
# Get all registered services
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/services
```

Expected response:
```json
{
  "portal": {
    "status": "healthy",
    "url": "http://portal:8031",
    "prefix": "/api/community/portal"
  },
  "eventbus": {
    "status": "healthy",
    "url": "http://eventbus:8001",
    "prefix": "/api/platform/events"
  }
}
```

### 3. Routing Test

```bash
# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "demo"}' \
  | jq -r '.access_token')

# Access Portal through Gateway
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/community/portal/knowledge/articles
```

### 4. EventBus Integration Test

```bash
# Create an article (should emit event)
curl -X POST http://localhost:8031/api/portal/knowledge/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article",
    "content": "Test content",
    "category": "General"
  }'

# Check event was published
curl http://localhost:8001/api/events/history?event_type=portal.knowledge.article_created
```

---

## 🔐 Authentication Flow

```
1. User requests access to Portal through Gateway
   → GET /api/community/portal/knowledge/articles
   ↓
2. Gateway validates JWT token
   ↓
3. Gateway extracts user info (user_id, tenant_id, roles)
   ↓
4. Gateway forwards request to Portal with headers:
   - X-User-ID: user_123
   - X-Tenant-ID: org_456
   - X-User-Roles: bcm_manager
   ↓
5. Portal processes request using user context
   ↓
6. Portal returns response to Gateway
   ↓
7. Gateway returns response to user
```

---

## 📊 Monitoring

### Gateway Metrics

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/metrics
```

Response:
```json
{
  "total_requests": 1523,
  "requests_per_service": {
    "portal": 456,
    "eventbus": 123,
    "clients": 234
  },
  "errors": 12,
  "error_rate": 0.0078,
  "uptime_seconds": 3600,
  "requests_per_second": 0.42
}
```

### EventBus Stats

```bash
curl http://localhost:8001/api/events/stats?tenant_id=org-123
```

Response:
```json
{
  "tenant_id": "org-123",
  "total_events": 789,
  "unique_event_types": 8,
  "top_event_types": [
    {"type": "portal.forum.post_created", "count": 234},
    {"type": "portal.knowledge.article_created", "count": 123},
    {"type": "portal.gamification.reputation_earned", "count": 456}
  ]
}
```

---

## 🔄 Data Flow Examples

### Example 1: User Creates Article

```
User → Gateway → Portal → Database
                    ↓
                EventBus → Redis → Subscribers
```

1. User creates article via Gateway
2. Portal saves article to PostgreSQL
3. Portal publishes `portal.knowledge.article_created` event
4. EventBus stores event in PostgreSQL
5. EventBus broadcasts to Redis channels
6. Subscribers receive real-time notification

### Example 2: User Deploys Scenario

```
User → Gateway → Portal → Validation Module
                    ↓
                EventBus → Exercise Creation Workflow
```

1. User deploys scenario via Gateway
2. Portal calls Validation Module to create exercise
3. Portal publishes `portal.scenarios.deployed` event
4. EventBus broadcasts event
5. Other services (e.g., Notification Service) react to event

---

## 🛠️ Development Workflow

### Local Development

```bash
# Terminal 1: Database
docker-compose -f docker-compose.platform.yml up postgres redis

# Terminal 2: EventBus
cd /Users/MD/ISO-22301—копия/services/SERVICES/PLATFORM/eventbus
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3: Clients Service
cd /Users/MD/ISO-22301—копия/services/SERVICES/COMMUNITY/clients
uvicorn main:app --host 0.0.0.0 --port 8030 --reload

# Terminal 4: Portal Service
cd /Users/MD/ISO-22301—копия/services/SERVICES/COMMUNITY/portal
uvicorn main:app --host 0.0.0.0 --port 8031 --reload

# Terminal 5: Gateway
cd /Users/MD/ISO-22301—копия/services/SERVICES/PLATFORM/gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Deployment

```bash
cd /Users/MD/ISO-22301—копия/services/SERVICES/PLATFORM

# Build and start all services
docker-compose -f docker-compose.platform.yml up -d --build

# View logs
docker-compose -f docker-compose.platform.yml logs -f

# Scale Portal service
docker-compose -f docker-compose.platform.yml up -d --scale portal=3
```

---

## 🐛 Troubleshooting

### Issue: Portal not accessible through Gateway

```bash
# Check Portal is running
curl http://localhost:8031/health

# Check Gateway service registry
docker exec bcm-gateway cat /app/main.py | grep -A 5 '"portal"'

# Check Gateway logs
docker logs bcm-gateway
```

### Issue: Events not publishing

```bash
# Check EventBus is running
curl http://localhost:8001/health

# Check Portal can reach EventBus
docker exec bcm-portal curl http://eventbus:8001/health

# Check EventBus logs
docker logs bcm-eventbus
```

### Issue: Database connection errors

```bash
# Check PostgreSQL is running
docker exec bcm-postgres pg_isready -U bcm_user

# Verify portal schema exists
docker exec bcm-postgres psql -U bcm_user -d bcm_platform -c "\dn"

# Check portal tables
docker exec bcm-postgres psql -U bcm_user -d bcm_platform -c "\dt portal.*"
```

---

## 📚 Next Steps

1. ✅ Portal Service implemented (Knowledge Hub + Forum + Scenarios)
2. ✅ Gateway integration complete
3. ✅ EventBus integration complete
4. ✅ Docker orchestration configured
5. → **Apply database migrations** (see DEPLOYMENT.md)
6. → **Configure frontend** to use Gateway endpoints
7. → **Setup monitoring** (Prometheus, Grafana)
8. → **Configure CI/CD** pipeline

---

## 📖 Related Documentation

- **Portal Service:** [README.md](./README.md)
- **Deployment Guide:** [DEPLOYMENT.md](./DEPLOYMENT.md)
- **API Documentation:** http://localhost:8031/docs
- **Gateway Documentation:** `/PLATFORM/gateway/README.md`
- **EventBus Documentation:** `/PLATFORM/eventbus/README.md`

---

**Integration Status:** ✅ Complete
**Last Updated:** 2025-10-02
**Maintained By:** BCM Platform Team
