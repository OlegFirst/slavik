"""
Observation Workflow - Continuous Platform Monitoring
======================================================

Temporal wrapper for continuous observation of all platform layers.

Pattern: "Temporal as Wrapper"
- Lightweight orchestration only
- Real work done by integrations (Automation Toolkit, Prometheus)
- Simple retry policies
- Durable execution (survives restarts)

Integration:
- AutomationToolkitManager (service discovery, metrics)
- Prometheus (metrics export)
- EventBus (problem events)
"""

import logging
from datetime import timedelta
from typing import Dict, Any, List

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)

# Global instances (injected by worker)
_toolkit_manager = None


def inject_dependencies(toolkit_manager):
    """Inject dependencies (called by Temporal worker)."""
    global _toolkit_manager
    _toolkit_manager = toolkit_manager
    logger.info("✅ Dependencies injected into Observation workflow")


# ============================================================================
# ACTIVITIES - Wrappers around real integrations
# ============================================================================

@activity.defn
async def observe_all_layers() -> Dict[str, Any]:
    """
    Observe all platform layers.

    Wrapper around AutomationToolkitManager.discover_services()
    """
    logger.info("📊 Observing all layers")

    try:
        # Real work: AutomationToolkitManager does service discovery
        result = await _toolkit_manager.discover_services()

        return {
            "status": "success",
            "total_services": result.get('total_services', 0),
            "monitored": result.get('coverage', {}).get('monitored', 0),
            "coverage_pct": result.get('coverage', {}).get('percentage', 0),
            "services": result.get('services', [])
        }

    except Exception as e:
        logger.error(f"❌ Observation failed: {e}")
        return {"status": "failed", "error": str(e)}


@activity.defn
async def detect_problems_from_observation(observation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect problems from observation data.

    Simple rule-based detection (complex logic in ReactionRulesEngine).
    """
    logger.info("🔍 Detecting problems")

    problems = []

    try:
        # Low coverage problem
        coverage_pct = observation.get('coverage_pct', 100)
        if coverage_pct < 80.0:
            problems.append({
                "type": "low_coverage",
                "severity": "medium",
                "data": observation
            })

        # Service down problem
        services = observation.get('services', [])
        down_services = [s for s in services if s.get('status') == 'down']
        if down_services:
            problems.append({
                "type": "service_down",
                "severity": "high",
                "data": {"services": down_services}
            })

        return problems

    except Exception as e:
        logger.error(f"❌ Problem detection failed: {e}")
        return []


@activity.defn
async def publish_problems_to_eventbus(problems: List[Dict[str, Any]]) -> int:
    """
    Publish problems to EventBus.

    Triggers ReactionWorkflow for each problem.
    """
    logger.info(f"📢 Publishing {len(problems)} problems")

    try:
        # Real EventBus integration
        from integrations.eventbus_client import get_eventbus_client

        eventbus = await get_eventbus_client()

        published = 0
        for problem in problems:
            success = await eventbus.publish_problem_detected(
                problem=problem,
                severity=problem.get('severity', 'medium'),
                source='observation-workflow'
            )
            if success:
                published += 1

        logger.info(f"✅ Published {published}/{len(problems)} problems to EventBus")
        return published

    except Exception as e:
        logger.error(f"❌ Publishing failed: {e}")
        return 0


# ============================================================================
# WORKFLOW - Lightweight orchestration wrapper
# ============================================================================

@workflow.defn
class ObservationWorkflow:
    """
    Observation Workflow - Continuous monitoring wrapper.

    Simple orchestration:
    1. Observe (via Automation Toolkit)
    2. Detect problems
    3. Publish to EventBus
    4. Sleep and repeat

    Temporal provides: durability, retries, restart recovery.
    """

    @workflow.run
    async def run(self, config: dict) -> None:
        """
        Run continuous observation.

        Args:
            config: {'interval_seconds': 30}
        """
        workflow.logger.info("🚀 Starting Observation Workflow")

        interval = config.get('interval_seconds', 30)

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=3
        )

        iteration = 0

        # Infinite loop (long-running workflow)
        while True:
            iteration += 1
            workflow.logger.info(f"📊 Observation iteration {iteration}")

            try:
                # 1. Observe
                observation = await workflow.execute_activity(
                    observe_all_layers,
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=retry_policy
                )

                if observation['status'] != 'success':
                    workflow.logger.error(f"Observation failed: {observation}")
                    await workflow.asyncio.sleep(interval)
                    continue

                # 2. Detect problems
                problems = await workflow.execute_activity(
                    detect_problems_from_observation,
                    args=[observation],
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=retry_policy
                )

                # 3. Publish problems
                if problems:
                    published = await workflow.execute_activity(
                        publish_problems_to_eventbus,
                        args=[problems],
                        start_to_close_timeout=timedelta(seconds=10),
                        retry_policy=retry_policy
                    )
                    workflow.logger.info(f"✅ Published {published} problems")

            except Exception as e:
                workflow.logger.error(f"❌ Iteration {iteration} failed: {e}")

            # Sleep until next observation
            await workflow.asyncio.sleep(interval)


# Export for worker registration
observation_activities = [
    observe_all_layers,
    detect_problems_from_observation,
    publish_problems_to_eventbus
]
