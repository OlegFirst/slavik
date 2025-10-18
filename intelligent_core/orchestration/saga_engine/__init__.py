"""
Saga Pattern Engine
===================

Distributed transaction management using the Saga pattern.

The Saga pattern coordinates distributed transactions across multiple services
by breaking them into a sequence of local transactions, each with a compensating
transaction for rollback.

Key Components:
--------------
- SagaOrchestrator: Main orchestrator for executing sagas
- SagaDefinition: Definition of saga steps and compensation logic
- CompensationManager: Handles rollback on failure
- SagaStateStore: Persistent state storage

Usage Example:
-------------
```python
from saga_engine import (
    SagaOrchestrator, SagaDefinition, SagaStepDefinition,
    InMemorySagaStateStore, SagaExecutionPolicy
)

# Create state store
state_store = InMemorySagaStateStore()

# Create orchestrator
orchestrator = SagaOrchestrator(
    state_store=state_store,
    service_invoker=my_service_invoker,
    event_publisher=my_event_publisher
)

# Define a saga
bcm_program_saga = SagaDefinition(
    name="create_bcm_program",
    description="Create complete BCM program",
    execution_policy=SagaExecutionPolicy.SEQUENTIAL
)

# Add steps
bcm_program_saga.add_step(
    SagaStepDefinition(
        name="create_bia",
        description="Create Business Impact Analysis",
        forward_action="bia_service.create_assessment",
        forward_params={"scope": "organization"},
        compensation_action="bia_service.delete_assessment",
        timeout_seconds=60
    )
)

# Register and execute
orchestrator.register_saga(bcm_program_saga)
saga_execution = await orchestrator.execute_saga(
    "create_bcm_program",
    initial_context={"organization_id": "org-123"}
)
```

Features:
---------
- Sequential, parallel, and pipeline execution modes
- Automatic retry with exponential backoff
- Multiple compensation strategies
- State persistence for crash recovery
- Event publishing for monitoring
- Multi-tenancy support
- Correlation tracking

Compensation Strategies:
-----------------------
- BACKWARD_RECOVERY: Rollback all completed steps (default)
- FORWARD_RECOVERY: Try to complete despite errors
- PARTIAL_COMPENSATION: Only rollback critical steps

See README.md for detailed documentation and examples.
"""

from .saga_definition import (
    SagaDefinition,
    SagaStepDefinition,
    SagaExecution,
    SagaStepExecution,
    SagaStatus,
    SagaStepStatus,
    SagaExecutionPolicy,
    CompensationStrategy
)

from .saga_state_store import (
    SagaStateStore,
    InMemorySagaStateStore,
    RedisSagaStateStore,
    PostgresSagaStateStore
)

from .compensation_manager import CompensationManager

from .saga_orchestrator import SagaOrchestrator

__all__ = [
    # Core classes
    'SagaOrchestrator',
    'CompensationManager',

    # Definitions
    'SagaDefinition',
    'SagaStepDefinition',

    # Execution state
    'SagaExecution',
    'SagaStepExecution',

    # Enums
    'SagaStatus',
    'SagaStepStatus',
    'SagaExecutionPolicy',
    'CompensationStrategy',

    # Storage
    'SagaStateStore',
    'InMemorySagaStateStore',
    'RedisSagaStateStore',
    'PostgresSagaStateStore',
]

__version__ = '1.0.0'
