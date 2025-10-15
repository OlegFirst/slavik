"""
Infrastructure Decision Consultation API

Provides consultation services for infrastructure-level decisions.
Integrates with Decision Center via EventBus for expert recommendations.

This module routes infrastructure problems to appropriate specialists:
- Database issues → Database Specialist
- Performance problems → Performance Expert
- Security concerns → Security Specialist
- BCM decisions → BCM Consultant
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SpecialistType(Enum):
    """Types of infrastructure specialists"""
    DATABASE_SPECIALIST = "database_specialist"
    PERFORMANCE_EXPERT = "performance_expert"
    SECURITY_SPECIALIST = "security_specialist"
    BCM_CONSULTANT = "bcm_consultant"
    GENERAL_CONSULTANT = "general_consultant"


class InfrastructureConsultationAPI:
    """
    Consultation API for infrastructure decisions

    Routes infrastructure problems to appropriate specialists and
    provides expert recommendations for Decision Center.

    MVP Implementation:
    - Simulates specialist consultations
    - Returns structured recommendations
    - Logs all consultations for learning

    Future:
    - Real specialist integration via AI Orchestrator
    - Multi-expert consensus
    - Historical pattern matching
    """

    def __init__(
        self,
        eventbus: Optional[Any] = None,
        enable_logging: bool = True
    ):
        """
        Initialize consultation API

        Args:
            eventbus: EventBus for event-driven integration
            enable_logging: Enable consultation logging
        """
        self.eventbus = eventbus
        self.enable_logging = enable_logging

        # Consultation statistics
        self.stats = {
            'total_consultations': 0,
            'by_specialist': {s.value: 0 for s in SpecialistType},
            'avg_confidence': 0.0
        }

        logger.info("Infrastructure Consultation API initialized")

    async def consult(
        self,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any],
        complexity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Get expert consultation for infrastructure decision

        Args:
            service: Service name (e.g., "database", "redis")
            action: Proposed action (e.g., "restart", "scale_up")
            reason: Reason for action
            context: Additional context
            complexity: Complexity level (low/medium/high)

        Returns:
            Consultation response with recommendations
        """
        # Determine which specialists to consult
        specialists = self._determine_specialists(service, reason, context)

        # Get recommendations from each specialist
        recommendations = []
        for specialist in specialists:
            recommendation = await self._consult_specialist(
                specialist=specialist,
                service=service,
                action=action,
                reason=reason,
                context=context,
                complexity=complexity
            )
            recommendations.append(recommendation)

        # Aggregate recommendations
        final_recommendation = self._aggregate_recommendations(
            recommendations=recommendations,
            service=service,
            action=action,
            context=context
        )

        # Update statistics
        self._update_stats(specialists, final_recommendation)

        # Log consultation (for learning)
        if self.enable_logging:
            await self._log_consultation(
                service=service,
                action=action,
                reason=reason,
                specialists=specialists,
                recommendation=final_recommendation
            )

        return final_recommendation

    def _determine_specialists(
        self,
        service: str,
        reason: str,
        context: Dict[str, Any]
    ) -> List[SpecialistType]:
        """
        Determine which specialists should be consulted

        Args:
            service: Service name
            reason: Problem reason
            context: Additional context

        Returns:
            List of specialist types to consult
        """
        specialists = []
        reason_lower = reason.lower()

        # Database specialist
        if 'database' in service.lower() or 'db' in service.lower():
            specialists.append(SpecialistType.DATABASE_SPECIALIST)
        if any(word in reason_lower for word in ['database', 'query', 'transaction', 'schema']):
            if SpecialistType.DATABASE_SPECIALIST not in specialists:
                specialists.append(SpecialistType.DATABASE_SPECIALIST)

        # Performance expert
        if any(word in reason_lower for word in ['performance', 'cpu', 'memory', 'latency', 'slow']):
            specialists.append(SpecialistType.PERFORMANCE_EXPERT)

        # Security specialist
        if any(word in reason_lower for word in ['security', 'breach', 'attack', 'unauthorized']):
            specialists.append(SpecialistType.SECURITY_SPECIALIST)

        # BCM consultant (for repeated failures or critical situations)
        recovery_attempts = context.get('recovery_attempts', 0)
        if recovery_attempts >= 2 or any(word in reason_lower for word in ['rto', 'rpo', 'critical']):
            specialists.append(SpecialistType.BCM_CONSULTANT)

        # Fallback to general consultant if no specific specialist
        if not specialists:
            specialists.append(SpecialistType.GENERAL_CONSULTANT)

        logger.info(f"Determined specialists for {service}: {[s.value for s in specialists]}")
        return specialists

    async def _consult_specialist(
        self,
        specialist: SpecialistType,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any],
        complexity: str
    ) -> Dict[str, Any]:
        """
        Get recommendation from specific specialist

        MVP: Simulates specialist consultation
        Future: Routes to actual AI specialists via Orchestrator

        Args:
            specialist: Specialist type
            service: Service name
            action: Proposed action
            reason: Reason for action
            context: Additional context
            complexity: Complexity level

        Returns:
            Specialist recommendation
        """
        # MVP: Simulate specialist consultations based on heuristics
        if specialist == SpecialistType.DATABASE_SPECIALIST:
            return self._database_specialist_logic(service, action, reason, context)

        elif specialist == SpecialistType.PERFORMANCE_EXPERT:
            return self._performance_expert_logic(service, action, reason, context)

        elif specialist == SpecialistType.SECURITY_SPECIALIST:
            return self._security_specialist_logic(service, action, reason, context)

        elif specialist == SpecialistType.BCM_CONSULTANT:
            return self._bcm_consultant_logic(service, action, reason, context)

        else:  # GENERAL_CONSULTANT
            return self._general_consultant_logic(service, action, reason, context)

    def _database_specialist_logic(
        self,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Database specialist recommendation logic (MVP simulation)"""
        recovery_attempts = context.get('recovery_attempts', 0)
        memory_percent = context.get('memory_percent', 0)

        if action == "restart":
            if recovery_attempts >= 2:
                return {
                    'specialist': SpecialistType.DATABASE_SPECIALIST.value,
                    'recommendation': 'investigate_before_restart',
                    'reasoning': 'Multiple restart attempts detected. Should investigate root cause before restarting again.',
                    'confidence': 0.85,
                    'suggested_actions': ['check_query_logs', 'analyze_slow_queries', 'review_schema']
                }
            elif memory_percent > 90:
                return {
                    'specialist': SpecialistType.DATABASE_SPECIALIST.value,
                    'recommendation': 'approve_restart',
                    'reasoning': 'High memory usage (>90%). Restart likely to resolve issue.',
                    'confidence': 0.90,
                    'suggested_actions': ['restart', 'monitor_memory', 'consider_scaling']
                }
            else:
                return {
                    'specialist': SpecialistType.DATABASE_SPECIALIST.value,
                    'recommendation': 'approve_restart',
                    'reasoning': 'Restart appears safe for database service.',
                    'confidence': 0.80,
                    'suggested_actions': ['restart', 'monitor_recovery']
                }

        return {
            'specialist': SpecialistType.DATABASE_SPECIALIST.value,
            'recommendation': 'needs_review',
            'reasoning': f'Action "{action}" requires careful review for database service.',
            'confidence': 0.60,
            'suggested_actions': ['manual_review']
        }

    def _performance_expert_logic(
        self,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Performance expert recommendation logic (MVP simulation)"""
        cpu_percent = context.get('cpu_percent', 0)
        memory_percent = context.get('memory_percent', 0)

        if cpu_percent > 85 or memory_percent > 85:
            return {
                'specialist': SpecialistType.PERFORMANCE_EXPERT.value,
                'recommendation': 'approve_restart',
                'reasoning': f'High resource usage detected (CPU: {cpu_percent}%, Memory: {memory_percent}%). Restart will likely improve performance.',
                'confidence': 0.85,
                'suggested_actions': ['restart', 'monitor_resources', 'consider_scaling']
            }
        else:
            return {
                'specialist': SpecialistType.PERFORMANCE_EXPERT.value,
                'recommendation': 'investigate_first',
                'reasoning': 'Performance issue may not require restart. Should investigate metrics first.',
                'confidence': 0.75,
                'suggested_actions': ['check_metrics', 'analyze_bottlenecks']
            }

    def _security_specialist_logic(
        self,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Security specialist recommendation logic (MVP simulation)"""
        if 'breach' in reason.lower() or 'attack' in reason.lower():
            return {
                'specialist': SpecialistType.SECURITY_SPECIALIST.value,
                'recommendation': 'escalate_immediately',
                'reasoning': 'Potential security incident detected. Requires immediate human review.',
                'confidence': 0.95,
                'suggested_actions': ['isolate_service', 'security_audit', 'incident_response']
            }
        else:
            return {
                'specialist': SpecialistType.SECURITY_SPECIALIST.value,
                'recommendation': 'approve_with_monitoring',
                'reasoning': 'Action appears safe from security perspective. Monitor for anomalies.',
                'confidence': 0.80,
                'suggested_actions': [action, 'monitor_security_logs']
            }

    def _bcm_consultant_logic(
        self,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """BCM consultant recommendation logic (MVP simulation)"""
        recovery_attempts = context.get('recovery_attempts', 0)
        downtime_seconds = context.get('downtime_seconds', 0)

        if recovery_attempts >= 3:
            return {
                'specialist': SpecialistType.BCM_CONSULTANT.value,
                'recommendation': 'escalate',
                'reasoning': f'Multiple recovery attempts ({recovery_attempts}) failed. Pattern indicates deeper issue requiring human intervention.',
                'confidence': 0.90,
                'suggested_actions': ['escalate_to_human', 'root_cause_analysis', 'failover_consideration']
            }
        elif downtime_seconds > 300:  # 5 minutes
            return {
                'specialist': SpecialistType.BCM_CONSULTANT.value,
                'recommendation': 'approve_urgent',
                'reasoning': f'Extended downtime ({downtime_seconds}s) detected. Urgent action needed to meet RTO.',
                'confidence': 0.85,
                'suggested_actions': [action, 'failover_if_fails', 'notify_stakeholders']
            }
        else:
            return {
                'specialist': SpecialistType.BCM_CONSULTANT.value,
                'recommendation': 'approve_restart',
                'reasoning': 'From BCM perspective, restart is acceptable within RTO/RPO constraints.',
                'confidence': 0.80,
                'suggested_actions': [action, 'monitor_rto']
            }

    def _general_consultant_logic(
        self,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """General consultant recommendation logic (MVP simulation)"""
        return {
            'specialist': SpecialistType.GENERAL_CONSULTANT.value,
            'recommendation': 'approve_with_caution',
            'reasoning': 'No specific concerns identified. Proceeding with standard caution.',
            'confidence': 0.70,
            'suggested_actions': [action, 'monitor_outcome']
        }

    def _aggregate_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        service: str,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggregate recommendations from multiple specialists

        Args:
            recommendations: List of specialist recommendations
            service: Service name
            action: Proposed action
            context: Additional context

        Returns:
            Aggregated final recommendation
        """
        if not recommendations:
            return {
                'recommendation': 'needs_review',
                'reasoning': 'No specialist consultations available.',
                'confidence': 0.50,
                'specialists_consulted': [],
                'consensus': False
            }

        # Check for escalation recommendations
        escalate_votes = sum(
            1 for r in recommendations
            if 'escalate' in r.get('recommendation', '').lower()
        )

        if escalate_votes > 0:
            # Any escalation recommendation triggers escalation
            return {
                'recommendation': 'escalate',
                'reasoning': 'One or more specialists recommend escalation for human review.',
                'confidence': max(r.get('confidence', 0.5) for r in recommendations),
                'specialists_consulted': [r['specialist'] for r in recommendations],
                'consensus': escalate_votes == len(recommendations),
                'specialist_details': recommendations
            }

        # Count approve votes
        approve_votes = sum(
            1 for r in recommendations
            if 'approve' in r.get('recommendation', '').lower()
        )

        # Majority voting
        if approve_votes >= len(recommendations) / 2:
            avg_confidence = sum(r.get('confidence', 0.5) for r in recommendations) / len(recommendations)
            return {
                'recommendation': 'approve',
                'reasoning': f'{approve_votes}/{len(recommendations)} specialists recommend approval.',
                'confidence': avg_confidence,
                'specialists_consulted': [r['specialist'] for r in recommendations],
                'consensus': approve_votes == len(recommendations),
                'specialist_details': recommendations
            }
        else:
            # No consensus - needs review
            return {
                'recommendation': 'needs_review',
                'reasoning': 'No consensus among specialists. Requires additional review.',
                'confidence': 0.60,
                'specialists_consulted': [r['specialist'] for r in recommendations],
                'consensus': False,
                'specialist_details': recommendations
            }

    def _update_stats(
        self,
        specialists: List[SpecialistType],
        recommendation: Dict[str, Any]
    ) -> None:
        """Update consultation statistics"""
        self.stats['total_consultations'] += 1

        for specialist in specialists:
            self.stats['by_specialist'][specialist.value] += 1

        # Update average confidence
        current_avg = self.stats['avg_confidence']
        total = self.stats['total_consultations']
        new_confidence = recommendation.get('confidence', 0.5)
        self.stats['avg_confidence'] = (current_avg * (total - 1) + new_confidence) / total

    async def _log_consultation(
        self,
        service: str,
        action: str,
        reason: str,
        specialists: List[SpecialistType],
        recommendation: Dict[str, Any]
    ) -> None:
        """
        Log consultation for learning and analytics

        Args:
            service: Service name
            action: Proposed action
            reason: Reason for consultation
            specialists: Specialists consulted
            recommendation: Final recommendation
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': service,
            'action': action,
            'reason': reason,
            'specialists_consulted': [s.value for s in specialists],
            'recommendation': recommendation.get('recommendation'),
            'confidence': recommendation.get('confidence'),
            'consensus': recommendation.get('consensus')
        }

        logger.info(f"📊 Consultation logged: {log_entry}")

        # TODO: Store in database for pattern learning
        # TODO: Publish to EventBus for AI learning

    def get_stats(self) -> Dict[str, Any]:
        """Get consultation statistics"""
        return self.stats.copy()


# Convenience function for direct use
async def consult_infrastructure_decision(
    service: str,
    action: str,
    reason: str,
    context: Dict[str, Any],
    complexity: str = "medium"
) -> Dict[str, Any]:
    """
    Quick consultation function

    Args:
        service: Service name
        action: Proposed action
        reason: Reason for action
        context: Additional context
        complexity: Complexity level

    Returns:
        Consultation recommendation
    """
    api = InfrastructureConsultationAPI()
    return await api.consult(
        service=service,
        action=action,
        reason=reason,
        context=context,
        complexity=complexity
    )
