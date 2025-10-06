# Infrastructure Implementation Tactics

**Date:** 2025-10-04
**Based on:** Full infrastructure audit
**Target:** Production-ready in 6 weeks

---

## 🎯 Strategic Approach

### Philosophy

**"Progressive Consolidation"** - не писать всё с нуля, а:

1. **Leverage what works** - используем готовые сервисы (EventBus, Database, Auth)
2. **Consolidate stubs** - объединяем разрозненные заглушки в unified patterns
3. **Pattern libraries** - создаём переиспользуемые паттерны
4. **Minimal viable services** - фокус на essential функциональности

### NOT Big Rewrite

❌ **Плохо:** "Перепишем всё с нуля за 2 недели"
✅ **Хорошо:** "Возьмём EventBus как эталон, остальное подтянем до его уровня"

---

## 📊 Current State Analysis

### What We Have (Ready ✅)

| Service | Status | LOC | Quality |
|---------|--------|-----|---------|
| EventBus | ✅ Production | 1,630 | 10/10 |
| Database | ✅ Production | 8,500 | 10/10 |
| Auth/Security | ✅ Production | 1,200 | 10/10 |
| Observability | ✅ Production | 800 | 10/10 |

**Total ready:** ~12,000 LOC, 47% of infrastructure

### What We Need (Gaps 🔴)

| Category | Current | Target | Gap |
|----------|---------|--------|-----|
| Reliability | 0 LOC | 500 LOC | 100% |
| Performance | 0 LOC | 400 LOC | 100% |
| Scalability | 0 LOC | 300 LOC | 100% |
| Kubernetes | 0 files | 15 files | 100% |
| Tests | 30% | 70% | 40% |
| Dockerfiles | 35% | 100% | 65% |

**Total needed:** ~2,000 LOC + configs

---

## 🏗️ Implementation Strategy

### Phase 1: Foundation Patterns (Week 1)

**Goal:** Create reusable pattern library

#### 1.1 Reliability Patterns Library

**Location:** `/infrastructure/reliability/patterns/`

**Create:**
```python
# circuit_breaker.py (~150 LOC)
class CircuitBreaker:
    """Generic circuit breaker for any service"""

# retry.py (~100 LOC)
class RetryPolicy:
    """Configurable retry with exponential backoff"""

# timeout.py (~80 LOC)
class TimeoutWrapper:
    """Timeout wrapper for async operations"""

# health_check.py (~120 LOC)
class HealthChecker:
    """Universal health check pattern"""
```

**Why this first:**
- All services need reliability
- Can be used immediately in existing services
- EventBus already has retry - extract and generalize

**Estimated time:** 2 days
**Impact:** High (affects all services)

#### 1.2 Performance Patterns Library

**Location:** `/infrastructure/performance/patterns/`

**Create:**
```python
# cache.py (~200 LOC)
class CacheDecorator:
    """Generic caching decorator using Redis"""

# rate_limiter.py (~150 LOC)
class RateLimiter:
    """Rate limiting for APIs and services"""

# connection_pool.py (~100 LOC)
class ConnectionPool:
    """Database connection pooling"""
```

**Why:**
- Database already has connection management - extract pattern
- Redis ready - just wrap it nicely

**Estimated time:** 1.5 days
**Impact:** Medium

#### 1.3 Scalability Patterns Library

**Location:** `/infrastructure/scalability/patterns/`

**Create:**
```python
# load_balancer.py (~100 LOC)
class ServiceLoadBalancer:
    """Client-side load balancing"""

# service_discovery.py (~150 LOC)
class ServiceRegistry:
    """Simple service discovery using Redis"""

# horizontal_scaling.py (~80 LOC)
class ScalingPolicy:
    """Metrics for auto-scaling decisions"""
```

**Why:**
- EventBus consumer groups = load balancing - generalize
- Redis = service registry backend

**Estimated time:** 1.5 days
**Impact:** Medium

**Total Week 1:** 5 days, ~1,200 LOC pattern libraries

---

### Phase 2: Essential Infrastructure (Week 2)

**Goal:** Minimum viable production infrastructure

#### 2.1 Kubernetes Manifests

**Location:** `/infrastructure/kubernetes/base/`

**Create:**
```yaml
# namespace.yaml
# configmap.yaml
# secrets.yaml (templated)
# postgresql.yaml (external service)
# redis.yaml (external service)
# eventbus-deployment.yaml
# api-gateway-deployment.yaml
# services.yaml
```

**Why minimal:**
- Start with just EventBus + API Gateway
- Add other services incrementally
- External PostgreSQL/Redis (Supabase/Upstash)

