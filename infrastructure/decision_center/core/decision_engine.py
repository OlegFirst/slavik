"""
Decision Engine - Core decision making logic
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .policy_engine import PolicyEngine
from ..models.decision import (
    Decision,
    DecisionRequest,
    DecisionType,
    DecisionOutcome
)

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Основной движок принятия решений

    Принимает DecisionRequest и возвращает Decision на основе:
    - Policies из PolicyEngine
    - Контекста системы
    - История recovery attempts
    - Приоритеты сервисов
    """

    def __init__(
        self,
        policy_engine: PolicyEngine,
        escalation_manager: Optional['EscalationManager'] = None,
        audit_logger: Optional['AuditLogger'] = None,
        ai_hub: Optional['AIIntelligenceHub'] = None
    ):
        """
        Initialize Decision Engine

        Args:
            policy_engine: Policy engine instance
            escalation_manager: Escalation manager (optional for MVP)
            audit_logger: Audit logger (optional for MVP)
            ai_hub: AI Intelligence Hub (optional for MVP)
        """
        self.policy_engine = policy_engine
        self.escalation_manager = escalation_manager
        self.audit_logger = audit_logger
        self.ai_hub = ai_hub

        logger.info("Decision Engine initialized")

    async def make_decision(
        self,
        request: DecisionRequest
    ) -> Decision:
        """
        Принимает решение на основе policies и context

        Args:
            request: Decision request

        Returns:
            Decision object

        Decision flow:
        1. Load policies for service
        2. Check if can auto-approve
        3. Check if requires escalation
        4. Check if requires AI consultation
        5. Check if requires manual approval
        6. Default: reject (safe fallback)
        """
        logger.info(
            f"Making decision for {request.service}.{request.action} "
            f"(request_id={request.request_id})"
        )

        # 1. Load policies for service
        policies = self.policy_engine.get_policies(request.service)

        try:
            # 2. Check auto-approval
            if self._can_auto_approve(request, policies):
                decision = self._auto_approve(request, policies)
                logger.info(f"Auto-approved: {request.service}.{request.action}")

            # 3. Check escalation needed
            elif self._requires_escalation(request, policies):
                decision = await self._escalate(request, policies)
                logger.warning(f"Escalated: {request.service}.{request.action}")

            # 4. Check AI consultation needed
            elif self._requires_ai_consultation(request):
                decision = await self._consult_ai(request, policies)
                logger.info(f"AI consulted: {request.service}.{request.action}")

            # 5. Manual approval needed
            elif self._requires_manual_approval(request, policies):
                decision = await self._request_approval(request, policies)
                logger.info(f"Manual approval requested: {request.service}.{request.action}")

            # 6. Safe default: reject
            else:
                decision = self._reject(
                    request,
                    "No matching policy - safe rejection"
                )
                logger.warning(f"Rejected (no policy): {request.service}.{request.action}")

            # Audit logging
            if self.audit_logger:
                await self.audit_logger.log_decision(decision, request, policies)

            return decision

        except Exception as e:
            logger.error(f"Decision making failed: {e}", exc_info=True)
            # Safe fallback: reject
            return self._reject(request, f"Decision error: {str(e)}")

    def _can_auto_approve(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> bool:
        """
        Проверяет можно ли автоматически одобрить

        Auto-approval conditions:
        - Action allowed by policy
        - Within max_auto_attempts
        - Not a critical service (or critical allows auto)
        - Not in business hours (if policy restricts)
        """
        auto_approval = policies.get("auto_approval", {})

        # Restart allowed if within attempts limit
        if request.action == "restart":
            attempts = request.context.get("recovery_attempts", 0)
            max_attempts = policies.get("max_auto_attempts", 3)

            if attempts < max_attempts:
                logger.debug(
                    f"Restart auto-approved: {attempts}/{max_attempts} attempts"
                )
                return True

            logger.debug(
                f"Restart requires escalation: {attempts} >= {max_attempts}"
            )
            return False

        # Failover allowed
        if request.action == "failover":
            allowed = auto_approval.get("failover_allowed", True)
            logger.debug(f"Failover auto-approval: {allowed}")
            return allowed

        # Scale down allowed (scale up requires approval)
        if request.action == "scale_down":
            requires_approval = auto_approval.get(
                "scale_down_requires_approval",
                False
            )
            allowed = not requires_approval
            logger.debug(f"Scale down auto-approval: {allowed}")
            return allowed

        # Configuration changes require approval
        if request.action == "configuration_change":
            logger.debug("Configuration change requires approval")
            return False

        # Default: don't auto-approve unknown actions
        logger.debug(f"Unknown action '{request.action}' - no auto-approval")
        return False

    def _requires_escalation(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> bool:
        """
        Проверяет нужна ли эскалация

        Escalation triggers:
        - Critical service with escalate_immediately policy
        - Max attempts exceeded
        - Failure pattern detected
        - RTO/RPO violation imminent
        """
        # Critical services escalate immediately
        if policies.get("escalate_immediately", False):
            logger.debug(f"Critical service - immediate escalation")
            return True

        # Max attempts exceeded
        attempts = request.context.get("recovery_attempts", 0)
        max_attempts = policies.get("max_auto_attempts", 3)

        if attempts >= max_attempts:
            logger.debug(
                f"Max attempts exceeded: {attempts} >= {max_attempts}"
            )
            return True

        # Pattern detection
        if self._detect_failure_pattern(request):
            logger.debug("Failure pattern detected - escalation needed")
            return True

        # RTO violation check
        if self._rto_violation_imminent(request, policies):
            logger.debug("RTO violation imminent - escalation needed")
            return True

        return False

    def _detect_failure_pattern(self, request: DecisionRequest) -> bool:
        """
        Детектирует паттерны повторяющихся проблем

        Pattern indicators:
        - Same failure repeatedly
        - Recurring at same time
        - Multiple services affected
        """
        # Get recent failures from context
        recent_failures = request.context.get("recent_failures", [])

        if len(recent_failures) >= 5:
            # Same failure 5+ times in window
            logger.debug(f"Pattern detected: {len(recent_failures)} recent failures")
            return True

        # Check time-based pattern (e.g., every day at 10:00)
        failure_times = request.context.get("failure_times", [])
        if len(failure_times) >= 3:
            # Simplified: if 3+ failures, consider pattern
            logger.debug(f"Time-based pattern: {len(failure_times)} occurrences")
            return True

        return False

    def _rto_violation_imminent(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> bool:
        """
        Проверяет близко ли нарушение RTO

        Args:
            request: Decision request
            policies: Service policies

        Returns:
            True if RTO violation imminent
        """
        rto = policies.get("rto", 300)  # default 5 minutes
        downtime = request.context.get("downtime_seconds", 0)

        # If downtime > 80% of RTO, consider violation imminent
        threshold = rto * 0.8

        if downtime > threshold:
            logger.warning(
                f"RTO violation imminent: {downtime}s > {threshold}s "
                f"(80% of RTO={rto}s)"
            )
            return True

        return False

    def _requires_ai_consultation(self, request: DecisionRequest) -> bool:
        """
        Проверяет нужна ли консультация с AI

        AI consultation for:
        - Unknown issues
        - Performance degradation
        - Root cause unclear
        - Resource optimization decisions
        """
        complexity_indicators = [
            "unknown issue",
            "repeated failure",
            "root cause unclear",
            "performance degradation",
            "resource optimization",
            "pattern not recognized"
        ]

        reason_lower = request.reason.lower()
        needs_ai = any(
            indicator in reason_lower
            for indicator in complexity_indicators
        )

        if needs_ai:
            logger.debug(f"AI consultation needed: {request.reason}")

        return needs_ai

    def _requires_manual_approval(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> bool:
        """
        Проверяет требуется ли manual approval

        Manual approval for:
        - Scale up operations
        - Critical services
        - Configuration changes
        - Policy-required approval
        """
        auto_approval = policies.get("auto_approval", {})

        # Scale up requires approval
        if request.action == "scale_up":
            requires = auto_approval.get("scale_up_requires_approval", True)
            if requires:
                logger.debug("Scale up requires manual approval")
                return True

        # Configuration changes require approval
        if request.action == "configuration_change":
            requires = auto_approval.get(
                "configuration_change_requires_approval",
                True
            )
            if requires:
                logger.debug("Configuration change requires approval")
                return True

        # Policy-defined manual approval
        if policies.get("require_manual_approval", False):
            logger.debug("Policy requires manual approval")
            return True

        return False

    def _auto_approve(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> Decision:
        """
        Автоматически одобряет действие

        Args:
            request: Decision request
            policies: Service policies

        Returns:
            Approved decision
        """
        return Decision.create(
            request=request,
            decision_type=DecisionType.AUTO_APPROVED,
            outcome=DecisionOutcome.APPROVED,
            justification=(
                f"Auto-approved by policy: {request.action} within limits. "
                f"Attempts: {request.context.get('recovery_attempts', 0)}/"
                f"{policies.get('max_auto_attempts', 3)}"
            ),
            decided_by="system",
            metadata={
                "policy_version": self.policy_engine.get_version(),
                "auto_approval_rule": f"{request.action}_allowed"
            }
        )

    async def _escalate(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> Decision:
        """
        Эскалирует решение к человеку

        Args:
            request: Decision request
            policies: Service policies

        Returns:
            Escalated decision
        """
        if not self.escalation_manager:
            # No escalation manager - safe rejection
            logger.error("Escalation needed but no EscalationManager configured")
            return self._reject(
                request,
                "Escalation required but not configured"
            )

        # Delegate to escalation manager
        decision = await self.escalation_manager.escalate(
            request,
            reason=(
                f"Max attempts: {request.context.get('recovery_attempts', 0)}/"
                f"{policies.get('max_auto_attempts', 3)}"
            )
        )

        return decision

    async def _consult_ai(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> Decision:
        """
        Консультация с AI Intelligence Hub

        Args:
            request: Decision request
            policies: Service policies

        Returns:
            AI-consulted decision
        """
        if not self.ai_hub:
            # No AI hub - fallback to manual approval
            logger.warning("AI consultation needed but no AI Hub configured")
            return await self._request_approval(request, policies)

        try:
            # Consult AI
            ai_response = await self.ai_hub.consult(
                problem=request.reason,
                context=request.context,
                service=request.service,
                action=request.action,
                complexity="medium"
            )

            # High confidence → auto-approve with AI justification
            if ai_response.confidence > 0.8:
                return Decision.create(
                    request=request,
                    decision_type=DecisionType.AI_CONSULTED,
                    outcome=DecisionOutcome.APPROVED,
                    justification=(
                        f"AI recommendation (confidence: {ai_response.confidence}): "
                        f"{ai_response.reasoning}"
                    ),
                    decided_by="ai",
                    metadata={
                        "ai_model": ai_response.model_used,
                        "ai_tier": ai_response.tier,
                        "confidence": ai_response.confidence
                    }
                )

            # Low confidence → escalate to human
            else:
                logger.warning(
                    f"AI confidence too low: {ai_response.confidence}. "
                    "Escalating to human."
                )
                return await self._escalate(request, policies)

        except Exception as e:
            logger.error(f"AI consultation failed: {e}")
            # Fallback to manual approval
            return await self._request_approval(request, policies)

    async def _request_approval(
        self,
        request: DecisionRequest,
        policies: Dict[str, Any]
    ) -> Decision:
        """
        Запрашивает manual approval

        Args:
            request: Decision request
            policies: Service policies

        Returns:
            Pending decision
        """
        # Create pending decision
        decision = Decision.create(
            request=request,
            decision_type=DecisionType.REQUIRES_APPROVAL,
            outcome=DecisionOutcome.PENDING,
            justification=f"Manual approval required for {request.action}",
            decided_by="system",
            expires_at=datetime.utcnow() + timedelta(minutes=30),  # 30 min TTL
            metadata={
                "approval_timeout_minutes": 30,
                "policy_version": self.policy_engine.get_version()
            }
        )

        # TODO: Send notification to operators
        logger.info(
            f"Manual approval requested: {request.service}.{request.action} "
            f"(decision_id={decision.decision_id})"
        )

        return decision

    def _reject(self, request: DecisionRequest, reason: str) -> Decision:
        """
        Отклоняет действие (safe fallback)

        Args:
            request: Decision request
            reason: Rejection reason

        Returns:
            Rejected decision
        """
        return Decision.create(
            request=request,
            decision_type=DecisionType.REJECTED,
            outcome=DecisionOutcome.REJECTED,
            justification=f"Rejected: {reason}",
            decided_by="system",
            metadata={
                "rejection_reason": reason,
                "safe_fallback": True
            }
        )
