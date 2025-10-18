"""
Saga Definition Models
======================

Defines the structure and models for saga transactions, including steps,
compensation logic, and execution policies.

A Saga is a sequence of local transactions where each transaction has a
compensating transaction for rollback.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime
from enum import Enum
import uuid


class SagaStepStatus(Enum):
    """Status of a saga step"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    COMPENSATION_FAILED = "compensation_failed"


class SagaStatus(Enum):
    """Status of the overall saga"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    COMPENSATION_FAILED = "compensation_failed"


class SagaExecutionPolicy(Enum):
    """Saga execution policies"""
    SEQUENTIAL = "sequential"  # Execute steps in order
    PARALLEL = "parallel"  # Execute independent steps in parallel
    PIPELINE = "pipeline"  # Pipeline pattern with data flow


class CompensationStrategy(Enum):
    """Compensation strategies on failure"""
    BACKWARD_RECOVERY = "backward"  # Rollback completed steps (default)
    FORWARD_RECOVERY = "forward"  # Try to complete saga despite errors
    PARTIAL_COMPENSATION = "partial"  # Compensate only critical steps


@dataclass
class SagaStepDefinition:
    """
    Definition of a single step in a saga.

    Each step has:
    - Forward transaction (the actual operation)
    - Compensating transaction (rollback operation)
    - Timeout and retry policies
    """

    name: str
    description: str

    # Forward transaction
    forward_action: str  # Service method to call (e.g., "bia_service.create_assessment")
    forward_params: Dict[str, Any] = field(default_factory=dict)

    # Compensating transaction
    compensation_action: Optional[str] = None  # Service method for rollback
    compensation_params: Dict[str, Any] = field(default_factory=dict)

    # Execution policies
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5

    # Dependencies (step names that must complete before this step)
    depends_on: List[str] = field(default_factory=list)

    # Idempotency key for retry safety
    idempotency_key_field: Optional[str] = None  # Field in params to use as idempotency key

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Critical flag - if True, must compensate on saga failure
    critical: bool = True

    # Step ID (auto-generated)
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def is_compensatable(self) -> bool:
        """Check if step has compensation logic"""
        return self.compensation_action is not None

    def get_idempotency_key(self, context: Dict[str, Any]) -> Optional[str]:
        """Extract idempotency key from execution context"""
        if not self.idempotency_key_field:
            return None

        # Try to get from forward_params first
        if self.idempotency_key_field in self.forward_params:
            return str(self.forward_params[self.idempotency_key_field])

        # Try from context
        if self.idempotency_key_field in context:
            return str(context[self.idempotency_key_field])

        return None


@dataclass
class SagaDefinition:
    """
    Definition of a complete saga (distributed transaction).

    A saga consists of:
    - Multiple steps (local transactions)
    - Compensation logic for each step
    - Execution policy and timeout
    - Recovery strategies
    """

    name: str
    description: str

    # Steps in the saga
    steps: List[SagaStepDefinition] = field(default_factory=list)

    # Execution policies
    execution_policy: SagaExecutionPolicy = SagaExecutionPolicy.SEQUENTIAL
    compensation_strategy: CompensationStrategy = CompensationStrategy.BACKWARD_RECOVERY

    # Timeouts
    total_timeout_seconds: int = 300  # 5 minutes default
    step_timeout_seconds: int = 30  # Default for steps without explicit timeout

    # Retry policies
    max_saga_retries: int = 1  # Retry entire saga on failure

    # Saga ID (auto-generated)
    saga_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Version for saga definition updates
    version: str = "1.0"

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Hooks for lifecycle events
    on_start: Optional[str] = None  # Called when saga starts
    on_complete: Optional[str] = None  # Called when saga completes successfully
    on_failure: Optional[str] = None  # Called when saga fails
    on_compensated: Optional[str] = None  # Called when compensation completes

    def add_step(self, step: SagaStepDefinition) -> 'SagaDefinition':
        """Add a step to the saga"""
        self.steps.append(step)
        return self

    def get_step(self, step_name: str) -> Optional[SagaStepDefinition]:
        """Get step by name"""
        for step in self.steps:
            if step.name == step_name:
                return step
        return None

    def get_dependency_order(self) -> List[List[str]]:
        """
        Get execution order respecting dependencies.
        Returns list of lists where each inner list can execute in parallel.
        """
        if self.execution_policy == SagaExecutionPolicy.SEQUENTIAL:
            # Sequential: each step in its own batch
            return [[step.name] for step in self.steps]

        # Build dependency graph
        step_names = {step.name for step in self.steps}
        dependencies = {step.name: set(step.depends_on) for step in self.steps}

        # Topological sort with level grouping
        levels = []
        remaining = set(step_names)
        completed = set()

        while remaining:
            # Find steps with no pending dependencies
            ready = {
                name for name in remaining
                if not dependencies[name] or dependencies[name].issubset(completed)
            }

            if not ready:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected in saga {self.name}")

            levels.append(sorted(ready))
            remaining -= ready
            completed |= ready

        return levels

    def validate(self) -> List[str]:
        """
        Validate saga definition.
        Returns list of validation errors (empty if valid).
        """
        errors = []

        if not self.name:
            errors.append("Saga name is required")

        if not self.steps:
            errors.append("Saga must have at least one step")

        # Check for duplicate step names
        step_names = [step.name for step in self.steps]
        if len(step_names) != len(set(step_names)):
            errors.append("Duplicate step names found")

        # Validate dependencies
        valid_names = set(step_names)
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in valid_names:
                    errors.append(f"Step '{step.name}' depends on unknown step '{dep}'")

        # Check for circular dependencies
        try:
            self.get_dependency_order()
        except ValueError as e:
            errors.append(str(e))

        return errors


@dataclass
class SagaStepExecution:
    """Runtime execution state of a saga step"""

    step_id: str
    step_name: str
    saga_id: str

    # Status
    status: SagaStepStatus = SagaStepStatus.PENDING

    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Retry tracking
    attempts: int = 0
    max_attempts: int = 3

    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None

    # Compensation tracking
    compensation_started_at: Optional[datetime] = None
    compensation_completed_at: Optional[datetime] = None
    compensation_result: Optional[Dict[str, Any]] = None
    compensation_error: Optional[str] = None

    # Idempotency
    idempotency_key: Optional[str] = None

    # Execution context (output from this step, input to next steps)
    output_context: Dict[str, Any] = field(default_factory=dict)

    def can_retry(self) -> bool:
        """Check if step can be retried"""
        return self.attempts < self.max_attempts and self.status == SagaStepStatus.FAILED

    def is_completed(self) -> bool:
        """Check if step completed successfully"""
        return self.status == SagaStepStatus.COMPLETED

    def needs_compensation(self) -> bool:
        """Check if step needs compensation"""
        return self.status == SagaStepStatus.COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence"""
        return {
            'step_id': self.step_id,
            'step_name': self.step_name,
            'saga_id': self.saga_id,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'result': self.result,
            'error': self.error,
            'error_details': self.error_details,
            'compensation_started_at': self.compensation_started_at.isoformat() if self.compensation_started_at else None,
            'compensation_completed_at': self.compensation_completed_at.isoformat() if self.compensation_completed_at else None,
            'compensation_result': self.compensation_result,
            'compensation_error': self.compensation_error,
            'idempotency_key': self.idempotency_key,
            'output_context': self.output_context
        }


