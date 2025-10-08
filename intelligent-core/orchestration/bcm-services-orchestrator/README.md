# BCM Services Orchestrator

**Level 2 Top Manager** - Coordinates BCM domain operations

## Overview

BCM Services Orchestrator is the **Top Manager** for Business Continuity Management domain. It receives strategic decisions from MEGA-BRAIN and coordinates execution across:

- **10 BCM Analyzers** (AI-powered stateless analysis)
- **Workflow Intelligence** (THE BRAIN - state machine with governance)
- **10 BCM Microservices** (operational CRUD)
- **Temporal Workflows** (durable multi-step execution)

## Architecture

```
MEGA-BRAIN (ai-orchestration/)
    ↓ delegates task
BCM Services Orchestrator ← YOU ARE HERE
    ↓ chooses strategy
    ├─→ Analyzer Coordinator (AI analysis)
    ├─→ Service Registry (operational work)
    ├─→ Workflow Intelligence (complex workflows)
    └─→ Temporal Client (durable workflows)
```

## Components

### 1. BCMServicesOrchestrator

Main orchestrator class. Receives tasks from MEGA-BRAIN and determines execution strategy.

**4 Execution Strategies:**

| Strategy | When to Use | Example |
|----------|------------|---------|
| `ANALYZER_ONLY` | Pure analysis, no state changes | Compliance gap analysis |
| `SERVICE_ONLY` | Simple CRUD operations | Fetch BIA results |
| `ANALYZER_THEN_SERVICE` | AI-enhanced operations | Generate recovery plan |
| `WORKFLOW` | Complex multi-step processes | Full BIA workflow |

**Usage:**
```python
from orchestration.bcm_services_orchestrator import BCMServicesOrchestrator

orchestrator = BCMServicesOrchestrator(
    analyzer_coordinator=analyzer_coord,
    service_registry=service_reg,
    temporal_client=temporal
)

result = await orchestrator.execute_task({
    'task_type': 'bia_analysis',
    'input': {'organization_id': 'org-123'},
    'tenant_id': 'tenant-456'
})
```

### 2. AnalyzerCoordinator

Routes analysis requests to appropriate BCM Analyzers.

**10 Analyzers:**
- `ComplianceAnalyzer` - ISO 22301 gap analysis
- `RiskAnalyzer` - FAIR-based risk quantification
- `ImpactAnalyzer` - BIA impact assessment
- `GovernanceAnalyzer` - Policy adherence
- `EmergencyAnalyzer` - Crisis response
- `PerformanceAnalyzer` - Metrics analysis
- `LearningAnalyzer` - Pattern extraction
- `LifecycleAnalyzer` - BCM maturity
- `PlanAnalyzer` - Recovery plan quality
- `ScenarioAnalyzer` - Exercise design

**Features:**
- Auto-routing based on analysis type
- Batch analysis (sequential pipeline)
- EventBus integration for audit trail
- Statistics tracking

**Usage:**
```python
from orchestration.bcm_services_orchestrator import AnalyzerCoordinator

coordinator = AnalyzerCoordinator(analyzers, event_bus)

# Auto-routing
result = await coordinator.route_analysis(
    analysis_type=AnalyzerType.AUTO,
    input_data={
        'type': 'compliance_gap',
        'standard': 'ISO_22301'
    },
    tenant_id='org-123'
)

# Batch analysis
result = await coordinator.batch_analysis(
    analyzer_sequence=[
        AnalyzerType.RISK,
        AnalyzerType.IMPACT,
        AnalyzerType.PLAN
    ],
    input_data={'scenario': 'ransomware_attack'},
    tenant_id='org-123'
)
```

### 3. BCMServiceRegistry

Maps ISO 22301 clauses to BCM microservices.

**10 Services:**

| Service | Port | ISO Clauses | Capabilities |
|---------|------|-------------|--------------|
| BIA Service | 8001 | 8.2, 6.1 | Process ID, Dependencies, Impact, RTO/RPO |
| Risk Service | 8002 | 8.1, 6.1 | Threats, Vulnerabilities, FAIR, Scoring |
| Plan Service | 8003 | 8.4, 6.2 | Recovery Strategy, Plan Gen, Resources |
| Exercise Service | 8004 | 8.5, 9.1 | Scenarios, Execution, Lessons |
| Incident Service | 8005 | 8.4, 10.2 | Detection, Severity, Response, PIR |
| Compliance Service | 8006 | 9.2, 10.1 | Gap Analysis, Audits, Controls |
| Learning Service | 8007 | 10.2, 7.4 | Patterns, Cross-Module, Knowledge Graph |
| Validation Service | 8008 | 9.1, 6.2 | KPIs, Objectives, Alerts |
| Governance Service | 8009 | 5.1, 4.1 | Policy, Stakeholders, Context |
| Document Service | 8010 | 7.5, 8.4 | Storage, Versions, Access |

