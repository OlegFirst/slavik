# Coordination Center Temporal Workflows

## Обзор

Coordination Center Workflows обеспечивают **durable, fault-tolerant execution** для координации между AI и BCM сервисами.

### Ключевые особенности:

- **Automatic Retry** - автоматические повторы при временных сбоях
- **Human Approval** - интеграция с approval workflow для критичных операций
- **Saga Pattern** - rollback при failures
- **Multi-Service Coordination** - orchestration нескольких сервисов
- **Conflict Resolution** - разрешение конфликтов между сервисами
- **Long-Running Support** - поддержка длительных операций (до 24 часов для approval)

---

## Workflows

### 1. CoordinationWorkflow

**Single Intent Execution** - выполнение одного AI intent через Coordination Center.

**Use Cases:**
- AI triggers BIA creation
- AI triggers risk assessment
- AI triggers compliance check
- Single-service operations

**Flow:**
```
AI Intent → Validate → [Approval?] → Execute → Track → [Rollback on failure]
```

**Example:**
```python
from temporalio.client import Client
from coordination_workflow import CoordinationWorkflow

client = await Client.connect("localhost:7233")

intent = {
    "action": "create",
    "entity": "bia_process",
    "params": {
        "organization_id": 123,
        "process_name": "IT Infrastructure",
        "scope": "IT"
    },
    "context": {
        "tenant_id": "tenant-001",
        "user_id": "ai_agent",
        "session_id": "session-456"
    },
    "require_approval": False
}

result = await client.execute_workflow(
    CoordinationWorkflow.run,
    intent,
    id="coordination-workflow-001",
    task_queue="coordination-queue"
)

print(f"Execution ID: {result['execution_id']}")
print(f"Status: {result['status']}")
```

**Features:**
- Automatic retry (3 attempts, exponential backoff)
- Human approval support (24h timeout)
- Automatic rollback on failure
- Progress tracking via Coordination Center

---

### 2. CrossServiceWorkflow

**Multi-Service Coordination** - orchestration нескольких сервисов с dependency management.

**Use Cases:**
- BIA + Risk Assessment + Compliance Check (parallel)
- Create incident → Assign team → Activate plan (sequential)
- Multi-domain operations
- Complex business processes

**Flow:**
```
Tasks → Distribute → Execute (parallel/sequential) → Resolve Conflicts → Aggregate Status → [Rollback on failure]
```

**Example:**
```python
tasks = [
    {
        "action": "create",
        "entity": "bia_process",
        "params": {"organization_id": 123, "scope": "IT"},
        "context": {"tenant_id": "tenant-001"}
    },
    {
        "action": "assess",
        "entity": "risk",
        "params": {"organization_id": 123, "domain": "IT"},
        "context": {"tenant_id": "tenant-001"}
    },
    {
        "action": "check",
        "entity": "compliance",
        "params": {"standard": "ISO_22301", "organization_id": 123},
        "context": {"tenant_id": "tenant-001"}
    }
]

result = await client.execute_workflow(
    CrossServiceWorkflow.run,
    tasks,
    id="cross-service-workflow-001",
    task_queue="coordination-queue"
)

print(f"Completed: {result['status_aggregation']['completed']}/{result['status_aggregation']['total']}")
```

**Features:**
- Parallel execution (independent tasks)
- Sequential execution (with dependencies - TODO)
- Conflict resolution (resource locks, data inconsistencies)
- Status aggregation
- Saga rollback on partial failure

---

### 3. ParallelTaskWorkflow

**Parallel Task Execution** - bulk operations с independent tasks.

**Use Cases:**
- Bulk BIA creation (multiple processes)
- Parallel analysis (risk + compliance + governance)
- Independent service calls
- Batch operations

**Flow:**
```
Tasks → Execute in Parallel → Aggregate Results
```

**Example:**
```python
tasks = [
    {
        "action": "create",
        "entity": "bia_process",
        "params": {"process_name": "Finance"},
        "context": {"tenant_id": "tenant-001"}
    },
    {
        "action": "create",
        "entity": "bia_process",
        "params": {"process_name": "HR"},
        "context": {"tenant_id": "tenant-001"}
    },
    {
        "action": "create",
        "entity": "bia_process",
        "params": {"process_name": "Operations"},
        "context": {"tenant_id": "tenant-001"}
    }
]

result = await client.execute_workflow(
    ParallelTaskWorkflow.run,
    tasks,
    fail_fast=False,  # Continue on error
    id="parallel-workflow-001",
    task_queue="coordination-queue"
)

print(f"Successful: {result['successful']}/{result['total_tasks']}")
```

