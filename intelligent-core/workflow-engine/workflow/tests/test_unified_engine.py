"""
Tests for Unified Workflow Engine

Phase 1: Basic integration tests
Phase 2: Will add Workflow Intelligence integration tests
"""

import pytest
from datetime import datetime
from ..core.unified_engine import UnifiedWorkflowEngine
from ..bpmn.models import ProcessStatus, TaskStatus


# Sample BPMN XML for testing
SAMPLE_BIA_BPMN = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
             id="bia_process_definitions"
             targetNamespace="http://bcm.example.com/bpmn">

  <process id="bia_process" name="BIA Process">
    <startEvent id="start" name="Start BIA"/>

    <sequenceFlow id="flow1" sourceRef="start" targetRef="identify_processes"/>

    <userTask id="identify_processes" name="Identify Critical Processes"/>

    <sequenceFlow id="flow2" sourceRef="identify_processes" targetRef="analyze_dependencies"/>

    <userTask id="analyze_dependencies" name="Analyze Dependencies"/>

    <sequenceFlow id="flow3" sourceRef="analyze_dependencies" targetRef="assess_impact"/>

    <userTask id="assess_impact" name="Assess Impact"/>

    <sequenceFlow id="flow4" sourceRef="assess_impact" targetRef="end"/>

    <endEvent id="end" name="BIA Complete"/>
  </process>