**Usage:**
```python
from orchestration.bcm_services_orchestrator import BCMServiceRegistry

registry = BCMServiceRegistry()

# Find services for ISO clause
services = registry.find_services_for_clause(ISO22301Clause.CLAUSE_8)

# Find service by capability
service = registry.find_service_by_capability("impact_assessment")

# Get coverage report
coverage = registry.get_coverage_report()
print(f"ISO 22301 Coverage: {coverage['coverage_percentage']}%")
```

## Integration with MEGA-BRAIN

BCM Services Orchestrator receives delegations from `ai-orchestration/decision_center/delegation_manager.py`:

```python
# In DelegationManager
specialist = self._select_specialist(decision)  # Returns "bia-specialist"

# Creates delegation event
event = self._create_delegation_event(decision, specialist)

# Publishes to EventBus
await self.event_bus.publish(event)
```

BCM Services Orchestrator subscribes to `orchestrator.delegate.bia-specialist` events and executes tasks.

## Temporal Workflows Integration

For complex multi-step processes, orchestrator starts Temporal workflows:

```python
# In BCMServicesOrchestrator._execute_workflow()
workflow_id = f"bia-analysis-{tenant_id}-{timestamp}"

handle = await self.temporal_client.start_workflow(
    "BIAWorkflow",
    input_data,
    id=workflow_id,
    task_queue="bcm-workflows",
    retry_policy=RetryPolicy(
        initial_interval_seconds=1,
        maximum_interval_seconds=30,
        maximum_attempts=3
    )
)
```

**Workflows:**
- `BIAWorkflow` - Full BIA process (6 stages)
- `RiskAssessmentWorkflow` - Risk analysis (5 stages)
- `ExerciseWorkflow` - Exercise execution
- `IncidentWorkflow` - Incident response

## Statistics & Monitoring

```python
# Get orchestrator stats
stats = orchestrator.get_stats()
print(stats)
# {
#   'orchestrator': 'BCMServicesOrchestrator',
#   'level': '2 (Top Manager)',
#   'domain': 'BCM Services',
#   'execution_stats': {
#     'total_tasks': 150,
#     'by_strategy': {
#       'analyzer_only': 50,
#       'service_only': 30,
#       'analyzer_then_service': 40,
#       'workflow': 30
#     },
#     'workflows_started': 30,
#     'analyzer_calls': 90,
#     'service_calls': 70
#   },
#   'analyzer_coordinator': {...},
#   'service_registry': {...}
# }

# Health check
health = await orchestrator.health_check()
```

## Event Flow

```
1. MEGA-BRAIN publishes delegation event
   └─→ orchestrator.delegate.bia-specialist

2. BCM Orchestrator receives event
   └─→ Determines execution strategy

3a. ANALYZER_ONLY strategy:
   └─→ AnalyzerCoordinator.route_analysis()
       └─→ ComplianceAnalyzer.analyze()
           └─→ Publishes: bcm.analyzer.compliance.completed

3b. WORKFLOW strategy:
   └─→ TemporalClient.start_workflow("BIAWorkflow")
       └─→ Workflow executes activities
           └─→ Each activity calls analyzers/services
               └─→ Publishes: workflow.bia.stage.completed

4. BCM Orchestrator publishes completion event
   └─→ bcm.orchestrator.task.completed
```

## Files

```
bcm-services-orchestrator/
├── __init__.py                  # Module exports
├── bcm_orchestrator.py          # Main orchestrator (528 lines)
├── analyzer_coordinator.py      # Analyzer routing (400+ lines)
├── service_registry.py          # Service catalog (300+ lines)
└── README.md                    # This file
```

## Next Steps

- [ ] Connect to actual analyzer instances
- [ ] Implement HTTP clients for BCM services
- [ ] Create Temporal workflow definitions
- [ ] Add circuit breaker pattern for service calls
- [ ] Implement service health monitoring
- [ ] Add caching layer for repeated analyses
- [ ] Create integration tests

## Related Modules

- **MEGA-BRAIN**: `ai-orchestration/` (Level 1)
- **Analyzers**: `expertise-center/domains/bcm/analyzers/` (Level 4 Workers)
- **Workflow Intelligence**: `workflow_intelligence/` (THE BRAIN)
- **Coordination Center**: `coordination-center/` (Level 3)

---

**Created:** 2025-10-06
**Status:** ✅ Core implementation complete (Week 1, Day 1-2)
**Next:** Week 1, Day 3 - Create AI Office Orchestrator
