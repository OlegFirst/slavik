# Golden Standard Templates - Scenario Intelligence

**Created**: 2025-10-12
**Status**: Complete
**Location**: `/intelligent-core/scenario-intelligence/templates/`

---

## 📋 Overview

This directory contains **4 golden standard templates** for generating scenarios at all levels of the platform hierarchy.

These templates serve as **reusable blueprints** for the Scenario Manager to automatically generate comprehensive test scenarios.

---

## 📂 Template Files

### 1. **golden_standard_l1.yaml** (Service Level)
- **Purpose**: Test individual platform services
- **Size**: 400 lines
- **Applicable to**: 46 platform services
- **Test Categories**: 6 scenarios per service
  - Service Startup & Health Check
  - Primary Operations Test
  - Dependency Verification
  - Error Handling & Resilience
  - Performance & Load Test
  - Monitoring & Observability

**Key Features**:
- Infrastructure health testing
- Dependency chain validation
- Technical resilience patterns
- Prometheus metrics validation
- Service discovery integration

---

### 2. **golden_standard_l1_application.yaml** (Application Level)
- **Purpose**: Test user-facing applications and BCM modules
- **Size**: 820 lines
- **Applicable to**: 4 main apps + 12 BCM modules = 16 total
- **Test Categories**: 8 scenarios per application
  - Application Startup & Availability
  - User Authentication & Authorization
  - Core Business Functionality
  - UI/UX Validation
  - Data Integration & API Communication
  - Security & Data Protection
  - Error Handling & User Feedback
  - Performance Under Load

**Key Features**:
- User authentication flows
- UI/UX validation (responsive, accessible)
- Business functionality testing
- Frontend performance (FCP, LCP, CLS)
- Security testing (XSS, CSRF, RBAC)
- Real-time WebSocket updates

---

### 3. **golden_standard_l2.yaml** (Subsystem Level)
- **Purpose**: Test coordinated subsystem operations
- **Size**: 600 lines
- **Applicable to**: 12 subsystems
- **Test Categories**: 8 scenarios per subsystem
  - Coordinated Startup
  - Inter-Service Communication
  - Subsystem-Level Resilience
  - Performance Under Load
  - Data Integration & Consistency
  - Security & Access Control
  - Monitoring & Observability
  - Dependency Management

**Key Features**:
- Service coordination testing
- Inter-service communication patterns
- Circuit breaker validation
- Distributed tracing
- Cross-service transactions
- Subsystem-level metrics

---

### 4. **golden_standard_l3.yaml** (Functional System Level)
- **Purpose**: Test end-to-end functional system operations
- **Size**: 750 lines
- **Applicable to**: 19 functional systems
- **Test Categories**: 8 scenarios per system
  - End-to-End Functional Flow
  - System-Level Resilience
  - Business Process Validation
  - Cross-Subsystem Integration
  - Performance & Scalability
  - User Experience Validation
  - Monitoring & Observability
  - Security & Compliance

**Key Features**:
- Business process validation
- Cross-subsystem orchestration
- System-level resilience (self-healing)
- User journey testing
- Compliance verification (ISO 22301, GDPR)
- Business metrics and KPIs

---

### 5. **golden_standard_l4.yaml** (User Workflow Level)
- **Purpose**: Test real user scenarios and business outcomes
- **Size**: 900 lines
- **Applicable to**: User workflows (variable)
- **Generation Method**: AI-Powered (OpenAI/Claude)
- **Test Categories**: 8 scenarios per workflow
  - Complete User Journey - Happy Path
  - Alternative Paths & Variations
  - Error Handling & Recovery
  - Collaboration & Multi-User Workflows
  - Performance & User Experience
  - Business Process Integration
  - Compliance & Audit Trail
  - Edge Cases & Stress Conditions

**Key Features**:
- Real user journey validation
- Business outcome measurement
- User satisfaction tracking
- Collaborative workflows
- Compliance and audit trails
- User feedback integration
- AI-generated scenarios based on context

---

## 🎯 Scenario Generation Statistics

### Total Scenarios to Generate

| Level | Template | Count | Total Scenarios | Estimated Time |
|-------|----------|-------|-----------------|----------------|
| L1 | Service | 46 | 276 (46 × 6) | 92 minutes |
| L1 | Application | 16 | 128 (16 × 8) | 32 minutes |
| L2 | Subsystem | 12 | 96 (12 × 8) | 36 minutes |
| L3 | Functional System | 19 | 152 (19 × 8) | 95 minutes |
| L4 | User Workflow | Variable | Variable | 10-15 min/workflow |