**Estimated time:** 2 days
**Impact:** Critical (enables deployment)

#### 2.2 Docker Compose for Local Dev

**Location:** `/docker-compose.dev.yml`

**Create:**
```yaml
services:
  # Local Redis (fallback)
  # Local PostgreSQL (fallback)
  # EventBus
  # API Gateway
  # BIA Service (first BCM service)
```

**Why:**
- Developers need local environment
- Can't always use cloud services
- Testing without network

**Estimated time:** 1 day
**Impact:** High (developer experience)

#### 2.3 Dockerfiles (Missing Services)

**Create for:**
- `/infrastructure/notification-service/Dockerfile`
- `/infrastructure/monitoring/Dockerfile`
- `/platform-services/bia-service/Dockerfile`
- `/platform-services/risk-service/Dockerfile`

**Template:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

**Estimated time:** 1 day
**Impact:** Medium

#### 2.4 Monitoring Stack Integration

**Goal:** Consolidate existing monitoring pieces

**Action:**
```bash
# Use existing /infrastructure/monitoring/ files
# Add Prometheus exporters to services
# Create Grafana dashboard configs
```

**Estimated time:** 1 day
**Impact:** Medium

**Total Week 2:** 5 days, essential deployment infrastructure

---

### Phase 3: Service Integration (Week 3-4)

**Goal:** Apply patterns to existing services

#### 3.1 Retrofit Pattern Libraries

**Services to update:**

1. **BIA Service** (Week 3)
   - Add CircuitBreaker to external calls
   - Add CacheDecorator to queries
   - Add HealthChecker
   - Write integration tests

2. **Risk Service** (Week 3)
   - Same patterns as BIA
   - EventBus integration

3. **Workflow Intelligence** (Week 4)
   - Add RetryPolicy for AI calls
   - Add RateLimiter for API endpoints
   - EventBus subscriptions

4. **API Gateway** (Week 4)
   - Add RateLimiter
   - Add ServiceLoadBalancer
   - Add request tracing

**Per service:** 1 day
**Total:** 4 services = 4 days

#### 3.2 Write Tests

**Target coverage:** 70%

**Priority tests:**
1. Pattern libraries (100% coverage) - 1 day
2. EventBus integration - 0.5 day
3. Critical path flows - 1 day
4. API endpoints - 0.5 day

**Total:** 3 days

**Total Week 3-4:** 7 days integration + testing

---

### Phase 4: Production Hardening (Week 5-6)

**Goal:** Production-ready checklist

#### 4.1 Complete Documentation

**Create for each service:**
- README.md (usage, config, deployment)
- ARCHITECTURE.md (design decisions)
- API.md (if applicable)

**Template existing:** EventBus docs as standard

**Estimated time:** 4 days (batch documentation sprint)

#### 4.2 Security Hardening

**Tasks:**
- Review all RLS policies (database)
- Add API authentication to all endpoints
- Secrets management (Kubernetes secrets)
- Network policies (Kubernetes)

**Estimated time:** 2 days

#### 4.3 Performance Testing

**Tasks:**
- Load test EventBus (target: 1K events/sec)
- Load test API Gateway (target: 100 req/sec)
- Database query optimization
- Redis cache hit rate analysis

**Estimated time:** 2 days

#### 4.4 Deployment Dry Run

**Tasks:**
- Deploy to staging environment
- Run smoke tests
- Verify monitoring/alerting
- Create runbook

**Estimated time:** 2 days

**Total Week 5-6:** 10 days production prep

---

## 📅 Detailed Timeline

### Week 1: Pattern Libraries
- **Day 1-2:** Reliability patterns (CircuitBreaker, Retry, Timeout, HealthCheck)
- **Day 3:** Performance patterns (Cache, RateLimiter, ConnectionPool)
- **Day 4-5:** Scalability patterns (LoadBalancer, ServiceDiscovery, Scaling)

### Week 2: Essential Infrastructure
- **Day 1-2:** Kubernetes manifests (base deployment)
- **Day 3:** Docker Compose for local dev
- **Day 4:** Dockerfiles for missing services
- **Day 5:** Monitoring integration

### Week 3: Service Integration Part 1
- **Day 1:** BIA Service - add patterns
- **Day 2:** Risk Service - add patterns
- **Day 3:** Pattern library tests
- **Day 4-5:** Integration testing

### Week 4: Service Integration Part 2
- **Day 1:** Workflow Intelligence - add patterns
- **Day 2:** API Gateway - add patterns
- **Day 3-4:** End-to-end testing
- **Day 5:** Bug fixes

