"""
Predictive Timeline Service

Predicts organization's BCM journey using ML and community data.

Uses:
- Current workflow state
- Similar organization journeys (Case Library)
- ML models (success predictor)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

@dataclass
class PredictedEvent:
    """Predicted future event in organization's journey"""
    event_type: str
    name: str
    predicted_date: datetime
    confidence: float
    reasoning: str
    preparation_actions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['predicted_date'] = self.predicted_date.isoformat()
        return result

class PredictiveTimelineService:
    """
    Predict organization's BCM journey

    Example:
    >>> service = PredictiveTimelineService(workflows, cases, ml)
    >>> timeline = await service.predict_timeline("org_123", horizon_months=12)
    """

    def __init__(
        self,
        workflow_engine,
        case_library,
        ml_predictor
    ):
        self.workflows = workflow_engine
        self.cases = case_library
        self.ml = ml_predictor

    async def predict_timeline(
        self,
        org_id: str,
        horizon_months: int = 12
    ) -> Dict[str, Any]:
        """
        Predict organization's timeline

        Returns:
        - Predicted events (milestones, needs)
        - Timeline visualization data
        - Preparation recommendations
        """

        # Get current state
        current = await self.workflows.get_org_state(org_id)

        # Find similar organizations' journeys
        similar = await self.cases.find_similar_orgs(
            industry=current.industry,
            size=current.size,
            module=current.current_module
        )

        # ML prediction
        ml_forecast = await self.ml.predict_journey(
            current_state=current,
            similar_journeys=similar
        )

        # Build timeline
        events = []
        current_date = datetime.utcnow()

        # Predict stage transitions
        for stage_prediction in ml_forecast.stage_sequence:
            event = PredictedEvent(
                event_type='stage_transition',
                name=f"Complete {stage_prediction.stage}",
                predicted_date=current_date + timedelta(days=stage_prediction.days_from_now),
                confidence=stage_prediction.confidence,
                reasoning=stage_prediction.reasoning,
                preparation_actions=stage_prediction.actions
            )
            events.append(event)

        # Predict resource needs
        for need in ml_forecast.predicted_needs:
            event = PredictedEvent(
                event_type='resource_need',
                name=need.description,
                predicted_date=current_date + timedelta(days=need.days_from_now),
                confidence=need.confidence,
                reasoning=f"Based on {need.similar_orgs_count} similar organizations",
                preparation_actions=need.recommendations
            )
            events.append(event)

        # Predict external events (regulatory, etc)
        external = await self._predict_external_events(current, horizon_months)
        events.extend(external)

        # Sort by date
        events.sort(key=lambda e: e.predicted_date)

        return {
            'organization': current.to_dict() if hasattr(current, 'to_dict') else {},
            'timeline': [e.to_dict() for e in events],
            'milestones': self._identify_milestones(events),
            'critical_path': self._calculate_critical_path(events),
            'estimated_completion': events[-1].predicted_date.isoformat() if events else None,
            'confidence_overall': sum(e.confidence for e in events) / len(events) if events else 0
        }

    async def _predict_external_events(
        self,
        current_state,
        horizon_months: int
    ) -> List[PredictedEvent]:
        """Predict external events (regulatory changes, etc)"""

        events = []

        # Healthcare-specific
        if hasattr(current_state, 'industry') and current_state.industry == 'healthcare':
            events.append(PredictedEvent(
                event_type='regulatory',
                name='Potential ISO 22301 revision',
                predicted_date=datetime(2026, 6, 1),
                confidence=0.6,
                reasoning='Standards typically revised every 5-7 years',
                preparation_actions=[
                    'Monitor ISO TC223 announcements',
                    'Join industry working groups',
                    'Review current compliance gaps'
                ]
            ))

        # Financial sector
        if hasattr(current_state, 'industry') and current_state.industry == 'finance':
            events.append(PredictedEvent(
                event_type='regulatory',
                name='DORA compliance deadline',
                predicted_date=datetime(2025, 1, 17),
                confidence=0.95,
                reasoning='EU Digital Operational Resilience Act effective date',
                preparation_actions=[
                    'Review ICT risk management framework',
                    'Update third-party risk assessments',
                    'Prepare incident reporting procedures'
                ]
            ))

        return events

    def _identify_milestones(self, events: List[PredictedEvent]) -> List[Dict]:
        """Identify key milestones"""

        milestones = []

        # First: BIA completion
        bia_complete = next((e for e in events if 'BIA' in e.name and 'Complete' in e.name), None)
        if bia_complete:
            milestones.append({
                'name': 'BIA Complete',
                'date': bia_complete.predicted_date.isoformat(),
                'significance': 'Foundation for all BCM activities'
            })

        # Second: Risk assessment complete
        risk_complete = next((e for e in events if 'Risk' in e.name and 'Complete' in e.name), None)
        if risk_complete:
            milestones.append({
                'name': 'Risk Assessment Complete',
                'date': risk_complete.predicted_date.isoformat(),
                'significance': 'Ready for strategy development'
            })

        # Third: Audit readiness
        audit_events = [e for e in events if e.event_type == 'resource_need' and 'audit' in e.name.lower()]
        if audit_events:
            milestones.append({
                'name': 'Audit Readiness',
                'date': audit_events[0].predicted_date.isoformat(),
                'significance': 'Ready for certification audit'
            })

        return milestones

    def _calculate_critical_path(self, events: List[PredictedEvent]) -> List[str]:
        """Identify critical path (events that can't be delayed)"""

        critical = []

        # Stage transitions are critical
        stage_events = [e for e in events if e.event_type == 'stage_transition']
        critical.extend([e.name for e in stage_events])

        # High-confidence resource needs are critical
        critical_needs = [
            e for e in events
            if e.event_type == 'resource_need' and e.confidence > 0.8
        ]
        critical.extend([e.name for e in critical_needs])

        return critical

    async def get_similar_org_insights(
        self,
        org_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get insights from similar organizations"""

        current = await self.workflows.get_org_state(org_id)

        similar = await self.cases.find_similar_orgs(
            industry=current.industry,
            size=current.size,
            module=current.current_module,
            limit=limit
        )

        # Analyze patterns
        avg_duration = sum(s.get('total_duration_days', 0) for s in similar) / len(similar) if similar else 0
        common_challenges = self._extract_common_challenges(similar)
        success_factors = self._extract_success_factors(similar)

        return {
            'similar_orgs_count': len(similar),
            'average_completion_days': avg_duration,
            'common_challenges': common_challenges,
            'success_factors': success_factors,
            'confidence': min(len(similar) / 10, 1.0)  # Higher with more data
        }

    def _extract_common_challenges(self, cases: List[Dict]) -> List[str]:
        """Extract common challenges from similar cases"""
        challenges = []
        for case in cases:
            if 'challenges' in case:
                challenges.extend(case['challenges'])

        # Count frequency
        from collections import Counter
        counter = Counter(challenges)
        return [c for c, count in counter.most_common(5)]

    def _extract_success_factors(self, cases: List[Dict]) -> List[str]:
        """Extract success factors from similar cases"""
        factors = []
        for case in cases:
            if case.get('metrics', {}).get('completed_successfully'):
                factors.extend(case.get('success_patterns', []))

        from collections import Counter
        counter = Counter(factors)
        return [f for f, count in counter.most_common(5)]
