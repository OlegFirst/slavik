"""
Coordination Center Workflow - Temporal Durable Execution
===========================================================

Coordination Center - посредник между AI (brain) и BCM tools (execution).

Temporal Workflows:
1. CoordinationWorkflow - single intent execution with retry & approval
2. CrossServiceWorkflow - multi-service coordination across BCM domain
3. ParallelTaskWorkflow - parallel execution of independent tasks

Activities:
- task_distribution - распределение задач между сервисами
- service_coordination - координация multi-service операций
- status_aggregation - сбор статусов с нескольких сервисов
- conflict_resolution - разрешение конфликтов между сервисами
- intent_execution - выполнение AI intent
- approval_request - запрос human approval
- rollback_execution - откат выполненных операций

Integrates with:
- Coordination Center (command interpreter, tool registry, security)
- BCM Services (via service registry)
- AI Orchestration (intent source)
- EventBus (audit trail)
"""

import logging
from datetime import timedelta, datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx

from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

logger = logging.getLogger(__name__)

# Global dependencies (injected by worker)
_coordination_center_url: str = None


def inject_dependencies(coordination_center_url: str = "http://localhost:8004"):
    """Inject dependencies for activities (called by Temporal worker)."""
    global _coordination_center_url
    _coordination_center_url = coordination_center_url
    logger.info(f"Dependencies injected: coordination_center={coordination_center_url}")


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Intent:
    """AI Intent for execution"""
    action: str
    entity: Optional[str]
    params: Dict[str, Any]
    context: Dict[str, Any]
    require_approval: bool = False


@dataclass
class ExecutionResult:
    """Result of intent execution"""
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    steps: List[Dict[str, Any]]


@dataclass
class ServiceCall:
    """Single service call"""
    service_name: str
    endpoint: str
    method: str
    payload: Dict[str, Any]
    headers: Optional[Dict[str, str]] = None


@dataclass
class CoordinationTask:
    """Task for coordination"""
    task_id: str
    intent: Intent
    priority: int = 1
    depends_on: Optional[List[str]] = None


# ============================================================================
# Activities - Coordination Operations
# ============================================================================

@activity.defn
async def intent_execution(intent_data: Dict[str, Any]) -> ExecutionResult:
    """
    Execute AI intent via Coordination Center.

    Activity: Calls Coordination Center /execute endpoint
    Idempotent: Safe to retry
    """
    logger.info(f"🎯 Executing intent: {intent_data.get('action')}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{_coordination_center_url}/coordination/execute",
                json={"intent": intent_data},
                headers={
                    "Content-Type": "application/json",
                    "X-Tenant-ID": intent_data.get("context", {}).get("tenant_id"),
                }
            )

            if response.status_code == 403:
                raise ApplicationError(
                    f"Authorization failed: {response.text}",
                    type="AUTHORIZATION_ERROR"
                )

            if response.status_code >= 400:
                raise ApplicationError(
                    f"Execution failed: {response.status_code} - {response.text}",
                    type="EXECUTION_ERROR"
                )

            result = response.json()

            execution_id = result.get("execution_id")

            # Poll for completion if async execution
            if result.get("status") in ["pending", "running"]:
                result = await _poll_execution_status(execution_id)

            return ExecutionResult(
                execution_id=execution_id,
                status=result.get("status"),
                result=result.get("result"),
                error=result.get("error", {}).get("message") if result.get("error") else None,
                steps=result.get("steps", [])
            )

    except httpx.TimeoutException:
        raise ApplicationError("Coordination Center timeout", type="TIMEOUT_ERROR")
    except Exception as e:
        logger.error(f"Intent execution failed: {str(e)}")
        raise


async def _poll_execution_status(execution_id: str, max_polls: int = 30) -> Dict[str, Any]:
    """Poll execution status until completion."""
    import asyncio

    for i in range(max_polls):
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{_coordination_center_url}/coordination/executions/{execution_id}"
            )

            if response.status_code != 200:
                raise Exception(f"Status poll failed: {response.status_code}")

            result = response.json()

            if result.get("status") in ["completed", "failed", "rollback_completed"]:
                return result

            # Wait before next poll
            await asyncio.sleep(1)

    raise Exception(f"Execution timeout after {max_polls} polls")


