# BCM Domain Workflows

**Location**: `platform_services/bcm_domain/workflows/`
**Purpose**: Business Continuity Management workflow definitions and orchestrations

---

## Overview

This directory contains BCM-specific workflow definitions that integrate with:
- **Workflow Intelligence** (`intelligent_core/workflow_intelligence`) - Generic workflow engine
- **BCM Scenarios** (`/catalogs/scenarios`) - Business scenario catalog
- **Process Framework** (`/catalogs/scenarios/process-framework`) - Standard process definitions

---

## Architecture

```
BCM Workflows Architecture:
┌─────────────────────────────────────────────────────────┐
│  bcm_domain/workflows/                                  │
│  ├── bcm_workflows.yaml          # BCM workflow defs   │
│  ├── bia_workflow.yaml           # BIA process         │
│  ├── risk_workflow.yaml          # Risk assessment     │
│  └── plan_workflow.yaml          # Plan development    │
└─────────────────────────────────────────────────────────┘
                    ↓ uses
┌─────────────────────────────────────────────────────────┐
│  intelligent_core/workflow_intelligence/                │
│  - WorkflowEngine (generic orchestrator)                │
│  - PDCA automation                                      │
│  - Case-based learning                                  │
└─────────────────────────────────────────────────────────┘
                    ↓ references
┌─────────────────────────────────────────────────────────┐
│  /catalogs/scenarios/                                   │
│  ├── WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md        │
│  ├── process-framework/         # Standard processes   │
│  ├── simulation-templates/      # Simulation scenarios │
│  └── theory-of-change/          # ToC models          │
└─────────────────────────────────────────────────────────┘
```

---

## BCM Workflow Types

### 1. BIA Workflow (Business Impact Analysis)
**File**: `bia_workflow.yaml`
**Purpose**: Structured BIA process following ISO 22301:2019 clause 8.2.2

**Steps**:
1. Scope definition
2. Process identification
3. Impact assessment
4. RTO/RPO determination
5. Dependency mapping
6. Resource requirements
7. Report generation

**References**:
- `/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md` - BIA scenarios
- `/catalogs/scenarios/process-framework/` - Standard BIA templates

### 2. Risk Assessment Workflow
**File**: `risk_workflow.yaml`
**Purpose**: BCM risk assessment following ISO 22301:2019 clause 8.2.3

**Steps**:
1. Risk identification
2. Risk analysis
3. Risk evaluation
4. Risk treatment
5. Monitoring and review

### 3. Plan Development Workflow
**File**: `plan_workflow.yaml`
**Purpose**: BC plan creation and maintenance

**Steps**:
1. Strategy selection
2. Procedure development
3. Resource allocation
4. Testing planning
5. Approval process

### 4. Exercise Workflow
**File**: `exercise_workflow.yaml`
**Purpose**: BC exercise planning and execution

**Steps**:
1. Scenario selection
2. Exercise design
3. Participant preparation
4. Execution
5. After-action review

---

## Integration with Catalog Scenarios

### Scenario Catalog Reference
All BCM workflows reference scenarios from:
```
/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md
```

This catalog contains:
- ✅ BCM workflow scenarios (BIA, Risk, Plans)
- ✅ Case-based learning examples
- ✅ Benchmarking data
- ✅ PDCA automation patterns

### Process Framework
Standard process templates from:
```
/catalogs/scenarios/process-framework/
```

Contains:
- ISO 22301 compliant process definitions
- Industry-specific templates
- Best practice workflows

---

## Usage Examples

### Define BCM Workflow
```yaml
# bia_workflow.yaml
name: "Business Impact Analysis"
standard: "ISO 22301:2019"
clause: "8.2.2"
steps:
  - id: "scope_definition"
    name: "Define BIA Scope"
    type: "governance_checkpoint"
    required: true
    template_ref: "/catalogs/scenarios/process-framework/bia-scope.yaml"

  - id: "process_identification"
    name: "Identify Critical Processes"
    type: "ai_assisted"
    ai_colleague: "bia_specialist"
    scenario_ref: "/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md#bia"
```

### Execute Workflow via API
```python
from intelligent_core.workflow_intelligence import WorkflowEngine
from platform_services.bcm_domain.workflows import load_bia_workflow

# Load BCM-specific workflow
workflow_def = load_bia_workflow()

# Execute via generic engine
engine = WorkflowEngine()
workflow_instance = await engine.start_workflow(
    definition=workflow_def,
    tenant_id="org-123",
    context={"organization_name": "ACME Corp"}
)
```

---

## Directory Structure

```
workflows/
├── README.md                    # This file
├── bcm_workflows.yaml           # Main BCM workflow registry
├── bia_workflow.yaml            # BIA process definition
├── risk_workflow.yaml           # Risk assessment process
├── plan_workflow.yaml           # Plan development process
├── exercise_workflow.yaml       # Exercise planning process
├── __init__.py                  # Python module
└── loaders/
    ├── __init__.py
    ├── yaml_loader.py          # YAML workflow loader
    └── scenario_resolver.py    # Resolve catalog references
```

---

## Scenario Resolution

### How Workflows Find Scenarios
1. Workflow YAML references catalog path: `/catalogs/scenarios/...`
2. `scenario_resolver.py` resolves absolute paths
3. WorkflowEngine loads referenced templates
4. AI colleagues access scenario context via RAG

### Example Resolution
```python
# In workflow definition
scenario_ref: "/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md#bia"

# Resolved by scenario_resolver.py
resolved_path = "/Users/MD/AI-Platform-ISO/catalogs/scenarios/WORKFLOW_INTELLIGENCE_BUSINESS_SCENARIOS.md"
scenario_section = extract_section(resolved_path, "bia")
```

---

## Future Enhancements

### Planned
- [ ] Complete all 4 core BCM workflows (BIA, Risk, Plan, Exercise)
- [ ] Add simulation workflow (integrate with simulation_service)
- [ ] Create workflow templates for different organization sizes
- [ ] Implement workflow versioning
- [ ] Add multi-language workflow support

### Under Consideration
- [ ] Visual workflow editor integration
- [ ] Workflow marketplace (share workflows across organizations)
- [ ] Industry-specific workflow packs

---

## Related Documentation

- **Workflow Engine**: `/intelligent_core/workflow_intelligence/README.md`
- **Scenario Catalog**: `/catalogs/scenarios/README.md`
- **Process Framework**: `/catalogs/scenarios/process-framework/`
- **BCM Services**: `/platform_services/bcm_domain/services/`
- **AI Colleagues**: `/platform_services/bcm_domain/ai_colleagues/`

---

## Status

- ✅ Directory structure created
- ✅ Integration architecture defined
- ✅ Catalog references established
- ⏳ Workflow definitions (pending)
- ⏳ Scenario resolver implementation (pending)

**Last Updated**: 2025-10-18
**Version**: 1.0.0
