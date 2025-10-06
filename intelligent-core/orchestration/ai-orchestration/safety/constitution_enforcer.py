"""
Constitution Enforcer
=====================

Enforces immutable safety rules (the "constitution").

CONSTITUTION RULES (IMMUTABLE):
1. Never modify user data without explicit permission
2. Never delete audit trail
3. Never modify production code without human review
4. Always escalate when confidence < 70%
5. Never bypass governance rules
6. Never expose sensitive data
7. Always maintain data integrity
"""

import logging
from typing import List

from intelligent_core.ai_orchestration.models import (
    Decision, FullContext, SafetyResult, SafetyConcern, ActionType
)

logger = logging.getLogger(__name__)


# IMMUTABLE CONSTITUTION - DO NOT MODIFY
CONSTITUTION = [
    {
        'id': 'CONST_001',
        'rule': 'Never modify user data without explicit permission',
        'severity': 'critical',
        'keywords': ['modify', 'update', 'change', 'alter', 'user_data', 'customer_data']
    },
    {
        'id': 'CONST_002',
        'rule': 'Never delete audit trail',
        'severity': 'critical',
        'keywords': ['delete', 'remove', 'drop', 'audit', 'log', 'trail']
    },
    {
        'id': 'CONST_003',
        'rule': 'Never modify production code without human review',
        'severity': 'critical',
        'keywords': ['code', 'production', 'deploy', 'release', 'modify_code']
    },
    {
        'id': 'CONST_004',
        'rule': 'Always escalate when confidence < 70%',
        'severity': 'high',
        'threshold': 0.7
    },
    {
        'id': 'CONST_005',
        'rule': 'Never bypass governance rules',
        'severity': 'critical',
        'keywords': ['bypass', 'skip', 'ignore', 'governance', 'compliance']
    },
    {
        'id': 'CONST_006',
        'rule': 'Never expose sensitive data',
        'severity': 'critical',
        'keywords': ['expose', 'leak', 'share', 'password', 'secret', 'token', 'api_key']
    },
    {
        'id': 'CONST_007',
        'rule': 'Always maintain data integrity',
        'severity': 'critical',
        'keywords': ['corrupt', 'damage', 'integrity', 'consistency']
    }
]


class ConstitutionEnforcer:
    """
    Enforces immutable constitution rules.

    The constitution is a set of rules that CANNOT be changed
    by the AI or any automatic process. They require manual
    code changes and deployment.

    Example:
        ```python
        enforcer = ConstitutionEnforcer()
        await enforcer.initialize()

        result = await enforcer.validate(decision, context)
        if not result.safe:
            print(f"Constitution violated: {result.concerns}")
        ```
    """

    def __init__(self):
        self.constitution = CONSTITUTION
        self.initialized = False
        self.violation_count = 0

    async def initialize(self) -> None:
        """Initialize constitution enforcer."""
        logger.info(f"Constitution loaded: {len(self.constitution)} rules")
        self.initialized = True

    async def validate(
        self,
        decision: Decision,
        context: FullContext
    ) -> SafetyResult:
        """
        Validate decision against constitution.

        Args:
            decision: Decision to validate
            context: Full context

        Returns:
            SafetyResult: Validation result

        Example:
            ```python
            result = await enforcer.validate(decision, context)
            for concern in result.concerns:
                if concern.type == 'constitution_violation':
                    # Block immediately
                    pass
            ```
        """
        concerns: List[SafetyConcern] = []

        # Check each rule
        for rule in self.constitution:
            violation = self._check_rule(rule, decision, context)
            if violation:
                concerns.append(violation)
                self.violation_count += 1

        # Constitution violations are always blocking
        safe = len(concerns) == 0

        if not safe:
            logger.error(f"Constitution violated: {len(concerns)} violations")

        return SafetyResult(
            safe=safe,
            concerns=concerns,
            constitution_check=safe
        )

    def _check_rule(
        self,
        rule: dict,
        decision: Decision,
        context: FullContext
    ) -> SafetyConcern | None:
        """Check individual rule."""

        # Rule CONST_004: Low confidence check
        if rule['id'] == 'CONST_004':
            if decision.confidence < rule.get('threshold', 0.7):
                if decision.action != ActionType.ESCALATE_HUMAN:
                    return SafetyConcern(
                        type='constitution_violation',
                        severity='high',
                        description=f"Confidence {decision.confidence:.2f} < 0.7 requires human escalation",
                        evidence={
                            'rule_id': rule['id'],
                            'confidence': decision.confidence,
                            'action': decision.action.value
                        },
                        recommended_action='escalate_to_human'
                    )
            return None

        # Keyword-based rules
        keywords = rule.get('keywords', [])
        if not keywords:
            return None

        # Check decision action and rationale
        text = f"{decision.action.value} {decision.rationale}".lower()

        # Check metadata
        metadata_text = str(decision.metadata).lower()
        text += " " + metadata_text

        # Look for keyword matches
        matches = [kw for kw in keywords if kw in text]

        if matches:
            # Potential violation - analyze context
            if self._is_violation(rule, decision, matches):
                return SafetyConcern(
                    type='constitution_violation',
                    severity=rule['severity'],
                    description=f"Violated: {rule['rule']}",
                    evidence={
                        'rule_id': rule['id'],
                        'rule': rule['rule'],
                        'matched_keywords': matches,
                        'decision_action': decision.action.value,
                        'decision_rationale': decision.rationale
                    },
                    recommended_action='block_and_escalate'
                )

        return None

    def _is_violation(
        self,
        rule: dict,
        decision: Decision,
        matches: List[str]
    ) -> bool:
        """Determine if keyword matches constitute actual violation."""

        # CONST_001: User data modification
        if rule['id'] == 'CONST_001':
            # Only violation if trying to auto-resolve without permission
            if decision.action == ActionType.AUTO_RESOLVE:
                if 'modify' in matches or 'update' in matches:
                    # Check if permission granted in metadata
                    return not decision.metadata.get('user_permission_granted', False)

        # CONST_002: Audit trail deletion
        if rule['id'] == 'CONST_002':
            if 'delete' in matches and 'audit' in matches:
                return True  # Always block audit deletion

        # CONST_003: Code modification
        if rule['id'] == 'CONST_003':
            if decision.action == ActionType.AUTO_RESOLVE:
                if 'code' in matches or 'production' in matches:
                    # Only allow with human review flag
                    return not decision.metadata.get('human_reviewed', False)

        # CONST_005: Governance bypass
        if rule['id'] == 'CONST_005':
            if 'bypass' in matches or 'skip' in matches:
                return True  # Always block bypass attempts

        # CONST_006: Data exposure
        if rule['id'] == 'CONST_006':
            if 'expose' in matches or 'leak' in matches:
                return True  # Always block data exposure

        # CONST_007: Data integrity
        if rule['id'] == 'CONST_007':
            if 'corrupt' in matches or 'damage' in matches:
                return True  # Always block integrity violations

        return False

    def get_constitution(self) -> List[dict]:
        """Get constitution rules (read-only)."""
        return self.constitution.copy()

    def get_violation_count(self) -> int:
        """Get total violation count."""
        return self.violation_count
