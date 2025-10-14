"""
Policy-Aware Orchestrator
=========================

Integrates AI Orchestrator with Infrastructure Decision Center.

This creates a unified decision-making system where:
1. AI Orchestrator makes intelligent decisions
2. Infrastructure Decision Center validates policy compliance
3. Decisions require both AI approval AND policy approval

Features:
- Policy validation before auto-resolve
- Compliance checking for all actions
- Audit trail for governance
- Escalation when policies are violated
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .orchestrator import AIOrchestrator
from .models import Decision, ActionType
from infrastructure.policy_engine.decision_center import InfrastructureDecisionCenter
from infrastructure.policy_engine.policy_engine import PolicyEngine
from infrastructure.policy_engine.audit_logger import AuditLogger

logger = logging.getLogger(__name__)


class PolicyAwareOrchestrator(AIOrchestrator):
    """
    AI Orchestrator with Infrastructure Policy Integration

    Extends AIOrchestrator to validate all decisions against infrastructure policies.

    Decision Flow:
    1. AI makes decision (standard AIOrchestrator logic)
    2. Policy compliance check (Infrastructure Decision Center)
    3. If compliant: proceed
    4. If not compliant: escalate to human

    Example:
        ```python
        orchestrator = PolicyAwareOrchestrator()
        await orchestrator.initialize()

        decision = await orchestrator.decide(situation)
        # Decision is automatically validated against policies

        result = await orchestrator.execute(decision)
        # Execution is blocked if policy violated
        ```
    """

    def __init__(
        self,
        event_bus_backend: str = 'redis',
        enable_evolution: bool = True,
        enable_safety: bool = True,
        policy_file_path: Optional[str] = None
    ):
        """
        Initialize Policy-Aware Orchestrator

        Args:
            event_bus_backend: EventBus backend
            enable_evolution: Enable self-evolution
            enable_safety: Enable safety monitoring
            policy_file_path: Path to policies.yaml (optional)
        """
        # Initialize base orchestrator
        super().__init__(
            event_bus_backend=event_bus_backend,
            enable_evolution=enable_evolution,
            enable_safety=enable_safety
        )

        # Infrastructure Decision Center
        self.policy_engine = None
        self.decision_center = None
        self.policy_file_path = policy_file_path

        logger.info("Policy-Aware Orchestrator created")

    async def initialize(self) -> None:
        """
        Initialize orchestrator and infrastructure decision center.
        """
        # Initialize base orchestrator first
        await super().initialize()

        # Initialize Infrastructure Decision Center
        await self._initialize_decision_center()

        logger.info("🚀 Policy-Aware Orchestrator initialized")

    async def _initialize_decision_center(self) -> None:
        """Initialize Infrastructure Decision Center and Policy Engine."""
        try:
            logger.info("🔄 Initializing Infrastructure Decision Center...")

            # Create Policy Engine
            if self.policy_file_path:
                from pathlib import Path
                self.policy_engine = PolicyEngine(policy_file=Path(self.policy_file_path))
            else:
                self.policy_engine = PolicyEngine()

            logger.info("✅ Policy Engine initialized")

            # Create Decision Center
            self.decision_center = InfrastructureDecisionCenter(
                policy_engine=self.policy_engine,
                eventbus=self.event_bus
            )

            logger.info("✅ Infrastructure Decision Center initialized")
            logger.info("   - Policy validation enabled")
            logger.info("   - Compliance checking active")
            logger.info("   - Dual governance (AI + Policy)")

        except Exception as e:
            logger.warning(f"⚠️ Decision Center initialization failed: {e}")
            logger.warning("   Orchestrator will continue with AI-only governance")
            self.decision_center = None

    async def execute(self, decision: Decision) -> Dict[str, Any]:
        """
        Execute decision with policy validation.

        Validates decision against infrastructure policies before execution.

        Args:
            decision: The decision to execute

        Returns:
            Execution result with policy compliance info
        """
        logger.info(f"Executing decision with policy validation: {decision.action.value}")

        # If no decision center, fall back to base orchestrator
        if not self.decision_center:
            logger.warning("⚠️ No Decision Center - executing without policy validation")
            return await super().execute(decision)

        try:
            # Check if action requires policy validation
            if decision.action in [ActionType.AUTO_RESOLVE, ActionType.EMERGENCY_STOP]:
                # Validate with Infrastructure Decision Center
                policy_decision, can_proceed = await self._validate_with_policy(decision)

                if not can_proceed:
                    logger.warning(f"❌ Policy violation - escalating decision")

                    # Override action to escalate
                    decision.action = ActionType.ESCALATE_HUMAN
                    decision.rationale = f"Policy violation: {policy_decision.reasoning}"
                    decision.metadata['policy_blocked'] = True
                    decision.metadata['policy_reason'] = policy_decision.reasoning

                    # Execute escalation
                    return await super().execute(decision)
                else:
                    logger.info(f"✅ Policy compliance validated")
                    decision.metadata['policy_approved'] = True
                    decision.metadata['policy_reference'] = policy_decision.policy_reference

            # Execute with base orchestrator
            result = await super().execute(decision)

            # Add policy info to result
            result['policy_validated'] = True
            result['policy_compliant'] = decision.metadata.get('policy_approved', False)

            return result

        except Exception as e:
            logger.error(f"Error in policy-aware execution: {e}", exc_info=True)
            # Fall back to base execution
            return await super().execute(decision)

    async def _validate_with_policy(self, decision: Decision) -> tuple:
        """
        Validate decision with Infrastructure Decision Center.

        Args:
            decision: AI decision to validate

        Returns:
            Tuple of (policy_decision, can_proceed)
        """
        # Map AI action to infrastructure action
        action_type = self._map_ai_action_to_infrastructure_action(decision.action)

        # Extract service name from decision metadata
        service_name = decision.metadata.get('service', 'unknown')

        # Call Infrastructure Decision Center
        if decision.action == ActionType.AUTO_RESOLVE:
            policy_decision, can_proceed = await self.decision_center.decide_recovery_action(
                service_name=service_name,
                action_type=action_type,
                trigger_data=decision.metadata
            )
        elif decision.action == ActionType.EMERGENCY_STOP:
            # Emergency stops always require human approval
            policy_decision, can_proceed = await self.decision_center.decide_recovery_action(
                service_name=service_name,
                action_type='emergency_stop',
                trigger_data=decision.metadata
            )
        else:
            # Other actions don't need policy validation
            from infrastructure.policy_engine.decision_models import Decision as PolicyDecision
            from infrastructure.policy_engine.decision_models import DecisionOutcome
            policy_decision = PolicyDecision(
                decision_type='optimization',
                service_name=service_name,
                action_type='other',
                outcome=DecisionOutcome.APPROVED
            )
            can_proceed = True

        return policy_decision, can_proceed

    def _map_ai_action_to_infrastructure_action(self, action: ActionType) -> str:
        """
        Map AI Orchestrator action to Infrastructure Decision Center action.

        Args:
            action: AI action type

        Returns:
            Infrastructure action type string
        """
        mapping = {
            ActionType.AUTO_RESOLVE: 'restart',
            ActionType.EMERGENCY_STOP: 'emergency_stop',
            ActionType.ESCALATE_HUMAN: 'escalate',
            ActionType.DELEGATE: 'delegate',
            ActionType.WAIT_AND_MONITOR: 'monitor'
        }
        return mapping.get(action, 'unknown')

    def get_stats(self) -> Dict[str, Any]:
        """
        Get combined stats from AI Orchestrator and Decision Center.

        Returns:
            Combined statistics dictionary
        """
        stats = super().get_stats()

        if self.decision_center:
            stats['infrastructure_decision_center'] = self.decision_center.stats
            stats['policy_engine_loaded'] = self.policy_engine is not None
        else:
            stats['infrastructure_decision_center'] = None
            stats['policy_engine_loaded'] = False

        return stats