### Week 5: Production Hardening
- **Day 1-3:** Documentation sprint (all services)
- **Day 4-5:** Security hardening

### Week 6: Testing & Deployment
- **Day 1-2:** Performance testing
- **Day 3-4:** Staging deployment
- **Day 5:** Production readiness review

---

## 🎯 Tactics for Each Component

### Reliability (0% → 100%)

**DON'T:** Write custom retry logic in every service
**DO:** Create `shared.reliability` package, import everywhere

**Implementation:**
```python
# In BIA Service
from shared.reliability import CircuitBreaker, with_retry

@with_retry(max_attempts=3, backoff=exponential)
async def call_ai_service():
    # Automatically retries on failure
    pass

circuit_breaker = CircuitBreaker(failure_threshold=5)

@circuit_breaker.protect
async def call_external_api():
    # Stops calling if too many failures
    pass
```

**Files to create:**
```
/shared/reliability/
├── __init__.py
├── circuit_breaker.py
├── retry.py
├── timeout.py
├── health_check.py
└── tests/
```

**Estimated:** 400 LOC (2 days)

---

### Performance (0% → 100%)

**DON'T:** Implement caching separately in each service
**DO:** Unified cache decorator using existing Redis

**Implementation:**
```python
from shared.performance import cache

@cache(ttl=300)  # Cache for 5 minutes
async def get_process(process_id: int):
    return await db.query(...)
```

**Files to create:**
```
/shared/performance/
├── __init__.py
├── cache.py (decorator + Redis wrapper)
├── rate_limiter.py
├── profiler.py (timing decorator)
└── tests/
```

**Estimated:** 350 LOC (1.5 days)

---

### Scalability (0% → 100%)

**DON'T:** Hard-code service URLs
**DO:** Service discovery via Redis

**Implementation:**
```python
from shared.scalability import ServiceRegistry

registry = ServiceRegistry(redis_client)

# Service registers itself
await registry.register('bia-service', 'http://10.0.1.5:8000')

# Client discovers service
url = await registry.discover('bia-service')
```

**Files to create:**
```
/shared/scalability/
├── __init__.py
├── service_registry.py
├── load_balancer.py
├── metrics.py (for autoscaling)
└── tests/
```

**Estimated:** 300 LOC (1.5 days)

---

### Kubernetes (0% → 100%)

**DON'T:** Complex Helm charts from day 1
**DO:** Simple manifests, iterate

**Start with:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eventbus
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: eventbus
        image: bcm-platform/eventbus:latest
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
```

**Files to create:**
```
/infrastructure/kubernetes/
├── namespace.yaml
├── configmap.yaml
├── secrets.yaml.example
├── deployments/
│   ├── eventbus.yaml
│   ├── api-gateway.yaml
│   └── bia-service.yaml
├── services/
│   └── services.yaml
└── README.md (deployment instructions)
```

**Estimated:** 15 files, 500 LOC (2 days)

---

### Tests (30% → 70%)

**Strategy:** Focus on critical paths

**Priority 1: Pattern libraries (100% coverage)**
```python
# test_circuit_breaker.py
async def test_circuit_opens_after_failures():
    cb = CircuitBreaker(failure_threshold=3)
    # Trigger 3 failures
    # Verify circuit is open
    # Verify calls are rejected
```

**Priority 2: Integration tests (EventBus)**
```python
async def test_event_flow_end_to_end():
    # Publish event in BIA service
    # Verify received in Workflow Intelligence
    # Verify database updated
```

**Priority 3: API endpoint tests**
```python
async def test_create_process_endpoint():
    response = await client.post('/api/processes', json={...})
    assert response.status_code == 201
