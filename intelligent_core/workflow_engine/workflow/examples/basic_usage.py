"""
Unified Workflow Engine - Basic Usage Examples

Демонстрирует как использовать UnifiedWorkflowEngine
"""

import asyncio
from intelligent_core.unified_workflow import UnifiedWorkflowEngine


# Sample BPMN for BIA process
BIA_BPMN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             id="bia_definitions"
             targetNamespace="http://bcm.acme.com/bpmn">

  <process id="bia_process" name="Business Impact Analysis">
    <startEvent id="start" name="Start BIA"/>
    <sequenceFlow id="flow1" sourceRef="start" targetRef="identify"/>

    <userTask id="identify" name="Identify Critical Processes"/>
    <sequenceFlow id="flow2" sourceRef="identify" targetRef="analyze"/>

    <userTask id="analyze" name="Analyze Dependencies"/>
    <sequenceFlow id="flow3" sourceRef="analyze" targetRef="assess"/>

    <userTask id="assess" name="Assess Impact"/>
    <sequenceFlow id="flow4" sourceRef="assess" targetRef="determine"/>

    <userTask id="determine" name="Determine RTO/RPO"/>
    <sequenceFlow id="flow5" sourceRef="determine" targetRef="end"/>

    <endEvent id="end" name="BIA Complete"/>
  </process>
