"""
Control Workflow - Task Execution Monitoring
=============================================

Temporal wrapper for monitoring task execution completion.

Pattern: "Temporal as Wrapper"
- Lightweight orchestration only
- Real work done by coordination_center and orchestrators
- Simple retry policies
- Tracks task from start to completion

Integration:
- coordination_center_client (task tracking)
- workflow_intelligence_client (brain communication)
- EventBus (status updates)
"""

import logging
from datetime import timedelta
from typing import Dict, Any

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)

# Global instances (injected by worker)
_coordination_client = None
_brain_client = None


def inject_dependencies(coordination_client, brain_client):
    """Inject dependencies (called by Temporal worker)."""
    global _coordination_client, _brain_client
    _coordination_client = coordination_client
    _brain_client = brain_client
    logger.info(" Dependencies injected into Control workflow")


# ============================================================================
# ACTIVITIES - Wrappers around real control components
# ============================================================================

@activity.defn
async def check_task_status(task_id: str) -> Dict[str, Any]:
    """
    Check task execution status.

    Wrapper around coordination_center_client.
    """
    logger.info(f" Checking task status: {task_id}")

    try:
        # TODO: Real coordination_center_client implementation
        # status = await _coordination_client.get_task_status(task_id)

        # Placeholder
        status = {
            "task_id": task_id,
            "status": "in_progress",  # pending, in_progress, completed, failed
            "progress": 0.5,
            "started_at": "2025-10-07T12:00:00Z",
            "updated_at": "2025-10-07T12:05:00Z"
        }

        return {
            "status": "success",
            "task_status": status
        }

    except Exception as e:
        logger.error(f" Task status check failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def report_progress_to_brain(task_id: str, progress: Dict[str, Any]) -> bool:
    """
    Report task progress to brain.

    Wrapper around workflow_intelligence_client.
    """
    logger.info(f" Reporting progress to brain: {task_id} - {progress.get('progress', 0)*100}%")

    try:
        # TODO: Real workflow_intelligence_client implementation
        # await _brain_client.report_task_progress(task_id, progress)

        return True

    except Exception as e:
        logger.error(f" Progress reporting failed: {e}")
        return False


@activity.defn
async def handle_task_completion(task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle task completion.

    Wrapper around completion handlers.
    """
    logger.info(f" Handling task completion: {task_id}")

    try:
        success = result.get('status') == 'completed'

        # TODO: Real completion handling
        # - Update metrics
        # - Trigger follow-up actions
        # - Archive task data

        return {
            "status": "success",
            "task_completed": success,
            "result": result
        }

    except Exception as e:
        logger.error(f" Completion handling failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def handle_task_failure(task_id: str, error: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle task failure.

    Wrapper around failure handlers.
    """
    logger.error(f" Handling task failure: {task_id}")

    try:
        # TODO: Real failure handling
        # - Escalate to brain
        # - Trigger retry or rollback
        # - Alert stakeholders

        return {
            "status": "escalated",
            "task_id": task_id,
            "error": error
        }

    except Exception as e:
        logger.error(f" Failure handling failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


# ============================================================================
# WORKFLOW - Lightweight orchestration wrapper
# ============================================================================

@workflow.defn
class ControlWorkflow:
    """
    Control Workflow - Task execution monitoring wrapper.

    Simple orchestration:
    1. Monitor task status
    2. Report progress to brain
    3. Handle completion/failure
    4. Ensure full execution cycle

    SLA:
    - Check interval: 30s
    - Max monitoring time: 24h
    - Progress reporting: Every 5min

    Temporal provides: durability, long-running support, retry.
    """

    @workflow.run
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute control workflow.

        Args:
            config: {
                'task_id': 'TASK-001',
                'check_interval': 30,  # seconds
                'max_monitoring_time': 86400,  # 24h in seconds
                'report_interval': 300  # 5min in seconds
            }
        """
        task_id = config.get('task_id')
        workflow.logger.info(f" Starting Control Workflow for task: {task_id}")

        check_interval = config.get('check_interval', 30)
        max_time = config.get('max_monitoring_time', 86400)
        report_interval = config.get('report_interval', 300)

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3
        )

        start_time = workflow.now()
        last_report_time = start_time
        iteration = 0

        # Monitoring loop
        while True:
            iteration += 1
            elapsed = (workflow.now() - start_time).total_seconds()

            # Check timeout
            if elapsed > max_time:
                workflow.logger.error(f"⏰ Monitoring timeout after {elapsed}s")
                return {
                    "status": "timeout",
                    "task_id": task_id,
                    "monitoring_time": elapsed
                }

            workflow.logger.info(f" Control iteration {iteration} (elapsed: {elapsed}s)")

            try:
                # 1. Check task status
                status_result = await workflow.execute_activity(
                    check_task_status,
                    args=[task_id],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=retry_policy
                )

                if status_result['status'] != 'success':
                    workflow.logger.error(f"Status check failed: {status_result}")
                    await workflow.asyncio.sleep(check_interval)
                    continue

                task_status = status_result['task_status']
                current_status = task_status.get('status')

                # 2. Report progress to brain (every report_interval)
                if (workflow.now() - last_report_time).total_seconds() >= report_interval:
                    reported = await workflow.execute_activity(
                        report_progress_to_brain,
                        args=[task_id, task_status],
                        start_to_close_timeout=timedelta(seconds=10),
                        retry_policy=retry_policy
                    )

                    if reported:
                        last_report_time = workflow.now()
                        workflow.logger.info(f" Progress reported to brain")

                # 3. Handle completion
                if current_status == 'completed':
                    workflow.logger.info(f" Task completed: {task_id}")

                    completion_result = await workflow.execute_activity(
                        handle_task_completion,
                        args=[task_id, task_status],
                        start_to_close_timeout=timedelta(seconds=30),
                        retry_policy=retry_policy
                    )

                    return {
                        "status": "completed",
                        "task_id": task_id,
                        "monitoring_time": elapsed,
                        "result": completion_result
                    }

                # 4. Handle failure
                elif current_status == 'failed':
                    workflow.logger.error(f" Task failed: {task_id}")

                    failure_result = await workflow.execute_activity(
                        handle_task_failure,
                        args=[task_id, task_status],
                        start_to_close_timeout=timedelta(seconds=30),
                        retry_policy=retry_policy
                    )

                    return {
                        "status": "failed",
                        "task_id": task_id,
                        "monitoring_time": elapsed,
                        "result": failure_result
                    }

                # 5. Continue monitoring
                else:
                    workflow.logger.info(f"⏳ Task still {current_status}, continuing...")

            except Exception as e:
                workflow.logger.error(f" Control iteration failed: {e}")

            # Sleep until next check
            await workflow.asyncio.sleep(check_interval)


# Export for worker registration
control_activities = [
    check_task_status,
    report_progress_to_brain,
    handle_task_completion,
    handle_task_failure
]