</definitions>
"""


@pytest.fixture
def workflow_engine():
    """Create workflow engine for testing"""
    return UnifiedWorkflowEngine(
        tenant_id="test-tenant",
        module="bia",
        use_persistence=False  # In-memory for testing
    )


@pytest.mark.asyncio
async def test_create_workflow_engine(workflow_engine):
    """Test: Create workflow engine"""
    assert workflow_engine.tenant_id == "test-tenant"
    assert workflow_engine.module == "bia"
    assert workflow_engine.bpmn_engine is not None


@pytest.mark.asyncio
async def test_start_process_from_bpmn(workflow_engine):
    """Test: Start process from BPMN XML"""
    instance_id = await workflow_engine.start_process_from_bpmn(
        bpmn_xml=SAMPLE_BIA_BPMN,
        initial_variables={
            "org_id": "org-123",
            "org_context": {
                "industry": "healthcare",
                "size": "medium"
            }
        },
        started_by="user-789",
        process_name="BIA Process Test"
    )

    assert instance_id is not None
    assert isinstance(instance_id, str)

    # Verify instance was created
    instance = await workflow_engine.bpmn_engine.get_instance(instance_id)
    assert instance is not None
    assert instance.status == ProcessStatus.ACTIVE
    assert instance.variables["org_id"] == "org-123"


@pytest.mark.asyncio
async def test_get_visual_state(workflow_engine):
    """Test: Get visual state for UI"""
    # Start process
    instance_id = await workflow_engine.start_process_from_bpmn(
        bpmn_xml=SAMPLE_BIA_BPMN,
        initial_variables={"org_id": "org-123"}
    )

    # Get visual state
    state = await workflow_engine.get_visual_state(instance_id)

    assert state.type == "bpmn"
    assert state.bpmn_xml is not None
    assert len(state.current_activities) > 0
    assert len(state.active_tasks) > 0

    # Check first task
    first_task = state.active_tasks[0]
    assert first_task["activity_id"] == "identify_processes"
    assert first_task["name"] == "Identify Critical Processes"
    assert "ai_tip" in first_task


@pytest.mark.asyncio
async def test_complete_task_workflow(workflow_engine):
    """Test: Complete task and workflow progression"""
    # Start process
    instance_id = await workflow_engine.start_process_from_bpmn(
        bpmn_xml=SAMPLE_BIA_BPMN,
        initial_variables={"org_id": "org-123"}
    )

    # Get initial state
    state = await workflow_engine.get_visual_state(instance_id)
    assert state.current_activities == ["identify_processes"]

    # Get first task
    first_task_id = state.active_tasks[0]["id"]

    # Complete first task
    await workflow_engine.complete_task(
        task_id=first_task_id,
        variables={"processes_identified": 5},
        completed_by="user-789"
    )

    # Verify task completed
    task = await workflow_engine.bpmn_engine.get_task(first_task_id)
    assert task.status == TaskStatus.COMPLETED

    # Verify moved to next activity
    state = await workflow_engine.get_visual_state(instance_id)
    assert state.current_activities == ["analyze_dependencies"]
    assert len(state.active_tasks) == 1
    assert state.active_tasks[0]["activity_id"] == "analyze_dependencies"


@pytest.mark.asyncio
async def test_complete_full_workflow(workflow_engine):
    """Test: Complete entire workflow"""
    # Start process
    instance_id = await workflow_engine.start_process_from_bpmn(
        bpmn_xml=SAMPLE_BIA_BPMN,
        initial_variables={"org_id": "org-123"}
    )

    # Complete all tasks
    tasks_to_complete = [
        "identify_processes",
        "analyze_dependencies",
        "assess_impact"
    ]

    for expected_activity in tasks_to_complete:
        state = await workflow_engine.get_visual_state(instance_id)
        assert expected_activity in state.current_activities

        task_id = state.active_tasks[0]["id"]
        await workflow_engine.complete_task(
            task_id=task_id,
            variables={f"{expected_activity}_data": "completed"}
        )

    # Verify workflow completed
    instance = await workflow_engine.bpmn_engine.get_instance(instance_id)
    assert instance.status == ProcessStatus.COMPLETED
    assert instance.completed_at is not None


@pytest.mark.asyncio
async def test_get_active_tasks_for_user(workflow_engine):
    """Test: Get tasks assigned to user"""
    # Start process
    instance_id = await workflow_engine.start_process_from_bpmn(
        bpmn_xml=SAMPLE_BIA_BPMN,
        initial_variables={"org_id": "org-123"}
    )

    # Get first task and assign it
    state = await workflow_engine.get_visual_state(instance_id)
    first_task_id = state.active_tasks[0]["id"]

    await workflow_engine.bpmn_engine.assign_task(
        task_id=first_task_id,
        assignee="user-789"
    )

    # Get tasks for user
    user_tasks = await workflow_engine.get_active_tasks_for_user(
        assignee="user-789"
    )

    assert len(user_tasks) == 1
    assert user_tasks[0]["id"] == first_task_id
    assert user_tasks[0]["assignee"] == "user-789"


@pytest.mark.asyncio
async def test_terminate_process(workflow_engine):
    """Test: Terminate process"""
    # Start process
    instance_id = await workflow_engine.start_process_from_bpmn(
        bpmn_xml=SAMPLE_BIA_BPMN,
        initial_variables={"org_id": "org-123"}
    )

    # Terminate
    await workflow_engine.terminate_process(
        workflow_id=instance_id,
        reason="User cancelled"
    )

    # Verify terminated
    instance = await workflow_engine.bpmn_engine.get_instance(instance_id)
    assert instance.status == ProcessStatus.TERMINATED

    # Verify tasks cancelled
    state = await workflow_engine.get_visual_state(instance_id)
    for task in state.active_tasks:
        task_obj = await workflow_engine.bpmn_engine.get_task(task["id"])
        assert task_obj.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_event_handlers_called(workflow_engine):
    """Test: Event handlers are called"""
    events_received = []

    # Register event handler
    @workflow_engine.bpmn_engine.on_event("bpmn.instance.started")
    async def on_started(event):
        events_received.append(event)

    # Start process
    instance_id = await workflow_engine.start_process_from_bpmn(
        bpmn_xml=SAMPLE_BIA_BPMN,
        initial_variables={"org_id": "org-123"}
    )

    # Verify event received
    assert len(events_received) == 1
    assert events_received[0]["event_type"] == "bpmn.instance.started"
    assert events_received[0]["data"]["instance_id"] == instance_id


@pytest.mark.asyncio
async def test_invalid_bpmn_xml(workflow_engine):
    """Test: Invalid BPMN XML raises error"""
    with pytest.raises(ValueError, match="Invalid XML"):
        await workflow_engine.start_process_from_bpmn(
            bpmn_xml="<invalid>xml</invalid>",
            initial_variables={}
        )


@pytest.mark.asyncio
async def test_template_workflow_not_implemented(workflow_engine):
    """Test: Template workflows raise NotImplementedError in Phase 1"""
    with pytest.raises(NotImplementedError, match="Phase 2"):
        await workflow_engine.start_process_from_template(
            template_name="bia_standard",
            initial_variables={}
        )


# ========== Integration Test (will work in Phase 2) ==========

@pytest.mark.skip(reason="Phase 2 - requires Workflow Intelligence")
@pytest.mark.asyncio
async def test_ai_recommendations_injected():
    """Test: AI recommendations are injected into tasks (Phase 2)"""
    # TODO Phase 2: Test AI integration
    pass


@pytest.mark.skip(reason="Phase 2 - requires Workflow Intelligence")
@pytest.mark.asyncio
async def test_case_collection_on_completion():
    """Test: Case is collected when workflow completes (Phase 2)"""
    # TODO Phase 2: Test Case Library integration
    pass
