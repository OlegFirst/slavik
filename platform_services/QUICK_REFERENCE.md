# Platform Services - Quick Reference

## Service Ports & Endpoints

| Service | Port | Base URL | Health Check | Metrics | Documentation |
|---------|------|----------|--------------|---------|---------------|
| **BIA Service** | 8012 | `/api/bia` | `/health` | `/metrics` | `/docs` |
| **Risk Service** | 8040 | `/api/v1/risk` | `/health` | `/metrics` | `/docs` |
| **Compliance Service** | 8013 | `/api/compliance` | `/health` | `/metrics` | `/docs` |
| **Planning Service** | 8014 | `/api/v1/planning` | `/health` | `/metrics` | `/docs` |
| **Plans Service** | 8015 | `/api/v1/plans` | `/health` | `/metrics` | `/docs` |
| **Response Service** | 8016 | `/api/v1/response` | `/health` | `/metrics` | `/docs` |
| **Validation Service** | 8017 | `/api/v1/validation` | `/health` | `/metrics` | `/docs` |
| **Governance Service** | 8018 | `/api/v1/governance` | `/health` | `/metrics` | `/docs` |
| **Documents Service** | 8019 | `/api/v1/documents` | `/health` | `/metrics` | `/docs` |
| **Learning Service** | 8020 | `/api/v1/learning` | `/health` | `/metrics` | `/docs` |
| **Community Service** | 8021 | `/api/v1/community` | `/health` | `/metrics` | `/docs` |
| **Living Docs** | 8022 | `/api/v1/living-docs` | `/health` | `/metrics` | `/docs` |
| **Simulation** | 8023 | `/api/v1/simulation` | `/health` | `/metrics` | `/docs` |

## ISO 22301:2019 Clause Mapping

| ISO Clause | Description | Service | Port |
|------------|-------------|---------|------|
| **4.1** | Context of organization | Governance | 8018 |
| **4.2** | Understanding needs | Governance | 8018 |
| **4.3** | BCMS scope | Governance | 8018 |
| **5.1** | Leadership | Governance | 8018 |
| **5.2** | Policy | Governance | 8018 |
| **5.3** | Roles & responsibilities | Governance | 8018 |
| **6.1** | Risk actions | Risk | 8040 |
| **6.2** | Objectives | Planning | 8014 |
| **7.1** | Resources | Governance | 8018 |
| **7.2** | Competence | Learning | 8020 |
| **7.3** | Awareness | Learning | 8020 |
| **7.4** | Communication | Community | 8021 |
| **7.5** | Documented information | Documents | 8019 |
| **8.2.2** | Business Impact Analysis | BIA | 8012 |
| **8.2.3** | Risk Assessment | Risk | 8040 |
| **8.3** | BC Strategies | Planning | 8014 |
| **8.4** | BC Procedures | Response | 8016 |
| **8.4.1** | Incident management | Response | 8016 |
| **8.5** | Exercising & Testing | Validation | 8017 |
| **9.1** | Monitoring & measurement | Validation | 8017 |
| **9.2** | Internal audit | Compliance | 8013 |
| **9.3** | Management review | Validation | 8017 |
| **10.1** | Nonconformity & CAPA | Compliance | 8013 |
| **10.2** | Continual improvement | Compliance | 8013 |

## Event Bus Topics

| Topic | Publisher | Subscribers |
|-------|-----------|-------------|
| `bcm.bia.started` | BIA (8012) | - |
| `bcm.bia.completed` | BIA (8012) | Risk, Planning, Validation |
| `bcm.bia.critical_process` | BIA (8012) | Risk, Planning |
| `bcm.risk.assessment.completed` | Risk (8040) | Planning, Compliance |
| `bcm.plan.created` | Planning (8014) | Documents, Validation |
| `bcm.plan.approved` | Planning (8014) | Validation, Response |
| `bcm.exercise.completed` | Validation (8017) | BIA, Learning, Compliance |
| `bcm.audit.completed` | Validation (8017) | Compliance, Governance |
| `bcm.gap.identified` | Compliance (8013) | Planning, Governance |
| `bcm.capa.created` | Compliance (8013) | Validation, Governance |
| `bcm.incident.activated` | Response (8016) | All |
| `bcm.incident.resolved` | Response (8016) | BIA, Learning, Compliance |

## Common Environment Variables

```bash
# Service Identity
SERVICE_NAME=<service-name>
SERVICE_PORT=<port>
SERVICE_VERSION=1.0.0
LOG_LEVEL=INFO

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/bcm_platform
DB_POOL_SIZE=20

# Cache (Redis)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# Authentication (JWT)
JWT_SECRET=your-secret-key-here

# EventBus (RabbitMQ)
EVENTBUS_ENABLED=true
EVENTBUS_URL=amqp://guest:guest@localhost:8001/

# CORS
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# AI Features
AI_ENABLED=true
```

## Database Schemas

