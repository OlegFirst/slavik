"""
Expert Demand Forecaster

Predicts marketplace demand for specialists.

Magic Features:
- Aggregate demand from all active organizations
- Forecast by specialty and time period
- Geographic distribution
- Proactive specialist notifications
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from collections import defaultdict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DemandForecast:
    """Forecast of expert demand"""
    forecast_date: datetime
    horizon_days: int
    total_predicted_projects: int
    by_specialty: Dict[str, 'SpecialtyDemand']
    by_industry: Dict[str, int]
    by_week: Dict[str, Dict[str, int]]  # week -> specialty -> count


@dataclass
class SpecialtyDemand:
    """Demand metrics for specialty"""
    specialty: str
    expected_projects: int
    peak_week: datetime
    confidence: float
    geographic_distribution: Dict[str, int]


class ExpertDemandForecaster:
    """
    Forecasts demand for marketplace specialists

    Use cases:
    - Specialists see: "5 BIA projects expected in healthcare next month"
    - Platform can recruit in shortage areas
    - Pricing optimization
    """

    def __init__(self, journey_predictor, db):
        """
        Initialize forecaster

        Args:
            journey_predictor: JourneyPredictor instance
            db: Database session
        """
        self.journey_predictor = journey_predictor
        self.db = db

    async def forecast_specialist_demand(
        self,
        horizon_days: int = 30,
        specialty: Optional[str] = None,
        industry: Optional[str] = None
    ) -> DemandForecast:
        """
        Forecast demand for specialists

        Method:
        1. Get all active organizations
        2. Predict their journeys
        3. Identify when they'll need external help
        4. Aggregate by specialty, industry, time

        Args:
            horizon_days: Forecast horizon (default 30 days)
            specialty: Filter by specialty (optional)
            industry: Filter by industry (optional)

        Returns:
            DemandForecast with aggregated predictions
        """

        logger.info(
            f"Forecasting demand: horizon={horizon_days}d, "
            f"specialty={specialty}, industry={industry}"
        )

        # Get active organizations
        active_orgs = await self._get_active_organizations(industry)

        logger.info(f"Found {len(active_orgs)} active organizations")

        # Predict needs for each
        all_predictions = []
        for org in active_orgs:
            try:
                prediction = await self.journey_predictor.predict_next_milestones(
                    org_context=org,
                    horizon_days=horizon_days
                )
                all_predictions.append({
                    'org': org,
                    'predictions': prediction
                })
            except Exception as e:
                logger.error(f"Failed to predict for org {org.org_id}: {e}")
                continue

        # Aggregate demand
        demand_by_specialty = defaultdict(list)
        demand_by_industry = defaultdict(int)
        demand_by_week = defaultdict(lambda: defaultdict(int))

        for pred in all_predictions:
            org = pred['org']

            for milestone in pred['predictions']:
                # Extract expert needs
                for expert in milestone.recommended_experts:
                    expert_specialty = expert.get('specialty', 'general')

                    # Filter if specialty specified
                    if specialty and expert_specialty != specialty:
                        continue

                    demand_by_specialty[expert_specialty].append({
                        'org_id': org.org_id,
                        'industry': org.industry,
                        'region': org.region,
                        'when': milestone.predicted_start_date,
                        'confidence': milestone.confidence,
                        'milestone': milestone.milestone
                    })

                    demand_by_industry[org.industry] += 1

                    # By week
                    week_start = self._get_week_start(milestone.predicted_start_date)
                    demand_by_week[week_start][expert_specialty] += 1

        # Build forecast
        specialty_forecasts = {}
        for spec, demand_list in demand_by_specialty.items():
            specialty_forecasts[spec] = SpecialtyDemand(
                specialty=spec,
                expected_projects=len(demand_list),
                peak_week=self._calculate_peak_week(demand_list),
                confidence=self._calculate_avg_confidence(demand_list),
                geographic_distribution=self._get_geographic_distribution(demand_list)
            )

        forecast = DemandForecast(
            forecast_date=datetime.utcnow(),
            horizon_days=horizon_days,
            total_predicted_projects=sum(len(d) for d in demand_by_specialty.values()),
            by_specialty=specialty_forecasts,
            by_industry=dict(demand_by_industry),
            by_week=dict(demand_by_week)
        )

        logger.info(
            f"Forecast complete: {forecast.total_predicted_projects} total projects, "
            f"{len(forecast.by_specialty)} specialties"
        )

        return forecast

    async def notify_specialists_of_demand(self):
        """
        Weekly job: Notify specialists of upcoming demand

        Sends email:
        "5 BIA projects expected in healthcare this month"
        """

        logger.info("Sending demand forecasts to specialists")

        # Get 30-day forecast
        forecast = await self.forecast_specialist_demand(horizon_days=30)

        # Get all active specialists
        specialists = await self._get_active_specialists()

        notifications_sent = 0

        for specialist in specialists:
            # Filter forecast to specialist's areas
            relevant_demand = {}

            for specialty in specialist.get('specialties', []):
                if specialty in forecast.by_specialty:
                    relevant_demand[specialty] = forecast.by_specialty[specialty]

            if relevant_demand:
                total_projects = sum(d.expected_projects for d in relevant_demand.values())

                # Send notification
                await self._send_specialist_notification(
                    specialist=specialist,
                    demand=relevant_demand,
                    total_projects=total_projects
                )

                notifications_sent += 1

        logger.info(f"Sent {notifications_sent} demand notifications")

        return notifications_sent

    async def get_shortage_areas(self) -> List[Dict[str, Any]]:
        """
        Identify areas with high demand / low supply

        Used for specialist recruitment
        """

        # Get demand forecast
        forecast = await self.forecast_specialist_demand(horizon_days=60)

        # Get current specialist supply
        specialist_counts = await self._get_specialist_counts_by_specialty()

        # Calculate shortage
        shortages = []
        for specialty, demand in forecast.by_specialty.items():
            supply = specialist_counts.get(specialty, 0)

            if supply == 0:
                shortage_ratio = float('inf')
            else:
                shortage_ratio = demand.expected_projects / supply

            # Shortage if demand/supply > 2
            if shortage_ratio > 2:
                shortages.append({
                    'specialty': specialty,
                    'demand': demand.expected_projects,
                    'supply': supply,
                    'shortage_ratio': shortage_ratio,
                    'peak_week': demand.peak_week,
                    'priority': 'critical' if shortage_ratio > 5 else 'high'
                })

        # Sort by shortage ratio
        shortages.sort(key=lambda x: x['shortage_ratio'], reverse=True)

        logger.info(f"Identified {len(shortages)} shortage areas")

        return shortages

    async def _get_active_organizations(
        self,
        industry: Optional[str] = None
    ) -> List[Any]:
        """Get active organizations from database"""

        from sqlalchemy import select, and_

        # This would query actual organization table
        # For now, mock implementation
        logger.warning("Using mock active organizations")

        # Mock data
        from .journey_predictor import OrganizationContext
        from uuid import uuid4

        mock_orgs = []
        for i in range(20):  # 20 active orgs
            org = OrganizationContext(
                org_id=uuid4(),
                industry=industry or 'healthcare',
                size=100 + i * 50,
                maturity_level=2,
                current_stage='bia' if i % 3 == 0 else 'risk',
                started_at=datetime.utcnow() - timedelta(days=30),
                workflows_completed=['governance'] if i % 2 == 0 else [],
                resources={'budget': 'medium', 'dedicated_team': True},
                region='north_america'
            )
            mock_orgs.append(org)

        return mock_orgs

    async def _get_active_specialists(self) -> List[Dict[str, Any]]:
        """Get active marketplace specialists"""

        # Would query specialist table
        logger.warning("Using mock specialists")

        return [
            {
                'specialist_id': 'spec_1',
                'email': 'jane@example.com',
                'specialties': ['bia', 'risk'],
                'industries': ['healthcare'],
                'availability': 'available'
            },
            {
                'specialist_id': 'spec_2',
                'email': 'john@example.com',
                'specialties': ['planning', 'compliance'],
                'industries': ['healthcare', 'finance'],
                'availability': 'available'
            }
        ]

    async def _get_specialist_counts_by_specialty(self) -> Dict[str, int]:
        """Count specialists by specialty"""

        specialists = await self._get_active_specialists()

        counts = defaultdict(int)
        for spec in specialists:
            for specialty in spec.get('specialties', []):
                counts[specialty] += 1

        return dict(counts)

    def _get_week_start(self, date: datetime) -> str:
        """Get week start date (Monday) for given date"""

        # Get Monday of the week
        days_since_monday = date.weekday()
        monday = date - timedelta(days=days_since_monday)

        return monday.strftime('%Y-%m-%d')

    def _calculate_peak_week(self, demand_list: List[Dict]) -> datetime:
        """Calculate week with highest demand"""

        week_counts = defaultdict(int)
        for demand in demand_list:
            week = self._get_week_start(demand['when'])
            week_counts[week] += 1

        if not week_counts:
            return datetime.utcnow()

        peak_week_str = max(week_counts.items(), key=lambda x: x[1])[0]
        return datetime.strptime(peak_week_str, '%Y-%m-%d')

    def _calculate_avg_confidence(self, demand_list: List[Dict]) -> float:
        """Calculate average confidence across demands"""

        if not demand_list:
            return 0.0

        confidences = [d['confidence'] for d in demand_list]
        return round(sum(confidences) / len(confidences), 2)

    def _get_geographic_distribution(self, demand_list: List[Dict]) -> Dict[str, int]:
        """Get geographic distribution of demand"""

        distribution = defaultdict(int)
        for demand in demand_list:
            region = demand.get('region', 'unknown')
            distribution[region] += 1

        return dict(distribution)

    async def _send_specialist_notification(
        self,
        specialist: Dict,
        demand: Dict[str, SpecialtyDemand],
        total_projects: int
    ):
        """Send demand notification to specialist"""

        # Build email content
        specialties_text = ', '.join(demand.keys())

        email_content = f"""
Subject: {total_projects} Projects Expected in Your Specialties

Hi {specialist.get('name', 'Specialist')},

Based on current platform activity, we forecast {total_projects} projects
in your specialties over the next 30 days:

"""

        for specialty, metrics in demand.items():
            email_content += f"""
{specialty.upper()}: {metrics.expected_projects} projects
  - Peak week: {metrics.peak_week.strftime('%B %d')}
  - Confidence: {int(metrics.confidence * 100)}%
  - Regions: {', '.join(metrics.geographic_distribution.keys())}
"""

        email_content += """

This is a great time to:
- Update your availability calendar
- Review your service offerings
- Prepare templates and resources

View opportunities: https://platform.com/marketplace

Best regards,
AI-Powered BCM Platform
"""

        # Would integrate with notification service
        logger.info(
            f"Notification sent to {specialist.get('email')}: "
            f"{total_projects} projects"
        )

        # Publish event for notification service
        # await eventbus.publish('specialist.demand_forecast', {...})

        return email_content
