# INTELLIGENCE Service - Simulation & Scenarios Analysis

**Document Version:** 1.0.0
**Analyzed:** 2025-10-02
**Source Location:** `/Users/MD/ISO-22301—копия/services/SERVICES/INTELLIGENCE/`
**Target Integration:** AI-Platform-ISO Community Service

---

## Executive Summary

Discovered **INTELLIGENCE Service** from old project containing comprehensive **Simulation** and **Scenarios** modules that need to be integrated into the AI-Platform-ISO architecture.

**Key Discoveries:**
- ✅ Full-featured Simulation Service (Port 8031 - conflict with Portal!)
- ✅ Scenario Orchestrator microservice
- ✅ BCM Incident Scenario module (Odoo-based)
- ✅ 3 simulation engines: What-If, Monte Carlo, Scenario
- ✅ Scenario library with pre-built BCM exercises
- ✅ EventBus integration for cross-service communication

---

## Architecture Overview

### INTELLIGENCE Service Structure

```
INTELLIGENCE/
├── simulation/                    # Simulation Service (Port 8031)
│   ├── api/                      # REST API
│   │   ├── simulation_router.py  # Simulation CRUD
│   │   ├── scenario_router.py    # Scenario management
│   │   ├── execution_router.py   # Simulation execution
│   │   └── scenario_library_router.py  # Pre-built scenarios
│   ├── engines/                  # Simulation engines
│   │   ├── what_if_engine.py     # What-if analysis
│   │   ├── monte_carlo_engine.py # Monte Carlo simulation
│   │   └── scenario_engine.py    # BCM scenario exercises
│   ├── models/
│   │   └── simulation_model.py   # SQLAlchemy models
│   └── main.py                   # FastAPI app

├── scenarios/                    # Scenario modules
│   ├── bcm_incident/            # BCM Incident module (Odoo)
│   └── scenario_orchestrator/   # Scenario orchestrator microservice

├── ai-intelligence/             # AI Intelligence module
├── digital-twin/                # Digital Twin module
├── learning-system/             # Learning System module
└── project-intelligence/        # Project Intelligence module
```

---

## Simulation Service API Endpoints

### Port: 8031 ⚠️ CONFLICT with Portal Service!

**Total Endpoints:** ~20

### 1. Simulation Management (simulation_router.py)

#### POST /api/simulation/simulations
Create new simulation
```json
{
  "tenant_id": "org123",
  "name": "RTO Impact Analysis",
  "simulation_type": "what_if",  // or monte_carlo, scenario, optimization
  "engine": "internal",
  "parameters": {
    "rto_hours": 24,
    "impact_threshold": 0.8
  },
  "metadata": {}
}
```

**Response:**
```json
{
  "id": 1,
  "tenant_id": "org123",
  "name": "RTO Impact Analysis",
  "simulation_type": "what_if",
  "engine": "internal",
  "status": "draft",
  "created_at": "2025-10-02T10:00:00Z"
}
```

#### GET /api/simulation/simulations
List simulations with filters
- Query params: `tenant_id`, `simulation_type`, `status`, `skip`, `limit`

#### GET /api/simulation/simulations/{sim_id}
Get simulation details

#### DELETE /api/simulation/simulations/{sim_id}
Delete simulation (cannot delete running simulations)

#### GET /api/simulation/engines
List available simulation engines
```json
{
  "engines": [
    {
      "name": "what_if",
      "description": "What-if analysis engine",
      "capabilities": ["impact_analysis", "dependency_analysis"]
    },
    {
      "name": "monte_carlo",
      "description": "Monte Carlo statistical simulation",
      "capabilities": ["risk_quantification", "uncertainty_analysis"]
    },
    {
      "name": "scenario",
      "description": "BCM scenario exercise engine",
      "capabilities": ["exercise_simulation", "training"]
    }
  ]
}
```

---

### 2. Scenario Management (scenario_router.py)

#### POST /api/simulation/scenarios
Create BCM scenario
```json
{
  "tenant_id": "org123",
  "title": "Cyber Attack Response Exercise",
  "category": "cyber",
  "complexity": 3,
  "scenario_type": "tabletop",
  "content": "Markdown scenario description...",
  "timeline": {
    "hour_0": "Initial attack detected",
    "hour_1": "Team mobilized"
  },
  "injects": {
    "inject_1": "CEO demands status update"
  },
  "success_metrics": {
    "response_time": "< 1 hour"
  }
}
```

