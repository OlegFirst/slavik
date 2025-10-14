# 🏗️ Simulation Service - Architecture & Flow

**Version**: 2.0.0
**Port**: 8095
**Type**: Platform Service
**Status**: Production Ready

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SIMULATION SERVICE                            │
│                         (Port 8095)                                  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                           │
        ▼                          ▼                           ▼
┌──────────────┐          ┌───────────────┐          ┌───────────────┐
│   API Layer  │          │  Engine Layer │          │ Storage Layer │
│  (FastAPI)   │          │ (7 Engines)   │          │  (PostgreSQL) │
└──────────────┘          └───────────────┘          └───────────────┘
        │                          │                           │
        ├─ Health                  ├─ JaamSim                 ├─ simulations
        ├─ Simulations             ├─ MonteCarlo              ├─ scenarios
        ├─ Scenarios               ├─ Scenario                ├─ executions
        ├─ Library                 ├─ WhatIf                  └─ results
        ├─ Executions              ├─ BCMQueue
        └─ Metrics                 ├─ AdvancedBIA
                                   └─ JaamSimClient

                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                           │
        ▼                          ▼                           ▼
┌──────────────┐          ┌───────────────┐          ┌───────────────┐
│ Integration  │          │ Support Layer │          │ Presentation  │
│    Layer     │          │  (Utilities)  │          │     Layer     │
└──────────────┘          └───────────────┘          └───────────────┘
        │                          │                           │
        ├─ EventBus                ├─ Validators              ├─ Visualization
        ├─ AI Foundation           ├─ Formatters              ├─ Analytics
        ├─ Workflow Intel          ├─ Math Utils              └─ Reports
        ├─ Service Discovery       └─ DateTime Helpers
        ├─ TheHive (optional)
        └─ NICS (optional)
```

---

## 🔄 Simulation Execution Flow

### **Standard Flow (Synchronous)**

```
┌─────────────┐
│   User/API  │
└──────┬──────┘
       │ 1. POST /simulations (create)
       │
       ▼
┌─────────────────────────────────────────────────┐
│           API Router (api/v1/)                  │
│  - Validate request (spec/request_schemas.py)   │
│  - Authenticate & authorize                      │
└──────────────────┬──────────────────────────────┘
                   │ 2. Create DB record
                   ▼
┌─────────────────────────────────────────────────┐
│      Storage Layer (storage/repositories/)      │
│  - Insert into simulation.simulations            │
│  - Status: 'draft'                               │
└──────────────────┬──────────────────────────────┘
                   │ 3. Publish event
                   ▼
┌─────────────────────────────────────────────────┐
│           EventBus Integration                  │
│  - Publish: simulation.created                   │
│  - Notify: knowledge_center, community_intel    │
└──────────────────┬──────────────────────────────┘
                   │
                   ◄────── API returns Simulation ID
                   │
                   │ 4. POST /simulations/{id}/execute
                   ▼
┌─────────────────────────────────────────────────┐
│         Execution Coordinator                   │
│  - Load simulation config                        │
│  - Validate parameters (utils/validators.py)    │
│  - Select engine based on type                   │
└──────────────────┬──────────────────────────────┘
                   │ 5. Route to engine
                   ▼
┌─────────────────────────────────────────────────┐
│           Simulation Engine                     │
│  - JaamSim / MonteCarlo / Scenario / etc.       │
│  - Execute simulation logic                      │
│  - Record progress                               │
└──────────────────┬──────────────────────────────┘
                   │ 6. Store results
                   ▼
┌─────────────────────────────────────────────────┐
│         Results Processing                      │
│  - Calculate statistics (utils/math_utils.py)   │
│  - Format results (utils/formatters.py)         │
│  - Store in simulation.results                   │
└──────────────────┬──────────────────────────────┘
                   │ 7. Generate visualization
                   ▼
┌─────────────────────────────────────────────────┐
│      Visualization Layer (visualization/)       │
│  - Generate charts (chart_generator.py)         │
│  - Create dashboard                              │
└──────────────────┬──────────────────────────────┘
                   │ 8. Publish completion
                   ▼