@dataclass
class SagaExecution:
    """Runtime execution state of a saga"""

    saga_id: str
    definition_name: str
    definition_version: str

    # Status
    status: SagaStatus = SagaStatus.PENDING

    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Step executions
    step_executions: Dict[str, SagaStepExecution] = field(default_factory=dict)

    # Execution context (shared across steps)
    execution_context: Dict[str, Any] = field(default_factory=dict)

    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # Tenant isolation
    tenant_id: Optional[str] = None

    # Correlation tracking
    correlation_id: Optional[str] = None
    parent_saga_id: Optional[str] = None  # For nested sagas

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_completed_steps(self) -> List[SagaStepExecution]:
        """Get all completed steps in execution order"""
        completed = [
            step for step in self.step_executions.values()
            if step.status == SagaStepStatus.COMPLETED
        ]
        # Sort by completion time
        return sorted(completed, key=lambda x: x.completed_at or datetime.min)

    def get_failed_step(self) -> Optional[SagaStepExecution]:
        """Get the first failed step"""
        for step in self.step_executions.values():
            if step.status == SagaStepStatus.FAILED:
                return step
        return None

    def is_completed(self) -> bool:
        """Check if saga completed successfully"""
        return self.status == SagaStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if saga failed"""
        return self.status in [
            SagaStatus.FAILED,
            SagaStatus.COMPENSATION_FAILED
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence"""
        return {
            'saga_id': self.saga_id,
            'definition_name': self.definition_name,
            'definition_version': self.definition_version,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'step_executions': {
                name: step.to_dict()
                for name, step in self.step_executions.items()
            },
            'execution_context': self.execution_context,
            'result': self.result,
            'error': self.error,
            'tenant_id': self.tenant_id,
            'correlation_id': self.correlation_id,
            'parent_saga_id': self.parent_saga_id,
            'metadata': self.metadata
        }
