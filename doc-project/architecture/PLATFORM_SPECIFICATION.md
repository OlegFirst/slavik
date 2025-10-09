# 🏗️ AI Platform ISO - Technical Specification

**Version:** 1.0.0
**Date:** 2025-10-05
**Status:** In Development

---

## 📋 Overview

AI-powered Business Continuity Management (BCM) platform with:
- Multi-domain expert system (BCM, future: HR, Finance)
- BPMN 2.0 workflow engine with AI recommendations
- RAG-based knowledge retrieval (ISO 22301, BCI GPG)
- Digital Twin simulation
- Web-based user interface

---

## 🏛️ Architecture

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 3: Presentation                    │
│                     (human-interface)                       │
│  • Next.js Web App                                          │
│  • API Gateway (BFF)                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 2: Expertise Center                   │
│                   (intelligent-core)                        │
│  • Chief Executive (routes requests)                        │
│  • Domain Plugins (BCM, HR future, Finance future)          │
│  • Shared AI (RAG, ML, Learning)                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 1: Platform Core                      │
│                   (intelligent-core)                        │
│  • Workflow Engine (BPMN 2.0)                               │
│  • Case Library                                             │
│  • Learning System                                          │
│  • Coordination Center                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 LAYER 0: Infrastructure                     │
│  • Supabase (PostgreSQL + Storage + Auth)                   │
│  • Redis (Caching + Rate Limiting)                          │
│  • Event Bus (RabbitMQ/Redis Streams)                       │
│  • Monitoring (Prometheus + Grafana)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
AI-Platform-ISO/
│
├── intelligent-core/                   # Core Intelligence
│   │
│   ├── platform-core/                 # Layer 1: Platform Functions
│   │   ├── workflow/                  # ✅ BPMN Engine (4040 lines)
│   │   │   ├── bpmn/                  # BPMN parser, models, engine
│   │   │   ├── core/                  # Unified engine
│   │   │   ├── persistence/           # DB repositories
│   │   │   ├── visualization/         # Graphviz rendering
│   │   │   └── api/                   # FastAPI routes
│   │   │
│   │   ├── case-library/              # ⚠️ TO MIGRATE from workflow_intelligence
│   │   ├── learning/                  # ✅ EXISTS - learning-system
│   │   └── coordination/              # ⚠️ TO CREATE from coordination-center
│   │
│   ├── expertise-center/              # Layer 2: AI Intelligence
│   │   │
│   │   ├── core/                      # ⚠️ TO CREATE
│   │   │   ├── chief_executive.py     # Master orchestrator
│   │   │   ├── governance_manager.py  # Policy enforcement
│   │   │   ├── platform_manager.py    # Platform services
│   │   │   └── domain_manager.py      # Domain loading
│   │   │
│   │   ├── shared/                    # ⚠️ TO MERGE
│   │   │   ├── base/                  # Base classes
│   │   │   │   ├── base_domain.py
│   │   │   │   ├── base_expert.py
│   │   │   │   ├── base_tool.py
│   │   │   │   └── base_organ.py
│   │   │   │
│   │   │   ├── rag/                   # RAG Pipeline (merge 2 sources)
│   │   │   │   ├── pipeline.py
│   │   │   │   ├── retrieval.py
│   │   │   │   └── embeddings.py
│   │   │   │
│   │   │   ├── ml/                    # ML Infrastructure
│   │   │   │   └── predictive.py
│   │   │   │
│   │   │   └── learning/              # Meta-learning
│   │   │       └── meta_learning.py
│   │   │
│   │   ├── domains/                   # ⚠️ TO CREATE
│   │   │   │
│   │   │   └── bcm/                   # BCM Domain Plugin
│   │   │       ├── domain_config.py   # BCMDomain class
│   │   │       │
│   │   │       ├── experts/           # 7 AI Colleagues
│   │   │       │   ├── bia_specialist.py
│   │   │       │   ├── risk_analyst.py
│   │   │       │   ├── compliance_auditor.py
│   │   │       │   ├── project_manager.py
│   │   │       │   ├── incident_expert.py
│   │   │       │   ├── exercise_designer.py
│   │   │       │   └── plan_generator.py
│   │   │       │
│   │   │       ├── organs/            # 10 AI Processors
│   │   │       │   ├── governance_brain.py
│   │   │       │   ├── emergency_response.py
│   │   │       │   ├── impact_oracle.py
│   │   │       │   ├── scenario_creator.py
│   │   │       │   ├── risk_advisor.py
│   │   │       │   ├── compliance_guardian.py
│   │   │       │   ├── performance_analyst.py
│   │   │       │   ├── learning_coach.py
│   │   │       │   ├── plan_generator_organ.py
│   │   │       │   └── lifecycle_monitor.py
│   │   │       │
│   │   │       ├── tools/             # Structured Tools
│   │   │       │   ├── bia_tools.py
│   │   │       │   ├── risk_tools.py
│   │   │       │   └── compliance_tools.py
│   │   │       │
│   │   │       ├── knowledge/         # Domain Knowledge
│   │   │       │   ├── iso22301/      # 35 documents
│   │   │       │   ├── bci_gpg/       # Best practices
│   │   │       │   └── knowledge_graph.py
│   │   │       │
│   │   │       └── services/          # REST API Services
│   │   │           ├── bia-service/   # Port 8001
│   │   │           ├── risk-service/  # Port 8002
│   │   │           ├── compliance-service/  # Port 8003
│   │   │           └── document-service/    # ⚠️ TO CREATE
│   │   │
│   │   └── api/                       # ⚠️ TO CREATE
│   │       └── main.py                # Expertise Center API (port 8031)
│   │
│   └── ai-orchestration/              # ✅ EXISTS (MEGA-BRAIN)
│       ├── brain/
│       ├── memory/
│       └── tentacles/
│
├── human-interface/                   # User Interface
│   ├── web-app/                       # ✅ Next.js (TypeScript)
│   │   ├── src/app/
│   │   │   ├── page.tsx              # Dashboard
│   │   │   ├── layout.tsx
│   │   │   └── documents/            # ⚠️ TO CREATE
│   │   │       └── page.tsx
│   │   └── package.json
│   │
│   └── api-gateway/                   # ✅ FastAPI (port 8000)
│       └── main.py
│
├── infrastructure/                    # Infrastructure Services
│   ├── database/                      # ✅ Supabase client + migrations
│   │   ├── managers/
│   │   │   ├── supabase_client.py
│   │   │   ├── db_manager.py
│   │   │   ├── cache_manager.py
│   │   │   ├── rate_limiter.py
│   │   │   └── session_store.py
│   │   │
│   │   └── migrations_source/        # ✅ Migrations 001-036
│   │
│   ├── eventbus/                      # ✅ Event Bus (Redis Streams)
│   ├── monitoring/                    # ⚠️ Prometheus + Grafana (partial)
│   ├── security/                      # ⚠️ Auth middleware (partial)
│   └── realtime-websocket/            # ⚠️ WebSocket server (stub)
│
├── shared/                            # Shared Utilities
│   ├── models/                        # Pydantic models
│   └── utils/                         # Common utilities
│
└── tests/                             # ⚠️ Test suite (minimal)
```

---

## 🔧 Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI** - REST APIs
- **Pydantic** - Data validation
- **SQLAlchemy** - ORM (optional)
- **Anthropic Claude / OpenAI GPT / Ollama** - LLM providers

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **React**

### Database & Storage
- **Supabase** (managed PostgreSQL)
  - pgvector extension (embeddings)
  - Row-Level Security (RLS)
  - Storage (documents, images)
  - Realtime subscriptions

### Caching & Messaging
- **Redis**
  - Cache (session, rate limiting)
  - Streams (event bus)
  - Pub/Sub (real-time updates)

### Orchestration
- **BPMN 2.0** (Workflow definitions)
- **Custom Python Engine** (execution)

### Monitoring & Observability
- **Prometheus** (metrics)
- **Grafana** (dashboards)
- **Structured Logging** (JSON)

---

## 🗄️ Database Schema

### Core Tables (migrations 001-005)

```sql
-- Tenants & Users
tenants
users
user_sessions