┌─────────────────────────────────────────────────┐
│           EventBus Integration                  │
│  - Publish: simulation.completed                 │
│  - Notify: workflow_intelligence, predictive    │
└──────────────────┬──────────────────────────────┘
                   │ 9. Record metrics
                   ▼
┌─────────────────────────────────────────────────┐
│         Metrics Layer (core/metrics.py)         │
│  - simulation_executions_total++                │
│  - simulation_duration_seconds.observe()        │
│  - simulation_success_rate.set()                │
└─────────────────────────────────────────────────┘
                   │
                   ◄────── Return execution results
```

---

## 🎯 AI Scenario Generation Flow

```
┌─────────────┐
│   User/API  │
└──────┬──────┘
       │ 1. POST /scenarios/generate
       │    { category: "cyber", complexity: 4 }
       ▼
┌─────────────────────────────────────────────────┐
│           API Router (api/scenarios.py)         │
│  - Validate request (ScenarioGenerateRequest)   │
└──────────────────┬──────────────────────────────┘
                   │ 2. Check templates
                   ▼
┌─────────────────────────────────────────────────┐
│     Scenario Templates (scenarios/templates/)   │
│  - Check if template exists                      │
│  - Get base template (optional)                  │
└──────────────────┬──────────────────────────────┘
                   │ 3. Call AI Foundation
                   ▼
┌─────────────────────────────────────────────────┐
│    AI Foundation Integration (port 8010)        │
│  - POST /rag/search (find similar scenarios)    │
│  - POST /llm/generate (create narrative)        │
└──────────────────┬──────────────────────────────┘
                   │ 4. Generate scenario
                   ▼
┌─────────────────────────────────────────────────┐
│         Scenario Generator Engine               │
│  - Build narrative                               │
│  - Create timeline                               │
│  - Generate injects                              │
│  - Define success metrics                        │
│  - Calculate quality score                       │
└──────────────────┬──────────────────────────────┘
                   │ 5. Validate & store
                   ▼
┌─────────────────────────────────────────────────┐
│      Storage Layer (simulation.scenarios)       │
│  - Insert scenario                               │
│  - Set is_ai_generated = true                    │
│  - Store ai_confidence_score                     │
└──────────────────┬──────────────────────────────┘
                   │ 6. Publish event
                   ▼
┌─────────────────────────────────────────────────┐
│           EventBus Integration                  │
│  - Publish: scenario.generated                   │
│  - Notify: workflow_intelligence                │
└──────────────────┬──────────────────────────────┘
                   │ 7. Record metrics
                   ▼
┌─────────────────────────────────────────────────┐
│         Metrics Layer                           │
│  - scenario_generation_count++                  │
│  - scenario_generation_quality_score.set()      │
└─────────────────────────────────────────────────┘
                   │
                   ◄────── Return generated scenario
```

---

## 🔌 EventBus Integration Pattern

### **Published Events** (8 events)

```
simulation-service ──┐
                     ├──> simulation.created
                     ├──> simulation.started
                     ├──> simulation.progress
                     ├──> simulation.completed
                     ├──> simulation.failed
                     ├──> scenario.generated
                     ├──> execution.started
                     └──> execution.completed
                             │
                             ├──> knowledge-center (stores in RAG)
                             ├──> community-intelligence (shares insights)
                             ├──> workflow-intelligence (adds to case library)
                             ├──> predictive (improves forecasting)
                             └──> monitoring (alerts & dashboards)
```

### **Subscribed Events** (4 events)

```
scenario.execution.requested ───┐
digital_twin.state.changed ──────┤
bia.analysis.requested ──────────┼──> simulation-service
workflow.scenario.required ──────┘        │
                                          ├──> Event Handler
                                          ├──> Execute Simulation
                                          └──> Publish Results
```

---

## 🗄️ Data Model (Database Schema)

```sql
-- simulation schema

