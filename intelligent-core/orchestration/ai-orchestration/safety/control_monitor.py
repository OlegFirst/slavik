"""
Control Monitor
===============

Monitors for loss of control:
- Runaway AI (too many auto-decisions)
- Scope creep (AI doing more than authorized)
- Resource abuse (excessive operations)
- Unauthorized escalation
"""

import logging
from typing import List
from datetime import datetime, timedelta

from intelligent_core.ai_orchestration.models import (
    Decision, FullContext, SafetyResult, SafetyConcern, ActionType
)

logger = logging.getLogger(__name__)


class ControlMonitor:
    """
    Monitors for loss of control.

    Tracks:
    - Auto-resolve rate (% of decisions auto-executed)
    - Decision velocity (decisions per hour)
    - Resource consumption
    - Authorization levels

    Example:
        ```python
        monitor = ControlMonitor()
        await monitor.initialize()

        result = await monitor.check(decision, context)
        if not result.safe:
            print(f"Control concern: {result.concerns}")
        ```
    """

    # Thresholds
    MAX_AUTO_RESOLVE_RATE = 0.8  # Max 80% auto-resolved
    MAX_DECISIONS_PER_HOUR = 100  # Max 100 decisions/hour
    MAX_CONSECUTIVE_AUTO = 10     # Max 10 consecutive auto-resolves

    def __init__(self):
        self.initialized = False
        self.recent_decisions = []
        self.consecutive_auto_count = 0

    async def initialize(self) -> None:
        """Initialize control monitor."""
        self.initialized = True
        logger.info("ControlMonitor initialized")

    async def check(
        self,
        decision: Decision,
        context: FullContext
    ) -> SafetyResult:
        """
        Check for control issues.

        Args:
            decision: Decision to check
            context: Full context

        Returns:
            SafetyResult: Check result
        """
        concerns: List[SafetyConcern] = []

        # Track decision
        self._track_decision(decision)

        # Check 1: Auto-resolve rate
        auto_rate_concern = self._check_auto_resolve_rate(decision)
        if auto_rate_concern:
            concerns.append(auto_rate_concern)

        # Check 2: Decision velocity
        velocity_concern = self._check_decision_velocity()
        if velocity_concern:
            concerns.append(velocity_concern)

        # Check 3: Consecutive auto-resolves
        consecutive_concern = self._check_consecutive_auto(decision)
        if consecutive_concern:
            concerns.append(consecutive_concern)

        # Check 4: Scope creep
        scope_concern = self._check_scope_creep(decision, context)
        if scope_concern:
            concerns.append(scope_concern)

        safe = len([c for c in concerns if c.severity in ['critical', 'high']]) == 0

        return SafetyResult(
            safe=safe,
            concerns=concerns
        )

    def _track_decision(self, decision: Decision) -> None:
        """Track decision for monitoring."""
        self.recent_decisions.append({
            'action': decision.action,
            'timestamp': decision.timestamp,
            'auto': decision.action == ActionType.AUTO_RESOLVE
        })

        # Update consecutive counter
        if decision.action == ActionType.AUTO_RESOLVE:
            self.consecutive_auto_count += 1
        else:
            self.consecutive_auto_count = 0

        # Keep only last hour
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.recent_decisions = [
            d for d in self.recent_decisions
            if d['timestamp'] > cutoff
        ]

    def _check_auto_resolve_rate(
        self,
        decision: Decision
    ) -> SafetyConcern | None:
        """Check if too many auto-resolves."""
        if len(self.recent_decisions) < 10:
            return None

        auto_count = sum(1 for d in self.recent_decisions if d['auto'])
        auto_rate = auto_count / len(self.recent_decisions)

        if auto_rate > self.MAX_AUTO_RESOLVE_RATE:
            return SafetyConcern(
                type='loss_of_control',
                severity='high',
                description=f"Auto-resolve rate too high: {auto_rate:.1%} (max: {self.MAX_AUTO_RESOLVE_RATE:.1%})",
                evidence={
                    'auto_rate': auto_rate,
                    'auto_count': auto_count,
                    'total_decisions': len(self.recent_decisions)
                },
                recommended_action='require_human_approval'
            )

        return None

    def _check_decision_velocity(self) -> SafetyConcern | None:
        """Check if too many decisions per hour."""
        count = len(self.recent_decisions)

        if count > self.MAX_DECISIONS_PER_HOUR:
            return SafetyConcern(
                type='loss_of_control',
                severity='medium',
                description=f"Decision velocity too high: {count} decisions/hour (max: {self.MAX_DECISIONS_PER_HOUR})",
                evidence={
                    'decisions_per_hour': count,
                    'max_allowed': self.MAX_DECISIONS_PER_HOUR
                },
                recommended_action='throttle_or_escalate'
            )

        return None

    def _check_consecutive_auto(
        self,
        decision: Decision
    ) -> SafetyConcern | None:
        """Check for too many consecutive auto-resolves."""
        if self.consecutive_auto_count >= self.MAX_CONSECUTIVE_AUTO:
            return SafetyConcern(
                type='loss_of_control',
                severity='high',
                description=f"{self.consecutive_auto_count} consecutive auto-resolves (max: {self.MAX_CONSECUTIVE_AUTO})",
                evidence={
                    'consecutive_count': self.consecutive_auto_count,
                    'max_allowed': self.MAX_CONSECUTIVE_AUTO
                },
                recommended_action='require_human_checkpoint'
            )

        return None

    def _check_scope_creep(
        self,
        decision: Decision,
        context: FullContext
    ) -> SafetyConcern | None:
        """Check if AI is exceeding authorized scope."""
        # Check if decision tries to do something not in governance rules
        metadata = decision.metadata

        # Example: Trying to modify production without authorization
        if metadata.get('environment') == 'production':
            if decision.action == ActionType.AUTO_RESOLVE:
                # Check if authorized
                authorized = any(
                    rule.get('allows_production_changes', False)
                    for rule in context.governance_rules
                )

                if not authorized:
                    return SafetyConcern(
                        type='loss_of_control',
                        severity='critical',
                        description="Attempting unauthorized production changes",
                        evidence={
                            'environment': 'production',
                            'action': decision.action.value,
                            'authorized': False
                        },
                        recommended_action='block_and_escalate'
                    )

        return None

    def reset_counters(self) -> None:
        """Reset monitoring counters."""
        self.recent_decisions.clear()
        self.consecutive_auto_count = 0
        logger.info("Control monitor counters reset")