-- Coordination
coordination_messages
coordination_history
```

### BCM Domain (migrations 006-018)

```sql
-- BIA & Risk
organizations
processes
dependencies
bia_analyses
risk_assessments
risk_treatments

-- Governance & Compliance
frameworks
controls
audits
evidence
documents

-- Response & Recovery
incidents
incident_responses
recovery_plans
exercises

-- Validation & Learning
validations
kpis
alerts
learning_modules
competencies
```

### Workflow (to be added)

```sql
-- BPMN Workflows
workflow.bpmn_processes
workflow.process_instances
workflow.tasks
workflow.process_events

-- Case Library
workflow.workflow_cases
workflow.case_embeddings
workflow.benchmarks
```

### AI Intelligence (to be added)

```sql
-- Expert System
ai.expert_sessions
ai.expert_interactions
ai.recommendations

-- RAG
ai.knowledge_documents
ai.document_embeddings
ai.retrieval_logs
```

---

## 🌐 API Endpoints

### Platform Core

#### Workflow Engine (port 8010)
```
POST   /api/workflow/processes          # Create BPMN process
POST   /api/workflow/instances          # Start instance
POST   /api/workflow/tasks/:id/complete # Complete task
GET    /api/workflow/instances/:id      # Get instance status
```

### Expertise Center

#### Chief Executive (port 8031)
```
POST   /api/ai/chat                     # Send message to Chief
POST   /api/ai/experts/:name/consult    # Consult specific expert
GET    /api/ai/domains                  # List loaded domains
POST   /api/ai/domains/:name/load       # Load domain plugin
```

### BCM Domain Services

#### BIA Service (port 8001)
```
POST   /api/bia/analyses                # Create BIA
GET    /api/bia/analyses/:id            # Get BIA
POST   /api/bia/processes               # Add process
```

#### Risk Service (port 8002)
```
POST   /api/risks/assessments           # Create risk assessment
GET    /api/risks/assessments/:id       # Get assessment
POST   /api/risks/treatments            # Add treatment
```

#### Document Service (port 8003) - TO CREATE
```
POST   /api/documents/upload            # Upload document
GET    /api/documents/:id               # Get document
POST   /api/documents/:id/analyze       # AI analysis
```

### Human Interface

#### API Gateway (port 8000)
```
POST   /api/auth/login                  # Login
POST   /api/auth/logout                 # Logout
GET    /api/dashboard                   # Dashboard data
POST   /api/chat                        # Chat with AI
POST   /api/documents/upload            # Upload document
```

#### Web App (port 3000)
```
/                                       # Dashboard
/bia                                    # BIA management
/risks                                  # Risk management
/documents                              # Document library
/chat                                   # AI chat interface
```

---

## 🔐 Authentication & Authorization

### Supabase Auth
- **JWT tokens** (access + refresh)
- **Row-Level Security** (RLS policies)
- **Multi-tenancy** (tenant_id isolation)

### User Roles
- **Admin** - Full access
- **BCM Manager** - BCM operations
- **User** - Read + limited write
- **Guest** - Read-only

### RLS Policies
```sql
-- Example: Users can only see their tenant's data
CREATE POLICY tenant_isolation ON processes
  FOR ALL
  TO authenticated
  USING (tenant_id = auth.uid()::text);
