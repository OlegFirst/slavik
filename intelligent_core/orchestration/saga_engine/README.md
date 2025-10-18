# Saga Pattern Engine

A production-ready implementation of the **Saga Pattern** for managing distributed transactions across microservices in the AI Platform ISO system.

## Overview

The Saga pattern is a design pattern for managing data consistency across microservices in distributed transaction scenarios. A saga is a sequence of local transactions where each transaction updates data within a single service and publishes an event or message triggering the next transaction step. If a step fails, the saga executes compensating transactions to undo the changes made by preceding steps.

### Why Use Sagas?

- **Avoid Distributed Transactions**: No need for 2PC (Two-Phase Commit) which doesn't scale
- **Maintain Data Consistency**: Eventual consistency across services
- **Handle Failures**: Automatic compensation on failures
- **Enable Recovery**: Persist state for crash recovery
- **Support Complex Workflows**: Orchestrate multi-step business processes

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Saga Orchestrator                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Execute Saga                                        │   │
│  │  • Load Definition                                   │   │
│  │  • Create Execution State                            │   │
│  │  • Execute Steps (Sequential/Parallel/Pipeline)      │   │
│  │  • Handle Failures                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                  │
│           ┌──────────────┼──────────────┐                  │
│           ▼              ▼              ▼                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Step 1   │  │   Step 2   │  │   Step 3   │           │
│  │  (Execute) │  │  (Execute) │  │  (Execute) │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│        │              │              │                      │
│        ▼              ▼              ▼                      │
│  ┌────────────────────────────────────────┐                │
│  │        State Store (Persistence)       │                │
│  │  • Redis / PostgreSQL / In-Memory      │                │
│  └────────────────────────────────────────┘                │
│                          │                                  │
│             (On Failure) ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Compensation Manager                       │   │
│  │  • Backward Recovery (rollback completed steps)      │   │
│  │  • Forward Recovery (try to complete)                │   │
│  │  • Partial Compensation (rollback critical only)     │   │
│  └─────────────────────────────────────────────────────┘   │
│           │              │              │                   │
│           ▼              ▼              ▼                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │Compensate 3│  │Compensate 2│  │Compensate 1│           │
│  │  (Reverse) │  │  (Reverse) │  │  (Reverse) │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Key Concepts

### Saga Definition

A **Saga Definition** describes:
- **Steps**: Sequence of operations to perform
- **Compensation**: How to undo each step
- **Execution Policy**: Sequential, parallel, or pipeline
- **Timeouts & Retries**: Resilience configuration

### Saga Execution

A **Saga Execution** tracks:
- **Current State**: Which steps completed, which failed
- **Context**: Shared data across steps
- **Results**: Output from each step
- **Status**: Pending, executing, completed, failed, compensating, compensated

### Compensation

**Compensation** is the rollback mechanism:
- **Backward Recovery**: Undo completed steps in reverse order (default)
- **Forward Recovery**: Try to complete the saga despite errors
- **Partial Compensation**: Only undo critical steps

## Quick Start

### 1. Basic Setup

```python
from intelligent_core.orchestration.saga_engine import (
    SagaOrchestrator,
    SagaDefinition,
    SagaStepDefinition,
    InMemorySagaStateStore,
    SagaExecutionPolicy,
    CompensationStrategy
)

# Create state store
state_store = InMemorySagaStateStore()

# Service invoker function
async def service_invoker(action: str, params: dict):
    """
    Invoke a service method.

    Format: "service_name.method_name"
    Example: "bia_service.create_assessment"
    """
    service_name, method_name = action.split('.')
    service = get_service(service_name)
    method = getattr(service, method_name)
    return await method(**params)

# Event publisher function (optional)
async def event_publisher(event_type: str, data: dict):
    """Publish events to EventBus"""
    await eventbus.publish(event_type, data)

# Create orchestrator
orchestrator = SagaOrchestrator(
    state_store=state_store,
    service_invoker=service_invoker,
    event_publisher=event_publisher
)
```

### 2. Define a Saga

