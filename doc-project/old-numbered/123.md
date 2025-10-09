Хорошо! Создаю финальный полный архитектурный документ прямо здесь в чате. Это будет большой документ со всеми компонентами:

---

# 🏗️ BCM PLATFORM - ФИНАЛЬНАЯ АРХИТЕКТУРА

**Version:** 2.0 Final  
**Date:** October 3, 2025  
**Статус:** Production Ready Architecture

---

## 📋 СОДЕРЖАНИЕ

1. [Общий Overview](#1-общий-overview)
2. [Пятиуровневая Архитектура](#2-пятиуровневая-архитектура)
3. [Data Layer - Детальная Спецификация](#3-data-layer)
4. [Platform Layer - Все Сервисы](#4-platform-layer)
5. [Intelligence Layer - AI Компоненты](#5-intelligence-layer)
6. [Interface Layer - Доступ Пользователей](#6-interface-layer)
7. [Observability Layer - Мониторинг](#7-observability-layer)
8. [Алгоритм Запуска (Снизу Вверх)](#8-алгоритм-запуска)
9. [Стандарты Кода](#9-стандарты-кода)
10. [Integration Patterns](#10-integration-patterns)
11. [Примеры Кода](#11-примеры-кода)

---

## 1. ОБЩИЙ OVERVIEW

### Архитектурная Философия

```
DATA FOUNDATION (снизу)
      ↓
PLATFORM SERVICES (бизнес-логика)
      ↓
INTELLIGENCE (AI/ML)
      ↓
INTERFACES (пользовательский доступ)
      ↓
OBSERVABILITY (мониторинг всего)
```

### Ключевые Принципы

1. **Event-Driven Architecture** - сервисы общаются через события
2. **Microservices** - независимые, масштабируемые компоненты
3. **Domain-Driven Design** - каждый сервис = bounded context
4. **Bottom-Up Assembly** - сборка снизу вверх
5. **AI-Powered** - интеллектуальные помощники на каждом уровне
6. **Self-Learning** - платформа учится на опыте пользователей

---

## 2. ПЯТИУРОВНЕВАЯ АРХИТЕКТУРА

```
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 5: OBSERVABILITY (Мониторинг всего)                      │
│  Prometheus, Grafana, ELK, Jaeger                               │
└──────────────────────────────────────────────────────────────────┘
                            ↕
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 4: INTERFACE (Доступ пользователей)                      │
│  • Web App (Next.js)                                            │
│  • Mobile App                                                    │
│  • MCP Interface (для Claude/ChatGPT) ← ЗДЕСЬ MCP              │
│  • REST API Clients                                             │
└──────────────────────────────────────────────────────────────────┘
                            ↕
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 3: INTELLIGENCE (AI/ML)                                   │
│  • AI Experts (BCM Advisor, Compliance Auditor, Strategic)     │
│  • RAG Pipeline (Knowledge retrieval + generation)              │
│  • ML Models (prediction, anomaly detection)                    │
│  • Case Library (self-learning from users)                     │
└──────────────────────────────────────────────────────────────────┘
                            ↕
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 2: PLATFORM (Бизнес-логика)                              │
│  Infrastructure:                                                 │
│  • API Gateway :8000                                            │
│  • Orchestrator :8002                                           │
│  • EventBus :8001                                               │
│                                                                  │
│  BCM Domain Services:                                            │
│  • Governance :8010                                             │
│  • BIA :8011                                                    │
│  • Risk :8013                                                   │
│  • Planning :8015                                               │
│  • Response :8016                                               │
│  • Compliance :8018                                             │
│  • Documents :8019                                              │
│  • Training :8020                                               │
│                                                                  │
│  Advanced Services:                                              │
│  • Digital Twin :8050                                           │
│  • Simulation :8051                                             │
│                                                                  │
│  Support Services:                                               │
│  • Knowledge Graph Service                                       │
│  • Case Library Service                                         │
│  • ML Predictor Service                                         │
│  • Notification Service                                         │
└──────────────────────────────────────────────────────────────────┘
                            ↕
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 1: DATA (Хранилище)                                      │
│  • PostgreSQL (business data, multi-tenant)                     │
│  • Redis (cache, queue, sessions)                              │
│  • Neo4j (Knowledge Graph - ISO/BCI/WHO standards)             │
│  • MinIO/S3 (documents, files, backups)                        │
│  • Pinecone/pgvector (embeddings для RAG)                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. DATA LAYER

### 3.1 PostgreSQL Schema

**Multi-Tenant Architecture:**

```sql
-- Core tenant table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    size VARCHAR(50), -- small, medium, large, enterprise
    bcm_maturity VARCHAR(50), -- basic, developing, mature, advanced
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users with RBAC
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50), -- admin, bcm_manager, consultant, auditor, viewer
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflow Cases (для Case Library)
CREATE TABLE workflow_cases (
    case_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module VARCHAR(50) NOT NULL, -- bia, risk, planning
    workflow_name VARCHAR(100) NOT NULL,
    
    -- Anonymized context
    organization_context JSONB NOT NULL,
    -- {industry, size, maturity}
    
    -- Full journey
    journey JSONB NOT NULL,
    -- [{stage, actions, challenges, duration}]
    
    -- Metrics
    metrics JSONB NOT NULL,
    -- {duration_days, success, ai_usage, ...}
    
    -- Patterns
    success_patterns JSONB,
    lessons_learned JSONB,
    
    -- For ML
    features JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflow events (для сбора cases)
CREATE TABLE workflow_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    module VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_workflow_events_org_module ON workflow_events(org_id, module);

-- Audit trail (immutable)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID NOT NULL,
    changes JSONB,
    ip_address INET,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
-- Make immutable
ALTER TABLE audit_log ADD CONSTRAINT audit_no_update CHECK (false);
```

**BIA Domain Tables:**

```sql
-- Business processes
CREATE TABLE business_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    bia_id UUID, -- связь с BIA session
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner VARCHAR(255),
    tier VARCHAR(10), -- tier_1, tier_2, tier_3, tier_4
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Impact assessments
CREATE TABLE impact_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID REFERENCES business_processes(id),
    financial_impact JSONB, -- {hourly_loss, daily_loss, ...}
    operational_impact JSONB,
    reputational_impact JSONB,
    regulatory_impact JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RTO/RPO/MTPD
CREATE TABLE recovery_objectives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID REFERENCES business_processes(id),
    rto_hours INTEGER,
    rpo_hours INTEGER,
    mtpd_hours INTEGER,
    rationale TEXT,
    ai_recommended BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dependencies
CREATE TABLE process_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID REFERENCES business_processes(id),
    depends_on UUID REFERENCES business_processes(id),
    dependency_type VARCHAR(50), -- people, technology, facility, supplier
    criticality VARCHAR(20), -- critical, important, normal
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Risk Management Tables:**

```sql
CREATE TABLE risks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- cyber, natural_disaster, operational, etc
    likelihood INTEGER CHECK (likelihood >= 1 AND likelihood <= 5),
    impact INTEGER CHECK (impact >= 1 AND impact <= 5),
    risk_score INTEGER GENERATED ALWAYS AS (likelihood * impact) STORED,
    status VARCHAR(50), -- identified, assessed, treated, monitored
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE risk_treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_id UUID REFERENCES risks(id),
    treatment_type VARCHAR(50), -- avoid, reduce, transfer, accept
    description TEXT,
    owner VARCHAR(255),
    due_date DATE,
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.2 Neo4j Knowledge Graph Schema

```cypher
// ISO 22301 Standard
CREATE (s:Standard {
    id: 'ISO22301:2019',
    name: 'ISO 22301:2019',
    title: 'Security and resilience - Business continuity management systems',
    type: 'international_standard'
})

// Clauses
CREATE (c:Clause {
    id: '8.2.2',
    title: 'Business impact analysis',
    parent: '8.2',
    level: 3
})

// Requirements
CREATE (r:Requirement {
    id: 'req_8.2.2_1',
    text: 'The organization shall conduct business impact analysis',
    type: 'mandatory',
    verification: 'BIA report exists and complete',
    guidance: 'BIA should identify critical activities and their dependencies'
})

// Relationships
CREATE (s)-[:HAS_CLAUSE]->(c)
CREATE (c)-[:HAS_REQUIREMENT]->(r)

// Evidence types
CREATE (e:EvidenceType {
    id: 'bia_report',
    name: 'Business Impact Analysis Report',
    required_fields: ['processes', 'impacts', 'rto', 'dependencies']
})
CREATE (r)-[:REQUIRES_EVIDENCE]->(e)

// Best Practices
CREATE (bp:BestPractice {
    id: 'bp_bia_001',
    title: 'Start with critical processes',
    description: 'Begin BIA by identifying Tier 1 critical processes',
    industry: 'healthcare',
    evidence_count: 45 // сколько успешных cases использовали
})
CREATE (c)-[:HAS_BEST_PRACTICE]->(bp)

// Standard overlaps
MATCH (iso:Standard {id: 'ISO22301:2019'})
MATCH (iso27001:Standard {id: 'ISO27001:2022'})
CREATE (iso)-[:OVERLAPS_WITH {
    percentage: 30,
    common_clauses: ['6.1', '6.2', '9.1']
}]->(iso27001)
```

### 3.3 Redis Data Structures

```redis
# Sessions
SET session:{session_id} "{user_id, org_id, permissions}" EX 3600

# Cache
SET cache:org:{org_id}:context "{...org data...}" EX 300

# Real-time workflow state
HSET workflow:bia:{bia_id} stage "identify_processes" progress 25

# Message queue (Redis Streams)
XADD events:bia * event "bia.process.added" data "{...}"

# Rate limiting
INCR ratelimit:{user_id}:{endpoint} EX 3600
```

### 3.4 Vector Database (Pinecone/pgvector)

```python
# Embeddings для RAG
{
    "id": "iso22301_clause_8.2.2",
    "vector": [0.123, -0.456, ...],  # 1536 dimensions
    "metadata": {
        "source": "ISO22301:2019",
        "clause": "8.2.2",
        "type": "requirement",
        "text": "The organization shall conduct BIA..."
    }
}

# Case embeddings
{
    "id": "case_abc123",
    "vector": [...],
    "metadata": {
        "industry": "healthcare",
        "module": "bia",
        "duration_days": 14,
        "success": true
    }
}
```

---

## 4. PLATFORM LAYER

### 4.1 Infrastructure Services

#### API Gateway (:8000)

**Responsibilities:**
- Authentication (JWT)
- Authorization (RBAC)
- Rate limiting
- Request routing
- Response aggregation (BFF pattern)

**Code Structure:**
```
api_gateway/
├── main.py
├── config.py
├── middleware/
│   ├── auth.py
│   ├── rate_limit.py
│   └── logging.py
├── routes/
│   ├── organizations.py
│   ├── bia.py
│   ├── risk.py
│   └── ...
└── services/
    └── service_proxy.py
```

**Example Code:**

```python
# api_gateway/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from middleware.auth import verify_token
from middleware.rate_limit import rate_limit
import httpx

app = FastAPI(title="BCM Platform API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Service registry
SERVICES = {
    "governance": "http://localhost:8010",
    "bia": "http://localhost:8011",
    "risk": "http://localhost:8013",
    # ...
}

@app.post("/api/organizations")
async def create_organization(
    org_data: dict,
    user = Depends(verify_token)
):
    """Proxy to Governance Service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['governance']}/organizations",
            json=org_data,
            headers={"X-User-ID": user.id}
        )
        return response.json()

@app.get("/api/organizations/{org_id}/context")
async def get_org_context(
    org_id: str,
    user = Depends(verify_token)
):
    """Aggregate data from multiple services"""
    async with httpx.AsyncClient() as client:
        # Parallel requests
        gov_task = client.get(f"{SERVICES['governance']}/organizations/{org_id}")
        bia_task = client.get(f"{SERVICES['bia']}/bia/{org_id}/current")
        risk_task = client.get(f"{SERVICES['risk']}/risks?org_id={org_id}")
        
        gov, bia, risk = await asyncio.gather(gov_task, bia_task, risk_task)
        
        return {
            "organization": gov.json(),
            "bia": bia.json(),
            "risks": risk.json()
        }
```

#### EventBus (:8001)

**Responsibilities:**
- Pub/Sub messaging
- WebSocket server (real-time)
- Event persistence
- Event replay

**Code Structure:**
```
eventbus/
├── main.py
├── broker/
│   ├── redis_broker.py
│   └── websocket.py
├── models/
│   └── event.py
└── storage/
    └── event_store.py
```

**Example Code:**

```python
# eventbus/main.py
from fastapi import FastAPI, WebSocket
from redis import asyncio as aioredis
import json

app = FastAPI(title="EventBus")

redis = aioredis.from_url("redis://localhost:6379")

# WebSocket connections
active_connections: dict[str, list[WebSocket]] = {}

@app.post("/publish")
async def publish_event(topic: str, data: dict):
    """Publish event to topic"""
    event = {
        "topic": topic,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    # Redis Streams
    await redis.xadd(f"events:{topic}", event)
    
    # Notify WebSocket subscribers
    await notify_websocket_subscribers(topic, event)
    
    return {"status": "published", "topic": topic}

@app.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str):
    """WebSocket subscription to topic"""
    await websocket.accept()
    
    if topic not in active_connections:
        active_connections[topic] = []
    active_connections[topic].append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except:
        active_connections[topic].remove(websocket)

async def notify_websocket_subscribers(topic: str, event: dict):
    """Send event to all WebSocket subscribers"""
    if topic in active_connections:
        for ws in active_connections[topic]:
            await ws.send_json(event)
```

#### Orchestrator (:8002)

**Responsibilities:**
- Service discovery
- Health checks
- Workflow orchestration (Temporal.io)
- Distributed tracing

**Code Structure:**
```
orchestrator/
├── main.py
├── registry/
│   └── service_registry.py
├── health/
│   └── health_checker.py
├── workflows/
│   ├── iso22301_implementation.py
│   └── bia_process.py
└── activities/
    └── service_activities.py
```

**Example Code:**

```python
# orchestrator/registry/service_registry.py
from typing import Dict, Optional
import httpx
from datetime import datetime

class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
    
    async def register(
        self,
        name: str,
        host: str,
        port: int,
        health_check_url: str
    ):
        """Register a service"""
        self.services[name] = ServiceInfo(
            name=name,
            host=host,
            port=port,
            health_check_url=health_check_url,
            status="healthy",
            last_checked=datetime.now()
        )
    
    async def health_check_all(self):
        """Check health of all services"""
        for name, service in self.services.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"http://{service.host}:{service.port}{service.health_check_url}",
                        timeout=5.0
                    )
                    service.status = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                service.status = "unreachable"
            
            service.last_checked = datetime.now()
    
    def get_service_url(self, name: str) -> Optional[str]:
        """Get service URL"""
        service = self.services.get(name)
        if service and service.status == "healthy":
            return f"http://{service.host}:{service.port}"
        return None
```

**Workflow Example (Temporal.io):**

```python
# orchestrator/workflows/iso22301_implementation.py
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class ISO22301ImplementationWorkflow:
    @workflow.run
    async def run(self, org_id: str) -> dict:
        """12-month ISO 22301 certification workflow"""
        
        # Phase 1: Context & Planning
        await workflow.execute_activity(
            create_organization_context,
            args=[org_id],
            start_to_close_timeout=timedelta(days=7)
        )
        
        # Phase 2: BIA
        bia_result = await workflow.execute_activity(
            conduct_bia,
            args=[org_id],
            start_to_close_timeout=timedelta(days=30)
        )
        
        # Wait for user approval
        await workflow.wait_condition(
            lambda: self.bia_approved,
            timeout=timedelta(days=14)
        )
        
        # Phase 3: Risk Assessment
        risk_result = await workflow.execute_activity(
            assess_risks,
            args=[org_id, bia_result],
            start_to_close_timeout=timedelta(days=30)
        )
        
        # ... continue through all phases
        
        return {"status": "completed", "duration_months": 12}
```

### 4.2 BCM Domain Services

#### BIA Service (:8011)

**Полная Архитектура:**

```
services/bia/
├── main.py                    # FastAPI app
├── config.py                  # Configuration
├── models/
│   ├── domain.py              # Pydantic models
│   └── database.py            # SQLAlchemy models
├── api/
│   ├── routes.py              # REST endpoints
│   └── schemas.py             # Request/Response schemas
├── services/
│   └── bia_service.py         # Business logic
├── repositories/
│   └── bia_repository.py      # Data access
├── workflow/
│   └── state_machine.py       # Workflow State Machine
├── events/
│   ├── publishers.py          # Publish events
│   └── subscribers.py         # Subscribe to events
└── migrations/
    └── versions/
```

**Workflow State Machine:**

```python
# services/bia/workflow/state_machine.py
from enum import Enum
from typing import List, Optional

class BIAStage(Enum):
    NOT_STARTED = "not_started"
    IDENTIFY_PROCESSES = "identify_processes"
    ANALYZE_DEPENDENCIES = "analyze_dependencies"
    ASSESS_IMPACT = "assess_impact"
    DETERMINE_RTO = "determine_rto"
    REVIEW_RESULTS = "review_results"
    COMPLETED = "completed"

class BIAWorkflow:
    TRANSITIONS = {
        BIAStage.NOT_STARTED: [BIAStage.IDENTIFY_PROCESSES],
        BIAStage.IDENTIFY_PROCESSES: [BIAStage.ANALYZE_DEPENDENCIES],
        BIAStage.ANALYZE_DEPENDENCIES: [BIAStage.ASSESS_IMPACT],
        BIAStage.ASSESS_IMPACT: [BIAStage.DETERMINE_RTO],
        BIAStage.DETERMINE_RTO: [BIAStage.REVIEW_RESULTS],
        BIAStage.REVIEW_RESULTS: [
            BIAStage.COMPLETED,
            BIAStage.IDENTIFY_PROCESSES  # can go back
        ]
    }
    
    REQUIREMENTS = {
        BIAStage.IDENTIFY_PROCESSES: {
            "min_processes": 3,
            "required_fields": ["name", "description", "owner"]
        },
        BIAStage.ANALYZE_DEPENDENCIES: {
            "min_dependencies_per_process": 2
        },
        BIAStage.ASSESS_IMPACT: {
            "required_impact_types": [
                "financial", "operational", "reputational", "regulatory"
            ]
        },
        BIAStage.DETERMINE_RTO: {
            "required_fields": ["rto", "rpo", "mtpd", "rationale"]
        }
    }
    
    def __init__(self, bia_id: str):
        self.bia_id = bia_id
        self.current_stage = BIAStage.NOT_STARTED
        self.completed_steps = []
    
    async def get_current_context(self) -> dict:
        """Full context for AI Advisor"""
        bia_data = await db.get_bia(self.bia_id)
        
        return {
            "bia_id": self.bia_id,
            "current_stage": self.current_stage.value,
            "progress": self._calculate_progress(),
            "data": {
                "processes": [p.dict() for p in bia_data.processes],
                "dependencies": [d.dict() for d in bia_data.dependencies],
                "impacts": [i.dict() for i in bia_data.impacts]
            },
            "gaps": self._identify_gaps(bia_data),
            "available_actions": self._get_available_actions(),
            "issues": self._identify_issues(bia_data)
        }
    
    def _identify_gaps(self, bia_data) -> List[dict]:
        """What's missing for current stage"""
        gaps = []
        requirements = self.REQUIREMENTS.get(self.current_stage, {})
        
        if self.current_stage == BIAStage.IDENTIFY_PROCESSES:
            min_processes = requirements["min_processes"]
            if len(bia_data.processes) < min_processes:
                gaps.append({
                    "type": "insufficient_data",
                    "message": f"Need {min_processes} processes, have {len(bia_data.processes)}",
                    "severity": "critical"
                })
        
        return gaps
    
    def _get_available_actions(self) -> List[dict]:
        """What user can do now"""
        actions = []
        
        if self.current_stage == BIAStage.IDENTIFY_PROCESSES:
            actions.append({
                "id": "add_process",
                "label": "Add Business Process",
                "type": "primary"
            })
            actions.append({
                "id": "ai_suggest_processes",
                "label": "AI: Suggest Typical Processes",
                "type": "secondary",
                "requires_ai": True
            })
        
        elif self.current_stage == BIAStage.ASSESS_IMPACT:
            actions.append({
                "id": "ai_analyze_impact",
                "label": "AI: Analyze Impact",
                "type": "primary",
                "requires_ai": True
            })
        
        return actions
    
    async def transition_to(self, next_stage: BIAStage) -> bool:
        """Move to next stage"""
        if next_stage not in self.TRANSITIONS[self.current_stage]:
            return False
        
        if not await self._stage_completed(self.current_stage):
            return False
        
        self.current_stage = next_stage
        self.completed_steps.append({
            "stage": next_stage.value,
            "completed_at": datetime.now()
        })
        
        await db.update_bia_stage(self.bia_id, next_stage.value)
        
        # Publish event
        await eventbus.publish("bia.stage.changed", {
            "bia_id": self.bia_id,
            "new_stage": next_stage.value,
            "progress": self._calculate_progress()
        })
        
        return True
```

**BIA Service Logic:**

```python
# services/bia/services/bia_service.py
class BIAService:
    def __init__(self, repository: BIARepository):
        self.repo = repository
        self.eventbus = EventBusClient()
    
    async def add_process(
        self,
        bia_id: str,
        process: ProcessCreate
    ) -> str:
        """Add process to BIA"""
        
        # Save to DB
        process_id = await self.repo.add_process(bia_id, process)
        
        # Publish event for Case Collector
        await self.eventbus.publish("bia.workflow.action.taken", {
            "bia_id": bia_id,
            "action": "add_process",
            "data": process.dict(),
            "timestamp": datetime.now()
        })
        
        # Check if can move to next stage
        workflow = BIAWorkflow(bia_id)
        context = await workflow.get_current_context()
        
        if len(context["data"]["processes"]) >= 3:
            await self.eventbus.publish("bia.milestone.reached", {
                "bia_id": bia_id,
                "milestone": "minimum_processes_reached"
            })
        
        return process_id
    
    async def analyze_impact(
        self,
        bia_id: str,
        process_id: str
    ) -> ImpactAssessment:
        """Analyze impact of process"""
        
        process = await self.repo.get_process(process_id)
        org = await self.repo.get_organization(process.org_id)
        
        # Calculate impacts
        impact = ImpactAssessment(
            process_id=process_id,
            financial_impact=self._calculate_financial_impact(process, org),
            operational_impact=self._calculate_operational_impact(process, org),
            reputational_impact=self._calculate_reputational_impact(process, org),
            regulatory_impact=self._calculate_regulatory_impact(process, org)
        )
        
        await self.repo.save_impact(bia_id, impact)
        
        # Publish event
        await self.eventbus.publish("bia.process.analyzed", {
            "bia_id": bia_id,
            "process_id": process_id,
            "impact": impact.dict()
        })
        
        return impact
```

**Event Subscribers:**

```python
# services/bia/events/subscribers.py
class BIAEventSubscriber:
    def __init__(self):
        self.eventbus = EventBusClient()
    
    async def start(self):
        await self.eventbus.subscribe([
            "governance.organization.created"
        ], self.handle_event)
    
    async def handle_event(self, event: Event):
        if event.topic == "governance.organization.created":
            await self.on_organization_created(event)
    
    async def on_organization_created(self, event: Event):
        """Auto-create BIA template for new org"""
        org_id = event.data["org_id"]
        industry = event.data["industry"]
        
        # Create BIA template
        bia_service = get_bia_service()
        bia_id = await bia_service.start_bia(org_id)
        
        # Suggest typical processes for industry
        suggested = get_default_processes_for_industry(industry)
        for process in suggested:
            await bia_service.add_process(bia_id, process)
```

#### Risk Service (:8013)

**Similar structure to BIA, key differences:**

```python
# services/risk/services/risk_service.py
class RiskService:
    async def assess_risk(
        self,
        org_id: str,
        risk_id: str
    ) -> RiskAssessment:
        """Assess risk using FAIR methodology"""
        
        risk = await self.repo.get_risk(risk_id)
        
        # FAIR: Loss Event Frequency * Loss Magnitude
        lef = await self._calculate_loss_event_frequency(risk)
        magnitude = await self._calculate_loss_magnitude(risk)
        
        assessment = RiskAssessment(
            risk_id=risk_id,
            likelihood=lef.to_likelihood_score(),
            impact=magnitude.to_impact_score(),
            risk_score=lef.to_likelihood_score() * magnitude.to_impact_score(),
            annualized_loss_expectancy=lef.annual * magnitude.average
        )
        
        await self.repo.save_assessment(assessment)
        
        # Publish event
        await self.eventbus.publish("risk.assessed", {
            "org_id": org_id,
            "risk_id": risk_id,
            "assessment": assessment.dict()
        })
        
        return assessment
```

---

## 5. INTELLIGENCE LAYER

### 5.1 AI Experts (не MCP серверы)

**AI Experts - это backend сервисы с AI capabilities**

```
ai_experts/
├── bcm_advisor/
│   ├── main.py
│   ├── advisors/
│   │   ├── bia_advisor.py
│   │   ├── risk_advisor.py
│   │   └── planning_advisor.py
│   └── tools/
│       ├── recommend_rto.py
│       ├── generate_plan.py
│       └── simulate_incident.py
├── compliance_auditor/
│   ├── main.py
│   └── auditors/
│       ├── document_auditor.py
│       ├── clause_checker.py
│       └── gap_analyzer.py
└── strategic_advisor/
    ├── main.py
    └── advisors/
        ├── benchmark.py
        └── roadmap.py
```

**BIA Advisor Example:**

```python
# ai_experts/bcm_advisor/advisors/bia_advisor.py
class BIAAdvisor:
    def __init__(self):
        self.llm = AnthropicClient()  # Claude
        self.knowledge_graph = Neo4jClient()
        self.case_library = CaseLibraryClient()
        self.vector_db = PineconeClient()
    
    async def get_advice(
        self,
        bia_id: str,
        user_message: Optional[str] = None
    ) -> dict:
        """Get contextual advice for BIA"""
        
        # 1. Get workflow state from platform
        workflow_context = await platform_api.get(
            f"/bia/{bia_id}/workflow-context"
        )
        
        # 2. Find similar successful cases
        similar_cases = await self.case_library.find_similar(
            industry=workflow_context["org"]["industry"],
            module="bia",
            stage=workflow_context["current_stage"],
            limit=3
        )
        
        # 3. Get relevant knowledge
        knowledge = await self._rag_retrieve(
            query=f"BIA {workflow_context['current_stage']} best practices",
            sources=["iso22301", "bci_gpg"]
        )
        
        # 4. Build comprehensive prompt
        prompt = self._build_advice_prompt(
            workflow_context=workflow_context,
            similar_cases=similar_cases,
            knowledge=knowledge,
            user_message=user_message
        )
        
        # 5. LLM generates advice
        advice = await self.llm.generate(
            prompt=prompt,
            model="claude-sonnet-4",
            temperature=0.7
        )
        
        return {
            "message": advice.text,
            "similar_cases": self._format_cases_for_ui(similar_cases),
            "suggested_actions": advice.suggested_actions,
            "benchmarks": await self.case_library.get_benchmarks(
                workflow_context["org"]
            )
        }
    
    async def _rag_retrieve(
        self,
        query: str,
        sources: List[str]
    ) -> List[Document]:
        """RAG retrieval"""
        
        # 1. Embed query
        query_embedding = await self.vector_db.embed(query)
        
        # 2. Semantic search
        results = await self.vector_db.query(
            vector=query_embedding,
            filter={"source": {"$in": sources}},
            top_k=10
        )
        
        # 3. Re-rank with Cohere
        reranked = await cohere_rerank(query, results)
        
        return reranked[:5]
    
    def _build_advice_prompt(
        self,
        workflow_context: dict,
        similar_cases: List[Case],
        knowledge: List[Document],
        user_message: Optional[str]
    ) -> str:
        return f"""
You are a BCM expert helping with Business Impact Analysis.

CURRENT SITUATION:
Stage: {workflow_context['current_stage']}
Progress: {workflow_context['progress']}%
Organization: {workflow_context['org']['industry']} ({workflow_context['org']['size']})

DATA:
- Processes identified: {len(workflow_context['data']['processes'])}
- Dependencies mapped: {len(workflow_context['data']['dependencies'])}

GAPS (what's missing):
{json.dumps(workflow_context['gaps'], indent=2)}

LEARN FROM SIMILAR SUCCESSFUL CASES:
{self._format_cases_for_prompt(similar_cases)}

KNOWLEDGE BASE:
{self._format_knowledge_for_prompt(knowledge)}

USER MESSAGE: {user_message or "Provide proactive guidance"}

YOUR TASK:
1. Analyze current situation vs. similar successful cases
2. Identify if user is on track or struggling
3. Provide specific, actionable advice
4. Suggest concrete next steps
5. Warn about common pitfalls

Be conversational, encouraging, and specific. Use examples from similar cases.
"""
```

**Tools that AI Experts expose:**

```python
# ai_experts/bcm_advisor/tools/recommend_rto.py
async def recommend_rto(
    org_id: str,
    process_name: str
) -> dict:
    """AI recommends RTO for a process"""
    
    # Get platform data
    org = await platform_api.get(f"/organizations/{org_id}")
    bia = await platform_api.get(f"/bia/{org_id}/current")
    process = find_process(bia, process_name)
    
    # Get knowledge
    iso_guidance = await knowledge_graph.query("""
        MATCH (c:Clause {id: '8.2.2'})-[:HAS_GUIDANCE]->(g)
        RETURN g.text
    """)
    
    # Get similar cases
    cases = await case_library.search({
        "industry": org["industry"],
        "process_type": process["type"],
        "successful": True
    })
    
    # LLM analysis
    prompt = f"""
Based on ISO 22301 and successful cases:

Organization: {org['name']} ({org['industry']}, {org['size']})
Process: {process_name}
Type: {process['type']}
Current data: {process}

ISO 22301 Guidance:
{iso_guidance}

Similar organizations did:
{format_cases(cases)}

Recommend appropriate RTO with detailed rationale.
Consider:
- Financial impact per hour of downtime
- Regulatory requirements
- Operational dependencies
- Industry benchmarks
"""
    
    recommendation = await llm_generate(
        prompt=prompt,
        structured_output=RTORecommendationSchema
    )
    
    # Save to platform
    await platform_api.post(
        f"/bia/{bia['id']}/rto",
        {
            "process_id": process["id"],
            "rto_hours": recommendation.rto_hours,
            "rationale": recommendation.rationale,
            "ai_generated": True
        }
    )
    
    return recommendation.dict()
```

### 5.2 Case Library Service

**Полная архитектура:**

```
services/case_library/
├── main.py
├── models/
│   └── case.py
├── services/
│   ├── collector.py      # Собирает cases из workflow events
│   ├── library.py        # Хранение и поиск
│   ├── analyzer.py       # Извлечение patterns с AI
│   └── benchmark.py      # Статистика
├── api/
│   └── routes.py
└── migrations/
```

**Case Collector:**

```python
# services/case_library/services/collector.py
class CaseCollector:
    def __init__(self):
        self.eventbus = EventBusClient()
    
    async def start(self):
        """Subscribe to ALL workflow events"""
        await self.eventbus.subscribe([
            "*.workflow.step.completed",
            "*.workflow.action.taken",
            "*.workflow.challenge.encountered",
            "*.workflow.completed"
        ], self.handle_event)
    
    async def handle_event(self, event: Event):
        """Record every workflow event"""
        
        # Save to workflow_events table
        await db.workflow_events.create({
            "org_id": event.data["org_id"],
            "module": event.data["module"],
            "event_type": event.topic,
            "data": event.data,
            "timestamp": event.timestamp
        })
        
        # If workflow completed, compile into case
        if event.topic.endswith(".workflow.completed"):
            await self.create_case(event)
    
    async def create_case(self, event: Event):
        """Compile all events into a workflow case"""
        
        org_id = event.data["org_id"]
        module = event.data["module"]
        
        # Get all events for this workflow
        events = await db.workflow_events.filter(
            org_id=org_id,
            module=module,
            created_at__gte=event.data["started_at"]
        )
        
        # Build journey from events
        journey = self._build_journey_from_events(events)
        
        # Calculate metrics
        metrics = {
            "duration_days": (event.timestamp - event.data["started_at"]).days,
            "total_actions": len([e for e in events if "action" in e.event_type]),
            "ai_usage_count": len([e for e in events if e.data.get("ai_generated")]),
            "challenges_encountered": len([e for e in events if "challenge" in e.event_type]),
            "completed_successfully": event.data["completed_successfully"]
        }
        
        # Extract success patterns with AI
        patterns = await self._extract_patterns_ai(journey, metrics)
        
        # Anonymize organization
        org_context = await self._anonymize_org_context(org_id)
        
        # Create case
        case = WorkflowCase(
            module=module,
            workflow_name=event.data["workflow_name"],
            organization_context=org_context,
            journey=journey,
            metrics=metrics,
            success_patterns=patterns,
            features=self._extract_ml_features(org_context, metrics)
        )
        
        await db.cases.create(case)
        
        # Create embedding for semantic search
        embedding = await self._create_case_embedding(case)
        await vector_db.upsert(
            id=case.case_id,
            vector=embedding,
            metadata={
                "module": module,
                "industry": org_context["industry"],
                "duration": metrics["duration_days"],
                "success": metrics["completed_successfully"]
            }
        )
        
        # Trigger ML retraining
        await ml_predictor.retrain_async()
    
    async def _extract_patterns_ai(
        self,
        journey: List[dict],
        metrics: dict
    ) -> List[str]:
        """AI extracts what worked well"""
        
        prompt = f"""
Analyze this workflow journey and identify success patterns:

Journey:
{json.dumps(journey, indent=2)}

Metrics:
- Duration: {metrics['duration_days']} days
- AI usage: {metrics['ai_usage_count']} times
- Challenges: {metrics['challenges_encountered']}

Identify:
1. Actions that accelerated progress
2. Effective problem-solving approaches
3. AI recommendations that were valuable
4. Best practices demonstrated

Return as bullet points.
"""
        
        patterns = await llm_generate(prompt)
        return patterns.split('\n')
```

**Case Library Search:**

```python
# services/case_library/services/library.py
class CaseLibrary:
    async def find_similar(
        self,
        industry: str,
        module: str,
        stage: str,
        limit: int = 5
    ) -> List[WorkflowCase]:
        """Find similar successful cases"""
        
        # Build semantic query
        query = f"""
        Organization: {industry}
        Module: {module}
        Stage: {stage}
        Looking for: successful workflow examples
        """
        
        # Semantic search in vector DB
        results = await vector_db.query(
            query=query,
            filter={
                "module": module,
                "industry": industry,
                "success": True
            },
            top_k=limit
        )
        
        # Load full cases
        cases = []
        for result in results:
            case = await db.cases.get(result.id)
            cases.append(case)
        
        return cases
    
    async def get_benchmarks(
        self,
        org: dict
    ) -> dict:
        """Industry benchmarks"""
        
        cases = await db.cases.filter(
            industry=org["industry"],
            size=org["size"]
        )
        
        if not cases:
            return {"message": "Not enough data yet"}
        
        return {
            "total_cases": len(cases),
            "avg_duration_days": statistics.mean([
                c.metrics["duration_days"] for c in cases
            ]),
            "success_rate": len([
                c for c in cases if c.metrics["completed_successfully"]
            ]) / len(cases),
            "common_challenges": self._aggregate_challenges(cases),
            "best_practices": self._aggregate_patterns(cases),
            "ai_usage_correlation": {
                "avg_ai_usage": statistics.mean([
                    c.metrics["ai_usage_count"] for c in cases
                ]),
                "success_with_high_ai": len([
                    c for c in cases 
                    if c.metrics["ai_usage_count"] > 10 
                    and c.metrics["completed_successfully"]
                ]) / len([c for c in cases if c.metrics["ai_usage_count"] > 10])
            }
        }
```

### 5.3 ML Predictor Service

```python
# services/ml_predictor/models/workflow_predictor.py
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import numpy as np

class WorkflowPredictor:
    def __init__(self):
        self.success_model = None
        self.duration_model = None
    
    async def train(self):
        """Train on Case Library data"""
        
        # Load all cases
        cases = await db.cases.all()
        
        # Prepare features and labels
        X = []
        y_success = []
        y_duration = []
        
        for case in cases:
            features = [
                self._encode_industry(case.features["industry"]),
                self._encode_size(case.features["size"]),
                case.features["experience_level"],
                case.features["team_size"],
                case.features["ai_assistance_level"]
            ]
            X.append(features)
            y_success.append(case.metrics["completed_successfully"])
            y_duration.append(case.metrics["duration_days"])
        
        X = np.array(X)
        y_success = np.array(y_success)
        y_duration = np.array(y_duration)
        
        # Train models
        self.success_model = RandomForestClassifier(n_estimators=100)
        self.success_model.fit(X, y_success)
        
        self.duration_model = RandomForestRegressor(n_estimators=100)
        self.duration_model.fit(X, y_duration)
        
        # Save models
        joblib.dump(self.success_model, "models/success_v1.pkl")
        joblib.dump(self.duration_model, "models/duration_v1.pkl")
    
    async def predict(
        self,
        org_context: dict,
        current_progress: dict
    ) -> dict:
        """Predict success and duration"""
        
        features = self._prepare_features(org_context, current_progress)
        
        success_prob = self.success_model.predict_proba(features)[0][1]
        estimated_duration = self.duration_model.predict(features)[0]
        
        # Identify risk factors
        risk_factors = []
        if success_prob < 0.7:
            risk_factors.append("Low success probability - consider consultant")
        
        if estimated_duration > 90:
            risk_factors.append("Long estimated duration - may need more resources")
        
        if current_progress["ai_usage"] < 5:
            risk_factors.append("Low AI usage - AI assistance may help accelerate")
        
        return {
            "success_probability": float(success_prob),
            "estimated_duration_days": float(estimated_duration),
            "risk_level": "high" if success_prob < 0.7 else "medium" if success_prob < 0.85 else "low",
            "risk_factors": risk_factors,
            "recommendations": self._generate_recommendations(risk_factors)
        }
```

---

## 6. INTERFACE LAYER

### 6.1 Web Application (Next.js)

**Структура:**

```
frontend/bcm-platform/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/
│   │   ├── overview/
│   │   ├── bia/
│   │   ├── risk/
│   │   ├── planning/
│   │   └── compliance/
│   └── layout.tsx
├── components/
│   ├── shared/
│   │   ├── AIAdvisorSidebar.tsx
│   │   ├── WorkflowProgress.tsx
│   │   └── SimilarCases.tsx
│   ├── bia/
│   │   ├── ProcessCanvas.tsx
│   │   ├── ImpactAssessment.tsx
│   │   └── RTODetermination.tsx
│   └── risk/
│       ├── RiskMatrix.tsx
│       └── TreatmentPlan.tsx
├── lib/
│   ├── api.ts
│   ├── websocket.ts
│   └── mcp-client.ts  (для MCP интеграции)
└── hooks/
    ├── useWorkflow.ts
    ├── useAIAdvisor.ts
    └── useCases.ts
```

**AI Advisor Sidebar (универсальный компонент):**

```typescript
// components/shared/AIAdvisorSidebar.tsx
import { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface AIAdvisorProps {
  module: 'bia' | 'risk' | 'planning';
  contextId: string;
  orgId: string;
}

export function AIAdvisorSidebar({ module, contextId, orgId }: AIAdvisorProps) {
  const [advice, setAdvice] = useState<AIAdvice | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(false);
  const ws = useWebSocket();
  
  // Load initial advice
  useEffect(() => {
    loadAdvice();
    loadSimilarCases();
  }, [module, contextId]);
  
  // Real-time updates
  useEffect(() => {
    ws.subscribe(`${module}.${contextId}.updated`, (event) => {
      loadAdvice(); // Refresh advice when workflow changes
    });
  }, [module, contextId]);
  
  async function loadAdvice() {
    setLoading(true);
    const response = await fetch(
      `/api/ai/${module}/${contextId}/advice`,
      {
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'X-Org-ID': orgId
        }
      }
    );
    const data = await response.json();
    setAdvice(data);
    setLoading(false);
  }
  
  async function loadSimilarCases() {
    const response = await fetch(
      `/api/case-library/similar?module=${module}&orgId=${orgId}`
    );
    const data = await response.json();
    setCases(data.cases);
  }
  
  async function handleAskAI(message: string) {
    setLoading(true);
    const response = await fetch(
      `/api/ai/${module}/${contextId}/chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ message })
      }
    );
    const data = await response.json();
    setAdvice(data);
    setLoading(false);
  }
  
  return (
    <div className="w-96 border-l bg-gray-50 flex flex-col h-full">
      {/* Workflow Progress */}
      <div className="p-4 border-b bg-white">
        <h3 className="font-semibold mb-2">Current Progress</h3>
        <WorkflowProgress 
          stage={advice?.workflow_state.current_stage}
          percentage={advice?.workflow_state.progress}
        />
      </div>
      
      {/* AI Advice */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="animate-pulse">Loading...</div>
        ) : (
          <>
            {/* Main advice */}
            <div className="mb-4">
              <div className="flex items-start gap-2">
                <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
                  🤖
                </div>
                <div className="flex-1">
                  <p className="text-sm whitespace-pre-line">
                    {advice?.message}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Gaps */}
            {advice?.workflow_state.gaps?.length > 0 && (
              <Alert variant="warning" className="mb-4">
                <AlertTitle>What's Missing</AlertTitle>
                <AlertDescription>
                  <ul className="list-disc pl-4">
                    {advice.workflow_state.gaps.map((gap, i) => (
                      <li key={i}>{gap.message}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}
            
            {/* Similar Cases */}
            {cases.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2">
                  📚 Learn from Similar Organizations
                </h4>
                <div className="space-y-2">
                  {cases.map(case => (
                    <Card key={case.case_id}>
                      <CardContent className="p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="text-sm font-medium">
                              {case.organization_context.industry}
                            </p>
                            <p className="text-xs text-gray-600">
                              Completed in {case.metrics.duration_days} days
                            </p>
                          </div>
                          <Badge variant="success">Success</Badge>
                        </div>
                        
                        <div>
                          <p className="text-xs font-medium mb-1">What worked:</p>
                          <ul className="text-xs space-y-1">
                            {case.success_patterns.slice(0, 3).map((pattern, i) => (
                              <li key={i} className="flex items-start gap-1">
                                <span>✓</span>
                                <span>{pattern}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
            
            {/* Benchmarks */}
            {advice?.benchmarks && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2">📊 Benchmarks</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <p className="text-gray-600">Avg Duration</p>
                    <p className="font-semibold">
                      {advice.benchmarks.avg_duration_days} days
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Success Rate</p>
                    <p className="font-semibold">
                      {(advice.benchmarks.success_rate * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
      
      {/* Quick Actions */}
      <div className="p-4 border-t bg-white">
        <h4 className="font-semibold mb-2">Suggested Actions</h4>
        <div className="space-y-2">
          {advice?.suggested_actions?.map(action => (
            <Button
              key={action.id}
              variant={action.type === 'primary' ? 'default' : 'outline'}
              className="w-full justify-start"
              onClick={() => handleAction(action.id)}
            >
              {action.label}
            </Button>
          ))}
        </div>
      </div>
      
      {/* Chat Input */}
      <div className="p-4 border-t">
        <input
          type="text"
          placeholder="Ask AI Advisor..."
          className="w-full px-3 py-2 border rounded-md"
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleAskAI(e.currentTarget.value);
              e.currentTarget.value = '';
            }
          }}
        />
      </div>
    </div>
  );
}
```

### 6.2 MCP Interface

**MCP - это протокол доступа к AI Experts, НЕ отдельный слой**

```
interfaces/
└── mcp/
    ├── mcp_server.py        # MCP Protocol implementation
    ├── tools_registry.py     # Available tools
    └── adapters/
        ├── bcm_advisor_adapter.py
        └── compliance_adapter.py
```

**MCP Server (тонкий адаптер):**

```python
# interfaces/mcp/mcp_server.py
from mcp.server import Server
import httpx

server = Server("bcm-platform-mcp")

# Platform API client
platform_api = httpx.AsyncClient(base_url="http://localhost:8000/api")

@server.tool("recommend_rto")
async def recommend_rto(org_id: str, process_name: str) -> dict:
    """
    MCP tool - просто прокси к AI Expert
    """
    
    # Вызвать AI Expert через Platform API
    response = await platform_api.post(
        "/ai/bcm-advisor/recommend-rto",
        json={
            "org_id": org_id,
            "process_name": process_name
        }
    )
    
    return response.json()

@server.tool("audit_documents")
async def audit_documents(org_id: str, standard: str = "ISO22301") -> dict:
    """
    MCP tool - прокси к Compliance Auditor
    """
    
    response = await platform_api.post(
        "/ai/compliance-auditor/audit-documents",
        json={
            "org_id": org_id,
            "standard": standard
        }
    )
    
    return response.json()

# ... все остальные tools как тонкие прокси
```

**MCP - это просто альтернативный интерфейс**, настоящая логика в AI Experts (Intelligence Layer).

---

## 7. OBSERVABILITY LAYER

### Prometheus Metrics

```python
# shared/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
bia_completed = Counter(
    'bia_completed_total',
    'Total BIAs completed',
    ['industry', 'size']
)

bia_duration = Histogram(
    'bia_duration_days',
    'BIA completion time',
    buckets=[7, 14, 21, 30, 60, 90]
)

# System metrics
http_requests = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# AI metrics
ai_requests = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['advisor', 'tool']
)

ai_latency = Histogram(
    'ai_latency_seconds',
    'AI request latency'
)
```

### Structured Logging

```python
# shared/utils/logging.py
import structlog

logger = structlog.get_logger()

# Every log is structured
logger.info(
    "bia_completed",
    org_id="hospital_001",
    bia_id="bia_123",
    duration_days=14,
    processes_count=12,
    ai_usage_count=15,
    user_id="user_456"
)
```

---

## 8. АЛГОРИТМ ЗАПУСКА (Снизу Вверх)

### Phase 1: Data Layer (День 1)

```bash
# 1. Создать .env
cp .env.
---

```bash
# 1. Создать .env
cp .env.example .env
# Отредактировать: добавить API ключи (OpenAI, Anthropic, Pinecone)

# 2. Запустить инфраструктуру
docker-compose -f docker-compose.dev.yml up -d

# 3. Проверить что всё работает
docker-compose ps  # все сервисы должны быть "Up"

# 4. Проверить connectivity
psql postgresql://bcm:bcm_dev_pass@localhost:5432/bcm_platform
# \dt  # должна быть пустая БД
# \q

redis-cli ping  # должно вернуть PONG

# 5. Проверить Neo4j
# Открыть http://localhost:7474
# Login: neo4j / neo4j_dev_pass
```

### Phase 2: Database Schemas (День 1-2)

```bash
# Создать все migrations для каждого сервиса

# Governance Service
cd services/governance
alembic init alembic
# Создать модели в models/database.py
alembic revision --autogenerate -m "initial governance schema"
alembic upgrade head

# BIA Service
cd ../bia
alembic init alembic
alembic revision --autogenerate -m "initial bia schema"
alembic upgrade head

# Risk Service
cd ../risk
alembic init alembic
alembic revision --autogenerate -m "initial risk schema"
alembic upgrade head

# ... repeat for all services

# Case Library
cd ../case_library
alembic init alembic
alembic revision --autogenerate -m "workflow cases schema"
alembic upgrade head
```

**Verify migrations:**
```sql
-- Проверить что таблицы созданы
psql postgresql://bcm:bcm_dev_pass@localhost:5432/bcm_platform

\dt  -- должны видеть все таблицы

SELECT * FROM organizations;  -- пусто, но таблица есть
```

### Phase 3: Knowledge Graph (День 2-3)

```bash
# Ingest ISO 22301 в Neo4j
cd scripts
python ingest_iso22301.py

# Ingest BCI Good Practice Guidelines
python ingest_bci_gpg.py

# Verify в Neo4j browser (http://localhost:7474)
# Query:
MATCH (s:Standard) RETURN s

# Должны видеть ISO 22301, ISO 27001, BCI GPG
```

**Скрипт для инициализации Knowledge Graph:**

```python
# scripts/ingest_iso22301.py
from neo4j import GraphDatabase
import json

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "neo4j_dev_pass")
)

def ingest_iso22301():
    with driver.session() as session:
        # Standard
        session.run("""
            CREATE (s:Standard {
                id: 'ISO22301:2019',
                name: 'ISO 22301:2019',
                title: 'Security and resilience - Business continuity management systems',
                type: 'international_standard',
                published: date('2019-10-31')
            })
        """)
        
        # Clauses (упрощенная версия)
        clauses = [
            {"id": "4", "title": "Context of the organization", "parent": None},
            {"id": "4.1", "title": "Understanding the organization and its context", "parent": "4"},
            {"id": "5", "title": "Leadership", "parent": None},
            {"id": "6", "title": "Planning", "parent": None},
            {"id": "6.1", "title": "Actions to address risks and opportunities", "parent": "6"},
            {"id": "7", "title": "Support", "parent": None},
            {"id": "8", "title": "Operation", "parent": None},
            {"id": "8.2", "title": "Business impact analysis and risk assessment", "parent": "8"},
            {"id": "8.2.2", "title": "Business impact analysis", "parent": "8.2"},
            {"id": "8.3", "title": "Business continuity strategy", "parent": "8"},
            {"id": "8.4", "title": "Business continuity procedures", "parent": "8"},
            {"id": "8.4.4", "title": "Business continuity plans and procedures", "parent": "8.4"},
            {"id": "9", "title": "Performance evaluation", "parent": None},
            {"id": "10", "title": "Improvement", "parent": None}
        ]
        
        for clause in clauses:
            session.run("""
                MATCH (s:Standard {id: 'ISO22301:2019'})
                CREATE (c:Clause {
                    id: $id,
                    title: $title,
                    parent: $parent
                })
                CREATE (s)-[:HAS_CLAUSE]->(c)
            """, **clause)
        
        # Requirements (примеры для 8.2.2)
        requirements = [
            {
                "clause": "8.2.2",
                "req_id": "8.2.2.a",
                "text": "The organization shall conduct a BIA to identify critical activities and their dependencies",
                "type": "mandatory"
            },
            {
                "clause": "8.2.2",
                "req_id": "8.2.2.b",
                "text": "Determine impact over time of disruption to critical activities",
                "type": "mandatory"
            },
            {
                "clause": "8.2.2",
                "req_id": "8.2.2.c",
                "text": "Establish prioritized timeframes (RTO, RPO, MTPD)",
                "type": "mandatory"
            }
        ]
        
        for req in requirements:
            session.run("""
                MATCH (c:Clause {id: $clause})
                CREATE (r:Requirement {
                    id: $req_id,
                    text: $text,
                    type: $type
                })
                CREATE (c)-[:HAS_REQUIREMENT]->(r)
            """, **req)
        
        print("✅ ISO 22301 ingested successfully")

if __name__ == "__main__":
    ingest_iso22301()
    driver.close()
```

### Phase 4: Core Platform Services (День 3-4)

**Порядок запуска (важен!):**

```bash
# 1. EventBus (первым - все от него зависят)
cd services/eventbus
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# Должен запуститься на :8001

# Verify:
curl http://localhost:8001/health
# {"status": "healthy"}

# 2. Orchestrator (вторым)
cd ../orchestrator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8002

curl http://localhost:8002/health

# 3. API Gateway (третьим)
cd ../api_gateway
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8000

curl http://localhost:8000/health
```

### Phase 5: Domain Services (День 4-7)

**Запускать в порядке зависимостей:**

```bash
# 1. Governance (не зависит ни от кого)
cd services/governance
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8010

# Test: создать организацию
curl -X POST http://localhost:8000/api/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Hospital",
    "industry": "healthcare",
    "size": "medium"
  }'

# 2. BIA (зависит от Governance)
cd ../bia
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8011

# Test: начать BIA
curl -X POST http://localhost:8000/api/bia/start \
  -H "Content-Type: application/json" \
  -d '{"org_id": "org_id_from_previous_step"}'

# 3. Risk (зависит от BIA)
cd ../risk
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8013

# 4. Planning (зависит от BIA + Risk)
cd ../planning
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8015

# 5. Response
cd ../response
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8016

# 6. Compliance
cd ../compliance
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8018

# 7. Documents
cd ../documents
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8019

# 8. Training
cd ../training
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
# :8020
```

**Verify все сервисы:**
```bash
# Проверить Service Registry в Orchestrator
curl http://localhost:8002/services

# Должны видеть все зарегистрированные сервисы с status "healthy"
```

### Phase 6: Intelligence Layer (День 8-10)

```bash
# 1. Knowledge Graph Service
cd services/knowledge_graph
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# Test query
curl http://localhost:8000/api/knowledge-graph/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (c:Clause {id: \"8.2.2\"}) RETURN c"
  }'

# 2. Case Library Service
cd ../case_library
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# Verify case collector subscribing to events
# Должны видеть в логах: "Subscribed to workflow events"

# 3. ML Predictor (initial training - нет данных пока)
cd ../ml_predictor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

# 4. AI Experts
cd ../../ai_experts/bcm_advisor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

cd ../compliance_auditor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &

cd ../strategic_advisor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py &
```

**Test AI Expert:**
```bash
# Test BIA Advisor
curl -X POST http://localhost:8000/api/ai/bia/bia_123/advice \
  -H "Content-Type: application/json"

# Должен вернуть advice (возможно с placeholder данными если BIA пустой)
```

### Phase 7: Frontend (День 11-12)

```bash
cd frontend/bcm-platform

# Install dependencies
npm install

# Start development server
npm run dev

# Открыть http://localhost:3000
```

**Verify integration:**
1. Зарегистрировать пользователя
2. Создать организацию
3. Начать BIA
4. Добавить процесс
5. Проверить что AI Advisor показывает advice

### Phase 8: MCP Interface (День 13-14)

```bash
cd interfaces/mcp

# Install MCP SDK
pip install mcp

# Start MCP server
python mcp_server.py

# Подключить к Claude Desktop:
# ~/.claude/config.json:
{
  "mcpServers": {
    "bcm-platform": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

**Test в Claude Desktop:**
```
User: "Recommend RTO for Emergency Department in my hospital"
Claude: [использует bcm-platform MCP tool]
```

---

## 9. СТАНДАРТЫ КОДА

### 9.1 Service Template

**Каждый сервис следует единой структуре:**

```python
# services/{service_name}/main.py

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from shared.database import get_db
from shared.eventbus import EventBusClient
from shared.orchestrator import OrchestratorClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await orchestrator.register_service(
        name=SERVICE_NAME,
        port=SERVICE_PORT,
        health_check_url="/health"
    )
    
    await eventbus.subscribe(
        service=SERVICE_NAME,
        topics=get_subscribed_topics()
    )
    
    yield
    
    # Shutdown
    await orchestrator.unregister_service(SERVICE_NAME)
    await eventbus.unsubscribe(SERVICE_NAME)

app = FastAPI(
    title=f"{SERVICE_NAME} Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": "1.0.0"
    }

@app.get("/ready")
async def ready():
    # Check dependencies
    db_ok = await check_database()
    eventbus_ok = await check_eventbus()
    
    return {
        "ready": db_ok and eventbus_ok,
        "checks": {
            "database": db_ok,
            "eventbus": eventbus_ok
        }
    }

# Include routers
from api.routes import router
app.include_router(router, prefix=f"/{SERVICE_NAME}")
```

### 9.2 Domain Models (Pydantic)

```python
# services/{service_name}/models/domain.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProcessTier(str, Enum):
    TIER_1 = "tier_1"  # Critical
    TIER_2 = "tier_2"  # Important
    TIER_3 = "tier_3"  # Normal
    TIER_4 = "tier_4"  # Low priority

class BusinessProcess(BaseModel):
    id: Optional[str] = None
    org_id: str = Field(..., description="Organization ID")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    owner: str = Field(..., description="Process owner")
    tier: ProcessTier
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "org_id": "org_123",
                "name": "Emergency Department",
                "description": "24/7 emergency care services",
                "owner": "Dr. John Smith",
                "tier": "tier_1"
            }
        }
```

### 9.3 Database Models (SQLAlchemy)

```python
# services/{service_name}/models/database.py

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from shared.database.base import Base, TenantMixin, TimestampMixin
import uuid
from datetime import datetime

class BusinessProcessDB(Base, TenantMixin, TimestampMixin):
    __tablename__ = "business_processes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String)
    owner = Column(String(255), nullable=False)
    tier = Column(
        Enum('tier_1', 'tier_2', 'tier_3', 'tier_4', name='process_tier'),
        nullable=False
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_process_org_tier', 'org_id', 'tier'),
    )
```

### 9.4 Repository Pattern

```python
# services/{service_name}/repositories/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from models.database import BusinessProcessDB
from models.domain import BusinessProcess

class BIARepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_process(
        self,
        process: BusinessProcess
    ) -> str:
        """Create new business process"""
        db_process = BusinessProcessDB(
            **process.dict(exclude={'id', 'created_at', 'updated_at'})
        )
        self.session.add(db_process)
        await self.session.commit()
        await self.session.refresh(db_process)
        return str(db_process.id)
    
    async def get_process(
        self,
        process_id: str
    ) -> Optional[BusinessProcess]:
        """Get process by ID"""
        result = await self.session.execute(
            select(BusinessProcessDB)
            .where(BusinessProcessDB.id == process_id)
        )
        db_process = result.scalar_one_or_none()
        
        if not db_process:
            return None
        
        return BusinessProcess.from_orm(db_process)
    
    async def list_processes(
        self,
        org_id: str,
        tier: Optional[str] = None
    ) -> List[BusinessProcess]:
        """List all processes for organization"""
        query = select(BusinessProcessDB).where(
            BusinessProcessDB.org_id == org_id
        )
        
        if tier:
            query = query.where(BusinessProcessDB.tier == tier)
        
        result = await self.session.execute(query)
        db_processes = result.scalars().all()
        
        return [BusinessProcess.from_orm(p) for p in db_processes]
```

### 9.5 Service Layer

```python
# services/{service_name}/services/business_logic.py

from repositories.repository import BIARepository
from shared.eventbus import EventBusClient
from datetime import datetime

class BIAService:
    def __init__(
        self,
        repository: BIARepository,
        eventbus: EventBusClient
    ):
        self.repo = repository
        self.eventbus = eventbus
    
    async def add_process(
        self,
        bia_id: str,
        process: ProcessCreate
    ) -> str:
        """Business logic for adding process"""
        
        # Validation
        if not process.name:
            raise ValueError("Process name required")
        
        # Check duplicates
        existing = await self.repo.find_by_name(
            bia_id, process.name
        )
        if existing:
            raise ValueError(f"Process '{process.name}' already exists")
        
        # Save
        process_id = await self.repo.create_process(bia_id, process)
        
        # Publish event
        await self.eventbus.publish("bia.process.added", {
            "bia_id": bia_id,
            "process_id": process_id,
            "process_data": process.dict(),
            "timestamp": datetime.now().isoformat()
        })
        
        return process_id
```

### 9.6 API Routes

```python
# services/{service_name}/api/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.domain import BusinessProcess, ProcessCreate
from services.business_logic import BIAService
from shared.auth import get_current_user

router = APIRouter()

@router.post(
    "/processes",
    response_model=dict,
    status_code=status.HTTP_201_CREATED
)
async def create_process(
    bia_id: str,
    process: ProcessCreate,
    service: BIAService = Depends(get_bia_service),
    user = Depends(get_current_user)
):
    """
    Create new business process
    
    - **bia_id**: BIA session ID
    - **process**: Process data
    
    Returns process ID
    """
    try:
        process_id = await service.add_process(bia_id, process)
        return {
            "process_id": process_id,
            "message": "Process created successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/processes",
    response_model=List[BusinessProcess]
)
async def list_processes(
    bia_id: str,
    tier: Optional[str] = None,
    service: BIAService = Depends(get_bia_service),
    user = Depends(get_current_user)
):
    """
    List all processes for BIA
    
    - **bia_id**: BIA session ID
    - **tier**: Optional filter by tier
    """
    processes = await service.list_processes(bia_id, tier)
    return processes
```

### 9.7 Event Publishing

```python
# services/{service_name}/events/publishers.py

from shared.eventbus import EventBusClient
from typing import Any, Dict

class BIAEventPublisher:
    def __init__(self, eventbus: EventBusClient):
        self.eventbus = eventbus
    
    async def publish_process_added(
        self,
        bia_id: str,
        process_id: str,
        process_data: Dict[str, Any]
    ):
        """Publish process added event"""
        await self.eventbus.publish(
            topic="bia.process.added",
            data={
                "bia_id": bia_id,
                "process_id": process_id,
                "process": process_data,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def publish_workflow_action(
        self,
        org_id: str,
        action: str,
        data: Dict[str, Any]
    ):
        """Publish workflow action for Case Collector"""
        await self.eventbus.publish(
            topic="bia.workflow.action.taken",
            data={
                "org_id": org_id,
                "module": "bia",
                "action": action,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        )
```

### 9.8 Event Subscribing

```python
# services/{service_name}/events/subscribers.py

from shared.eventbus import EventBusClient, Event
from services.business_logic import BIAService

class BIAEventSubscriber:
    def __init__(
        self,
        eventbus: EventBusClient,
        service: BIAService
    ):
        self.eventbus = eventbus
        self.service = service
    
    async def start(self):
        """Start subscribing to events"""
        await self.eventbus.subscribe(
            topics=["governance.organization.created"],
            handler=self.handle_event
        )
    
    async def handle_event(self, event: Event):
        """Route event to appropriate handler"""
        if event.topic == "governance.organization.created":
            await self.on_organization_created(event)
    
    async def on_organization_created(self, event: Event):
        """Auto-create BIA template for new organization"""
        org_id = event.data["org_id"]
        industry = event.data["industry"]
        
        # Create BIA
        bia_id = await self.service.start_bia(org_id)
        
        # Add suggested processes
        suggested = get_default_processes_for_industry(industry)
        for process in suggested:
            await self.service.add_process(bia_id, process)
```

---

## 10. INTEGRATION PATTERNS

### 10.1 Synchronous (REST)

**Use case**: Immediate response needed

```typescript
// Frontend
const response = await fetch('/api/organizations', {
  method: 'POST',
  body: JSON.stringify(orgData)
});
const org = await response.json();
```

```python
# API Gateway proxies to service
@gateway.post("/api/organizations")
async def create_organization(org_data: dict):
    response = await httpx.post(
        f"{GOVERNANCE_URL}/organizations",
        json=org_data
    )
    return response.json()
```

### 10.2 Asynchronous (Events)

**Use case**: Multiple services need to react

```python
# Service A publishes
await eventbus.publish("bia.completed", {
    "org_id": "org_123",
    "bia_id": "bia_456",
    "critical_processes": [...]
})

# Service B subscribes
@eventbus.subscribe("bia.completed")
async def on_bia_completed(event):
    # Auto-start risk assessment
    await risk_service.create_assessment(event.data)

# Service C also subscribes
@eventbus.subscribe("bia.completed")
async def on_bia_completed(event):
    # Check ISO compliance
    await compliance_service.check_clause(event.data, "8.2.2")
```

### 10.3 Orchestrated (Workflow)

**Use case**: Multi-step business process

```python
@workflow.defn
class BIAProcessWorkflow:
    @workflow.run
    async def run(self, org_id: str):
        # Step 1
        await workflow.execute_activity(
            identify_processes,
            args=[org_id],
            timeout=timedelta(days=7)
        )
        
        # Step 2
        await workflow.execute_activity(
            analyze_dependencies,
            args=[org_id],
            timeout=timedelta(days=7)
        )
        
        # ... etc
```

---

## 11. ПРИМЕРЫ КОДА

### Complete BIA Workflow Example

```python
# User starts BIA → adds process → AI analyzes → completes BIA

# 1. User starts BIA
POST /api/bia/start
{
  "org_id": "hospital_001"
}

Response: {"bia_id": "bia_123", "status": "started"}

# BIA Service публикует:
eventbus.publish("bia.workflow.started", {...})

# 2. User adds process
POST /api/bia/bia_123/processes
{
  "name": "Emergency Department",
  "description": "24/7 emergency care",
  "owner": "Dr. Smith",
  "tier": "tier_1"
}

Response: {"process_id": "proc_456"}

# BIA Service:
- Saves process to DB
- Publishes "bia.process.added"
- Case Collector records action

# 3. User requests AI to analyze impact
POST /api/ai/bia/bia_123/analyze-impact
{
  "process_id": "proc_456"
}

# AI Expert:
- Gets workflow context (from BIA Service)
- Gets similar cases (from Case Library)
- Gets ISO guidance (from Knowledge Graph)
- LLM analyzes
- Returns impact assessment

Response: {
  "financial_impact": {...},
  "operational_impact": {...},
  "recommended_tier": "tier_1"
}

# 4. User determines RTO (AI assisted)
POST /api/ai/bia/bia_123/recommend-rto
{
  "process_id": "proc_456"
}

# AI Expert:
- Analyzes process criticality
- Checks industry benchmarks
- References similar successful cases
- Recommends RTO

Response: {
  "rto_hours": 0,
  "rationale": "Tier 1 critical, immediate availability required",
  "alternatives": [{rto: 1, risk: "high"}]
}

# 5. User completes BIA
POST /api/bia/bia_123/complete

# BIA Service:
- Validates all requirements met
- Updates workflow state to "completed"
- Publishes "bia.workflow.completed"

# EventBus broadcasts to:
- Risk Service → auto-creates risk assessments
- Planning Service → prepares strategy options
- Compliance Service → checks ISO 8.2.2 compliance
- Case Collector → compiles into workflow case
```

---

## 12. DEPLOYMENT CHECKLIST

### Development
- [ ] PostgreSQL running
- [ ] Redis running
- [ ] Neo4j running with data
- [ ] MinIO running
- [ ] All services started
- [ ] Frontend running
- [ ] Can create organization
- [ ] Can start BIA
- [ ] AI Advisor responds

### Staging
- [ ] Docker Compose deployed
- [ ] Environment variables set
- [ ] Database migrations applied
- [ ] Knowledge Graph populated
- [ ] SSL certificates configured
- [ ] Monitoring setup (Prometheus/Grafana)
- [ ] Load testing passed
- [ ] Backup strategy configured

### Production
- [ ] Kubernetes cluster ready
- [ ] Secrets managed (Vault/AWS Secrets Manager)
- [ ] Auto-scaling configured
- [ ] CDN for frontend
- [ ] Database replicas
- [ ] Disaster recovery plan
- [ ] Monitoring alerts configured
- [ ] Log aggregation (ELK)
- [ ] Performance baselines established

---

## 13. TROUBLESHOOTING

### Service не запускается
```bash
# Check logs
docker-compose logs -f service_name

# Check dependencies
curl http://localhost:5432  # PostgreSQL
redis-cli ping              # Redis
curl http://localhost:7474  # Neo4j

# Check EventBus
curl http://localhost:8001/health
```

### Events не доходят
```bash
# Check EventBus logs
docker-compose logs -f eventbus

# Manually publish test event
curl -X POST http://localhost:8001/publish \
  -H "Content-Type: application/json" \
  -d '{"topic": "test", "data": {}}'

# Check subscriber
# В логах сервиса должно быть: "Subscribed to topics: [...]"
```

### AI Advisor не отвечает
```bash
# Check AI Expert service
curl http://localhost:8000/api/ai/health

# Check LLM API keys
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Test direct LLM call
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model": "claude-sonnet-4", "messages": [{"role": "user", "content": "test"}]}'
```

---

# 🎯 ИТОГО: ПОЛНАЯ АРХИТЕКТУРА

Этот документ описывает:

✅ **5 слоев архитектуры** с четким разделением ответственности  
✅ **Все компоненты** от БД до MCP интерфейса  
✅ **Workflow State Machine** для контекстного AI  
✅ **Case Library** для самообучения платформы  
✅ **Алгоритм запуска снизу вверх** с конкретными командами  
✅ **Стандарты кода** для каждого типа компонента  
✅ **Integration patterns** (sync/async/orchestrated)  
✅ **Примеры кода** для всех ключевых flow  
✅ **Deployment checklist**  
✅ **Troubleshooting guide**

**MCP правильно** - это interface layer (способ доступа), не AI компонент  
**Сборка правильно** - снизу вверх (Data → Platform → Intelligence → Interface)

---
Отличный вопрос о размещении компонентов! Вижу 3 разных типа AI компонентов в твоих документах:

1. **Workflow Intelligence Engine** - это "мозг" платформы (state machine + case library + governance)
2. **AI Workflow Optimizer** - ML-сервис для предсказаний и оптимизации
3. **AI Intelligence Service** - 10 специализированных AI "органов" для BCM анализа
4. **MIO Manager** - управляющий центр с automation toolkit

Давай я правильно разложу их по архитектуре:

---

## 🏗️ ПРАВИЛЬНОЕ РАЗМЕЩЕНИЕ AI КОМПОНЕНТОВ

### INTELLIGENCE LAYER (Слой 3)

```
ai_intelligence/
│
├── ai_experts/              # AI WORKERS (бизнес-логика + AI)
│   │
│   ├── bcm_advisor/         # Основной BCM эксперт
│   │   ├── main.py
│   │   ├── advisors/
│   │   │   ├── bia_advisor.py
│   │   │   ├── risk_advisor.py
│   │   │   └── planning_advisor.py
│   │   └── tools/
│   │       ├── recommend_rto.py
│   │       ├── generate_plan.py
│   │       └── simulate_incident.py
│   │
│   ├── compliance_auditor/  # Compliance эксперт
│   │   ├── main.py
│   │   └── auditors/
│   │       ├── document_auditor.py
│   │       ├── clause_checker.py
│   │       └── gap_analyzer.py
│   │
│   └── strategic_advisor/   # Стратегический эксперт
│       ├── main.py
│       └── advisors/
│           ├── benchmark.py
│           └── roadmap.py
│
├── ai_services/             # AI SERVICE TOOLS (инструменты для workers)
│   │
│   ├── workflow_intelligence/    # ✅ Твой Workflow Intelligence Engine
│   │   ├── core/                 # State machine + validators
│   │   ├── case_library/         # Self-learning
│   │   ├── governance/           # Rules + creative zones
│   │   ├── ml/                   # Predictive models
│   │   └── schemas/
│   │
│   ├── ml_optimizer/             # ✅ Твой AI Workflow Optimizer
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── performance_predictor.py
│   │   │   ├── bottleneck_detector.py
│   │   │   └── anomaly_detector.py
│   │   └── training/
│   │
│   └── domain_organs/            # ✅ Твой AI Intelligence Service (10 organs)
│       ├── main.py
│       └── organs/
│           ├── governance_brain.py
│           ├── emergency_response.py
│           ├── impact_oracle.py
│           └── ... (остальные 7)
│
└── mcp_interface/           # MCP АДАПТЕРЫ (НЕ сервисы!)
    ├── mcp_server.py        # Тонкий адаптер к ai_experts
    └── adapters/
        ├── bcm_advisor_adapter.py
        └── compliance_adapter.py
```

---

## 📊 PLATFORM LAYER (Слой 2)

```
platform_services/
│
├── orchestration/
│   ├── orchestrator/        # Координация workflows
│   └── mio_manager/         # ✅ Твой MIO Manager (управление + мониторинг)
│       ├── main.py
│       ├── integrations/
│       │   ├── automation_toolkit.py
│       │   ├── orchestrator_client.py
│       │   └── gateway_manager.py
│       └── scheduler/
│           └── automation_jobs.py
│
└── ... (остальные platform сервисы)
```

---

## 🎯 КАК РАЗЛИЧАТЬ

### AI WORKER (в ai_experts/)
**Признаки:**
- Принимает бизнес-запросы от пользователей
- Имеет специализацию (BIA, Risk, Planning)
- Использует LLM для генерации контента
- Взаимодействует с платформой через API
- Публикует события в EventBus

**Примеры:**
- ✅ `bcm_advisor` - помогает с BIA/Risk/Planning
- ✅ `compliance_auditor` - проводит аудиты
- ✅ `strategic_advisor` - дает стратегические советы

### AI SERVICE TOOL (в ai_services/)
**Признаки:**
- Предоставляет **инструменты** для AI Workers
- НЕ взаимодействует с пользователями напрямую
- Переиспользуется несколькими workers
- Содержит shared logic/models

**Примеры:**
- ✅ `workflow_intelligence` - state machine для ВСЕХ workflows
- ✅ `ml_optimizer` - ML модели для ВСЕХ предсказаний
- ✅ `domain_organs` - 10 специализированных "органов" используемых разными workers

---

## 🔄 ВЗАИМОДЕЙСТВИЕ

```
USER запрашивает совет по BIA
       ↓
API Gateway → bcm_advisor (AI WORKER)
       ↓
bcm_advisor использует:
   1. workflow_intelligence (SERVICE TOOL) → получить workflow state
   2. ml_optimizer (SERVICE TOOL) → получить предсказание
   3. domain_organs/impact_oracle (SERVICE TOOL) → проанализировать impact
   4. case_library (SERVICE TOOL) → найти similar cases
       ↓
bcm_advisor комбинирует все → генерирует advice через LLM
       ↓
Response пользователю
```

---

## 📝 КОНКРЕТНОЕ РАЗМЕЩЕНИЕ ТВОИХ КОМПОНЕНТОВ

### 1. Workflow Intelligence Engine
**Размещение:** `ai_intelligence/ai_services/workflow_intelligence/`

**Почему:** Это SERVICE TOOL потому что:
- Используется всеми AI workers (bcm_advisor, compliance_auditor)
- Предоставляет state machine логику
- Не взаимодействует с пользователями напрямую
- Shared governance rules

**Структура:**
```
workflow_intelligence/
├── core/                    # State machine engine
├── case_library/            # Self-learning repository
├── governance/              # Rules + creative zones
├── ml/                      # Predictive models
└── schemas/                 # Data models
```

### 2. AI Workflow Optimizer
**Размещение:** `ai_intelligence/ai_services/ml_optimizer/`

**Почему:** Это SERVICE TOOL потому что:
- ML модели используются разными workers
- Не принимает пользовательские запросы
- Предоставляет predictions для других компонентов

**Переименовать в:** `ml_optimizer` (более понятное название)

### 3. AI Intelligence Service (10 organs)
**Размещение:** `ai_intelligence/ai_services/domain_organs/`

**Почему:** Это SERVICE TOOL потому что:
- 10 "органов" - это специализированные инструменты
- Используются AI workers для анализа
- Не взаимодействуют с пользователями напрямую

**Переименовать в:** `domain_organs` и интегрировать:
```python
# bcm_advisor использует organs

from domain_organs import ImpactOracle, RiskAdvisor, ScenarioCreator

class BIAAdvisor:
    def __init__(self):
        self.impact_oracle = ImpactOracle()
        self.risk_advisor = RiskAdvisor()
        self.scenario_creator = ScenarioCreator()
    
    async def analyze_process(self, process):
        # Использовать organs для анализа
        impact = await self.impact_oracle.predict_impact(process)
        risks = await self.risk_advisor.identify_risks(process)
        scenarios = await self.scenario_creator.generate_scenarios(process)
        
        # Комбинировать в advice
        return self.generate_advice(impact, risks, scenarios)
```

### 4. MIO Manager
**Размещение:** `platform_services/orchestration/mio_manager/`

**Почему:** Это PLATFORM SERVICE потому что:
- Управляет другими сервисами (не AI логика)
- Координирует automation toolkit
- Мониторинг и observability
- Делегирует задачи orchestrator

**НЕ AI компонент**, а управляющий сервис.

---

## 🏗️ ИТОГОВАЯ СТРУКТУРА

```
/Users/MD/AI-Platform-ISO/

├── platform_services/           # PLATFORM LAYER
│   ├── orchestration/
│   │   ├── orchestrator/
│   │   └── mio_manager/         # ✅ MIO Manager здесь
│   ├── api_gateway/
│   ├── eventbus/
│   └── ... (domain services)
│
├── ai_intelligence/             # INTELLIGENCE LAYER
│   │
│   ├── ai_experts/              # AI WORKERS
│   │   ├── bcm_advisor/
│   │   ├── compliance_auditor/
│   │   └── strategic_advisor/
│   │
│   ├── ai_services/             # AI SERVICE TOOLS
│   │   ├── workflow_intelligence/  # ✅ Workflow Intelligence Engine
│   │   ├── ml_optimizer/           # ✅ AI Workflow Optimizer
│   │   └── domain_organs/          # ✅ 10 AI Organs
│   │
│   └── mcp_interface/           # MCP АДАПТЕРЫ
│       └── mcp_server.py
│
├── data_layer/                  # DATA LAYER
│   ├── postgres/
│   ├── neo4j/
│   └── vector_db/
│
└── interface_layer/             # INTERFACE LAYER
    ├── frontend/
    └── ... (other interfaces)
```

---

## ✅ КРИТЕРИИ РАЗДЕЛЕНИЯ

| Компонент | AI Worker | AI Service Tool | Platform Service |
|-----------|-----------|-----------------|------------------|
| **Принимает user requests** | ✅ Да | ❌ Нет | ✅ Да |
| **Использует LLM** | ✅ Да | ⚠️ Может | ❌ Нет |
| **Специализирован** | ✅ Да (BIA/Risk) | ✅ Да (tools) | ❌ Нет |
| **Переиспользуется** | ❌ Нет | ✅ Да | ❌ Нет |
| **Управляет другими** | ❌ Нет | ❌ Нет | ✅ Да |

**Примеры:**
- `bcm_advisor` → AI Worker (специализирован на BIA/Risk)
- `workflow_intelligence` → AI Service Tool (используется всеми workers)
- `mio_manager` → Platform Service (управляет сервисами)

---

Правильно разложить компоненты критически важно для:
1. ✅ Переиспользования кода
2. ✅ Масштабирования
3. ✅ Понятной архитектуры
4. ✅ Легкого тестирования