```

---

## 🔄 Key Workflows

### 1. Document Upload & Analysis

```
User uploads BCM policy PDF
         ↓
Web App (Next.js)
         ↓
API Gateway (/api/documents/upload)
         ↓
Document Service (saves to Supabase Storage)
         ↓
Document Service → Chief Executive (AI analysis request)
         ↓
Chief Executive → Documentation Expert (BCM domain)
         ↓
Documentation Expert → RAG Pipeline (parse + embed)
         ↓
RAG Pipeline → Supabase pgvector (store embeddings)
         ↓
Documentation Expert returns:
  - Document type
  - Key sections
  - ISO compliance gaps
  - Recommendations
         ↓
Results displayed in Web App
```

### 2. BIA Creation with AI Guidance

```
User: "How to conduct BIA for hospital?"
         ↓
Web App → API Gateway → Chief Executive
         ↓
Chief Executive routes to BIA Specialist (expert)
         ↓
BIA Specialist:
  1. Consults Impact Oracle (organ) for criticality analysis
  2. Uses RAG to retrieve ISO 22301 BIA requirements
  3. Generates step-by-step guidance
         ↓
BIA Specialist → BIA Tools (structured operations)
         ↓
BIA Tools → BIA Service (creates BIA in DB)
         ↓
BIA Service → Workflow Engine (starts BIA workflow)
         ↓
