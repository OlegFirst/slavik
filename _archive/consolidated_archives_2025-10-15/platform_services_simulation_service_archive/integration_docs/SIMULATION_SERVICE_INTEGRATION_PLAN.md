# Simulation Service Integration Plan
# Comprehensive Analysis & Integration Strategy

**Date**: 2025-10-13
**Version**: 1.0.0
**Status**: Analysis Complete - Ready for Integration
**Target Service**: `/platform-services/simulation/simulation-service`

---

## Executive Summary

This document provides a comprehensive integration plan for the **simulation-service** into the AI-Platform-ISO ecosystem. After analyzing the system architecture, database schemas, EventBus patterns, service discovery, and existing catalogs, this report identifies all integration points, requirements, and step-by-step implementation tasks.

**Key Findings**:
- Simulation service is **80% integrated** but missing critical platform connections
- Database schema exists in `intelligence.simulations` but service needs dedicated schema
- EventBus client exists but subscriptions not configured
- Service not registered in Service Discovery
- Missing from Service Catalog entries
- No MIO Manager monitoring integration
- RAG/Knowledge system connections incomplete

---

## Table of Contents

1. [Current System Architecture](#1-current-system-architecture)
2. [Simulation Service Current State](#2-simulation-service-current-state)
3. [Database Integration Analysis](#3-database-integration-analysis)
4. [EventBus Integration Analysis](#4-eventbus-integration-analysis)
5. [Service Discovery Integration](#5-service-discovery-integration)
6. [Catalog Integration Requirements](#6-catalog-integration-requirements)
7. [Platform Services Integration](#7-platform-services-integration)
8. [Missing Dependencies](#8-missing-dependencies)
9. [Step-by-Step Integration Checklist](#9-step-by-step-integration-checklist)
10. [Integration Verification](#10-integration-verification)

---

## 1. Current System Architecture

### 1.1 Platform Overview

```
AI-Platform-ISO Architecture (46 Services, 11 Subsystems, 19 Functional Systems)

Layer 0: Infrastructure Foundation
├── PostgreSQL (5432) - Multi-schema database with 29 schemas
├── Redis (6379) - Caching + Session + EventBus backend
├── EventBus (8055) - Event-driven coordination (Redis Streams)
├── API Gateway (8000) - Single entry point, auth, rate limiting
├── Service Discovery (8500) - Consul-based service registry
├── Prometheus (9090) - Metrics collection (30+ services)
└── Grafana (3000) - 18 dashboards

Layer 1: AI Office Infrastructure (8 Agents)
├── MIO Manager (8046) - EYES: Monitoring + Intelligence + Reaction
├── AI Orchestrator (8026) - Agent coordination
├── Agent Router (8027) - Task routing
├── Analytics Specialist (8094) - Platform analytics
├── DB Intelligence (8051) - Database optimization
├── DevOps Agent (8097) - Infrastructure operations
├── Project Agent (8096) - Project management
└── AI Event Manager (8098) - AI event coordination

Layer 2: Intelligent Core (12 Services)
├── Workflow Intelligence (8037) - BRAIN: Goals + Rules + Governance
├── AI Orchestration (8030) - Decision center, delegation, memory
├── Scenario Intelligence (8090) - 4-level scenario execution
├── AI Foundation (8025) - RAG, LLM Router, ML models
├── Predictive (8031) - Journey prediction, demand forecasting
├── Expertise Center (8035) - BCM domain experts
├── Workflow Engine (8036) - BPMN workflows, Temporal integration
├── AI Workflow Optimizer (8038) - ML-powered optimization
├── Event Intelligence (8039) - Event pattern learning
├── Community Intelligence (8030) - Peer review, case curation
├── Collective (8032) - Anonymous collaboration (K-anonymity)
└── Coordination Center (PLANNED Q1 2026)

Layer 3: Platform Services (11 Services)
├── BIA Service (8008) - Business Impact Analysis
├── Risk Service (8009) - Risk Assessment
├── Compliance Service (8010) - ISO 22301 compliance
├── Plans Service (8011) - BC/DR Plans
├── Planning Service (8012) - Strategic planning
├── Response Service (8013) - Incident response
├── Learning Service (8014) - Training & awareness
├── Governance Service (8015) - Governance framework
├── Documents Service (8016) - Document generation
├── Validation Service (8017) - Testing & validation
└── Digital Twin (8096) - System state modeling

Layer 4: Interface
├── Admin Panel (3030) - Management UI
└── Platform UI (RESERVED)
```

### 1.2 Critical Integration Points

**EventBus** (Port 8055):
- Backend: Redis Streams
- Event Types: 35+ event patterns per scenario
- Transport: Async pub/sub
- Location: `/infrastructure/eventbus/`

**Service Discovery** (Port 8500):
- Backend: Consul
- Features: Health checks, metadata, KPI tracking
- Integration: v2.0 with Service Catalog
- Location: `/infrastructure/runtime/service-discovery/`

**MIO Manager** (Port 8046):
- Role: Platform EYES (observation + intelligence)
- Monitors: All services via Prometheus + EventBus
- Checks: Metrics coverage, health, KPIs
- Location: `/infrastructure/AI-office-infrastructure/mio-manager/`

**Database** (Port 5432):
- Type: PostgreSQL via Supabase
- Schemas: 29 schemas (System, Platform, Business)
- Key Schemas: `intelligence`, `workflow_intelligence`, `validation`
- RLS: Enabled for multi-tenancy
- Location: `/infrastructure/database/postgresql/`

---

## 2. Simulation Service Current State

### 2.1 Service Overview

**Location**: `/platform-services/simulation/simulation-service/`
**Port**: 8095 (configured in settings.py)
**Status**: Development - Not Integrated
**Technology**: FastAPI + SQLAlchemy + Redis

### 2.2 Existing Components

#### A. Core Implementation (COMPLETE)
```
simulation-service/
├── main.py                          ✅ FastAPI app with lifespan
├── config/settings.py               ✅ Pydantic settings (comprehensive)
├── storage/
│   ├── database.py                  ✅ DatabaseManager (PostgreSQL + Redis)
│   ├── models.py                    ✅ ORM models (4 tables)
│   └── repositories/                ✅ Repository pattern (4 repos)
├── core/
│   ├── orchestrator.py              ✅ Simulation orchestration
│   ├── scenario_flow_manager.py     ✅ Scenario execution
│   ├── ai_scenario_generator.py     ✅ AI-powered generation
│   ├── scenario_classifier.py       ✅ Scenario classification
│   ├── metrics_calculator.py        ✅ KPI calculation
│   └── scenario_learning.py         ✅ Learning from results
├── engines/
│   ├── jaamsim_engine.py            ✅ JaamSim integration
│   ├── simpy_engine.py              ✅ SimPy DES engine
│   └── (5 more engines)             ✅ Complete
├── api/
│   ├── bridge_router.py             ✅ Integration orchestration
│   ├── scenario_advanced_router.py  ✅ AI-powered scenarios
│   └── (4 more routers)             ✅ Complete
└── integration/
    ├── eventbus_client.py           ⚠️  CLIENT EXISTS - needs subscription setup
    ├── foundation_client.py         ✅ AI Foundation client
    ├── knowledge_client.py          ✅ Knowledge Center client
    ├── community_client.py          ✅ Community Intelligence client
    ├── scenario_client.py           ✅ Scenario Intelligence client
    └── scenario_orchestrator_client.py ✅ Orchestrator client
```

#### B. Missing Components (TO BE ADDED)

```
❌ Service Discovery registration
❌ MIO Manager metrics integration
❌ Service Catalog entry
❌ Prometheus /metrics endpoint
❌ EventBus subscriptions (handlers exist but not registered)
❌ Health check integration with Service Discovery
❌ Dedicated simulation schema in database
❌ RLS policies for simulation tables
❌ KPI.yaml registration
❌ SERVICE_INFO.yaml
```

### 2.3 Current Configuration

**From `config/settings.py`**:
```python
port: 8095
service_name: "simulation-service"

# Platform Integration URLs (configured but not used):
eventbus_url: "http://localhost:8055"
ai_orchestrator_url: "http://localhost:8026"
workflow_intelligence_url: "http://localhost:8037"
ai_foundation_url: "http://localhost:8025"
community_intelligence_url: "http://localhost:8030"
predictive_journey_url: "http://localhost:8031"
scenario_orchestrator_url: "http://localhost:8085"
digital_twin_url: "http://localhost:8096"

# Database
database_url: "postgresql://simulation_user:simulation_pass@localhost:5432/simulation_db"
redis_url: "redis://localhost:6379/0"

# Engines
jaamsim_enabled: true
simpy_enabled: true
```

### 2.4 EventBus Integration (Partial)

**Publishing Events** (IMPLEMENTED):
```python
# From integration/eventbus_client.py
- publish_simulation_created(simulation_id, config)
- publish_simulation_started(simulation_id)
- publish_progress_update(simulation_id, progress)
- publish_simulation_completed(simulation_id, results)
- publish_simulation_failed(simulation_id, error)
- publish_case_created(case_id)
- publish_knowledge_stored(knowledge_id)
- publish_community_contributed(contribution_id)
```

**Subscribing Events** (NOT IMPLEMENTED):
```python
❌ No subscriptions configured
❌ No event handlers registered in main.py
❌ No async consumer started
```

---

## 3. Database Integration Analysis

### 3.1 Existing Database Schema

**Current State**: Simulation tables exist in TWO locations:

#### A. `intelligence.simulations` (Migration 005)
```sql
-- Location: /infrastructure/database/postgresql/migrations_source/005_intelligence_schema.sql

CREATE TABLE intelligence.simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    digital_twin_id UUID REFERENCES intelligence.digital_twins(id),
    organization_id UUID REFERENCES public.organizations(id),

    -- Config
    simulation_name VARCHAR(255),
    scenario_type VARCHAR(50),
    input_parameters JSONB,
    assumptions JSONB,

    -- Execution
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Results
    results JSONB,
    confidence_score DECIMAL(5,2),
    key_findings TEXT[],
    recommendations JSONB,

    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS enabled
ALTER TABLE intelligence.simulations ENABLE ROW LEVEL SECURITY;
```

**Purpose**: Digital Twin simulations (integration with digital-twin service)

#### B. `simulation.*` Schema (Simulation-Service Models)
```python
# Location: /platform-services/simulation/simulation-service/storage/models.py

class Simulation(Base):
    __tablename__ = "simulations"
    __table_args__ = {'schema': 'simulation'}

    # Comprehensive simulation model with:
    # - Multi-tenancy (tenant_id)
    # - Simulation types (what_if, monte_carlo, scenario, optimization)
    # - Engines (jaamsim, simpy, ciw, external)
    # - Parameters, status, metadata
    # - Relationships to executions

class Scenario(Base):
    __tablename__ = "scenarios"
    __table_args__ = {'schema': 'simulation'}

    # BCM exercise scenarios with:
    # - Categories (cyber, pandemic, disaster)
    # - Complexity (1-5)
    # - Timeline, injects, success_metrics
    # - AI generation metadata

class SimulationExecution(Base):
    __tablename__ = "executions"
    __table_args__ = {'schema': 'simulation'}

    # Execution history

class SimulationResult(Base):
    __tablename__ = "results"
    __table_args__ = {'schema': 'simulation'}

    # Time-series results (optimized for TimescaleDB)
```

**Purpose**: Dedicated simulation service tables (BCM exercises + modeling)

### 3.2 Database Integration Requirements

#### ACTION REQUIRED:

**Option 1: Create Dedicated Schema (RECOMMENDED)**
```sql
-- Create new migration: 045_simulation_service_schema.sql

-- 1. Create simulation schema
CREATE SCHEMA IF NOT EXISTS simulation;

-- 2. Create tables (from models.py)
CREATE TABLE simulation.simulations (...);
CREATE TABLE simulation.scenarios (...);
CREATE TABLE simulation.executions (...);
CREATE TABLE simulation.results (...);

-- 3. Enable RLS
ALTER TABLE simulation.simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.results ENABLE ROW LEVEL SECURITY;

-- 4. Create RLS policies (multi-tenant)
CREATE POLICY "Simulations visible to org members"
    ON simulation.simulations FOR SELECT
    USING (auth.is_org_member_by_tenant(tenant_id));

CREATE POLICY "Simulations manageable by org admins"
    ON simulation.simulations FOR ALL
    USING (auth.is_org_admin_by_tenant(tenant_id));

-- Repeat for other tables

-- 5. Create indexes
CREATE INDEX idx_simulations_tenant ON simulation.simulations(tenant_id);
CREATE INDEX idx_simulations_status ON simulation.simulations(status);
CREATE INDEX idx_simulations_type ON simulation.simulations(simulation_type);
-- ... more indexes
```

**Option 2: Use Existing intelligence.simulations**
- Extend existing table with simulation-service fields
- Add foreign keys to link with digital-twin
- Less flexible, tighter coupling

**RECOMMENDATION**: Option 1 (dedicated schema) for:
- Clear separation of concerns
- Independent evolution
- Simpler RLS policies
- Better performance (no joins with digital_twins)

### 3.3 RLS Helper Functions Needed

```sql
-- Add to 002_rls_functions.sql or create new migration

CREATE OR REPLACE FUNCTION auth.is_org_member_by_tenant(
    p_tenant_id TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    -- Check if current user belongs to tenant
    RETURN EXISTS (
        SELECT 1 FROM public.user_tenants ut
        WHERE ut.user_id = auth.uid()
        AND ut.tenant_id = p_tenant_id::UUID
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION auth.is_org_admin_by_tenant(
    p_tenant_id TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    -- Check if current user is admin of tenant
    RETURN EXISTS (
        SELECT 1 FROM public.user_tenants ut
        WHERE ut.user_id = auth.uid()
        AND ut.tenant_id = p_tenant_id::UUID
        AND ut.role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 4. EventBus Integration Analysis

### 4.1 EventBus Architecture

**Location**: `/infrastructure/eventbus/`
**Backend**: Redis Streams
**Client**: `/infrastructure/eventbus/core/interface.py`

**Event Model**:
```python
# From /infrastructure/eventbus/core/events.py

@dataclass
class Event:
    id: str                          # UUID
    type: str                        # e.g., "simulation.created"
    data: Dict[str, Any]             # Event payload
    source: str                      # "simulation-service"
    tenant_id: str                   # Multi-tenancy
    correlation_id: Optional[str]    # Tracing
    timestamp: datetime
    priority: EventPriority          # LOW, NORMAL, HIGH, CRITICAL
    retry_count: int = 0
    max_retries: int = 3
```

### 4.2 Simulation-Service Event Patterns

#### A. Events to Publish (IMPLEMENTED)

```python
# simulation.lifecycle
simulation.created              # New simulation configured
simulation.started              # Simulation execution started
simulation.progress.updated     # Progress update (for long-running)
simulation.completed            # Simulation finished successfully
simulation.failed               # Simulation failed

# simulation.scenario
simulation.scenario.generated   # AI-generated scenario created
simulation.scenario.classified  # Scenario classified (complexity, category)

# simulation.learning
simulation.case.created         # Learning case extracted
simulation.knowledge.stored     # Knowledge stored in RAG
simulation.community.contributed # Contributed to community

# simulation.analysis
simulation.metrics.calculated   # KPIs calculated
simulation.results.analyzed     # Results analyzed
```

#### B. Events to Subscribe (TO BE IMPLEMENTED)

```python
# Listen to other services for integration

# From Scenario Intelligence (8090)
scenario.execution.requested    # Execute simulation for scenario
  → Handler: start_scenario_simulation()

# From Digital Twin (8096)
digital_twin.state.changed      # Twin state updated → re-run simulation
  → Handler: update_simulation_parameters()

# From Predictive (8031)
predictive.demand.forecasted    # Demand forecast → input to simulation
  → Handler: adjust_simulation_load()

# From Workflow Intelligence (8037)
workflow.pdca.plan              # PDCA Plan → trigger simulation test
  → Handler: execute_pdca_simulation()

# From BIA Service (8008)
bia.critical_function.identified # New critical function → simulate impact
  → Handler: create_impact_simulation()

# From Community Intelligence (8030)
community.scenario.shared       # Community scenario → add to library
  → Handler: import_community_scenario()

# From Governance Service (8015)
governance.policy.changed       # Policy change → simulate compliance
  → Handler: test_policy_simulation()
```

### 4.3 EventBus Integration Code

**Current Implementation** (`integration/eventbus_client.py`):
```python
class SimulationEventBusClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = EventBusClient(
            backend='redis',
            redis_url=settings.eventbus_redis_url
        )

    async def connect(self):
        await self.client.initialize()

    # Publishing methods exist (8 methods) ✅
    # Subscription methods MISSING ❌
```

**Required Additions**:
```python
# Add to integration/eventbus_client.py

async def subscribe_to_scenarios(self, handler: Callable):
    """Subscribe to scenario execution requests"""
    await self.client.subscribe(
        'scenario.execution.requested',
        handler
    )

async def subscribe_to_digital_twin(self, handler: Callable):
    """Subscribe to digital twin events"""
    await self.client.subscribe(
        'digital_twin.state.changed',
        handler
    )

# ... add 6 more subscription methods

async def start_subscriptions(self):
    """Start all subscriptions"""
    from api.event_handlers import SimulationEventHandlers

    handlers = SimulationEventHandlers()

    await self.subscribe_to_scenarios(handlers.handle_scenario_request)
    await self.subscribe_to_digital_twin(handlers.handle_twin_update)
    # ... register all handlers

    await self.client.start_consumer()
```

**New File Required**: `api/event_handlers.py`
```python
"""
Event handlers for simulation-service
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SimulationEventHandlers:
    """Handles incoming EventBus events"""

    async def handle_scenario_request(self, event: Dict[str, Any]):
        """Handle scenario execution request"""
        logger.info(f"Scenario request received: {event}")
        # 1. Extract scenario_id from event
        # 2. Load scenario from database
        # 3. Create simulation
        # 4. Start execution
        # 5. Publish simulation.started event

    async def handle_twin_update(self, event: Dict[str, Any]):
        """Handle digital twin state change"""
        logger.info(f"Twin update received: {event}")
        # 1. Find related simulations
        # 2. Update parameters
        # 3. Re-run if auto-update enabled

    # ... implement all 8 handlers
```

---

## 5. Service Discovery Integration

### 5.1 Service Discovery Architecture

**Location**: `/infrastructure/runtime/service-discovery/`
**Type**: Consul (Port 8500)
**Version**: v2.0 with Service Catalog integration
**Features**:
- Service registration + health checks
- Metadata + KPI tracking
- EventBus integration (publishes service lifecycle events)
- Service Catalog sync

### 5.2 Registration Requirements

**File to Create**: `/platform-services/simulation/simulation-service/SERVICE_INFO.yaml`

```yaml
# SERVICE_INFO.yaml for simulation-service

service:
  name: simulation-service
  display_name: "Simulation & Modeling Service"
  version: "1.0.0"
  description: |
    BCM simulation service with AI-powered scenario generation and multi-engine support.
    Supports JaamSim, SimPy, and internal simulation engines.

  port: 8095
  protocol: http
  health_check_path: /health
  metrics_path: /metrics

  category: platform_services
  subsystem: bcm_business_logic
  functional_system: testing_validation

  iso_22301_clauses:
    - "8.4.6"  # Testing
    - "8.5"    # Evaluation and improvement
    - "10.1"   # Monitoring and measurement

  tags:
    - simulation
    - modeling
    - bcm
    - testing
    - scenario-execution
    - jaamsim
    - simpy

  capabilities:
    - BCM scenario simulation
    - What-if analysis
    - Monte Carlo simulation
    - AI-powered scenario generation
    - Multi-engine support (JaamSim, SimPy)
    - Real-time visualization
    - Results analytics
    - PDCA integration

  dependencies:
    required:
      - postgresql
      - redis
      - eventbus
    optional:
      - ai-foundation          # For RAG + LLM
      - scenario-intelligence  # For scenario library
      - community-intelligence # For community scenarios
      - predictive            # For demand forecasting
      - workflow-intelligence # For PDCA integration

  integrations:
    - service: ai-foundation
      type: client
      purpose: RAG search + LLM generation
    - service: scenario-intelligence
      type: bi-directional
      purpose: Scenario execution + learning
    - service: community-intelligence
      type: client
      purpose: Community scenario sharing
    - service: digital-twin
      type: bi-directional
      purpose: Twin state → simulation input
    - service: bia-service
      type: subscriber
      purpose: Critical function impact simulation

  kpis:
    - name: simulation_executions_total
      type: counter
      description: "Total number of simulations executed"
      labels: [simulation_type, engine, status]

    - name: simulation_duration_seconds
      type: histogram
      description: "Simulation execution time"
      buckets: [1, 5, 10, 30, 60, 300, 600]

    - name: scenario_generation_duration_seconds
      type: histogram
      description: "AI scenario generation time"
      buckets: [1, 5, 10, 30]

    - name: simulation_results_quality_score
      type: gauge
      description: "Average quality score of simulation results"
      range: [0, 10]

    - name: active_simulations
      type: gauge
      description: "Number of currently running simulations"

    - name: scenarios_library_size
      type: gauge
      description: "Number of scenarios in library"

  health_checks:
    liveness:
      path: /health/live
      interval: 10s
      timeout: 2s

    readiness:
      path: /health/ready
      interval: 10s
      timeout: 5s
      checks:
        - database
        - redis
        - eventbus

  resources:
    memory_limit: 2Gi
    cpu_limit: "2"
    memory_request: 512Mi
    cpu_request: "0.5"

  environment_variables:
    PORT:
      required: true
      default: 8095
    DATABASE_URL:
      required: true
      secret: true
    REDIS_URL:
      required: true
    EVENTBUS_URL:
      required: true
      default: "http://localhost:8055"
    JAAMSIM_ENABLED:
      required: false
      default: "true"
    SIMPY_ENABLED:
      required: false
      default: "true"

  documentation:
    readme: /platform-services/simulation/simulation-service/README.md
    api_docs: http://localhost:8095/docs
    architecture: /platform-services/simulation/simulation-service/docs/ARCHITECTURE.md

  ownership:
    team: "BCM Platform Team"
    primary_contact: "simulation-team@company.com"
    on_call: "platform-oncall@company.com"

  deployment:
    docker:
      image: "simulation-service:latest"
      build_context: ./
      dockerfile: Dockerfile

    kubernetes:
      replicas: 2
      namespace: platform-services
      service_type: ClusterIP

    startup_order: 50  # After infrastructure (1-30), AI core (31-49)
```

### 5.3 Registration Code

**Add to `main.py`** (in lifespan startup):
```python
from integrations.service_discovery_client import ServiceDiscoveryClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing startup code ...

    # Register with Service Discovery
    logger.info("Registering with Service Discovery...")
    sd_client = ServiceDiscoveryClient(
        service_discovery_url=settings.service_discovery_url,
        service_name="simulation-service",
        service_port=settings.port,
        health_check_path="/health"
    )

    await sd_client.register()
    logger.info("✅ Registered with Service Discovery")

    # Start health check heartbeat
    sd_client.start_heartbeat(interval=30)

    yield

    # Shutdown
    await sd_client.deregister()
    logger.info("✅ Deregistered from Service Discovery")
```

**New File Required**: `integration/service_discovery_client.py`
```python
"""
Service Discovery integration client
"""
import httpx
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ServiceDiscoveryClient:
    def __init__(
        self,
        service_discovery_url: str,
        service_name: str,
        service_port: int,
        health_check_path: str = "/health"
    ):
        self.sd_url = service_discovery_url
        self.service_name = service_name
        self.service_port = service_port
        self.health_path = health_check_path
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def register(self):
        """Register service with Service Discovery"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.sd_url}/v1/agent/service/register",
                    json={
                        "Name": self.service_name,
                        "Port": self.service_port,
                        "Tags": ["simulation", "bcm", "platform-services"],
                        "Meta": {
                            "version": "1.0.0",
                            "category": "platform_services"
                        },
                        "Check": {
                            "HTTP": f"http://localhost:{self.service_port}{self.health_path}",
                            "Interval": "10s",
                            "Timeout": "5s"
                        }
                    }
                )
                response.raise_for_status()
                logger.info(f"Registered {self.service_name} with Service Discovery")
        except Exception as e:
            logger.error(f"Service Discovery registration failed: {e}")
            # Non-fatal - service can run without registration

    async def deregister(self):
        """Deregister service"""
        try:
            async with httpx.AsyncClient() as client:
                await client.put(
                    f"{self.sd_url}/v1/agent/service/deregister/{self.service_name}"
                )
        except Exception as e:
            logger.error(f"Service Discovery deregistration failed: {e}")

    def start_heartbeat(self, interval: int = 30):
        """Start periodic heartbeat"""
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(interval))

    async def _heartbeat_loop(self, interval: int):
        """Periodic heartbeat to Service Discovery"""
        while True:
            try:
                await asyncio.sleep(interval)
                # Service Discovery checks health via HTTP check
                # No explicit heartbeat needed with Consul
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
```

---

## 6. Catalog Integration Requirements

### 6.1 Service Catalog Location

**Primary Catalog**: `/catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml`
**Current State**: Contains 45 services, simulation-service NOT included

### 6.2 Required Catalog Entries

#### A. Add to SERVICE_CATALOG_DETAILED.yaml

```yaml
# Add to platform_services section

platform_services:
  # ... existing services ...

  simulation-service:
    name: simulation-service
    display_name: Simulation & Modeling Service
    registration:
      type: platform_service
      status: production
      environment: docker

    description: |
      BCM simulation service with AI-powered scenario generation and multi-engine support.
      Provides what-if analysis, Monte Carlo simulation, and scenario execution.

    capabilities:
      - BCM scenario simulation
      - What-if analysis
      - Monte Carlo simulation
      - AI-powered scenario generation
      - Multi-engine support (JaamSim, SimPy)
      - Real-time visualization
      - Results analytics
      - PDCA integration

    features:
      - JaamSim discrete-event simulation
      - SimPy process simulation
      - Internal optimization engine
      - AI scenario generator (LLM-powered)
      - Real-time progress tracking (WebSocket)
      - Results visualization (D3.js)
      - Community scenario sharing

    runtime:
      port: 8095
      protocol: http
      health_endpoint: /health
      metrics_endpoint: /metrics
      api_docs: /docs

    dependencies:
      required:
        - postgresql
        - redis
        - eventbus
      optional:
        - ai-foundation
        - scenario-intelligence
        - community-intelligence
        - predictive
        - workflow-intelligence

    integrations:
      - service: ai-foundation
        integration_type: client
        description: RAG search + LLM generation

      - service: scenario-intelligence
        integration_type: bi-directional
        description: Scenario library + execution feedback

      - service: community-intelligence
        integration_type: client
        description: Community scenario import/export

      - service: digital-twin
        integration_type: bi-directional
        description: Twin state → simulation input

      - service: workflow-intelligence
        integration_type: subscriber
        description: PDCA cycle simulation testing

    kpis:
      - name: simulation_executions_total
        type: counter
        description: Total simulations executed
        threshold_warning: 1000
        threshold_critical: 5000

      - name: simulation_duration_seconds_p95
        type: gauge
        description: 95th percentile execution time
        target: 60
        threshold_warning: 120
        threshold_critical: 300

      - name: scenarios_library_size
        type: gauge
        description: Number of scenarios in library
        target: 100

      - name: simulation_results_quality_score_avg
        type: gauge
        description: Average quality score (0-10)
        target: 8.0
        threshold_warning: 7.0
        threshold_critical: 6.0

    eventbus:
      publishes:
        - event: simulation.created
          priority: normal
        - event: simulation.started
          priority: normal
        - event: simulation.completed
          priority: normal
        - event: simulation.failed
          priority: high
        - event: simulation.scenario.generated
          priority: normal

      subscribes:
        - event: scenario.execution.requested
          handler: handle_scenario_request
        - event: digital_twin.state.changed
          handler: handle_twin_update
        - event: workflow.pdca.plan
          handler: execute_pdca_simulation
        - event: bia.critical_function.identified
          handler: create_impact_simulation

    deployment:
      how_to_run: Docker Compose / Kubernetes
      startup_command: uvicorn main:app --host 0.0.0.0 --port 8095
      environment_variables:
        DATABASE_URL:
          required: true
          secret: true
        REDIS_URL:
          required: true
        EVENTBUS_URL:
          required: true
        JAAMSIM_PATH:
          required: false
          default: /opt/jaamsim

    ownership:
      team: BCM Platform Team
      primary_contact: simulation-team@company.com

    documentation:
      main: /platform-services/simulation/simulation-service/README.md
      api_docs: http://localhost:8095/docs
```

#### B. Add to SUBSYSTEMS_CATALOG.yaml

```yaml
# catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml

subsystems:
  # ... existing subsystems ...

  platform_services:
    services:
      # ... existing services ...
      - simulation-service  # ADD THIS
```

#### C. Add to SYSTEMS_CATALOG.yaml

```yaml
# catalogs/systems/SYSTEMS_CATALOG.yaml

functional_systems:
  testing_validation:
    name: "Testing & Validation"
    purpose: "BCM plan testing, exercises, and continuous validation"
    services:
      - validation-service
      - simulation-service  # ADD THIS

    capabilities:
      - Plan testing
      - Exercise management
      - Simulation modeling
      - Scenario execution
      - Results validation
```

---

## 7. Platform Services Integration

### 7.1 MIO Manager Integration (EYES)

**MIO Manager** monitors all services via:
1. Prometheus metrics scraping
2. EventBus event monitoring
3. Service Discovery health checks

**Required Actions**:

#### A. Add Prometheus /metrics Endpoint

```python
# Add to main.py

from prometheus_client import Counter, Histogram, Gauge, make_asgi_app

# Define metrics
simulation_executions_total = Counter(
    'simulation_executions_total',
    'Total simulations executed',
    ['simulation_type', 'engine', 'status']
)

simulation_duration_seconds = Histogram(
    'simulation_duration_seconds',
    'Simulation execution time',
    buckets=[1, 5, 10, 30, 60, 300, 600]
)

scenario_generation_duration = Histogram(
    'scenario_generation_duration_seconds',
    'AI scenario generation time',
    buckets=[1, 5, 10, 30]
)

simulation_quality_score = Gauge(
    'simulation_results_quality_score',
    'Average quality score of simulation results'
)

active_simulations = Gauge(
    'active_simulations',
    'Number of currently running simulations'
)

scenarios_library_size = Gauge(
    'scenarios_library_size',
    'Number of scenarios in library'
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

#### B. Instrument Code with Metrics

```python
# Example: In core/orchestrator.py

async def execute_simulation(self, simulation_id: int):
    """Execute simulation with metrics"""

    # Increment active simulations
    active_simulations.inc()

    try:
        start_time = time.time()

        # Execute simulation
        result = await self._run_simulation(simulation_id)

        # Record duration
        duration = time.time() - start_time
        simulation_duration_seconds.observe(duration)

        # Record execution
        simulation_executions_total.labels(
            simulation_type=result.type,
            engine=result.engine,
            status='success'
        ).inc()

        # Record quality
        if result.quality_score:
            simulation_quality_score.set(result.quality_score)

        return result

    except Exception as e:
        simulation_executions_total.labels(
            simulation_type='unknown',
            engine='unknown',
            status='failed'
        ).inc()
        raise

    finally:
        active_simulations.dec()
```

#### C. MIO Manager Will Automatically:
- Scrape /metrics every 15 seconds
- Check if service is registered (via Service Discovery events)
- Verify metrics endpoint accessibility
- Publish observations to EventBus if issues found

### 7.2 AI Foundation Integration (RAG)

**Current State**: `integration/foundation_client.py` exists
**Required**: Verify connection + test

```python
# Test AI Foundation integration

from integration.foundation_client import AIFoundationClient

client = AIFoundationClient(
    base_url="http://localhost:8025"
)

# Test RAG search
results = await client.search_similar_scenarios(
    query="hospital cyber attack",
    limit=5
)

# Test LLM generation
scenario = await client.generate_scenario(
    category="cyber",
    complexity=3,
    industry="healthcare"
)
```

### 7.3 Scenario Intelligence Integration

**Current State**: `integration/scenario_client.py` exists
**Purpose**: Bi-directional integration
- Simulation → Scenario Intelligence: Execution results, learning
- Scenario Intelligence → Simulation: Scenario execution requests

**Required Actions**:

#### A. Register as Scenario Execution Engine
```python
# In lifespan startup

from integration.scenario_client import ScenarioIntelligenceClient

scenario_client = ScenarioIntelligenceClient(
    base_url="http://localhost:8090"
)

# Register as execution engine
await scenario_client.register_engine({
    "engine_name": "simulation-service",
    "engine_type": "simulation",
    "capabilities": [
        "bcm_scenarios",
        "what_if_analysis",
        "monte_carlo",
        "discrete_event_simulation"
    ],
    "supported_scenario_types": [
        "cyber",
        "pandemic",
        "disaster",
        "supply_chain",
        "operational"
    ]
})
```

#### B. Subscribe to Scenario Execution Requests
```python
# Already covered in EventBus section
# Subscribe to: scenario.execution.requested
```

### 7.4 Workflow Intelligence Integration (PDCA)

**Purpose**: Integrate with PDCA cycle for continuous improvement

```python
# integration/workflow_intelligence_client.py (NEW FILE)

from typing import Dict, Any
import httpx

class WorkflowIntelligenceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def register_pdca_cycle(
        self,
        cycle_type: str,
        plan: Dict[str, Any],
        simulation_id: int
    ):
        """Register PDCA cycle with simulation"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/pdca/cycles",
                json={
                    "cycle_type": cycle_type,
                    "plan": plan,
                    "metadata": {
                        "simulation_id": simulation_id,
                        "source": "simulation-service"
                    }
                }
            )
            return response.json()

    async def report_pdca_check(
        self,
        cycle_id: str,
        results: Dict[str, Any]
    ):
        """Report simulation results as PDCA Check"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/pdca/cycles/{cycle_id}/check",
                json=results
            )
            return response.json()
```

---

## 8. Missing Dependencies

### 8.1 Critical Missing Components

#### A. KPI.yaml (EXISTS but needs registration)

**Current File**: `/platform-services/simulation/simulation-service/KPI.yaml`

**Action**: Verify format matches platform standard

```yaml
# Verify KPI.yaml format

service_name: simulation-service
version: "1.0.0"

kpis:
  - name: simulation_executions_total
    type: counter
    description: "Total number of simulations executed"
    labels:
      - simulation_type
      - engine
      - status
    thresholds:
      warning: 1000
      critical: 5000

  - name: simulation_duration_seconds
    type: histogram
    description: "Simulation execution time in seconds"
    buckets: [1, 5, 10, 30, 60, 300, 600]
    targets:
      p50: 10
      p95: 60
      p99: 300

  # ... rest of KPIs
```

#### B. Prometheus Client Library

**Check**: `requirements.txt`

```txt
# Verify prometheus_client is included

prometheus-client>=0.17.0
```

#### C. Health Check Enhancements

**Current**: Basic `/health` endpoint exists
**Required**: Enhanced health checks for Service Discovery

```python
# Enhance /health endpoint in main.py

@app.get("/health")
async def health_check():
    """
    Comprehensive health check

    Checks:
    - Database (PostgreSQL + Redis)
    - EventBus connection
    - AI Foundation availability (optional)
    - Scenario Intelligence availability (optional)
    """
    health_status = {
        "service": "simulation-service",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    overall_healthy = True

    # Check database
    if db_manager:
        db_health = await db_manager.health_check()
        health_status["checks"]["database"] = {
            "postgres": db_health.get("postgres", False),
            "redis": db_health.get("redis", False)
        }
        if not db_health.get("postgres"):
            overall_healthy = False

    # Check EventBus
    if eventbus_client:
        eb_health = await eventbus_client.health_check()
        health_status["checks"]["eventbus"] = {
            "connected": eb_health.get("connected", False)
        }
        # EventBus optional for read operations

    # Check AI Foundation (optional)
    try:
        from integration.foundation_client import AIFoundationClient
        foundation = AIFoundationClient(settings.ai_foundation_url)
        foundation_health = await foundation.health_check()
        health_status["checks"]["ai_foundation"] = {
            "available": foundation_health.get("status") == "healthy",
            "optional": True
        }
    except:
        health_status["checks"]["ai_foundation"] = {
            "available": False,
            "optional": True
        }

    # Set overall status
    health_status["status"] = "healthy" if overall_healthy else "unhealthy"

    status_code = 200 if overall_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)
```

#### D. Dockerfile

**Check if exists**: `/platform-services/simulation/simulation-service/Dockerfile`

**If missing, create**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8095

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8095/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8095"]
```

#### E. docker-compose Integration

**Add to**: `/intelligent-core/docker-compose.yml` or create separate file

```yaml
# docker-compose.simulation.yml

version: '3.8'

services:
  simulation-service:
    build:
      context: ../platform-services/simulation/simulation-service
      dockerfile: Dockerfile

    container_name: simulation-service

    ports:
      - "8095:8095"

    environment:
      - PORT=8095
      - DATABASE_URL=postgresql://postgres:password@postgresql:5432/bcm_platform
      - REDIS_URL=redis://redis:6379/0
      - EVENTBUS_URL=http://eventbus:8055
      - EVENTBUS_REDIS_URL=redis://redis:6379/1
      - AI_ORCHESTRATOR_URL=http://ai-orchestration:8026
      - WORKFLOW_INTELLIGENCE_URL=http://workflow-intelligence:8037
      - AI_FOUNDATION_URL=http://ai-foundation:8025
      - SCENARIO_ORCHESTRATOR_URL=http://scenario-intelligence:8090
      - COMMUNITY_INTELLIGENCE_URL=http://community-intelligence:8030
      - PREDICTIVE_JOURNEY_URL=http://predictive:8031
      - DIGITAL_TWIN_URL=http://digital-twin:8096
      - JAAMSIM_ENABLED=true
      - SIMPY_ENABLED=true

    depends_on:
      - postgresql
      - redis
      - eventbus

    networks:
      - platform-network

    restart: unless-stopped

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8095/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

networks:
  platform-network:
    external: true
```

---

## 9. Step-by-Step Integration Checklist

### Phase 1: Database Integration (Priority: CRITICAL)

#### Task 1.1: Create Database Migration
- [ ] **File**: Create `/infrastructure/database/postgresql/migrations_source/045_simulation_service_schema.sql`
- [ ] **Content**:
  ```sql
  -- Create simulation schema
  CREATE SCHEMA IF NOT EXISTS simulation;

  -- Create tables from models.py
  -- (Copy table definitions)

  -- Enable RLS
  -- (Add RLS policies)

  -- Create indexes
  -- (Add performance indexes)
  ```
- [ ] **Test**: Run migration on local PostgreSQL
- [ ] **Verify**: Check schema exists, tables created, RLS enabled

#### Task 1.2: Add RLS Helper Functions
- [ ] **File**: Update `/infrastructure/database/postgresql/migrations_source/002_rls_functions.sql`
- [ ] **Add**:
  - `auth.is_org_member_by_tenant(p_tenant_id TEXT)`
  - `auth.is_org_admin_by_tenant(p_tenant_id TEXT)`
- [ ] **Test**: Verify functions work with tenant isolation

#### Task 1.3: Update Database URL in settings
- [ ] **File**: `config/settings.py`
- [ ] **Change**:
  ```python
  # FROM
  database_url: "postgresql://simulation_user:simulation_pass@localhost:5432/simulation_db"

  # TO (use platform database)
  database_url: "postgresql://postgres:<password>@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
  ```
- [ ] **Add**: Schema to SQLAlchemy models already correct (`schema='simulation'`)

#### Task 1.4: Test Database Connection
- [ ] Run simulation-service
- [ ] Verify tables created in `simulation` schema
- [ ] Test CRUD operations
- [ ] Verify RLS isolation with different tenant_ids

---

### Phase 2: EventBus Integration (Priority: HIGH)

#### Task 2.1: Implement Event Handlers
- [ ] **File**: Create `api/event_handlers.py`
- [ ] **Implement** 8 handlers:
  - `handle_scenario_request(event)`
  - `handle_twin_update(event)`
  - `handle_predictive_forecast(event)`
  - `handle_pdca_plan(event)`
  - `handle_bia_function(event)`
  - `handle_community_scenario(event)`
  - `handle_policy_change(event)`
  - `handle_workflow_test(event)`
- [ ] **Test**: Mock events, verify handlers execute

#### Task 2.2: Register Subscriptions in EventBus Client
- [ ] **File**: Update `integration/eventbus_client.py`
- [ ] **Add** subscription methods (8 methods)
- [ ] **Add** `start_subscriptions()` method
- [ ] **Test**: Verify subscriptions registered

#### Task 2.3: Start EventBus Consumer in main.py
- [ ] **File**: Update `main.py` lifespan
- [ ] **Add** after EventBus connection:
  ```python
  # Start EventBus subscriptions
  await eventbus_client.start_subscriptions()
  logger.info("✅ EventBus subscriptions active")
  ```
- [ ] **Test**: Publish test events, verify handlers called

#### Task 2.4: Verify Event Publishing
- [ ] **Test**: Create simulation → verify `simulation.created` published
- [ ] **Test**: Start simulation → verify `simulation.started` published
- [ ] **Test**: Complete simulation → verify `simulation.completed` published
- [ ] **Monitor**: Check EventBus logs for published events

---

### Phase 3: Service Discovery Integration (Priority: HIGH)

#### Task 3.1: Create SERVICE_INFO.yaml
- [ ] **File**: Create `/platform-services/simulation/simulation-service/SERVICE_INFO.yaml`
- [ ] **Content**: Copy from Section 5.2 above
- [ ] **Validate**: YAML syntax, completeness

#### Task 3.2: Implement Service Discovery Client
- [ ] **File**: Create `integration/service_discovery_client.py`
- [ ] **Implement**: ServiceDiscoveryClient class
- [ ] **Methods**: register(), deregister(), start_heartbeat()
- [ ] **Test**: Mock Consul API, verify registration

#### Task 3.3: Register in main.py Lifespan
- [ ] **File**: Update `main.py` lifespan
- [ ] **Add** registration on startup
- [ ] **Add** deregistration on shutdown
- [ ] **Test**: Verify service appears in Service Discovery

#### Task 3.4: Verify Health Checks
- [ ] **Test**: Service Discovery calls /health endpoint
- [ ] **Test**: Service marked healthy in registry
- [ ] **Monitor**: Check Service Discovery logs

---

### Phase 4: Prometheus Metrics Integration (Priority: HIGH)

#### Task 4.1: Add Prometheus Client
- [ ] **File**: Update `requirements.txt`
- [ ] **Add**: `prometheus-client>=0.17.0`
- [ ] **Install**: `pip install -r requirements.txt`

#### Task 4.2: Define Metrics in main.py
- [ ] **File**: Update `main.py`
- [ ] **Add** metric definitions (6 metrics from Section 7.1A)
- [ ] **Mount** `/metrics` endpoint
- [ ] **Test**: `curl http://localhost:8095/metrics`

#### Task 4.3: Instrument Code
- [ ] **File**: `core/orchestrator.py`
- [ ] **Add** metric increments in:
  - `execute_simulation()` → duration, count
  - `generate_scenario()` → generation time
  - `calculate_quality()` → quality score
- [ ] **Files**: Repeat for other modules
- [ ] **Test**: Run simulation, check metrics updated

#### Task 4.4: Verify MIO Manager Scraping
- [ ] **Run**: MIO Manager
- [ ] **Check**: Prometheus scrapes simulation-service
- [ ] **Verify**: Metrics appear in Prometheus UI
- [ ] **Monitor**: MIO Manager logs show simulation-service

---

### Phase 5: Catalog Integration (Priority: MEDIUM)

#### Task 5.1: Add to SERVICE_CATALOG_DETAILED.yaml
- [ ] **File**: `/catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml`
- [ ] **Add**: simulation-service entry (from Section 6.2A)
- [ ] **Location**: Under `platform_services:` section
- [ ] **Validate**: YAML syntax

#### Task 5.2: Add to SUBSYSTEMS_CATALOG.yaml
- [ ] **File**: `/catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml`
- [ ] **Add**: `- simulation-service` to platform_services list
- [ ] **Validate**: YAML syntax

#### Task 5.3: Add to SYSTEMS_CATALOG.yaml
- [ ] **File**: `/catalogs/systems/SYSTEMS_CATALOG.yaml`
- [ ] **Add**: `- simulation-service` to testing_validation system
- [ ] **Validate**: YAML syntax

#### Task 5.4: Sync Catalog with Service Discovery
- [ ] **Run**: Catalog sync script (if exists)
- [ ] **Verify**: Service appears in unified catalog view
- [ ] **Test**: Query `/v2/catalog/services` API

---

### Phase 6: AI Foundation Integration (Priority: MEDIUM)

#### Task 6.1: Verify AI Foundation Client
- [ ] **File**: `integration/foundation_client.py`
- [ ] **Test**: Connection to AI Foundation (8025)
- [ ] **Test**: RAG search functionality
- [ ] **Test**: LLM generation

#### Task 6.2: Configure RAG Collection
- [ ] **Add** simulation scenarios to Qdrant
- [ ] **Collection**: `simulation_scenarios`
- [ ] **Embeddings**: Store scenario embeddings
- [ ] **Test**: Search for similar scenarios

#### Task 6.3: Implement Scenario Generation
- [ ] **File**: `core/ai_scenario_generator.py`
- [ ] **Verify**: Uses AI Foundation for generation
- [ ] **Test**: Generate cyber scenario
- [ ] **Verify**: Quality score calculated

---

### Phase 7: Scenario Intelligence Integration (Priority: MEDIUM)

#### Task 7.1: Register as Execution Engine
- [ ] **File**: Update `main.py` lifespan
- [ ] **Add**: Registration with Scenario Intelligence
- [ ] **Test**: Verify engine registered

#### Task 7.2: Implement Execution Callback
- [ ] **File**: `api/event_handlers.py`
- [ ] **Handler**: `handle_scenario_request()`
- [ ] **Flow**:
  1. Receive scenario_id from event
  2. Load scenario from Scenario Intelligence
  3. Create simulation
  4. Execute
  5. Send results back
- [ ] **Test**: Request execution via EventBus

#### Task 7.3: Implement Learning Feedback
- [ ] **File**: `core/scenario_learning.py`
- [ ] **Add**: Send execution results to Scenario Intelligence
- [ ] **Add**: Update scenario success metrics
- [ ] **Test**: Verify feedback loop

---

### Phase 8: Workflow Intelligence Integration (Priority: LOW)

#### Task 8.1: Create Workflow Intelligence Client
- [ ] **File**: Create `integration/workflow_intelligence_client.py`
- [ ] **Implement**: PDCA cycle registration
- [ ] **Implement**: Check result reporting
- [ ] **Test**: Mock PDCA cycle

#### Task 8.2: Subscribe to PDCA Events
- [ ] **Event**: `workflow.pdca.plan`
- [ ] **Handler**: `execute_pdca_simulation()`
- [ ] **Test**: Verify simulation triggered by PDCA

#### Task 8.3: Report Simulation Results
- [ ] **After** simulation completes
- [ ] **Send** results to Workflow Intelligence
- [ ] **Test**: Verify PDCA Check recorded

---

### Phase 9: Docker & Deployment (Priority: MEDIUM)

#### Task 9.1: Create/Verify Dockerfile
- [ ] **File**: `/platform-services/simulation/simulation-service/Dockerfile`
- [ ] **Content**: From Section 8.1D
- [ ] **Build**: `docker build -t simulation-service:latest .`
- [ ] **Test**: `docker run -p 8095:8095 simulation-service:latest`

#### Task 9.2: Add to docker-compose
- [ ] **File**: Create `docker-compose.simulation.yml`
- [ ] **Content**: From Section 8.1E
- [ ] **Test**: `docker-compose -f docker-compose.simulation.yml up`
- [ ] **Verify**: All dependencies connected

#### Task 9.3: Environment Variables
- [ ] **File**: Create `.env.production`
- [ ] **Add**: All required environment variables
- [ ] **Test**: Load .env and start service

---

### Phase 10: Testing & Verification (Priority: CRITICAL)

#### Task 10.1: Integration Tests
- [ ] **File**: Create `tests/integration/test_platform_integration.py`
- [ ] **Tests**:
  - Database connection
  - EventBus pub/sub
  - Service Discovery registration
  - Prometheus metrics
  - Health checks
- [ ] **Run**: `pytest tests/integration/`

#### Task 10.2: End-to-End Test
- [ ] **Scenario**: Full simulation flow
  1. Register with Service Discovery
  2. Create simulation
  3. Publish `simulation.created` event
  4. Execute simulation
  5. Publish `simulation.completed` event
  6. Check metrics updated
  7. Verify results stored in database
- [ ] **Verify**: All integration points working

#### Task 10.3: Monitor MIO Manager
- [ ] **Check**: MIO Manager detects simulation-service
- [ ] **Verify**: Metrics scraped
- [ ] **Verify**: Health checks passing
- [ ] **Check**: No observations published (means all good)

---

## 10. Integration Verification

### 10.1 Verification Checklist

Once all phases complete, verify:

#### Database Integration
- [ ] Schema `simulation` exists in PostgreSQL
- [ ] Tables created: simulations, scenarios, executions, results
- [ ] RLS enabled and working (tenant isolation)
- [ ] Indexes created
- [ ] Can create/read/update/delete simulations
- [ ] Multi-tenant isolation verified

#### EventBus Integration
- [ ] Can publish events (8 event types)
- [ ] Can subscribe to events (8 subscriptions)
- [ ] Event handlers execute correctly
- [ ] Events visible in EventBus logs
- [ ] Correlation IDs working for tracing

#### Service Discovery Integration
- [ ] Service registered in Consul
- [ ] Health checks passing
- [ ] Metadata correct
- [ ] Appears in Service Discovery UI
- [ ] Heartbeats working
- [ ] Deregistration on shutdown working

#### Prometheus Metrics Integration
- [ ] `/metrics` endpoint returns data
- [ ] Prometheus scrapes metrics
- [ ] Metrics visible in Prometheus UI
- [ ] Grafana dashboard can query metrics
- [ ] MIO Manager sees metrics

#### MIO Manager Integration
- [ ] MIO Manager detects service (via Service Discovery event)
- [ ] Checks metrics endpoint
- [ ] No observations published (means healthy)
- [ ] Service appears in MIO Dashboard
- [ ] Alerts work if service goes down

#### Catalog Integration
- [ ] Service in SERVICE_CATALOG_DETAILED.yaml
- [ ] Service in SUBSYSTEMS_CATALOG.yaml
- [ ] Service in SYSTEMS_CATALOG.yaml
- [ ] Unified catalog API returns simulation-service
- [ ] Catalog sync working

#### AI Foundation Integration
- [ ] Can search RAG for scenarios
- [ ] Can generate scenarios with LLM
- [ ] Embeddings stored in Qdrant
- [ ] Quality scores calculated

#### Scenario Intelligence Integration
- [ ] Registered as execution engine
- [ ] Can receive execution requests
- [ ] Can send results back
- [ ] Learning feedback loop working

### 10.2 Integration Tests

**Create**: `tests/integration/test_full_integration.py`

```python
"""
Full Integration Test for Simulation Service

Tests all platform integration points.
"""

import pytest
import asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_integration_flow():
    """Test complete simulation flow with all integrations"""

    base_url = "http://localhost:8095"

    # 1. Health check
    async with AsyncClient() as client:
        response = await client.get(f"{base_url}/health")
        assert response.status_code == 200
        health = response.json()
        assert health["status"] == "healthy"
        assert health["checks"]["database"]["postgres"] is True
        assert health["checks"]["eventbus"]["connected"] is True

    # 2. Check Service Discovery registration
    sd_url = "http://localhost:8500"
    async with AsyncClient() as client:
        response = await client.get(f"{sd_url}/v1/catalog/service/simulation-service")
        assert response.status_code == 200
        services = response.json()
        assert len(services) > 0
        assert services[0]["ServiceName"] == "simulation-service"

    # 3. Create simulation
    async with AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/v1/simulations",
            json={
                "name": "Test Integration Simulation",
                "simulation_type": "scenario",
                "engine": "simpy",
                "parameters": {
                    "duration": 100,
                    "entities": 10
                },
                "tenant_id": "test-tenant"
            }
        )
        assert response.status_code == 201
        simulation = response.json()
        simulation_id = simulation["id"]

    # 4. Start simulation
    async with AsyncClient() as client:
        response = await client.post(
            f"{base_url}/api/v1/simulations/{simulation_id}/start"
        )
        assert response.status_code == 200

    # 5. Wait for completion
    await asyncio.sleep(5)

    # 6. Check results
    async with AsyncClient() as client:
        response = await client.get(
            f"{base_url}/api/v1/simulations/{simulation_id}"
        )
        assert response.status_code == 200
        simulation = response.json()
        assert simulation["status"] in ["completed", "running"]

    # 7. Check metrics
    async with AsyncClient() as client:
        response = await client.get(f"{base_url}/metrics")
        assert response.status_code == 200
        metrics = response.text
        assert "simulation_executions_total" in metrics
        assert "simulation_duration_seconds" in metrics

    # 8. Verify EventBus events
    # (Check EventBus logs or subscribe to events)

    # 9. Verify Prometheus scraping
    prometheus_url = "http://localhost:9090"
    async with AsyncClient() as client:
        response = await client.get(
            f"{prometheus_url}/api/v1/query",
            params={"query": "simulation_executions_total"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"

    print("✅ Full integration test passed!")


@pytest.mark.asyncio
async def test_eventbus_pub_sub():
    """Test EventBus publish and subscribe"""

    # This requires actual EventBus connection
    # Mock or use test EventBus instance

    from integration.eventbus_client import SimulationEventBusClient
    from config.settings import get_settings

    settings = get_settings()
    client = SimulationEventBusClient(settings)

    await client.connect()

    # Publish test event
    await client.publish_simulation_created(
        simulation_id=999,
        config={"test": "data"}
    )

    # Verify event published
    # (Check EventBus or subscribe to verify)

    await client.disconnect()

    print("✅ EventBus pub/sub test passed!")


@pytest.mark.asyncio
async def test_mio_manager_integration():
    """Test MIO Manager can monitor simulation-service"""

    mio_url = "http://localhost:8046"

    # Check MIO Manager can see simulation-service
    async with AsyncClient() as client:
        response = await client.get(f"{mio_url}/api/services")
        assert response.status_code == 200
        services = response.json()

        # Find simulation-service
        sim_service = None
        for svc in services:
            if svc["name"] == "simulation-service":
                sim_service = svc
                break

        assert sim_service is not None
        assert sim_service["status"] == "healthy"
        assert sim_service["metrics_available"] is True

    print("✅ MIO Manager integration test passed!")
```

---

## 11. Conflicts & Resolutions

### 11.1 Port Conflicts

**Issue**: Port 8095 may conflict with existing service

**Check**:
```bash
lsof -i :8095
netstat -an | grep 8095
```

**Resolution**:
- If conflict, change port in `config/settings.py`
- Update SERVICE_INFO.yaml
- Update all references

### 11.2 Database Schema Conflicts

**Issue**: Two simulation tables (`intelligence.simulations` vs `simulation.simulations`)

**Resolution** (CHOSEN):
- Use dedicated `simulation` schema
- Keep `intelligence.simulations` for digital-twin integration
- Document distinction:
  - `intelligence.simulations` = Digital Twin predictions
  - `simulation.simulations` = BCM exercise simulations

### 11.3 EventBus Subscription Conflicts

**Issue**: Multiple services may subscribe to same events

**Resolution**:
- EventBus supports multiple subscribers (fan-out)
- Each service gets copy of event
- No conflicts

### 11.4 Service Discovery Name Conflicts

**Issue**: Service name must be unique

**Check**: No other service named "simulation-service"

**Resolution**: Name is unique, no conflict

---

## 12. Dependencies Summary

### 12.1 Critical Dependencies (Must Have)

| Dependency | Port | Purpose | Status |
|-----------|------|---------|--------|
| PostgreSQL | 5432 | Database | ✅ Available |
| Redis | 6379 | Cache + EventBus | ✅ Available |
| EventBus | 8055 | Event coordination | ✅ Available |
| Service Discovery | 8500 | Service registry | ✅ Available |
| Prometheus | 9090 | Metrics collection | ✅ Available |

### 12.2 Integration Dependencies (Should Have)

| Dependency | Port | Purpose | Status |
|-----------|------|---------|--------|
| MIO Manager | 8046 | Monitoring | ✅ Available |
| AI Foundation | 8025 | RAG + LLM | ✅ Available |
| Scenario Intelligence | 8090 | Scenario execution | ✅ Available |
| Workflow Intelligence | 8037 | PDCA integration | ✅ Available |
| AI Orchestration | 8026 | Agent coordination | ✅ Available |

### 12.3 Optional Dependencies (Nice to Have)

| Dependency | Port | Purpose | Status |
|-----------|------|---------|--------|
| Community Intelligence | 8030 | Community scenarios | ✅ Available |
| Predictive | 8031 | Demand forecasting | ✅ Available |
| Digital Twin | 8096 | Twin state input | ⚠️ Planned |
| Collective | 8032 | Anonymous collaboration | ✅ Available |

---

## 13. Timeline Estimate

### Effort Estimation

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|---------------|----------|
| Phase 1: Database | 4 tasks | 4-6 hours | CRITICAL |
| Phase 2: EventBus | 4 tasks | 6-8 hours | HIGH |
| Phase 3: Service Discovery | 4 tasks | 3-4 hours | HIGH |
| Phase 4: Prometheus | 4 tasks | 2-3 hours | HIGH |
| Phase 5: Catalog | 4 tasks | 1-2 hours | MEDIUM |
| Phase 6: AI Foundation | 3 tasks | 2-3 hours | MEDIUM |
| Phase 7: Scenario Intelligence | 3 tasks | 3-4 hours | MEDIUM |
| Phase 8: Workflow Intelligence | 3 tasks | 2-3 hours | LOW |
| Phase 9: Docker | 3 tasks | 2-3 hours | MEDIUM |
| Phase 10: Testing | 3 tasks | 4-6 hours | CRITICAL |
| **TOTAL** | **35 tasks** | **29-42 hours** | - |

**Suggested Schedule**:
- **Day 1**: Phase 1 + Phase 2 (Critical integrations)
- **Day 2**: Phase 3 + Phase 4 (Service discovery + metrics)
- **Day 3**: Phase 5 + Phase 6 + Phase 7 (Catalog + AI integrations)
- **Day 4**: Phase 8 + Phase 9 (Workflow + Docker)
- **Day 5**: Phase 10 (Testing + verification)

**Total**: 5 working days (40 hours)

---

## 14. Success Criteria

Integration is considered **complete** when:

### Technical Criteria
- [ ] Service starts without errors
- [ ] All health checks passing
- [ ] Database schema created and RLS working
- [ ] EventBus publishing and subscribing working
- [ ] Service registered in Service Discovery
- [ ] Prometheus metrics exposed and scraped
- [ ] MIO Manager monitoring active
- [ ] All integration tests passing

### Functional Criteria
- [ ] Can create and execute simulations
- [ ] Can generate AI scenarios
- [ ] Can execute BCM exercises
- [ ] Results stored in database
- [ ] Events published to EventBus
- [ ] Metrics visible in Grafana

### Operational Criteria
- [ ] Service appears in all catalogs
- [ ] Docker container builds and runs
- [ ] docker-compose integration works
- [ ] Documentation updated
- [ ] SERVICE_INFO.yaml complete

### Integration Criteria
- [ ] MIO Manager sees service and metrics
- [ ] Scenario Intelligence can trigger executions
- [ ] AI Foundation provides scenario generation
- [ ] Workflow Intelligence PDCA integration works
- [ ] Community scenarios can be imported

---

## 15. Next Steps

1. **Start with Phase 1** (Database Integration)
   - Most critical
   - Blocks other work

2. **Then Phase 2** (EventBus Integration)
   - Core communication mechanism
   - Required for platform participation

3. **Then Phase 3** (Service Discovery)
   - Makes service visible to platform
   - Enables health monitoring

4. **Continue sequentially** through remaining phases

5. **Test continuously**
   - Don't wait until end
   - Test each phase immediately

---

## 16. Contact & Support

**Integration Questions**: platform-team@company.com
**Database Issues**: database-team@company.com
**EventBus Issues**: infrastructure-team@company.com
**Service Discovery**: devops-team@company.com
**Monitoring**: monitoring-team@company.com

---

## Appendix A: File Locations Reference

```
Key Integration Files:

Database:
- /infrastructure/database/postgresql/migrations_source/045_simulation_service_schema.sql (CREATE)
- /infrastructure/database/postgresql/migrations_source/002_rls_functions.sql (UPDATE)

Service Files:
- /platform-services/simulation/simulation-service/main.py (UPDATE)
- /platform-services/simulation/simulation-service/config/settings.py (VERIFY)
- /platform-services/simulation/simulation-service/SERVICE_INFO.yaml (CREATE)
- /platform-services/simulation/simulation-service/Dockerfile (CREATE)
- /platform-services/simulation/simulation-service/docker-compose.simulation.yml (CREATE)

Integration Files:
- /platform-services/simulation/simulation-service/integration/eventbus_client.py (UPDATE)
- /platform-services/simulation/simulation-service/integration/service_discovery_client.py (CREATE)
- /platform-services/simulation/simulation-service/integration/workflow_intelligence_client.py (CREATE)
- /platform-services/simulation/simulation-service/api/event_handlers.py (CREATE)

Catalog Files:
- /catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml (UPDATE)
- /catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml (UPDATE)
- /catalogs/systems/SYSTEMS_CATALOG.yaml (UPDATE)

Test Files:
- /platform-services/simulation/simulation-service/tests/integration/test_platform_integration.py (CREATE)
- /platform-services/simulation/simulation-service/tests/integration/test_full_integration.py (CREATE)
```

---

## Appendix B: EventBus Event Catalog

**Simulation-Service Events**:

### Publishing (8 events)
```
simulation.created
simulation.started
simulation.progress.updated
simulation.completed
simulation.failed
simulation.scenario.generated
simulation.case.created
simulation.knowledge.stored
```

### Subscribing (8 events)
```
scenario.execution.requested
digital_twin.state.changed
predictive.demand.forecasted
workflow.pdca.plan
bia.critical_function.identified
community.scenario.shared
governance.policy.changed
workflow.test.requested
```

---

## Appendix C: Database Schema

```sql
-- Schema: simulation

CREATE TABLE simulation.simulations (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    simulation_type VARCHAR(50) NOT NULL,
    engine VARCHAR(50),
    parameters JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'draft',
    created_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE simulation.scenarios (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    complexity INTEGER,
    scenario_type VARCHAR(50),
    content TEXT,
    timeline JSONB,
    injects JSONB,
    success_metrics JSONB,
    participant_roles JSONB,
    recommended_participants_count INTEGER,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    ai_generation_params JSONB,
    ai_confidence_score FLOAT,
    tags JSONB DEFAULT '[]',
    industry VARCHAR(100),
    organization_size VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE simulation.executions (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL REFERENCES simulation.simulations(id),
    execution_number INTEGER,
    run_id VARCHAR(100),
    parameters JSONB,
    status VARCHAR(50) NOT NULL,
    progress FLOAT DEFAULT 0.0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds FLOAT,
    results JSONB,
    metrics JSONB,
    error_message TEXT,
    error_details JSONB,
    executed_by VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE simulation.results (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL,
    execution_id INTEGER,
    result_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100),
    result_data JSONB NOT NULL,
    confidence_score FLOAT,
    quality_score FLOAT,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE simulation.simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation.results ENABLE ROW LEVEL SECURITY;

-- Indexes
CREATE INDEX idx_simulations_tenant ON simulation.simulations(tenant_id);
CREATE INDEX idx_simulations_status ON simulation.simulations(status);
CREATE INDEX idx_simulations_type ON simulation.simulations(simulation_type);
CREATE INDEX idx_scenarios_category ON simulation.scenarios(category);
CREATE INDEX idx_executions_simulation ON simulation.executions(simulation_id);
CREATE INDEX idx_results_simulation ON simulation.results(simulation_id);
CREATE INDEX idx_results_execution ON simulation.results(execution_id);
```

---

**END OF INTEGRATION PLAN**

**Document Version**: 1.0.0
**Last Updated**: 2025-10-13
**Status**: Ready for Implementation
