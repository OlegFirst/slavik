"""
Proactive Recommendations Engine

Sends daily recommendations to organizations based on predictions.

Magic Features:
- Daily digest of upcoming milestones
- Smart reminders (7, 3, 1 days before)
- Resource preparation suggestions
- Expert booking recommendations
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProactiveRecommendation:
    """Proactive recommendation for organization"""
    type: str  # 'milestone_approaching', 'prepare_resources', 'book_expert'
    priority: str  # 'high', 'medium', 'low'
    milestone: str
    days_until: int
    confidence: float
    actions: List[str]
    resources: List[Dict[str, Any]]


class ProactiveRecommendationsEngine:
    """
    Generates and sends proactive recommendations

    Daily cron job:
    1. Check all active organizations
    2. Identify upcoming milestones
    3. Generate recommendations
    4. Send notifications
    """

    def __init__(self, journey_predictor, eventbus):
        """
        Initialize engine

        Args:
            journey_predictor: JourneyPredictor instance
            eventbus: EventBus for publishing notifications
        """
        self.journey_predictor = journey_predictor
        self.eventbus = eventbus

    async def generate_daily_recommendations(self) -> Dict[str, List[ProactiveRecommendation]]:
        """
        Daily job: Generate recommendations for all active orgs

        Returns:
            Dict mapping org_id to list of recommendations
        """

        logger.info("Generating daily proactive recommendations")

        # Get all active organizations
        active_orgs = await self._get_active_organizations()

        all_recommendations = {}

        for org in active_orgs:
            recommendations = await self.get_recommendations(org.org_id, days_ahead=14)

            if recommendations:
                all_recommendations[str(org.org_id)] = recommendations

        logger.info(
            f"Generated recommendations for {len(all_recommendations)} organizations"
        )

        # Send notifications
        await self._send_daily_digests(all_recommendations)

        return all_recommendations

    async def get_recommendations(
        self,
        org_id: UUID,
        days_ahead: int = 14
    ) -> List[ProactiveRecommendation]:
        """
        Get proactive recommendations for organization

        Args:
            org_id: Organization ID
            days_ahead: Look ahead window (default 14 days)

        Returns:
            List of recommendations
        """

        # Get organization context
        org_context = await self._get_org_context(org_id)

        # Get journey predictions
        predictions = await self.journey_predictor.predict_next_milestones(
            org_context=org_context,
            horizon_days=days_ahead
        )

        recommendations = []

        for milestone in predictions:
            days_until = (milestone.predicted_start_date - datetime.utcnow()).days

            # Generate recommendations based on timeline
            if days_until <= 1:
                # Starting today/tomorrow
                rec = self._create_starting_soon_recommendation(milestone)
                recommendations.append(rec)

            elif days_until <= 3:
                # 3 days or less
                rec = self._create_prepare_now_recommendation(milestone)
                recommendations.append(rec)

            elif days_until <= 7:
                # 1 week ahead
                rec = self._create_one_week_reminder(milestone)
                recommendations.append(rec)

        logger.info(
            f"Generated {len(recommendations)} recommendations for org {org_id}"
        )

        return recommendations

    def _create_starting_soon_recommendation(
        self,
        milestone
    ) -> ProactiveRecommendation:
        """Create recommendation for milestone starting today/tomorrow"""

        actions = [
            f"Review {milestone.milestone} workflow in platform",
            "Gather required team members",
            "Ensure tools and templates are ready"
        ]

        if milestone.recommended_experts:
            expert = milestone.recommended_experts[0]
            actions.append(
                f"Consider booking {expert.get('specialty')} expert for guidance"
            )

        resources = self._get_resources_for_milestone(milestone.milestone)

        return ProactiveRecommendation(
            type='milestone_approaching',
            priority='high',
            milestone=milestone.milestone,
            days_until=0,
            confidence=milestone.confidence,
            actions=actions,
            resources=resources
        )

    def _create_prepare_now_recommendation(
        self,
        milestone
    ) -> ProactiveRecommendation:
        """Create recommendation for milestone in 1-3 days"""

        actions = [
            f"Review prerequisites for {milestone.milestone}",
            "Schedule team kickoff meeting",
            "Download relevant templates"
        ]

        # Add challenge-specific preparations
        if milestone.challenges:
            top_challenge = milestone.challenges[0]
            actions.extend(top_challenge.get('mitigation_strategies', [])[:2])

        resources = self._get_resources_for_milestone(milestone.milestone)

        return ProactiveRecommendation(
            type='prepare_resources',
            priority='high',
            milestone=milestone.milestone,
            days_until=(milestone.predicted_start_date - datetime.utcnow()).days,
            confidence=milestone.confidence,
            actions=actions,
            resources=resources
        )

    def _create_one_week_reminder(
        self,
        milestone
    ) -> ProactiveRecommendation:
        """Create reminder for milestone in ~1 week"""

        actions = [
            f"{milestone.milestone.upper()} starting in ~1 week",
            "Review similar case studies",
            "Prepare team calendar"
        ]

        if milestone.recommended_experts:
            actions.append("Review available experts and their profiles")

        resources = self._get_resources_for_milestone(milestone.milestone)

        return ProactiveRecommendation(
            type='milestone_approaching',
            priority='medium',
            milestone=milestone.milestone,
            days_until=(milestone.predicted_start_date - datetime.utcnow()).days,
            confidence=milestone.confidence,
            actions=actions,
            resources=resources
        )

    def _get_resources_for_milestone(self, milestone: str) -> List[Dict[str, Any]]:
        """Get recommended resources for milestone"""

        RESOURCE_MAP = {
            'bia': [
                {'type': 'template', 'name': 'BIA Worksheet', 'url': '/templates/bia'},
                {'type': 'video', 'name': 'BIA Best Practices', 'url': '/learn/bia'},
                {'type': 'cases', 'name': '5 Similar BIA Cases', 'url': '/cases?module=bia'}
            ],
            'risk': [
                {'type': 'template', 'name': 'Risk Register Template', 'url': '/templates/risk'},
                {'type': 'tool', 'name': 'Risk Assessment Calculator', 'url': '/tools/risk'},
                {'type': 'guide', 'name': 'FAIR Methodology Guide', 'url': '/learn/fair'}
            ],
            'planning': [
                {'type': 'template', 'name': 'Strategy Template', 'url': '/templates/strategy'},
                {'type': 'cases', 'name': 'Planning Case Studies', 'url': '/cases?module=planning'},
                {'type': 'checklist', 'name': 'Planning Checklist', 'url': '/checklists/planning'}
            ]
        }

        return RESOURCE_MAP.get(milestone, [
            {'type': 'guide', 'name': f'{milestone.title()} Guide', 'url': f'/learn/{milestone}'}
        ])

    async def _send_daily_digests(
        self,
        recommendations: Dict[str, List[ProactiveRecommendation]]
    ):
        """Send daily digest emails to organizations"""

        for org_id, recs in recommendations.items():
            if not recs:
                continue

            # Build digest email
            email_content = self._build_digest_email(org_id, recs)

            # Publish notification event
            await self.eventbus.publish('proactive.daily_digest', {
                'org_id': org_id,
                'recommendations_count': len(recs),
                'email_content': email_content
            })

        logger.info(f"Sent {len(recommendations)} daily digests")

    def _build_digest_email(
        self,
        org_id: str,
        recommendations: List[ProactiveRecommendation]
    ) -> str:
        """Build daily digest email content"""

        # Get certification prediction
        cert_prediction = None  # Would call journey_predictor

        email = f"""