```python
# Define BCM Program Creation Saga
bcm_program_saga = SagaDefinition(
    name="create_bcm_program",
    description="Create complete BCM program with BIA, plans, and compliance",
    execution_policy=SagaExecutionPolicy.SEQUENTIAL,
    compensation_strategy=CompensationStrategy.BACKWARD_RECOVERY,
    total_timeout_seconds=600  # 10 minutes
)

# Step 1: Create BIA
bcm_program_saga.add_step(
    SagaStepDefinition(
        name="create_bia",
        description="Create Business Impact Analysis",
        forward_action="bia_service.create_assessment",
        forward_params={
            "assessment_type": "comprehensive",
            "scope": "organization"
        },
        compensation_action="bia_service.delete_assessment",
        timeout_seconds=120,
        max_retries=3,
        critical=True  # Must be compensated on failure
    )
)

# Step 2: Create BCM Plans
bcm_program_saga.add_step(
    SagaStepDefinition(
        name="create_plans",
        description="Create BCM and DR plans",
        forward_action="plans_service.create_plan_suite",
        forward_params={
            "plan_types": ["bcm", "dr", "incident_response"]
        },
        compensation_action="plans_service.delete_plan_suite",
        timeout_seconds=60,
        max_retries=2,
        critical=True
    )
)

# Step 3: Initialize Compliance
bcm_program_saga.add_step(
    SagaStepDefinition(
        name="init_compliance",
        description="Initialize ISO 22301 compliance tracking",
        forward_action="compliance_service.initialize_program",
        forward_params={
            "standard": "ISO_22301",
            "scope": "bcm_program"
        },
        compensation_action="compliance_service.remove_program",
        timeout_seconds=30,
        max_retries=2,
        critical=True
    )
)

# Step 4: Setup Monitoring (non-critical)
bcm_program_saga.add_step(
    SagaStepDefinition(
        name="setup_monitoring",
        description="Setup program monitoring and alerts",
        forward_action="monitoring_service.setup_program_monitoring",
        forward_params={
            "metrics": ["plan_coverage", "compliance_score"]
        },
        compensation_action="monitoring_service.remove_monitoring",
        timeout_seconds=20,
        critical=False  # Won't be compensated if saga fails
    )
)

# Register saga
orchestrator.register_saga(bcm_program_saga)
```

### 3. Execute the Saga

```python
# Execute saga
saga_execution = await orchestrator.execute_saga(
    saga_name="create_bcm_program",
    initial_context={
        "organization_id": "org-123",
        "created_by": "user-456",
        "program_name": "Enterprise BCM Program"
    },
    tenant_id="tenant-789",
    correlation_id="correlation-abc"
)

# Check result
if saga_execution.is_completed():
    print(f"✅ BCM Program created successfully!")
    print(f"Results: {saga_execution.result}")
else:
    print(f"❌ BCM Program creation failed: {saga_execution.error}")
    print(f"Status: {saga_execution.status.value}")
```

### 4. Monitor Saga Status

```python
# Get saga status
status = await orchestrator.get_saga_status(saga_execution.saga_id)

print(f"Saga: {status['saga_id']}")
print(f"Status: {status['status']}")
print(f"Steps:")
for step in status['steps']:
    print(f"  - {step['name']}: {step['status']} (attempts: {step['attempts']})")
```

## Advanced Examples

### Example 1: Parallel Execution with Dependencies

```python
# Create saga with parallel execution
parallel_saga = SagaDefinition(
    name="parallel_data_import",
    description="Import data from multiple sources in parallel",
    execution_policy=SagaExecutionPolicy.PARALLEL
)

# These can run in parallel (no dependencies)
parallel_saga.add_step(
    SagaStepDefinition(
        name="import_users",
        forward_action="import_service.import_users",
        compensation_action="import_service.rollback_users"
    )
)

parallel_saga.add_step(
    SagaStepDefinition(
        name="import_assets",
        forward_action="import_service.import_assets",
        compensation_action="import_service.rollback_assets"
    )
)

# This depends on users being imported
parallel_saga.add_step(
    SagaStepDefinition(
        name="assign_permissions",
        forward_action="import_service.assign_permissions",
        compensation_action="import_service.revoke_permissions",
        depends_on=["import_users"]  # Wait for users
    )
)

orchestrator.register_saga(parallel_saga)
```

### Example 2: Pipeline Mode with Data Flow

