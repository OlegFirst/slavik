# Unified Workflow Engine - Quick Start Guide

**Version:** 2.0.0 (Phase 2 - PostgreSQL + AI)

---

## Installation

### Prerequisites

```bash
# Python 3.9+
python3 --version

# PostgreSQL database (Supabase)
export DATABASE_URL="postgresql://postgres.xxx:5432/postgres"
```

### Dependencies

```bash
pip install sqlalchemy asyncpg pydantic
```

---

## Basic Usage

### 1. Initialize Engine

```python
import asyncio
import os
from unified_workflow.core.unified_engine import UnifiedWorkflowEngine

async def main():
    # Create engine (async factory)
    engine = await UnifiedWorkflowEngine.create(
        tenant_id="your-company",
        module="bia",  # or "risk", "compliance", etc.
        database_url=os.getenv("DATABASE_URL"),
        workflow_intelligence_enabled=True
    )

    # Use engine...

    # Cleanup
    await engine.close()

asyncio.run(main())
```

### 2. Start a Workflow

```python
# From BPMN XML
instance_id = await engine.start_process_from_bpmn(
    bpmn_xml=bpmn_content,
    process_name="BIA Assessment",
    initial_variables={
        "org_context": {
            "industry": "healthcare",
            "size": "medium"
        },
        "requester": "John Smith"
    },
    started_by="john.smith@company.com"
)

print(f"Started workflow: {instance_id}")
```

### 3. Get Visual State (for UI)

```python
visual_state = await engine.get_visual_state(instance_id)

print(f"Type: {visual_state.type}")  # "bpmn"
print(f"Active tasks: {len(visual_state.active_tasks)}")
print(f"Progress: {visual_state.workflow_context['progress_percentage']:.1f}%")

# For each task
for task in visual_state.active_tasks:
    print(f"Task: {task['name']}")
    print(f"AI Tip: {task['ai_tip']}")

    # AI recommendations
    for rec in task.get('ai_recommendations', []):
        print(f"  - {rec['message']} (Priority: {rec['priority']})")
```

### 4. Assign and Complete Tasks

```python
# Assign task to user
await engine.assign_task(
    task_id=task_id,
    assignee="john.smith@company.com"
)

# Complete task with data
await engine.complete_task(
    task_id=task_id,
    variables={
        "processes_identified": 5,
        "critical_processes": [
            {"name": "Patient Care", "criticality": "high"}
        ]
    },
    completed_by="john.smith@company.com"
)
```

### 5. Get User's Tasks

```python
# Get all active tasks for a user
tasks = await engine.get_active_tasks_for_user(
    assignee="john.smith@company.com"
)

for task in tasks:
    print(f"Task: {task['name']}")
    print(f"Process: {task['process_name']}")
    print(f"Progress: {task['progress_percentage']:.1f}%")
```

---

## BPMN XML Example

### Simple Linear Workflow

```xml
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             id="bia_process">
  <process id="Process_BIA" name="BIA Assessment">
    <!-- Start -->
    <startEvent id="Start" name="Start BIA"/>
    <sequenceFlow id="Flow1" sourceRef="Start" targetRef="Task1"/>

    <!-- Task 1 -->
    <userTask id="Task1" name="Identify Processes"/>
    <sequenceFlow id="Flow2" sourceRef="Task1" targetRef="Task2"/>

    <!-- Task 2 -->
    <userTask id="Task2" name="Analyze Impact"/>
    <sequenceFlow id="Flow3" sourceRef="Task2" targetRef="End"/>

    <!-- End -->
    <endEvent id="End" name="BIA Complete"/>
  </process>
</definitions>
```

---

## Visual State Response

### What You Get

```python
visual_state = {
    "type": "bpmn",

    # BPMN XML for rendering
    "bpmn_xml": "<?xml version...",

    # Highlighted elements
    "current_activities": ["Task_AnalyzeImpact"],

    # Active tasks with AI
    "active_tasks": [
        {
            "id": "uuid",
            "activity_id": "Task_AnalyzeImpact",
            "name": "Analyze Business Impact",
            "assignee": "john.smith@company.com",
            "status": "active",
            "created_at": "2025-10-05T10:00:00Z",

            # AI recommendations
            "ai_tip": "Use AI to analyze scenarios",
            "ai_recommendations": [
                {
                    "action": "analyze_impact",
                    "message": "AI can analyze impact scenarios",
                    "priority": "medium",
                    "ai_powered": True
                }
            ],
            "estimated_hours": 2.5
        }
    ],

    # Workflow context
    "workflow_context": {
        "instance_id": "uuid",
        "process_id": "uuid",
        "status": "active",
        "started_at": "2025-10-05T10:00:00Z",
        "started_by": "john.smith@company.com",
        "progress_percentage": 33.3,
        "variables": {
            "org_context": {...},
            "processes_identified": 5
        }
    },

    # AI predictions
    "predictions": {
        "estimated_completion_date": "2025-10-12T10:00:00Z",
        "success_probability": 0.85,
        "risk_level": "low"
    },

    # UI hints
    "visualization_hints": {
        "highlight": ["Task_AnalyzeImpact"],
        "show_ai_overlay": True,
        "module": "bia"
    }
}
```

---

## API Methods Reference

### Workflow Management

