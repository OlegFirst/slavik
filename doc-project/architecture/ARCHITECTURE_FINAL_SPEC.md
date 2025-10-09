# AI-POWERED BCM PLATFORM - FINAL ARCHITECTURE SPECIFICATION

Version: 1.0
Date: 2025-10-04
Status: Foundation Document

---

## DOCUMENT PURPOSE

This is the SINGLE SOURCE OF TRUTH for the AI-Powered BCM Platform architecture.

**What this document contains:**
- Complete system architecture
- All components and their responsibilities
- Data flow and integration patterns
- Technical specifications for each layer
- What exists vs what needs to be built

**Who uses this:**
- Development teams (human + AI agents)
- Project coordinator (MD)
- Future maintainers
- Integration partners

---

## ARCHITECTURE PHILOSOPHY

### Core Principles

**1. AI-First, Not AI-Added**
AI is integrated into the workflow engine core, not bolted on top. Every business process has AI context awareness.

**2. Self-Learning Platform**
The platform learns from every successful workflow completion, building a case library that improves advice over time.

**3. Managed Autonomy**
AI has creative freedom within governance boundaries:
- Rules Engine defines safety rails
- Checkpoints ensure mandatory validations
- Creative Zones allow AI decision-making

**4. Event-Driven Architecture**
Services communicate through events, not direct calls. Enables:
- Loose coupling
- Easy service addition/removal
- Audit trail
- Async processing

**5. ISO 22301 Native**
Platform structure maps directly to ISO 22301 PDCA cycle and clause requirements.

---

## SYSTEM LAYERS

```
┌─────────────────────────────────────────────────────────┐
│                 LAYER 1: INFRASTRUCTURE                 │
│  Database │ Cache │ Message Queue │ Knowledge Graph    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              LAYER 2: PLATFORM SERVICES                 │
│  EventBus │ API Gateway │ Auth │ Monitoring            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│               LAYER 3: BCM CORE SERVICES                │
│  BIA │ Risk │ Governance │ Planning │ Response │ ...   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│            LAYER 4: INTELLIGENCE LAYER                  │
│  Workflow Intelligence │ AI Organs │ Case Library      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                LAYER 5: USER INTERFACES                 │
│  Web App │ API │ MCP Tools │ Mobile (future)           │
└─────────────────────────────────────────────────────────┘
```

---

## LAYER 1: INFRASTRUCTURE

### Purpose
Foundation services that all other layers depend on.

### Components

#### 1.1 PostgreSQL (Supabase)
**Status:** Deployed, partially migrated (024/033)
**Connection:** Cloud (aws-1-eu-north-1.pooler.supabase.com)

**Databases:**
- `postgres` - Main database (all schemas in one for MVP)

**Schemas:**
- `public` - BCM business data
- `auth` - Supabase auth
- `platform` - Platform-level data
- `system` - AI and intelligence data

**Migration Status:**
- Applied: 001-024 (policies, security, RLS)
- Pending: 025-033 (admin users, final security fixes)

**Action Required:**
- Apply remaining 9 migrations
- Verify RLS policies

#### 1.2 Redis (Upstash)
**Status:** Deployed and configured
**Connection:** redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com

**Usage:**
- Session storage
- Cache layer
- Rate limiting
- Event bus temporary storage
- Real-time WebSocket state

#### 1.3 Neo4j
**Status:** Not deployed
**Purpose:** Knowledge Graph for ISO 22301, BCI guidelines, regulations

**Data to Store:**
- ISO 22301:2019 clauses and requirements
- BCI Good Practice Guidelines
- Industry best practices
- Regulatory requirements
- Cross-references between standards

**Action Required:**
- Deploy Neo4j (Docker or Aura Cloud)
- Run initialization script (ingest ISO 22301)

#### 1.4 RabbitMQ
**Status:** Code ready, not deployed
**Purpose:** Message queue for EventBus

**Features:**
- Persistent message storage
- Dead letter queues
- Event replay capability
- Guaranteed delivery

**Action Required:**
- Deploy RabbitMQ container
- Configure exchanges and queues

---

## LAYER 2: PLATFORM SERVICES

### Purpose
Cross-cutting concerns that all BCM services use.

### Components

#### 2.1 EventBus
**Location:** `/infrastructure/event-bus/`
**Status:** Code complete (930 lines)
**Port:** 8001

**Features:**
- FastAPI REST API
- WebSocket support for real-time
- Redis pub/sub
- RabbitMQ integration with fallback
- Event history storage
- Subscription management