Subject: Your BCM Journey - This Week's Guidance

Good morning! 👋

Here's your personalized guidance based on your BCM journey progress:

"""

        # High priority items first
        high_priority = [r for r in recommendations if r.priority == 'high']

        if high_priority:
            email += "🔥 ACTION NEEDED THIS WEEK:\n\n"

            for rec in high_priority:
                days_text = "TODAY" if rec.days_until == 0 else f"in {rec.days_until} days"
                email += f"📌 {rec.milestone.upper()} ({days_text})\n"
                email += f"   Confidence: {int(rec.confidence * 100)}%\n\n"

                for action in rec.actions[:3]:
                    email += f"   ✓ {action}\n"

                email += "\n"

                # Resources
                if rec.resources:
                    email += "   📚 Resources:\n"
                    for resource in rec.resources[:2]:
                        email += f"      - {resource['name']}\n"

                email += "\n"

        # Medium priority
        medium_priority = [r for r in recommendations if r.priority == 'medium']

        if medium_priority:
            email += "📅 UPCOMING MILESTONES:\n\n"

            for rec in medium_priority:
                email += f"   {rec.milestone}: ~{rec.days_until} days\n"

        # Certification tracker
        if cert_prediction:
            email += f"""
🎯 CERTIFICATION TRACKER:
   Predicted: {cert_prediction.predicted_certification_date.strftime('%B %Y')}
   Success Probability: {int(cert_prediction.success_probability * 100)}%

"""

        email += """
Questions? Need help? Reply to this email or visit your dashboard.

Best regards,
Your AI-Powered BCM Platform
"""

        return email

    async def _get_active_organizations(self) -> List[Any]:
        """Get active organizations"""

        # Would query database
        # For now, mock
        logger.warning("Using mock organizations")

        from .journey_predictor import OrganizationContext
        from uuid import uuid4

        return [
            OrganizationContext(
                org_id=uuid4(),
                industry='healthcare',
                size=200,
                maturity_level=2,
                current_stage='bia',
                started_at=datetime.utcnow() - timedelta(days=30),
                workflows_completed=[],
                resources={'budget': 'medium'},
                region='north_america'
            )
        ]

    async def _get_org_context(self, org_id: UUID):
        """Get organization context"""

        # Would query database
        from .journey_predictor import OrganizationContext

        return OrganizationContext(
            org_id=org_id,
            industry='healthcare',
            size=200,
            maturity_level=2,
            current_stage='bia',
            started_at=datetime.utcnow() - timedelta(days=30),
            workflows_completed=[],
            resources={'budget': 'medium'},
            region='north_america'
        )
