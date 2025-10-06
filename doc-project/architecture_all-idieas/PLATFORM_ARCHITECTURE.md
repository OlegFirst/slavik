# BCM Platform - Architecture Documentation

**Version:** 1.0
**Date:** October 3, 2025
**Status:** Final Architecture Design

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Three-Tier Architecture](#2-three-tier-architecture)
3. [Microservices Architecture](#3-microservices-architecture)
4. [AI Services Architecture](#4-ai-services-architecture)
5. [Integration Patterns](#5-integration-patterns)
6. [Module Structure](#6-module-structure)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Code Examples](#8-code-examples)

---

## 1. System Overview

### 1.1 Architectural Principles

The BCM Platform follows these core principles:

- **Domain-Driven Design (DDD)**: Each service represents a bounded context
- **Event-Driven Architecture (EDA)**: Services communicate via events, not direct calls
- **Microservices Pattern**: Independently deployable services
- **MCP Integration**: AI capabilities provided via Model Context Protocol

### 1.2 Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (REST API)
- Pydantic (validation)
- SQLAlchemy (ORM)
- Alembic (migrations)

**Data Storage:**
- PostgreSQL 15 (relational data)
- Redis 7 (cache + message queue)
- Neo4j 5 (knowledge graph)
- MinIO (S3-compatible storage)
- pgvector/Pinecone (vector embeddings)

**Communication:**
- HTTP/REST (synchronous)
- WebSocket (real-time)
- Redis Streams (asynchronous events)

**AI/ML:**
- LangChain (RAG orchestration)
- OpenAI/Anthropic (LLM)
- Pinecone/pgvector (embeddings)
- MCP (Model Context Protocol)

---

## 2. Three-Tier Architecture

### 2.1 System Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│  SYSTEM LAYER (Meta Intelligence)                       │
│  - Knowledge Graph (ISO/BCI/WHO standards)              │
│  - Vector Database (embeddings for RAG)                 │
│  - MCP Servers (AI experts)                             │
│  Purpose: Cross-organizational knowledge & AI           │
└─────────────────────────────────────────────────────────┘
                          ↓↑
┌─────────────────────────────────────────────────────────┐
│  PLATFORM LAYER (Business Logic)                        │
│  - API Gateway (:8000)                                  │
│  - Orchestrator (:8002)                                 │
│  - EventBus (:8001)                                     │
│  - 10+ BCM Domain Services                              │
│  Purpose: BCM business processes & workflows            │
└─────────────────────────────────────────────────────────┘
                          ↓↑
┌─────────────────────────────────────────────────────────┐
│  BUSINESS LAYER (User Data)                             │
│  - PostgreSQL (multi-tenant data)                       │
│  - S3/MinIO (documents)                                 │
│  - Marketplace (consultants - future)                   │
│  Purpose: Organization-specific data                    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Layer Responsibilities

**SYSTEM LAYER:**
- Shared knowledge across all organizations
- AI pattern recognition and learning
- Standard mappings (ISO 22301 ↔ ISO 27001 ↔ GDPR)
- Best practices and templates

**PLATFORM LAYER:**
- BCM business logic
- Workflow orchestration
- Service coordination
- Event distribution

**BUSINESS LAYER:**
- Tenant-specific data
- User management
- Document storage
- Audit trails

---

## 3. Microservices Architecture

### 3.1 Core Infrastructure Services

#### API Gateway (:8000)
**Responsibilities:**
- Authentication/Authorization (JWT)
- Rate limiting
- Request routing
- Response aggregation
- CORS handling

**Key Endpoints:**
```
POST   /api/auth/login
POST   /api/auth/register
GET    /api/organizations/{org_id}/context
POST   /api/bia/start
GET    /api/risks/{risk_id}
```

#### Orchestrator (:8002)
**Responsibilities:**
- Service discovery & health checks
- Workflow orchestration (Temporal.io)
- Task scheduling
- Distributed tracing

**Key Workflows:**
- `iso22301_implementation_workflow` (12 months)
- `bia_process_workflow` (2-4 weeks)
- `bc_plan_development_workflow` (4-8 weeks)

#### EventBus (:8001)
**Responsibilities:**
- Event publishing/subscription
- WebSocket server (real-time updates)
- Message queue (Redis Streams)
- Event persistence

**Event Topics:**
```
bcm.bia.started
bcm.bia.completed
bcm.risk.identified
bcm.plan.created
bcm.exercise.completed
bcm.compliance.gap_found
```

### 3.2 BCM Domain Services

#### 1. Governance Service (:8010)
**Domain:** Organizational context & leadership

**Models:**
- Organization
- Stakeholder
- Policy
- Objective
- Scope

**Key APIs:**
```
GET    /organizations
POST   /organizations
GET    /organizations/{id}/context
POST   /organizations/{id}/stakeholders
```

**Events Published:**
- `governance.organization.created`
- `governance.policy.approved`
- `governance.objective.set`

#### 2. BIA Service (:8011)
**Domain:** Business impact analysis

**Models:**
- BusinessProcess
- ImpactAssessment
- Dependency
- RTO/RPO/MTPD

**Key APIs:**
```
POST   /bia/start
GET    /bia/{bia_id}/status
POST   /bia/{bia_id}/processes
GET    /bia/{bia_id}/results
```

**Events Published:**
- `bia.process.analyzed`
- `bia.completed`
- `bia.rto.determined`

**Events Subscribed:**
- `governance.organization.created`

#### 3. Risk Management Service (:8013)
**Domain:** Risk identification & assessment

**Models:**
- Risk
- Threat
- Vulnerability
- Control
- RiskAssessment

**Key APIs:**
```
GET    /risks
POST   /risks
POST   /risks/{id}/assess
GET    /risks/{id}/treatment-plan
```

**Events Published:**
- `risk.identified`
- `risk.assessed`
- `risk.treatment.planned`

**Events Subscribed:**
- `bia.completed` (auto-start risk assessment)

#### 4. Planning Service (:8015)
**Domain:** BC strategy & plans

**Models:**
- BCStrategy
- BCPlan
- RecoveryProcedure
- Resource

**Key APIs:**
```
GET    /strategies
POST   /strategies
GET    /plans
POST   /plans
POST   /plans/{id}/validate
```

#### 5. Response Service (:8016)
**Domain:** Incident response & recovery

**Models:**
- Incident
- Response
- RecoveryAction
- StatusUpdate

**Key APIs:**
```
POST   /incidents
POST   /incidents/{id}/activate-plan
GET    /incidents/{id}/timeline
```

#### 6. Compliance & Audit Service (:8018)
**Domain:** ISO compliance tracking

**Models:**
- ComplianceStatus
- Audit
- Finding
- Evidence
- Certification

**Key APIs:**
```
GET    /compliance/status
GET    /compliance/gaps
POST   /audits
GET    /audits/{id}/report
```

#### 7. Documents Service (:8019)
**Domain:** Document management

**Models:**
- Document
- Version
- Template
- Approval

**Key APIs:**
```
GET    /documents
POST   /documents
PUT    /documents/{id}
POST   /documents/{id}/approve
```

#### 8. Training Service (:8020)
**Domain:** Competence & awareness

**Models:**
- TrainingProgram
- Course
- Competency
- Certificate

**Key APIs:**
```
GET    /training/programs
POST   /training/courses
POST   /training/enroll
```

### 3.3 Advanced Services

#### Digital Twin Service (:8050)
**Domain:** Organization digital representation

**Models:**
- OrganizationTwin
- ProcessTwin
- SystemTwin

**Key APIs:**
```
GET    /twins/{org_id}
POST   /twins/{org_id}/sync
GET    /twins/{org_id}/predictions
```

#### Simulation Service (:8051)
**Domain:** Scenario testing & simulation

**Models:**
- Scenario
- Simulation
- SimulationResult

**Key APIs:**
```
POST   /simulations
GET    /simulations/{id}/results
GET    /scenarios/library
```

---

## 4. AI Services Architecture

### 4.1 MCP Server Architecture

The platform uses **Model Context Protocol (MCP)** to provide AI capabilities:

```
┌────────────────────────────────────┐
│  USER INTERFACE                    │
│  - Claude Desktop                  │
│  - ChatGPT                         │
│  - Platform Embedded AI            │
└────────────┬───────────────────────┘
             │ MCP Protocol
      ┌──────▼──────┐
      │ MCP CLIENT  │
      └──────┬──────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼────────┐  ┌────▼──────────┐
│ BCM AI      │  │ Compliance    │
│ Expert      │  │ Auditor       │
│ MCP Server  │  │ MCP Server    │
└────┬────────┘  └────┬──────────┘
     │                │
     │ REST API       │
     │                │
┌────▼────────────────▼──────┐
│  BCM PLATFORM              │
│  (API Gateway :8000)       │
└────────────────────────────┘
```

### 4.2 MCP Servers

#### BCM AI Expert Server

**Tools:**
- `recommend_rto` - AI recommends RTO for business process
- `generate_bc_plan` - AI generates Business Continuity Plan
- `simulate_incident` - AI simulates incident scenario
- `answer_bcm_question` - General BCM Q&A

#### Compliance Auditor Server

**Tools:**
- `audit_documents` - AI audits all documents against standard
- `gap_analysis` - AI conducts gap analysis
- `check_clause_compliance` - Checks specific ISO clause

#### Knowledge Graph Navigator Server

**Tools:**
- `find_related_standards` - Finds related standards
- `map_requirements` - Maps requirements between standards

### 4.3 RAG (Retrieval-Augmented Generation)

**Knowledge Sources:**
- ISO 22301:2019 (clause by clause)
- BCI Good Practice Guidelines 7.0
- WHO Health Emergency BCM Framework
- Case studies
- Templates
- FAQs

**Pipeline:**
```
1. Preprocessing (chunking, metadata)
2. Embedding (text-embedding-3-large)
3. Vector Storage (Pinecone/pgvector)
4. Query-time Retrieval (semantic search)
5. Re-ranking (Cohere rerank)
6. LLM Generation (Claude/GPT-4)
```

---

## 5. Integration Patterns

### 5.1 Pattern: Request-Response (Synchronous)

**When to use:** CRUD operations, immediate responses needed

```
USER → Frontend → API Gateway → Service → Database → Response
```

**Example Flow:**
1. User clicks "Create Organization"
2. Frontend sends POST /api/organizations
3. API Gateway validates JWT
4. Routes to Governance Service
5. Service saves to PostgreSQL
6. Response returns to frontend

### 5.2 Pattern: Event-Driven (Asynchronous)

**When to use:** Cascading updates, multiple services need to react

```
Service A → EventBus → [Service B, Service C, Service D]
```

**Example: BIA Completed Event**

```
BIA Service
    │ publish "bia.completed"
    ▼
EventBus
    ├───► Risk Service (auto-start risk assessment)
    ├───► Planning Service (prepare strategy options)
    ├───► Compliance Service (check ISO clause 8.2.2)
    └───► Digital Twin (update twin state)
```

### 5.3 Pattern: Orchestrated Workflow

**When to use:** Multi-step business processes with dependencies

**Example: ISO 22301 Implementation (12 months)**

```
Phase 1: Context & Planning (Month 1-2)
  → Create context analysis
  → Set BC objectives

Phase 2: Analysis (Month 3-4)
  → Conduct BIA
  → Assess risks

Phase 3: Strategy & Plans (Month 5-7)
  → Develop strategies
  → Create BC plans

Phase 4: Implementation (Month 8-9)
  → Train staff

Phase 5: Testing (Month 10)
  → Conduct exercises

Phase 6: Audit Preparation (Month 11)
  → Internal audit
  → Management review

Phase 7: Certification (Month 12)
  → Readiness assessment
  → Certification audit
```

### 5.4 Pattern: Saga (Distributed Transaction)

**When to use:** Multi-service transaction with rollback capability

**Example: Create Organization with Full Setup**

Success flow:
```
1. Create Org → SUCCESS
2. Create BIA template → SUCCESS
3. Create default policies → SUCCESS
4. Assign admin user → SUCCESS
✅ Commit all
```

Failure flow:
```
1. Create Org → SUCCESS
2. Create BIA template → SUCCESS
3. Create default policies → FAILURE
❌ Rollback:
   - Delete BIA template
   - Delete Org
```

---

## 6. Module Structure

### 6.1 Standard Service Structure

Each service follows this structure:

```
service_name/
├── __init__.py
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration
├── models/
│   ├── __init__.py
│   ├── domain.py              # Domain models (Pydantic)
│   └── database.py            # SQLAlchemy models
├── api/
│   ├── __init__.py
│   ├── routes.py              # API endpoints
│   └── schemas.py             # Request/Response schemas
├── services/
│   ├── __init__.py
│   └── business_logic.py      # Core business logic
├── repositories/
│   ├── __init__.py
│   └── repository.py          # Data access layer
├── events/
│   ├── __init__.py
│   ├── publishers.py          # Event publishing
│   └── subscribers.py         # Event handling
├── migrations/                # Alembic migrations
│   └── versions/
├── tests/
│   ├── unit/
│   └── integration/
└── requirements.txt
```

### 6.2 Shared Libraries

```
shared/
├── __init__.py
├── database/
│   ├── __init__.py
│   ├── connection.py          # DB connection pool
│   └── base.py                # Base SQLAlchemy models
├── eventbus/
│   ├── __init__.py
│   ├── client.py              # EventBus client
│   ├── publisher.py           # Event publishing
│   └── subscriber.py          # Event subscription
├── orchestrator/
│   ├── __init__.py
│   └── client.py              # Orchestrator client
├── auth/
│   ├── __init__.py
│   ├── jwt.py                 # JWT handling
│   └── permissions.py         # RBAC
├── models/
│   ├── __init__.py
│   └── common.py              # Common Pydantic models
└── utils/
    ├── __init__.py
    ├── logging.py             # Structured logging
    └── metrics.py             # Prometheus metrics
```

### 6.3 Configuration Management

All services use consistent configuration:

```python
# shared/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str
    SERVICE_PORT: int

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20

    # Redis
    REDIS_URL: str

    # EventBus
    EVENTBUS_URL: str = "http://localhost:8001"

    # Orchestrator
    ORCHESTRATOR_URL: str = "http://localhost:8002"

    # AI
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    # Vector DB
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "bcm-knowledge"

    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 7. Deployment Architecture

### 7.1 Docker Compose Setup

```yaml
version: '3.8'

services:
  # Infrastructure
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: bcm_platform
      POSTGRES_USER: bcm
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  neo4j:
    image: neo4j:5-community
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  # Core Services
  api-gateway:
    build: ./api_gateway
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://bcm:${DB_PASSWORD}@postgres:5432/bcm_platform
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      - postgres
      - redis

  orchestrator:
    build: ./orchestrator
    ports:
      - "8002:8002"
    environment:
      DATABASE_URL: postgresql://bcm:${DB_PASSWORD}@postgres:5432/bcm_platform
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  eventbus:
    build: ./eventbus
    ports:
      - "8001:8001"
    environment:
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis

  # BCM Services
  governance:
    build: ./services/governance
    environment:
      DATABASE_URL: postgresql://bcm:${DB_PASSWORD}@postgres:5432/bcm_platform
      SERVICE_PORT: 8010
      EVENTBUS_URL: http://eventbus:8001
    depends_on:
      - postgres
      - eventbus

  bia:
    build: ./services/bia
    environment:
      DATABASE_URL: postgresql://bcm:${DB_PASSWORD}@postgres:5432/bcm_platform
      SERVICE_PORT: 8011
      EVENTBUS_URL: http://eventbus:8001
    depends_on:
      - postgres
      - eventbus

  risk:
    build: ./services/risk
    environment:
      DATABASE_URL: postgresql://bcm:${DB_PASSWORD}@postgres:5432/bcm_platform
      SERVICE_PORT: 8013
      EVENTBUS_URL: http://eventbus:8001
    depends_on:
      - postgres
      - eventbus

volumes:
  postgres_data:
  redis_data:
  neo4j_data:
  minio_data:
```

---

## 8. Code Examples

### 8.1 BCMService Base Class

All BCM services inherit from this base class:

```python
# shared/base_service.py

from abc import ABC, abstractmethod
from fastapi import FastAPI
from typing import List
import httpx

class BCMService(ABC):
    """Base class for all BCM services"""

    def __init__(self, service_name: str, port: int):
        self.app = FastAPI(title=service_name)
        self.service_name = service_name
        self.port = port
        self.orchestrator = OrchestrationClient()
        self.eventbus = EventBusClient()

        # Setup lifecycle hooks
        self.app.add_event_handler("startup", self.startup)
        self.app.add_event_handler("shutdown", self.shutdown)

    async def startup(self):
        """Register service with orchestrator on startup"""
        await self.orchestrator.register_service(
            name=self.service_name,
            port=self.port,
            health_check_url=f"http://localhost:{self.port}/health"
        )

        # Subscribe to events
        topics = self.get_subscribed_topics()
        if topics:
            await self.eventbus.subscribe(
                service=self.service_name,
                topics=topics
            )

    async def shutdown(self):
        """Unregister service on shutdown"""
        await self.orchestrator.unregister_service(self.service_name)

    @abstractmethod
    def get_subscribed_topics(self) -> List[str]:
        """Return list of event topics this service subscribes to"""
        pass
```

### 8.2 Event Publishing Pattern

```python
# Example: Publishing an event from BIA Service

from shared.eventbus import EventBusClient

eventbus = EventBusClient()

# Complete BIA and publish event
async def complete_bia(bia_id: str, org_id: str):
    # Business logic to complete BIA
    results = await bia_service.finalize_bia(bia_id)

    # Publish event
    await eventbus.publish(
        topic="bia.completed",
        data={
            "org_id": org_id,
            "bia_id": bia_id,
            "critical_processes": results.tier_1_processes,
            "rto_requirements": {
                "tier_1": 0,
                "tier_2": 4,
                "tier_3": 24
            },
            "timestamp": datetime.now().isoformat()
        }
    )

    return results
```

### 8.3 Event Subscription Pattern

```python
# Example: Risk Service subscribes to BIA completed event

from shared.eventbus import EventSubscriber

subscriber = EventSubscriber("risk")

@subscriber.on("bia.completed")
async def on_bia_completed(event: Event):
    """
    Auto-start risk assessment when BIA is completed
    """
    org_id = event.data["org_id"]
    critical_processes = event.data["critical_processes"]

    # Create risk assessment tasks for critical processes
    for process in critical_processes:
        await risk_service.start_risk_assessment(
            org_id=org_id,
            process_id=process["id"],
            process_name=process["name"],
            criticality=process["tier"]
        )

    logger.info(
        f"Started risk assessment for {len(critical_processes)} "
        f"critical processes in org {org_id}"
    )
```

### 8.4 Orchestrated Workflow Example

```python
# Example: ISO 22301 Implementation Workflow using Temporal

from temporalio import workflow
from datetime import timedelta

@workflow.defn
class ISO22301ImplementationWorkflow:
    """12-month ISO 22301 certification workflow"""

    @workflow.run
    async def run(self, org_id: str) -> dict:

        # Phase 1: Context & Planning (Month 1-2)
        context = await workflow.execute_activity(
            create_context_analysis,
            args=[org_id],
            start_to_close_timeout=timedelta(hours=24)
        )

        objectives = await workflow.execute_activity(
            set_bc_objectives,
            args=[org_id],
            start_to_close_timeout=timedelta(hours=48)
        )

        # Phase 2: Analysis (Month 3-4)
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

        risk_result = await workflow.execute_activity(
            assess_risks,
            args=[org_id, bia_result],
            start_to_close_timeout=timedelta(days=30)
        )

        # Phase 3: Strategy & Plans (Month 5-7)
        strategies = await workflow.execute_activity(
            develop_strategies,
            args=[org_id, bia_result, risk_result],
            start_to_close_timeout=timedelta(days=30)
        )

        await workflow.wait_condition(
            lambda: self.strategy_selected,
            timeout=timedelta(days=14)
        )

        plans = await workflow.execute_activity(
            create_bc_plans,
            args=[org_id, self.selected_strategy],
            start_to_close_timeout=timedelta(days=60)
        )

        # Continue through remaining phases...

        return {
            "status": "completed",
            "duration_months": 12
        }
```

### 8.5 Service Implementation Example (BIA Service)

```python
# services/bia/main.py

from fastapi import FastAPI, Depends
from shared.base_service import BCMService
from shared.eventbus import EventBusClient

class BIAServiceApp(BCMService):
    """BIA Service implementation"""

    def __init__(self):
        super().__init__(service_name="bia", port=8011)
        self.setup_routes()

    def get_subscribed_topics(self) -> List[str]:
        return ["governance.organization.created"]

    def setup_routes(self):
        @self.app.post("/bia/start")
        async def start_bia(
            org_id: str,
            bia_service: BIAService = Depends()
        ):
            """Start BIA process for organization"""
            bia_id = await bia_service.start_bia(org_id)

            await self.eventbus.publish(
                topic="bia.started",
                data={"org_id": org_id, "bia_id": bia_id}
            )

            return {"bia_id": bia_id, "status": "started"}

        @self.app.post("/bia/{bia_id}/complete")
        async def complete_bia(
            bia_id: str,
            bia_service: BIAService = Depends()
        ):
            """Complete BIA and publish results"""
            results = await bia_service.complete_bia(bia_id)

            await self.eventbus.publish(
                topic="bia.completed",
                data={
                    "bia_id": bia_id,
                    "org_id": results.org_id,
                    "critical_processes": results.tier_1_processes,
                    "rto_requirements": results.rto_summary
                }
            )

            return results

        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "service": "bia"}

# Create app instance
app = BIAServiceApp().app
```

### 8.6 Shared Configuration Pattern

```python
# .env file (each service has its own)
SERVICE_NAME=bia
SERVICE_PORT=8011

DATABASE_URL=postgresql://bcm:password@localhost:5432/bcm_platform
REDIS_URL=redis://localhost:6379

EVENTBUS_URL=http://localhost:8001
ORCHESTRATOR_URL=http://localhost:8002

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

JWT_SECRET=your-secret-key
```

```python
# services/bia/config.py

from shared.config import Settings

settings = Settings(
    SERVICE_NAME="bia",
    SERVICE_PORT=8011
)

# Use in service
DATABASE_URL = settings.DATABASE_URL
EVENTBUS_URL = settings.EVENTBUS_URL
```

### 8.7 MCP Server Example

```python
# mcp_servers/bcm_ai_expert.py

from mcp.server import Server
import httpx

server = Server("bcm-ai-expert")
platform_api = "http://localhost:8000/api"

@server.tool("recommend_rto")
async def recommend_rto(
    org_id: str,
    process_name: str
) -> dict:
    """
    AI recommends RTO for business process

    Args:
        org_id: Organization ID
        process_name: Name of business process

    Returns:
        {
            "recommended_rto": "0 hours",
            "rationale": "...",
            "alternatives": [...],
            "risks": [...]
        }
    """

    # 1. Get context from platform
    async with httpx.AsyncClient() as client:
        org_response = await client.get(
            f"{platform_api}/organizations/{org_id}/context"
        )
        org_context = org_response.json()

        bia_response = await client.get(
            f"{platform_api}/bia/{org_id}/results"
        )
        bia_data = bia_response.json()

    # 2. RAG: retrieve relevant knowledge
    knowledge = await rag_retrieve(
        query=f"RTO recommendations for {process_name} in {org_context['industry']}",
        sources=["iso22301", "bci_gpg", "case_studies"]
    )

    # 3. LLM analysis
    prompt = f"""
    Based on ISO 22301 and BCI Good Practice Guidelines:

    Organization: {org_context['name']}
    Industry: {org_context['industry']}
    Process: {process_name}
    Current BIA: {bia_data}

    Knowledge: {knowledge}

    Recommend appropriate RTO with detailed rationale.
    """

    recommendation = await llm_generate(
        prompt=prompt,
        model="claude-sonnet-4",
        structured_output=RTORecommendationSchema
    )

    # 4. Save back to platform
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{platform_api}/bia/{org_id}/rto",
            json={
                "process": process_name,
                "rto": recommendation.rto,
                "rationale": recommendation.rationale
            }
        )

    return recommendation.model_dump()
```

---

## Summary

This architecture provides:

1. **Modularity**: Each service is independently deployable
2. **Scalability**: Services can scale independently
3. **Flexibility**: Easy to add new services or modify existing ones
4. **Event-Driven**: Loose coupling via events
5. **AI-Powered**: MCP servers provide intelligent capabilities
6. **Standards-Based**: Follows DDD, microservices, and event-driven patterns

The platform supports both synchronous (REST) and asynchronous (events) communication, with orchestrated workflows for complex multi-step processes. AI capabilities are provided through MCP servers, allowing flexible integration with various AI interfaces while keeping data centralized in the platform.
