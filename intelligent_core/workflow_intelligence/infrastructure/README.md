# Workflow Intelligence Infrastructure

Module infrastructure providing process governance, policies, and templates.

## Components

- **process_framework/** - Process definition and execution framework
- **orchestration/** - AI-powered process orchestration
- **templates/** - Document template library
- **policies/** - Governance policies (security, compliance, performance)
- **monitoring/** - Infrastructure monitoring and metrics

## Architecture

This infrastructure is separate from:
- Global platform infrastructure (/infrastructure/) - Kubernetes, Docker, deployment
- Module infrastructure (this directory) - Process governance, policies, templates

## Usage Examples

### Process Framework

```python
from intelligent_core.workflow_intelligence.infrastructure.process_framework import (
    ProcessDefinition,
    ProcessStep,
    get_process_framework
)

# Get framework instance
framework = get_process_framework()

# Create and register process
process = ProcessDefinition(
    id="my_process",
    name="My Business Process",
    version="1.0",
    description="Custom process"
)

framework.register_process(process)
```

### Document Templates

```python
from intelligent_core.workflow_intelligence.infrastructure.templates import (
    get_document_library,
    create_bia_report_template
)

# Get template library
library = get_document_library()

# Generate document
document = library.generate_document(
    template_id="bia_report_v1",
    variables={
        "organization_name": "ACME Corp",
        "analysis_date": "2025-10-21",
        "prepared_by": "John Doe"
    }
)
```

### Process Orchestration

```python
from intelligent_core.workflow_intelligence.infrastructure.orchestration import (
    get_process_orchestrator
)

# Get orchestrator
orchestrator = get_process_orchestrator()

# Execute process automatically with AI
instance = await orchestrator.execute_process_automatically(
    process_id="bcm_bia_v1",
    initial_data={"organization": "ACME Corp"},
    user_email="john@acme.com"
)
```

### Policies

```python
from intelligent_core.workflow_intelligence.infrastructure.policies import (
    check_permission,
    ISO_22301_REQUIREMENTS,
    SLA_POLICIES
)

# Check user permission
has_access = check_permission(
    user_roles=["bcm_manager"],
    required_permission="process.bia.create"
)

# Get compliance requirements
bia_requirements = ISO_22301_REQUIREMENTS["8.2.2"]

# Get SLA policy
sla = SLA_POLICIES["bia_initiation"]
```

## Directory Structure

```
infrastructure/
├── process_framework/
│   ├── __init__.py
│   ├── models.py          # Data classes
│   ├── validation.py      # Validation rules
│   └── framework.py       # Core framework
├── orchestration/
│   ├── __init__.py
│   └── orchestrator.py    # AI orchestrator
├── templates/
│   ├── __init__.py
│   ├── models.py
│   ├── library.py
│   └── generators/
│       ├── __init__.py
│       ├── bia_template.py
│       ├── risk_template.py
│       └── bc_plan_template.py
├── policies/
│   ├── __init__.py
│   ├── security.py        # Access control
│   ├── compliance.py      # ISO 22301 requirements
│   └── performance.py     # SLA policies
└── monitoring/
    ├── __init__.py
    └── metrics_exporter.py
```

## Integration

This infrastructure integrates with:

1. **Workflows** (`/workflows/`) - Standard BCM process definitions
2. **Monitoring** (`/monitoring/`) - Operational metrics and dashboards
3. **AI Core** (`/intelligent_core/ai/`) - AI agent integration
4. **Governance** (`/intelligent_core/governance/`) - Policy enforcement

## See Also

- Main module README: `/intelligent_core/workflow_intelligence/README.md`
- Process definitions: `/intelligent_core/workflow_intelligence/workflows/`
- Monitoring setup: `/intelligent_core/workflow_intelligence/monitoring/`
