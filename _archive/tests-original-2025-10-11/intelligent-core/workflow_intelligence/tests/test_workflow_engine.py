"""
🧪 ТЕСТЫ - Workflow Engine

Полное покрытие всех функций Workflow Engine
"""

import pytest
import asyncio
from datetime import datetime
from typing import List, Optional

# Import components to test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflow_engine import (
    WorkflowEngine,
    WorkflowContext,
    WorkflowEvent,
    EventBus,
    InMemoryStorageAdapter
)


# ============================================================================
# FIXTURES
# ============================================================================

class MockStateMachine:
    """Mock state machine для тестирования"""

    @staticmethod
    def can_transition(from_state: str, action: str) -> bool:
        valid_transitions = {
            ("initial", "start"): True,
            ("started", "process"): True,
            ("processed", "complete"): True,
        }
        return valid_transitions.get((from_state, action), False)

    @staticmethod
    def get_next_state(from_state: str, action: str) -> Optional[str]:
        transitions = {
            ("initial", "start"): "started",
            ("started", "process"): "processed",
            ("processed", "complete"): "completed",
        }
        return transitions.get((from_state, action))

    @staticmethod
    def get_allowed_actions(state: str) -> List[str]:
        allowed = {
            "initial": ["start"],
            "started": ["process"],
            "processed": ["complete"],
            "completed": [],
        }
        return allowed.get(state, [])

    @staticmethod
    def get_completion_percentage(state: str) -> float:
        progress = {
            "initial": 0.0,
            "started": 0.25,
            "processed": 0.75,
            "completed": 1.0,
        }
        return progress.get(state, 0.0)

    @staticmethod
    def get_required_fields(state: str) -> List[str]:
        required = {
            "started": ["name"],
            "processed": ["name", "data"],
            "completed": ["name", "data", "result"],
        }
        return required.get(state, [])


@pytest.fixture
def event_bus():
    """Event bus instance"""
    return EventBus()


@pytest.fixture
def storage():
    """In-memory storage"""
    return InMemoryStorageAdapter()


@pytest.fixture
def workflow_engine(storage, event_bus):
    """Workflow engine instance"""
    return WorkflowEngine(
        module="test",
        state_machine=MockStateMachine,
        storage_adapter=storage,
        event_bus=event_bus
    )


# ============================================================================
# TESTS: Workflow Engine Basic Operations
# ============================================================================

@pytest.mark.asyncio
async def test_start_workflow(workflow_engine):
    """Тест: Запуск workflow"""

    workflow_id = "test-001"
    initial_data = {"name": "Test Workflow"}

    context = await workflow_engine.start(
        workflow_id=workflow_id,
        initial_data=initial_data,
        tenant_id="test-tenant",
        user_id="user-001"
    )

    assert context.workflow_id == workflow_id
    assert context.module == "test"
    assert context.current_stage == "initial"
    assert context.progress_percentage == 0.0
    assert context.tenant_id == "test-tenant"
    assert context.user_id == "user-001"
    assert context.workflow_data["name"] == "Test Workflow"


@pytest.mark.asyncio
async def test_execute_action_success(workflow_engine):
    """Тест: Успешное выполнение действия"""

    workflow_id = "test-002"

    # Start workflow
    await workflow_engine.start(workflow_id, {"name": "Test"})

    # Execute action
    context = await workflow_engine.execute_action(
        workflow_id=workflow_id,
        action="start",
        action_data={"started_at": datetime.utcnow().isoformat()},
        user_id="user-001"
    )

    assert context.current_stage == "started"
    assert context.progress_percentage == 25.0
    assert len(context.completed_steps) == 1
    assert context.completed_steps[0]["action"] == "start"


@pytest.mark.asyncio
async def test_execute_action_invalid(workflow_engine):
    """Тест: Невалидное действие"""

    workflow_id = "test-003"

    # Start workflow
    await workflow_engine.start(workflow_id, {"name": "Test"})

    # Try invalid action
    with pytest.raises(ValueError, match="not allowed"):
        await workflow_engine.execute_action(
            workflow_id=workflow_id,
            action="complete",  # Can't complete from initial state
            action_data={}
        )


@pytest.mark.asyncio
async def test_workflow_completion(workflow_engine):
    """Тест: Завершение workflow"""

    workflow_id = "test-004"

    # Start and progress workflow
    await workflow_engine.start(workflow_id, {"name": "Test"})
    await workflow_engine.execute_action(workflow_id, "start", {})
    await workflow_engine.execute_action(workflow_id, "process", {"data": "processed"})

    # Complete
    context = await workflow_engine.complete(workflow_id)

    assert context.progress_percentage == 75.0  # At 'processed' state

    # Verify completed_at is set
    workflow = await workflow_engine.storage.get_workflow(workflow_id)
    assert workflow["completed_at"] is not None