</definitions>
"""


async def example_1_start_bia_process():
    """
    Example 1: Start BIA process from BPMN visual model
    """
    print("\n=== Example 1: Start BIA Process ===\n")

    # Initialize workflow engine
    workflow = UnifiedWorkflowEngine(
        tenant_id="acme-corp",
        module="bia"
    )

    # Start process from BPMN XML
    instance_id = await workflow.start_process_from_bpmn(
        bpmn_xml=BIA_BPMN_XML,
        initial_variables={
            "org_id": "org-456",
            "org_context": {
                "industry": "healthcare",
                "size": "medium",
                "employees": 250
            }
        },
        started_by="user-john",
        process_name="Acme Corp BIA 2025"
    )

    print(f"✅ BIA process started!")
    print(f"   Instance ID: {instance_id}")

    # Get visual state (for UI)
    state = await workflow.get_visual_state(instance_id)

    print(f"\n📊 Current State:")
    print(f"   Type: {state.type}")
    print(f"   Current Activities: {state.current_activities}")
    print(f"   Active Tasks: {len(state.active_tasks)}")

    if state.active_tasks:
        first_task = state.active_tasks[0]
        print(f"\n📋 First Task:")
        print(f"   Name: {first_task['name']}")
        print(f"   Activity ID: {first_task['activity_id']}")
        print(f"   AI Tip: {first_task['ai_tip']}")

    return instance_id, workflow


async def example_2_complete_task(instance_id, workflow):
    """
    Example 2: Complete task and progress workflow
    """
    print("\n\n=== Example 2: Complete Task ===\n")

    # Get current state
    state = await workflow.get_visual_state(instance_id)
    first_task = state.active_tasks[0]

    print(f"🎯 Completing task: {first_task['name']}")

    # Complete task with data
    await workflow.complete_task(
        task_id=first_task['id'],
        variables={
            "processes_identified": 12,
            "critical_processes": [
                "Emergency Department",
                "Patient Records",
                "Pharmacy",
                "Laboratory"
            ]
        },
        completed_by="user-john"
    )

    print(f"✅ Task completed!")

    # Get new state
    state = await workflow.get_visual_state(instance_id)

    print(f"\n📊 Updated State:")
    print(f"   Current Activities: {state.current_activities}")
    print(f"   Next Task: {state.active_tasks[0]['name'] if state.active_tasks else 'None'}")


async def example_3_assign_tasks():
    """
    Example 3: Assign tasks to users
    """
    print("\n\n=== Example 3: Task Assignment ===\n")

    workflow = UnifiedWorkflowEngine(
        tenant_id="acme-corp",
        module="bia"
    )

    # Start process
    instance_id = await workflow.start_process_from_bpmn(
        bpmn_xml=BIA_BPMN_XML,
        initial_variables={"org_id": "org-456"}
    )

    # Get first task
    state = await workflow.get_visual_state(instance_id)
    task_id = state.active_tasks[0]["id"]

    # Assign to user
    await workflow.bpmn_engine.assign_task(
        task_id=task_id,
        assignee="user-sarah"
    )

    print(f"✅ Task assigned to user-sarah")

    # Get user's tasks
    user_tasks = await workflow.get_active_tasks_for_user(
        assignee="user-sarah"
    )

    print(f"\n📋 Tasks for user-sarah:")
    for task in user_tasks:
        print(f"   - {task['name']} (Activity: {task['activity_id']})")


async def example_4_monitor_workflow():
    """
    Example 4: Monitor workflow progress
    """
    print("\n\n=== Example 4: Monitor Workflow ===\n")

    workflow = UnifiedWorkflowEngine(
        tenant_id="acme-corp",
        module="bia"
    )

    # Start process
    instance_id = await workflow.start_process_from_bpmn(
        bpmn_xml=BIA_BPMN_XML,
        initial_variables={"org_id": "org-456"}
    )

    # Complete multiple tasks
    for step_num in range(1, 4):
        state = await workflow.get_visual_state(instance_id)

        if not state.active_tasks:
            break

        task = state.active_tasks[0]

        print(f"📍 Step {step_num}: {task['name']}")
        print(f"   Activity: {task['activity_id']}")
        print(f"   AI Tip: {task['ai_tip']}")

        # Complete task
        await workflow.complete_task(
            task_id=task['id'],
            variables={f"step_{step_num}_completed": True}
        )

        print(f"   ✅ Completed\n")

    # Final state
    instance = await workflow.bpmn_engine.get_instance(instance_id)
    print(f"📊 Final Status: {instance.status.value}")


async def example_5_event_handling():
    """
    Example 5: Listen to workflow events
    """
    print("\n\n=== Example 5: Event Handling ===\n")

    workflow = UnifiedWorkflowEngine(
        tenant_id="acme-corp",
        module="bia"
    )

    # Register event handlers
    @workflow.bpmn_engine.on_event("bpmn.instance.started")
    async def on_started(event):
        print(f"🎬 Process started: {event['data']['instance_id']}")

    @workflow.bpmn_engine.on_event("bpmn.task.created")
    async def on_task_created(event):
        print(f"📋 Task created: {event['data']['name']}")

    @workflow.bpmn_engine.on_event("bpmn.task.completed")
    async def on_task_completed(event):
        print(f"✅ Task completed: {event['data']['task_id']}")

    # Start process - events will fire
    instance_id = await workflow.start_process_from_bpmn(
        bpmn_xml=BIA_BPMN_XML,
        initial_variables={"org_id": "org-456"}
    )

    # Complete first task - more events will fire
    state = await workflow.get_visual_state(instance_id)
    await workflow.complete_task(
        task_id=state.active_tasks[0]['id']
    )


async def example_6_terminate_workflow():
    """
    Example 6: Terminate workflow
    """
    print("\n\n=== Example 6: Terminate Workflow ===\n")

    workflow = UnifiedWorkflowEngine(
        tenant_id="acme-corp",
        module="bia"
    )

    # Start process
    instance_id = await workflow.start_process_from_bpmn(
        bpmn_xml=BIA_BPMN_XML,
        initial_variables={"org_id": "org-456"}
    )

    print(f"▶️  Process started: {instance_id}")

    # Terminate
    await workflow.terminate_process(
        workflow_id=instance_id,
        reason="User cancelled - starting fresh BIA instead"
    )

    # Check status
    instance = await workflow.bpmn_engine.get_instance(instance_id)
    print(f"🛑 Process terminated: {instance.status.value}")


async def main():
    """
    Run all examples
    """
    print("="*60)
    print("Unified Workflow Engine - Basic Usage Examples")
    print("="*60)

    # Example 1 & 2: Start and complete
    instance_id, workflow = await example_1_start_bia_process()
    await example_2_complete_task(instance_id, workflow)

    # Example 3: Task assignment
    await example_3_assign_tasks()

    # Example 4: Monitor progress
    await example_4_monitor_workflow()

    # Example 5: Events
    await example_5_event_handling()

    # Example 6: Terminate
    await example_6_terminate_workflow()

    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