**API Endpoints:**
```
POST   /publish              - Publish event
POST   /subscribe            - Subscribe to topics
GET    /events/{tenant_id}   - Get event history
WS     /ws                   - WebSocket stream
GET    /health               - Health check
```

**Integration:**
```python
from shared.eventbus import EventBusClient

eventbus = EventBusClient(url="http://localhost:8001")

await eventbus.publish("bia.process.added", {
    "bia_id": "...",
    "process": {...}
})

await eventbus.subscribe(
    topics=["bia.completed"],
    handler=on_bia_completed
)
```

#### 2.2 API Gateway
**Location:** `/human-interface/api-gateway/`
**Status:** Code complete (272 lines)
**Port:** 3001

**Responsibilities:**
- Single entry point for all API requests
- JWT authentication
- Rate limiting
- Request routing to services
- CORS handling

**Routes:**
```
/api/v1/ai/*       → Intelligent Core (port 9000)
/api/v1/bcm/*      → BCM Services (various ports)
/api/v1/auth/*     → Auth service
/ws                → WebSocket proxy
```

#### 2.3 Shared Libraries
**Location:** `/shared/`
**Status:** 51 files, production ready

**Modules:**
- `auth/` - JWT, permissions, RLS helpers
- `database/` - Connection management, models
- `cache/` - Redis caching decorators
- `eventbus/` - EventBus client
- `audit/` - Audit logging
- `monitoring/` - Health checks, metrics
- `middleware/` - Error handling, logging

**Usage:**
```python
from shared.auth import get_current_user, require_permission
from shared.cache import cache_result
from shared.database import get_db
from shared.eventbus import get_eventbus
```

---

## LAYER 3: BCM CORE SERVICES

### Purpose
Business logic for ISO 22301 BCM implementation.

### Service Architecture Pattern

All BCM services follow this structure:
```
service-name/
├── main.py                   # FastAPI app with lifespan
├── config.py                 # Pydantic settings
├── api/
│   └── routes.py             # REST endpoints
├── models/
│   ├── domain.py             # Pydantic models
│   └── database.py           # SQLAlchemy models
├── services/
│   └── business_logic.py     # Core logic
├── repositories/
│   └── repository.py         # Data access
├── events/
│   ├── publishers.py         # Event publishing
│   └── subscribers.py        # Event handling
└── tests/
    └── test_*.py             # Test suite
```

### Services

#### 3.1 BIA Service
**Port:** 8011
**ISO Clause:** 8.2.2
**Status:** Complete with Workflow Intelligence integrated

**Features:**
- Business process identification
- Dependency analysis
- Impact assessment (financial, operational, reputational)
- Recovery time objectives (RTO, RPO, MTPD)
- Supply chain integration
- Workflow Intelligence integration

**Unique:** Only service currently integrated with Workflow Intelligence Engine.

#### 3.2 Risk Service
**Port:** 8012
**ISO Clause:** 8.2.3
**Status:** Complete

**Features:**
- Risk identification
- Risk assessment (likelihood, impact)
- FAIR quantitative analysis
- Monte Carlo simulation
- Risk treatment plans
- Risk register

#### 3.3 Governance Service
**Port:** 8020
**ISO Clauses:** 4, 5, 6
**Status:** Complete

**Features:**
- BCM policy management
- Scope definition
- Stakeholder management
- Roles and responsibilities
- Objectives and KPIs

#### 3.4 Planning Service
**Port:** 8021
**ISO Clause:** 8.3
**Status:** Complete

**Features:**
- Business continuity strategy
- Resource requirements
- Response structure
- Strategy evaluation

#### 3.5 Plans Service
**Port:** 8022
**ISO Clause:** 8.4
**Status:** Complete

**Features:**
- BC plan creation
- Incident response procedures
- Recovery procedures
- Communication plans
- Plan versioning

#### 3.6 Response Service
**Port:** 8023
**ISO Clause:** 8.4
**Status:** Complete

**Features:**
- Incident declaration
- Activation procedures
- Crisis management team
- Communication management
- Resource mobilization

#### 3.7 Validation Service
**Port:** TBD (suggest 8025)
**ISO Clause:** 8.5, 9.1
**Status:** Complete

**Features:**
- Exercise planning and execution
- Test scenarios
- Performance monitoring
- KPI tracking
- Corrective actions (CAPA)

#### 3.8 Compliance Service
**Port:** 8024
**ISO Clause:** 9.2
**Status:** Complete

