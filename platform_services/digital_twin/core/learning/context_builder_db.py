"""
Context Builder (Database-enabled)

PostgreSQL-backed version of Context Builder.
Uses LearningRepository for database operations.

Builds dynamic organizational context from accumulated learning insights:
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

from sqlalchemy.ext.asyncio import AsyncSession

from .passive_learning_engine_db import PassiveLearningEngineDB, InsightType
from storage.learning_repository import LearningRepository

logger = logging.getLogger(__name__)


# ============================================
# MODELS
# ============================================

class OrganizationContext(BaseModel):
    """Dynamic organizational context built from learning"""

    twin_id: str

    # Culture & Behavior
    organizational_culture: Optional[str] = None
    decision_speed: Optional[str] = None
    thoroughness: Optional[str] = None
    learning_orientation: Optional[str] = None

    # Risk Profile
    risk_tolerance: Optional[str] = None
    risk_appetite: Optional[str] = None
    control_preference: Optional[str] = None

    # Communication
    communication_style: Optional[str] = None
    response_speed: Optional[str] = None

    # Operational Patterns
    avg_rto_hours: Optional[float] = None
    dependency_count: Optional[int] = None
    primary_risk_focus: Optional[str] = None

    # Knowledge & Capability
    knowledge_level: Optional[str] = None
    knowledge_gaps: List[str] = Field(default_factory=list)
    engagement_level: Optional[str] = None

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
# CONTEXT BUILDER (DB)
# ============================================

class ContextBuilderDB:
    """
    Database-backed Context Builder

    Builds rich organizational context from learning insights
    """

    def __init__(
        self,
        db_session: AsyncSession,
        tenant_id: str,
        learning_engine: Optional[PassiveLearningEngineDB] = None
    ):
        """
        Initialize Context Builder

        Args:
            db_session: SQLAlchemy async session
            tenant_id: Tenant ID for multi-tenancy
            learning_engine: Passive learning engine
        """
        self.repository = LearningRepository(db_session)
        self.tenant_id = tenant_id
        self.learning_engine = learning_engine or PassiveLearningEngineDB(db_session, tenant_id)

        logger.info(f"Context Builder (DB) initialized for tenant: {tenant_id}")

    # ============================================
    # PUBLIC API
    # ============================================

    async def build_context(
        self,
        twin_id: str,
        use_cache: bool = True
    ) -> OrganizationContext:
        """
        Build complete organizational context

        Args:
            twin_id: Organization twin ID
            use_cache: Use cached context if available

        Returns:
            OrganizationContext with all available insights
        """
        logger.info(f"Building context for twin: {twin_id}")

        # Try to get from cache first
        if use_cache:
            cached = await self.repository.get_context(twin_id)
            if cached and (datetime.utcnow() - cached.last_updated).seconds < 3600:  # 1 hour cache
                logger.info(f"Using cached context for twin: {twin_id}")
                return self._db_context_to_pydantic(cached)

        # Build fresh context
        insights = await self.learning_engine.get_insights(twin_id)
        patterns = await self.learning_engine.detect_patterns(twin_id)
        events = await self.learning_engine.get_learning_history(twin_id)

        # Extract values from insights (handle both dict and simple values)
        def get_insight_value(key: str) -> Any:
            value = insights.get(key)
            if isinstance(value, dict) and 'value' in value:
                return value['value']
            elif isinstance(value, dict) and 'values' in value:
                return value['values']
            return value

        # Build context
        context = OrganizationContext(
            twin_id=twin_id,

            # Culture & Behavior
            organizational_culture=self._infer_culture(insights),
            decision_speed=get_insight_value('decision_speed'),
            thoroughness=get_insight_value('thoroughness'),
            learning_orientation=get_insight_value('learning_orientation'),

            # Risk Profile
            risk_tolerance=get_insight_value('risk_tolerance'),
            risk_appetite=self._get_consistent_value(insights, patterns, 'risk_appetite'),
            control_preference=get_insight_value('control_preference'),

            # Communication
            communication_style=get_insight_value('communication_style'),
            response_speed=get_insight_value('response_speed'),

            # Operational Patterns
            avg_rto_hours=get_insight_value('recovery_time_hours'),
            dependency_count=None,  # TODO: extract from BIA data
            primary_risk_focus=get_insight_value('primary_risk_focus'),

            # Knowledge & Capability
            knowledge_level=get_insight_value('knowledge_level'),
            knowledge_gaps=get_insight_value('knowledge_gaps') or [],
            engagement_level=get_insight_value('engagement_level'),

            # BCM Maturity
            critical_functions=get_insight_value('critical_functions') or [],
            recovery_time_hours=get_insight_value('recovery_time_hours'),

            # Patterns & Trends
            patterns=patterns,
            trends=self._extract_trends(patterns),

            # Metadata
            total_events=len(events),
            last_updated=datetime.utcnow(),
            confidence_score=self._calculate_confidence(insights, events)
        )

        # Store in cache
        await self._cache_context(context)

        logger.info(
            f"Context built for {twin_id}: "
            f"{len(insights)} insights, confidence={context.confidence_score:.2f}"
        )

        return context

    async def get_context_summary(
        self,
        twin_id: str
    ) -> Dict[str, Any]:
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

        # Rebuild context (without cache)
        return await self.build_context(twin_id, use_cache=False)

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
        from datetime import timedelta

        # Get events in time period
        cutoff = datetime.utcnow() - timedelta(days=time_period_days)
        all_events = await self.learning_engine.get_learning_history(twin_id, limit=500)

        recent_events = [
            e for e in all_events
            if e.timestamp >= cutoff
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
    # CONTEXT RECOMMENDATIONS
    # ============================================

    async def get_recommendations(
        self,
        twin_id: str
    ) -> List[Dict[str, str]]:
        """
        Get recommendations based on context

        Returns:
            List of actionable recommendations
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
            'context_builder_type': 'database_backed',
            'tenant_id': self.tenant_id,
            'learning_engine_stats': self.learning_engine.get_statistics(),
        }

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

        # Helper to get value from insight dict
        def get_value(key: str) -> Any:
            value = insights.get(key)
            if isinstance(value, dict) and 'value' in value:
                return value['value']
            return value

        # Formal vs Informal
        comm_style = get_value('communication_style')
        if comm_style == 'formal':
            culture_indicators.append('formal')
        elif comm_style == 'informal':
            culture_indicators.append('informal')

        # Risk-averse vs Risk-taking
        risk_appetite = get_value('risk_appetite')
        if risk_appetite == 'low':
            culture_indicators.append('risk_averse')
        elif risk_appetite == 'high':
            culture_indicators.append('risk_taking')

        # Thoroughness → detail-oriented
        thoroughness = get_value('thoroughness')
        if thoroughness == 'high':
            culture_indicators.append('detail_oriented')

        # Learning orientation → learning culture
        learning = get_value('learning_orientation')
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
            if isinstance(pattern, dict) and pattern.get('consistency', 0) > 0.7:
                return pattern.get('value')

        # Fall back to latest insight
        value = insights.get(key)
        if isinstance(value, dict) and 'value' in value:
            return value['value']
        return value

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
        sources = set(e.source.value for e in events)
        confidence += min(len(sources) / 5.0, 0.3)  # Max 0.3 from diversity (5 source types)

        return min(confidence, 1.0)

    async def _cache_context(self, context: OrganizationContext):
        """Store context in database cache"""
        context_data = {
            'twin_id': context.twin_id,
            'tenant_id': self.tenant_id,
            'organizational_culture': context.organizational_culture,
            'decision_speed': context.decision_speed,
            'thoroughness': context.thoroughness,
            'learning_orientation': context.learning_orientation,
            'risk_tolerance': context.risk_tolerance,
            'risk_appetite': context.risk_appetite,
            'control_preference': context.control_preference,
            'communication_style': context.communication_style,
            'response_speed': context.response_speed,
            'avg_rto_hours': context.avg_rto_hours,
            'dependency_count': context.dependency_count,
            'primary_risk_focus': context.primary_risk_focus,
            'knowledge_level': context.knowledge_level,
            'knowledge_gaps': context.knowledge_gaps,
            'engagement_level': context.engagement_level,
            'critical_functions': context.critical_functions,
            'recovery_time_hours': context.recovery_time_hours,
            'patterns': context.patterns,
            'trends': context.trends,
            'total_events': context.total_events,
            'confidence_score': context.confidence_score,
            'last_updated': datetime.utcnow(),
            'created_at': datetime.utcnow(),
        }

        await self.repository.upsert_context(context_data)

    def _db_context_to_pydantic(self, db_context) -> OrganizationContext:
        """Convert database model to Pydantic model"""
        return OrganizationContext(
            twin_id=db_context.twin_id,
            organizational_culture=db_context.organizational_culture,
            decision_speed=db_context.decision_speed,
            thoroughness=db_context.thoroughness,
            learning_orientation=db_context.learning_orientation,
            risk_tolerance=db_context.risk_tolerance,
            risk_appetite=db_context.risk_appetite,
            control_preference=db_context.control_preference,
            communication_style=db_context.communication_style,
            response_speed=db_context.response_speed,
            avg_rto_hours=db_context.avg_rto_hours,
            dependency_count=db_context.dependency_count,
            primary_risk_focus=db_context.primary_risk_focus,
            knowledge_level=db_context.knowledge_level,
            knowledge_gaps=db_context.knowledge_gaps or [],
            engagement_level=db_context.engagement_level,
            critical_functions=db_context.critical_functions or [],
            recovery_time_hours=db_context.recovery_time_hours,
            patterns=db_context.patterns or {},
            trends=db_context.trends or {},
            total_events=db_context.total_events,
            last_updated=db_context.last_updated,
            confidence_score=db_context.confidence_score,
        )