```python
# Create pipeline saga (output flows to next step)
pipeline_saga = SagaDefinition(
    name="bia_to_plan_pipeline",
    description="Pipeline from BIA analysis to plan generation",
    execution_policy=SagaExecutionPolicy.PIPELINE
)

# Step 1: Analyze BIA
pipeline_saga.add_step(
    SagaStepDefinition(
        name="analyze_bia",
        forward_action="bia_service.analyze_impact",
        # Output: {"critical_processes": [...], "rto_requirements": {...}}
    )
)

# Step 2: Generate recovery strategies
# Uses output from Step 1 automatically
pipeline_saga.add_step(
    SagaStepDefinition(
        name="generate_strategies",
        forward_action="strategy_service.generate_recovery_strategies",
        # Receives: critical_processes, rto_requirements from previous step
        # Output: {"strategies": [...]}
    )
)

# Step 3: Create plans
# Uses output from Steps 1 & 2
pipeline_saga.add_step(
    SagaStepDefinition(
        name="create_plans",
        forward_action="plans_service.create_from_strategies",
        # Receives: critical_processes, rto_requirements, strategies
    )
)
```

### Example 3: Forward Recovery Strategy

```python
# Use forward recovery for idempotent operations
forward_saga = SagaDefinition(
    name="send_notifications",
    description="Send notifications to stakeholders",
    execution_policy=SagaExecutionPolicy.SEQUENTIAL,
    compensation_strategy=CompensationStrategy.FORWARD_RECOVERY
)

forward_saga.add_step(
    SagaStepDefinition(
        name="notify_team",
        forward_action="notification_service.notify_team",
        # No compensation - forward recovery will retry
    )
)

forward_saga.add_step(
    SagaStepDefinition(
        name="notify_management",
        forward_action="notification_service.notify_management"
    )
)

forward_saga.add_step(
    SagaStepDefinition(
        name="notify_external",
        forward_action="notification_service.notify_external"
    )
)
```

### Example 4: Nested Sagas

```python
# Parent saga that orchestrates child sagas
async def execute_drill_program():
    """Execute complete drill program with nested sagas"""

    # Parent saga
    drill_program = SagaDefinition(
        name="execute_drill_program",
        description="Execute quarterly BCM drill program"
    )

    drill_program.add_step(
        SagaStepDefinition(
            name="schedule_drills",
            forward_action="drill_service.schedule_quarterly_drills"
        )
    )

    drill_program.add_step(
        SagaStepDefinition(
            name="execute_drills",
            forward_action="drill_service.execute_all_drills",
            # This internally executes child sagas for each drill
        )
    )

    drill_program.add_step(
        SagaStepDefinition(
            name="generate_reports",
            forward_action="reporting_service.generate_drill_reports"
        )
    )

    orchestrator.register_saga(drill_program)

    # Execute
    result = await orchestrator.execute_saga(
        "execute_drill_program",
        initial_context={"quarter": "Q1", "year": 2025}
    )

    return result
```

### Example 5: Idempotency with Keys

```python
# Use idempotency keys for safe retries
saga = SagaDefinition(name="payment_processing")

saga.add_step(
    SagaStepDefinition(
        name="charge_customer",
        forward_action="payment_service.charge",
        forward_params={
            "amount": 100.00,
            "payment_id": "pay-123"  # This will be used as idempotency key
        },
        compensation_action="payment_service.refund",
        idempotency_key_field="payment_id",  # Use this field as idempotency key
        max_retries=5  # Safe to retry with idempotency
    )
)
```

### Example 6: Lifecycle Hooks

```python
# Add hooks for lifecycle events
saga = SagaDefinition(
    name="bcm_program_with_hooks",
    on_start="notification_service.notify_program_start",
    on_complete="notification_service.notify_program_complete",
    on_failure="notification_service.notify_program_failed",
    on_compensated="notification_service.notify_program_rollback"
)

# Hooks receive saga context:
# {
#     "saga_id": "...",
#     "status": "completed",
#     "context": {...}
# }
```

## Event-Driven Integration

The Saga Engine publishes events to the EventBus for monitoring and integration:

### Published Events

```python
# Saga lifecycle events
"saga.started"            # Saga execution started
"saga.completed"          # Saga completed successfully
"saga.failed"             # Saga failed
"saga.compensated"        # Saga compensation completed
"saga.compensation_failed" # Saga compensation failed
"saga.error"              # Saga encountered error

# Step lifecycle events
"saga.step.started"       # Step execution started
"saga.step.completed"     # Step completed successfully
"saga.step.failed"        # Step failed
```

### Event Integration Example