**Features:**
- Internal audit planning
- Audit execution
- Non-conformity management
- ISO 22301 gap analysis
- Compliance reporting

#### 3.9 Documents Service
**Port:** 8014
**ISO Clause:** 7.5
**Status:** Complete

**Features:**
- Document management
- Template library
- Version control
- Approval workflows
- Document generation

#### 3.10 Learning Service
**Port:** TBD (suggest 8026)
**ISO Clause:** 7.2
**Status:** Complete

**Features:**
- Training program management
- Competency tracking
- Awareness campaigns
- Training records
- Gamification

### Service Communication

**Synchronous (REST):**
- Used for: Immediate data retrieval
- Example: API Gateway → BIA Service

**Asynchronous (Events):**
- Used for: Cross-service reactions
- Example: BIA completed → Risk service auto-creates assessments

```python
# BIA Service publishes:
await eventbus.publish("bia.completed", {
    "org_id": "...",
    "bia_id": "...",
    "critical_processes": [...]
})

# Risk Service subscribes and reacts:
@eventbus.subscribe("bia.completed")
async def on_bia_completed(event):
    # Auto-create risk assessments for critical processes
    for process in event.data["critical_processes"]:
        await create_risk_assessment(process)
```

---

## LAYER 4: INTELLIGENCE LAYER

### Purpose
AI-powered intelligence and workflow management.

### 4.1 Workflow Intelligence Engine

**Location:** `/intelligent-core/workflow_intelligence/`
**Status:** Core complete (770 lines), extracted complete versions in `/EXTRACTED_FROM_SESSION/`

**Architecture:**
```
workflow_intelligence/
├── core/
│   └── workflow_engine.py        # State machine (335 lines)
├── workflows/
│   └── bia_workflow.py           # BIA implementation (450 lines)
├── case_library/
│   ├── models.py                 # Data models
│   ├── collector.py              # Auto-collection (667 lines)
│   └── repository.py             # Storage and search (750 lines)
├── ai/
│   └── context_advisor.py        # AI integration (637 lines)
├── adapters/
│   └── bia_adapter.py            # Service integration (150 lines)
└── governance/
    ├── rules_engine.py           # 13 rules (500 lines)
    ├── creative_zones.py         # 4 zones (280 lines)
    └── checkpoints.py            # 5 checkpoints (275 lines)
```

**Core Concepts:**

**State Machine:**
- Tracks current stage of workflow
- Validates transitions
- Publishes events on state changes
- Provides context for AI

**Case Library:**
- Automatically collects successful workflows
- Stores anonymized organization context
- Enables semantic search for similar cases
- Feeds ML predictor for success probability

**Governance System:**
```
Rules Engine (Safety Rails)
    ↓
Must follow ISO 22301 requirements
Must validate data completeness
Must check dependencies

Checkpoints (Mandatory Validation)
    ↓
5 points where human review required
Cannot proceed without approval

Creative Zones (AI Freedom)
    ↓
4 zones where AI can suggest creative solutions
Boundaries defined, AI chooses within them
```

### 4.2 AI Organs (Future Integration)

**Location:** `/intelligent-core/ai-office/`
**Status:** 10 organs implemented (85K+ lines total)

**Organs:**
1. Governance Brain - Policy and scope intelligence
2. Emergency Response - Incident intelligence
3. Impact Oracle - BIA intelligence
4. Scenario Creator - Testing scenario generation
5. Risk Advisor - Risk intelligence
6. Compliance Guardian - Audit intelligence
7. Performance Analyst - Metrics intelligence
8. Learning Coach - Training intelligence
9. Plan Generator - BC plan intelligence
10. Lifecycle Monitor - PDCA tracking

**Integration Strategy:**
- MVP: Use only Context Advisor (already in Workflow Intelligence)
- Phase 2: Integrate Impact Oracle with BIA
- Phase 3: Integrate Risk Advisor
- Phase 4: Integrate remaining organs

### 4.3 Community Intelligence (Extracted)

**Location:** `/EXTRACTED_FROM_SESSION/community_api_extracted.py`
**Status:** Complete implementation (500 lines)
**Purpose:** Community-driven best practice sharing

**Features:**
- Case contribution system
- Reputation and gamification
- Living documentation (annotations)
- Predictive timeline
- Community statistics

**Integration:** Phase 3 or later (not MVP critical)

---

## LAYER 5: USER INTERFACES

### 5.1 Web Application
**Technology:** Next.js 14 (App Router)
**Status:** Skeleton only

