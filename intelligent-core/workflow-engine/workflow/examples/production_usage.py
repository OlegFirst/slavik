"""
Production Usage Example - UnifiedWorkflowEngine with PostgreSQL

Demonstrates complete integration:
- BPMN process deployment
- Instance creation and execution
- AI recommendations
- Visual state for UI
- Event synchronization
"""

import asyncio
import os
import sys
from datetime import datetime

# Add intelligent-core to Python path
INTELLIGENT_CORE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, INTELLIGENT_CORE_PATH)

# Set up database URL (from environment or .env)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    print("Please set it in .env file or export it")
    print("Example: export DATABASE_URL='postgresql://...'")
    exit(1)


async def main():
    """Complete workflow lifecycle with AI recommendations"""

    # Import UnifiedWorkflowEngine
    # Note: Import from unified_workflow (relative to intelligent-core/)
    from unified_workflow.core.unified_engine import UnifiedWorkflowEngine

    print("=" * 80)
    print("UNIFIED WORKFLOW ENGINE - Production Example")
    print("=" * 80)

    # ========== 1. Initialize Engine ==========

    print("\n[1] Initializing Unified Workflow Engine...")

    engine = await UnifiedWorkflowEngine.create(
        tenant_id="acme-healthcare",
        module="bia",
        database_url=DATABASE_URL,
        workflow_intelligence_enabled=True
    )

    print(f"✓ Engine initialized for tenant: acme-healthcare")
    print(f"✓ Module: BIA (Business Impact Analysis)")
    print(f"✓ Workflow Intelligence: ENABLED")

    # ========== 2. Deploy BPMN Process ==========

    print("\n[2] Deploying BPMN process...")

    # Sample BPMN XML (simple BIA workflow)
    bpmn_xml = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
             id="bia_process"
             targetNamespace="http://bpmn.io/schema/bpmn">
  <process id="Process_BIA_Assessment" name="BIA Assessment Process">
    <startEvent id="StartEvent_1" name="Start BIA"/>
    <sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_IdentifyProcesses"/>

    <userTask id="Task_IdentifyProcesses" name="Identify Critical Processes"/>
    <sequenceFlow id="Flow_2" sourceRef="Task_IdentifyProcesses" targetRef="Task_AnalyzeImpact"/>

    <userTask id="Task_AnalyzeImpact" name="Analyze Business Impact"/>
    <sequenceFlow id="Flow_3" sourceRef="Task_AnalyzeImpact" targetRef="Task_SetRTO"/>

    <userTask id="Task_SetRTO" name="Set RTO/RPO Targets"/>
    <sequenceFlow id="Flow_4" sourceRef="Task_SetRTO" targetRef="EndEvent_1"/>

    <endEvent id="EndEvent_1" name="BIA Complete"/>
  </process>
