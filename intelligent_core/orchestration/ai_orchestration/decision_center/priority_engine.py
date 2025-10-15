"""
Priority Engine
===============

Assesses priority level for situations based on multiple factors:
- Business impact
- Time sensitivity
- Risk level
- Compliance requirements
- User impact
"""

import logging
from typing import Dict, List
from datetime import datetime

from ..models import Priority, PriorityLevel, FullContext

logger = logging.getLogger(__name__)


class PriorityEngine:
    """
    Determines priority level for situations.

    Priority is calculated based on weighted factors:
    - Business impact (30%)
    - Time sensitivity (25%)
    - Risk level (20%)
    - Compliance impact (15%)
    - User impact (10%)

    Example:
        ```python
        engine = PriorityEngine()
        priority = await engine.assess_priority(context)
        print(f"Priority: {priority.level.name} ({priority.score}/100)")
        ```
    """

    # Priority factor weights
    WEIGHTS = {
        'business_impact': 0.30,
        'time_sensitivity': 0.25,
        'risk_level': 0.20,
        'compliance_impact': 0.15,
        'user_impact': 0.10
    }

    def __init__(self):
        logger.info("PriorityEngine initialized")

    async def assess_priority(self, context: FullContext) -> Priority:
        """
        Assess priority for given context.

        Args:
            context: Full context with platform state, workflows, events, etc.

        Returns:
            Priority: Priority assessment with level and reasoning

        Example:
            ```python
            priority = await engine.assess_priority(context)
            if priority.level == PriorityLevel.CRITICAL:
                # Handle immediately
                pass
            ```
        """
        logger.debug("Assessing priority...")

        # Calculate individual factor scores
        business_impact = self._assess_business_impact(context)
        time_sensitivity = self._assess_time_sensitivity(context)
        risk_level = self._assess_risk_level(context)
        compliance_impact = self._assess_compliance_impact(context)
        user_impact = self._assess_user_impact(context)

        # Calculate weighted score
        score = (
            business_impact * self.WEIGHTS['business_impact'] +
            time_sensitivity * self.WEIGHTS['time_sensitivity'] +
            risk_level * self.WEIGHTS['risk_level'] +
            compliance_impact * self.WEIGHTS['compliance_impact'] +
            user_impact * self.WEIGHTS['user_impact']
        )

        # Reasoning breakdown
        reasoning = {
            'business_impact': business_impact,
            'time_sensitivity': time_sensitivity,
            'risk_level': risk_level,
            'compliance_impact': compliance_impact,
            'user_impact': user_impact,
            'weighted_score': score
        }

        priority = Priority.from_score(score, reasoning)

        logger.info(f"Priority assessed: {priority.level.name} (score: {score:.1f})")
        return priority

    def _assess_business_impact(self, context: FullContext) -> float:
        """
        Assess business impact (0-100).

        Factors:
        - Number of affected workflows
        - Critical processes impacted
        - Financial impact
        """
        score = 0.0

        # Active workflows
        num_workflows = len(context.workflows)
        if num_workflows > 10:
            score += 30
        elif num_workflows > 5:
            score += 20
        elif num_workflows > 0:
            score += 10

        # Critical processes
        critical_workflows = [
            w for w in context.workflows
            if w.get('priority') == 'critical'
        ]
        if len(critical_workflows) > 0:
            score += 40

        # Platform state
        if context.platform_state.get('status') == 'degraded':
            score += 20
        elif context.platform_state.get('status') == 'down':
            score += 50

        return min(score, 100)

    def _assess_time_sensitivity(self, context: FullContext) -> float:
        """
        Assess time sensitivity (0-100).

        Factors:
        - SLA deadlines
        - Regulatory deadlines
        - User expectations
        """
        score = 0.0

        # Recent events frequency (high activity = time sensitive)
        num_recent_events = len(context.recent_events)
        if num_recent_events > 100:
            score += 40
        elif num_recent_events > 50:
            score += 25
        elif num_recent_events > 10:
            score += 10

        # Check for workflow deadlines
        for workflow in context.workflows:
            deadline = workflow.get('deadline')
            if deadline:
                # TODO: Calculate time until deadline
                score += 20
                break

        # Governance rules urgency
        urgent_rules = [
            r for r in context.governance_rules
            if r.get('urgency') == 'high'
        ]
        if len(urgent_rules) > 0:
            score += 30

        return min(score, 100)

    def _assess_risk_level(self, context: FullContext) -> float:
        """
        Assess risk level (0-100).

        Factors:
        - Security risks
        - Data integrity risks
        - Compliance risks
        """
        score = 0.0

        # Check for security-related events
        security_events = [
            e for e in context.recent_events
            if 'security' in e.get('type', '').lower()
        ]
        if len(security_events) > 0:
            score += 50

        # Similar situations with bad outcomes
        failed_situations = [
            s for s in context.similar_situations
            if s.get('outcome') == 'failure'
        ]
        if len(failed_situations) > len(context.similar_situations) / 2:
            score += 30

        # Platform state risks
        if context.platform_state.get('status') in ['degraded', 'down']:
            score += 40

        return min(score, 100)

    def _assess_compliance_impact(self, context: FullContext) -> float:
        """
        Assess compliance impact (0-100).

        Factors:
        - Regulatory requirements
        - Audit requirements
        - Governance rules
        """
        score = 0.0

        # Critical governance rules
        critical_rules = [
            r for r in context.governance_rules
            if r.get('severity') == 'critical'
        ]
        if len(critical_rules) > 0:
            score += 50

        # Regulatory changes
        if len(context.regulatory_changes) > 0:
            score += 30

        # Audit-related workflows
        audit_workflows = [
            w for w in context.workflows
            if 'audit' in w.get('type', '').lower()
        ]
        if len(audit_workflows) > 0:
            score += 20

        return min(score, 100)

    def _assess_user_impact(self, context: FullContext) -> float:
        """
        Assess user impact (0-100).

        Factors:
        - Number of affected users
        - User experience degradation
        - Service availability
        """
        score = 0.0

        # Platform availability
        if context.platform_state.get('status') == 'down':
            score += 80
        elif context.platform_state.get('status') == 'degraded':
            score += 40

        # Active workflows (proxy for user activity)
        num_workflows = len(context.workflows)
        if num_workflows > 20:
            score += 40
        elif num_workflows > 10:
            score += 25
        elif num_workflows > 5:
            score += 15

        return min(score, 100)
