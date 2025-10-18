"""
Context Builder

Builds dynamic organizational context from accumulated learning insights.

Creates a rich, evolving profile that goes beyond static data:
- Organizational culture
- Decision patterns
- Risk appetite
- Communication style
- Operational patterns
- Knowledge gaps
- Historical behavior
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from .passive_learning_engine import PassiveLearningEngine, InsightType

logger = logging.getLogger(__name__)


# ============================================
# MODELS
# ============================================

class OrganizationContext(BaseModel):
    """Dynamic organizational context built from learning"""

    twin_id: str

    # Culture & Behavior
    organizational_culture: Optional[str] = None  # "formal_hierarchical", "informal_collaborative", etc.
    decision_speed: Optional[str] = None  # "fast", "moderate", "slow"
    thoroughness: Optional[str] = None  # "high", "medium", "low"
    learning_orientation: Optional[str] = None  # "high", "medium", "low"

    # Risk Profile
    risk_tolerance: Optional[str] = None  # "low", "medium", "high"
    risk_appetite: Optional[str] = None  # "conservative", "moderate", "aggressive"
    control_preference: Optional[str] = None  # "technical", "organizational", "balanced"

    # Communication
    communication_style: Optional[str] = None  # "formal", "informal"
    response_speed: Optional[str] = None  # "very_fast", "fast", "moderate", "slow"

    # Operational Patterns
    avg_rto_hours: Optional[float] = None
    dependency_count: Optional[int] = None
    primary_risk_focus: Optional[str] = None

    # Knowledge & Capability
    knowledge_level: Optional[str] = None  # "high", "medium", "low"
    knowledge_gaps: List[str] = Field(default_factory=list)
    engagement_level: Optional[str] = None  # "high", "medium", "low"

    # BCM Maturity Indicators
    critical_functions: List[str] = Field(default_factory=list)
    recovery_time_hours: Optional[float] = None

    # Patterns & Trends
    patterns: Dict[str, Any] = Field(default_factory=dict)
    trends: Dict[str, str] = Field(default_factory=dict)

    # Metadata
    total_events: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


# ============================================
# CONTEXT BUILDER
# ============================================

class ContextBuilder:
    """
    Builds rich organizational context from learning insights
    """

    def __init__(
        self,
        learning_engine: Optional[PassiveLearningEngine] = None
    ):
        """
        Initialize Context Builder

        Args:
            learning_engine: Passive learning engine
        """
        self.learning_engine = learning_engine or PassiveLearningEngine()

        logger.info("Context Builder initialized")

    # ============================================
    # PUBLIC API
    # ============================================

    async def build_context(self, twin_id: str) -> OrganizationContext:
        """
        Build complete organizational context

        Args:
            twin_id: Organization twin ID

        Returns:
            OrganizationContext with all available insights
        """
        logger.info(f"Building context for twin: {twin_id}")

        # Get all insights
        insights = await self.learning_engine.get_insights(twin_id)

        # Get patterns
        patterns = await self.learning_engine.detect_patterns(twin_id)

        # Get event history for confidence calculation
        events = await self.learning_engine.get_learning_history(twin_id)

        # Build context
        context = OrganizationContext(
            twin_id=twin_id,

            # Culture & Behavior
            organizational_culture=self._infer_culture(insights),
            decision_speed=insights.get('decision_speed'),
            thoroughness=insights.get('thoroughness'),
            learning_orientation=insights.get('learning_orientation'),

            # Risk Profile
            risk_tolerance=insights.get('risk_tolerance'),
            risk_appetite=self._get_consistent_value(insights, patterns, 'risk_appetite'),
            control_preference=insights.get('control_preference'),

            # Communication
            communication_style=insights.get('communication_style'),
            response_speed=insights.get('response_speed'),

            # Operational Patterns
            avg_rto_hours=insights.get('avg_rto_hours'),
            dependency_count=insights.get('dependency_count'),
            primary_risk_focus=insights.get('primary_risk_focus'),

            # Knowledge & Capability
            knowledge_level=insights.get('knowledge_level'),
            knowledge_gaps=insights.get('knowledge_gaps', []),
            engagement_level=insights.get('engagement_level'),

            # BCM Maturity
            critical_functions=insights.get('critical_functions', []),
            recovery_time_hours=insights.get('recovery_time_hours'),

            # Patterns & Trends
            patterns=patterns,
            trends=self._extract_trends(patterns),

            # Metadata
            total_events=len(events),
            last_updated=datetime.utcnow(),
            confidence_score=self._calculate_confidence(insights, events)
        )

        logger.info(
            f"Context built for {twin_id}: "
            f"{len(insights)} insights, confidence={context.confidence_score:.2f}"
        )

        return context

    async def get_context_summary(self, twin_id: str) -> Dict[str, Any]:
        """
        Get summarized context (for quick overview)

        Returns:
            Dictionary with key context points
        """
        context = await self.build_context(twin_id)

        summary = {
            'twin_id': twin_id,
            'culture': context.organizational_culture,
            'risk_profile': {
                'tolerance': context.risk_tolerance,
                'appetite': context.risk_appetite,
            },
            'decision_making': {
                'speed': context.decision_speed,
                'thoroughness': context.thoroughness,
            },
            'bcm_maturity': {
                'critical_functions_count': len(context.critical_functions),
                'avg_rto_hours': context.avg_rto_hours,
            },
            'knowledge': {
                'level': context.knowledge_level,
                'gaps_count': len(context.knowledge_gaps),
            },
            'confidence': context.confidence_score,
            'last_updated': context.last_updated.isoformat(),
        }

        return summary

    async def update_context_from_event(
        self,
        twin_id: str,
        event_data: Dict[str, Any],
        event_source: str
    ) -> OrganizationContext:
        """
        Update context from a new event

        Args:
            twin_id: Twin ID
            event_data: Event data
            event_source: Source type (bia, risk, incident, etc.)

        Returns:
            Updated context
        """
        # Process event through learning engine
        if event_source == 'bia':
            await self.learning_engine.learn_from_bia(twin_id, event_data)
        elif event_source == 'risk_assessment':
            await self.learning_engine.learn_from_risk_assessment(twin_id, event_data)
        elif event_source == 'incident':
            await self.learning_engine.learn_from_incident(twin_id, event_data)
        elif event_source == 'training':
            await self.learning_engine.learn_from_training(twin_id, event_data)
        elif event_source == 'document':
            await self.learning_engine.learn_from_document(twin_id, event_data)

        # Rebuild context
        return await self.build_context(twin_id)

    # ============================================
    # CONTEXT ANALYSIS
    # ============================================

    async def compare_contexts(
        self,
        twin_id_a: str,
        twin_id_b: str
    ) -> Dict[str, Any]:
        """
        Compare contexts of two organizations

        Returns:
            Comparison highlighting similarities and differences
        """
        context_a = await self.build_context(twin_id_a)
        context_b = await self.build_context(twin_id_b)

        comparison = {
            'similarities': [],
            'differences': [],
            'similarity_score': 0.0,
        }

        matches = 0
        total = 0

        # Compare key attributes
        comparisons = [
            ('organizational_culture', 'Organizational Culture'),
            ('risk_tolerance', 'Risk Tolerance'),
            ('risk_appetite', 'Risk Appetite'),
            ('decision_speed', 'Decision Speed'),
            ('communication_style', 'Communication Style'),
        ]

        for attr, label in comparisons:
            value_a = getattr(context_a, attr)
            value_b = getattr(context_b, attr)

            if value_a and value_b:
                total += 1
                if value_a == value_b:
                    matches += 1
                    comparison['similarities'].append(f"Both have {label}: {value_a}")
                else:
                    comparison['differences'].append(
                        f"{label}: {value_a} vs {value_b}"
                    )

        # Calculate similarity score
        comparison['similarity_score'] = matches / total if total > 0 else 0.0

        return comparison

    async def get_evolution(
        self,
        twin_id: str,
        time_period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze how organization context has evolved

        Args:
            twin_id: Twin ID
            time_period_days: Period to analyze

        Returns:
            Evolution analysis
        """
        # Get events in time period
        all_events = await self.learning_engine.get_learning_history(twin_id)

        # Filter by time period
        cutoff = datetime.utcnow().timestamp() - (time_period_days * 24 * 3600)
        recent_events = [
            e for e in all_events
            if e.timestamp.timestamp() >= cutoff
        ]

        evolution = {
            'period_days': time_period_days,
            'events_count': len(recent_events),
            'changes': [],
        }

        # Analyze changes in key metrics
        # TODO: Implement time-series analysis

        return evolution

    # ============================================
    # PRIVATE METHODS - INFERENCE
    # ============================================

    def _infer_culture(self, insights: Dict[str, Any]) -> Optional[str]:
        """
        Infer organizational culture from insights

        Possible cultures:
        - formal_hierarchical
        - informal_collaborative
        - data_driven
        - risk_averse
        - innovative
        """
        culture_indicators = []

        # Formal vs Informal
        comm_style = insights.get('communication_style')
        if comm_style == 'formal':
            culture_indicators.append('formal')
        elif comm_style == 'informal':
            culture_indicators.append('informal')

        # Risk-averse vs Risk-taking
        risk_appetite = insights.get('risk_appetite')
        if risk_appetite == 'low':
            culture_indicators.append('risk_averse')
        elif risk_appetite == 'high':
            culture_indicators.append('risk_taking')

        # Thoroughness → detail-oriented
        thoroughness = insights.get('thoroughness')
        if thoroughness == 'high':
            culture_indicators.append('detail_oriented')

        # Learning orientation → learning culture
        learning = insights.get('learning_orientation')
        if learning == 'high':
            culture_indicators.append('learning_focused')

        # Combine indicators
        if 'formal' in culture_indicators and 'risk_averse' in culture_indicators:
            return 'formal_risk_averse'
        elif 'informal' in culture_indicators and 'learning_focused' in culture_indicators:
            return 'informal_learning_focused'
        elif culture_indicators:
            return '_'.join(culture_indicators[:2])

        return None

    def _get_consistent_value(
        self,
        insights: Dict[str, Any],
        patterns: Dict[str, Any],
        key: str
    ) -> Optional[Any]:
        """
        Get value, preferring consistent pattern over latest insight

        Args:
            insights: Current insights
            patterns: Detected patterns
            key: Key to lookup

        Returns:
            Most reliable value
        """
        # Check if pattern exists with high consistency
        pattern_key = f"{key}_consistency"
        if pattern_key in patterns:
            pattern = patterns[pattern_key]
            if pattern.get('consistency', 0) > 0.7:  # 70% consistency threshold
                return pattern.get('value')

        # Fall back to latest insight
        return insights.get(key)

    def _extract_trends(self, patterns: Dict[str, Any]) -> Dict[str, str]:
        """Extract trends from patterns"""
        trends = {}

        # Knowledge trend
        if 'knowledge_trend' in patterns:
            trends['knowledge'] = patterns['knowledge_trend']

        # TODO: Add more trend extraction

        return trends

    def _calculate_confidence(
        self,
        insights: Dict[str, Any],
        events: List[Any]
    ) -> float:
        """
        Calculate confidence score for context

        Based on:
        - Number of insights
        - Number of events
        - Consistency of patterns
        """
        confidence = 0.0

        # More insights = higher confidence
        insight_count = len([v for v in insights.values() if v is not None])
        confidence += min(insight_count / 20.0, 0.4)  # Max 0.4 from insights

        # More events = higher confidence
        event_count = len(events)
        confidence += min(event_count / 50.0, 0.3)  # Max 0.3 from events

        # Diversity of sources
        sources = set(e.source for e in events)
        confidence += min(len(sources) / 6.0, 0.3)  # Max 0.3 from diversity (6 source types)

        return min(confidence, 1.0)

    # ============================================
    # CONTEXT RECOMMENDATIONS
    # ============================================

    async def get_recommendations(self, twin_id: str) -> List[Dict[str, str]]:
        """
        Get recommendations based on context

        Returns:
            List of recommendations
        """
        context = await self.build_context(twin_id)
        recommendations = []

        # Knowledge gaps
        if context.knowledge_gaps:
            recommendations.append({
                'type': 'training',
                'priority': 'high',
                'title': 'Address Knowledge Gaps',
                'description': f"Focus training on: {', '.join(context.knowledge_gaps[:3])}",
                'reason': f"Detected {len(context.knowledge_gaps)} knowledge gaps from training assessments"
            })

        # Low engagement
        if context.engagement_level == 'low':
            recommendations.append({
                'type': 'engagement',
                'priority': 'medium',
                'title': 'Improve Staff Engagement',
                'description': 'Consider more interactive BCM activities',
                'reason': 'Low engagement observed in training completion rates'
            })

        # High risk appetite but low controls
        if context.risk_appetite == 'high' and context.control_preference != 'technical':
            recommendations.append({
                'type': 'risk',
                'priority': 'high',
                'title': 'Review Risk Controls',
                'description': 'Consider implementing additional technical controls',
                'reason': 'High risk appetite detected but limited technical controls'
            })

        # Slow response speed
        if context.response_speed == 'slow':
            recommendations.append({
                'type': 'incident_response',
                'priority': 'high',
                'title': 'Improve Incident Response Time',
                'description': 'Review and streamline incident response procedures',
                'reason': 'Slow response times observed in incident reports'
            })

        # Low confidence score
        if context.confidence_score < 0.3:
            recommendations.append({
                'type': 'data_collection',
                'priority': 'low',
                'title': 'Increase Platform Usage',
                'description': 'More platform interactions will improve recommendations',
                'reason': f'Low confidence score ({context.confidence_score:.2f}) - need more data'
            })

        return recommendations

    # ============================================
    # STATISTICS
    # ============================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get context builder statistics"""
        return {
            'learning_engine_stats': self.learning_engine.get_statistics(),
        }