```sql
-- Core business schemas
bia.*             -- BIA Service
risk.*            -- Risk Service
compliance.*      -- Compliance Service
planning.*        -- Planning Service
plans.*           -- Plans Service
response.*        -- Response Service
validation.*      -- Validation Service
governance.*      -- Governance Service
documents.*       -- Documents Service
learning.*        -- Learning Service
community.*       -- Community Service
simulation.*      -- Simulation Service

-- Shared infrastructure schemas
workflow.*        -- Workflow Intelligence (all services)
audit.*           -- Audit logs (all services)
auth.*            -- Authentication (shared)
```

## Service Dependencies

### Core Dependencies (All Services)
- **PostgreSQL** - Primary database
- **workflow-intelligence** - Workflow engine, audit, compliance
- **shared/auth** - JWT authentication

### Optional Dependencies
- **Redis** - Caching (recommended)
- **RabbitMQ** - Event bus (recommended)
- **AI Orchestration** - AI features (optional)

## Quick Start Commands

```bash
# Start all infrastructure
docker-compose up -d postgres redis rabbitmq

# Start specific service
cd bia-service
uvicorn main:app --host 0.0.0.0 --port 8012 --reload

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bia-service

# Stop all services
docker-compose down

# Reset database
docker-compose down -v
docker-compose up -d postgres
# Run migrations...
```

## Authentication Examples

### Get JWT Token (Dev Mode)
```bash
# Using X-Dev-User header
curl -X GET "http://localhost:8012/api/bia/processes?tenant_id=tenant-123" \
  -H "X-Dev-User: {\"sub\":\"user123\",\"tenant_id\":\"tenant-123\",\"permissions\":[\"BIA_VIEW\"]}"
```

### Production JWT
```bash
# Get token from auth service
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Use token
curl -X GET "http://localhost:8012/api/bia/processes?tenant_id=tenant-123" \
  -H "Authorization: Bearer $TOKEN"
```

## Common API Patterns

### Create Resource
```bash
POST /api/{service}/{resource}
Content-Type: application/json
Authorization: Bearer <token>

{
  "tenant_id": "tenant-123",
  "name": "Example Resource",
  ...
}
```

### List Resources with Filters
```bash
GET /api/{service}/{resources}?tenant_id=tenant-123&status=active&limit=100
Authorization: Bearer <token>
```

### Update Resource
```bash
PUT /api/{service}/{resource}/{id}?tenant_id=tenant-123
Content-Type: application/json
Authorization: Bearer <token>

{
  "field_to_update": "new_value"
}
```

### Delete Resource
```bash
DELETE /api/{service}/{resource}/{id}?tenant_id=tenant-123
Authorization: Bearer <token>
```

## Troubleshooting Quick Fixes

### Issue: Service won't start
```bash
# Check PostgreSQL
docker-compose ps postgres
docker-compose logs postgres

# Check database connection
psql postgresql://user:pass@localhost:5432/bcm_platform -c "SELECT 1"
```

### Issue: 401 Unauthorized
```bash
# Check JWT_SECRET matches across services
grep JWT_SECRET .env

# Verify token
jwt decode <token>
```

### Issue: EventBus errors
```bash
# Check RabbitMQ
docker-compose ps rabbitmq
docker-compose logs rabbitmq

# Management UI
open http://localhost:15672  # guest/guest
```

### Issue: Slow queries
```bash
# Check Redis cache
redis-cli ping

# View cache stats
curl http://localhost:8012/metrics/cache
```

## Health Check Script

```bash
#!/bin/bash
# check_services.sh

SERVICES=(
  "bia-service:8012"
  "risk-service:8040"
  "compliance-service:8013"
  "planning-service:8014"
  "plans-service:8015"
  "response-service:8016"
  "validation-service:8017"
  "governance-service:8018"
  "documents-service:8019"
  "learning-service:8020"
  "community-service:8021"
  "living-docs:8022"
  "simulation:8023"
)

for service in "${SERVICES[@]}"; do
  name=${service%:*}
  port=${service#*:}
  
  status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)
  
  if [ "$status" == "200" ]; then
    echo "✅ $name - healthy"
  else
    echo "❌ $name - unhealthy (HTTP $status)"
  fi
done
```

## Documentation Links

- **Platform Overview:** [PLATFORM_SERVICES_DOCUMENTATION.md](PLATFORM_SERVICES_DOCUMENTATION.md)
- **Integration Map:** [INTEGRATION_MAP.md](INTEGRATION_MAP.md)
- **BIA Service:** [bia-service/SERVICE_DOCUMENTATION.md](bia-service/SERVICE_DOCUMENTATION.md)
- **Risk Service:** [risk-service/SERVICE_DOCUMENTATION.md](risk-service/SERVICE_DOCUMENTATION.md)

## Support Contacts

- **Platform Team:** #platform-services (Slack)
- **On-Call:** PagerDuty rotation
- **Documentation:** Swagger UI at `http://localhost:<port>/docs`
- **Issues:** GitHub Issues