# ============================================================================
# TESTS: Context Generation
# ============================================================================

@pytest.mark.asyncio
async def test_context_gaps_detection(workflow_engine):
    """Тест: Обнаружение gaps"""

    workflow_id = "test-005"

    # Start workflow
    await workflow_engine.start(workflow_id, {})

    # Move to state that requires fields
    await workflow_engine.execute_action(workflow_id, "start", {})

    context = await workflow_engine.get_context(workflow_id)

    # Should have gap for missing 'name' field
    assert len(context.gaps) > 0
    assert any(gap["field"] == "name" for gap in context.gaps)


@pytest.mark.asyncio
async def test_context_available_actions(workflow_engine):
    """Тест: Доступные действия"""

    workflow_id = "test-006"

    await workflow_engine.start(workflow_id, {"name": "Test"})

    context = await workflow_engine.get_context(workflow_id)

    assert len(context.available_actions) > 0
    assert any(action["id"] == "start" for action in context.available_actions)


@pytest.mark.asyncio
async def test_context_progress_calculation(workflow_engine):
    """Тест: Расчёт прогресса"""

    workflow_id = "test-007"

    # Initial state
    await workflow_engine.start(workflow_id, {"name": "Test"})
    context = await workflow_engine.get_context(workflow_id)
    assert context.progress_percentage == 0.0

    # After start
    await workflow_engine.execute_action(workflow_id, "start", {})
    context = await workflow_engine.get_context(workflow_id)
    assert context.progress_percentage == 25.0

    # After process
    await workflow_engine.execute_action(workflow_id, "process", {"data": "test"})
    context = await workflow_engine.get_context(workflow_id)
    assert context.progress_percentage == 75.0


# ============================================================================
# TESTS: Event Publishing
# ============================================================================

@pytest.mark.asyncio
async def test_event_publishing_on_start(workflow_engine):
    """Тест: Публикация события при старте"""

    events_received = []

    async def event_handler(event: WorkflowEvent):
        events_received.append(event)

    workflow_engine.event_bus.subscribe("test.workflow.started", event_handler)

    await workflow_engine.start("test-008", {"name": "Test"})

    # Wait a bit for event processing
    await asyncio.sleep(0.1)

    assert len(events_received) == 1
    assert events_received[0].event_type == "test.workflow.started"
    assert events_received[0].workflow_id == "test-008"


@pytest.mark.asyncio
async def test_event_publishing_on_action(workflow_engine):
    """Тест: Публикация событий при действиях"""

    events_received = []

    async def event_handler(event: WorkflowEvent):
        events_received.append(event)

    workflow_engine.event_bus.subscribe("test.*", event_handler)

    await workflow_engine.start("test-009", {"name": "Test"})
    await workflow_engine.execute_action("test-009", "start", {})

    await asyncio.sleep(0.1)

    # Should have: started, action.executed, stage.changed
    assert len(events_received) >= 3

    event_types = [e.event_type for e in events_received]
    assert "test.workflow.started" in event_types
    assert "test.action.executed" in event_types
    assert "test.stage.changed" in event_types


@pytest.mark.asyncio
async def test_event_publishing_on_completion(workflow_engine):
    """Тест: Публикация события при завершении"""

    events_received = []

    async def event_handler(event: WorkflowEvent):
        events_received.append(event)

    workflow_engine.event_bus.subscribe("test.workflow.completed", event_handler)

    await workflow_engine.start("test-010", {"name": "Test"})
    await workflow_engine.complete("test-010")

    await asyncio.sleep(0.1)

    assert len(events_received) == 1
    assert events_received[0].event_type == "test.workflow.completed"

    # Check event data
    event_data = events_received[0].data
    assert "duration_seconds" in event_data
    assert "total_steps" in event_data


# ============================================================================
# TESTS: Storage Adapter
# ============================================================================

@pytest.mark.asyncio
async def test_storage_create_workflow(storage):
    """Тест: Создание workflow в storage"""

    workflow = {
        "workflow_id": "test-011",
        "module": "test",
        "current_stage": "initial",
        "workflow_data": {"name": "Test"},
        "started_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "completed_steps": []
    }

    created = await storage.create_workflow(workflow)

    assert created["workflow_id"] == "test-011"

    # Retrieve it
    retrieved = await storage.get_workflow("test-011")
    assert retrieved is not None
    assert retrieved["module"] == "test"