```

**Estimated:** 1,000 LOC tests (3 days)

---

## 🚫 What NOT to Build (Yet)

### Defer to Later

**Intelligent Gateway** (stub, 30 LOC)
- **Why defer:** Complex AI routing not needed for MVP
- **When:** After basic services stable (Week 8+)
- **Alternative:** Use simple API Gateway for now

**Process Mining Service** (stub, 25 LOC)
- **Why defer:** Nice-to-have, not critical path
- **When:** After core BCM services working (Week 10+)

**Message Queue** (separate from EventBus)
- **Why defer:** EventBus handles events, RabbitMQ overkill for MVP
- **When:** If EventBus can't handle load (unlikely)

**Advanced Kubernetes Features**
- **Defer:** Autoscaling, service mesh, advanced networking
- **Start with:** Basic deployments, services, configmaps
- **Add later:** As we learn what we need

---

## 🔧 Consolidation Opportunities

### 1. Merge Monitoring + Observability

**Current:**
- `/infrastructure/monitoring/` (Prometheus, Grafana)
- `/infrastructure/observability/` (OpenTelemetry, Jaeger)

**Tactic:**
```bash
# Keep observability/ (more complete)
# Move Prometheus configs to observability/prometheus/
# Move Grafana dashboards to observability/grafana/
# Delete monitoring/ (avoid duplication)
```

**Result:** One unified `/infrastructure/observability/` with all monitoring

---

### 2. Shared Patterns Library

**Current:** Patterns scattered across services

**Tactic:**
```bash
# Create /shared/patterns/ or /shared/infrastructure/
/shared/patterns/
├── reliability/
├── performance/
├── scalability/
└── __init__.py (re-exports all)
```

**All services import:**
```python
from shared.patterns import CircuitBreaker, cache, ServiceRegistry
```

---

### 3. Unified Configuration

**Current:** Each service has own config

**Tactic:**
```python
# /shared/config.py
class InfrastructureConfig:
    DATABASE_URL: str
    REDIS_URL: str
    EVENTBUS_BACKEND: str

    @classmethod
    def from_env(cls):
        return cls(
            DATABASE_URL=os.getenv('DATABASE_URL'),
            ...
        )