#### GET /api/simulation/scenarios
List scenarios
- Filters: `category`, `complexity`, `skip`, `limit`

#### GET /api/simulation/scenarios/{scenario_id}
Get full scenario details including timeline, injects, success metrics

#### DELETE /api/simulation/scenarios/{scenario_id}
Delete scenario

---

### 3. Simulation Execution (execution_router.py)

#### POST /api/simulation/simulations/{sim_id}/run
Run simulation (background task)
```json
{
  "simulation_id": 123,
  "status": "started",
  "message": "Simulation started in background"
}
```

#### GET /api/simulation/simulations/{sim_id}/status
Get simulation execution status
```json
{
  "simulation_id": 123,
  "status": "running",  // draft, ready, running, completed, failed
  "started_at": "2025-10-02T10:00:00Z",
  "completed_at": null
}
```

#### GET /api/simulation/simulations/{sim_id}/results
Get simulation results (only for completed simulations)
```json
{
  "simulation_id": 123,
  "status": "completed",
  "results": [
    {
      "id": 1,
      "result_type": "final",
      "result_data": {
        "impact_score": 0.75,
        "affected_processes": 12,
        "recommendations": [...]
      },
      "confidence_score": 0.92,
      "recorded_at": "2025-10-02T10:30:00Z"
    }
  ]
}
```

#### POST /api/simulation/simulations/{sim_id}/stop
Stop running simulation

---

### 4. Scenario Library (scenario_library_router.py)

**Pre-built BCM scenarios from shared library**

#### GET /api/simulation/library
List all scenarios from library
- Filters: `threat_type`, `complexity`

```json
[
  {
    "id": "cyber_ransomware_001",
    "name": "Ransomware Attack Exercise",
    "threat_type": "cyber",
    "complexity": "Intermediate",
    "duration_hours": 4,
    "description": "...",
    "inject_count": 8,
    "learning_objectives": [...]
  }
]
```

#### GET /api/simulation/library/{scenario_id}
Get full scenario details from library
```json
{
  "id": "cyber_ransomware_001",
  "name": "Ransomware Attack Exercise",
  "threat_type": "cyber",
  "complexity": "Intermediate",
  "duration_hours": 4,
  "description": "...",
  "initial_situation": "...",
  "timeline": [...],
  "injects": [...],
  "success_criteria": [...],
  "learning_objectives": [...],
  "debrief_questions": [...]
}
```

#### GET /api/simulation/library/threat-types
List all threat types
```json
{
  "threat_types": [
    "cyber",
    "natural_disaster",
    "pandemic",
    "supply_chain",
    "infrastructure",
    "human_error",
    "terrorism"
  ]
}
```

#### GET /api/simulation/library/complexity-levels
List complexity levels
```json
{
  "complexity_levels": ["Beginner", "Intermediate", "Advanced", "Expert"]
}
```

#### GET /api/simulation/library/stats
Get library statistics
```json
{
  "total_scenarios": 25,
  "by_threat_type": {
    "cyber": 8,
    "natural_disaster": 5,
    "pandemic": 3
  },
  "by_complexity": {
    "Beginner": 6,
    "Intermediate": 12,
    "Advanced": 5,
    "Expert": 2
  },
  "avg_duration_hours": 5.2,
  "total_injects": 180
}
```

---

## Database Schema

### Schema: `simulation`

#### Table: `simulations`
```sql
CREATE TABLE simulation.simulations (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    simulation_type VARCHAR(50) NOT NULL,  -- what_if, monte_carlo, scenario, optimization
    engine VARCHAR(50),  -- internal, jaamsim, external
    parameters JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'draft',  -- draft, ready, running, completed, failed
    created_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
CREATE INDEX idx_simulations_tenant ON simulation.simulations(tenant_id);
```

#### Table: `scenarios`
```sql
CREATE TABLE simulation.scenarios (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50),  -- cyber, pandemic, disaster
    complexity INTEGER,  -- 1-5
    scenario_type VARCHAR(50),  -- tabletop, functional, full_scale
    content TEXT,  -- Markdown
    timeline JSONB,
    injects JSONB,
    success_metrics JSONB,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    ai_generation_params JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_scenarios_tenant ON simulation.scenarios(tenant_id);
```