Workflow Engine creates tasks:
  - Identify critical processes
  - Assess impact
  - Determine RTO/RPO
  - Document dependencies
         ↓
User completes tasks in Web App
         ↓
Workflow Engine triggers AI validation
         ↓
Results stored in Supabase
```

### 3. Risk Assessment

```
User starts risk assessment
         ↓
Chief Executive → Risk Analyst (expert)
         ↓
Risk Analyst:
  1. Consults Risk Advisor (organ) for threat analysis
  2. Uses FAIR methodology (ML model)
  3. Generates risk scenarios
         ↓
Risk Analyst → Risk Tools → Risk Service
         ↓
Risk Service creates risk_assessment in DB
         ↓
Workflow Engine starts risk workflow
         ↓
Tasks: Identify risks → Analyze → Evaluate → Treat
         ↓
Results visualized in Web App
```

---

## 📊 Data Flow

### Request Flow
```
User → Web App → API Gateway → Service → Database
                      ↓
                 Chief Executive
                      ↓
                Domain Expert
                      ↓
                  AI Organs
                      ↓
               RAG / ML / Learning
```

### Event Flow
```
Service A publishes event → Event Bus → Service B subscribes
                                ↓
                           Workflow Engine (triggers process)
                                ↓
                            AI Analysis (background)
```

---

## 🚀 Deployment

### Development
```bash
# Install dependencies
pip install -r requirements.txt
cd human-interface/web-app && npm install

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Start services
python intelligent-core/platform-core/workflow/api/main.py  # Port 8010
python human-interface/api-gateway/main.py                  # Port 8000
cd human-interface/web-app && npm run dev                   # Port 3000
```

### Production (Docker Compose)
```bash
docker-compose up -d
```

---

## 🔗 External Integrations

### Required
- **Supabase** - Database, Storage, Auth
- **Anthropic / OpenAI / Ollama** - LLM provider

### Optional
- **Redis** - Caching (fallback: in-memory)
- **Prometheus** - Monitoring
- **Grafana** - Dashboards

---

## 📈 Performance Targets

- **API Response Time:** < 200ms (p95)
- **LLM Response Time:** < 5s (p95)
- **Workflow Execution:** < 100ms per task
- **RAG Retrieval:** < 500ms
- **Concurrent Users:** 100+
- **Throughput:** 1000 req/min

---

## 🔒 Security

### Implemented
- ✅ Supabase RLS (tenant isolation)
- ✅ JWT authentication
- ✅ HTTPS (Supabase managed)
- ✅ Input validation (Pydantic)

### To Implement
- ⚠️ Rate limiting (Redis)
- ⚠️ API key rotation
- ⚠️ Audit logging
- ⚠️ Encryption at rest
- ⚠️ RBAC (role-based access control)

---

## 📝 License

Proprietary - Internal use only