**Planned Pages:**
```
/                       - Dashboard
/bia                    - Business Impact Analysis
/risk                   - Risk Assessment
/plans                  - BC Plans
/incidents              - Incident Management
/compliance             - ISO 22301 Compliance
/ai-chat                - Conversational AI Interface
```

### 5.2 MCP Tools
**Purpose:** Claude integration via Model Context Protocol
**Status:** Design phase

**Planned Tools:**
```python
# Example MCP tool
mcp_tool("recommend_rto",
    description="Recommend RTO for business process",
    parameters={"process_id": "string"}
)
```

---

## DATA FLOW EXAMPLES

### Example 1: Create BIA with AI Advice

```
User → Web App
    ↓
    POST /api/v1/bcm/bia/start
    ↓
API Gateway → BIA Service (port 8011)
    ↓
BIA Service:
  - Creates BIA in database
  - Initializes Workflow Engine (state: "identify_processes")
  - Publishes event: "bia.workflow.started"
    ↓
EventBus broadcasts → Case Collector records workflow start
    ↓
User → Add process
    ↓
BIA Service:
  - Validates process data
  - Saves to database
  - Updates workflow state
  - Publishes event: "bia.process.added"
    ↓
User → Request AI advice
    ↓
BIA Service → Workflow Intelligence Context Advisor:
  - Get current workflow state
  - Get similar cases from Case Library
  - Get ISO 22301 guidance from Knowledge Graph
  - Get organization context
  - Build AI prompt
  - Call LLM (Claude/GPT-4)
  - Return contextual advice
    ↓
User sees AI advice with:
  - Current progress (e.g., "You're at stage 2/7")
  - What's needed next
  - Similar organization examples
  - ISO compliance tips
```

### Example 2: BIA Completion Triggers Risk Assessment

```
User → Complete BIA
    ↓
BIA Service:
  - Validates all requirements met
  - Updates state to "completed"
  - Publishes event: "bia.completed" {
      critical_processes: [...],
      recovery_objectives: {...}
    }
    ↓
EventBus broadcasts to all subscribers
    ↓
Risk Service (subscribed to "bia.completed"):
  - Auto-creates risk assessment
  - Pre-populates from BIA data
  - Notifies user: "Risk assessment ready"
    ↓
Planning Service (subscribed to "bia.completed"):
  - Prepares strategy options
  - Suggests resources needed
    ↓
Compliance Service (subscribed to "bia.completed"):
  - Checks ISO 8.2.2 compliance
  - Generates compliance report
    ↓
Case Collector (subscribed to all workflow events):
  - Compiles entire BIA journey into case
  - Anonymizes data
  - Stores in Case Library
  - Future users benefit from this workflow
```

---

## DEPLOYMENT ARCHITECTURE

### Development Environment

```yaml
# docker-compose.dev.yml

Infrastructure:
  - Supabase PostgreSQL (cloud) - already running
  - Upstash Redis (cloud) - already running
  - Neo4j (local docker) - needs deployment
  - RabbitMQ (local docker) - needs deployment

Platform Services:
  - EventBus (port 8001)
  - API Gateway (port 3001)

BCM Services:
  - BIA (8011), Risk (8012), Governance (8020)
  - Planning (8021), Plans (8022), Response (8023)
  - Compliance (8024), Documents (8014)
  - Validation (8025), Learning (8026)

Intelligence:
  - Workflow Intelligence (integrated in BIA for MVP)
  - AI Organs (future)

Frontend:
  - Next.js (port 3000)
```

### Production Environment

```
Load Balancer
    ↓
API Gateway (multiple instances)
    ↓
Service Mesh (Kubernetes)
    ↓
BCM Services (auto-scaled)
    ↓
Infrastructure (managed services)
```

---

## WHAT EXISTS VS WHAT NEEDS TO BE BUILT

### Ready to Deploy

**Infrastructure:**
- Database managers (6 files, 51KB)
- Shared libraries (51 files)
- EventBus service (930 lines)
- API Gateway (272 lines)

**BCM Services:**
- All 10 services have complete code
- All have main.py, routes, models, business logic
- All have test suites

**Intelligence:**
- Workflow Intelligence core (770 lines in repo)
- Complete extracted versions (3,441 lines in EXTRACTED_FROM_SESSION)

### Needs Configuration

**Infrastructure:**
- Apply database migrations 025-033
- Deploy Neo4j
- Deploy RabbitMQ
- Update .env files with service URLs