#### Table: `executions`
```sql
CREATE TABLE simulation.executions (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL,
    execution_number INTEGER,
    parameters JSONB,
    status VARCHAR(50),  -- running, completed, failed
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    results JSONB,
    error_message TEXT
);
CREATE INDEX idx_executions_simulation ON simulation.executions(simulation_id);
```

#### Table: `results`
```sql
CREATE TABLE simulation.results (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL,
    result_type VARCHAR(50),  -- final, intermediate, metric
    result_data JSONB NOT NULL,
    confidence_score FLOAT,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_results_simulation ON simulation.results(simulation_id);
CREATE INDEX idx_results_recorded ON simulation.results(recorded_at);
```

---

## Simulation Engines

### 1. What-If Engine (what_if_engine.py)

**Purpose:** Impact analysis and dependency analysis

**Use Cases:**
- "What if critical supplier fails?"
- "What if RTO exceeds 24 hours?"
- "What if key personnel unavailable?"

**Capabilities:**
- Impact propagation analysis
- Dependency chain analysis
- Critical path identification

---

### 2. Monte Carlo Engine (monte_carlo_engine.py)

**Purpose:** Statistical risk quantification

**Use Cases:**
- Risk probability distribution
- Financial impact modeling
- Recovery time estimation

**Capabilities:**
- Probability distribution analysis
- Uncertainty quantification
- Confidence interval calculation

---

### 3. Scenario Engine (scenario_engine.py)

**Purpose:** BCM exercise simulation

**Use Cases:**
- Tabletop exercises
- Functional exercises
- Full-scale drills

**Capabilities:**
- Exercise timeline management
- Inject delivery
- Performance tracking

---

## Scenario Orchestrator

**Location:** `scenarios/scenario_orchestrator/`

**Purpose:** AI-powered scenario orchestration microservice

**Model:**
```python
class Scenario(BaseModel):
    id: str
    company_id: str
    title: str
    description: str
    scenario_type: str
    risk_level: str
    data: Dict[str, Any]
    created_by: str
    created_at: datetime
```

---

## BCM Incident Module

**Location:** `scenarios/bcm_incident/`

**Type:** Odoo module (Python)

**Purpose:** BCM incident management and scenario exercises

**Key Files:**
- `models/bcm_incident_unified.py` - Unified incident model
- `models/bcm_incident_integration_api.py` - Integration API
- `models/ai_communication_models.py` - AI communication

---

## Integration Strategy

### ⚠️ Port Conflict Resolution

**Problem:** Both Simulation Service and Portal Service use port 8031

**Solutions:**

#### Option 1: Merge Simulation into Portal (Recommended)
```
Portal Service (8031):
├── Knowledge Hub
├── Community Forum
├── Scenarios (existing)
└── Simulations (NEW - merged from INTELLIGENCE)
```

**Pros:**
- Single community-facing service
- Simpler architecture
- Scenarios + Simulations together (logical grouping)

**Cons:**
- Portal service becomes larger
- More complex codebase

#### Option 2: Change Simulation Service Port
```
Portal Service: 8031
Simulation Service: 8033 (NEW)
Marketplace Service: 8032
```

**Pros:**
- Services remain independent
- Clear separation of concerns

**Cons:**
- Additional microservice to manage
- Cross-service integration needed

---

### Recommended Integration Path

**Phase 1: Analysis (DONE ✅)**
- ✅ Discovered INTELLIGENCE service
- ✅ Analyzed simulation and scenarios modules
- ✅ Documented API endpoints

**Phase 2: Migration Planning**
1. Merge simulation endpoints into Portal Service
   - `/api/knowledge` - Knowledge Hub (existing)
   - `/api/forum` - Community Forum (existing)
   - `/api/scenarios` - Scenario Marketplace (existing)
   - `/api/simulations` - Simulations (NEW)
   - `/api/simulation/library` - Scenario Library (NEW)
2. Create unified database schema migration
   - Add `simulation` schema to Community Service migration
3. Update Docker Compose configuration
4. Update frontend specification

**Phase 3: Database Migration**
1. Add simulation schema to Supabase
2. Migrate scenario library data
3. Test connections

**Phase 4: Service Integration**
1. Copy simulation engines to Portal
2. Update imports and paths
3. Register simulation routers in Portal main.py
4. Test API endpoints

**Phase 5: Frontend Update**
1. Update technical specification (v3.0.0)
2. Add simulation UI flows
3. Add scenario library browser

---

## Data Flows

### Flow 1: Deploy Scenario from Library