</definitions>"""

    instance_id = await engine.start_process_from_bpmn(
        bpmn_xml=bpmn_xml,
        process_name="BIA Assessment - Acme Healthcare",
        initial_variables={
            "org_context": {
                "industry": "healthcare",
                "size": "medium",
                "employees": 500,
                "maturity_level": "basic"
            },
            "requester": "John Smith",
            "department": "IT"
        },
        started_by="john.smith@acme.com",
        created_by="admin@acme.com",
        description="Complete BIA assessment for Acme Healthcare",
        version="1.0"
    )

    print(f"✓ BPMN process deployed and started")
    print(f"✓ Instance ID: {instance_id}")

    # ========== 3. Get Visual State (for UI) ==========

    print("\n[3] Getting visual state for UI...")

    visual_state = await engine.get_visual_state(instance_id)

    print(f"✓ Visual state retrieved")
    print(f"  - Type: {visual_state.type}")
    print(f"  - Current activities: {visual_state.current_activities}")
    print(f"  - Active tasks: {len(visual_state.active_tasks)}")
    print(f"  - Progress: {visual_state.workflow_context.get('progress_percentage', 0):.1f}%")

    # Show AI recommendations for first task
    if visual_state.active_tasks:
        first_task = visual_state.active_tasks[0]
        print(f"\n  First task: {first_task['name']}")
        print(f"  Task ID: {first_task['id']}")
        print(f"  AI Tip: {first_task.get('ai_tip', 'No tip')}")

        if first_task.get('ai_recommendations'):
            print(f"  AI Recommendations:")
            for rec in first_task['ai_recommendations']:
                print(f"    - [{rec.get('priority', 'medium').upper()}] {rec.get('message', '')}")

    # ========== 4. Assign and Complete First Task ==========

    print("\n[4] Working on first task...")

    if visual_state.active_tasks:
        first_task_id = visual_state.active_tasks[0]['id']

        # Assign task
        await engine.assign_task(
            task_id=first_task_id,
            assignee="john.smith@acme.com"
        )
        print(f"✓ Task assigned to: john.smith@acme.com")

        # Complete task with data
        await engine.complete_task(
            task_id=first_task_id,
            variables={
                "critical_processes": [
                    {"name": "Patient Care", "criticality": "high"},
                    {"name": "Laboratory Services", "criticality": "high"},
                    {"name": "Billing", "criticality": "medium"}
                ],
                "processes_identified_count": 3,
                "identified_at": datetime.utcnow().isoformat(),
                "identified_by": "john.smith@acme.com"
            },
            completed_by="john.smith@acme.com"
        )
        print(f"✓ Task completed")

    # ========== 5. Get Updated State ==========

    print("\n[5] Getting updated visual state...")

    updated_state = await engine.get_visual_state(instance_id)

    print(f"✓ Progress: {updated_state.workflow_context.get('progress_percentage', 0):.1f}%")
    print(f"✓ Active tasks: {len(updated_state.active_tasks)}")

    if updated_state.active_tasks:
        next_task = updated_state.active_tasks[0]
        print(f"✓ Next task: {next_task['name']}")
        print(f"  AI Tip: {next_task.get('ai_tip', 'No tip')}")

    # Show predictions
    if updated_state.predictions:
        print(f"\n  AI Predictions:")
        print(f"  - Estimated completion: {updated_state.predictions.get('estimated_completion_date', 'Unknown')}")
        print(f"  - Success probability: {updated_state.predictions.get('success_probability', 0) * 100:.1f}%")
        print(f"  - Risk level: {updated_state.predictions.get('risk_level', 'unknown').upper()}")

    # ========== 6. Get User's Task Inbox ==========

    print("\n[6] Getting user's task inbox...")

    user_tasks = await engine.get_active_tasks_for_user(
        assignee="john.smith@acme.com"
    )

    print(f"✓ User has {len(user_tasks)} active task(s)")
    for task in user_tasks:
        print(f"  - {task['name']} (Progress: {task.get('progress_percentage', 0):.1f}%)")

    # ========== 7. List All Instances ==========

    print("\n[7] Listing all process instances...")

    from unified_workflow.bpmn.models import ProcessStatus

    instances = await engine.list_instances(status=ProcessStatus.ACTIVE)
    print(f"✓ Found {len(instances)} active instance(s)")

    # ========== 8. Get Process Analytics ==========

    print("\n[8] Getting process analytics...")

    analytics = await engine.get_process_analytics()
    print(f"✓ Analytics:")
    print(f"  - Module: {analytics['module']}")
    print(f"  - Total instances: {analytics['total_instances']}")
    print(f"  - Active: {analytics['active_instances']}")
    print(f"  - Completed: {analytics['completed_instances']}")

    # ========== 9. Cleanup ==========

    print("\n[9] Cleaning up...")

    await engine.close()
    print(f"✓ Engine closed")

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETE")
    print("=" * 80)
    print("\nKey Features Demonstrated:")
    print("✓ BPMN process deployment with PostgreSQL persistence")
    print("✓ Instance creation with initial variables")
    print("✓ Visual state generation (for bpmn-js rendering)")
    print("✓ AI recommendations injection into tasks")
    print("✓ Task assignment and completion")
    print("✓ Progress tracking and predictions")
    print("✓ User task inbox")
    print("✓ Event synchronization (BPMN ↔ Workflow Intelligence)")
    print("\nNext Steps:")
    print("- Connect UI frontend (bpmn-js)")
    print("- Enable full Workflow Intelligence integration")
    print("- Integrate Case Library for self-learning")
    print("- Add ML predictor for outcome predictions")


if __name__ == "__main__":
    asyncio.run(main())
