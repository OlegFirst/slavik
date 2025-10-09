# Infrastructure Layer

**Layer Type:** Foundation Infrastructure Services
**Purpose:** Core platform infrastructure and cross-cutting concerns
**Status:** Production Ready
**Version:** 1.0.0
**Last Updated:** 2025-10-09

---

## Overview

The Infrastructure Layer provides foundational services that enable the AI-Platform-ISO to operate reliably, securely, and at scale. This layer handles cross-cutting concerns including event-driven messaging, data persistence, security, observability, and service orchestration.

**Key Characteristics:**
- Microservices architecture with independent scaling
- Event-driven communication for loose coupling
- Multi-tenant security and data isolation
- Production-grade monitoring and observability
- Cloud-agnostic deployment capabilities

---

## Architecture

### Infrastructure Layer Components

```
infrastructure/
├── eventbus/                    # Event-driven messaging system
├── database/                    # PostgreSQL and Redis management
├── security/                    # Authentication, authorization, encryption
├── gateway/                     # API Gateway and intelligent routing
├── observability/               # Monitoring, logging, metrics
├── runtime/                     # Container orchestration
├── deployment/                  # Deployment automation
├── tools/                       # Development and operations tools
└── AI-office-infrastructure/    # AI-powered infrastructure automation
```

### Communication Patterns

The infrastructure layer supports multiple communication patterns:

**Event-Driven (Asynchronous):**
- EventBus with Redis Streams and in-memory fallback
- Publish-subscribe for loose coupling
- Event sourcing for audit trails
- Dead letter queues for error handling

**Request-Response (Synchronous):**
- HTTP/REST via API Gateway
- Service-to-service direct calls
- Request timeout and circuit breakers
- Retry policies with exponential backoff

**Shared Libraries:**
- Common utilities in `/shared/` directory
- Database access patterns
- Authentication helpers
- Caching abstractions

---

## Core Infrastructure Components

### 1. EventBus

**Purpose:** Event-driven messaging and service integration

**Features:**
- Multiple backend support (Memory, Redis Streams)
- Topic-based publish-subscribe
- Event replay and audit trail
- Guaranteed delivery with acknowledgments
- Dead letter queue for failed events

**Architecture:**
```
EventBus
├── Publishers (Platform Services, Intelligent Core)
├── Event Router (Topic-based routing)
├── Subscribers (Event handlers)
└── Backend (Redis Streams / In-Memory)
```

**Usage:**
```python
from infrastructure.eventbus import EventBus

# Publish event
eventbus.publish(
    topic="bia.analysis.completed",
    event={
        "analysis_id": "bia-123",
        "organization_id": "org-456",
        "status": "completed"
    }
)

# Subscribe to events
@eventbus.subscribe("bia.analysis.completed")
async def handle_bia_completion(event):
    # Process event
    pass
```

**Documentation:** [/infrastructure/eventbus/README.md](/infrastructure/eventbus/README.md)

### 2. Database

**Purpose:** Data persistence and caching

**Components:**

**PostgreSQL (Primary Database):**
- Multi-tenant data isolation
- Full-text search capabilities
- JSON/JSONB support for flexible schemas
- Connection pooling (SQLAlchemy)
- Migration management (Alembic)

**Redis (Caching and Real-Time):**
- Session storage
- API response caching
- Real-time data structures (lists, sets, sorted sets)
- Pub/Sub for real-time notifications
- Distributed locks

**Supabase Integration:**
- Managed PostgreSQL with automatic backups
- Real-time subscriptions
- Row-level security (RLS)
- Built-in authentication

**Usage:**
```python
from infrastructure.database import DatabaseManager, CacheManager

# Database operations
db = DatabaseManager()
organization = await db.get_organization(org_id="org-123")

# Caching
cache = CacheManager()
await cache.set("bia:org-123", bia_data, ttl=3600)
cached_data = await cache.get("bia:org-123")
```

**Documentation:** [/infrastructure/database/README.md](/infrastructure/database/README.md)

### 3. Security

**Purpose:** Authentication, authorization, and data protection

**Components:**