**Services:**
- Connect to database
- Connect to EventBus
- Configure inter-service URLs

### Needs Development

**Intelligence Integration:**
- Integrate Workflow Intelligence into all services (currently only BIA has it)
- Connect to Neo4j for Knowledge Graph queries
- Implement semantic search for Case Library

**Frontend:**
- Build Next.js pages
- Connect to API Gateway
- Implement real-time updates (WebSocket)

**AI Organs:**
- Decide which organs to integrate first
- Configure LLM API keys
- Implement organ-to-service connections

---

## INTEGRATION PRIORITIES

### MVP (Minimal Viable Product)

**Goal:** One complete workflow (BIA) working end-to-end with AI

**Includes:**
1. Infrastructure: PostgreSQL, Redis, EventBus
2. Platform: API Gateway, Auth
3. Services: BIA Service (with Workflow Intelligence)
4. Intelligence: Workflow Intelligence Engine, Context Advisor
5. Frontend: Basic BIA workflow UI

**Timeline:** 2-3 weeks

### Phase 2: Expand BCM Services

**Goal:** All 10 BCM services integrated

**Includes:**
1. Integrate Workflow Intelligence into remaining 9 services
2. Deploy Neo4j with ISO 22301 data
3. Enable cross-service event flows
4. Add Risk and Planning services to frontend

**Timeline:** 3-4 weeks

### Phase 3: Full Intelligence Layer

**Goal:** AI Organs active, Case Library learning

**Includes:**
1. Deploy selected AI Organs (Impact Oracle, Risk Advisor)
2. Implement semantic search for Case Library
3. Enable ML-based success prediction
4. Community Intelligence features

**Timeline:** 4-6 weeks

---

## TECHNICAL SPECIFICATIONS

### Programming Languages
- Backend: Python 3.11+
- Frontend: TypeScript/JavaScript (Next.js)
- Database: SQL (PostgreSQL)
- Knowledge Graph: Cypher (Neo4j)

### Frameworks & Libraries
- Backend: FastAPI, SQLAlchemy (async), Pydantic
- Frontend: Next.js 14, React 18, TailwindCSS
- Testing: pytest, pytest-asyncio
- AI: LangChain, OpenAI SDK, Anthropic SDK

### Database Schemas
- Total tables: 80-100 (estimated)
- RLS policies: All tables have tenant isolation
- Indexes: All foreign keys indexed
- Migrations: 33 total (024 applied, 009 pending)

### API Standards
- REST: OpenAPI 3.0 (all services auto-generate docs)
- Authentication: JWT tokens (Supabase Auth)
- Rate Limiting: Redis-based, per-tenant
- Versioning: /api/v1/... (all endpoints)

### Event Schema
```python
{
    "event_type": "bia.process.added",
    "tenant_id": "org_123",
    "timestamp": "2025-10-04T01:00:00Z",
    "data": {
        "bia_id": "bia_456",
        "process": {...}
    },
    "user_id": "user_789",
    "correlation_id": "uuid"
}
```

---

## SECURITY

### Authentication
- Supabase Auth (email/password, OAuth, MFA)
- JWT tokens (24h expiration)
- Refresh tokens (30 days)

### Authorization
- Row Level Security (RLS) on all tables
- Tenant isolation (org_id filtering)
- Role-based permissions

### Data Protection
- Encryption in transit (TLS/SSL)
- Encryption at rest (Supabase default)
- Secrets in environment variables
- API keys in secure storage

---

## MONITORING & OBSERVABILITY

### Metrics (Prometheus)
- Request rate, latency, errors
- Database query performance
- Cache hit rates
- Event processing lag

### Logs
- Structured JSON logging
- Centralized log aggregation
- Log levels: DEBUG, INFO, WARNING, ERROR

### Tracing
- Request tracing across services
- Correlation IDs
- Performance bottleneck identification

---

## CONCLUSION

This specification represents the complete architecture of the AI-Powered BCM Platform. It balances:
- What's already built (significant!)
- What needs configuration (manageable)
- What needs development (planned phases)

The platform is 65-70% complete in terms of code. The challenge is integration, not missing functionality.

**Next Steps:**
1. Complete infrastructure setup (migrations, Neo4j, RabbitMQ)
2. Create unified docker-compose
3. Test MVP workflow (BIA end-to-end)
4. Iterate and expand

---

**Document Owner:** Project Team
**Last Updated:** 2025-10-04
**Version:** 1.0 (Foundation)