**Features:**
- True parallel execution (all tasks start simultaneously)
- Fail-fast or continue-on-error mode
- Results aggregation
- Retry per task (3 attempts)

---

## Activities

### Core Activities

| Activity | Description | Timeout | Retries |
|----------|-------------|---------|---------|
| `intent_execution` | Execute AI intent via Coordination Center | 10min | 3 |
| `task_distribution` | Distribute tasks to services | 5min | 3 |
| `service_coordination` | Coordinate multi-service calls | 15min | 3 |
| `status_aggregation` | Aggregate status from executions | 5min | 3 |
| `conflict_resolution` | Resolve service conflicts | 5min | 3 |
| `approval_request` | Request human approval | 24h | 1 |
| `rollback_execution` | Rollback completed executions | 5min | 2 |

### Activity Details

#### intent_execution
- Calls Coordination Center `/execute` endpoint
- Polls for async execution completion
- Handles authorization errors
- Idempotent (safe to retry)

#### task_distribution
- Routes tasks based on Tool Registry
- Finds appropriate services for each task
- Returns distribution plan

#### service_coordination
- Executes multiple service calls
- Tracks success/failure per service
- Aggregates results

#### status_aggregation
- Polls execution status from multiple executions
- Aggregates statistics (completed, failed, running)
- Returns overall status

#### conflict_resolution
- Detects resource locks, data inconsistencies, permission errors
- Applies resolution strategies:
  - `wait_and_retry` - for resource locks
  - `use_latest` - for data conflicts
  - `escalate_to_human` - for permission issues

#### approval_request
- Long-running activity (up to 24h)
- Waits for human approval via Coordination Center
- Supports heartbeats for monitoring

#### rollback_execution
- Saga compensation pattern
- Calls Coordination Center `/rollback` endpoint
- Attempts rollback for all executions

---

## Integration with Coordination Center

### Architecture

```
AI Orchestration
       ↓
  [Temporal Workflow]
       ↓
  Coordination Center (/execute)
       ↓
  Command Interpreter → Tool Registry → Security Layer
       ↓
  Execution Tracker → HTTP Client
       ↓
  BCM Services (BIA, Risk, Compliance, etc.)
```

### Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/coordination/execute` | POST | Execute intent |
| `/coordination/executions/{id}` | GET | Get execution status |
| `/coordination/executions/{id}/approve` | POST | Approve execution |
| `/coordination/executions/{id}/rollback` | POST | Rollback execution |

### Configuration

Set Coordination Center URL in worker:

```python
from coordination_workflow import inject_dependencies

inject_dependencies(
    coordination_center_url="http://localhost:8004"
)
```

---

## Retry Policies

### Default Retry Policy

```python
RetryPolicy(
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=3,
    backoff_coefficient=2.0
)
```

### Approval Activity (No Retry)

```python
# Long-running, single attempt
start_to_close_timeout=timedelta(hours=24)
heartbeat_timeout=timedelta(minutes=5)
```

### Rollback Activity

```python
RetryPolicy(maximum_attempts=2)  # Limited retries for rollback
```

---

## Error Handling

### Error Types

| Error | Type | Handling |
|-------|------|----------|
| Authorization failed | `AUTHORIZATION_ERROR` | No retry, fail immediately |
| Service timeout | `TIMEOUT_ERROR` | Retry with backoff |
| Execution failed | `EXECUTION_FAILED` | Retry, then rollback |
| Approval denied | `APPROVAL_DENIED` | Fail workflow |
| Partial failure | `PARTIAL_FAILURE` | Rollback all executions |

### Compensation (Saga Pattern)

On workflow failure:
1. Collect all successful execution IDs
2. Call `rollback_execution` activity
3. Coordination Center attempts rollback for each
4. Log rollback results

---

## Monitoring

### Metrics

