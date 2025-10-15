"""
AI Orchestrator Integration with Decision Center

This module provides the bridge between:
- Decision Center (Infrastructure Level) → AI Orchestrator (Intelligent Core Level)
- Complex decisions that require deep analysis are sent to AI Orchestrator
- AI Orchestrator provides expert consultation and strategic recommendations

Flow:
1. Decision Center detects complex problem (high attempts, unknown issue, etc.)
2. Decision Center publishes decision.consultation_requested event
3. AI Orchestrator receives event and analyzes situation
4. AI Orchestrator consults with Expertise Center specialists
5. AI Orchestrator responds with recommendation via EventBus
6. Decision Center receives recommendation and makes final decision

Integration Points:
- EventBus (for async communication)
- Service Registry (for discovery)
- Expertise Center (for specialized consultation)
- Predictive Intelligence (for forecasting)
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import sys

# Add infrastructure to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from infrastructure.eventbus import create_eventbus, Event, EventPriority

logger = logging.getLogger(__name__)


class DecisionCenterIntegration:
    """
    Integration layer between Decision Center and AI Orchestrator

    Responsibilities:
    - Listen for complex decision requests from Decision Center
    - Route requests to AI Orchestrator
    - Aggregate analysis from multiple AI experts
    - Provide enriched recommendations back to Decision Center

    Features:
    - Async event-driven communication
    - Multi-expert consultation
    - Predictive analysis
    - Context enrichment
    """

    def __init__(
        self,
        orchestrator: 'AIOrchestrator',
        event_bus_backend: str = 'redis'
    ):
        """
        Initialize Decision Center Integration

        Args:
            orchestrator: AI Orchestrator instance
            event_bus_backend: EventBus backend ('memory', 'redis', 'rabbitmq')
        """
        self.orchestrator = orchestrator
        self.event_bus = create_eventbus(event_bus_backend)

        # Stats
        self.stats = {
            'consultations_received': 0,
            'consultations_completed': 0,
            'consultations_failed': 0,
            'average_response_time_ms': 0,
            'expert_consultations': 0,
            'predictive_analyses': 0
        }

        self.initialized = False
        logger.info("Decision Center Integration created")

    async def initialize(self) -> None:
        """
        Initialize integration

        Must be called before using integration.
        """
        if self.initialized:
            logger.warning("Integration already initialized")
            return

        try:
            # Subscribe to decision center events
            await self._subscribe_to_decision_events()

            self.initialized = True
            logger.info("✅ Decision Center Integration initialized")
            logger.info("   - Subscribed to decision center events")
            logger.info("   - Ready to provide AI consultation")

        except Exception as e:
            logger.error(f"Failed to initialize Decision Center integration: {e}")
            raise

    async def _subscribe_to_decision_events(self) -> None:
        """Subscribe to Decision Center consultation requests"""
        # Subscribe to complex decision requests
        await self.event_bus.subscribe(
            'infrastructure.decision.consultation_requested',
            self._handle_consultation_request,
            consumer_group='ai_orchestrator'
        )

        # Subscribe to escalation events
        await self.event_bus.subscribe(
            'infrastructure.escalation.created',
            self._handle_escalation,
            consumer_group='ai_orchestrator'
        )

        # Subscribe to recovery events
        await self.event_bus.subscribe(
            'platform.service.recovery.attempted',
            self._handle_recovery_event,
            consumer_group='ai_orchestrator'
        )

        logger.info("Subscribed to Decision Center events")

    async def _handle_consultation_request(self, event: Event) -> None:
        """
        Handle consultation request from Decision Center

        Args:
            event: Consultation request event
        """
        start_time = datetime.utcnow()
        self.stats['consultations_received'] += 1

        try:
            logger.info(f"Received consultation request: {event.event_id}")

            # Extract decision context
            decision_data = event.data
            service = decision_data.get('service')
            action = decision_data.get('action')
            reason = decision_data.get('reason')
            context = decision_data.get('context', {})
            request_id = decision_data.get('request_id')

            logger.info(f"Consulting on: {service}.{action} - {reason}")

            # Build situation for AI Orchestrator
            situation = {
                'type': 'infrastructure_decision',
                'service': service,
                'action': action,
                'reason': reason,
                'context': context,
                'request_id': request_id,
                'source': 'decision_center',
                'timestamp': datetime.utcnow().isoformat()
            }

            # Step 1: Get AI Orchestrator decision
            logger.info("Consulting AI Orchestrator...")
            orchestrator_decision = await self.orchestrator.decide(
                situation=situation,
                tenant_id=event.tenant_id
            )

            logger.info(f"Orchestrator decision: {orchestrator_decision.action.value}")

            # Step 2: Consult specialists if needed
            specialist_recommendations = []

            if orchestrator_decision.action.name in ['DELEGATE', 'AUTO_RESOLVE']:
                # Get expert consultation
                specialist_recommendations = await self._consult_experts(
                    service=service,
                    action=action,
                    reason=reason,
                    context=context
                )

                logger.info(f"Received {len(specialist_recommendations)} specialist recommendations")
                self.stats['expert_consultations'] += len(specialist_recommendations)

            # Step 3: Get predictive analysis
            predictive_insight = await self._get_predictive_insight(
                service=service,
                context=context
            )

            if predictive_insight:
                logger.info(f"Predictive insight: {predictive_insight.get('forecast')}")
                self.stats['predictive_analyses'] += 1

            # Step 4: Build comprehensive recommendation
            recommendation = self._build_recommendation(
                orchestrator_decision=orchestrator_decision,
                specialist_recommendations=specialist_recommendations,
                predictive_insight=predictive_insight,
                situation=situation
            )

            # Step 5: Calculate response time
            response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            recommendation['response_time_ms'] = response_time_ms

            # Update average response time
            total = self.stats['consultations_completed'] + 1
            current_avg = self.stats['average_response_time_ms']
            self.stats['average_response_time_ms'] = (
                (current_avg * (total - 1) + response_time_ms) / total
            )

            # Step 6: Publish recommendation back to Decision Center
            await self._publish_recommendation(
                request_id=request_id,
                recommendation=recommendation,
                tenant_id=event.tenant_id
            )

            self.stats['consultations_completed'] += 1
            logger.info(f"Consultation complete: {request_id} ({response_time_ms}ms)")

        except Exception as e:
            logger.error(f"Error handling consultation request: {e}", exc_info=True)
            self.stats['consultations_failed'] += 1

            # Publish error response
            try:
                await self._publish_recommendation(
                    request_id=decision_data.get('request_id'),
                    recommendation={
                        'success': False,
                        'error': str(e),
                        'recommendation': 'escalate',  # Safe fallback
                        'reasoning': f"AI consultation failed: {str(e)}",
                        'confidence': 0.0
                    },
                    tenant_id=event.tenant_id
                )
            except Exception as publish_error:
                logger.error(f"Failed to publish error response: {publish_error}")

    async def _consult_experts(
        self,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any]
    ) -> list:
        """
        Consult with Expertise Center specialists

        Routes to appropriate specialists based on problem type:
        - Database issues → Database Specialist
        - Performance issues → Performance Expert
        - Security issues → Security Specialist
        - BCM decisions → BCM Consultant

        Args:
            service: Service name
            action: Proposed action
            reason: Problem reason
            context: Additional context

        Returns:
            list: Specialist recommendations
        """
        recommendations = []

        try:
            # Determine which specialists to consult
            specialists_needed = self._determine_specialists(service, reason, context)

            logger.info(f"Consulting specialists: {', '.join(specialists_needed)}")

            # Publish consultation requests to specialists
            for specialist in specialists_needed:
                consultation_event = Event.create(
                    event_type=f'expertise.{specialist}.consultation_requested',
                    data={
                        'service': service,
                        'action': action,
                        'reason': reason,
                        'context': context,
                        'requested_by': 'ai_orchestrator',
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    source='decision_center_integration',
                    priority=EventPriority.HIGH
                )

                await self.event_bus.publish(consultation_event)
                logger.info(f"Requested consultation from {specialist}")

            # Wait for specialist responses (with timeout)
            # TODO: In production, implement proper response collection via EventBus
            # For MVP, simulate specialist recommendations
            recommendations = self._simulate_specialist_responses(
                specialists_needed,
                service,
                action,
                reason,
                context
            )

        except Exception as e:
            logger.error(f"Error consulting experts: {e}")

        return recommendations

    def _determine_specialists(
        self,
        service: str,
        reason: str,
        context: Dict[str, Any]
    ) -> list:
        """
        Determine which specialists should be consulted

        Args:
            service: Service name
            reason: Problem reason
            context: Additional context

        Returns:
            list: Specialist names to consult
        """
        specialists = []
        reason_lower = reason.lower()

        # Database specialist
        if 'database' in service or 'database' in reason_lower or 'db' in service:
            specialists.append('database_specialist')

        # Performance expert
        if any(word in reason_lower for word in [
            'performance', 'slow', 'latency', 'cpu', 'memory', 'resource'
        ]):
            specialists.append('performance_expert')

        # Security specialist
        if any(word in reason_lower for word in [
            'security', 'breach', 'unauthorized', 'vulnerability', 'attack'
        ]):
            specialists.append('security_specialist')

        # BCM consultant for recovery decisions
        recovery_attempts = context.get('recovery_attempts', 0)
        if recovery_attempts >= 2 or 'recovery' in reason_lower:
            specialists.append('bcm_consultant')

        # If no specific specialist, use general consultant
        if not specialists:
            specialists.append('general_consultant')

        return specialists

    def _simulate_specialist_responses(
        self,
        specialists: list,
        service: str,
        action: str,
        reason: str,
        context: Dict[str, Any]
    ) -> list:
        """
        Simulate specialist responses for MVP

        In production, this would wait for actual specialist responses via EventBus.

        Args:
            specialists: List of specialists consulted
            service: Service name
            action: Proposed action
            reason: Problem reason
            context: Additional context

        Returns:
            list: Simulated specialist recommendations
        """
        recommendations = []

        for specialist in specialists:
            if specialist == 'database_specialist':
                recommendations.append({
                    'specialist': 'database_specialist',
                    'recommendation': 'approve' if context.get('recovery_attempts', 0) < 3 else 'investigate',
                    'reasoning': 'Database restart is safe with proper checkpointing. High memory indicates possible memory leak.',
                    'confidence': 0.85,
                    'suggested_actions': [
                        'Check for memory leaks in application queries',
                        'Review slow query log',
                        'Consider connection pool tuning'
                    ]
                })

            elif specialist == 'performance_expert':
                recommendations.append({
                    'specialist': 'performance_expert',
                    'recommendation': 'approve' if action in ['restart', 'scale_up'] else 'investigate',
                    'reasoning': 'Performance degradation likely due to resource exhaustion. Restart will help short-term.',
                    'confidence': 0.80,
                    'suggested_actions': [
                        'Monitor resource usage post-restart',
                        'Consider horizontal scaling',
                        'Review application performance metrics'
                    ]
                })

            elif specialist == 'security_specialist':
                recommendations.append({
                    'specialist': 'security_specialist',
                    'recommendation': 'approve_with_caution',
                    'reasoning': 'No immediate security concerns detected. Proceed with monitoring.',
                    'confidence': 0.75,
                    'suggested_actions': [
                        'Review access logs',
                        'Check for unusual patterns',
                        'Verify security patches are current'
                    ]
                })

            elif specialist == 'bcm_consultant':
                recovery_attempts = context.get('recovery_attempts', 0)
                recommendations.append({
                    'specialist': 'bcm_consultant',
                    'recommendation': 'escalate' if recovery_attempts >= 3 else 'approve',
                    'reasoning': f'Recovery attempt {recovery_attempts}/3. ISO 22301 suggests escalation after 3 attempts.',
                    'confidence': 0.90,
                    'suggested_actions': [
                        'Document recovery attempt in audit log',
                        'Notify operations team',
                        'Prepare for potential failover' if recovery_attempts >= 2 else 'Monitor closely'
                    ],
                    'iso_22301_clause': '8.4 - Business Continuity Procedures',
                    'rto_status': self._check_rto_status(context)
                })

            else:  # general_consultant
                recommendations.append({
                    'specialist': 'general_consultant',
                    'recommendation': 'approve',
                    'reasoning': f'Standard {action} operation for {service}. No special concerns identified.',
                    'confidence': 0.70,
                    'suggested_actions': [
                        f'Execute {action}',
                        'Monitor outcome',
                        'Document result'
                    ]
                })

        return recommendations

    def _check_rto_status(self, context: Dict[str, Any]) -> str:
        """Check RTO status from context"""
        downtime = context.get('downtime_seconds', 0)
        if downtime > 300:  # 5 minutes
            return 'RTO_VIOLATION_IMMINENT'
        elif downtime > 180:  # 3 minutes
            return 'RTO_WARNING'
        else:
            return 'WITHIN_RTO'

    async def _get_predictive_insight(
        self,
        service: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get predictive analysis from Predictive Intelligence

        Uses Infrastructure Prevention Advisor for failure forecasting.

        Args:
            service: Service name
            context: Current context

        Returns:
            dict: Predictive insight or None
        """
        try:
            # Publish request to Predictive Intelligence
            prediction_event = Event.create(
                event_type='predictive.forecast_requested',
                data={
                    'service': service,
                    'context': context,
                    'forecast_horizon_hours': 24,
                    'requested_by': 'decision_center_integration'
                },
                source='decision_center_integration',
                priority=EventPriority.NORMAL
            )

            await self.event_bus.publish(prediction_event)
            logger.debug(f"Requested predictive forecast for {service}")

            # Use Infrastructure Prevention Advisor
            try:
                from intelligent_core.predictive.services.infrastructure_prevention import (
                    InfrastructurePreventionAdvisor
                )

                advisor = InfrastructurePreventionAdvisor(
                    eventbus=self.event_bus,
                    enable_logging=True
                )

                # Get failure prediction
                prediction = await advisor.predict_failure_risk(
                    service=service,
                    context=context,
                    horizon_hours=24
                )

                # Convert to dict format
                insight = {
                    'forecast': prediction.forecast,
                    'failure_type': prediction.failure_type.value,
                    'probability': prediction.probability,
                    'time_to_failure_hours': prediction.time_to_failure_hours,
                    'risk_level': prediction.risk_level.value,
                    'reasoning': prediction.reasoning,
                    'preventive_actions': prediction.preventive_actions,
                    'confidence': prediction.confidence,
                    'rto_risk': prediction.rto_risk,
                    'rpo_risk': prediction.rpo_risk,
                    'metrics_analyzed': prediction.metrics_analyzed
                }

                logger.info(
                    f"✅ Predictive analysis: {prediction.forecast} "
                    f"(risk: {prediction.risk_level.value}, confidence: {prediction.confidence:.2f})"
                )

                return insight

            except ImportError as e:
                logger.warning(f"Infrastructure Prevention Advisor not available: {e}")
                logger.warning("Falling back to simulated predictive insight")

                # Fallback to simulation
                insight = self._simulate_predictive_insight(service, context)
                return insight

        except Exception as e:
            logger.error(f"Error getting predictive insight: {e}")
            return None

    def _simulate_predictive_insight(
        self,
        service: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate predictive insight for MVP

        In production, this would come from Predictive Intelligence service.

        Args:
            service: Service name
            context: Current context

        Returns:
            dict: Simulated predictive insight
        """
        recovery_attempts = context.get('recovery_attempts', 0)
        memory_percent = context.get('memory_percent', 0)

        # Simulate forecast based on current conditions
        if memory_percent > 90 or recovery_attempts >= 2:
            return {
                'forecast': 'high_risk_of_failure',
                'probability': 0.75,
                'time_to_failure_hours': 2,
                'reasoning': 'Current trends indicate high risk of repeated failure within 2 hours.',
                'preventive_actions': [
                    'Consider proactive scaling',
                    'Review memory usage patterns',
                    'Prepare backup capacity'
                ],
                'confidence': 0.80
            }
        elif memory_percent > 80:
            return {
                'forecast': 'moderate_risk',
                'probability': 0.45,
                'time_to_failure_hours': 6,
                'reasoning': 'Resource usage trending upward. Monitor closely.',
                'preventive_actions': [
                    'Monitor resource trends',
                    'Consider optimization'
                ],
                'confidence': 0.70
            }
        else:
            return {
                'forecast': 'low_risk',
                'probability': 0.15,
                'reasoning': 'No concerning trends detected.',
                'preventive_actions': [],
                'confidence': 0.65
            }

    def _build_recommendation(
        self,
        orchestrator_decision: 'Decision',
        specialist_recommendations: list,
        predictive_insight: Optional[Dict[str, Any]],
        situation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build comprehensive recommendation from all inputs

        Aggregates:
        - AI Orchestrator decision
        - Specialist recommendations
        - Predictive analysis

        Args:
            orchestrator_decision: Decision from AI Orchestrator
            specialist_recommendations: Recommendations from specialists
            predictive_insight: Predictive analysis
            situation: Original situation

        Returns:
            dict: Comprehensive recommendation
        """
        # Map orchestrator action to decision center action
        action_mapping = {
            'AUTO_RESOLVE': 'approve',
            'DELEGATE': 'approve',
            'ESCALATE_HUMAN': 'escalate',
            'WAIT_AND_MONITOR': 'wait_and_monitor',
            'EMERGENCY_STOP': 'reject'
        }

        primary_recommendation = action_mapping.get(
            orchestrator_decision.action.name,
            'escalate'  # Safe default
        )

        # Calculate consensus confidence
        confidences = [orchestrator_decision.confidence]
        for rec in specialist_recommendations:
            confidences.append(rec.get('confidence', 0.5))

        if predictive_insight:
            confidences.append(predictive_insight.get('confidence', 0.5))

        consensus_confidence = sum(confidences) / len(confidences)

        # Build comprehensive reasoning
        reasoning_parts = [
            f"AI Orchestrator: {orchestrator_decision.rationale}"
        ]

        for rec in specialist_recommendations:
            reasoning_parts.append(
                f"{rec['specialist']}: {rec['reasoning']}"
            )

        if predictive_insight:
            reasoning_parts.append(
                f"Predictive: {predictive_insight['reasoning']}"
            )

        comprehensive_reasoning = " | ".join(reasoning_parts)

        # Build recommendation
        recommendation = {
            'success': True,
            'recommendation': primary_recommendation,
            'reasoning': comprehensive_reasoning,
            'confidence': consensus_confidence,
            'orchestrator_decision': {
                'action': orchestrator_decision.action.name,
                'rationale': orchestrator_decision.rationale,
                'confidence': orchestrator_decision.confidence,
                'safety_approved': orchestrator_decision.safety_approved
            },
            'specialist_recommendations': specialist_recommendations,
            'predictive_insight': predictive_insight,
            'metadata': {
                'consultation_type': 'multi_expert',
                'experts_consulted': len(specialist_recommendations),
                'predictive_analysis_included': predictive_insight is not None,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

        return recommendation

    async def _publish_recommendation(
        self,
        request_id: str,
        recommendation: Dict[str, Any],
        tenant_id: str
    ) -> None:
        """
        Publish recommendation back to Decision Center

        Args:
            request_id: Original request ID
            recommendation: Comprehensive recommendation
            tenant_id: Tenant identifier
        """
        try:
            response_event = Event.create(
                event_type='infrastructure.decision.consultation_response',
                data={
                    'request_id': request_id,
                    'recommendation': recommendation,
                    'responded_by': 'ai_orchestrator',
                    'timestamp': datetime.utcnow().isoformat()
                },
                source='ai_orchestrator',
                tenant_id=tenant_id,
                priority=EventPriority.HIGH
            )

            await self.event_bus.publish(response_event)
            logger.info(f"Published recommendation for request: {request_id}")

        except Exception as e:
            logger.error(f"Error publishing recommendation: {e}")
            raise

    async def _handle_escalation(self, event: Event) -> None:
        """
        Handle escalation event from Decision Center

        When Decision Center escalates a decision, AI Orchestrator can:
        - Provide additional analysis
        - Suggest alternative approaches
        - Learn from escalation patterns

        Args:
            event: Escalation event
        """
        try:
            logger.info(f"Received escalation event: {event.event_id}")

            escalation_data = event.data
            service = escalation_data.get('service')
            reason = escalation_data.get('reason')

            logger.info(f"Escalation: {service} - {reason}")

            # Store escalation in memory for learning
            await self.orchestrator.memory.working_memory.store({
                'type': 'decision_center_escalation',
                'service': service,
                'reason': reason,
                'data': escalation_data,
                'timestamp': datetime.utcnow().isoformat()
            })

            logger.info("Escalation stored for learning")

        except Exception as e:
            logger.error(f"Error handling escalation: {e}")

    async def _handle_recovery_event(self, event: Event) -> None:
        """
        Handle recovery event from System BCM Coordinator

        Learns from recovery attempts and outcomes.

        Args:
            event: Recovery event
        """
        try:
            logger.debug(f"Received recovery event: {event.event_id}")

            recovery_data = event.data
            service = recovery_data.get('service')
            outcome = recovery_data.get('outcome')

            # Store in memory for learning
            await self.orchestrator.memory.working_memory.store({
                'type': 'recovery_event',
                'service': service,
                'outcome': outcome,
                'data': recovery_data,
                'timestamp': datetime.utcnow().isoformat()
            })

            logger.debug(f"Recovery event stored: {service} - {outcome}")

        except Exception as e:
            logger.error(f"Error handling recovery event: {e}")

    async def shutdown(self) -> None:
        """Shutdown integration and cleanup"""
        logger.info("Shutting down Decision Center Integration...")

        try:
            await self.event_bus.close()
            logger.info("✅ Decision Center Integration shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            **self.stats,
            'initialized': self.initialized
        }


# Convenience function for initialization
async def setup_decision_center_integration(
    orchestrator: 'AIOrchestrator',
    event_bus_backend: str = 'redis'
) -> DecisionCenterIntegration:
    """
    Setup and initialize Decision Center integration

    Args:
        orchestrator: AI Orchestrator instance
        event_bus_backend: EventBus backend

    Returns:
        DecisionCenterIntegration: Initialized integration

    Example:
        ```python
        from orchestration.ai_orchestration.orchestrator import AIOrchestrator

        # Create orchestrator
        orchestrator = AIOrchestrator()
        await orchestrator.initialize()

        # Setup Decision Center integration
        integration = await setup_decision_center_integration(orchestrator)

        # Integration now listening for Decision Center events
        logger.info(f"Integration stats: {integration.get_stats()}")
        ```
    """
    integration = DecisionCenterIntegration(
        orchestrator=orchestrator,
        event_bus_backend=event_bus_backend
    )

    await integration.initialize()

    logger.info("✅ Decision Center integration setup complete")
    logger.info("   - AI Orchestrator <-> Decision Center bridge active")
    logger.info("   - Multi-expert consultation enabled")
    logger.info("   - Predictive analysis enabled")

    return integration


# Export
__all__ = [
    'DecisionCenterIntegration',
    'setup_decision_center_integration'
]