```
User → Frontend
  ↓
GET /api/simulation/library  # Browse scenarios
  ↓
GET /api/simulation/library/{id}  # View scenario details
  ↓
POST /api/simulation/scenarios  # Create scenario instance
  ↓
POST /api/simulation/simulations  # Create simulation
  (type: "scenario", parameters: scenario_id)
  ↓
POST /api/simulation/simulations/{id}/run  # Execute
  ↓
GET /api/simulation/simulations/{id}/status  # Monitor
  ↓
GET /api/simulation/simulations/{id}/results  # View results
```

### Flow 2: What-If Analysis

```
User → Frontend
  ↓
POST /api/simulation/simulations
  {
    "simulation_type": "what_if",
    "parameters": {
      "scenario": "supplier_failure",
      "supplier_id": "SUP-123",
      "duration_hours": 48
    }
  }
  ↓
POST /api/simulation/simulations/{id}/run
  ↓ (WhatIfEngine runs in background)
GET /api/simulation/simulations/{id}/results
  {
    "affected_processes": 15,
    "impact_score": 0.82,
    "recommendations": [...]
  }
```

### Flow 3: Create Case Study from Simulation

```
Simulation Completed
  ↓
POST /api/simulations/{id}/convert-to-case-study
  ↓
EventBus: "simulation.completed"
  ↓
Marketplace Service receives event
  ↓
POST /api/specialists/{specialist_id}/portfolio
  {
    "title": "RTO Improvement Project",
    "description": "Reduced RTO from 48h to 24h",
    "simulation_id": 123,
    "results_summary": {...}
  }
  ↓
Case study appears in specialist portfolio
```

---

## Key Differences from Portal Scenarios

### Portal Scenarios (Existing)
- **Purpose:** Scenario marketplace (buy/sell scenarios)
- **Schema:** `portal.bcm_scenarios`
- **Features:** Catalog, deployment, reviews
- **Endpoints:** 6 endpoints

### Simulation Scenarios (INTELLIGENCE)
- **Purpose:** Full scenario execution and simulation
- **Schema:** `simulation.scenarios` + `simulation.simulations`
- **Features:** Execution engine, timeline, injects, results tracking
- **Endpoints:** 20+ endpoints

### Integration Approach
**Merge both into unified Scenario System:**

```
Unified Scenario System:
├── Scenario Library (read-only, pre-built scenarios)
├── Scenario Marketplace (user-created scenarios for sale)
├── Scenario Execution Engine (run scenarios as exercises)
└── Simulation Engine (what-if, monte carlo)
```

---

## Next Steps

### Immediate Actions
1. ✅ Complete INTELLIGENCE service analysis (DONE)
2. ⏳ Update frontend specification to v3.0.0
3. ⏳ Create integration plan for Portal + Simulation merge
4. ⏳ Plan database migration for simulation schema

### Short-term (Next Week)
5. ⏳ Migrate simulation endpoints to Portal Service
6. ⏳ Apply database migrations to Supabase
7. ⏳ Test integrated API endpoints
8. ⏳ Update Docker Compose

### Medium-term (Next Month)
9. ⏳ Develop frontend UI for simulations
10. ⏳ Migrate scenario library data
11. ⏳ Implement cross-service case study creation
12. ⏳ End-to-end testing

---

## API Summary

### Total Endpoints: ~20

**Simulation Management:** 5
- Create, list, get, delete simulations
- List engines

**Scenario Management:** 4
- Create, list, get, delete scenarios

**Execution:** 4
- Run, status, results, stop simulation

**Scenario Library:** 7
- List library, get scenario, threat types, complexity levels, stats

---

## Recommendations

### Architecture
✅ **Merge Simulation into Portal Service** - Logical grouping of community features
✅ **Unified Scenario System** - Combine marketplace + library + execution
✅ **EventBus Integration** - Enable cross-service case study creation

### Database
✅ **Add simulation schema** to Community Service migration
✅ **Preserve portal.bcm_scenarios** for marketplace
✅ **Add simulation.scenarios** for execution

### Frontend
✅ **Update specification to v3.0.0** with simulations
✅ **Design simulation execution UI** with real-time status
✅ **Scenario library browser** with filters and preview

---

**Document Status:** Complete
**Next Document:** FRONTEND_TECHNICAL_SPECIFICATION v3.0.0
**Analysis Date:** 2025-10-02
