"""
EventBus Integration for Predictive Service

Handles all event subscriptions and publishing for prediction-related events.

Event Publishers (8+):
- prediction.forecast_generated
- prediction.model_updated
- prediction.anomaly_detected
- prediction.confidence_low
- prediction.trend_identified
- prediction.risk_calculated
- prediction.financial_impact_estimated
- prediction.rto_probability_calculated

Event Subscribers (5+):
- workflow.completed
- bia.completed
- incident.resolved
- case.approved
- risk.score_changed
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID

logger = logging.getLogger(__name__)


class PredictiveEventHandlers:
    """
    Centralized event handlers for Predictive Service

    Manages both publishing prediction events and subscribing to platform events
    to continuously improve prediction models.
    """

    def __init__(self, eventbus, journey_predictor=None, demand_forecaster=None):
        """
        Initialize event handlers

        Args:
            eventbus: EventBusService instance
            journey_predictor: JourneyPredictor instance (optional)
            demand_forecaster: DemandForecaster instance (optional)
        """
        self.eventbus = eventbus
        self.journey_predictor = journey_predictor
        self.demand_forecaster = demand_forecaster

        # Track model updates for learning
        self.model_update_count = 0
        self.learning_events_processed = 0

    # =====================================================
    # EVENT PUBLISHERS (8+)
    # =====================================================

    async def publish_forecast_generated(
        self,
        org_id: UUID,
        forecast_type: str,
        horizon_days: int,
        milestones_count: int,
        confidence: float,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Publish event when forecast is generated

        Triggered when: Journey predictions or demand forecasts are created
        """
        await self.eventbus.publish({
            'event_type': 'prediction.forecast_generated',
            'tenant_id': tenant_id,
            'data': {
                'org_id': str(org_id),
                'forecast_type': forecast_type,  # 'journey', 'demand', 'certification'
                'horizon_days': horizon_days,
                'milestones_count': milestones_count,
                'average_confidence': confidence,
                'generated_at': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            },
            'priority': 'normal'
        })

        logger.info(
            f"Published forecast_generated event: {forecast_type} for org {org_id}"
        )

    async def publish_model_updated(
        self,
        model_type: str,
        update_reason: str,
        training_samples: int,
        accuracy_improvement: float,
        tenant_id: str
    ):
        """
        Publish event when prediction model is updated

        Triggered when: ML models are retrained with new data
        """
        self.model_update_count += 1

        await self.eventbus.publish({
            'event_type': 'prediction.model_updated',
            'tenant_id': tenant_id,
            'data': {
                'model_type': model_type,  # 'journey', 'demand', 'similarity'
                'update_reason': update_reason,
                'training_samples': training_samples,
                'accuracy_improvement': accuracy_improvement,
                'update_number': self.model_update_count,
                'updated_at': datetime.utcnow().isoformat()
            },
            'priority': 'low'
        })

        logger.info(
            f"Published model_updated event: {model_type} "
            f"(improvement: {accuracy_improvement:.2%})"
        )

    async def publish_anomaly_detected(
        self,
        org_id: UUID,
        anomaly_type: str,
        severity: str,
        description: str,
        affected_predictions: list,
        tenant_id: str
    ):
        """
        Publish event when anomaly detected in predictions

        Triggered when: Unusual patterns or outliers detected in org journey
        """
        await self.eventbus.publish({
            'event_type': 'prediction.anomaly_detected',
            'tenant_id': tenant_id,
            'data': {
                'org_id': str(org_id),
                'anomaly_type': anomaly_type,  # 'delayed_milestone', 'unexpected_cost', 'low_progress'
                'severity': severity,  # 'low', 'medium', 'high', 'critical'
                'description': description,
                'affected_predictions': affected_predictions,
                'detected_at': datetime.utcnow().isoformat(),
                'requires_review': severity in ['high', 'critical']
            },
            'priority': 'high' if severity in ['high', 'critical'] else 'normal'
        })

        logger.warning(
            f"Published anomaly_detected event: {anomaly_type} "
            f"for org {org_id} (severity: {severity})"
        )

    async def publish_confidence_low(
        self,
        org_id: UUID,
        milestone: str,
        confidence: float,
        threshold: float,
        reason: str,
        tenant_id: str
    ):
        """
        Publish event when prediction confidence is below threshold

        Triggered when: Confidence score < threshold (e.g., < 0.5)
        """
        await self.eventbus.publish({
            'event_type': 'prediction.confidence_low',
            'tenant_id': tenant_id,
            'data': {
                'org_id': str(org_id),
                'milestone': milestone,
                'confidence': confidence,
                'threshold': threshold,
                'reason': reason,
                'similar_orgs_needed': True,
                'detected_at': datetime.utcnow().isoformat()
            },
            'priority': 'normal'
        })

        logger.info(
            f"Published confidence_low event: {milestone} for org {org_id} "
            f"(confidence: {confidence:.2f} < threshold: {threshold:.2f})"
        )

    async def publish_trend_identified(
        self,
        trend_type: str,
        description: str,
        affected_orgs: int,
        confidence: float,
        trend_data: Dict[str, Any],
        tenant_id: str
    ):
        """
        Publish event when new trend identified across organizations

        Triggered when: Pattern analysis reveals industry/regional trends
        """
        await self.eventbus.publish({
            'event_type': 'prediction.trend_identified',
            'tenant_id': tenant_id,
            'data': {
                'trend_type': trend_type,  # 'industry_acceleration', 'common_challenge', 'success_pattern'
                'description': description,
                'affected_orgs_count': affected_orgs,
                'confidence': confidence,
                'trend_data': trend_data,
                'identified_at': datetime.utcnow().isoformat()
            },
            'priority': 'normal'
        })

        logger.info(
            f"Published trend_identified event: {trend_type} "
            f"(affects {affected_orgs} orgs, confidence: {confidence:.2f})"
        )

    async def publish_risk_calculated(
        self,
        org_id: UUID,
        risk_type: str,
        risk_score: float,
        factors: list,
        mitigation_suggestions: list,
        tenant_id: str
    ):
        """
        Publish event when risk score calculated for prediction

        Triggered when: Risk assessment performed on journey predictions
        """
        await self.eventbus.publish({
            'event_type': 'prediction.risk_calculated',
            'tenant_id': tenant_id,
            'data': {
                'org_id': str(org_id),
                'risk_type': risk_type,  # 'timeline_delay', 'certification_failure', 'resource_shortage'
                'risk_score': risk_score,  # 0-1 scale
                'risk_level': self._get_risk_level(risk_score),
                'contributing_factors': factors,
                'mitigation_suggestions': mitigation_suggestions,
                'calculated_at': datetime.utcnow().isoformat()
            },
            'priority': 'high' if risk_score > 0.7 else 'normal'
        })

        logger.info(
            f"Published risk_calculated event: {risk_type} for org {org_id} "
            f"(score: {risk_score:.2f})"
        )

    async def publish_financial_impact_estimated(
        self,
        org_id: UUID,
        milestone: str,
        estimated_cost: Dict[str, Any],
        confidence: float,
        cost_drivers: list,
        tenant_id: str
    ):
        """
        Publish event when financial impact estimated

        Triggered when: Cost predictions calculated for milestones
        """
        await self.eventbus.publish({
            'event_type': 'prediction.financial_impact_estimated',
            'tenant_id': tenant_id,
            'data': {
                'org_id': str(org_id),
                'milestone': milestone,
                'estimated_cost': estimated_cost,
                'confidence': confidence,
                'cost_drivers': cost_drivers,
                'currency': estimated_cost.get('currency', 'USD'),
                'estimated_at': datetime.utcnow().isoformat()
            },
            'priority': 'normal'
        })

        logger.info(
            f"Published financial_impact_estimated event: {milestone} for org {org_id} "
            f"(${estimated_cost.get('estimated_min', 0)}-${estimated_cost.get('estimated_max', 0)})"
        )

    async def publish_rto_probability_calculated(
        self,
        org_id: UUID,
        target_rto_days: int,
        achievement_probability: float,
        current_trajectory: str,
        recommendations: list,
        tenant_id: str
    ):
        """
        Publish event when RTO achievement probability calculated

        Triggered when: Recovery Time Objective predictions analyzed
        """
        await self.eventbus.publish({
            'event_type': 'prediction.rto_probability_calculated',
            'tenant_id': tenant_id,
            'data': {
                'org_id': str(org_id),
                'target_rto_days': target_rto_days,
                'achievement_probability': achievement_probability,
                'current_trajectory': current_trajectory,  # 'on_track', 'at_risk', 'delayed'
                'recommendations': recommendations,
                'calculated_at': datetime.utcnow().isoformat()
            },
            'priority': 'high' if achievement_probability < 0.5 else 'normal'
        })

        logger.info(
            f"Published rto_probability_calculated event: org {org_id} "
            f"(target: {target_rto_days}d, probability: {achievement_probability:.2%})"
        )

    # =====================================================
    # EVENT SUBSCRIBERS (5+)
    # =====================================================

    async def subscribe_to_platform_events(self):
        """
        Subscribe to all platform events that improve predictions

        Call this during service startup
        """
        await self.eventbus.subscribe('workflow.completed', self.handle_workflow_completed)
        await self.eventbus.subscribe('bia.completed', self.handle_bia_completed)
        await self.eventbus.subscribe('incident.resolved', self.handle_incident_resolved)
        await self.eventbus.subscribe('case.approved', self.handle_case_approved)
        await self.eventbus.subscribe('risk.score_changed', self.handle_risk_score_changed)

        logger.info("Subscribed to 5+ platform events for learning")

    async def handle_workflow_completed(self, event_data: Dict[str, Any]):
        """
        Handle workflow completion to update success models

        Learns from: Actual completion times vs predictions
        """
        try:
            self.learning_events_processed += 1

            workflow_id = event_data.get('data', {}).get('workflow_id')
            org_id = event_data.get('data', {}).get('org_id')
            module = event_data.get('data', {}).get('module')
            duration_days = event_data.get('data', {}).get('duration_days')

            logger.info(
                f"Processing workflow.completed: org={org_id}, module={module}, "
                f"duration={duration_days} days"
            )

            # Update journey predictor model with actual data
            if self.journey_predictor and org_id and module and duration_days:
                await self._update_milestone_duration_model(
                    org_id=UUID(org_id),
                    milestone=module,
                    actual_duration=duration_days
                )

            # Check prediction accuracy
            await self._check_prediction_accuracy(
                org_id=UUID(org_id) if org_id else None,
                milestone=module,
                actual_duration=duration_days,
                tenant_id=event_data.get('tenant_id', 'default')
            )

        except Exception as e:
            logger.error(f"Error handling workflow.completed: {e}")

    async def handle_bia_completed(self, event_data: Dict[str, Any]):
        """
        Handle BIA completion to analyze patterns

        Learns from: BIA outcomes, critical processes identified
        """
        try:
            self.learning_events_processed += 1

            org_id = event_data.get('data', {}).get('org_id')
            critical_processes = event_data.get('data', {}).get('critical_processes', [])
            total_processes = event_data.get('data', {}).get('total_processes', 0)

            logger.info(
                f"Processing bia.completed: org={org_id}, "
                f"critical={len(critical_processes)}/{total_processes}"
            )

            # Analyze BIA complexity for future predictions
            if org_id:
                await self._analyze_bia_complexity(
                    org_id=UUID(org_id),
                    critical_count=len(critical_processes),
                    total_count=total_processes,
                    tenant_id=event_data.get('tenant_id', 'default')
                )

        except Exception as e:
            logger.error(f"Error handling bia.completed: {e}")

    async def handle_incident_resolved(self, event_data: Dict[str, Any]):
        """
        Handle incident resolution to improve predictions

        Learns from: Actual recovery times, incident patterns
        """
        try:
            self.learning_events_processed += 1

            incident_id = event_data.get('data', {}).get('incident_id')
            org_id = event_data.get('data', {}).get('org_id')
            resolution_time = event_data.get('data', {}).get('resolution_time_hours')
            incident_type = event_data.get('data', {}).get('incident_type')

            logger.info(
                f"Processing incident.resolved: org={org_id}, type={incident_type}, "
                f"resolution_time={resolution_time}h"
            )

            # Update RTO prediction models with actual incident data
            if org_id and resolution_time:
                await self._update_rto_models(
                    org_id=UUID(org_id),
                    incident_type=incident_type,
                    actual_resolution_hours=resolution_time,
                    tenant_id=event_data.get('tenant_id', 'default')
                )

        except Exception as e:
            logger.error(f"Error handling incident.resolved: {e}")

    async def handle_case_approved(self, event_data: Dict[str, Any]):
        """
        Handle case approval to learn from community

        Learns from: Approved community cases, best practices
        """
        try:
            self.learning_events_processed += 1

            case_id = event_data.get('data', {}).get('case_id')
            module = event_data.get('data', {}).get('module')
            industry = event_data.get('data', {}).get('industry')
            success_factors = event_data.get('data', {}).get('success_factors', [])

            logger.info(
                f"Processing case.approved: case={case_id}, module={module}, "
                f"industry={industry}"
            )

            # Add to pattern library for predictions
            await self._add_to_pattern_library(
                module=module,
                industry=industry,
                success_factors=success_factors,
                tenant_id=event_data.get('tenant_id', 'default')
            )

        except Exception as e:
            logger.error(f"Error handling case.approved: {e}")

    async def handle_risk_score_changed(self, event_data: Dict[str, Any]):
        """
        Handle risk score changes to adjust predictions

        Learns from: Risk assessment changes, trend shifts
        """
        try:
            self.learning_events_processed += 1

            org_id = event_data.get('data', {}).get('org_id')
            risk_type = event_data.get('data', {}).get('risk_type')
            old_score = event_data.get('data', {}).get('old_score')
            new_score = event_data.get('data', {}).get('new_score')

            logger.info(
                f"Processing risk.score_changed: org={org_id}, type={risk_type}, "
                f"{old_score} -> {new_score}"
            )

            # Adjust prediction confidence based on risk changes
            if org_id and abs(new_score - old_score) > 0.2:
                await self._adjust_prediction_confidence(
                    org_id=UUID(org_id),
                    risk_type=risk_type,
                    risk_delta=new_score - old_score,
                    tenant_id=event_data.get('tenant_id', 'default')
                )

        except Exception as e:
            logger.error(f"Error handling risk.score_changed: {e}")

    # =====================================================
    # HELPER METHODS
    # =====================================================

    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to level"""
        if risk_score >= 0.8:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'

    async def _update_milestone_duration_model(
        self,
        org_id: UUID,
        milestone: str,
        actual_duration: int
    ):
        """Update model with actual milestone duration"""
        logger.info(
            f"Updating duration model: {milestone} took {actual_duration} days "
            f"for org {org_id}"
        )
        # Would update ML model or database with actual vs predicted
        # This improves future predictions

    async def _check_prediction_accuracy(
        self,
        org_id: Optional[UUID],
        milestone: str,
        actual_duration: int,
        tenant_id: str
    ):
        """Check if prediction was accurate and publish results"""
        # Would compare actual vs predicted
        # If significantly different, publish anomaly event
        logger.debug(f"Checking prediction accuracy for {milestone}")

    async def _analyze_bia_complexity(
        self,
        org_id: UUID,
        critical_count: int,
        total_count: int,
        tenant_id: str
    ):
        """Analyze BIA complexity for future predictions"""
        complexity_ratio = critical_count / max(total_count, 1)

        logger.info(
            f"BIA complexity for org {org_id}: "
            f"{critical_count}/{total_count} = {complexity_ratio:.2%} critical"
        )

        # High complexity might indicate longer future phases
        if complexity_ratio > 0.5:
            await self.publish_trend_identified(
                trend_type='high_bia_complexity',
                description=f'Organization has high BIA complexity ({complexity_ratio:.0%} critical processes)',
                affected_orgs=1,
                confidence=0.85,
                trend_data={
                    'org_id': str(org_id),
                    'complexity_ratio': complexity_ratio,
                    'critical_count': critical_count
                },
                tenant_id=tenant_id
            )

    async def _update_rto_models(
        self,
        org_id: UUID,
        incident_type: str,
        actual_resolution_hours: float,
        tenant_id: str
    ):
        """Update RTO prediction models with actual incident data"""
        logger.info(
            f"Updating RTO models: {incident_type} resolved in "
            f"{actual_resolution_hours}h for org {org_id}"
        )
        # Would update RTO probability calculations

    async def _add_to_pattern_library(
        self,
        module: str,
        industry: str,
        success_factors: list,
        tenant_id: str
    ):
        """Add approved case patterns to prediction library"""
        logger.info(
            f"Adding pattern to library: {module} in {industry} "
            f"with {len(success_factors)} success factors"
        )
        # Would add to pattern database for similarity matching

    async def _adjust_prediction_confidence(
        self,
        org_id: UUID,
        risk_type: str,
        risk_delta: float,
        tenant_id: str
    ):
        """Adjust prediction confidence based on risk changes"""
        direction = "increased" if risk_delta > 0 else "decreased"

        logger.info(
            f"Risk {direction} for org {org_id}: {risk_type} "
            f"(delta: {risk_delta:+.2f})"
        )

        # Significant risk increases should lower confidence
        if risk_delta > 0.2:
            await self.publish_confidence_low(
                org_id=org_id,
                milestone=risk_type,
                confidence=0.6 - risk_delta,
                threshold=0.7,
                reason=f"Risk score increased significantly ({risk_delta:+.2f})",
                tenant_id=tenant_id
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get event handler statistics"""
        return {
            'model_updates': self.model_update_count,
            'learning_events_processed': self.learning_events_processed,
            'active_subscriptions': 5,
            'event_publishers': 8
        }
