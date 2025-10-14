#!/usr/bin/env python3
"""
Coordination Workflow Examples
================================

Demonstrates how to use Coordination Center Temporal Workflows:
- CoordinationWorkflow (single intent)
- CrossServiceWorkflow (multi-service)
- ParallelTaskWorkflow (bulk operations)
"""

import asyncio
from temporalio.client import Client
from datetime import timedelta

# Import workflows
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from intelligent_core.workflow_intelligence.temporal_workflows.coordination_workflow import (
    CoordinationWorkflow,
    CrossServiceWorkflow,
    ParallelTaskWorkflow,
    inject_dependencies
)


async def example_single_intent():
    """
    Example 1: Single Intent Execution

    Use case: AI triggers BIA creation
    """
    print("\n" + "="*60)
    print("Example 1: Single Intent Execution (BIA Creation)")
    print("="*60)

    # Connect to Temporal
    client = await Client.connect("localhost:7233", namespace="default")

    # Inject dependencies
    inject_dependencies(coordination_center_url="http://localhost:8004")

    # Define intent
    intent = {
        "action": "create",
        "entity": "bia_process",
        "params": {
            "organization_id": 123,
            "process_name": "IT Infrastructure",
            "scope": "IT",
            "description": "Critical IT systems and infrastructure"
        },
        "context": {
            "tenant_id": "tenant-001",
            "user_id": "ai_agent",
            "session_id": "session-001"
        },
        "require_approval": False
    }

    print(f"\n📤 Submitting intent: {intent['action']} {intent['entity']}")

    # Execute workflow
    try:
        result = await client.execute_workflow(
            CoordinationWorkflow.run,
            intent,
            id=f"coordination-single-{asyncio.get_running_loop().time()}",
            task_queue="coordination-queue",
            execution_timeout=timedelta(minutes=15)
        )

        print(f"\n✅ Workflow completed!")
        print(f"   Status: {result['status']}")
        print(f"   Execution ID: {result['execution_id']}")
        print(f"   Steps: {len(result['steps'])}")

        if result.get('result'):
            print(f"   Result: {result['result']}")

    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")


async def example_multi_service():
    """
    Example 2: Multi-Service Coordination

    Use case: Parallel execution of BIA + Risk + Compliance
    """
    print("\n" + "="*60)
    print("Example 2: Multi-Service Coordination (Parallel Analysis)")
    print("="*60)

    client = await Client.connect("localhost:7233", namespace="default")
    inject_dependencies(coordination_center_url="http://localhost:8004")

    # Define multiple tasks
    tasks = [
        {
            "task_id": "task-1",
            "action": "create",
            "entity": "bia_process",
            "params": {
                "organization_id": 123,
                "process_name": "IT Infrastructure",
                "scope": "IT"
            },
            "context": {
                "tenant_id": "tenant-001",
                "user_id": "ai_agent"
            }
        },
        {
            "task_id": "task-2",
            "action": "assess",
            "entity": "risk",
            "params": {
                "organization_id": 123,
                "domain": "IT",
                "assessment_type": "comprehensive"
            },
            "context": {
                "tenant_id": "tenant-001",
                "user_id": "ai_agent"
            }
        },
        {
            "task_id": "task-3",
            "action": "check",
            "entity": "compliance",
            "params": {
                "organization_id": 123,
                "standard": "ISO_22301",
                "scope": "IT"
            },
            "context": {
                "tenant_id": "tenant-001",
                "user_id": "ai_agent"
            }
        }
    ]

    print(f"\n📤 Submitting {len(tasks)} tasks for parallel execution")

    try:
        result = await client.execute_workflow(
            CrossServiceWorkflow.run,
            tasks,
            id=f"coordination-multi-{asyncio.get_running_loop().time()}",
            task_queue="coordination-queue",
            execution_timeout=timedelta(minutes=30)
        )

        print(f"\n✅ Multi-service workflow completed!")
        print(f"   Status: {result['status']}")
        print(f"   Total tasks: {result['total_tasks']}")

        agg = result.get('status_aggregation', {})
        print(f"   Completed: {agg.get('completed', 0)}/{agg.get('total', 0)}")
        print(f"   Failed: {agg.get('failed', 0)}")
        print(f"   Execution IDs: {result.get('execution_ids', [])}")

    except Exception as e:
        print(f"\n❌ Multi-service workflow failed: {str(e)}")