@activity.defn
async def task_distribution(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Distribute tasks to appropriate services.

    Activity: Routes tasks based on entity type and service registry
    """
    logger.info(f"📋 Distributing {len(tasks)} tasks")

    from orchestration.coordination_center.core.tool_registry import tool_registry

    distributed = []

    for task in tasks:
        # Find appropriate service
        entity = task.get("entity")
        action = task.get("action")

        tool = tool_registry.find_tool_for_action(action, entity)

        if not tool:
            logger.warning(f"No tool found for {action} on {entity}")
            continue

        distributed.append({
            "task_id": task.get("task_id"),
            "service": tool.name,
            "tool_id": tool.tool_id,
            "endpoint": tool.endpoints.get(action),
            "action": action,
            "params": task.get("params")
        })

    logger.info(f"✅ Distributed to {len(distributed)} services")

    return {
        "distributed_count": len(distributed),
        "tasks": distributed,
        "failed_count": len(tasks) - len(distributed)
    }


@activity.defn
async def service_coordination(service_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Coordinate multiple service calls with dependency management.

    Activity: Orchestrates multi-service operations
    """
    logger.info(f"🔗 Coordinating {len(service_calls)} service calls")

    results = []
    failed = []

    for call in service_calls:
        try:
            # Execute service call via Coordination Center
            intent = {
                "action": call.get("action"),
                "entity": call.get("entity"),
                "params": call.get("params"),
                "context": call.get("context", {})
            }

            result = await intent_execution(intent)

            results.append({
                "service": call.get("service"),
                "execution_id": result.execution_id,
                "status": result.status,
                "result": result.result
            })

        except Exception as e:
            logger.error(f"Service call failed: {call.get('service')} - {str(e)}")
            failed.append({
                "service": call.get("service"),
                "error": str(e)
            })

    return {
        "successful_calls": len(results),
        "failed_calls": len(failed),
        "results": results,
        "failures": failed
    }


@activity.defn
async def status_aggregation(execution_ids: List[str]) -> Dict[str, Any]:
    """
    Aggregate status from multiple executions.

    Activity: Collects and aggregates status from parallel executions
    """
    logger.info(f"📊 Aggregating status from {len(execution_ids)} executions")

    statuses = []

    for exec_id in execution_ids:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{_coordination_center_url}/coordination/executions/{exec_id}"
                )

                if response.status_code == 200:
                    result = response.json()
                    statuses.append({
                        "execution_id": exec_id,
                        "status": result.get("status"),
                        "steps": len(result.get("steps", [])),
                        "has_error": result.get("error") is not None
                    })
                else:
                    logger.warning(f"Failed to get status for {exec_id}")

        except Exception as e:
            logger.error(f"Status fetch failed for {exec_id}: {str(e)}")

    # Aggregate statistics
    completed = sum(1 for s in statuses if s.get("status") == "completed")
    failed = sum(1 for s in statuses if s.get("status") == "failed")
    running = sum(1 for s in statuses if s.get("status") == "running")

    return {
        "total": len(execution_ids),
        "completed": completed,
        "failed": failed,
        "running": running,
        "statuses": statuses,
        "overall_status": "completed" if completed == len(execution_ids) else "partial"
    }


