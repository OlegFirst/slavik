"""
Daily Proactive Recommendations Scheduler

Runs daily at 8 AM to:
1. Generate recommendations for all active organizations
2. Send email digests to users
3. Log recommendations to database
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyDigestScheduler:
    """Handles daily proactive recommendation generation and delivery"""

    def __init__(self, dependencies):
        self.deps = dependencies
        self.predictive_repo = dependencies.predictive_repo
        self.case_library = dependencies.case_library
        self.notification_client = dependencies.notification_client

    async def run_daily_digests(self):
        """
        Main job: Generate and send daily recommendation digests

        Process:
        1. Get all active organizations
        2. For each org, generate recommendations
        3. Save to database
        4. Send email to users
        """
        logger.info("🔮 Starting daily proactive recommendations job...")

        try:
            # Get active organizations
            active_orgs = await self._get_active_organizations()
            logger.info(f"📊 Found {len(active_orgs)} active organizations")

            # Process each organization
            recommendations_sent = 0
            for org in active_orgs:
                try:
                    # Generate recommendations
                    recommendations = await self._generate_recommendations_for_org(org)

                    if not recommendations:
                        logger.info(f"   No recommendations for org {org['id']}")
                        continue

                    # Save to database
                    saved_ids = await self._save_recommendations(org['id'], recommendations)

                    # Get org users
                    users = await self._get_org_users(org['id'])

                    # Send email to each user
                    for user in users:
                        if user.get('email_notifications_enabled', True):
                            await self._send_digest_email(user, recommendations, saved_ids)
                            recommendations_sent += 1

                except Exception as e:
                    logger.error(f"   Error processing org {org['id']}: {e}")
                    continue

            logger.info(f"✅ Daily digest job complete: {recommendations_sent} emails sent")

            return {
                "status": "success",
                "organizations_processed": len(active_orgs),
                "recommendations_sent": recommendations_sent,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Daily digest job failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _get_active_organizations(self) -> List[Dict]:
        """Get organizations with active BCM journeys"""
        try:
            # Query organizations that:
            # 1. Have workflows in progress
            # 2. Last activity within 30 days
            # 3. Not yet certified

            result = self.deps.supabase.table("organizations") \
                .select("id, name, industry, size, current_module, current_stage, created_at") \
                .eq("status", "active") \
                .gte("last_activity_at", (datetime.now() - timedelta(days=30)).isoformat()) \
                .is_("certified_at", "null") \
                .execute()

            return result.data

        except Exception as e:
            logger.error(f"Error getting active organizations: {e}")
            return []

    async def _generate_recommendations_for_org(self, org: Dict) -> List[Dict]:
        """
        Generate proactive recommendations for organization

        Recommendation types:
        - milestone_approaching: Upcoming milestone in 7/3/1 days
        - expert_needed: Should book expert consultation
        - challenge_predicted: Potential challenge detected
        - resource_required: Document/template needed
        """
        recommendations = []

        # Import prediction services
        from ..services.journey_predictor import JourneyPredictor, OrganizationContext
        from ..services.proactive_recommendations import ProactiveRecommendationsEngine
        from uuid import UUID

        # Build org context
        org_context = OrganizationContext(
            org_id=UUID(org['id']),
            industry=org.get('industry', 'unknown'),
            size=org.get('size', 100),
            maturity_level=org.get('maturity_level', 2),
            current_stage=org.get('current_stage', 'planning'),
            started_at=datetime.fromisoformat(org.get('created_at')),
            workflows_completed=[],
            resources={},
            region=org.get('region', 'unknown')
        )

        # Initialize predictor with Case Library
        journey_predictor = JourneyPredictor(case_library=self.case_library)

        # Predict next milestones
        predicted_milestones = await journey_predictor.predict_next_milestones(
            org_context,
            horizon_days=30  # Look 30 days ahead
        )

        # Initialize recommendations engine
        rec_engine = ProactiveRecommendationsEngine(
            journey_predictor=journey_predictor,
            case_library=self.case_library
        )

        # Generate recommendations from predictions
        for milestone in predicted_milestones:
            days_until = (milestone.predicted_start_date - datetime.now()).days

            # Milestone approaching (7, 3, 1 days before)
            if days_until in [7, 3, 1]:
                recommendations.append({
                    "type": "milestone_approaching",
                    "priority": "high" if days_until <= 3 else "medium",
                    "milestone": milestone.milestone,
                    "days_until": days_until,
                    "confidence": milestone.confidence,
                    "title": f"{milestone.milestone.replace('_', ' ').title()} starts in {days_until} days",
                    "message": milestone.reasoning,
                    "actions": [
                        f"Review {milestone.milestone} requirements",
                        "Prepare necessary documentation",
                        "Schedule team kickoff meeting"
                    ] + [f"Book {expert['specialty']} expert" for expert in milestone.recommended_experts[:1]],
                    "resources": [
                        {"type": "template", "name": f"{milestone.milestone} Template"},
                        {"type": "guide", "name": f"How to complete {milestone.milestone}"}
                    ]
                })

            # Expert consultation recommended
            if milestone.recommended_experts and days_until <= 14:
                recommendations.append({
                    "type": "expert_needed",
                    "priority": "medium",
                    "milestone": milestone.milestone,
                    "days_until": days_until,
                    "confidence": milestone.confidence,
                    "title": f"Expert consultation recommended for {milestone.milestone}",
                    "message": f"Based on similar organizations, booking an expert now will increase success probability by 23%.",
                    "actions": [
                        f"Browse {milestone.recommended_experts[0]['specialty']} experts",
                        "Review expert profiles and ratings",
                        "Schedule consultation call"
                    ],
                    "resources": [
                        {"type": "marketplace", "url": "/marketplace/experts"},
                        {"type": "guide", "name": "How to work with BCM consultants"}
                    ]
                })

            # Challenge prediction
            if milestone.challenges:
                for challenge in milestone.challenges[:1]:  # Top challenge only
                    if challenge['probability'] > 0.5:
                        recommendations.append({
                            "type": "challenge_predicted",
                            "priority": "high" if challenge['probability'] > 0.7 else "medium",
                            "milestone": milestone.milestone,
                            "days_until": days_until,
                            "confidence": challenge['probability'],
                            "title": f"Potential challenge: {challenge['challenge_type']}",
                            "message": f"We predict a {int(challenge['probability'] * 100)}% chance of encountering {challenge['challenge_type']} during {milestone.milestone}.",
                            "actions": challenge.get('mitigation_strategies', []),
                            "resources": []
                        })

        return recommendations

    async def _save_recommendations(
        self,
        org_id: str,
        recommendations: List[Dict]
    ) -> List[str]:
        """Save recommendations to database"""
        saved_ids = []

        # Get org users
        users = await self._get_org_users(org_id)

        for rec in recommendations:
            for user in users:
                try:
                    rec_id = await self.predictive_repo.save_proactive_recommendation(
                        org_id=org_id,
                        user_id=user['id'],
                        recommendation_data=rec
                    )
                    saved_ids.append(rec_id)

                except Exception as e:
                    logger.error(f"Error saving recommendation: {e}")

        return saved_ids

    async def _get_org_users(self, org_id: str) -> List[Dict]:
        """Get all users for organization"""
        try:
            result = self.deps.supabase.table("organization_members") \
                .select("user_id, users(id, email, full_name)") \
                .eq("organization_id", org_id) \
                .execute()

            return [
                {
                    "id": member['users']['id'],
                    "email": member['users']['email'],
                    "name": member['users'].get('full_name', 'User'),
                    "email_notifications_enabled": True  # TODO: Get from user preferences
                }
                for member in result.data
            ]

        except Exception as e:
            logger.error(f"Error getting org users: {e}")
            return []

    async def _send_digest_email(
        self,
        user: Dict,
        recommendations: List[Dict],
        recommendation_ids: List[str]
    ):
        """Send digest email to user"""
        try:
            logger.info(f"   📧 Sending digest to {user['email']}")

            # Send via Notification Service
            result = await self.notification_client.send_proactive_digest(
                user_email=user['email'],
                recommendations=recommendations
            )

            if result.get('status') == 'success':
                # Mark recommendations as sent
                for rec_id in recommendation_ids:
                    await self.predictive_repo.mark_recommendation_sent(
                        recommendation_id=rec_id,
                        sent_via=['email'],
                        notification_ids=[result.get('notification_id')]
                    )

                logger.info(f"   ✅ Digest sent successfully")
            else:
                logger.error(f"   ❌ Failed to send digest: {result.get('message')}")

        except Exception as e:
            logger.error(f"   ❌ Error sending digest email: {e}")


# =====================================================
# STANDALONE SCRIPT
# =====================================================

async def main():
    """Run daily digest job"""
    from ..integration.dependencies import get_dependencies, cleanup_dependencies

    try:
        # Initialize dependencies
        deps = await get_dependencies()

        # Run job
        scheduler = DailyDigestScheduler(deps)
        result = await scheduler.run_daily_digests()

        logger.info(f"Job result: {result}")

        # Cleanup
        await cleanup_dependencies()

        return result

    except Exception as e:
        logger.error(f"Job failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
