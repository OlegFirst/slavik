"""
Decision Engine - Intelligent decision making for MIO Manager
==============================================================

Makes decisions based on:
- Platform state
- Historical patterns
- Business rules
- AI recommendations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DecisionPriority(Enum):
    """Decision priority levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"          # Act soon
    MEDIUM = "medium"      # Can wait
    LOW = "low"            # Nice to have


class DecisionType(Enum):
    """Types of decisions"""
    DEPLOY = "deploy"
    RESTART = "restart"
    SCALE = "scale"
    FIX = "fix"
    ALERT = "alert"
    INVESTIGATE = "investigate"
    IGNORE = "ignore"


class DecisionEngine:
    """
    Makes intelligent decisions for platform management

    Uses:
    - Business rules (policy-based)
    - AI recommendations (from AICoordinator)
    - Historical patterns
    - Current state
    """

    def __init__(self):
        """Initialize decision engine"""
        self.decisions_history = []
        logger.info(" Decision Engine initialized")

    async def make_decision(
        self,
        situation: Dict[str, Any],
        ai_recommendation: Optional[Dict] = None,
        policies: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make decision based on situation, AI recommendation, and policies

        Args:
            situation: Current situation
            ai_recommendation: AI coordinator's recommendation
            policies: Business policies/constraints

        Returns:
            Decision with action, reasoning, and metadata
        """
        logger.info(f" Making decision for: {situation.get('type', 'unknown')}")

        try:
            # Extract situation details
            situation_type = situation.get('type')
            severity = situation.get('severity', 'medium')
            metrics = situation.get('metrics', {})

            # Apply business rules first
            policy_decision = self._apply_policies(situation, policies)

            # If policy has strong opinion, follow it
            if policy_decision.get('mandatory'):
                decision = policy_decision
                decision['reasoning'] = f"Policy-mandated: {policy_decision['reasoning']}"
                decision['source'] = 'policy'

            # Otherwise consider AI recommendation
            elif ai_recommendation and ai_recommendation.get('confidence', 0) > 0.7:
                decision = {
                    'action': ai_recommendation['recommended_action'],
                    'reasoning': ai_recommendation['reasoning'],
                    'confidence': ai_recommendation['confidence'],
                    'source': 'ai',
                    'mandatory': False
                }

            # Fallback to rule-based decision
            else:
                decision = self._rule_based_decision(situation)
                decision['source'] = 'rules'

            # Add metadata
            decision['situation'] = situation_type
            decision['severity'] = severity
            decision['priority'] = self._calculate_priority(severity, decision)
            decision['timestamp'] = datetime.utcnow().isoformat()

            # Record decision
            self._record_decision(decision)

            logger.info(f" Decision made: {decision['action']} (source: {decision['source']})")

            return decision

        except Exception as e:
            logger.error(f" Decision making failed: {e}")
            return self._safe_decision(situation)

    def _apply_policies(
        self,
        situation: Dict,
        policies: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Apply business policies

        Examples:
        - Never restart during business hours
        - Always alert on critical issues
        - Auto-approve low-risk changes
        """
        if not policies:
            return {'mandatory': False}

        # Example policy checks
        severity = situation.get('severity')
        time_of_day = datetime.utcnow().hour

        # Critical issues - always mandatory
        if severity == 'critical':
            return {
                'action': DecisionType.ALERT.value,
                'reasoning': 'Critical severity requires immediate alert',
                'mandatory': True,
                'confidence': 1.0
            }

        # Business hours policy (9-18)
        if 9 <= time_of_day <= 18:
            if situation.get('requires_restart'):
                return {
                    'action': DecisionType.INVESTIGATE.value,
                    'reasoning': 'Cannot restart during business hours',
                    'mandatory': True,
                    'confidence': 1.0
                }

        return {'mandatory': False}

    def _rule_based_decision(self, situation: Dict) -> Dict[str, Any]:
        """
        Rule-based decision (fallback when no AI/policy)

        Simple heuristics based on situation type and metrics
        """
        situation_type = situation.get('type')
        severity = situation.get('severity', 'medium')
        metrics = situation.get('metrics', {})

        # Service down
        if situation_type == 'service_down':
            return {
                'action': DecisionType.RESTART.value,
                'reasoning': 'Service is down, restart recommended',
                'confidence': 0.8,
                'mandatory': False
            }

        # High CPU/Memory
        if metrics.get('cpu', 0) > 90 or metrics.get('memory', 0) > 90:
            return {
                'action': DecisionType.INVESTIGATE.value,
                'reasoning': 'High resource usage requires investigation',
                'confidence': 0.7,
                'mandatory': False
            }

        # Event gap
        if situation_type == 'event_gap':
            gap_type = situation.get('gap_type')
            if gap_type == 'missing_subscriber':
                return {
                    'action': DecisionType.FIX.value,
                    'reasoning': 'Missing subscriber should be fixed',
                    'confidence': 0.9,
                    'mandatory': False
                }

        # Default: investigate
        return {
            'action': DecisionType.INVESTIGATE.value,
            'reasoning': 'Unknown situation, investigate first',
            'confidence': 0.5,
            'mandatory': False
        }

    def _calculate_priority(self, severity: str, decision: Dict) -> str:
        """Calculate decision priority"""
        # Mandatory decisions are high priority
        if decision.get('mandatory'):
            return DecisionPriority.CRITICAL.value

        # Severity-based
        if severity == 'critical':
            return DecisionPriority.CRITICAL.value
        elif severity == 'high':
            return DecisionPriority.HIGH.value
        elif severity == 'medium':
            return DecisionPriority.MEDIUM.value
        else:
            return DecisionPriority.LOW.value

    def _safe_decision(self, situation: Dict) -> Dict[str, Any]:
        """Safe fallback decision"""
        return {
            'action': DecisionType.INVESTIGATE.value,
            'reasoning': 'Error in decision making, investigate manually',
            'confidence': 0.0,
            'priority': DecisionPriority.MEDIUM.value,
            'source': 'fallback',
            'timestamp': datetime.utcnow().isoformat()
        }

    def _record_decision(self, decision: Dict):
        """Record decision for learning"""
        self.decisions_history.append(decision)

        # Keep only recent decisions (last 1000)
        if len(self.decisions_history) > 1000:
            self.decisions_history = self.decisions_history[-1000:]

    def get_decision_history(
        self,
        limit: int = 10,
        action_type: Optional[str] = None
    ) -> List[Dict]:
        """Get recent decisions"""
        history = self.decisions_history

        if action_type:
            history = [d for d in history if d.get('action') == action_type]

        return history[-limit:]

    def get_decision_stats(self) -> Dict[str, Any]:
        """Get decision statistics"""
        if not self.decisions_history:
            return {'total': 0}

        total = len(self.decisions_history)

        # Count by source
        by_source = {}
        by_action = {}
        by_priority = {}

        for decision in self.decisions_history:
            source = decision.get('source', 'unknown')
            action = decision.get('action', 'unknown')
            priority = decision.get('priority', 'unknown')

            by_source[source] = by_source.get(source, 0) + 1
            by_action[action] = by_action.get(action, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

        return {
            'total': total,
            'by_source': by_source,
            'by_action': by_action,
            'by_priority': by_priority,
            'most_common_action': max(by_action, key=by_action.get) if by_action else None,
            'most_common_source': max(by_source, key=by_source.get) if by_source else None
        }