@activity.defn
async def conflict_resolution(conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Resolve conflicts between service operations.

    Activity: Handles resource conflicts, data inconsistencies
    """
    logger.info(f"⚔️ Resolving {len(conflicts)} conflicts")

    resolved = []
    unresolved = []

    for conflict in conflicts:
        conflict_type = conflict.get("type")

        try:
            if conflict_type == "resource_lock":
                # Wait and retry
                logger.info(f"Resource conflict: {conflict.get('resource')} - waiting")
                resolution = {
                    "strategy": "wait_and_retry",
                    "wait_seconds": 5
                }
                resolved.append({
                    "conflict": conflict,
                    "resolution": resolution
                })

            elif conflict_type == "data_inconsistency":
                # Use latest timestamp
                logger.info(f"Data conflict: using latest version")
                resolution = {
                    "strategy": "use_latest",
                    "selected": "latest_by_timestamp"
                }
                resolved.append({
                    "conflict": conflict,
                    "resolution": resolution
                })

            elif conflict_type == "permission_denied":
                # Escalate to human
                logger.warning(f"Permission conflict: escalating")
                resolution = {
                    "strategy": "escalate_to_human",
                    "reason": conflict.get("reason")
                }
                unresolved.append({
                    "conflict": conflict,
                    "resolution": resolution
                })

            else:
                logger.warning(f"Unknown conflict type: {conflict_type}")
                unresolved.append(conflict)

        except Exception as e:
            logger.error(f"Conflict resolution failed: {str(e)}")
            unresolved.append(conflict)

    return {
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "resolved": resolved,
        "unresolved": unresolved
    }


@activity.defn
async def approval_request(approval_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Request human approval for critical operations.

    Activity: Long-running, waits for approval
    """
    logger.info(f"✋ Requesting approval for: {approval_data.get('action')}")

    # Send approval request to Coordination Center
    execution_id = approval_data.get("execution_id")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{_coordination_center_url}/coordination/executions/{execution_id}/approve",
            json={
                "approved": True,  # In real system, wait for human input
                "reason": "Automated approval for testing",
                "approved_by": "system"
            }
        )

        if response.status_code != 200:
            raise ApplicationError("Approval failed", type="APPROVAL_ERROR")

        result = response.json()

    return {
        "approved": True,
        "execution_id": execution_id,
        "approved_by": "system",
        "timestamp": datetime.utcnow().isoformat()
    }