async def example_parallel_bulk():
    """
    Example 3: Parallel Bulk Operations

    Use case: Create multiple BIA processes in parallel
    """
    print("\n" + "="*60)
    print("Example 3: Parallel Bulk Operations (Bulk BIA Creation)")
    print("="*60)

    client = await Client.connect("localhost:7233", namespace="default")
    inject_dependencies(coordination_center_url="http://localhost:8004")

    # Define bulk tasks
    processes = ["Finance", "HR", "Operations", "Marketing", "Sales"]

    tasks = [
        {
            "action": "create",
            "entity": "bia_process",
            "params": {
                "organization_id": 123,
                "process_name": process,
                "scope": process
            },
            "context": {
                "tenant_id": "tenant-001",
                "user_id": "ai_agent"
            }
        }
        for process in processes
    ]

    print(f"\n📤 Creating {len(tasks)} BIA processes in parallel")

    try:
        result = await client.execute_workflow(
            ParallelTaskWorkflow.run,
            tasks,
            False,  # Continue on error
            id=f"coordination-parallel-{asyncio.get_running_loop().time()}",
            task_queue="coordination-queue",
            execution_timeout=timedelta(minutes=20)
        )

        print(f"\n✅ Parallel workflow completed!")
        print(f"   Status: {result['status']}")
        print(f"   Total tasks: {result['total_tasks']}")
        print(f"   Successful: {result['successful']}")
        print(f"   Failed: {result['failed']}")

        print(f"\n   Results:")
        for i, r in enumerate(result.get('results', []), 1):
            status_icon = "✅" if r['status'] == 'completed' else "❌"
            print(f"   {i}. {status_icon} {r['execution_id']} - {r['status']}")

    except Exception as e:
        print(f"\n❌ Parallel workflow failed: {str(e)}")


async def example_with_approval():
    """
    Example 4: Intent with Human Approval

    Use case: Critical operation requiring approval
    """
    print("\n" + "="*60)
    print("Example 4: Intent with Human Approval")
    print("="*60)

    client = await Client.connect("localhost:7233", namespace="default")
    inject_dependencies(coordination_center_url="http://localhost:8004")

    # Define critical intent requiring approval
    intent = {
        "action": "delete",
        "entity": "bia_process",
        "params": {
            "process_id": "bia-123",
            "reason": "Obsolete process"
        },
        "context": {
            "tenant_id": "tenant-001",
            "user_id": "ai_agent"
        },
        "require_approval": True  # Requires human approval
    }

    print(f"\n📤 Submitting critical intent (requires approval)")
    print(f"   Action: {intent['action']} {intent['entity']}")

    try:
        # Note: This will wait for approval (up to 24h)
        # In real system, approval would come from human via UI
        result = await client.execute_workflow(
            CoordinationWorkflow.run,
            intent,
            id=f"coordination-approval-{asyncio.get_running_loop().time()}",
            task_queue="coordination-queue",
            execution_timeout=timedelta(hours=24)  # Long timeout for approval
        )

        print(f"\n✅ Workflow completed after approval!")
        print(f"   Status: {result['status']}")
        print(f"   Execution ID: {result['execution_id']}")

    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")


async def example_query_status():
    """
    Example 5: Query Workflow Status

    Use case: Check status of running workflow
    """
    print("\n" + "="*60)
    print("Example 5: Query Workflow Status")
    print("="*60)

    client = await Client.connect("localhost:7233", namespace="default")

    workflow_id = "coordination-single-12345"  # Replace with actual ID

    print(f"\n🔍 Querying workflow status: {workflow_id}")

    try:
        handle = client.get_workflow_handle(workflow_id)

        # Get workflow status
        description = await handle.describe()

        print(f"\n   Status: {description.status}")
        print(f"   Execution time: {description.execution_time}")
        print(f"   Task queue: {description.task_queue}")

    except Exception as e:
        print(f"\n❌ Query failed: {str(e)}")


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("COORDINATION CENTER TEMPORAL WORKFLOWS - EXAMPLES")
    print("="*60)
    print("\nPrerequisites:")
    print("1. Temporal server running (localhost:7233)")
    print("2. Coordination Center running (localhost:8004)")
    print("3. Temporal worker running (coordination-queue)")
    print("\nStarting examples...\n")

    # Run examples
    await example_single_intent()
    await asyncio.sleep(2)

    await example_multi_service()
    await asyncio.sleep(2)

    await example_parallel_bulk()
    await asyncio.sleep(2)

    # Note: Approval example commented out (requires manual approval)
    # await example_with_approval()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