**Authentication:**
- JWT token-based authentication
- Token refresh mechanism
- Multi-factor authentication (MFA)
- Session management

**Authorization:**
- Role-based access control (RBAC)
- Resource-level permissions
- API key management
- OAuth2 integration

**API Gateway:**
- Request authentication and validation
- Rate limiting and throttling
- Request/response transformation
- Audit logging
- Load balancing across service instances

**Data Protection:**
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Secrets management integration (Vault, AWS Secrets Manager)
- Key rotation policies

**Architecture:**
```
API Gateway
├── Authentication Middleware (JWT validation)
├── Authorization Middleware (RBAC)
├── Rate Limiting (per user/organization)
├── Request Routing (intelligent load balancing)
├── Audit Logging (all API calls)
└── Response Caching (GET requests)
```

**Documentation:** [/infrastructure/security/README.md](/infrastructure/security/README.md)

### 4. Observability

**Purpose:** Monitoring, logging, and distributed tracing

**Components:**

**Prometheus (Metrics):**
- Service health metrics
- Application performance metrics
- Business metrics (BIA completion rate, etc.)
- Custom metric collection
- Alert rules and notifications

**Grafana (Visualization):**
- Real-time dashboards
- Service health overview
- Performance analytics
- Custom dashboard creation
- Alert visualization

**Logging:**
- Structured JSON logging
- Centralized log aggregation
- Log correlation with trace IDs
- Log retention and rotation
- Search and analytics

**Distributed Tracing:**
- Request flow visualization
- Performance bottleneck identification
- Service dependency mapping
- Error tracking and debugging

**Key Metrics:**
```
Platform Metrics:
- Request rate (requests/second)
- Error rate (errors/second)
- Response time (p50, p95, p99)
- Service availability (uptime %)

Business Metrics:
- BIA analyses completed
- Risk assessments performed
- Compliance checks passed
- User active sessions
```

**Documentation:** [/infrastructure/observability/README.md](/infrastructure/observability/README.md)

### 5. Runtime

**Purpose:** Container orchestration and service lifecycle management

**Components:**

**Docker:**
- Service containerization
- Multi-stage builds for optimization
- Health checks and restart policies
- Resource limits and reservations

**Docker Compose:**
- Local development environment
- Service dependency management
- Network configuration
- Volume management

**Kubernetes (Production):**
- Service deployment and scaling
- Rolling updates and rollbacks
- Service discovery and load balancing
- ConfigMaps and Secrets management
- Ingress and traffic routing

**Documentation:** [/infrastructure/runtime/README.md](/infrastructure/runtime/README.md)

---

## Infrastructure Services Catalog

### Production-Ready Services

| Service | Purpose | Status | Port | Dependencies |
|---------|---------|--------|------|--------------|
| EventBus | Event-driven messaging | Operational | N/A | Redis (optional) |
| Database Manager | PostgreSQL access | Operational | 5432 | PostgreSQL |
| Redis Manager | Caching and real-time | Operational | 6379 | Redis |
| API Gateway | Request routing and security | Operational | 8000 | All services |
| Service Discovery | Health monitoring | Operational | 8500 | All services |
| Prometheus | Metrics collection | Operational | 9090 | All services |
| Grafana | Metrics visualization | Operational | 3001 | Prometheus |

### Configuration-Required Services

| Service | Purpose | Status | Configuration Needed |
|---------|---------|--------|---------------------|
| Notification Service | Email, Slack, SMS notifications | Ready | SMTP, Slack webhook, Twilio API |
| WebSocket Server | Real-time updates | Ready | Redis Pub/Sub |
| Message Queue | Async task processing | Ready | RabbitMQ or Redis |
| Secrets Manager | Secure secrets storage | Ready | Vault or AWS Secrets Manager |

### Planned Services

| Service | Purpose | Priority | Estimated Effort |
|---------|---------|----------|-----------------|
| Distributed Tracing | Request flow visualization | Medium | 2-3 weeks |
| Centralized Logging | Log aggregation and search | Medium | 2-3 weeks |
| Kubernetes Manifests | K8s deployment | High | 1-2 weeks |

---

## Integration Patterns

### Service-to-Infrastructure Integration