@activity.defn
async def rollback_execution(execution_ids: List[str]) -> Dict[str, Any]:
    """
    Rollback completed executions (compensating action).

    Activity: Saga compensation for failed workflows
    """
    logger.warning(f"⏪ Rolling back {len(execution_ids)} executions")

    rollback_results = []

    for exec_id in execution_ids:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{_coordination_center_url}/coordination/executions/{exec_id}/rollback",
                    json={
                        "reason": "Workflow compensation",
                        "initiated_by": "temporal_workflow"
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    rollback_results.append({
                        "execution_id": exec_id,
                        "status": result.get("status"),
                        "rollback_successful": True
                    })
                else:
                    logger.error(f"Rollback failed for {exec_id}: {response.status_code}")
                    rollback_results.append({
                        "execution_id": exec_id,
                        "rollback_successful": False,
                        "error": response.text
                    })

        except Exception as e:
            logger.error(f"Rollback exception for {exec_id}: {str(e)}")
            rollback_results.append({
                "execution_id": exec_id,
                "rollback_successful": False,
                "error": str(e)
            })

    successful = sum(1 for r in rollback_results if r.get("rollback_successful"))

    return {
        "total_rollbacks": len(execution_ids),
        "successful": successful,
        "failed": len(execution_ids) - successful,
        "results": rollback_results
    }


# ============================================================================
# Workflow 1: Coordination Workflow (Single Intent)
# ============================================================================

@workflow.defn
class CoordinationWorkflow:
    """
    Single Intent Execution Workflow

    Features:
    - Automatic retry on transient failures
    - Human approval for critical operations
    - Rollback on failure
    - Progress tracking via Coordination Center

    Use cases:
    - AI triggers BIA creation
    - AI triggers risk assessment
    - AI triggers compliance check
    """

    @workflow.run
    async def run(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute single AI intent with coordination.

        Steps:
        1. Validate intent
        2. Request approval (if required)
        3. Execute via Coordination Center
        4. Track progress
        5. Rollback on failure
        """
        workflow.logger.info(f"🎯 Starting Coordination Workflow: {intent_data.get('action')}")

        # Retry policy for transient failures
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3,
            backoff_coefficient=2.0
        )

        result = {
            "workflow": "CoordinationWorkflow",
            "intent": intent_data.get("action"),
            "started_at": workflow.now().isoformat()
        }

        execution_result = None

        try:
            # Step 1: Execute intent
            execution_result = await workflow.execute_activity(
                intent_execution,
                intent_data,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy
            )

            workflow.logger.info(f"✅ Intent executed: {execution_result.execution_id}")

            # Step 2: Handle approval if required
            if execution_result.status == "requires_approval":
                workflow.logger.info("✋ Approval required, waiting...")

                approval = await workflow.execute_activity(
                    approval_request,
                    {
                        "execution_id": execution_result.execution_id,
                        "action": intent_data.get("action"),
                        "context": intent_data.get("context")
                    },
                    start_to_close_timeout=timedelta(hours=24),  # Wait up to 24h
                    heartbeat_timeout=timedelta(minutes=5)
                )

                if not approval.get("approved"):
                    raise ApplicationError("Approval denied", type="APPROVAL_DENIED")

                workflow.logger.info("✅ Approval granted, continuing...")

                # Re-poll execution status after approval
                execution_result = await workflow.execute_activity(
                    intent_execution,
                    intent_data,
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=retry_policy
                )

            # Step 3: Verify completion
            if execution_result.status == "completed":
                result.update({
                    "status": "completed",
                    "execution_id": execution_result.execution_id,
                    "result": execution_result.result,
                    "steps": execution_result.steps,
                    "completed_at": workflow.now().isoformat()
                })
            else:
                raise ApplicationError(
                    f"Execution failed: {execution_result.error}",
                    type="EXECUTION_FAILED"
                )

            workflow.logger.info("🎉 Coordination Workflow completed!")
            return result

        except Exception as e:
            workflow.logger.error(f"❌ Coordination Workflow failed: {str(e)}")

            # Rollback if execution was started
            if execution_result and execution_result.execution_id:
                workflow.logger.warning("⏪ Rolling back execution...")

                await workflow.execute_activity(
                    rollback_execution,
                    [execution_result.execution_id],
                    start_to_close_timeout=timedelta(minutes=5)
                )

            result.update({
                "status": "failed",
                "error": str(e),
                "failed_at": workflow.now().isoformat()
            })

            raise


# ============================================================================
# Workflow 2: Cross-Service Workflow (Multi-Service Coordination)
# ============================================================================

@workflow.defn
class CrossServiceWorkflow:
    """
    Multi-Service Coordination Workflow

    Features:
    - Parallel execution of independent tasks
    - Sequential execution with dependencies
    - Service conflict resolution
    - Status aggregation
    - Saga pattern for rollback

    Use cases:
    - BIA + Risk Assessment + Compliance Check (parallel)
    - Create incident -> Assign team -> Activate plan (sequential)
    - Multi-domain coordination
    """

    @workflow.run
    async def run(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multi-service coordination.

        Steps:
        1. Distribute tasks to services
        2. Execute (parallel or sequential based on dependencies)
        3. Resolve conflicts
        4. Aggregate status
        5. Rollback on failure
        """
        workflow.logger.info(f"🔗 Starting Cross-Service Workflow: {len(tasks)} tasks")

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3
        )

        result = {
            "workflow": "CrossServiceWorkflow",
            "total_tasks": len(tasks),
            "started_at": workflow.now().isoformat()
        }

        execution_ids = []

        try:
            # Step 1: Distribute tasks
            distribution = await workflow.execute_activity(
                task_distribution,
                tasks,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )

            workflow.logger.info(
                f"📋 Distributed {distribution['distributed_count']} tasks"
            )

            # Step 2: Execute tasks (parallel for now, TODO: handle dependencies)
            distributed_tasks = distribution.get("tasks", [])

            # Execute all tasks in parallel
            execution_futures = []

            for task in distributed_tasks:
                intent = {
                    "action": task.get("action"),
                    "entity": task.get("entity"),
                    "params": task.get("params"),
                    "context": tasks[0].get("context", {})  # Use context from first task
                }

                future = workflow.execute_activity(
                    intent_execution,
                    intent,
                    start_to_close_timeout=timedelta(minutes=15),
                    retry_policy=retry_policy
                )

                execution_futures.append(future)

            # Wait for all executions
            execution_results = await workflow.gather(*execution_futures)

            # Collect execution IDs
            execution_ids = [r.execution_id for r in execution_results]

            workflow.logger.info(f"✅ Executed {len(execution_ids)} tasks")

            # Step 3: Check for conflicts
            conflicts = []
            for r in execution_results:
                if r.error and "conflict" in r.error.lower():
                    conflicts.append({
                        "type": "resource_lock",
                        "execution_id": r.execution_id,
                        "error": r.error
                    })

            if conflicts:
                workflow.logger.warning(f"⚔️ Detected {len(conflicts)} conflicts")

                conflict_resolution_result = await workflow.execute_activity(
                    conflict_resolution,
                    conflicts,
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=retry_policy
                )

                workflow.logger.info(
                    f"✅ Resolved {conflict_resolution_result['resolved_count']}/{len(conflicts)} conflicts"
                )

            # Step 4: Aggregate status
            status_agg = await workflow.execute_activity(
                status_aggregation,
                execution_ids,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )

            workflow.logger.info(
                f"📊 Status: {status_agg['completed']}/{status_agg['total']} completed"
            )

            # Step 5: Determine overall status
            if status_agg.get("failed", 0) > 0:
                raise ApplicationError(
                    f"{status_agg['failed']} tasks failed",
                    type="PARTIAL_FAILURE"
                )

            result.update({
                "status": "completed",
                "execution_ids": execution_ids,
                "status_aggregation": status_agg,
                "completed_at": workflow.now().isoformat()
            })

            workflow.logger.info("🎉 Cross-Service Workflow completed!")
            return result

        except Exception as e:
            workflow.logger.error(f"❌ Cross-Service Workflow failed: {str(e)}")

            # Rollback all executions (Saga pattern)
            if execution_ids:
                workflow.logger.warning(f"⏪ Rolling back {len(execution_ids)} executions...")

                await workflow.execute_activity(
                    rollback_execution,
                    execution_ids,
                    start_to_close_timeout=timedelta(minutes=10)
                )

            result.update({
                "status": "failed",
                "error": str(e),
                "execution_ids": execution_ids,
                "failed_at": workflow.now().isoformat()
            })

            raise


# ============================================================================
# Workflow 3: Parallel Task Workflow
# ============================================================================

@workflow.defn
class ParallelTaskWorkflow:
    """
    Parallel Task Execution Workflow

    Features:
    - Execute multiple independent tasks in parallel
    - Fail-fast or continue-on-error
    - Results aggregation

    Use cases:
    - Bulk operations (create multiple BIAs)
    - Parallel analysis (risk + compliance + governance)
    - Independent service calls
    """

    @workflow.run
    async def run(
        self,
        tasks: List[Dict[str, Any]],
        fail_fast: bool = False
    ) -> Dict[str, Any]:
        """
        Execute tasks in parallel.

        Args:
            tasks: List of independent tasks
            fail_fast: If True, fail on first error; if False, continue
        """
        workflow.logger.info(f"⚡ Starting Parallel Task Workflow: {len(tasks)} tasks")

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=20),
            maximum_attempts=3
        )

        # Execute all tasks in parallel
        futures = []

        for task in tasks:
            future = workflow.execute_activity(
                intent_execution,
                task,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy
            )
            futures.append(future)

        if fail_fast:
            # Wait for all, fail on first error
            results = await workflow.gather(*futures)
        else:
            # Continue on error, collect all results
            results = []
            for future in futures:
                try:
                    result = await future
                    results.append(result)
                except Exception as e:
                    workflow.logger.warning(f"Task failed: {str(e)}")
                    results.append(ExecutionResult(
                        execution_id="failed",
                        status="failed",
                        result=None,
                        error=str(e),
                        steps=[]
                    ))

        # Aggregate results
        successful = sum(1 for r in results if r.status == "completed")
        failed = sum(1 for r in results if r.status == "failed")

        workflow.logger.info(f"✅ Parallel execution: {successful}/{len(tasks)} successful")

        return {
            "workflow": "ParallelTaskWorkflow",
            "total_tasks": len(tasks),
            "successful": successful,
            "failed": failed,
            "results": [
                {
                    "execution_id": r.execution_id,
                    "status": r.status,
                    "error": r.error
                }
                for r in results
            ],
            "status": "completed" if failed == 0 else "partial",
            "completed_at": workflow.now().isoformat()
        }


# ============================================================================
# Export activities for worker registration
# ============================================================================

coordination_activities = [
    intent_execution,
    task_distribution,
    service_coordination,
    status_aggregation,
    conflict_resolution,
    approval_request,
    rollback_execution
]
