"""
Metrics Engine for Digital Twin Universal Service

Calculates various health scores and metrics for organizations:
- Overall health score
- Financial health
- Operational health
- Impact score
- Sustainability metrics
- Data quality score
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from statistics import mean

from core.models.base import (
    Organization,
    HealthScore,
    MetricPoint,
    MetricSeries,
    QualityScore,
)

logger = logging.getLogger(__name__)


# ============================================
# METRICS ENGINE
# ============================================

class MetricsEngine:
    """
    Main Metrics Engine

    Calculates health scores and various metrics for digital twins
    """

    def __init__(self):
        logger.info("Metrics Engine initialized")

    async def calculate_health_score(
        self,
        organization: Organization,
        time_series: Optional[List[MetricSeries]] = None
    ) -> HealthScore:
        """
        Calculate overall health score for organization

        Args:
            organization: Organization digital twin
            time_series: Optional historical metrics

        Returns:
            HealthScore with breakdown by category
        """
        logger.info(f"Calculating health score for {organization.name}")

        # Calculate component scores
        financial = await self._calculate_financial_health(organization, time_series)
        operational = await self._calculate_operational_health(organization, time_series)
        impact = await self._calculate_impact_score(organization, time_series)
        sustainability = await self._calculate_sustainability_score(organization, time_series)

        # Overall score (weighted average)
        overall = (
            financial * 0.30 +
            operational * 0.30 +
            impact * 0.20 +
            sustainability * 0.20
        )

        health_score = HealthScore(
            overall=round(overall, 2),
            financial=round(financial, 2),
            operational=round(operational, 2),
            impact=round(impact, 2),
            sustainability=round(sustainability, 2),
            calculated_at=datetime.utcnow()
        )

        logger.info(
            f"Health score calculated: overall={health_score.overall:.1f}, "
            f"financial={health_score.financial:.1f}, "
            f"operational={health_score.operational:.1f}"
        )

        return health_score

    async def _calculate_financial_health(
        self,
        organization: Organization,
        time_series: Optional[List[MetricSeries]] = None
    ) -> float:
        """
        Calculate financial health score (0-100)

        Factors:
        - Revenue/Budget trends
        - Financial stability
        - Growth rate
        - Profitability (if available)
        """
        score = 50.0  # Baseline

        # Revenue/Budget size (normalized)
        if organization.annual_revenue:
            # Score based on revenue size (log scale)
            revenue = organization.annual_revenue
            if revenue > 0:
                revenue_score = min(50 + (revenue / 1000000) * 5, 80)
                score = max(score, revenue_score)

        elif organization.annual_budget:
            budget = organization.annual_budget
            if budget > 0:
                budget_score = min(50 + (budget / 1000000) * 5, 80)
                score = max(score, budget_score)

        # Growth trend from time series
        if time_series:
            revenue_metrics = [m for m in time_series if m.metric_name == 'revenue']
            if revenue_metrics and len(revenue_metrics[0].points) >= 2:
                points = revenue_metrics[0].points
                # Calculate trend
                first_value = points[0].value
                last_value = points[-1].value

                if first_value > 0:
                    growth_rate = ((last_value - first_value) / first_value) * 100

                    # Positive growth boosts score
                    if growth_rate > 0:
                        score = min(score + (growth_rate * 0.5), 95)
                    # Negative growth reduces score
                    else:
                        score = max(score + (growth_rate * 0.5), 20)

        # Maturity level bonus
        score = min(score + (organization.maturity_level * 2), 100)

        return max(0, min(score, 100))

    async def _calculate_operational_health(
        self,
        organization: Organization,
        time_series: Optional[List[MetricSeries]] = None
    ) -> float:
        """
        Calculate operational health score (0-100)

        Factors:
        - Staff size and stability
        - Process maturity
        - Data completeness
        - System integration
        """
        score = 50.0  # Baseline

        # Staff size (stability indicator)
        if organization.employee_count:
            staff = organization.employee_count
            # Optimal range: 10-500 employees
            if 10 <= staff <= 500:
                score += 15
            elif staff > 500:
                score += 10
            elif staff > 0:
                score += 5

        # Maturity level (strong indicator)
        maturity_boost = organization.maturity_level * 8
        score += maturity_boost

        # Data completeness
        completeness = organization.completeness_score
        if completeness > 0:
            score += (completeness / 100) * 15

        # Number of data sources (integration level)
        num_sources = len(organization.sources)
        if num_sources >= 5:
            score += 15
        elif num_sources >= 3:
            score += 10
        elif num_sources >= 1:
            score += 5

        # Time series trends
        if time_series:
            # Look for operational metrics
            operational_metrics = [
                m for m in time_series
                if m.metric_name in ['employee_count', 'productivity', 'efficiency']
            ]

            if operational_metrics:
                # Stability bonus (low variance)
                for metric in operational_metrics:
                    if len(metric.points) >= 3:
                        values = [p.value for p in metric.points]
                        avg = mean(values)
                        variance = sum((v - avg) ** 2 for v in values) / len(values)

                        # Low variance = good stability
                        if variance < (avg * 0.1):  # Less than 10% variance
                            score += 5

        return max(0, min(score, 100))

    async def _calculate_impact_score(
        self,
        organization: Organization,
        time_series: Optional[List[MetricSeries]] = None
    ) -> float:
        """
        Calculate impact score (0-100)

        Factors:
        - Organization type and sector
        - Size and reach
        - BCM data (if available)
        - Historical impact metrics
        """
        score = 50.0  # Baseline

        # Organization type impact potential
        org_type_scores = {
            'infrastructure': 20,  # High impact potential
            'government': 15,
            'npo': 15,
            'corporate': 10,
        }
        score += org_type_scores.get(organization.org_type.value, 10)

        # Size/reach impact
        if organization.employee_count:
            # Larger organizations typically have broader impact
            staff = organization.employee_count
            if staff > 1000:
                score += 15
            elif staff > 100:
                score += 10
            elif staff > 10:
                score += 5

        # Geographic reach (multiple locations)
        num_locations = len(organization.locations)
        if num_locations > 10:
            score += 15
        elif num_locations > 3:
            score += 10
        elif num_locations > 1:
            score += 5

        # BCM data available (indicates impact awareness)
        if organization.bcm_data:
            # Check for key BCM indicators
            if 'critical_functions' in organization.bcm_data:
                score += 5
            if 'stakeholders' in organization.bcm_data:
                score += 5
            if 'dependencies' in organization.bcm_data:
                score += 5

        # Time series impact metrics
        if time_series:
            impact_metrics = [
                m for m in time_series
                if m.metric_name in ['beneficiaries', 'reach', 'impact_score']
            ]

            for metric in impact_metrics:
                if metric.points:
                    # Growth in impact metrics
                    if len(metric.points) >= 2:
                        first = metric.points[0].value
                        last = metric.points[-1].value
                        if first > 0:
                            growth = ((last - first) / first) * 100
                            score += min(growth * 0.3, 10)

        return max(0, min(score, 100))

    async def _calculate_sustainability_score(
        self,
        organization: Organization,
        time_series: Optional[List[MetricSeries]] = None
    ) -> float:
        """
        Calculate sustainability score (0-100)

        Factors:
        - Financial sustainability
        - Operational resilience
        - Risk management maturity
        - Data quality
        """
        score = 50.0  # Baseline

        # Maturity = sustainability indicator
        score += organization.maturity_level * 6

        # Low risk score = high sustainability
        if organization.risk_score > 0:
            # Inverse relationship: low risk = high sustainability
            sustainability_from_risk = 100 - organization.risk_score
            score = (score + sustainability_from_risk) / 2

        # Data quality = sustainability indicator
        if organization.quality_score > 0:
            score += (organization.quality_score / 100) * 15

        # Multiple data sources = resilience
        num_sources = len(organization.sources)
        if num_sources >= 5:
            score += 15
        elif num_sources >= 3:
            score += 10
        elif num_sources >= 1:
            score += 5

        # BCM preparedness
        if organization.bcm_data:
            bcm_indicators = [
                'business_continuity_plan',
                'disaster_recovery_plan',
                'risk_register',
                'incident_response_plan'
            ]

            available = sum(1 for ind in bcm_indicators if ind in organization.bcm_data)
            score += available * 3

        # Financial stability from time series
        if time_series:
            revenue_metrics = [m for m in time_series if m.metric_name in ['revenue', 'budget']]

            for metric in revenue_metrics:
                if len(metric.points) >= 3:
                    values = [p.value for p in metric.points]

                    # Check for consistent positive values (stability)
                    if all(v > 0 for v in values):
                        score += 5

                    # Check for growth trend
                    if len(values) >= 2:
                        if values[-1] > values[0]:
                            score += 5

        return max(0, min(score, 100))

    async def calculate_quality_score(
        self,
        organization: Organization
    ) -> QualityScore:
        """
        Calculate data quality score for organization

        Dimensions:
        - Completeness: % of fields populated
        - Accuracy: validation checks passed
        - Consistency: cross-field validation
        - Timeliness: data freshness
        - Uniqueness: duplicate detection

        Args:
            organization: Organization digital twin

        Returns:
            QualityScore with breakdown and recommendations
        """
        logger.info(f"Calculating quality score for {organization.name}")

        dimensions: Dict[str, float] = {}
        issues: List[str] = []
        recommendations: List[str] = []

        # 1. Completeness Score
        completeness = self._calculate_completeness(organization, issues, recommendations)
        dimensions['completeness'] = completeness

        # 2. Accuracy Score
        accuracy = self._calculate_accuracy(organization, issues, recommendations)
        dimensions['accuracy'] = accuracy

        # 3. Consistency Score
        consistency = self._calculate_consistency(organization, issues, recommendations)
        dimensions['consistency'] = consistency

        # 4. Timeliness Score
        timeliness = self._calculate_timeliness(organization, issues, recommendations)
        dimensions['timeliness'] = timeliness

        # 5. Uniqueness Score (always 100 for single record, useful for multi-source)
        dimensions['uniqueness'] = 100.0

        # Overall score (weighted average)
        overall = (
            completeness * 0.30 +
            accuracy * 0.25 +
            consistency * 0.25 +
            timeliness * 0.15 +
            dimensions['uniqueness'] * 0.05
        )

        quality_score = QualityScore(
            overall=round(overall, 2),
            dimensions=dimensions,
            issues=issues,
            recommendations=recommendations,
            assessed_at=datetime.utcnow()
        )

        logger.info(f"Quality score: {quality_score.overall:.1f}/100")

        return quality_score

    def _calculate_completeness(
        self,
        organization: Organization,
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """Calculate completeness score (% of fields populated)"""
        total_fields = 0
        populated_fields = 0

        # Core identity fields
        fields = {
            'name': organization.name,
            'org_type': organization.org_type,
            'industry': organization.industry,
            'employee_count': organization.employee_count,
            'annual_revenue': organization.annual_revenue or organization.annual_budget,
            'headquarters': organization.headquarters,
            'email_domain': organization.email_domain,
        }

        for field_name, value in fields.items():
            total_fields += 1
            if value is not None:
                populated_fields += 1
            else:
                issues.append(f"Missing: {field_name}")

        # Contact info
        if len(organization.contacts) > 0:
            populated_fields += 1
        else:
            issues.append("No contact information")
            recommendations.append("Add contact information (email, phone, website)")
        total_fields += 1

        # Location info
        if len(organization.locations) > 0:
            populated_fields += 1
        else:
            recommendations.append("Add location information")
        total_fields += 1

        # Data sources
        if len(organization.sources) > 0:
            populated_fields += 1
        else:
            issues.append("No data sources connected")
            recommendations.append("Connect at least one data source")
        total_fields += 1

        completeness = (populated_fields / total_fields) * 100

        if completeness < 60:
            recommendations.append("Improve data completeness by adding missing fields")

        return completeness

    def _calculate_accuracy(
        self,
        organization: Organization,
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """Calculate accuracy score (validation checks)"""
        score = 100.0

        # Email domain validation
        if organization.email_domain:
            if not ('.' in organization.email_domain and len(organization.email_domain) > 3):
                score -= 10
                issues.append("Invalid email domain format")

        # Website validation
        if organization.website:
            if not (organization.website.startswith('http://') or organization.website.startswith('https://')):
                score -= 10
                issues.append("Website URL should start with http:// or https://")

        # Financial data validation
        if organization.annual_revenue and organization.annual_revenue < 0:
            score -= 15
            issues.append("Annual revenue cannot be negative")

        if organization.annual_budget and organization.annual_budget < 0:
            score -= 15
            issues.append("Annual budget cannot be negative")

        # Employee count validation
        if organization.employee_count and organization.employee_count < 0:
            score -= 15
            issues.append("Employee count cannot be negative")

        # Score ranges validation
        if organization.health_score < 0 or organization.health_score > 100:
            score -= 20
            issues.append("Health score out of valid range (0-100)")

        if score < 80:
            recommendations.append("Review and correct data validation issues")

        return max(0, score)

    def _calculate_consistency(
        self,
        organization: Organization,
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """Calculate consistency score (cross-field validation)"""
        score = 100.0

        # Revenue vs Budget consistency
        if organization.annual_revenue and organization.annual_budget:
            # For corporates, revenue usually > budget
            # For NPOs/Gov, budget is more relevant
            if organization.org_type.value == 'corporate':
                if organization.annual_budget > organization.annual_revenue * 1.5:
                    score -= 10
                    issues.append("Budget significantly higher than revenue (unusual for corporate)")

        # Employee count vs revenue consistency
        if organization.employee_count and organization.annual_revenue:
            revenue_per_employee = organization.annual_revenue / organization.employee_count

            # Very low revenue per employee might indicate data issue
            if revenue_per_employee < 1000:
                score -= 10
                issues.append("Very low revenue per employee - verify data")

            # Very high might also be unusual
            if revenue_per_employee > 10000000:
                score -= 5
                issues.append("Very high revenue per employee - verify data")

        # Contacts consistency
        for contact in organization.contacts:
            if contact.type == 'email':
                if '@' not in contact.value:
                    score -= 5
                    issues.append(f"Invalid email format: {contact.value}")
            elif contact.type == 'website':
                if not contact.value.startswith('http'):
                    score -= 5
                    issues.append(f"Invalid website URL: {contact.value}")

        # Name vs aliases consistency
        if organization.canonical_name and organization.name:
            if organization.canonical_name.lower() not in organization.name.lower():
                if organization.name.lower() not in organization.canonical_name.lower():
                    score -= 5
                    issues.append("Canonical name doesn't match organization name")

        if score < 85:
            recommendations.append("Review data consistency across fields")

        return max(0, score)

    def _calculate_timeliness(
        self,
        organization: Organization,
        issues: List[str],
        recommendations: List[str]
    ) -> float:
        """Calculate timeliness score (data freshness)"""
        score = 100.0
        now = datetime.utcnow()

        # Check last update time
        if organization.updated_at:
            days_since_update = (now - organization.updated_at).days

            if days_since_update > 180:  # 6 months
                score -= 40
                issues.append("Data not updated in over 6 months")
                recommendations.append("Update organization data")
            elif days_since_update > 90:  # 3 months
                score -= 20
                issues.append("Data not updated in over 3 months")
                recommendations.append("Consider updating organization data")
            elif days_since_update > 30:  # 1 month
                score -= 10

        # Check data source freshness
        for source in organization.sources:
            if source.last_sync:
                days_since_sync = (now - source.last_sync).days

                if days_since_sync > 30:
                    score -= 10
                    issues.append(f"Source {source.source_type.value} not synced in {days_since_sync} days")
                    recommendations.append(f"Sync {source.source_type.value} data source")

        return max(0, score)

    async def generate_metric_series(
        self,
        twin_id: str,
        metric_name: str,
        start_date: datetime,
        end_date: datetime,
        interval_days: int = 1
    ) -> MetricSeries:
        """
        Generate placeholder metric series (for testing/demo)

        In production, this would query actual time-series database

        Args:
            twin_id: Organization twin ID
            metric_name: Name of metric
            start_date: Start date
            end_date: End date
            interval_days: Days between points

        Returns:
            MetricSeries with generated points
        """
        points: List[MetricPoint] = []
        current_date = start_date

        # Simulate some data
        base_value = 1000.0

        while current_date <= end_date:
            # Add some variation
            import random
            variation = random.uniform(0.95, 1.05)
            value = base_value * variation

            points.append(MetricPoint(
                timestamp=current_date,
                value=value,
                unit='count',
                metadata={}
            ))

            current_date += timedelta(days=interval_days)
            base_value *= 1.01  # Slight upward trend

        return MetricSeries(
            metric_name=metric_name,
            twin_id=twin_id,
            points=points,
            aggregation='daily'
        )
