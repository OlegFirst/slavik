"""
Infrastructure Failure Prevention Advisor

Predicts potential infrastructure failures and provides preventive recommendations
for Decision Center integration.

Features:
- Failure forecasting based on current metrics
- Trend analysis (CPU, memory, disk, network)
- Pattern detection (time-based failures, cascading failures)
- Preventive action recommendations
- RTO/RPO risk assessment
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class FailureType(Enum):
    """Types of predicted failures"""
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    CASCADING_FAILURE = "cascading_failure"
    CONFIGURATION_DRIFT = "configuration_drift"
    DEPENDENCY_FAILURE = "dependency_failure"
    UNKNOWN = "unknown"


@dataclass
class PreventiveInsight:
    """Preventive insight for infrastructure decision"""
    forecast: str  # 'high_risk_of_failure', 'moderate_risk', 'low_risk'
    failure_type: FailureType
    probability: float  # 0.0-1.0
    time_to_failure_hours: Optional[float]
    risk_level: RiskLevel
    reasoning: str
    preventive_actions: List[str]
    confidence: float
    metrics_analyzed: Dict[str, Any]
    rto_risk: str  # 'SAFE', 'WARNING', 'VIOLATION_IMMINENT'
    rpo_risk: str


class InfrastructurePreventionAdvisor:
    """
    Analyzes infrastructure metrics and predicts potential failures

    Provides preventive recommendations to Decision Center to avoid
    failures before they occur.

    MVP Implementation:
    - Heuristic-based trend analysis
    - Threshold detection
    - Pattern matching

    Future:
    - ML-based prediction models
    - Historical pattern learning
    - Cross-service correlation analysis
    """

    def __init__(
        self,
        eventbus: Optional[Any] = None,
        enable_logging: bool = True
    ):
        """
        Initialize prevention advisor

        Args:
            eventbus: EventBus for event integration
            enable_logging: Enable prediction logging
        """
        self.eventbus = eventbus
        self.enable_logging = enable_logging

        # Prediction statistics
        self.stats = {
            'predictions_made': 0,
            'high_risk_predictions': 0,
            'preventive_actions_recommended': 0,
            'avg_confidence': 0.0
        }

        logger.info("Infrastructure Prevention Advisor initialized")

    async def predict_failure_risk(
        self,
        service: str,
        context: Dict[str, Any],
        horizon_hours: int = 24
    ) -> PreventiveInsight:
        """
        Predict failure risk for service

        Args:
            service: Service name
            context: Current metrics and context
            horizon_hours: Prediction horizon in hours

        Returns:
            PreventiveInsight with predictions and recommendations
        """
        # Extract metrics
        metrics = self._extract_metrics(context)

        # Analyze trends
        trends = self._analyze_trends(service, metrics, context)

        # Detect patterns
        patterns = self._detect_failure_patterns(service, context)

        # Calculate failure probability
        failure_prob, failure_type = self._calculate_failure_probability(
            trends, patterns, metrics
        )

        # Estimate time to failure
        time_to_failure = self._estimate_time_to_failure(
            trends, failure_prob, horizon_hours
        )

        # Determine risk level
        risk_level = self._determine_risk_level(
            failure_prob, time_to_failure, context
        )

        # Generate preventive actions
        preventive_actions = self._generate_preventive_actions(
            failure_type, trends, patterns, metrics, risk_level
        )

        # Assess RTO/RPO risk
        rto_risk, rpo_risk = self._assess_rto_rpo_risk(
            service, context, time_to_failure
        )

        # Build reasoning
        reasoning = self._build_reasoning(
            failure_type, failure_prob, trends, patterns, time_to_failure
        )

        # Determine forecast category
        forecast = self._categorize_forecast(risk_level, failure_prob)

        # Calculate confidence
        confidence = self._calculate_confidence(trends, patterns, metrics)

        # Create insight
        insight = PreventiveInsight(
            forecast=forecast,
            failure_type=failure_type,
            probability=failure_prob,
            time_to_failure_hours=time_to_failure,
            risk_level=risk_level,
            reasoning=reasoning,
            preventive_actions=preventive_actions,
            confidence=confidence,
            metrics_analyzed=metrics,
            rto_risk=rto_risk,
            rpo_risk=rpo_risk
        )

        # Update stats
        self._update_stats(insight)

        # Log prediction
        if self.enable_logging:
            await self._log_prediction(service, insight)

        return insight

    def _extract_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metrics from context"""
        return {
            'cpu_percent': context.get('cpu_percent', 0),
            'memory_percent': context.get('memory_percent', 0),
            'disk_percent': context.get('disk_percent', 0),
            'network_errors': context.get('network_errors', 0),
            'recovery_attempts': context.get('recovery_attempts', 0),
            'downtime_seconds': context.get('downtime_seconds', 0),
            'recent_failures': context.get('recent_failures', []),
            'response_time_ms': context.get('response_time_ms', 0),
            'error_rate': context.get('error_rate', 0.0)
        }

    def _analyze_trends(
        self,
        service: str,
        metrics: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Analyze metric trends

        Returns:
            Dict with trend direction for each metric
        """
        trends = {}

        # CPU trend
        cpu = metrics['cpu_percent']
        if cpu > 90:
            trends['cpu'] = 'critical_high'
        elif cpu > 80:
            trends['cpu'] = 'high_increasing'
        elif cpu > 70:
            trends['cpu'] = 'moderate_increasing'
        else:
            trends['cpu'] = 'normal'

        # Memory trend
        memory = metrics['memory_percent']
        if memory > 95:
            trends['memory'] = 'critical_high'
        elif memory > 85:
            trends['memory'] = 'high_increasing'
        elif memory > 75:
            trends['memory'] = 'moderate_increasing'
        else:
            trends['memory'] = 'normal'

        # Error rate trend
        error_rate = metrics['error_rate']
        if error_rate > 0.1:  # 10%
            trends['errors'] = 'critical_high'
        elif error_rate > 0.05:  # 5%
            trends['errors'] = 'high_increasing'
        elif error_rate > 0.02:  # 2%
            trends['errors'] = 'moderate'
        else:
            trends['errors'] = 'normal'

        # Response time trend
        response_time = metrics['response_time_ms']
        if response_time > 5000:  # 5 seconds
            trends['response_time'] = 'critical_slow'
        elif response_time > 3000:  # 3 seconds
            trends['response_time'] = 'degraded'
        elif response_time > 1000:  # 1 second
            trends['response_time'] = 'slightly_degraded'
        else:
            trends['response_time'] = 'normal'

        return trends

    def _detect_failure_patterns(
        self,
        service: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Detect failure patterns

        Returns:
            List of detected patterns
        """
        patterns = []

        recovery_attempts = context.get('recovery_attempts', 0)
        recent_failures = context.get('recent_failures', [])

        # Repeated restart pattern
        if recovery_attempts >= 2:
            patterns.append('repeated_restarts')

        # Frequent failures pattern
        if len(recent_failures) >= 3:
            patterns.append('frequent_failures')

        # Time-based pattern detection (simplified)
        # In production, would analyze timestamps
        if len(recent_failures) >= 5:
            patterns.append('failure_storm')

        # Cascading failure detection
        if context.get('dependent_services_failing'):
            patterns.append('cascading_failure')

        return patterns

    def _calculate_failure_probability(
        self,
        trends: Dict[str, str],
        patterns: List[str],
        metrics: Dict[str, Any]
    ) -> tuple[float, FailureType]:
        """
        Calculate failure probability

        Returns:
            (probability, failure_type)
        """
        base_probability = 0.1  # 10% baseline

        # Trend-based probability increase
        critical_trends = sum(
            1 for trend in trends.values()
            if 'critical' in trend
        )
        high_trends = sum(
            1 for trend in trends.values()
            if 'high' in trend
        )

        base_probability += critical_trends * 0.25
        base_probability += high_trends * 0.15

        # Pattern-based probability increase
        if 'repeated_restarts' in patterns:
            base_probability += 0.20
        if 'frequent_failures' in patterns:
            base_probability += 0.15
        if 'failure_storm' in patterns:
            base_probability += 0.30
        if 'cascading_failure' in patterns:
            base_probability += 0.25

        # Cap at 0.95
        probability = min(base_probability, 0.95)

        # Determine failure type
        failure_type = self._determine_failure_type(trends, patterns, metrics)

        return probability, failure_type

    def _determine_failure_type(
        self,
        trends: Dict[str, str],
        patterns: List[str],
        metrics: Dict[str, Any]
    ) -> FailureType:
        """Determine most likely failure type"""

        # Cascading failure has highest priority
        if 'cascading_failure' in patterns:
            return FailureType.CASCADING_FAILURE

        # Resource exhaustion
        if trends.get('cpu') == 'critical_high' or trends.get('memory') == 'critical_high':
            return FailureType.RESOURCE_EXHAUSTION

        # Performance degradation
        if trends.get('response_time') in ['critical_slow', 'degraded']:
            return FailureType.PERFORMANCE_DEGRADATION

        # Repeated failures → unknown issue
        if 'repeated_restarts' in patterns or 'frequent_failures' in patterns:
            return FailureType.UNKNOWN

        return FailureType.UNKNOWN

    def _estimate_time_to_failure(
        self,
        trends: Dict[str, str],
        probability: float,
        horizon_hours: int
    ) -> Optional[float]:
        """
        Estimate time until failure

        Returns:
            Hours until failure, or None if low risk
        """
        if probability < 0.3:
            return None  # Low risk, no imminent failure

        # Critical trends → very soon
        if any('critical' in trend for trend in trends.values()):
            return 1.0  # 1 hour

        # High trends → within a few hours
        if any('high' in trend for trend in trends.values()):
            if probability > 0.7:
                return 2.0
            else:
                return 6.0

        # Moderate → within horizon
        return horizon_hours * 0.5

    def _determine_risk_level(
        self,
        probability: float,
        time_to_failure: Optional[float],
        context: Dict[str, Any]
    ) -> RiskLevel:
        """Determine overall risk level"""

        # Critical: High probability and imminent
        if probability >= 0.75 and time_to_failure and time_to_failure <= 2:
            return RiskLevel.CRITICAL

        # High: High probability or very soon
        if probability >= 0.65 or (time_to_failure and time_to_failure <= 4):
            return RiskLevel.HIGH

        # Moderate: Medium probability
        if probability >= 0.40:
            return RiskLevel.MODERATE

        # Low: Low probability
        return RiskLevel.LOW

    def _generate_preventive_actions(
        self,
        failure_type: FailureType,
        trends: Dict[str, str],
        patterns: List[str],
        metrics: Dict[str, Any],
        risk_level: RiskLevel
    ) -> List[str]:
        """Generate preventive action recommendations"""
        actions = []

        if risk_level == RiskLevel.CRITICAL:
            actions.append("️  URGENT: Immediate action required to prevent failure")

        # Type-specific actions
        if failure_type == FailureType.RESOURCE_EXHAUSTION:
            if trends.get('memory') in ['critical_high', 'high_increasing']:
                actions.append("Scale up memory immediately")
                actions.append("Investigate memory leaks")
                actions.append("Enable memory profiling")

            if trends.get('cpu') in ['critical_high', 'high_increasing']:
                actions.append("Scale horizontally (add instances)")
                actions.append("Optimize CPU-intensive operations")
                actions.append("Review query performance")

        elif failure_type == FailureType.PERFORMANCE_DEGRADATION:
            actions.append("Review slow query logs")
            actions.append("Check database indexes")
            actions.append("Analyze connection pool usage")
            actions.append("Consider caching frequently accessed data")

        elif failure_type == FailureType.CASCADING_FAILURE:
            actions.append("Isolate failing dependencies")
            actions.append("Enable circuit breakers")
            actions.append("Implement graceful degradation")
            actions.append("Prepare failover procedures")

        # Pattern-specific actions
        if 'repeated_restarts' in patterns:
            actions.append("STOP automatic restarts - investigate root cause first")
            actions.append("Enable debug logging")
            actions.append("Capture heap dump before next restart")

        if 'frequent_failures' in patterns:
            actions.append("Escalate to engineering team for deep analysis")
            actions.append("Review application logs for error patterns")

        # General preventive actions
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            actions.append("Notify on-call team")
            actions.append("Prepare rollback procedures")
            actions.append("Increase monitoring frequency")

        if not actions:
            actions.append("Continue monitoring metrics closely")

        return actions

    def _assess_rto_rpo_risk(
        self,
        service: str,
        context: Dict[str, Any],
        time_to_failure: Optional[float]
    ) -> tuple[str, str]:
        """Assess RTO/RPO risk"""

        downtime = context.get('downtime_seconds', 0)

        # RTO assessment
        if downtime > 300:  # 5 minutes
            rto_risk = "VIOLATION_IMMINENT"
        elif downtime > 180:  # 3 minutes
            rto_risk = "WARNING"
        else:
            rto_risk = "SAFE"

        # RPO assessment (simplified)
        # In production, would check last backup time
        if time_to_failure and time_to_failure < 1:
            rpo_risk = "WARNING"
        else:
            rpo_risk = "SAFE"

        return rto_risk, rpo_risk

    def _build_reasoning(
        self,
        failure_type: FailureType,
        probability: float,
        trends: Dict[str, str],
        patterns: List[str],
        time_to_failure: Optional[float]
    ) -> str:
        """Build human-readable reasoning"""

        parts = []

        # Main prediction
        if probability >= 0.75:
            parts.append(f"High risk ({int(probability * 100)}%) of {failure_type.value}")
        elif probability >= 0.50:
            parts.append(f"Moderate risk ({int(probability * 100)}%) of {failure_type.value}")
        else:
            parts.append(f"Low risk ({int(probability * 100)}%) of failure")

        # Time estimate
        if time_to_failure:
            if time_to_failure < 2:
                parts.append(f"expected within {int(time_to_failure * 60)} minutes")
            else:
                parts.append(f"expected within {int(time_to_failure)} hours")

        # Key trends
        critical_trends = [k for k, v in trends.items() if 'critical' in v]
        if critical_trends:
            parts.append(f"Critical: {', '.join(critical_trends)}")

        # Key patterns
        if patterns:
            parts.append(f"Patterns detected: {', '.join(patterns)}")

        return ". ".join(parts) + "."

    def _categorize_forecast(
        self,
        risk_level: RiskLevel,
        probability: float
    ) -> str:
        """Categorize forecast for Decision Center"""

        if risk_level == RiskLevel.CRITICAL:
            return 'critical_risk_of_failure'
        elif risk_level == RiskLevel.HIGH:
            return 'high_risk_of_failure'
        elif risk_level == RiskLevel.MODERATE:
            return 'moderate_risk'
        else:
            return 'low_risk'

    def _calculate_confidence(
        self,
        trends: Dict[str, str],
        patterns: List[str],
        metrics: Dict[str, Any]
    ) -> float:
        """Calculate prediction confidence"""

        base_confidence = 0.60

        # More data → higher confidence
        if metrics['recovery_attempts'] > 0:
            base_confidence += 0.10

        if len(patterns) > 0:
            base_confidence += 0.10

        # Critical metrics → higher confidence
        critical_count = sum(1 for v in trends.values() if 'critical' in v)
        base_confidence += critical_count * 0.05

        return min(base_confidence, 0.95)

    def _update_stats(self, insight: PreventiveInsight) -> None:
        """Update prediction statistics"""
        self.stats['predictions_made'] += 1

        if insight.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.stats['high_risk_predictions'] += 1

        self.stats['preventive_actions_recommended'] += len(insight.preventive_actions)

        # Update average confidence
        total = self.stats['predictions_made']
        current_avg = self.stats['avg_confidence']
        self.stats['avg_confidence'] = (
            (current_avg * (total - 1) + insight.confidence) / total
        )

    async def _log_prediction(
        self,
        service: str,
        insight: PreventiveInsight
    ) -> None:
        """Log prediction for learning"""

        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': service,
            'forecast': insight.forecast,
            'failure_type': insight.failure_type.value,
            'probability': insight.probability,
            'risk_level': insight.risk_level.value,
            'confidence': insight.confidence,
            'preventive_actions_count': len(insight.preventive_actions)
        }

        logger.info(f" Prediction logged: {log_entry}")

        # TODO: Store in database for ML training
        # TODO: Publish to EventBus for learning

    def get_stats(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        return self.stats.copy()


# Convenience function
async def predict_infrastructure_failure(
    service: str,
    context: Dict[str, Any],
    horizon_hours: int = 24
) -> PreventiveInsight:
    """
    Quick prediction function

    Args:
        service: Service name
        context: Current metrics and context
        horizon_hours: Prediction horizon

    Returns:
        PreventiveInsight with predictions
    """
    advisor = InfrastructurePreventionAdvisor()
    return await advisor.predict_failure_risk(
        service=service,
        context=context,
        horizon_hours=horizon_hours
    )