@pytest.mark.asyncio
async def test_storage_update_workflow(storage):
    """Тест: Обновление workflow"""

    workflow = {
        "workflow_id": "test-012",
        "module": "test",
        "current_stage": "initial",
        "workflow_data": {},
        "started_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "completed_steps": []
    }

    await storage.create_workflow(workflow)

    # Update
    workflow["current_stage"] = "started"
    workflow["workflow_data"]["updated"] = True

    updated = await storage.update_workflow("test-012", workflow)

    assert updated["current_stage"] == "started"
    assert updated["workflow_data"]["updated"] is True


@pytest.mark.asyncio
async def test_storage_list_workflows(storage):
    """Тест: Список workflows"""

    # Create multiple workflows
    for i in range(5):
        await storage.create_workflow({
            "workflow_id": f"test-{i}",
            "module": "test",
            "current_stage": "initial",
            "workflow_data": {},
            "started_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_steps": [],
            "tenant_id": "tenant-1" if i < 3 else "tenant-2"
        })

    # List all
    all_workflows = await storage.list_workflows()
    assert len(all_workflows) == 5

    # Filter by tenant
    tenant1_workflows = await storage.list_workflows(tenant_id="tenant-1")
    assert len(tenant1_workflows) == 3

    # Filter by module
    test_workflows = await storage.list_workflows(module="test")
    assert len(test_workflows) == 5


# ============================================================================
# TESTS: Integration
# ============================================================================

@pytest.mark.asyncio
async def test_full_workflow_lifecycle(workflow_engine):
    """Тест: Полный жизненный цикл workflow"""

    workflow_id = "test-full-001"

    # Track events
    events = []

    async def track_events(event):
        events.append(event.event_type)

    workflow_engine.event_bus.subscribe("test.*", track_events)

    # 1. Start
    context = await workflow_engine.start(
        workflow_id,
        {"name": "Full Test"},
        tenant_id="test-tenant"
    )
    assert context.current_stage == "initial"
    assert context.progress_percentage == 0.0

    # 2. Execute actions
    context = await workflow_engine.execute_action(workflow_id, "start", {})
    assert context.current_stage == "started"
    assert context.progress_percentage == 25.0

    context = await workflow_engine.execute_action(
        workflow_id,
        "process",
        {"data": "processed_data"}
    )
    assert context.current_stage == "processed"
    assert context.progress_percentage == 75.0

    # 3. Complete
    context = await workflow_engine.complete(workflow_id)

    # 4. Verify final state
    assert len(context.completed_steps) == 2
    assert context.workflow_data["name"] == "Full Test"
    assert context.workflow_data["data"] == "processed_data"

    # 5. Verify events
    await asyncio.sleep(0.1)
    assert "test.workflow.started" in events
    assert "test.action.executed" in events
    assert "test.stage.changed" in events
    assert "test.workflow.completed" in events


# ============================================================================
# TESTS: Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_workflow_not_found(workflow_engine):
    """Тест: Workflow не найден"""

    with pytest.raises(ValueError, match="not found"):
        await workflow_engine.get_context("non-existent")


@pytest.mark.asyncio
async def test_invalid_action_for_state(workflow_engine):
    """Тест: Невалидное действие для состояния"""

    workflow_id = "test-error-001"

    await workflow_engine.start(workflow_id, {"name": "Test"})

    # Try to execute action not allowed in current state
    with pytest.raises(ValueError, match="not allowed"):
        await workflow_engine.execute_action(workflow_id, "process", {})


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_workflows(workflow_engine):
    """Тест: Параллельные workflows"""

    async def run_workflow(i):
        workflow_id = f"concurrent-{i}"
        await workflow_engine.start(workflow_id, {"name": f"Test {i}"})
        await workflow_engine.execute_action(workflow_id, "start", {})
        return await workflow_engine.get_context(workflow_id)

    # Run 10 workflows concurrently
    results = await asyncio.gather(*[run_workflow(i) for i in range(10)])

    assert len(results) == 10
    assert all(r.current_stage == "started" for r in results)


@pytest.mark.asyncio
async def test_event_bus_performance(event_bus):
    """Тест: Производительность event bus"""

    events_received = []

    async def handler(event):
        events_received.append(event)

    # Subscribe 100 handlers
    for i in range(100):
        event_bus.subscribe("test.*", handler)

    # Publish 100 events
    for i in range(100):
        await event_bus.publish(WorkflowEvent(
            event_type="test.event",
            workflow_id=f"perf-{i}",
            module="test"
        ))

    await asyncio.sleep(0.5)

    # Should have 100 events * 100 handlers = 10,000 calls
    assert len(events_received) == 10000


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