# In services
from shared.config import InfrastructureConfig
config = InfrastructureConfig.from_env()
```

---

## 📋 Checklists

### Week 1 Checklist (Pattern Libraries)

- [ ] Create `/shared/patterns/` directory
- [ ] Implement `CircuitBreaker` class
- [ ] Implement `RetryPolicy` class
- [ ] Implement `TimeoutWrapper` class
- [ ] Implement `HealthChecker` class
- [ ] Implement `CacheDecorator` class
- [ ] Implement `RateLimiter` class
- [ ] Implement `ConnectionPool` class (extract from database)
- [ ] Implement `ServiceRegistry` class
- [ ] Implement `LoadBalancer` class
- [ ] Write tests for all patterns (100% coverage)
- [ ] Write README for patterns package
- [ ] Create usage examples

### Week 2 Checklist (Infrastructure)

- [ ] Create Kubernetes namespace manifest
- [ ] Create configmap template
- [ ] Create secrets template
- [ ] Create EventBus deployment
- [ ] Create API Gateway deployment
- [ ] Create service definitions
- [ ] Create ingress rules
- [ ] Create `docker-compose.dev.yml`
- [ ] Test local Docker Compose setup
- [ ] Write Dockerfiles for 5 missing services
- [ ] Test all Docker builds
- [ ] Document Kubernetes deployment process
- [ ] Document Docker Compose usage

### Week 3 Checklist (Integration Part 1)

- [ ] BIA Service: Add CircuitBreaker to AI calls
- [ ] BIA Service: Add cache to database queries
- [ ] BIA Service: Add health check endpoint
- [ ] BIA Service: Write integration tests
- [ ] Risk Service: Same pattern integration
- [ ] Risk Service: EventBus integration
- [ ] Risk Service: Integration tests
- [ ] Pattern library integration tests
- [ ] Fix any integration bugs

### Week 4 Checklist (Integration Part 2)

- [ ] Workflow Intelligence: Add retry to AI calls
- [ ] Workflow Intelligence: Add rate limiting
- [ ] Workflow Intelligence: EventBus subscriptions
- [ ] Workflow Intelligence: Tests
- [ ] API Gateway: Add rate limiting
- [ ] API Gateway: Add load balancing
- [ ] API Gateway: Add request tracing
- [ ] End-to-end smoke tests
- [ ] Performance baseline measurements

### Week 5 Checklist (Documentation)

- [ ] Document all pattern libraries
- [ ] Document BIA Service
- [ ] Document Risk Service
- [ ] Document Workflow Intelligence
- [ ] Document API Gateway
- [ ] Document EventBus (already done ✅)
- [ ] Document Database layer (already done ✅)
- [ ] Document deployment process
- [ ] Create architecture diagrams
- [ ] Create API documentation

### Week 6 Checklist (Production Prep)

- [ ] Security review (RLS policies)
- [ ] Security review (API authentication)
- [ ] Secrets management setup
- [ ] Network policies
- [ ] Load test EventBus (1K events/sec)
- [ ] Load test API Gateway (100 req/sec)
- [ ] Database query optimization
- [ ] Deploy to staging
- [ ] Smoke tests in staging
- [ ] Monitoring/alerting verification
- [ ] Create runbook
- [ ] Production readiness review
- [ ] Go/No-Go decision

---

## 🎯 Success Metrics

### Code Quality

- **Test Coverage:** 30% → 70%
- **Documentation:** 50% → 100%
- **Dockerfiles:** 35% → 100%
- **Code with patterns:** 0% → 80%

### Infrastructure Health

- **Production-ready services:** 8/17 (47%) → 17/17 (100%)
- **Empty stubs eliminated:** 0% → 100%
- **Kubernetes manifests:** 0 → 15 files
- **Health score:** 6.4/10 → 9.0/10

### Performance

- **EventBus throughput:** Test → 1,000 events/sec
- **API response time:** Measure → <100ms p95
- **Database query time:** Measure → <50ms p95
- **Cache hit rate:** N/A → >80%

### Operational

- **Deployment time:** N/A → <10 min
- **Rollback time:** N/A → <5 min
- **MTTR (Mean Time To Recovery):** N/A → <30 min
- **Monitoring coverage:** 50% → 100%

---

## 🚀 Quick Start

**Tomorrow (Day 1):**

1. Create `/shared/patterns/reliability/` directory
2. Extract retry logic from EventBus
3. Generalize into `RetryPolicy` class
4. Write tests
5. Use in BIA Service

**Estimated:** 4-6 hours → First production pattern ready!

**Day 2:**

1. Implement `CircuitBreaker`
2. Write tests
3. Integrate into BIA Service external calls

**Result:** 2 days → 2 production patterns + real usage

---

## 📞 Decision Points

### Should We Use Pattern X?

**Ask:**
1. Do >2 services need this? → Create pattern
2. Is it one-off? → Keep in service
3. Is there existing code? → Extract and generalize
4. Is it external library? → Just use library

### Should We Build or Buy?

**Build:**
- Custom business logic (BIA, Risk, Workflow)
- Platform-specific patterns (ServiceRegistry using our Redis)

**Buy/Use:**
- Standard infrastructure (PostgreSQL, Redis, Kubernetes)
- Observability (OpenTelemetry, Jaeger)
- Monitoring (Prometheus, Grafana)

### When to Consolidate?

**Consolidate when:**
- 2+ implementations of same thing exist
- Code duplication >50%
- Maintenance burden high

**Keep separate when:**
- Different use cases
- Different maturity levels
- Experimental vs production

---

## 🎓 Learning from EventBus

**EventBus = Gold Standard**

**What made it successful:**
1. ✅ Clean interface (`IEventBus`)
2. ✅ Pluggable backends
3. ✅ Comprehensive tests
4. ✅ Excellent documentation (3 docs)
5. ✅ Working examples
6. ✅ Zero vendor lock-in

**Apply to other services:**
- Same doc structure (README + QUICKSTART + ARCHITECTURE)
- Same test coverage (unit + integration)
- Same interface-first design
- Same example-driven approach

**Template:**
```
/infrastructure/{service}/
├── core/               # Interfaces + models
├── backends/           # Implementations (if applicable)
├── tests/              # 70%+ coverage
├── examples/           # Working code
├── README.md           # Full guide
├── QUICKSTART.md       # 5-min tutorial
└── ARCHITECTURE.md     # Design docs
```

---

## ⚠️ Risks & Mitigation

### Risk 1: Scope Creep

**Risk:** Try to make everything perfect
**Mitigation:** Follow "Minimum Viable" principle - 80/20 rule

### Risk 2: Over-Engineering

**Risk:** Complex patterns nobody uses
**Mitigation:** Start simple, add features based on real usage

### Risk 3: Integration Breaking

**Risk:** Pattern changes break services
**Mitigation:** Semantic versioning, deprecation warnings

### Risk 4: Timeline Slip

**Risk:** 6 weeks → 12 weeks
**Mitigation:** Weekly check-ins, cut scope if needed, defer non-critical

### Risk 5: Testing Gaps

**Risk:** Patterns work in isolation but fail integrated
**Mitigation:** Integration tests weekly, not just at end

---

## 🎯 North Star

**Vision:** Infrastructure so good, services write themselves

**Indicators:**
- New service takes <1 day to scaffold
- Common patterns are one import away
- Deployment is one command
- Monitoring is automatic
- Documentation writes itself (code → docs)

**When we're done:**
```python
# Future service creation
from shared.patterns import (
    with_retry, CircuitBreaker, cache,
    HealthChecker, ServiceRegistry
)

@with_retry
@cache(ttl=300)
async def my_business_logic():
    # Focus on business logic, infrastructure is handled
    pass
```

---

**Let's build!** 🚀