```python
from intelligent_core.orchestration.coordination_center.core.event_handlers import (
    event_handlers
)

# Subscribe to saga events
async def handle_saga_completed(event_data: dict, tenant_id: str):
    """Handle saga completion"""
    saga_id = event_data.get("saga_id")
    saga_name = event_data.get("saga_name")
    result = event_data.get("result")

    logger.info(f"Saga {saga_name} completed: {saga_id}")

    # Trigger downstream actions
    await trigger_post_processing(saga_id, result)

# Register handler
event_handlers.register_handler("saga.completed", handle_saga_completed)
```

## State Persistence

### In-Memory Store (Development)

```python
from saga_engine import InMemorySagaStateStore

state_store = InMemorySagaStateStore()
# Data lost on restart - use for testing only
```

### Redis Store (Production)

```python
from saga_engine import RedisSagaStateStore
import aioredis

redis = await aioredis.create_redis_pool('redis://localhost')
state_store = RedisSagaStateStore(redis, key_prefix="bcm:saga:")

# Features:
# - Fast access
# - Automatic TTL for completed sagas
# - Index by status and tenant
```

### PostgreSQL Store (Production)

```python
from saga_engine import PostgresSagaStateStore
import asyncpg

db_pool = await asyncpg.create_pool(
    'postgresql://user:pass@localhost/bcm_platform'
)
state_store = PostgresSagaStateStore(db_pool)

# Features:
# - Full ACID guarantees
# - Complex querying
# - Audit trail
```

### Database Schema (PostgreSQL)

```sql
-- Sagas table
CREATE TABLE sagas (
    saga_id VARCHAR(100) PRIMARY KEY,
    definition_name VARCHAR(200) NOT NULL,
    definition_version VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_context JSONB,
    result JSONB,
    error TEXT,
    tenant_id VARCHAR(100),
    correlation_id VARCHAR(100),
    parent_saga_id VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Saga steps table
CREATE TABLE saga_steps (
    step_id VARCHAR(100) NOT NULL,
    step_name VARCHAR(200) NOT NULL,
    saga_id VARCHAR(100) NOT NULL REFERENCES sagas(saga_id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    result JSONB,
    error TEXT,
    error_details JSONB,
    compensation_started_at TIMESTAMP,
    compensation_completed_at TIMESTAMP,
    compensation_result JSONB,
    compensation_error TEXT,
    idempotency_key VARCHAR(200),
    output_context JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (saga_id, step_name)
);

-- Indices
CREATE INDEX idx_sagas_status ON sagas(status);
CREATE INDEX idx_sagas_tenant ON sagas(tenant_id);
CREATE INDEX idx_sagas_correlation ON sagas(correlation_id);
CREATE INDEX idx_sagas_started_at ON sagas(started_at DESC);
CREATE INDEX idx_saga_steps_status ON saga_steps(status);
```

## Recovery and Resilience

### Automatic Recovery

```python
# After system restart, recover in-progress sagas
async def recover_all_sagas():
    """Recover all executing or compensating sagas"""

    # Get sagas in executing state
    executing_sagas = await state_store.list_sagas(
        status=SagaStatus.EXECUTING
    )

    for saga in executing_sagas:
        try:
            recovered = await orchestrator.recover_saga(saga.saga_id)
            logger.info(f"Recovered saga {saga.saga_id}: {recovered.status}")
        except Exception as e:
            logger.error(f"Failed to recover saga {saga.saga_id}: {e}")

    # Get sagas in compensating state
    compensating_sagas = await state_store.list_sagas(
        status=SagaStatus.COMPENSATING
    )

    for saga in compensating_sagas:
        try:
            recovered = await orchestrator.recover_saga(saga.saga_id)
            logger.info(f"Recovered compensation for {saga.saga_id}: {recovered.status}")
        except Exception as e:
            logger.error(f"Failed to recover compensation {saga.saga_id}: {e}")
```

### Manual Retry

```python
# Manually retry a failed saga
async def retry_failed_saga(saga_id: str):
    """Retry a failed saga from the last successful step"""

    saga = await state_store.get_saga(saga_id)

    if saga.status != SagaStatus.FAILED:
        raise ValueError(f"Saga {saga_id} is not in failed state")

    # Reset failed step
    failed_step = saga.get_failed_step()
    if failed_step:
        failed_step.status = SagaStepStatus.PENDING
        failed_step.attempts = 0
        failed_step.error = None
        await state_store.save_step(saga.saga_id, failed_step)

    # Reset saga status
    saga.status = SagaStatus.EXECUTING
    await state_store.save_saga(saga)

    # Recover (will continue from failed step)
    return await orchestrator.recover_saga(saga_id)
```