**Total L1-L3**: 652 scenarios
**Total Generation Time**: ~4.25 hours (automated)

---

## 🏗️ Template Structure

All templates follow a consistent structure:

```yaml
meta:
  id: "scenario_id"
  level: 1|2|3|4
  type: "service|application|subsystem|functional_system|user_workflow"
  # ... metadata

description:
  summary: "..."
  purpose: "..."
  # ... description fields

# Level-specific info (service_info, subsystem_info, etc.)

dependencies:
  # Dependencies on other levels

test_scenarios:
  - name: "Scenario 1"
    scenario_id: "..."
    priority: "critical|high|medium|low"
    execution_time: "..."
    steps:
      - id: "1.1"
        action: "..."
        expected: {...}
      # ... more steps

monitoring:
  metrics: [...]
  alerts: [...]
  dashboards: [...]

execution_history: []  # Populated after execution

learning_data: {}  # Populated by AI learning system

metadata:
  template_version: "1.0.0"
  created_by: "scenario_manager"
  # ... metadata
```

---

## 🔄 Scenario Generation Workflow

### Phase 1: Initial Generation (Automated)

1. **L1 Platform Services** (46 scenarios)
   - Generator reads `SERVICE_CATALOG_DETAILED.yaml`
   - For each service, fills `golden_standard_l1.yaml` template
   - Generates 6 test scenarios per service

2. **L1 Applications** (16 scenarios)
   - Generator reads `USER_APPLICATIONS_CATALOG.yaml`
   - For each app/module, fills `golden_standard_l1_application.yaml`
   - Generates 8 test scenarios per application

3. **L2 Subsystems** (12 scenarios)
   - Generator reads `SUBSYSTEMS_CATALOG.yaml`
   - For each subsystem, fills `golden_standard_l2.yaml`
   - Generates 8 test scenarios per subsystem

4. **L3 Functional Systems** (19 scenarios)
   - Generator reads `SYSTEMS_CATALOG.yaml`
   - For each system, fills `golden_standard_l3.yaml`
   - Generates 8 test scenarios per system

5. **L4 User Workflows** (Variable)
   - AI (OpenAI/Claude) generates scenarios based on:
     - User roles and context
     - Business objectives
     - Involved systems from L1/L2/L3
     - Compliance requirements
   - Fills `golden_standard_l4.yaml` template

### Phase 2: Continuous Improvement (AI-Powered)

```
Execution → Analysis → Prediction → Decision → Improvement
   ↓           ↓           ↓            ↓           ↓
Results → Analytics → Predictive → AI Orch. → Updated
          Specialist   Service      Decision    Scenario
```

**EventBus Integration**:
- `scenario.execution.completed` → Analytics Specialist analyzes
- `analysis.completed` → Predictive Service forecasts
- `prediction.created` → AI Orchestration decides
- `decision.made` → Scenario Manager improves scenario
- `scenario.improved` → New version archived

---

## 📊 Monitoring & Metrics

Each template includes comprehensive monitoring:

### Service Metrics (L1)
- `{service}_requests_total`
- `{service}_errors_total`
- `{service}_latency_seconds`
- `{service}_health_status`

### Application Metrics (L1 App)
- `{app}_page_load_time`
- `{app}_api_calls_total`
- `{app}_errors_total`
- `{app}_user_sessions_active`
- Web Vitals: FCP, LCP, CLS

### Subsystem Metrics (L2)
- `{subsystem}_services_healthy`
- `{subsystem}_requests_total`
- `{subsystem}_request_duration_seconds`
- `{subsystem}_inter_service_calls_total`

### System Metrics (L3)
- `{system}_health_score`
- `{system}_throughput`
- `{system}_end_to_end_latency`
- `{system}_success_rate`
- `{system}_availability`

### Workflow Metrics (L4)
- `{workflow}_completions_total`
- `{workflow}_duration_seconds`
- `{workflow}_errors_total`
- `{workflow}_user_satisfaction`
- `{workflow}_abandonment_rate`

---

## 🤖 AI Office Integration

Templates integrate with AI Office through EventBus:

### Event Types Published:
- `scenario.generation.started`
- `scenario.l1.generated`
- `scenario.l2.generated`
- `scenario.l3.generated`
- `scenario.l4.generated`
- `scenario.generation.completed`
- `scenario.execution.started`
- `scenario.execution.completed`
- `scenario.improved`
- `scenario.archived`

### AI Office Subscriptions:
- **MIO Manager**: All `scenario.*`, `execution.*`, `analysis.*`
- **Analytics Specialist**: `scenario.execution.completed`, `execution.completed`
- **Project Agent**: `scenario.execution.completed`, `task.created`
- **Predictive Service**: `analysis.completed`
- **AI Orchestration**: `prediction.created`
- **DevOps Agent**: `task.created` (for test execution)