**1. Database Access:**
```python
from infrastructure.database import get_db_session

async def get_organization(org_id: str):
    async with get_db_session() as session:
        result = await session.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()
```

**2. Event Publishing:**
```python
from infrastructure.eventbus import get_eventbus

async def publish_bia_completed(analysis_id: str):
    eventbus = get_eventbus()
    await eventbus.publish(
        topic="bia.analysis.completed",
        event={
            "analysis_id": analysis_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

**3. Caching:**
```python
from infrastructure.database.cache import get_cache

async def get_cached_bia(org_id: str):
    cache = get_cache()
    cached = await cache.get(f"bia:{org_id}")
    if cached:
        return cached

    # Fetch from database
    bia = await fetch_bia_from_db(org_id)

    # Cache for 1 hour
    await cache.set(f"bia:{org_id}", bia, ttl=3600)
    return bia
```

**4. Metrics Collection:**
```python
from infrastructure.observability import metrics

# Counter
metrics.increment("bia.analysis.completed")

# Gauge
metrics.gauge("bia.active_analyses", 42)

# Histogram
metrics.histogram("bia.analysis.duration", 125.5)
```

---

## Deployment

### Local Development

```bash
# Start infrastructure services
cd infrastructure
docker-compose up -d

# Verify services
docker-compose ps

# Check logs
docker-compose logs -f eventbus
```

### Production Deployment

**Docker Compose:**
```bash
# Production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale api-gateway=3
```

**Kubernetes:**
```bash
# Apply infrastructure manifests
kubectl apply -f infrastructure/k8s/namespace.yaml
kubectl apply -f infrastructure/k8s/configmaps/
kubectl apply -f infrastructure/k8s/secrets/
kubectl apply -f infrastructure/k8s/deployments/
kubectl apply -f infrastructure/k8s/services/

# Verify deployment
kubectl get pods -n ai-platform-infrastructure
kubectl get svc -n ai-platform-infrastructure
```

See [Deployment Guide](/docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## Configuration

### Environment Variables

**Database Configuration:**
```bash
DATABASE_URL=postgresql://user:password@host:5432/database
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

**EventBus Configuration:**
```bash
EVENTBUS_BACKEND=redis  # Options: memory, redis
EVENTBUS_REDIS_URL=redis://localhost:6379/0
```

**Security Configuration:**
```bash
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**Monitoring Configuration:**
```bash
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=admin
```

### Configuration Files

Configuration files are located in:
- `/infrastructure/config/` - Service configurations
- `/infrastructure/k8s/configmaps/` - Kubernetes ConfigMaps
- `/infrastructure/docker/` - Docker and Docker Compose files

---

## Performance and Scalability

### Performance Characteristics

**EventBus:**
- Throughput: 10,000+ events/second (Redis backend)
- Latency: < 10ms p99
- Supports horizontal scaling

**Database:**
- Connection pooling: 20 connections per service
- Query timeout: 30 seconds
- Read replicas for read-heavy workloads

**Caching:**
- Redis cluster for high availability
- Cache hit ratio target: > 80%
- TTL-based expiration

**API Gateway:**
- Request routing: < 5ms overhead
- Rate limiting: 1000 requests/minute per user
- Concurrent connections: 10,000+

### Scalability Strategy

**Horizontal Scaling:**
- Stateless services scale independently
- Load balancing across instances
- Auto-scaling based on CPU/memory

**Database Scaling:**
- Read replicas for read operations
- Connection pooling to limit connections
- Sharding for multi-tenant isolation

**Caching Strategy:**
- Redis cluster for distributed caching
- Cache warming on deployment
- Invalidation on data updates

---

## Monitoring and Health Checks

### Health Check Endpoints

All infrastructure services expose health endpoints:

```
GET /health
Response: {"status": "healthy", "timestamp": "2025-10-09T12:00:00Z"}

GET /ready
Response: {"status": "ready", "dependencies": {"database": "ok", "redis": "ok"}}
```

### Prometheus Metrics

Key metrics exported by infrastructure services:

```
# Request metrics
http_requests_total{service="api-gateway", method="GET", status="200"}
http_request_duration_seconds{service="api-gateway", method="GET"}