## Monitoring and Observability

### Compensation Report

```python
# Get detailed compensation report
from saga_engine import CompensationManager

comp_manager = CompensationManager(state_store, service_invoker)
report = await comp_manager.get_compensation_report(saga)

print(f"Compensation Status: {report['compensation_status']}")
print(f"Compensated: {report['compensated_count']}/{report['total_steps']}")
print(f"Failed: {report['failed_count']}")

for step in report['compensated_steps']:
    print(f"  ✅ {step['step_name']} compensated at {step['compensated_at']}")

for step in report['failed_compensations']:
    print(f"  ❌ {step['step_name']} failed: {step['error']}")
```

### Metrics

```python
# Track saga metrics
async def get_saga_metrics(tenant_id: str = None):
    """Get saga execution metrics"""

    metrics = {
        "total": 0,
        "completed": 0,
        "failed": 0,
        "compensated": 0,
        "in_progress": 0
    }

    for status in SagaStatus:
        sagas = await state_store.list_sagas(
            status=status,
            tenant_id=tenant_id
        )
        count = len(sagas)
        metrics["total"] += count

        if status == SagaStatus.COMPLETED:
            metrics["completed"] = count
        elif status == SagaStatus.FAILED:
            metrics["failed"] = count
        elif status == SagaStatus.COMPENSATED:
            metrics["compensated"] = count
        elif status == SagaStatus.EXECUTING:
            metrics["in_progress"] = count

    return metrics
```

## Best Practices

### 1. Design Idempotent Operations

```python
# ❌ BAD: Not idempotent
async def create_assessment(org_id: str):
    assessment = Assessment(organization_id=org_id)
    await db.insert(assessment)
    return assessment.id

# ✅ GOOD: Idempotent with key
async def create_assessment(org_id: str, idempotency_key: str):
    # Check if already exists
    existing = await db.get_by_key(idempotency_key)
    if existing:
        return existing.id

    assessment = Assessment(
        organization_id=org_id,
        idempotency_key=idempotency_key
    )
    await db.insert(assessment)
    return assessment.id
```

### 2. Implement Proper Compensation

```python
# ❌ BAD: Incomplete compensation
async def delete_assessment(assessment_id: str):
    await db.delete(assessment_id)
    # Forgot to clean up related data!

# ✅ GOOD: Complete compensation
async def delete_assessment(assessment_id: str):
    # Clean up all related data
    await db.delete_related_processes(assessment_id)
    await db.delete_related_risks(assessment_id)
    await db.delete_related_controls(assessment_id)
    await db.delete(assessment_id)

    # Publish event
    await eventbus.publish("assessment.deleted", {"id": assessment_id})
```

### 3. Handle Partial Failures

```python
# Use critical flag to mark steps that MUST be compensated
saga.add_step(
    SagaStepDefinition(
        name="charge_payment",
        forward_action="payment_service.charge",
        compensation_action="payment_service.refund",
        critical=True  # Always compensate
    )
)

saga.add_step(
    SagaStepDefinition(
        name="send_email",
        forward_action="email_service.send_confirmation",
        critical=False  # OK to skip compensation
    )
)
```

### 4. Use Timeouts and Retries

```python
saga.add_step(
    SagaStepDefinition(
        name="external_api_call",
        forward_action="external_service.call_api",
        timeout_seconds=10,  # Fail fast for external calls
        max_retries=3,
        retry_delay_seconds=2  # Exponential backoff handled automatically
    )
)
```

### 5. Monitor and Alert

```python
# Subscribe to saga failure events
async def handle_saga_failed(event_data: dict):
    saga_id = event_data["saga_id"]
    error = event_data["error"]

    # Alert operations team
    await alerting_service.send_alert(
        level="error",
        message=f"Saga {saga_id} failed: {error}",
        tags=["saga", "failure"]
    )

    # Create incident if critical
    if is_critical_saga(saga_id):
        await incident_service.create_incident({
            "title": f"Critical Saga Failure: {saga_id}",
            "description": error,
            "severity": "high"
        })
```

## Integration with AI Platform ISO

### With EventBus