```python
# Start workflow from BPMN
instance_id = await engine.start_process_from_bpmn(
    bpmn_xml: str,
    process_name: str = None,
    initial_variables: dict = None,
    started_by: str = None,
    created_by: str = None,
    description: str = None,
    version: str = "1.0"
) -> str

# Get visual state
visual_state = await engine.get_visual_state(
    workflow_id: str
) -> VisualState

# Terminate workflow
await engine.terminate_process(
    workflow_id: str,
    reason: str = None
)

# List processes
processes = await engine.list_processes(
    module: str = None
) -> List[dict]

# List instances
instances = await engine.list_instances(
    status: ProcessStatus = None
) -> List[dict]
```

### Task Management

```python
# Assign task
await engine.assign_task(
    task_id: str,
    assignee: str
)

# Complete task
await engine.complete_task(
    task_id: str,
    variables: dict = None,
    completed_by: str = None
)

# Get user's tasks
tasks = await engine.get_active_tasks_for_user(
    assignee: str,
    status: TaskStatus = None
) -> List[dict]
```

### Analytics

```python
# Get analytics
analytics = await engine.get_process_analytics(
    process_id: str = None
) -> dict
```

---

## Database Schema

### Tables Created

```sql
-- Process definitions
workflow.bpmn_processes (
    id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    module TEXT,
    name TEXT NOT NULL,
    bpmn_xml TEXT NOT NULL,
    version TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    created_by TEXT
)

-- Process instances
workflow.bpmn_instances (
    id UUID PRIMARY KEY,
    process_id UUID REFERENCES workflow.bpmn_processes,
    tenant_id TEXT NOT NULL,
    status TEXT,  -- active, completed, terminated
    variables JSONB,
    current_activities TEXT[],
    started_at TIMESTAMPTZ,
    started_by TEXT,
    completed_at TIMESTAMPTZ
)

-- Tasks
workflow.bpmn_tasks (
    id UUID PRIMARY KEY,
    process_instance_id UUID REFERENCES workflow.bpmn_instances,
    activity_id TEXT NOT NULL,
    name TEXT NOT NULL,
    task_type TEXT,
    assignee TEXT,
    status TEXT,  -- active, completed, cancelled
    ai_recommendations JSONB,
    ai_predicted_duration_hours NUMERIC,
    created_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    completed_by TEXT
)

-- Analytics
workflow.process_analytics (
    id UUID PRIMARY KEY,
    process_id UUID,
    tenant_id TEXT,
    event_type TEXT,
    event_data JSONB,
    timestamp TIMESTAMPTZ
)
```

---

## Events Published

### BPMN Events

```python
# When process deployed
"bpmn.process.deployed" → {
    process_id, process_name, tenant_id, module, version
}

# When instance started
"bpmn.instance.started" → {
    instance_id, process_id, tenant_id, variables, started_by
}

# When task created
"bpmn.task.created" → {
    task_id, instance_id, activity_id, name, tenant_id
}

# When task completed
"bpmn.task.completed" → {
    task_id, instance_id, activity_id, tenant_id, variables, completed_by
}

# When instance completed
"bpmn.instance.completed" → {
    instance_id, process_id, tenant_id, variables
}

# When instance terminated
"bpmn.instance.terminated" → {
    instance_id, tenant_id, reason
}
```

### Subscribe to Events

```python
@engine.bpmn_engine.on_event("bpmn.task.completed")
async def on_task_completed(event):
    print(f"Task completed: {event['data']['task_id']}")
```

---

## Error Handling

### Common Patterns

```python
try:
    instance_id = await engine.start_process_from_bpmn(bpmn_xml)
except ValueError as e:
    print(f"Invalid BPMN: {e}")
except Exception as e:
    print(f"Failed to start process: {e}")
```

### Validation Errors

```python
from unified_workflow.bpmn.parser import BPMNParser

# Validate BPMN before deploying
try:
    BPMNParser.validate_bpmn_xml(bpmn_xml)
    print("✓ BPMN is valid")
except ValueError as e:
    print(f"✗ Invalid BPMN: {e}")
```

---

## Testing

### Run Example

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/unified-workflow
export DATABASE_URL="postgresql://..."
python3 examples/production_usage.py
```

### Verify in Database

```sql
-- Check deployed processes
SELECT id, name, module, version, created_at
FROM workflow.bpmn_processes
ORDER BY created_at DESC;

-- Check active instances
SELECT i.id, i.status, p.name as process_name, i.started_at
FROM workflow.bpmn_instances i
JOIN workflow.bpmn_processes p ON i.process_id = p.id
WHERE i.status = 'active';

-- Check tasks with AI
SELECT id, name, assignee, ai_recommendations
FROM workflow.bpmn_tasks
WHERE status = 'active';
```

---

## Troubleshooting

### Database Connection

```python
# Test connection
from unified_workflow.persistence.database import DatabaseManager

db = DatabaseManager(database_url)
await db.connect()
print("✓ Connected to database")
await db.close()
```

### Check Migration

```sql
-- Check if migration 036 applied
SELECT version, applied_at
FROM public.schema_migrations
WHERE version = '036';
```

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("unified_workflow")
logger.setLevel(logging.DEBUG)
```

---

## Next Steps

1. **Read Full Documentation:** [PHASE_2_COMPLETE.md](./PHASE_2_COMPLETE.md)
2. **Run Example:** [production_usage.py](./examples/production_usage.py)
3. **Integrate with Service:** See integration examples
4. **Build Frontend:** Use visual_state API with bpmn-js

---

**Need Help?** Check:
- [PHASE_2_COMPLETE.md](./PHASE_2_COMPLETE.md) - Complete documentation
- [UNIFIED_WORKFLOW_PHASE_2_SUMMARY.md](../../UNIFIED_WORKFLOW_PHASE_2_SUMMARY.md) - Summary
- [examples/production_usage.py](./examples/production_usage.py) - Working example
