"""
Reaction Workflow - Automated Response to Problems
===================================================

Temporal wrapper for automated problem response.

Pattern: "Temporal as Wrapper"
- Lightweight orchestration only
- Real work done by ReactionRulesEngine, ActionExecutor, EscalationManager
- Simple retry policies
- Three reaction levels: L1 (instant), L2 (quick), L3 (escalate to brain)

Integration:
- ReactionRulesEngine (problem classification)
- ActionExecutor (execute automated actions)
- EscalationManager (escalate to workflow_intelligence)
- workflow_intelligence_client (brain communication)
"""

import logging
from datetime import timedelta
from typing import Dict, Any

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)

# Global instances (injected by worker)
_rules_engine = None
_action_executor = None
_escalation_manager = None


def inject_dependencies(rules_engine, action_executor, escalation_manager):
    """Inject dependencies (called by Temporal worker)."""
    global _rules_engine, _action_executor, _escalation_manager
    _rules_engine = rules_engine
    _action_executor = action_executor
    _escalation_manager = escalation_manager
    logger.info("✅ Dependencies injected into Reaction workflow")


# ============================================================================
# ACTIVITIES - Wrappers around real reaction components
# ============================================================================

@activity.defn
async def classify_problem_activity(problem: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify problem using ReactionRulesEngine.

    Wrapper around ReactionRulesEngine.classify_problem()
    """
    logger.info(f"🔍 Classifying problem: {problem.get('type')}")

    try:
        # Real work: ReactionRulesEngine does classification
        classification = _rules_engine.classify_problem(problem)

        return {
            "status": "success",
            "reaction_level": classification.reaction_level.value,
            "recommended_action": classification.recommended_action,
            "reasoning": classification.reasoning
        }

    except Exception as e:
        logger.error(f"❌ Classification failed: {e}")
        # On error, escalate to brain
        return {
            "status": "failed",
            "reaction_level": "L3_escalate",
            "reasoning": f"Classification error: {e}"
        }


@activity.defn
async def execute_instant_action(problem: Dict[str, Any], action: str) -> Dict[str, Any]:
    """
    Execute L1 instant action (<10s).

    Wrapper around ActionExecutor L1 actions.
    """
    logger.info(f"⚡ Executing L1 instant action: {action}")

    try:
        # Real work: ActionExecutor handles execution
        context = {
            'problem_type': problem.get('type'),
            'severity': problem.get('severity'),
            'data': problem.get('data', {})
        }

        if action == 'restart_service':
            result = await _action_executor.restart_service(context)
        elif action == 'cleanup_disk':
            result = await _action_executor.cleanup_old_files(context)
        elif action == 'trigger_gc':
            result = await _action_executor.trigger_garbage_collection(context)
        else:
            result = ActionResult(
                success=False,
                action=action,
                message=f"Unknown action: {action}"
            )

        return {
            "status": "success" if result.success else "failed",
            "success": result.success,
            "action": result.action,
            "message": result.message,
            "execution_time": result.execution_time
        }

    except Exception as e:
        logger.error(f"❌ L1 action failed: {e}")
        return {
            "status": "failed",
            "success": False,
            "error": str(e)
        }


@activity.defn
async def execute_quick_action(problem: Dict[str, Any], action: str) -> Dict[str, Any]:
    """
    Execute L2 quick action (<1min).

    Wrapper around ActionExecutor L2 actions.
    """
    logger.info(f"⚡ Executing L2 quick action: {action}")

    try:
        context = {
            'problem_type': problem.get('type'),
            'severity': problem.get('severity'),
            'data': problem.get('data', {})
        }

        if action == 'scale_up':
            result = await _action_executor.scale_up_preventively(context)
        elif action == 'investigate':
            result = await _action_executor.investigate_processes(context)
        else:
            result = ActionResult(
                success=False,
                action=action,
                message=f"Unknown action: {action}"
            )

        return {
            "status": "success" if result.success else "failed",
            "success": result.success,
            "action": result.action,
            "message": result.message,
            "execution_time": result.execution_time
        }

    except Exception as e:
        logger.error(f"❌ L2 action failed: {e}")
        return {
            "status": "failed",
            "success": False,
            "error": str(e)
        }


@activity.defn
async def escalate_to_brain_activity(
    problem: Dict[str, Any],
    classification: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Escalate problem to workflow_intelligence (brain).

    Wrapper around EscalationManager.escalate_to_brain()
    """
    logger.info(f"🧠 Escalating to brain: {problem.get('type')}")

    try:
        # Real work: EscalationManager handles escalation
        escalation = await _escalation_manager.escalate_to_brain(
            problem=problem,
            severity=problem.get('severity', 'medium'),
            context=problem.get('data', {}),
            recommendations=[],
            reason=classification.get('reasoning', 'Unknown pattern')
        )

        return {
            "status": "success",
            "escalation_id": escalation.escalation_id,
            "escalated_at": escalation.escalated_at
        }

    except Exception as e:
        logger.error(f"❌ Escalation failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def wait_for_brain_directive_activity(escalation_id: str) -> Dict[str, Any]:
    """
    Wait for directive from brain.

    Wrapper around EscalationManager.check_for_directive()
    """
    logger.info(f"⏳ Waiting for brain directive: {escalation_id}")

    try:
        # TODO: Real implementation with polling or webhook
        # directive = await _escalation_manager.wait_for_directive(escalation_id)

        # Placeholder for now
        return {
            "status": "received",
            "directive": {
                "action": "apply_fix",
                "parameters": {}
            }
        }

    except Exception as e:
        logger.error(f"❌ Failed to receive directive: {e}")
        return {
            "status": "timeout",
            "error": str(e)
        }


# ============================================================================
# WORKFLOW - Lightweight orchestration wrapper
# ============================================================================

@workflow.defn
class ReactionWorkflow:
    """
    Reaction Workflow - Automated response wrapper.

    Simple orchestration:
    1. Classify problem (L1/L2/L3)
    2. Execute based on level:
       - L1: Instant reflex (<10s)
       - L2: Quick response (<1min)
       - L3: Escalate to brain
    3. Retry if failed
    4. Report to brain

    Temporal provides: durability, retries, state tracking.
    """

    @workflow.run
    async def run(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute reaction workflow.

        Args:
            problem: {
                'type': 'service_down',
                'severity': 'high',
                'data': {...}
            }
        """
        workflow.logger.info(f"🚀 Starting Reaction Workflow for: {problem.get('type')}")

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=3
        )

        try:
            # 1. Classify problem
            classification = await workflow.execute_activity(
                classify_problem_activity,
                args=[problem],
                start_to_close_timeout=timedelta(seconds=5),
                retry_policy=retry_policy
            )

            reaction_level = classification.get('reaction_level')
            workflow.logger.info(f"📊 Classified as: {reaction_level}")

            # 2. Act based on level
            if reaction_level == "L1_instant":
                result = await self._handle_L1(problem, classification)
            elif reaction_level == "L2_quick":
                result = await self._handle_L2(problem, classification)
            else:  # L3_escalate
                result = await self._handle_L3(problem, classification)

            return result

        except Exception as e:
            workflow.logger.error(f"❌ Reaction workflow failed: {e}")
            # On error, escalate to brain
            return await self._handle_L3_error(problem, str(e))

    async def _handle_L1(
        self,
        problem: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle L1 instant reflex."""
        workflow.logger.info("⚡ L1 Instant Reflex")

        action = classification.get('recommended_action')
        result = await workflow.execute_activity(
            execute_instant_action,
            args=[problem, action],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )

        if not result.get('success'):
            # L1 failed, escalate to L3
            workflow.logger.warning("⚠️ L1 failed, escalating to L3")
            return await self._handle_L3(problem, classification)

        workflow.logger.info(f"✅ L1 success: {result.get('message')}")
        return result

    async def _handle_L2(
        self,
        problem: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle L2 quick response."""
        workflow.logger.info("⚡ L2 Quick Response")

        action = classification.get('recommended_action')
        result = await workflow.execute_activity(
            execute_quick_action,
            args=[problem, action],
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )

        if not result.get('success'):
            # L2 failed, escalate to L3
            workflow.logger.warning("⚠️ L2 failed, escalating to L3")
            return await self._handle_L3(problem, classification)

        workflow.logger.info(f"✅ L2 success: {result.get('message')}")
        return result

    async def _handle_L3(
        self,
        problem: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle L3 escalation to brain."""
        workflow.logger.info("🧠 L3 Escalating to Brain")

        # Escalate
        escalation = await workflow.execute_activity(
            escalate_to_brain_activity,
            args=[problem, classification],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # Wait for directive from brain
        directive = await workflow.execute_activity(
            wait_for_brain_directive_activity,
            args=[escalation.get('escalation_id')],
            start_to_close_timeout=timedelta(minutes=10),
            heartbeat_timeout=timedelta(seconds=30)
        )

        workflow.logger.info(f"✅ L3 escalated: {escalation.get('escalation_id')}")

        return {
            "status": "escalated",
            "escalation_id": escalation.get('escalation_id'),
            "directive_status": directive.get('status')
        }

    async def _handle_L3_error(
        self,
        problem: Dict[str, Any],
        error: str
    ) -> Dict[str, Any]:
        """Handle workflow error by escalating."""
        workflow.logger.error(f"🚨 Escalating workflow error: {error}")

        error_classification = {
            "reaction_level": "L3_escalate",
            "reasoning": f"Workflow error: {error}"
        }

        return await self._handle_L3(
            {**problem, "workflow_error": error},
            error_classification
        )


# Export for worker registration
reaction_activities = [
    classify_problem_activity,
    execute_instant_action,
    execute_quick_action,
    escalate_to_brain_activity,
    wait_for_brain_directive_activity
]


# Import ActionResult for type hints
from dataclasses import dataclass

@dataclass
class ActionResult:
    """Action execution result (matches ActionExecutor)."""
    success: bool
    action: str
    message: str
    execution_time: float = 0.0
    details: dict = None