┌────────────────────────────────────────┐
│         simulations                    │  ◄── Main table
├────────────────────────────────────────┤
│ id (PK)                                │
│ tenant_id                              │
│ name, description                      │
│ simulation_type (what_if|monte_carlo|...) │
│ status (draft|ready|running|completed) │
│ parameters (JSONB)                     │
│ created_at, updated_at                 │
└────────────────┬───────────────────────┘
                 │
                 │ 1:N
                 │
┌────────────────▼───────────────────────┐
│         executions                     │  ◄── Execution history
├────────────────────────────────────────┤
│ id (PK)                                │
│ simulation_id (FK)                     │
│ execution_number                       │
│ status (running|completed|failed)      │
│ progress (0-100)                       │
│ results (JSONB)                        │
│ started_at, completed_at               │
└────────────────┬───────────────────────┘
                 │
                 │ 1:N
                 │
┌────────────────▼───────────────────────┐
│         results                        │  ◄── Time-series results
├────────────────────────────────────────┤
│ id (PK)                                │
│ simulation_id (FK)                     │
│ execution_id (FK)                      │
│ result_type (final|intermediate|...)  │
│ result_data (JSONB)                    │
│ recorded_at                            │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│         scenarios                      │  ◄── BCM scenarios
├────────────────────────────────────────┤
│ id (PK)                                │
│ tenant_id (NULL for public)            │
│ title, description                     │
│ category (cyber|pandemic|...)          │
│ complexity (1-5)                       │
│ content (TEXT)                         │
│ timeline, injects (JSONB)              │
│ is_ai_generated                        │
│ ai_confidence_score                    │
└────────────────────────────────────────┘
```

**RLS Policies**: All tables have Row-Level Security for multi-tenancy

---

## 🧩 Component Layers

### **1. API Layer** (`/api`)
- **Purpose**: HTTP endpoints, request/response handling
- **Technology**: FastAPI with async/await
- **Files**: 6 routers, 31 endpoints
- **Validation**: Pydantic models from `/spec`

### **2. Engine Layer** (`/engines`)
- **Purpose**: Simulation execution logic
- **Engines**:
  1. `JaamSimEngine` - Discrete-event (external JaamSim)
  2. `MonteCarloEngine` - Probabilistic analysis
  3. `ScenarioEngine` - BCM scenario execution
  4. `WhatIfEngine` - Decision analysis
  5. `BCMQueueSimulator` - Queue theory (M/M/c)
  6. `AdvancedBIAEngine` - Multi-resource BIA
  7. `JaamSimClient` - BCM exercise orchestrator

### **3. Storage Layer** (`/storage`)
- **Purpose**: Database access & ORM
- **Components**:
  - `repositories/` - Data access objects
  - `models/` - SQLAlchemy models
  - `migrations/` - Database migrations

### **4. Integration Layer** (`/integration`)
- **Purpose**: External service communication
- **Clients**:
  - `eventbus_client.py` - EventBus pub/sub
  - `ai_foundation_client.py` - AI generation
  - `workflow_intelligence_client.py` - Case library
  - `service_discovery_client.py` - Consul registration
  - `thehive_client.py` - BCM exercise platform
  - `nics_client.py` - Emergency management

### **5. Support Layer** (`/utils`, `/core`)
- **Purpose**: Shared utilities
- **Modules**:
  - `validators.py` - Parameter validation
  - `formatters.py` - Result formatting
  - `math_utils.py` - Statistical calculations
  - `datetime_helpers.py` - Date/time operations
  - `metrics.py` - Prometheus metrics

### **6. Presentation Layer** (`/visualization`, `/analytics`)
- **Purpose**: Result visualization & reporting
- **Components**:
  - Chart generators (time series, distributions)
  - Dashboard templates
  - Report generators (PDF, HTML, Excel)
  - Trend analysis

### **7. Content Layer** (`/scenarios`)
- **Purpose**: BCM scenario templates
- **Templates**: 6 pre-built scenarios
  - IT Failure, Pandemic, Disaster, Ransomware, Supply Chain, Data Breach

---

## 📊 Metrics & Observability

### **Prometheus Metrics** (6 KPIs + operational)

```
# KPIs
simulation_executions_total{type, engine, status, tenant}
simulation_success_rate{type, tenant}
simulation_duration_seconds{type, engine, tenant}
scenario_generation_quality_score{category, complexity, tenant}
simulation_active_count{tenant}
simulation_error_rate{tenant}

