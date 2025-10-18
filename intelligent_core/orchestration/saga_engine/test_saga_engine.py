"""
Saga Engine Tests
==================

Unit tests for the Saga Pattern Engine.

Run with: pytest test_saga_engine.py -v
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from saga_definition import (
    SagaDefinition,
    SagaStepDefinition,
    SagaExecution,
    SagaStepExecution,
    SagaStatus,
    SagaStepStatus,
    SagaExecutionPolicy,
    CompensationStrategy
)
from saga_orchestrator import SagaOrchestrator
from saga_state_store import InMemorySagaStateStore
from compensation_manager import CompensationManager


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def state_store():
    """Create in-memory state store for testing"""
    return InMemorySagaStateStore()


@pytest.fixture
def mock_results():
    """Storage for mock service results"""
    return {
        "calls": [],
        "results": {},
        "should_fail": set()
    }


@pytest.fixture
def service_invoker(mock_results):
    """Mock service invoker"""

    async def invoker(action: str, params: Dict[str, Any]) -> Any:
        # Record call
        mock_results["calls"].append({
            "action": action,
            "params": params,
            "timestamp": datetime.utcnow()
        })

        # Check if should fail
        if action in mock_results["should_fail"]:
            raise Exception(f"Simulated failure for {action}")

        # Return predefined result or default
        return mock_results["results"].get(action, {
            "status": "success",
            "action": action
        })

    return invoker


@pytest.fixture
def event_log():
    """Storage for published events"""
    return []


@pytest.fixture
def event_publisher(event_log):
    """Mock event publisher"""

    async def publisher(event_type: str, data: Dict[str, Any]) -> None:
        event_log.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow()
        })

    return publisher


@pytest.fixture
def orchestrator(state_store, service_invoker, event_publisher):
    """Create configured orchestrator"""
    return SagaOrchestrator(
        state_store=state_store,
        service_invoker=service_invoker,
        event_publisher=event_publisher
    )


# ==============================================================================
# Saga Definition Tests
# ==============================================================================

def test_saga_definition_creation():
    """Test creating a saga definition"""
    saga = SagaDefinition(
        name="test_saga",
        description="Test saga",
        execution_policy=SagaExecutionPolicy.SEQUENTIAL
    )

    assert saga.name == "test_saga"
    assert saga.execution_policy == SagaExecutionPolicy.SEQUENTIAL
    assert len(saga.steps) == 0


def test_saga_add_step():
    """Test adding steps to saga"""
    saga = SagaDefinition(name="test_saga")

    step = SagaStepDefinition(
        name="step1",
        description="First step",
        forward_action="service.action1"
    )

    saga.add_step(step)

    assert len(saga.steps) == 1
    assert saga.steps[0].name == "step1"


def test_saga_validation():
    """Test saga validation"""
    saga = SagaDefinition(name="test_saga")

    # Empty saga should have error
    errors = saga.validate()
    assert "at least one step" in errors[0].lower()

    # Add valid step
    saga.add_step(SagaStepDefinition(
        name="step1",
        forward_action="service.action1"
    ))

    errors = saga.validate()
    assert len(errors) == 0


def test_saga_dependency_order():
    """Test dependency resolution"""
    saga = SagaDefinition(
        name="test_saga",
        execution_policy=SagaExecutionPolicy.PARALLEL
    )

    # Add steps with dependencies
    saga.add_step(SagaStepDefinition(name="step1", forward_action="service.action1"))
    saga.add_step(SagaStepDefinition(name="step2", forward_action="service.action2"))
    saga.add_step(SagaStepDefinition(
        name="step3",
        forward_action="service.action3",
        depends_on=["step1", "step2"]
    ))

    levels = saga.get_dependency_order()

    # Step 1 and 2 should be in first level
    assert set(levels[0]) == {"step1", "step2"}

    # Step 3 should be in second level
    assert levels[1] == ["step3"]


def test_circular_dependency_detection():
    """Test detection of circular dependencies"""
    saga = SagaDefinition(
        name="test_saga",
        execution_policy=SagaExecutionPolicy.PARALLEL
    )

    saga.add_step(SagaStepDefinition(
        name="step1",
        forward_action="service.action1",
        depends_on=["step2"]
    ))
    saga.add_step(SagaStepDefinition(
        name="step2",
        forward_action="service.action2",
        depends_on=["step1"]
    ))

    errors = saga.validate()
    assert any("circular" in e.lower() for e in errors)


# ==============================================================================
# Sequential Execution Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_sequential_execution_success(orchestrator, mock_results):
    """Test successful sequential execution"""

    # Define saga
    saga = SagaDefinition(
        name="test_saga",
        execution_policy=SagaExecutionPolicy.SEQUENTIAL
    )

    saga.add_step(SagaStepDefinition(name="step1", forward_action="service.action1"))
    saga.add_step(SagaStepDefinition(name="step2", forward_action="service.action2"))
    saga.add_step(SagaStepDefinition(name="step3", forward_action="service.action3"))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga(
        "test_saga",
        initial_context={"test": "data"}
    )

    # Verify
    assert execution.is_completed()
    assert execution.status == SagaStatus.COMPLETED
    assert len(mock_results["calls"]) == 3
    assert mock_results["calls"][0]["action"] == "service.action1"
    assert mock_results["calls"][1]["action"] == "service.action2"
    assert mock_results["calls"][2]["action"] == "service.action3"


@pytest.mark.asyncio
async def test_sequential_execution_failure(orchestrator, mock_results):
    """Test sequential execution with failure"""

    # Configure step2 to fail
    mock_results["should_fail"].add("service.action2")

    # Define saga
    saga = SagaDefinition(name="test_saga")

    saga.add_step(SagaStepDefinition(
        name="step1",
        forward_action="service.action1",
        compensation_action="service.compensation1"
    ))
    saga.add_step(SagaStepDefinition(
        name="step2",
        forward_action="service.action2"
    ))
    saga.add_step(SagaStepDefinition(
        name="step3",
        forward_action="service.action3"
    ))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga("test_saga")

    # Verify
    assert execution.is_failed()
    assert execution.status == SagaStatus.COMPENSATED
    assert len(mock_results["calls"]) == 5  # action1, action2 (fail), compensation1

    # Check that step3 was NOT called
    actions = [call["action"] for call in mock_results["calls"]]
    assert "service.action3" not in actions

    # Check that compensation was called
    assert "service.compensation1" in actions


# ==============================================================================
# Parallel Execution Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_parallel_execution(orchestrator, mock_results):
    """Test parallel execution of independent steps"""

    saga = SagaDefinition(
        name="test_saga",
        execution_policy=SagaExecutionPolicy.PARALLEL
    )

    # Three independent steps
    saga.add_step(SagaStepDefinition(name="step1", forward_action="service.action1"))
    saga.add_step(SagaStepDefinition(name="step2", forward_action="service.action2"))
    saga.add_step(SagaStepDefinition(name="step3", forward_action="service.action3"))

    orchestrator.register_saga(saga)

    # Execute
    start_time = datetime.utcnow()
    execution = await orchestrator.execute_saga("test_saga")
    end_time = datetime.utcnow()

    # Verify
    assert execution.is_completed()
    assert len(mock_results["calls"]) == 3

    # All steps should have started around the same time (parallel)
    call_times = [call["timestamp"] for call in mock_results["calls"]]
    time_spread = (max(call_times) - min(call_times)).total_seconds()
    assert time_spread < 1.0  # Should start within 1 second of each other


@pytest.mark.asyncio
async def test_parallel_with_dependencies(orchestrator, mock_results):
    """Test parallel execution respecting dependencies"""

    saga = SagaDefinition(
        name="test_saga",
        execution_policy=SagaExecutionPolicy.PARALLEL
    )

    saga.add_step(SagaStepDefinition(name="step1", forward_action="service.action1"))
    saga.add_step(SagaStepDefinition(name="step2", forward_action="service.action2"))
    saga.add_step(SagaStepDefinition(
        name="step3",
        forward_action="service.action3",
        depends_on=["step1", "step2"]
    ))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga("test_saga")

    # Verify
    assert execution.is_completed()

    # Check execution order
    actions = [call["action"] for call in mock_results["calls"]]

    # step1 and step2 should come before step3
    step1_idx = actions.index("service.action1")
    step2_idx = actions.index("service.action2")
    step3_idx = actions.index("service.action3")

    assert step1_idx < step3_idx
    assert step2_idx < step3_idx


# ==============================================================================
# Pipeline Execution Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_pipeline_execution(orchestrator, mock_results):
    """Test pipeline execution with data flow"""

    # Configure results to flow
    mock_results["results"]["service.action1"] = {"output": "data1"}
    mock_results["results"]["service.action2"] = {"output": "data2"}

    saga = SagaDefinition(
        name="test_saga",
        execution_policy=SagaExecutionPolicy.PIPELINE
    )

    saga.add_step(SagaStepDefinition(name="step1", forward_action="service.action1"))
    saga.add_step(SagaStepDefinition(name="step2", forward_action="service.action2"))
    saga.add_step(SagaStepDefinition(name="step3", forward_action="service.action3"))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga(
        "test_saga",
        initial_context={"initial": "value"}
    )

    # Verify
    assert execution.is_completed()

    # Check that context accumulated data
    assert "output" in execution.execution_context
    assert execution.execution_context["initial"] == "value"


# ==============================================================================
# Compensation Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_backward_recovery_compensation(orchestrator, mock_results):
    """Test backward recovery compensation strategy"""

    # Step 2 will fail
    mock_results["should_fail"].add("service.action2")

    saga = SagaDefinition(
        name="test_saga",
        compensation_strategy=CompensationStrategy.BACKWARD_RECOVERY
    )

    saga.add_step(SagaStepDefinition(
        name="step1",
        forward_action="service.action1",
        compensation_action="service.compensation1"
    ))
    saga.add_step(SagaStepDefinition(
        name="step2",
        forward_action="service.action2",
        compensation_action="service.compensation2"
    ))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga("test_saga")

    # Verify
    assert execution.status == SagaStatus.COMPENSATED

    # Check compensation was called for step1 only (step2 never completed)
    actions = [call["action"] for call in mock_results["calls"]]
    assert "service.compensation1" in actions
    assert "service.compensation2" not in actions


@pytest.mark.asyncio
async def test_partial_compensation(orchestrator, mock_results):
    """Test partial compensation strategy"""

    # Step 3 will fail
    mock_results["should_fail"].add("service.action3")

    saga = SagaDefinition(
        name="test_saga",
        compensation_strategy=CompensationStrategy.PARTIAL_COMPENSATION
    )

    # Step 1 is critical
    saga.add_step(SagaStepDefinition(
        name="step1",
        forward_action="service.action1",
        compensation_action="service.compensation1",
        critical=True
    ))

    # Step 2 is NOT critical
    saga.add_step(SagaStepDefinition(
        name="step2",
        forward_action="service.action2",
        compensation_action="service.compensation2",
        critical=False
    ))

    # Step 3 will fail
    saga.add_step(SagaStepDefinition(
        name="step3",
        forward_action="service.action3"
    ))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga("test_saga")

    # Verify
    actions = [call["action"] for call in mock_results["calls"]]

    # Only critical step1 should be compensated
    assert "service.compensation1" in actions
    assert "service.compensation2" not in actions


# ==============================================================================
# Retry Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_step_retry(orchestrator, mock_results):
    """Test automatic step retry on failure"""

    call_count = {"count": 0}

    async def failing_invoker(action: str, params: Dict[str, Any]) -> Any:
        mock_results["calls"].append({"action": action, "params": params})

        if action == "service.action1":
            call_count["count"] += 1
            if call_count["count"] < 3:  # Fail first 2 times
                raise Exception("Temporary failure")

        return {"status": "success"}

    # Create orchestrator with failing invoker
    orchestrator = SagaOrchestrator(
        state_store=InMemorySagaStateStore(),
        service_invoker=failing_invoker
    )

    saga = SagaDefinition(name="test_saga")

    saga.add_step(SagaStepDefinition(
        name="step1",
        forward_action="service.action1",
        max_retries=3,
        retry_delay_seconds=0  # No delay for testing
    ))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga("test_saga")

    # Verify - should succeed after retries
    assert execution.is_completed()
    assert call_count["count"] == 3  # Failed twice, succeeded third time


# ==============================================================================
# State Store Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_state_persistence(state_store):
    """Test saga state persistence"""

    # Create saga execution
    saga = SagaExecution(
        saga_id="test-saga-123",
        definition_name="test_saga",
        definition_version="1.0",
        status=SagaStatus.EXECUTING,
        started_at=datetime.utcnow()
    )

    # Save
    await state_store.save_saga(saga)

    # Retrieve
    retrieved = await state_store.get_saga("test-saga-123")

    # Verify
    assert retrieved is not None
    assert retrieved.saga_id == saga.saga_id
    assert retrieved.status == SagaStatus.EXECUTING


@pytest.mark.asyncio
async def test_step_persistence(state_store):
    """Test step state persistence"""

    # Create saga
    saga = SagaExecution(
        saga_id="test-saga-123",
        definition_name="test_saga",
        definition_version="1.0"
    )
    await state_store.save_saga(saga)

    # Create step
    step = SagaStepExecution(
        step_id="step-1",
        step_name="test_step",
        saga_id="test-saga-123",
        status=SagaStepStatus.COMPLETED,
        result={"output": "test"}
    )

    # Save step
    await state_store.save_step("test-saga-123", step)

    # Retrieve
    retrieved_step = await state_store.get_step("test-saga-123", "test_step")

    # Verify
    assert retrieved_step is not None
    assert retrieved_step.step_name == "test_step"
    assert retrieved_step.status == SagaStepStatus.COMPLETED
    assert retrieved_step.result["output"] == "test"


# ==============================================================================
# Event Publishing Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_event_publishing(orchestrator, event_log):
    """Test that events are published during saga execution"""

    saga = SagaDefinition(name="test_saga")
    saga.add_step(SagaStepDefinition(name="step1", forward_action="service.action1"))

    orchestrator.register_saga(saga)

    # Execute
    await orchestrator.execute_saga("test_saga")

    # Verify events
    event_types = [event["type"] for event in event_log]

    assert "saga.started" in event_types
    assert "saga.step.started" in event_types
    assert "saga.step.completed" in event_types
    assert "saga.completed" in event_types


# ==============================================================================
# Recovery Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_saga_recovery(state_store, service_invoker):
    """Test saga recovery after crash"""

    # Create orchestrator and execute saga
    orchestrator1 = SagaOrchestrator(
        state_store=state_store,
        service_invoker=service_invoker
    )

    saga = SagaDefinition(name="test_saga")
    saga.add_step(SagaStepDefinition(name="step1", forward_action="service.action1"))
    saga.add_step(SagaStepDefinition(name="step2", forward_action="service.action2"))

    orchestrator1.register_saga(saga)

    execution = await orchestrator1.execute_saga("test_saga")
    saga_id = execution.saga_id

    # Simulate crash and restart with new orchestrator
    orchestrator2 = SagaOrchestrator(
        state_store=state_store,  # Same state store
        service_invoker=service_invoker
    )

    orchestrator2.register_saga(saga)

    # Recover
    recovered = await orchestrator2.recover_saga(saga_id)

    # Verify
    assert recovered is not None
    assert recovered.saga_id == saga_id
    assert recovered.is_completed()


# ==============================================================================
# Integration Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_complex_saga_workflow(orchestrator, mock_results):
    """Test a complex saga with multiple features"""

    # Configure some results
    mock_results["results"]["service.get_data"] = {"data": "important"}

    saga = SagaDefinition(
        name="complex_saga",
        execution_policy=SagaExecutionPolicy.PARALLEL,
        compensation_strategy=CompensationStrategy.BACKWARD_RECOVERY,
        total_timeout_seconds=60
    )

    # Parallel data fetching
    saga.add_step(SagaStepDefinition(
        name="fetch_data_1",
        forward_action="service.get_data",
        compensation_action="service.cleanup_data"
    ))
    saga.add_step(SagaStepDefinition(
        name="fetch_data_2",
        forward_action="service.get_data",
        compensation_action="service.cleanup_data"
    ))

    # Processing depends on both fetches
    saga.add_step(SagaStepDefinition(
        name="process_data",
        forward_action="service.process",
        depends_on=["fetch_data_1", "fetch_data_2"],
        compensation_action="service.revert_process"
    ))

    # Final step
    saga.add_step(SagaStepDefinition(
        name="finalize",
        forward_action="service.finalize",
        depends_on=["process_data"],
        critical=True
    ))

    orchestrator.register_saga(saga)

    # Execute
    execution = await orchestrator.execute_saga(
        "complex_saga",
        initial_context={"user_id": "123"}
    )

    # Verify
    assert execution.is_completed()
    assert len(mock_results["calls"]) == 4

    # Check dependency order
    actions = [call["action"] for call in mock_results["calls"]]
    process_idx = actions.index("service.process")
    finalize_idx = actions.index("service.finalize")

    # Both get_data calls should come before process
    assert process_idx > 1

    # process should come before finalize
    assert process_idx < finalize_idx


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
