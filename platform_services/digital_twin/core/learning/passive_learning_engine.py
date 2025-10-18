"""
Passive Learning Engine

Learns about organizations from their platform interactions without explicit data entry.

Learning Sources:
- BIA completion → critical functions, RTO/RPO, dependencies, decision patterns
- Risk assessment → risk perception, risk appetite, mitigation preferences
- Incident reports → response patterns, communication style, recovery speed
- Training completion → knowledge gaps, learning preferences
- Document uploads → communication style, organizational structure
- Exercise/drills → preparedness level, team coordination
- Plan updates → planning approach, update frequency
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================
# MODELS
# ============================================

class LearningSource(str, Enum):
    """Source of learning event"""
    BIA = "bia"
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT_REPORT = "incident_report"
    TRAINING = "training"
    EXERCISE = "exercise"
    PLAN_UPDATE = "plan_update"
    DOCUMENT_UPLOAD = "document_upload"
    AUDIT = "audit"
    SIMULATION = "simulation"


class LearningEvent(BaseModel):
    """A learning event from platform interaction"""
    event_id: str
    source: LearningSource
    twin_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    insights: Dict[str, Any] = Field(default_factory=dict)


class InsightType(str, Enum):
    """Type of insight learned"""
    CRITICAL_FUNCTION = "critical_function"
    DEPENDENCY = "dependency"
    RISK_PERCEPTION = "risk_perception"
    RISK_APPETITE = "risk_appetite"
    DECISION_PATTERN = "decision_pattern"
    RESPONSE_PATTERN = "response_pattern"
    COMMUNICATION_STYLE = "communication_style"
    KNOWLEDGE_GAP = "knowledge_gap"
    ORGANIZATIONAL_CULTURE = "organizational_culture"
    OPERATIONAL_PATTERN = "operational_pattern"


# ============================================
# PASSIVE LEARNING ENGINE
# ============================================

class PassiveLearningEngine:
    """
    Engine that learns from platform interactions
    """

    def __init__(self):
        """Initialize Passive Learning Engine"""
        # In-memory storage (TODO: replace with database)
        self._events: Dict[str, List[LearningEvent]] = {}  # twin_id → events
        self._insights: Dict[str, Dict[str, Any]] = {}  # twin_id → insights

        logger.info("Passive Learning Engine initialized")

    # ============================================
    # PUBLIC API - LEARNING FROM EVENTS
    # ============================================

    async def learn_from_bia(
        self,
        twin_id: str,
        bia_data: Dict[str, Any]
    ) -> LearningEvent:
        """
        Learn from BIA completion

        Insights extracted:
        - Critical functions
        - Recovery objectives (RTO/RPO)
        - Dependencies
        - Risk tolerance (how aggressive/conservative RTO/RPO are)
        - Decision-making speed (time taken to complete)
        - Thoroughness (number of revisions)
        """
        logger.info(f"Learning from BIA for twin: {twin_id}")

        insights = {}

        # Extract critical functions
        if 'critical_functions' in bia_data:
            insights['critical_functions'] = bia_data['critical_functions']

        # Extract RTO/RPO and analyze risk tolerance
        if 'rto_rpo' in bia_data:
            rto_values = [obj.get('rto') for obj in bia_data['rto_rpo'] if obj.get('rto')]
            if rto_values:
                avg_rto = sum(rto_values) / len(rto_values)
                insights['avg_rto_hours'] = avg_rto

                # Infer risk tolerance
                if avg_rto < 4:
                    insights['risk_tolerance'] = 'low'  # Very tight RTO = low tolerance
                elif avg_rto < 24:
                    insights['risk_tolerance'] = 'medium'
                else:
                    insights['risk_tolerance'] = 'high'

        # Extract dependencies
        if 'dependencies' in bia_data:
            insights['dependencies'] = bia_data['dependencies']
            insights['dependency_count'] = len(bia_data['dependencies'])

        # Analyze decision-making patterns
        if 'completion_time' in bia_data:
            completion_time_days = bia_data['completion_time']

            if completion_time_days < 7:
                insights['decision_speed'] = 'fast'
            elif completion_time_days < 30:
                insights['decision_speed'] = 'moderate'
            else:
                insights['decision_speed'] = 'slow'

        # Analyze thoroughness
        if 'revision_count' in bia_data:
            revisions = bia_data['revision_count']

            if revisions > 5:
                insights['thoroughness'] = 'high'  # Many revisions = thorough
            elif revisions > 2:
                insights['thoroughness'] = 'medium'
            else:
                insights['thoroughness'] = 'low'

        # Create learning event
        event = LearningEvent(
            event_id=f"bia_{twin_id}_{datetime.utcnow().timestamp()}",
            source=LearningSource.BIA,
            twin_id=twin_id,
            data=bia_data,
            insights=insights
        )

        # Store event
        await self._store_event(event)

        # Update twin insights
        await self._update_insights(twin_id, insights)

        logger.info(f"Learned {len(insights)} insights from BIA: {list(insights.keys())}")

        return event

    async def learn_from_risk_assessment(
        self,
        twin_id: str,
        risk_data: Dict[str, Any]
    ) -> LearningEvent:
        """
        Learn from risk assessment

        Insights:
        - Risk perception (what they consider risks)
        - Risk appetite (which risks they accept vs mitigate)
        - Mitigation preferences (technical vs organizational controls)
        - Focus areas (which risk categories get most attention)
        """
        logger.info(f"Learning from risk assessment for twin: {twin_id}")

        insights = {}

        # Analyze identified risks
        if 'identified_risks' in risk_data:
            risks = risk_data['identified_risks']
            insights['risk_count'] = len(risks)

            # Categorize risks
            risk_categories = {}
            for risk in risks:
                category = risk.get('category', 'other')
                risk_categories[category] = risk_categories.get(category, 0) + 1

            insights['risk_categories'] = risk_categories
            insights['primary_risk_focus'] = max(risk_categories, key=risk_categories.get)

        # Analyze risk appetite
        if 'risk_treatments' in risk_data:
            treatments = risk_data['risk_treatments']
            accept_count = sum(1 for t in treatments if t.get('action') == 'accept')
            mitigate_count = sum(1 for t in treatments if t.get('action') == 'mitigate')
            transfer_count = sum(1 for t in treatments if t.get('action') == 'transfer')

            total = len(treatments)
            if total > 0:
                accept_rate = accept_count / total

                if accept_rate > 0.4:
                    insights['risk_appetite'] = 'high'  # Accept many risks
                elif accept_rate > 0.2:
                    insights['risk_appetite'] = 'medium'
                else:
                    insights['risk_appetite'] = 'low'  # Mitigate most risks

                insights['risk_treatment_distribution'] = {
                    'accept': accept_count,
                    'mitigate': mitigate_count,
                    'transfer': transfer_count
                }

        # Analyze mitigation preferences
        if 'mitigation_controls' in risk_data:
            controls = risk_data['mitigation_controls']
            technical = sum(1 for c in controls if c.get('type') == 'technical')
            organizational = sum(1 for c in controls if c.get('type') == 'organizational')

            if technical > organizational:
                insights['control_preference'] = 'technical'
            elif organizational > technical:
                insights['control_preference'] = 'organizational'
            else:
                insights['control_preference'] = 'balanced'

        # Create event
        event = LearningEvent(
            event_id=f"risk_{twin_id}_{datetime.utcnow().timestamp()}",
            source=LearningSource.RISK_ASSESSMENT,
            twin_id=twin_id,
            data=risk_data,
            insights=insights
        )

        await self._store_event(event)
        await self._update_insights(twin_id, insights)

        logger.info(f"Learned {len(insights)} insights from risk assessment")

        return event

    async def learn_from_incident(
        self,
        twin_id: str,
        incident_data: Dict[str, Any]
    ) -> LearningEvent:
        """
        Learn from incident report

        Insights:
        - Response patterns (how quickly they respond)
        - Communication style (formal vs informal, transparent vs guarded)
        - Recovery effectiveness
        - Lessons learned adoption
        """
        logger.info(f"Learning from incident for twin: {twin_id}")

        insights = {}

        # Analyze response time
        if 'detected_at' in incident_data and 'response_started_at' in incident_data:
            detected = datetime.fromisoformat(incident_data['detected_at'])
            responded = datetime.fromisoformat(incident_data['response_started_at'])
            response_time_minutes = (responded - detected).total_seconds() / 60

            if response_time_minutes < 15:
                insights['response_speed'] = 'very_fast'
            elif response_time_minutes < 60:
                insights['response_speed'] = 'fast'
            elif response_time_minutes < 240:
                insights['response_speed'] = 'moderate'
            else:
                insights['response_speed'] = 'slow'

        # Analyze recovery time
        if 'response_started_at' in incident_data and 'resolved_at' in incident_data:
            started = datetime.fromisoformat(incident_data['response_started_at'])
            resolved = datetime.fromisoformat(incident_data['resolved_at'])
            recovery_hours = (resolved - started).total_seconds() / 3600

            insights['recovery_time_hours'] = recovery_hours

        # Analyze communication
        if 'communications' in incident_data:
            comms = incident_data['communications']
            insights['communication_count'] = len(comms)

            # Analyze style (simple heuristic)
            if comms:
                # Check for formal language indicators
                formal_indicators = ['Dear', 'Sincerely', 'Regards', 'stakeholders', 'pursuant']
                informal_indicators = ['Hi', 'Thanks', 'team', 'guys', 'quick update']

                all_text = ' '.join(c.get('message', '') for c in comms)
                formal_count = sum(1 for ind in formal_indicators if ind.lower() in all_text.lower())
                informal_count = sum(1 for ind in informal_indicators if ind.lower() in all_text.lower())

                if formal_count > informal_count:
                    insights['communication_style'] = 'formal'
                else:
                    insights['communication_style'] = 'informal'

        # Lessons learned
        if 'lessons_learned' in incident_data:
            lessons = incident_data['lessons_learned']
            insights['lessons_count'] = len(lessons)

            if len(lessons) > 5:
                insights['learning_orientation'] = 'high'
            elif len(lessons) > 2:
                insights['learning_orientation'] = 'medium'
            else:
                insights['learning_orientation'] = 'low'

        # Create event
        event = LearningEvent(
            event_id=f"incident_{twin_id}_{datetime.utcnow().timestamp()}",
            source=LearningSource.INCIDENT_REPORT,
            twin_id=twin_id,
            data=incident_data,
            insights=insights
        )

        await self._store_event(event)
        await self._update_insights(twin_id, insights)

        logger.info(f"Learned {len(insights)} insights from incident")

        return event

    async def learn_from_training(
        self,
        twin_id: str,
        training_data: Dict[str, Any]
    ) -> LearningEvent:
        """
        Learn from training completion

        Insights:
        - Knowledge gaps (low scores indicate gaps)
        - Learning preferences (completion rates, time spent)
        - Engagement level
        """
        logger.info(f"Learning from training for twin: {twin_id}")

        insights = {}

        # Analyze scores
        if 'scores' in training_data:
            scores = training_data['scores']
            avg_score = sum(scores) / len(scores) if scores else 0

            if avg_score < 60:
                insights['knowledge_level'] = 'low'
            elif avg_score < 80:
                insights['knowledge_level'] = 'medium'
            else:
                insights['knowledge_level'] = 'high'

            # Identify weak areas
            if 'topics' in training_data:
                weak_topics = [
                    topic for topic, score in zip(training_data['topics'], scores)
                    if score < 70
                ]
                if weak_topics:
                    insights['knowledge_gaps'] = weak_topics

        # Analyze engagement
        if 'completion_rate' in training_data:
            rate = training_data['completion_rate']

            if rate > 0.8:
                insights['engagement_level'] = 'high'
            elif rate > 0.5:
                insights['engagement_level'] = 'medium'
            else:
                insights['engagement_level'] = 'low'

        # Create event
        event = LearningEvent(
            event_id=f"training_{twin_id}_{datetime.utcnow().timestamp()}",
            source=LearningSource.TRAINING,
            twin_id=twin_id,
            data=training_data,
            insights=insights
        )

        await self._store_event(event)
        await self._update_insights(twin_id, insights)

        logger.info(f"Learned {len(insights)} insights from training")

        return event

    async def learn_from_document(
        self,
        twin_id: str,
        document_data: Dict[str, Any]
    ) -> LearningEvent:
        """
        Learn from document upload

        Insights:
        - Communication style (formal vs informal)
        - Organizational structure (from org charts, hierarchies)
        - Terminology preferences
        - Documentation maturity
        """
        logger.info(f"Learning from document for twin: {twin_id}")

        insights = {}

        # Document type analysis
        if 'document_type' in document_data:
            doc_type = document_data['document_type']
            insights['document_type'] = doc_type

        # TODO: Implement text analysis
        # - Extract organizational structure from org charts
        # - Analyze communication style from documents
        # - Build terminology database

        # Create event
        event = LearningEvent(
            event_id=f"document_{twin_id}_{datetime.utcnow().timestamp()}",
            source=LearningSource.DOCUMENT_UPLOAD,
            twin_id=twin_id,
            data=document_data,
            insights=insights
        )

        await self._store_event(event)
        await self._update_insights(twin_id, insights)

        return event

    # ============================================
    # INSIGHTS RETRIEVAL
    # ============================================

    async def get_insights(self, twin_id: str) -> Dict[str, Any]:
        """Get all accumulated insights for twin"""
        return self._insights.get(twin_id, {})

    async def get_insight(
        self,
        twin_id: str,
        insight_type: str
    ) -> Optional[Any]:
        """Get specific insight"""
        insights = self._insights.get(twin_id, {})
        return insights.get(insight_type)

    async def get_learning_history(
        self,
        twin_id: str,
        source: Optional[LearningSource] = None,
        limit: int = 100
    ) -> List[LearningEvent]:
        """Get learning event history"""
        events = self._events.get(twin_id, [])

        if source:
            events = [e for e in events if e.source == source]

        # Sort by timestamp (newest first)
        events = sorted(events, key=lambda e: e.timestamp, reverse=True)

        return events[:limit]

    # ============================================
    # PATTERN RECOGNITION
    # ============================================

    async def detect_patterns(self, twin_id: str) -> Dict[str, Any]:
        """
        Detect patterns from accumulated learning events

        Patterns:
        - Consistency (do they consistently show same behavior?)
        - Evolution (how are they changing over time?)
        - Anomalies (any unusual behaviors?)
        """
        events = self._events.get(twin_id, [])

        patterns = {}

        # Analyze consistency
        if len(events) >= 5:
            # Check if risk appetite is consistent
            risk_appetites = [
                e.insights.get('risk_appetite')
                for e in events
                if e.source == LearningSource.RISK_ASSESSMENT and 'risk_appetite' in e.insights
            ]

            if risk_appetites:
                most_common = max(set(risk_appetites), key=risk_appetites.count)
                consistency = risk_appetites.count(most_common) / len(risk_appetites)

                patterns['risk_appetite_consistency'] = {
                    'value': most_common,
                    'consistency': consistency
                }

        # Analyze evolution (are they improving?)
        training_events = [e for e in events if e.source == LearningSource.TRAINING]
        if len(training_events) >= 2:
            # Sort by time
            training_events.sort(key=lambda e: e.timestamp)

            first_knowledge = training_events[0].insights.get('knowledge_level')
            last_knowledge = training_events[-1].insights.get('knowledge_level')

            if first_knowledge and last_knowledge:
                knowledge_levels = {'low': 1, 'medium': 2, 'high': 3}
                first_level = knowledge_levels.get(first_knowledge, 0)
                last_level = knowledge_levels.get(last_knowledge, 0)

                if last_level > first_level:
                    patterns['knowledge_trend'] = 'improving'
                elif last_level < first_level:
                    patterns['knowledge_trend'] = 'declining'
                else:
                    patterns['knowledge_trend'] = 'stable'

        return patterns

    # ============================================
    # PRIVATE METHODS
    # ============================================

    async def _store_event(self, event: LearningEvent) -> None:
        """Store learning event"""
        if event.twin_id not in self._events:
            self._events[event.twin_id] = []

        self._events[event.twin_id].append(event)

    async def _update_insights(
        self,
        twin_id: str,
        new_insights: Dict[str, Any]
    ) -> None:
        """Update accumulated insights"""
        if twin_id not in self._insights:
            self._insights[twin_id] = {}

        # Merge new insights
        self._insights[twin_id].update(new_insights)

        # Add metadata
        self._insights[twin_id]['last_updated'] = datetime.utcnow().isoformat()
        self._insights[twin_id]['total_events'] = len(self._events.get(twin_id, []))

    # ============================================
    # STATISTICS
    # ============================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning engine statistics"""
        total_events = sum(len(events) for events in self._events.values())
        total_twins = len(self._events)

        events_by_source = {}
        for events in self._events.values():
            for event in events:
                source = event.source.value
                events_by_source[source] = events_by_source.get(source, 0) + 1

        return {
            'total_events': total_events,
            'total_twins_learning': total_twins,
            'avg_events_per_twin': total_events / total_twins if total_twins > 0 else 0,
            'events_by_source': events_by_source,
        }