# Operational
simulation_api_requests_total{method, endpoint, status}
simulation_api_request_duration_seconds{method, endpoint}
simulation_eventbus_events_published_total{event_type, tenant}
simulation_database_operations_total{operation, table, status}
```

### **Health Check** (`/health`)

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "engines": ["JaamSim", "MonteCarlo", "Scenario", ...],
  "uptime_seconds": 3600,
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "eventbus": "connected"
  }
}
```

---

## 🔐 Security & Multi-Tenancy

### **Row-Level Security (RLS)**
```sql
-- All queries automatically filtered by tenant
CREATE POLICY simulations_tenant_isolation
  ON simulation.simulations
  FOR ALL
  USING (tenant_id = current_setting('app.current_tenant_id', true));
```

### **Authentication**
- JWT tokens via API Gateway
- Service-to-service authentication for internal calls

### **Authorization**
- Role-based access (BCM Coordinator, Manager, Viewer)
- Resource-level permissions

---

## 🚀 Deployment

### **Docker**
```yaml
simulation-service:
  image: simulation-service:2.0.0
  ports:
    - "8095:8095"
  environment:
    - DATABASE_URL=${DATABASE_URL}
    - REDIS_URL=${REDIS_URL}
    - EVENTBUS_URL=${EVENTBUS_URL}
  replicas: 2
  resources:
    cpu: "1.0"
    memory: "1Gi"
```

### **Service Discovery** (Consul)
- Auto-registration on startup
- Health checks every 10s
- Heartbeat mechanism
- Graceful deregistration on shutdown

---

## 📈 Performance Characteristics

### **Throughput**
- Target: > 100 simulations/day
- Max concurrent: 100 active simulations
- API response time: < 100ms (p95)

### **Scalability**
- Horizontal: 2+ replicas
- Database: Connection pooling (Supabase)
- Cache: Redis for session management

### **Reliability**
- Success rate: > 95%
- Auto-retry on failures (EventBus)
- Circuit breaker pattern for external services

---

## 🎓 Usage Examples

### **Create & Execute Monte Carlo Simulation**

```python
# 1. Create simulation
response = requests.post("http://localhost:8095/api/v1/simulations", json={
    "name": "IT Recovery Analysis",
    "simulation_type": "monte_carlo",
    "parameters": {
        "iterations": 1000,
        "variables": {
            "recovery_time": {"distribution": "normal", "mean": 4, "std": 1}
        }
    }
})
simulation_id = response.json()["id"]

# 2. Execute
execution = requests.post(
    f"http://localhost:8095/api/v1/simulations/{simulation_id}/execute"
)

# 3. Get results
results = requests.get(
    f"http://localhost:8095/api/v1/executions/{execution.json()['id']}"
)
```

### **Generate AI Scenario**

```python
response = requests.post("http://localhost:8095/api/v1/scenarios/generate", json={
    "category": "cyber",
    "complexity": 4,
    "industry": "healthcare",
    "organization_size": "large"
})
scenario = response.json()
```

---

## 📚 Key Files

**Configuration**:
- `SERVICE_INFO.yaml` - Service metadata
- `KPI.yaml` - KPI definitions
- `requirements.txt` - Python dependencies

**Core**:
- `main.py` - FastAPI application
- `api/` - API routers
- `engines/` - Simulation engines
- `storage/` - Database layer

**Documentation**:
- `README.md` - Quick start
- `INTEGRATION_COMPLETE.md` - Integration status
- `CATALOG_ENTRY.yaml` - Service catalog entry

---

**Created**: 2025-10-14
**Version**: 2.0.0
**Status**: Production Ready
**Port**: 8095
