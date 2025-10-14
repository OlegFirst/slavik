"""
Stuck Organization Detector

Detects when organizations need collective help.

Signals:
- No progress for 7+ days
- Multiple validation failures
- Repeated document reviews
- Low AI confidence scores
- User asks same question multiple times

When stuck detected → Offer collective agent creation

Example:
>>> detector = StuckDetectorService(db, analytics)
>>> is_stuck = await detector.check_organization("org-123")
>>> if is_stuck:
...     await detector.offer_collective_help("org-123", "supply_chain_complexity")
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class StuckDetectorService:
    """
    Detects when organizations are stuck and need help

    Scoring system:
    - Days no progress (>7): +3 points
    - Validation failures (>5): +2 points
    - Low confidence (<0.6): +2 points
    - Repeated questions (>3): +1 point

    Threshold: 4+ points = stuck
    """

    def __init__(
        self,
        db: AsyncSession,
        analytics_client,
        collective_agent_service
    ):
        self.db = db
        self.analytics = analytics_client
        self.collective_service = collective_agent_service

    async def check_organization(
        self,
        org_id: str,
        module: str = None
    ) -> Dict[str, Any]:
        """
        Check if organization is stuck

        Returns:
            {
                'is_stuck': True,
                'stuck_score': 5,
                'signals': {
                    'days_no_progress': 10,
                    'validation_failures': 7,
                    'confidence_scores': 0.45,
                    'repeated_questions': 4
                },
                'recommendations': ['Create collective agent for BIA']
            }
        """

        # Gather signals
        signals = await self._gather_signals(org_id, module)

        # Calculate stuck score
        stuck_score = self._calculate_stuck_score(signals)

        # Determine if stuck
        is_stuck = stuck_score >= settings.STUCK_THRESHOLD

        # Get recommendations
        recommendations = []
        if is_stuck:
            recommendations = await self._generate_recommendations(
                org_id,
                signals,
                module
            )

        return {
            'is_stuck': is_stuck,
            'stuck_score': stuck_score,
            'threshold': settings.STUCK_THRESHOLD,
            'signals': signals,
            'recommendations': recommendations
        }

    async def _gather_signals(
        self,
        org_id: str,
        module: Optional[str]
    ) -> Dict[str, Any]:
        """
        Gather all signals indicating organization might be stuck

        Signals:
        1. Days without progress
        2. Validation failure count
        3. AI confidence scores
        4. Repeated questions
        5. Document review patterns
        """

        signals = {}

        # Signal 1: Days without progress
        signals['days_no_progress'] = await self._get_days_no_progress(org_id, module)

        # Signal 2: Validation failures
        signals['validation_failures'] = await self._count_validation_failures(
            org_id,
            days=7
        )

        # Signal 3: AI confidence scores
        signals['avg_confidence'] = await self._get_avg_confidence(org_id, days=7)

        # Signal 4: Repeated questions
        signals['repeated_questions'] = await self._detect_repeated_questions(
            org_id,
            days=7
        )

        # Signal 5: Document review patterns
        signals['repeated_doc_reviews'] = await self._detect_repeated_doc_reviews(
            org_id,
            days=7
        )

        # Signal 6: User frustration indicators
        signals['frustration_score'] = await self._detect_frustration(org_id, days=7)

        return signals

    def _calculate_stuck_score(self, signals: Dict[str, Any]) -> int:
        """
        Calculate stuck score from signals

        Scoring:
        - Days no progress: 0-3 points
        - Validation failures: 0-2 points
        - Low confidence: 0-2 points
        - Repeated questions: 0-2 points
        - Repeated doc reviews: 0-1 point
        - Frustration: 0-2 points

        Max score: 12
        Stuck threshold: 4
        """

        score = 0

        # Days without progress
        days = signals.get('days_no_progress', 0)
        if days > 14:
            score += 3
        elif days > 7:
            score += 2
        elif days > 3:
            score += 1

        # Validation failures
        failures = signals.get('validation_failures', 0)
        if failures > 10:
            score += 2
        elif failures > 5:
            score += 1

        # AI confidence
        confidence = signals.get('avg_confidence', 1.0)
        if confidence < 0.5:
            score += 2
        elif confidence < 0.6:
            score += 1

        # Repeated questions
        repeated = signals.get('repeated_questions', 0)
        if repeated > 5:
            score += 2
        elif repeated > 3:
            score += 1

        # Repeated document reviews
        doc_repeats = signals.get('repeated_doc_reviews', 0)
        if doc_repeats > 5:
            score += 1

        # Frustration
        frustration = signals.get('frustration_score', 0)
        if frustration > 0.7:
            score += 2
        elif frustration > 0.5:
            score += 1

        return score

    async def _get_days_no_progress(
        self,
        org_id: str,
        module: Optional[str]
    ) -> int:
        """
        Get days since last meaningful progress

        Progress indicators:
        - Workflow step completed
        - Document uploaded
        - Validation passed
        - Significant user activity
        """

        # Query analytics for last progress event
        last_progress = await self.analytics.get_last_progress_event(
            org_id=org_id,
            module=module
        )

        if not last_progress:
            return 0

        # Calculate days
        days = (datetime.utcnow() - last_progress['timestamp']).days
        return days

    async def _count_validation_failures(
        self,
        org_id: str,
        days: int
    ) -> int:
        """
        Count validation failures in last N days

        High failure rate = stuck
        """

        since = datetime.utcnow() - timedelta(days=days)

        failures = await self.analytics.count_events(
            org_id=org_id,
            event_type='validation_failed',
            since=since
        )

        return failures

    async def _get_avg_confidence(
        self,
        org_id: str,
        days: int
    ) -> float:
        """
        Get average AI confidence scores

        Low confidence = AI struggling to help = org stuck
        """

        since = datetime.utcnow() - timedelta(days=days)

        scores = await self.analytics.get_confidence_scores(
            org_id=org_id,
            since=since
        )

        if not scores:
            return 1.0  # No data = assume OK

        return sum(scores) / len(scores)

    async def _detect_repeated_questions(
        self,
        org_id: str,
        days: int
    ) -> int:
        """
        Detect if user asking same questions repeatedly

        Uses semantic similarity to find repeated questions
        """

        since = datetime.utcnow() - timedelta(days=days)

        # Get all user questions
        questions = await self.analytics.get_user_questions(
            org_id=org_id,
            since=since
        )

        # Find semantic duplicates
        # Simplified: Exact match on keywords
        # Production: Use embeddings
        repeated_count = 0
        seen = {}

        for q in questions:
            # Extract key terms
            key_terms = self._extract_key_terms(q['text'])
            key = tuple(sorted(key_terms))

            if key in seen:
                repeated_count += 1
            else:
                seen[key] = q

        return repeated_count

    async def _detect_repeated_doc_reviews(
        self,
        org_id: str,
        days: int
    ) -> int:
        """
        Detect if user reviewing same document pages repeatedly

        Pattern: User stuck on same concept, re-reading same page
        """

        since = datetime.utcnow() - timedelta(days=days)

        doc_views = await self.analytics.get_document_views(
            org_id=org_id,
            since=since
        )

        # Count views per page
        page_views = {}
        for view in doc_views:
            page_key = (view['doc_id'], view['page'])
            page_views[page_key] = page_views.get(page_key, 0) + 1

        # Count pages viewed 5+ times
        repeated = sum(1 for count in page_views.values() if count >= 5)

        return repeated

    async def _detect_frustration(
        self,
        org_id: str,
        days: int
    ) -> float:
        """
        Detect user frustration from behavior patterns

        Indicators:
        - Rapid question asking (desperation)
        - Short session times (giving up)
        - Decreased activity (disengagement)

        Returns:
            Frustration score: 0.0 (none) to 1.0 (high)
        """

        since = datetime.utcnow() - timedelta(days=days)

        # Get activity patterns
        sessions = await self.analytics.get_sessions(
            org_id=org_id,
            since=since
        )

        if not sessions:
            return 0.0

        frustration_score = 0.0

        # Check 1: Rapid question asking
        questions_per_session = [s.get('question_count', 0) for s in sessions]
        avg_questions = sum(questions_per_session) / len(questions_per_session)
        if avg_questions > 10:  # Many questions = confusion
            frustration_score += 0.3

        # Check 2: Short sessions
        session_durations = [s.get('duration_minutes', 0) for s in sessions]
        avg_duration = sum(session_durations) / len(session_durations)
        if avg_duration < 5:  # Giving up quickly
            frustration_score += 0.3

        # Check 3: Decreased activity
        recent_sessions = [s for s in sessions if s['timestamp'] > datetime.utcnow() - timedelta(days=3)]
        if len(recent_sessions) < len(sessions) * 0.3:  # Activity dropped
            frustration_score += 0.4

        return min(frustration_score, 1.0)

    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from question text

        Simple implementation: Filter stop words, lowercase
        Production: Use NLP
        """

        # Lowercase
        text = text.lower()

        # Simple word extraction
        words = text.split()

        # Filter stop words
        stop_words = {'how', 'what', 'when', 'where', 'why', 'is', 'are', 'the', 'a', 'an', 'to', 'for', 'of', 'in', 'on'}
        key_terms = [w for w in words if w not in stop_words and len(w) > 3]

        return key_terms[:5]  # Top 5 terms

    async def _generate_recommendations(
        self,
        org_id: str,
        signals: Dict[str, Any],
        module: Optional[str]
    ) -> List[str]:
        """
        Generate recommendations for stuck organization

        Main recommendation: Create collective agent
        """

        recommendations = []

        # Check if collective agent would help
        if signals.get('days_no_progress', 0) > 7:
            # Find if other orgs solved this
            problem_type = await self._identify_problem_type(org_id, module)

            solver_count = await self._count_solver_organizations(problem_type)

            if solver_count >= settings.MIN_ORGS_FOR_COLLECTIVE:
                recommendations.append({
                    'type': 'collective_agent',
                    'title': f'Get help from {solver_count} organizations that solved this',
                    'description': f'We found {solver_count} similar organizations that successfully completed {problem_type}. Would you like to chat with a Collective Agent created from their experiences?',
                    'action': 'create_collective_agent',
                    'problem_type': problem_type
                })

        # Other recommendations
        if signals.get('validation_failures', 0) > 5:
            recommendations.append({
                'type': 'validation_help',
                'title': 'Review common validation errors',
                'description': 'You\'re experiencing validation failures. Review our guide on common issues.',
                'action': 'show_validation_guide'
            })

        if signals.get('repeated_questions', 0) > 3:
            recommendations.append({
                'type': 'documentation',
                'title': 'Check enhanced documentation',
                'description': 'Your questions suggest you might benefit from our detailed guides.',
                'action': 'show_documentation'
            })

        return recommendations

    async def _identify_problem_type(
        self,
        org_id: str,
        module: Optional[str]
    ) -> str:
        """
        Identify specific problem organization is stuck on

        Based on:
        - Current workflow stage
        - Recent questions
        - Validation failures
        """

        # Get current stage
        current_stage = await self.analytics.get_current_stage(org_id, module)

        # Map stage to problem type
        problem_mapping = {
            'dependency_mapping': 'supply_chain_complexity',
            'criticality_assessment': 'critical_process_prioritization',
            'rto_calculation': 'rto_determination',
            'resource_planning': 'resource_allocation',
            'risk_assessment': 'risk_identification'
        }

        return problem_mapping.get(current_stage, 'general_bcm_challenge')

    async def _count_solver_organizations(self, problem_type: str) -> int:
        """
        Count organizations that solved this problem

        Queries Case Library
        """

        solvers = await self.collective_service.case_library.count_successful_cases(
            problem_type=problem_type,
            min_success_rate=0.8
        )

        return solvers

    async def offer_collective_help(
        self,
        org_id: str,
        problem_type: str
    ) -> str:
        """
        Offer to create collective agent

        Returns:
            offer_id: ID of offer (for tracking acceptance)
        """

        # Create offer
        offer = {
            'org_id': org_id,
            'problem_type': problem_type,
            'offered_at': datetime.utcnow(),
            'status': 'pending'
        }

        # Send notification
        await self._send_collective_agent_offer(org_id, problem_type)

        return "offer-123"  # Placeholder

    async def _send_collective_agent_offer(
        self,
        org_id: str,
        problem_type: str
    ):
        """
        Send notification offering collective agent

        Notification appears in UI:
        "We noticed you're working on X. 7 organizations solved this.
         Would you like help from their collective experience?"
        """

        # Placeholder for notification service
        logger.info(f"Offering collective agent to {org_id} for {problem_type}")

    async def check_all_organizations(self) -> List[Dict]:
        """
        Check all active organizations for stuck signals

        Runs daily as cron job

        Returns list of stuck organizations
        """

        # Get all active orgs
        active_orgs = await self.analytics.get_active_organizations(
            days=30
        )

        stuck_orgs = []

        for org in active_orgs:
            result = await self.check_organization(org['org_id'])

            if result['is_stuck']:
                stuck_orgs.append({
                    'org_id': org['org_id'],
                    'stuck_score': result['stuck_score'],
                    'signals': result['signals'],
                    'recommendations': result['recommendations']
                })

                # Auto-offer collective help
                if result['recommendations']:
                    for rec in result['recommendations']:
                        if rec['type'] == 'collective_agent':
                            await self.offer_collective_help(
                                org['org_id'],
                                rec['problem_type']
                            )

        return stuck_orgs