---

## 🗄️ Database Schema

Scenarios are stored in PostgreSQL:

```sql
CREATE SCHEMA scenario_intelligence;

CREATE TABLE scenario_intelligence.scenarios (
  id UUID PRIMARY KEY,
  level INT NOT NULL CHECK (level IN (1,2,3,4)),
  name TEXT NOT NULL,
  content JSONB NOT NULL,  -- Full scenario YAML as JSON
  version TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active','deprecated','archived')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE scenario_intelligence.executions (
  id UUID PRIMARY KEY,
  scenario_id UUID REFERENCES scenario_intelligence.scenarios(id),
  triggered_by TEXT NOT NULL,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  status TEXT NOT NULL,
  results JSONB,
  metrics JSONB
);

CREATE TABLE scenario_intelligence.learning (
  id UUID PRIMARY KEY,
  scenario_id UUID REFERENCES scenario_intelligence.scenarios(id),
  patterns JSONB,
  predictions JSONB,
  recommendations JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE scenario_intelligence.archive (
  id UUID PRIMARY KEY,
  scenario_id UUID REFERENCES scenario_intelligence.scenarios(id),
  version TEXT NOT NULL,
  content JSONB NOT NULL,
  archived_at TIMESTAMPTZ DEFAULT NOW(),
  reason TEXT
);
```

---

## 🚀 Next Steps

1. **Create Scenario Manager Service**
   - FastAPI service (port TBD)
   - REST API for scenario CRUD
   - EventBus integration
   - Database integration

2. **Implement Generators**
   - L1 Platform Generator
   - L1 Application Generator
   - L2 Generator
   - L3 Generator
   - L4 AI Generator (OpenAI/Claude integration)

3. **Generate Initial Scenarios**
   - Run generators to create 652 scenarios
   - Store in database
   - Archive golden standards

4. **Integrate with Simulation Service**
   - Connect with `/platform-services/simulation/simulation-service`
   - Use scenarios for simulation exercises
   - Feed simulation results back to learning system

5. **Setup Continuous Improvement**
   - Connect to Analytics Specialist
   - Connect to Predictive Service
   - Connect to AI Orchestration
   - Enable automated scenario improvement

---

## 📝 Template Usage Examples

### Example: Generate L1 Service Scenario

```python
from scenario_manager import ScenarioGenerator

# Load template
template = load_yaml("golden_standard_l1.yaml")

# Load service info from catalog
service = get_service_from_catalog("mio-manager")

# Fill template
scenario = template.fill({
    "service_name": service.name,
    "port": service.port,
    "criticality": service.criticality,
    "subsystem_name": service.subsystem,
    "internal_dependencies": service.dependencies.internal,
    "external_dependencies": service.dependencies.external
})

# Generate scenario file
save_scenario(f"l1-service-mio-manager.yaml", scenario)
```

### Example: Generate L4 Workflow Scenario (AI)

```python
from scenario_manager import AIScenarioGenerator
from openai import OpenAI

# Initialize AI generator
ai_gen = AIScenarioGenerator(model="gpt-4")

# Context from platform
context = {
    "workflow_name": "BCM BIA Creation Workflow",
    "user_role": "BCM Manager",
    "business_objective": "Complete Business Impact Analysis",
    "systems_involved": ["bcm_portal", "bia_service", "workflow_intelligence"],
    "compliance_requirements": ["ISO 22301"]
}

# Generate using AI
scenario = ai_gen.generate_l4_scenario(
    template="golden_standard_l4.yaml",
    context=context
)

# Review and save
if review_scenario(scenario):
    save_scenario(f"l4-workflow-bcm-bia-creation.yaml", scenario)
```

---

## 🔗 Related Documentation

- [Scenario Generation System Design](/catalogs/SCENARIO_GENERATION_SYSTEM_DESIGN.md) - Complete system architecture
- [Subsystems Catalog](/catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml) - 12 subsystems
- [Systems Catalog](/catalogs/systems/SYSTEMS_CATALOG.yaml) - 19 functional systems
- [User Applications Catalog](/catalogs/business-services/USER_APPLICATIONS_CATALOG.yaml) - 4 apps + 12 modules
- [Service Catalog](/infrastructure/SERVICE_CATALOG_DETAILED.yaml) - 46 platform services

---

**Created by**: Scenario Manager
**Last Updated**: 2025-10-12
**Status**: ✅ Complete - Ready for Implementation