Workflows export metrics:
- `coordination_workflow_started`
- `coordination_workflow_completed`
- `coordination_workflow_failed`
- `coordination_intent_execution_duration`
- `coordination_approval_wait_time`
- `coordination_rollback_count`

### Events

Published to EventBus:
- `coordination.intent_received`
- `coordination.execution_started`
- `coordination.execution_completed`
- `coordination.execution_failed`
- `coordination.approval_required`
- `coordination.approval_decision`
- `coordination.rollback_initiated`
- `coordination.rollback_completed`

### Audit Trail

All coordination operations are logged via:
- Coordination Center Security Layer
- Temporal workflow history
- EventBus events

---

## Temporal Worker Setup

### 1. Install Dependencies

```bash
pip install temporalio httpx
```

### 2. Create Worker

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from coordination_workflow import (
    CoordinationWorkflow,
    CrossServiceWorkflow,
    ParallelTaskWorkflow,
    coordination_activities,
    inject_dependencies
)

async def main():
    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Inject dependencies
    inject_dependencies(
        coordination_center_url="http://localhost:8004"
    )

    # Create worker
    worker = Worker(
        client,
        task_queue="coordination-queue",
        workflows=[
            CoordinationWorkflow,
            CrossServiceWorkflow,
            ParallelTaskWorkflow
        ],
        activities=coordination_activities
    )

    # Run worker
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Run Worker

```bash
python temporal_worker.py
```

---

## Testing

### Unit Tests

```python
import pytest
from temporalio.testing import WorkflowEnvironment
from coordination_workflow import CoordinationWorkflow

@pytest.mark.asyncio
async def test_coordination_workflow():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[CoordinationWorkflow],
            activities=coordination_activities
        ):
            intent = {
                "action": "create",
                "entity": "bia_process",
                "params": {"process_name": "Test"},
                "context": {"tenant_id": "test-tenant"}
            }

            result = await env.client.execute_workflow(
                CoordinationWorkflow.run,
                intent,
                id="test-workflow-001",
                task_queue="test-queue"
            )

            assert result["status"] == "completed"
```

### Integration Tests

Test with real Coordination Center:

```bash
# 1. Start Coordination Center
cd intelligent-core/orchestration/coordination-center
python main.py

# 2. Start Temporal Worker
python temporal_worker.py

# 3. Execute workflow
python test_coordination_workflow.py
```

---

## Production Deployment

### 1. Temporal Cloud

Use Temporal Cloud for production:

```python
client = await Client.connect(
    "your-namespace.tmprl.cloud:7233",
    namespace="your-namespace",
    tls=True
)
```

### 2. Horizontal Scaling

Scale workers independently:

```bash
# Run 3 worker instances
docker-compose up --scale coordination-worker=3
```

### 3. Monitoring

- Temporal Web UI: http://localhost:8080
- Prometheus metrics
- Grafana dashboards

---

## Future Enhancements

### Planned Features:

1. **Dependency Management** - sequential execution based on task dependencies
2. **Priority Queue** - task prioritization
3. **Circuit Breaker** - stop execution on repeated service failures
4. **Caching** - cache tool registry lookups
5. **Batch Operations** - optimize bulk operations
6. **Advanced Conflict Resolution** - ML-based conflict detection
7. **Progressive Approval** - multi-stage approval workflow

---

## Troubleshooting

### Common Issues

#### 1. "Coordination Center timeout"

**Cause:** Coordination Center не отвечает

**Fix:**
```bash
# Check if Coordination Center is running
curl http://localhost:8004/coordination/health

# Restart if needed
cd intelligent-core/orchestration/coordination-center
python main.py
```

#### 2. "Activity timeout"

**Cause:** Activity выполняется дольше timeout

**Fix:** Увеличить timeout:
```python
await workflow.execute_activity(
    intent_execution,
    intent,
    start_to_close_timeout=timedelta(minutes=20)  # Increase
)
```

#### 3. "Rollback failed"

**Cause:** Сервис не поддерживает rollback

**Fix:** Реализовать compensation logic в Tool Registry

---

## References

- [Temporal Documentation](https://docs.temporal.io/)
- [Coordination Center README](../../../orchestration/coordination-center/README.md)
- [BIA Workflow](./bia_workflow.py)
- [Risk Workflow](./risk_workflow.py)
