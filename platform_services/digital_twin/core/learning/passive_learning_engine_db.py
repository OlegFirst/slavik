"""
Passive Learning Engine (Database-enabled)

PostgreSQL-backed version of Passive Learning Engine.
Uses LearningRepository for database operations.

Learns from platform interactions transparently:
- BIA completion
- Risk assessments
- Incident reports
- Training completion
- Document uploads

Accumulates insights over time without explicit data entry.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from storage.learning_repository import LearningRepository

logger = logging.getLogger(__name__)


# ============================================
# ENUMS
# ============================================

class LearningSource(str, Enum):
    """Sources of learning events"""
    BIA = "bia"
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT = "incident"
    TRAINING = "training"
    DOCUMENT = "document"


class InsightType(str, Enum):
    """Types of insights"""
    RISK_TOLERANCE = "risk_tolerance"
    DECISION_SPEED = "decision_speed"
    THOROUGHNESS = "thoroughness"
    ORGANIZATIONAL_CULTURE = "organizational_culture"
    COMMUNICATION_STYLE = "communication_style"
    RESPONSE_SPEED = "response_speed"
    LEARNING_ORIENTATION = "learning_orientation"
    KNOWLEDGE_LEVEL = "knowledge_level"
    ENGAGEMENT_LEVEL = "engagement_level"
    CONTROL_PREFERENCE = "control_preference"


# ============================================
# MODELS
# ============================================

class LearningEvent:
    """Learning event from platform interaction"""
    def __init__(
        self,
        event_id: str,
        twin_id: str,
        source: LearningSource,
        insights: Dict[str, Any],
        timestamp: datetime,
        confidence: float = 0.8
    ):
        self.event_id = event_id
        self.twin_id = twin_id
        self.source = source
        self.insights = insights
        self.timestamp = timestamp
        self.confidence = confidence


# ============================================
# PASSIVE LEARNING ENGINE (DB)
# ============================================

class PassiveLearningEngineDB:
    """
    Database-backed Passive Learning Engine

    Learns from platform interactions and accumulates insights
    """

    def __init__(
        self,
        db_session: AsyncSession,
        tenant_id: str
    ):
        """
        Initialize Passive Learning Engine

        Args:
            db_session: SQLAlchemy async session
            tenant_id: Tenant ID for multi-tenancy
        """
        self.repository = LearningRepository(db_session)
        self.tenant_id = tenant_id

        logger.info(f"Passive Learning Engine (DB) initialized for tenant: {tenant_id}")

    # ============================================
    # LEARNING HOOKS (Called by other services)
    # ============================================

    async def learn_from_bia(
        self,
        twin_id: str,
        bia_data: Dict[str, Any]
    ) -> LearningEvent:
        """
        Learn from BIA completion

        Args:
            twin_id: Twin ID
            bia_data: BIA data

        Returns:
            Learning event
        """
        logger.info(f"Processing BIA learning event for twin: {twin_id}")

        insights = {}

        # Extract critical functions
        if 'critical_functions' in bia_data:
            insights['critical_functions'] = bia_data['critical_functions']

        # Infer risk tolerance from RTO/RPO targets
        if 'rto_rpo' in bia_data:
            rto_values = [item.get('rto_hours', 24) for item in bia_data['rto_rpo']]
            avg_rto = sum(rto_values) / len(rto_values) if rto_values else 24

            if avg_rto < 4:
                insights['risk_tolerance'] = 'low'
                insights['recovery_time_hours'] = avg_rto
            elif avg_rto < 24:
                insights['risk_tolerance'] = 'medium'
                insights['recovery_time_hours'] = avg_rto
            else:
                insights['risk_tolerance'] = 'high'
                insights['recovery_time_hours'] = avg_rto

        # Analyze decision-making speed (based on BIA completion time)
        if 'completion_time_days' in bia_data:
            if bia_data['completion_time_days'] < 7:
                insights['decision_speed'] = 'fast'
            elif bia_data['completion_time_days'] < 30:
                insights['decision_speed'] = 'moderate'
            else:
                insights['decision_speed'] = 'slow'

        # Analyze thoroughness
        if 'details_provided' in bia_data:
            detail_score = bia_data['details_provided']
            if detail_score > 0.8:
                insights['thoroughness'] = 'high'
            elif detail_score > 0.5:
                insights['thoroughness'] = 'medium'
            else:
                insights['thoroughness'] = 'low'

        # Store event
        event = await self._create_event(
            twin_id,
            LearningSource.BIA,
            insights,
            bia_data
        )

        # Update insights
        await self._update_insights(twin_id, insights)

        return event

    async def learn_from_risk_assessment(
        self,
        twin_id: str,
        risk_data: Dict[str, Any]
    ) -> LearningEvent:
        """Learn from risk assessment"""
        logger.info(f"Processing risk assessment learning event for twin: {twin_id}")

        insights = {}

        # Analyze risk appetite
        if 'risk_scores' in risk_data:
            avg_risk = sum(risk_data['risk_scores']) / len(risk_data['risk_scores'])
            if avg_risk < 30:
                insights['risk_appetite'] = 'low'
            elif avg_risk < 70:
                insights['risk_appetite'] = 'medium'
            else:
                insights['risk_appetite'] = 'high'

        # Identify primary risk focus
        if 'risk_categories' in risk_data:
            # Most frequent category
            from collections import Counter
            counter = Counter(risk_data['risk_categories'])
            most_common = counter.most_common(1)
            if most_common:
                insights['primary_risk_focus'] = most_common[0][0]

        # Analyze control preference
        if 'control_types' in risk_data:
            tech_controls = sum(1 for c in risk_data['control_types'] if 'technical' in c.lower())
            org_controls = sum(1 for c in risk_data['control_types'] if 'organizational' in c.lower())

            if tech_controls > org_controls * 1.5:
                insights['control_preference'] = 'technical'
            elif org_controls > tech_controls * 1.5:
                insights['control_preference'] = 'organizational'
            else:
                insights['control_preference'] = 'balanced'

        event = await self._create_event(twin_id, LearningSource.RISK_ASSESSMENT, insights, risk_data)
        await self._update_insights(twin_id, insights)

        return event

    async def learn_from_incident(
        self,
        twin_id: str,
        incident_data: Dict[str, Any]
    ) -> LearningEvent:
        """Learn from incident report"""
        logger.info(f"Processing incident learning event for twin: {twin_id}")

        insights = {}

        # Analyze response speed
        if 'time_to_detection_hours' in incident_data and 'time_to_response_hours' in incident_data:
            total_time = incident_data['time_to_detection_hours'] + incident_data['time_to_response_hours']

            if total_time < 2:
                insights['response_speed'] = 'very_fast'
            elif total_time < 8:
                insights['response_speed'] = 'fast'
            elif total_time < 24:
                insights['response_speed'] = 'moderate'
            else:
                insights['response_speed'] = 'slow'

        # Analyze communication style from incident report
        if 'report_length' in incident_data and 'report_detail_score' in incident_data:
            if incident_data['report_detail_score'] > 0.7 and incident_data['report_length'] > 500:
                insights['communication_style'] = 'formal'
            else:
                insights['communication_style'] = 'informal'

        event = await self._create_event(twin_id, LearningSource.INCIDENT, insights, incident_data)
        await self._update_insights(twin_id, insights)

        return event

    async def learn_from_training(
        self,
        twin_id: str,
        training_data: Dict[str, Any]
    ) -> LearningEvent:
        """Learn from training completion"""
        logger.info(f"Processing training learning event for twin: {twin_id}")

        insights = {}

        # Analyze learning orientation
        if 'completion_rate' in training_data:
            if training_data['completion_rate'] > 0.8:
                insights['learning_orientation'] = 'high'
            elif training_data['completion_rate'] > 0.5:
                insights['learning_orientation'] = 'medium'
            else:
                insights['learning_orientation'] = 'low'

        # Identify knowledge gaps
        if 'failed_topics' in training_data and training_data['failed_topics']:
            insights['knowledge_gaps'] = training_data['failed_topics']

        # Analyze knowledge level
        if 'average_score' in training_data:
            if training_data['average_score'] > 0.8:
                insights['knowledge_level'] = 'high'
            elif training_data['average_score'] > 0.6:
                insights['knowledge_level'] = 'medium'
            else:
                insights['knowledge_level'] = 'low'

        # Analyze engagement
        if 'participation_rate' in training_data:
            if training_data['participation_rate'] > 0.7:
                insights['engagement_level'] = 'high'
            elif training_data['participation_rate'] > 0.4:
                insights['engagement_level'] = 'medium'
            else:
                insights['engagement_level'] = 'low'

        event = await self._create_event(twin_id, LearningSource.TRAINING, insights, training_data)
        await self._update_insights(twin_id, insights)

        return event

    async def learn_from_document(
        self,
        twin_id: str,
        document_data: Dict[str, Any]
    ) -> LearningEvent:
        """Learn from document upload"""
        logger.info(f"Processing document learning event for twin: {twin_id}")

        insights = {}

        # Analyze document types for organizational culture
        if 'document_type' in document_data:
            doc_type = document_data['document_type']
            if doc_type in ['policy', 'procedure', 'standard']:
                insights['organizational_culture_indicator'] = 'formal'
            elif doc_type in ['guide', 'checklist', 'quick_reference']:
                insights['organizational_culture_indicator'] = 'practical'

        event = await self._create_event(twin_id, LearningSource.DOCUMENT, insights, document_data)
        await self._update_insights(twin_id, insights)

        return event

    # ============================================
    # INSIGHTS ACCESS
    # ============================================

    async def get_insights(
        self,
        twin_id: str
    ) -> Dict[str, Any]:
        """
        Get all accumulated insights for twin

        Returns:
            Dictionary mapping insight_type -> value
        """
        return await self.repository.get_insights_dict(twin_id)

    async def get_insight(
        self,
        twin_id: str,
        insight_type: str
    ) -> Optional[Any]:
        """Get specific insight"""
        db_insight = await self.repository.get_insight(twin_id, insight_type)
        if not db_insight:
            return None

        return db_insight.insight_value

    async def get_learning_history(
        self,
        twin_id: str,
        source: Optional[LearningSource] = None,
        limit: int = 100
    ) -> List[LearningEvent]:
        """Get learning event history"""
        source_str = source.value if source else None

        db_events = await self.repository.get_events_for_twin(
            twin_id,
            source=source_str,
            limit=limit
        )

        # Convert to LearningEvent objects
        events = []
        for db_event in db_events:
            event = LearningEvent(
                event_id=db_event.event_id,
                twin_id=db_event.twin_id,
                source=LearningSource(db_event.source),
                insights=db_event.insights,
                timestamp=db_event.created_at,
                confidence=db_event.confidence or 0.8
            )
            events.append(event)

        return events

    # ============================================
    # PATTERN DETECTION
    # ============================================

    async def detect_patterns(
        self,
        twin_id: str
    ) -> Dict[str, Any]:
        """
        Detect behavioral patterns from learning history

        Returns:
            Dictionary of detected patterns
        """
        # Get all events
        events = await self.get_learning_history(twin_id, limit=500)

        patterns = {}

        # Pattern: Consistency in risk tolerance
        risk_tolerance_values = [
            e.insights.get('risk_tolerance')
            for e in events
            if 'risk_tolerance' in e.insights
        ]
        if len(risk_tolerance_values) >= 3:
            from collections import Counter
            most_common = Counter(risk_tolerance_values).most_common(1)[0]
            consistency = most_common[1] / len(risk_tolerance_values)
            patterns['risk_appetite_consistency'] = {
                'value': most_common[0],
                'consistency': consistency
            }

        # Pattern: Decision speed trend
        decision_speeds = [
            e.insights.get('decision_speed')
            for e in events
            if 'decision_speed' in e.insights
        ]
        if decision_speeds:
            from collections import Counter
            patterns['decision_speed_pattern'] = Counter(decision_speeds).most_common(1)[0][0]

        # Pattern: Knowledge trend
        knowledge_events = [e for e in events if e.source == LearningSource.TRAINING]
        if len(knowledge_events) >= 3:
            # Simple trend: comparing first half vs second half
            mid = len(knowledge_events) // 2
            first_half_knowledge = [
                e.insights.get('knowledge_level')
                for e in knowledge_events[:mid]
                if 'knowledge_level' in e.insights
            ]
            second_half_knowledge = [
                e.insights.get('knowledge_level')
                for e in knowledge_events[mid:]
                if 'knowledge_level' in e.insights
            ]

            if first_half_knowledge and second_half_knowledge:
                level_map = {'low': 1, 'medium': 2, 'high': 3}
                avg_first = sum(level_map.get(k, 2) for k in first_half_knowledge) / len(first_half_knowledge)
                avg_second = sum(level_map.get(k, 2) for k in second_half_knowledge) / len(second_half_knowledge)

                if avg_second > avg_first:
                    patterns['knowledge_trend'] = 'improving'
                elif avg_second < avg_first:
                    patterns['knowledge_trend'] = 'declining'
                else:
                    patterns['knowledge_trend'] = 'stable'

        return patterns

    # ============================================
    # STATISTICS
    # ============================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning engine statistics"""
        # Note: This should be async in real implementation
        return {
            'engine_type': 'database_backed',
            'tenant_id': self.tenant_id,
        }

    # ============================================
    # PRIVATE METHODS
    # ============================================

    async def _create_event(
        self,
        twin_id: str,
        source: LearningSource,
        insights: Dict[str, Any],
        raw_data: Dict[str, Any]
    ) -> LearningEvent:
        """Create learning event in database"""
        event_data = {
            'event_id': str(uuid4()),
            'twin_id': twin_id,
            'tenant_id': self.tenant_id,
            'source': source.value,
            'insights': insights,
            'raw_data': raw_data,
            'confidence': 0.8,
            'created_at': datetime.utcnow(),
        }

        db_event = await self.repository.create_event(event_data)

        return LearningEvent(
            event_id=db_event.event_id,
            twin_id=db_event.twin_id,
            source=LearningSource(db_event.source),
            insights=db_event.insights,
            timestamp=db_event.created_at,
            confidence=db_event.confidence or 0.8
        )

    async def _update_insights(
        self,
        twin_id: str,
        new_insights: Dict[str, Any]
    ):
        """Update accumulated insights (upsert)"""
        for insight_type, insight_value in new_insights.items():
            # Get existing insight
            existing = await self.repository.get_insight(twin_id, insight_type)

            if existing:
                # Update existing insight
                # Combine values if needed (for lists)
                if isinstance(insight_value, list) and isinstance(existing.insight_value, dict):
                    combined_value = existing.insight_value.copy()
                    if 'values' in combined_value:
                        combined_value['values'].extend(insight_value)
                    else:
                        combined_value = {'values': insight_value}
                    final_value = combined_value
                else:
                    final_value = {'value': insight_value}

                # Increment source count
                source_count = existing.source_event_count + 1
            else:
                # New insight
                if isinstance(insight_value, list):
                    final_value = {'values': insight_value}
                else:
                    final_value = {'value': insight_value}
                source_count = 1

            # Upsert
            await self.repository.upsert_insight({
                'id': str(uuid4()),
                'twin_id': twin_id,
                'tenant_id': self.tenant_id,
                'insight_type': insight_type,
                'insight_value': final_value,
                'confidence': 0.8,
                'source_event_count': source_count,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