# Service health
up{service="eventbus"} 1
service_health{service="database", status="healthy"} 1

# Resource usage
process_cpu_usage{service="api-gateway"} 0.45
process_memory_usage_bytes{service="api-gateway"} 536870912
```

### Grafana Dashboards

Pre-built dashboards:
- Infrastructure Overview (all services)
- API Gateway Performance
- Database Performance
- EventBus Metrics
- Resource Utilization

---

## Security

### Security Controls

**Network Security:**
- Services communicate within private network
- API Gateway as single public entry point
- TLS encryption for all external traffic
- mTLS for service-to-service communication (optional)

**Authentication:**
- JWT token validation on all API requests
- Token rotation and expiration
- API key management for service accounts

**Authorization:**
- Role-based access control (RBAC)
- Resource-level permissions
- Audit logging of all access attempts

**Data Protection:**
- Encryption at rest (database, backups)
- Encryption in transit (TLS 1.3)
- Secrets management (Vault, AWS Secrets Manager)
- Regular security scans (Trivy, Snyk)

---

## Troubleshooting

### Common Issues

**EventBus Not Publishing:**
```bash
# Check Redis connectivity
redis-cli ping

# Check EventBus logs
docker-compose logs eventbus

# Verify EventBus health
curl http://localhost:8000/health/eventbus
```

**Database Connection Errors:**
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# Check connection pool
docker-compose logs database-manager

# Verify connection limits
SELECT count(*) FROM pg_stat_activity;
```

**High Memory Usage:**
```bash
# Check service resource usage
docker stats

# Identify memory leaks
docker-compose exec api-gateway python -m memory_profiler script.py

# Adjust resource limits in docker-compose.yml
```

---

## Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/AI-Platform-ISO.git
cd AI-Platform-ISO

# Start infrastructure
cd infrastructure
docker-compose up -d

# Verify services
docker-compose ps
curl http://localhost:8000/health
```

### Testing Infrastructure

```bash
# Run infrastructure tests
pytest infrastructure/tests/

# Integration tests
pytest infrastructure/tests/integration/

# Load tests
locust -f infrastructure/tests/load/locustfile.py
```

---

## Contributing

### Adding New Infrastructure Service

1. Create service directory in `/infrastructure/`
2. Implement service with health check endpoint
3. Add Docker configuration
4. Update docker-compose.yml
5. Add monitoring and metrics
6. Document in this README
7. Add tests

### Code Standards

- Follow Python PEP 8 style guide
- Type hints for all functions
- Comprehensive error handling
- Logging at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Unit tests with > 80% coverage

---

## Documentation

### Infrastructure Documentation

- [INDEX.md](./INDEX.md) - Complete infrastructure index
- [TECHNICAL_GUIDE.md](./TECHNICAL_GUIDE.md) - Developer guide
- [DEPLOYMENT_ROADMAP.md](./DEPLOYMENT_ROADMAP.md) - Deployment plans

### Component Documentation

Each infrastructure component has its own README:
- [EventBus README](./eventbus/README.md)
- [Database README](./database/README.md)
- [Security README](./security/README.md)
- [Gateway README](./gateway/README.md)
- [Observability README](./observability/README.md)

---

## Support

### Resources

- **Platform Documentation:** [/docs/README.md](/docs/README.md)
- **Getting Started:** [/docs/GETTING_STARTED.md](/docs/GETTING_STARTED.md)
- **Deployment Guide:** [/docs/DEPLOYMENT_GUIDE.md](/docs/DEPLOYMENT_GUIDE.md)

### Contact

- **Issues:** GitHub Issues
- **DevOps Team:** devops@ai-platform-iso.com
- **Documentation:** documentation@ai-platform-iso.com

---

## Document Information

**Document Version:** 1.0.0
**Last Updated:** 2025-10-09
**Next Review:** 2025-11-09
**Maintained By:** Infrastructure Team
**Status:** Production Ready

---

The Infrastructure Layer is the foundation of the AI-Platform-ISO, providing reliable, secure, and scalable services that enable the intelligent core and platform services to deliver business value. For questions or contributions, contact the infrastructure team.
