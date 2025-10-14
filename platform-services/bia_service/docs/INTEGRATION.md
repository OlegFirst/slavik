# BIA Service - Integration Documentation

**Version**: 1.0.0
**Date**: 2025-10-09

## Table of Contents

1. [Integration Overview](#1-integration-overview)
2. [Internal Service Integrations](#2-internal-service-integrations)
3. [Infrastructure Integrations](#3-infrastructure-integrations)
4. [Event-Driven Integration](#4-event-driven-integration)
5. [AI Service Integration](#5-ai-service-integration)
6. [Database Integration](#6-database-integration)
7. [Cache Integration](#7-cache-integration)
8. [Workflow Intelligence Integration](#8-workflow-intelligence-integration)

## 1. Integration Overview

The BIA Service integrates with multiple platform components to deliver comprehensive Business Impact Analysis capabilities.

### 1.1 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BIA Service                              │
└──────┬────────┬────────┬────────┬────────┬────────┬─────────────┘
       │        │        │        │        │        │
       │        │        │        │        │        │
   ┌───▼──┐ ┌──▼───┐ ┌──▼──┐ ┌───▼───┐ ┌─▼──┐ ┌──▼─────────┐
   │ Risk │ │Compli│ │Plans│ │EventB │ │ AI │ │  Workflow  │
   │      │ │ance  │ │     │ │  us   │ │Orch│ │Intelligence│
   └──────┘ └──────┘ └─────┘ └───────┘ └────┘ └────────────┘
       │        │        │        │        │         │
       │        │        │        │        │         │
   ┌───▼────────▼────────▼────────▼────────▼─────────▼─────┐
   │              Infrastructure Layer                      │
   │  - PostgreSQL  - Redis  - RabbitMQ  - Monitoring      │
   └────────────────────────────────────────────────────────┘
```

### 1.2 Integration Patterns

| Integration Type | Pattern | Technology |
|-----------------|---------|------------|
| Synchronous API | REST | HTTP/JSON |
| Asynchronous Messaging | Event-Driven | RabbitMQ |
| Data Persistence | Repository | PostgreSQL |
| Caching | Cache-Aside | Redis |
| AI Services | REST Client | HTTP/JSON |
| Monitoring | Metrics Export | Prometheus |

## 2. Internal Service Integrations

### 2.1 Risk Service Integration

**Integration Purpose**: Link BIA processes to risk assessments

**Direction**: Bidirectional

**Integration Points:**

```python
# BIA Service subscribes to Risk events
EventBus.subscribe("risk.critical_risk_identified", handler=link_risk_to_bia)

# BIA Service publishes events consumed by Risk
EventBus.publish("bcm.bia.critical_process_identified", payload={
    "process_id": 1,
    "criticality": "critical",
    "financial_impact_24h": 1000000
})
```

**Use Cases:**
- When critical risk identified → Link to relevant BIA process
- When critical BIA process created → Trigger risk assessment
- Cross-reference RTO requirements with risk treatment plans

**Example Workflow:**

```
1. Risk Service identifies critical risk: "Payment Gateway Failure"
2. Risk Service publishes: risk.critical_risk_identified
3. BIA Service receives event
4. BIA Service searches for related processes by name/keywords
5. BIA Service links risk to "Payment Processing" BIA process
6. BIA Service updates dependency criticality if needed
```

### 2.2 Compliance Service Integration

**Integration Purpose**: Evidence BIA completion for ISO 22301 compliance

**Direction**: BIA → Compliance

**Integration Points:**

```python
# BIA completion triggers compliance evidence
EventBus.publish("bcm.bia.completed", payload={
    "process_id": 1,
    "tenant_id": "tenant_123",
    "iso_clause": "8.2.2"
})

# Compliance Service automatically creates evidence record
```

**Use Cases:**
- BIA completion generates ISO 22301 Clause 8.2.2 evidence
- Compliance assessments query BIA completion status
- Gap analysis checks for missing BIAs

### 2.3 Plans Service Integration

**Integration Purpose**: Use BIA data to generate recovery plans

**Direction**: BIA → Plans

**Integration Points:**

```python
# Plans Service queries BIA data
GET /api/bia/processes?tenant_id=X&criticality=critical

# Plans Service uses RTO/RPO to define recovery strategies
```

**Use Cases:**
- Generate recovery plans based on BIA RTO requirements
- Prioritize recovery activities by criticality
- Validate plan RTOs against BIA requirements

### 2.4 Planning Service Integration

**Integration Purpose**: BIA drives exercise planning

**Direction**: BIA → Planning

**Integration Points:**

```python
# Planning Service subscribes to BIA events
EventBus.subscribe("bcm.bia.critical_process_identified",
                  handler=schedule_exercise)
```

**Use Cases:**
- Schedule exercises for critical processes
- Test RTO/RPO achievability through exercises
- Validate recovery strategies

## 3. Infrastructure Integrations

### 3.1 API Gateway Integration

**Endpoint Exposure:**

```yaml
API Gateway Routes:
  - Path: /bia/*
    Target: http://bia-service:8012/api/bia/*
    Auth: JWT Required
    Rate Limit: 100 req/min per user
    CORS: Enabled
```

**Request Flow:**

```
Client → API Gateway (Port 8000)
       ↓ (JWT validation, rate limiting)
       → BIA Service (Port 8012)
       ↓ (process request)
       ← Response
       ← Client
```

### 3.2 Service Discovery Integration

**Registration:**

```python
# BIA Service registers with Service Discovery on startup
service_registry.register(
    service_name="bia-service",
    host="bia-service",
    port=8012,
    health_check="/health",
    metadata={
        "iso_clause": "8.2.2",
        "version": "1.0.0",
        "capabilities": ["bia", "ai-suggestions", "reporting"]
    }
)
```

**Health Checks:**

```python
# Service Discovery polls /health every 30 seconds
# If 3 consecutive failures → mark as unhealthy
```

## 4. Event-Driven Integration

### 4.1 EventBus Integration

**Connection:**

```python
# Startup
eventbus_client = EventBusClient(
    url="amqp://guest:guest@rabbitmq:5672",
    service_name="bia-service"
)
await eventbus_client.connect()
```

**Events Published by BIA Service:**

| Event Name | Trigger | Payload |
|------------|---------|---------|
| bcm.bia.started | BIA process created | {process_id, tenant_id, criticality} |
| bcm.bia.completed | BIA marked complete | {process_id, tenant_id, iso_clause} |
| bcm.bia.critical_process_identified | Critical process created | {process_id, name, financial_impact} |
| bcm.bia.updated | BIA process updated | {process_id, changes} |
| bcm.bia.deleted | BIA process deleted | {process_id, tenant_id} |

**Events Subscribed by BIA Service:**

| Event Name | Source | Handler |
|------------|--------|---------|
| governance.organization.created | Governance | auto_create_bia_template |
| risk.critical_risk_identified | Risk | link_risk_to_process |

**Example Event Publishing:**

```python
async def create_bia_process(process: BIAProcessCreate):
    # ... create process in database ...

    # Publish event
    await eventbus.publish(
        topic="bcm.bia.started",
        payload={
            "event_type": "bia_started",
            "process_id": new_process.id,
            "tenant_id": new_process.tenant_id,
            "criticality": new_process.criticality,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # If critical, publish additional event
    if new_process.criticality == "critical":
        await eventbus.publish(
            topic="bcm.bia.critical_process_identified",
            payload={
                "process_id": new_process.id,
                "name": new_process.name,
                "financial_impact_24h": process.financial_impact["24_hours"]
            }
        )
```

### 4.2 Event Handler Examples

**Handler: Auto-create BIA Template**

```python
async def auto_create_bia_template(event_data: dict):
    """
    When new organization created, auto-create BIA template processes
    """
    tenant_id = event_data["tenant_id"]
    industry = event_data.get("industry", "general")

    # Get industry-specific template processes
    templates = get_bia_templates(industry)

    # Create template processes for new tenant
    for template in templates:
        await bia_service.create_process(
            BIAProcessCreate(
                tenant_id=tenant_id,
                name=template["name"],
                description="Template - customize as needed",
                criticality=template["criticality"],
                industry=industry,
                rto_hours=template["rto_hours"],
                rpo_hours=template["rpo_hours"],
                mtpd_hours=template["mtpd_hours"]
            )
        )
```

## 5. AI Service Integration

### 5.1 AI Orchestration Service

**Connection:**

```python
ai_orchestrator_url = "http://ai-orchestration:8002"

async def suggest_rto(process: BIAProcess) -> AIRTOSuggestion:
    """Call AI Orchestration Service for RTO suggestion"""

    payload = {
        "process_name": process.name,
        "criticality": process.criticality,
        "financial_impact": process.financial_impact,
        "industry": process.industry,
        "operational_impact": process.operational_impact
    }

    try:
        response = await http_client.post(
            f"{ai_orchestrator_url}/ai/suggest-rto",
            json=payload,
            timeout=2.0  # 2 second timeout
        )

        return AIRTOSuggestion(**response.json())

    except Exception as e:
        # Fallback to rule-based suggestion
        return rule_based_rto_suggestion(process)
```

**AI Endpoints Used:**

| Endpoint | Purpose | Timeout |
|----------|---------|---------|
| POST /ai/suggest-rto | RTO/RPO/MTPD suggestions | 2s |
| POST /ai/discover-dependencies | Dependency discovery | 3s |
| POST /ai/analyze-impact | Impact analysis | 2s |

### 5.2 Fallback Strategy

```python
class AIServiceIntegration:
    """
    AI service integration with fallback to rule-based logic
    """

    async def suggest_rto(self, process: BIAProcess) -> AIRTOSuggestion:
        # Try AI first
        try:
            return await self._ai_suggest_rto(process)
        except AIServiceUnavailable:
            logger.warning("AI service unavailable, using rule-based fallback")
            return self._rule_based_suggest_rto(process)
        except AIServiceTimeout:
            logger.warning("AI service timeout, using rule-based fallback")
            return self._rule_based_suggest_rto(process)

    def _rule_based_suggest_rto(self, process: BIAProcess) -> AIRTOSuggestion:
        """Rule-based RTO suggestion when AI unavailable"""

        rto_map = {
            "critical": (2.0, 1.0, 4.0),
            "high": (4.0, 2.0, 8.0),
            "medium": (8.0, 4.0, 24.0),
            "low": (24.0, 8.0, 48.0)
        }

        rto, rpo, mtpd = rto_map.get(
            process.criticality,
            (8.0, 4.0, 24.0)
        )

        return AIRTOSuggestion(
            suggested_rto_hours=rto,
            suggested_rpo_hours=rpo,
            suggested_mtpd_hours=mtpd,
            confidence_score=0.6,
            reasoning=f"Rule-based suggestion for {process.criticality} process",
            industry_benchmark="Generic industry benchmark"
        )
```

## 6. Database Integration

### 6.1 PostgreSQL Connection

**Connection Pool:**

```python
# Async SQLAlchemy engine
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@postgres:5432/bcm_platform",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

**Connection Management:**

```python
# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()
```

### 6.2 Transaction Management

```python
async def create_process_with_dependencies(
    process: BIAProcessCreate
) -> BIAProcess:
    """
    Create process and dependencies in single transaction
    """
    async with async_session() as session:
        async with session.begin():
            # Insert main process
            db_process = BIAProcessDB(**process.dict())
            session.add(db_process)
            await session.flush()  # Get ID

            # Insert dependencies
            for dep in process.dependencies:
                db_dep = BIADependencyDB(
                    process_id=db_process.id,
                    **dep.dict()
                )
                session.add(db_dep)

            # Commit transaction
            await session.commit()

            return BIAProcess.from_orm(db_process)
```

## 7. Cache Integration

### 7.1 Redis Cache

**Connection:**

```python
redis_client = aioredis.from_url(
    "redis://redis:6379/0",
    encoding="utf-8",
    decode_responses=True
)
```

**Caching Strategy:**

```python
class BIACacheManager:
    """Cache management for BIA service"""

    async def get_process(
        self,
        tenant_id: str,
        process_id: int
    ) -> Optional[BIAProcess]:
        """Get process from cache"""
        cache_key = f"bia:process:{tenant_id}:{process_id}"

        cached = await redis_client.get(cache_key)
        if cached:
            return BIAProcess.parse_raw(cached)

        return None

    async def set_process(
        self,
        process: BIAProcess,
        ttl: int = 300  # 5 minutes
    ):
        """Cache process"""
        cache_key = f"bia:process:{process.tenant_id}:{process.id}"
        await redis_client.setex(
            cache_key,
            ttl,
            process.json()
        )

    async def invalidate_process(
        self,
        tenant_id: str,
        process_id: int
    ):
        """Invalidate process cache"""
        cache_key = f"bia:process:{tenant_id}:{process_id}"
        await redis_client.delete(cache_key)

        # Also invalidate list caches for tenant
        pattern = f"bia:list:{tenant_id}:*"
        async for key in redis_client.scan_iter(match=pattern):
            await redis_client.delete(key)
```

## 8. Workflow Intelligence Integration

### 8.1 Audit Logging

```python
from workflow_intelligence.audit import AuditLogger

# Log BIA creation
await audit_logger.log_action(
    module="bia",
    action="create_process",
    user_id=current_user["user_id"],
    tenant_id=current_user["tenant_id"],
    resource_type="bia_process",
    resource_id=str(process.id),
    changes={
        "name": process.name,
        "criticality": process.criticality
    }
)
```

### 8.2 Compliance Checking

```python
from workflow_intelligence.compliance import ISO22301Checker

# Check ISO 22301 compliance
iso_checker = ISO22301Checker()
compliance_result = await iso_checker.check_clause(
    clause="8.2.2",
    context={
        "bia_processes_count": 50,
        "completed_bia_count": 45,
        "critical_processes_with_rto": 12
    }
)
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-09
**Maintained By**: AI Platform Team