```python
# In your service initialization
from intelligent_core.shared.eventbus import eventbus

orchestrator = SagaOrchestrator(
    state_store=state_store,
    service_invoker=service_invoker,
    event_publisher=lambda event_type, data: eventbus.publish(event_type, data)
)
```

### With Coordination Center

```python
# Coordination Center can execute sagas
from intelligent_core.orchestration.coordination_center import CoordinationCenter

coordination_center = CoordinationCenter()
coordination_center.register_saga_orchestrator(orchestrator)

# Execute saga through coordination
await coordination_center.execute_coordination_saga(
    saga_name="create_bcm_program",
    context={"organization_id": "org-123"}
)
```

### With Workflow Intelligence

```python
# Workflow steps can trigger sagas
workflow_step = WorkflowStep(
    name="create_program",
    action_type="saga",
    action_params={
        "saga_name": "create_bcm_program",
        "context": "${workflow.context}"
    }
)
```

## Testing

### Unit Testing

```python
import pytest
from saga_engine import (
    SagaOrchestrator, SagaDefinition, SagaStepDefinition,
    InMemorySagaStateStore
)

@pytest.mark.asyncio
async def test_saga_execution():
    # Setup
    state_store = InMemorySagaStateStore()
    results = []

    async def mock_invoker(action: str, params: dict):
        results.append(action)
        return {"status": "success"}

    orchestrator = SagaOrchestrator(
        state_store=state_store,
        service_invoker=mock_invoker
    )

    # Define saga
    saga = SagaDefinition(name="test_saga")
    saga.add_step(SagaStepDefinition(
        name="step1",
        forward_action="service.action1"
    ))
    saga.add_step(SagaStepDefinition(
        name="step2",
        forward_action="service.action2"
    ))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga("test_saga")

    # Assert
    assert execution.is_completed()
    assert len(results) == 2
    assert "service.action1" in results
    assert "service.action2" in results

@pytest.mark.asyncio
async def test_saga_compensation():
    # Test compensation on failure
    state_store = InMemorySagaStateStore()
    compensations = []

    async def mock_invoker(action: str, params: dict):
        if "step2" in action and "delete" not in action:
            raise Exception("Step 2 failed!")
        if "delete" in action:
            compensations.append(action)
        return {"status": "success"}

    orchestrator = SagaOrchestrator(
        state_store=state_store,
        service_invoker=mock_invoker
    )

    # Define saga with compensation
    saga = SagaDefinition(name="test_saga")
    saga.add_step(SagaStepDefinition(
        name="step1",
        forward_action="service.create1",
        compensation_action="service.delete1"
    ))
    saga.add_step(SagaStepDefinition(
        name="step2",
        forward_action="service.create2",
        compensation_action="service.delete2"
    ))

    orchestrator.register_saga(saga)

    # Execute (will fail at step2)
    execution = await orchestrator.execute_saga("test_saga")

    # Assert
    assert execution.is_failed()
    assert execution.status == SagaStatus.COMPENSATED
    assert "service.delete1" in compensations  # Step1 compensated
```

## Performance Considerations

- **State Store**: Use Redis or PostgreSQL for production
- **Parallel Execution**: Use `SagaExecutionPolicy.PARALLEL` for independent steps
- **Timeout Configuration**: Set appropriate timeouts to avoid hanging
- **Cleanup**: Run periodic cleanup of old completed sagas
- **Monitoring**: Track saga duration and failure rates

## Troubleshooting

### Saga Stuck in Executing State

```python
# Check saga status
saga = await state_store.get_saga(saga_id)
print(f"Status: {saga.status}")
print(f"Steps: {[(s.name, s.status) for s in saga.step_executions.values()]}")

# Recover
await orchestrator.recover_saga(saga_id)
```

### Compensation Failed

```python
# Get compensation report
report = await comp_manager.get_compensation_report(saga)

# Manually compensate failed steps
for failed in report['failed_compensations']:
    step_name = failed['step_name']
    # Manual intervention required
    await manual_compensation(saga_id, step_name)
```

### High Memory Usage

```python
# Clean up old sagas
deleted = await state_store.cleanup_old_sagas(older_than_days=7)
print(f"Deleted {deleted} old sagas")
```

## License

This Saga Pattern Engine is part of the AI Platform ISO project.

## Support

For questions or issues:
- Check the examples in this README
- Review the source code documentation
- Contact the platform team
