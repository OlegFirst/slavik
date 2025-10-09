"""
Prediction Engine for Digital Twin Universal Service

Generates predictions for organizations:
- Financial trend predictions
- Impact predictions
- Risk predictions
- Growth forecasts
- Resource needs predictions
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from statistics import mean, stdev

from core.models.base import (
    Organization,
    Prediction,
    MetricSeries,
    MetricPoint,
)

logger = logging.getLogger(__name__)


# ============================================
# PREDICTION ENGINE
# ============================================

class PredictionEngine:
    """
    Main Prediction Engine

    Generates various predictions for digital twins using statistical models
    and machine learning techniques
    """

    def __init__(self):
        logger.info("Prediction Engine initialized")

    async def predict_financial_trend(
        self,
        organization: Organization,
        time_series: List[MetricSeries],
        timeframe_months: int = 12
    ) -> Prediction:
        """
        Predict financial trend (revenue/budget) for next N months

        Uses linear regression on historical data

        Args:
            organization: Organization digital twin
            time_series: Historical financial metrics
            timeframe_months: Months to predict ahead

        Returns:
            Prediction with forecasted value
        """
        logger.info(
            f"Predicting {timeframe_months}-month financial trend for {organization.name}"
        )

        # Find revenue or budget metrics
        financial_metrics = [
            m for m in time_series
            if m.metric_name in ['revenue', 'budget', 'annual_revenue', 'annual_budget']
        ]

        if not financial_metrics:
            # No historical data - use current value as baseline
            current_value = organization.annual_revenue or organization.annual_budget or 0
            return self._create_baseline_prediction(
                organization,
                'financial_trend',
                timeframe_months,
                current_value,
                confidence=0.3,
                assumptions=['No historical data available', 'Using current value as baseline']
            )

        # Get most relevant metric
        metric = financial_metrics[0]
        points = metric.points

        if len(points) < 2:
            # Not enough data points
            current_value = points[0].value if points else 0
            return self._create_baseline_prediction(
                organization,
                'financial_trend',
                timeframe_months,
                current_value,
                confidence=0.4,
                assumptions=['Insufficient historical data', 'Using last known value']
            )

        # Simple linear regression
        predicted_value, confidence, lower_bound, upper_bound = self._linear_forecast(
            points,
            timeframe_months
        )

        # Build prediction
        assumptions = [
            'Linear trend continuation',
            f'Based on {len(points)} historical data points',
            'Assumes no major market disruptions'
        ]

        factors = {
            'historical_trend': 'primary',
            'data_points': len(points),
            'method': 'linear_regression',
            'volatility': self._calculate_volatility(points)
        }

        prediction = Prediction(
            twin_id=organization.twin_id,
            prediction_type='financial_trend',
            timeframe_months=timeframe_months,
            predicted_value=predicted_value,
            confidence=confidence,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            assumptions=assumptions,
            factors=factors,
            methodology='Linear Regression on Historical Data'
        )

        logger.info(
            f"Financial prediction: ${predicted_value:,.0f} "
            f"(confidence: {confidence:.1%})"
        )

        return prediction

    async def predict_impact(
        self,
        organization: Organization,
        time_series: Optional[List[MetricSeries]] = None,
        timeframe_months: int = 12
    ) -> Prediction:
        """
        Predict future impact score

        Args:
            organization: Organization digital twin
            time_series: Historical impact metrics
            timeframe_months: Months to predict ahead

        Returns:
            Prediction with forecasted impact
        """
        logger.info(f"Predicting impact for {organization.name}")

        # Current baseline
        current_impact = organization.health_score  # Use health score as proxy

        if not time_series:
            # No historical data - use heuristics
            predicted_impact = current_impact * 1.05  # Assume slight improvement

            return Prediction(
                twin_id=organization.twin_id,
                prediction_type='impact',
                timeframe_months=timeframe_months,
                predicted_value=min(predicted_impact, 100),
                confidence=0.5,
                lower_bound=max(current_impact * 0.9, 0),
                upper_bound=min(current_impact * 1.15, 100),
                assumptions=[
                    'No historical data',
                    'Assuming gradual improvement',
                    'Based on current maturity level'
                ],
                factors={
                    'current_impact': current_impact,
                    'maturity_level': organization.maturity_level,
                    'org_type': organization.org_type.value
                },
                methodology='Heuristic baseline estimation'
            )

        # Find impact metrics
        impact_metrics = [
            m for m in time_series
            if m.metric_name in ['impact_score', 'health_score', 'beneficiaries', 'reach']
        ]

        if impact_metrics and len(impact_metrics[0].points) >= 2:
            # Use trend analysis
            points = impact_metrics[0].points
            predicted_value, confidence, lower_bound, upper_bound = self._linear_forecast(
                points,
                timeframe_months
            )

            # Cap at 100
            predicted_value = min(predicted_value, 100)
            upper_bound = min(upper_bound, 100)

            return Prediction(
                twin_id=organization.twin_id,
                prediction_type='impact',
                timeframe_months=timeframe_months,
                predicted_value=predicted_value,
                confidence=confidence,
                lower_bound=max(lower_bound, 0),
                upper_bound=upper_bound,
                assumptions=[
                    'Historical trend continuation',
                    f'Based on {len(points)} data points'
                ],
                factors={
                    'historical_data': len(points),
                    'current_trend': 'positive' if points[-1].value > points[0].value else 'negative'
                },
                methodology='Trend analysis with bounds'
            )

        # Fallback to baseline
        return await self._predict_impact_baseline(organization, timeframe_months)

    async def predict_risk(
        self,
        organization: Organization,
        time_series: Optional[List[MetricSeries]] = None,
        timeframe_months: int = 12
    ) -> Prediction:
        """
        Predict future risk score

        Args:
            organization: Organization digital twin
            time_series: Historical risk metrics
            timeframe_months: Months to predict ahead

        Returns:
            Prediction with forecasted risk
        """
        logger.info(f"Predicting risk for {organization.name}")

        current_risk = organization.risk_score

        # Risk factors
        risk_factors = {
            'financial_stability': self._assess_financial_stability(organization),
            'operational_maturity': organization.maturity_level,
            'data_quality': organization.quality_score,
            'diversification': len(organization.sources)
        }

        # Calculate composite risk
        financial_risk = 100 - risk_factors['financial_stability']
        maturity_risk = (5 - risk_factors['operational_maturity']) * 15
        quality_risk = 100 - risk_factors['data_quality']
        diversification_risk = max(0, 50 - (risk_factors['diversification'] * 10))

        predicted_risk = (
            financial_risk * 0.35 +
            maturity_risk * 0.25 +
            quality_risk * 0.20 +
            diversification_risk * 0.20
        )

        # If we have historical data, adjust prediction
        if time_series:
            risk_metrics = [m for m in time_series if m.metric_name == 'risk_score']
            if risk_metrics and len(risk_metrics[0].points) >= 2:
                points = risk_metrics[0].points
                trend_risk, confidence, lower_bound, upper_bound = self._linear_forecast(
                    points,
                    timeframe_months
                )

                # Weighted average: 70% model, 30% trend
                predicted_risk = predicted_risk * 0.7 + trend_risk * 0.3
                confidence = 0.7
            else:
                confidence = 0.6
        else:
            confidence = 0.6

        # Bounds
        lower_bound = max(predicted_risk * 0.8, 0)
        upper_bound = min(predicted_risk * 1.2, 100)

        prediction = Prediction(
            twin_id=organization.twin_id,
            prediction_type='risk',
            timeframe_months=timeframe_months,
            predicted_value=min(predicted_risk, 100),
            confidence=confidence,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            assumptions=[
                'Current operational patterns continue',
                'No major external disruptions',
                'Risk mitigation measures maintained'
            ],
            factors=risk_factors,
            methodology='Composite risk model with factor analysis'
        )

        logger.info(f"Risk prediction: {predicted_risk:.1f}/100 (confidence: {confidence:.1%})")

        return prediction

    async def predict_growth(
        self,
        organization: Organization,
        time_series: List[MetricSeries],
        timeframe_months: int = 12
    ) -> Prediction:
        """
        Predict organizational growth (staff, revenue, impact)

        Args:
            organization: Organization digital twin
            time_series: Historical growth metrics
            timeframe_months: Months to predict ahead

        Returns:
            Prediction with growth percentage
        """
        logger.info(f"Predicting growth for {organization.name}")

        # Look for growth indicators
        growth_metrics = [
            m for m in time_series
            if m.metric_name in ['revenue', 'employee_count', 'beneficiaries', 'customers']
        ]

        if not growth_metrics:
            # No data - estimate based on maturity
            baseline_growth = organization.maturity_level * 2  # 2-10% based on maturity

            return Prediction(
                twin_id=organization.twin_id,
                prediction_type='growth',
                timeframe_months=timeframe_months,
                predicted_value=baseline_growth,
                confidence=0.4,
                lower_bound=0,
                upper_bound=baseline_growth * 1.5,
                assumptions=['No historical data', 'Based on maturity level'],
                factors={'maturity_level': organization.maturity_level},
                methodology='Maturity-based estimation'
            )

        # Calculate growth rates from historical data
        growth_rates = []

        for metric in growth_metrics:
            if len(metric.points) >= 2:
                first_value = metric.points[0].value
                last_value = metric.points[-1].value

                if first_value > 0:
                    growth_rate = ((last_value - first_value) / first_value) * 100
                    growth_rates.append(growth_rate)

        if not growth_rates:
            # Fallback
            return Prediction(
                twin_id=organization.twin_id,
                prediction_type='growth',
                timeframe_months=timeframe_months,
                predicted_value=5.0,  # Default 5% growth
                confidence=0.3,
                lower_bound=0,
                upper_bound=10,
                assumptions=['Insufficient trend data'],
                factors={},
                methodology='Default baseline'
            )

        # Average growth rate
        avg_growth = mean(growth_rates)

        # Adjust for timeframe (compound)
        years = timeframe_months / 12
        projected_growth = avg_growth * years

        # Confidence based on consistency
        if len(growth_rates) > 1:
            variance = stdev(growth_rates)
            # Lower variance = higher confidence
            confidence = max(0.5, min(0.9, 1 - (variance / 100)))
        else:
            confidence = 0.6

        prediction = Prediction(
            twin_id=organization.twin_id,
            prediction_type='growth',
            timeframe_months=timeframe_months,
            predicted_value=projected_growth,
            confidence=confidence,
            lower_bound=projected_growth * 0.7,
            upper_bound=projected_growth * 1.3,
            assumptions=[
                'Historical growth patterns continue',
                f'Based on {len(growth_metrics)} growth indicators',
                'Market conditions remain stable'
            ],
            factors={
                'historical_growth_rate': avg_growth,
                'growth_consistency': 'high' if confidence > 0.7 else 'moderate',
                'data_points': sum(len(m.points) for m in growth_metrics)
            },
            methodology='Historical growth rate extrapolation'
        )

        logger.info(f"Growth prediction: {projected_growth:+.1f}% over {timeframe_months} months")

        return prediction

    async def predict_resource_needs(
        self,
        organization: Organization,
        time_series: Optional[List[MetricSeries]] = None,
        timeframe_months: int = 12
    ) -> Prediction:
        """
        Predict future resource needs (staff, budget)

        Args:
            organization: Organization digital twin
            time_series: Historical resource metrics
            timeframe_months: Months to predict ahead

        Returns:
            Prediction with resource requirements
        """
        logger.info(f"Predicting resource needs for {organization.name}")

        current_staff = organization.employee_count or 10
        current_budget = organization.annual_budget or organization.annual_revenue or 100000

        # Growth assumptions
        expected_growth_rate = 0.05  # 5% default

        if time_series:
            # Calculate actual growth trend
            revenue_metrics = [m for m in time_series if m.metric_name in ['revenue', 'budget']]
            if revenue_metrics and len(revenue_metrics[0].points) >= 2:
                points = revenue_metrics[0].points
                first = points[0].value
                last = points[-1].value
                if first > 0:
                    expected_growth_rate = (last - first) / first

        # Project resources needed
        years = timeframe_months / 12
        projected_budget = current_budget * (1 + expected_growth_rate * years)
        projected_staff = current_staff * (1 + expected_growth_rate * 0.8 * years)  # Staff grows slower

        # Total resource index
        resource_index = (projected_budget / 100000) + (projected_staff * 10)

        prediction = Prediction(
            twin_id=organization.twin_id,
            prediction_type='resource_needs',
            timeframe_months=timeframe_months,
            predicted_value=resource_index,
            confidence=0.65,
            lower_bound=resource_index * 0.85,
            upper_bound=resource_index * 1.15,
            assumptions=[
                f'Growth rate: {expected_growth_rate:.1%}',
                'Staff growth lags revenue growth',
                'No major operational changes'
            ],
            factors={
                'projected_budget': projected_budget,
                'projected_staff': int(projected_staff),
                'current_budget': current_budget,
                'current_staff': current_staff
            },
            methodology='Resource scaling model based on growth projections'
        )

        logger.info(
            f"Resource prediction: {int(projected_staff)} staff, "
            f"${projected_budget:,.0f} budget"
        )

        return prediction

    # ============================================
    # HELPER METHODS
    # ============================================

    def _linear_forecast(
        self,
        points: List[MetricPoint],
        timeframe_months: int
    ) -> tuple[float, float, float, float]:
        """
        Simple linear regression forecast

        Returns: (predicted_value, confidence, lower_bound, upper_bound)
        """
        if len(points) < 2:
            value = points[0].value if points else 0
            return value, 0.3, value * 0.9, value * 1.1

        # Extract values
        values = [p.value for p in points]

        # Calculate trend (simple slope)
        n = len(values)
        x = list(range(n))
        y = values

        # Linear regression: y = mx + b
        x_mean = mean(x)
        y_mean = mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            # No trend
            return y_mean, 0.5, y_mean * 0.9, y_mean * 1.1

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Project forward
        future_x = n + (timeframe_months / 12) * (n / max(1, len(points)))  # Scale by data density
        predicted_value = slope * future_x + intercept

        # Confidence based on R²
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))

        if ss_tot == 0:
            r_squared = 0
        else:
            r_squared = 1 - (ss_res / ss_tot)

        confidence = max(0.3, min(0.95, r_squared))

        # Bounds based on variance
        if len(values) > 2:
            std = stdev(values)
            lower_bound = predicted_value - (std * 1.5)
            upper_bound = predicted_value + (std * 1.5)
        else:
            lower_bound = predicted_value * 0.8
            upper_bound = predicted_value * 1.2

        return predicted_value, confidence, lower_bound, upper_bound

    def _calculate_volatility(self, points: List[MetricPoint]) -> float:
        """Calculate volatility (standard deviation / mean)"""
        if len(points) < 2:
            return 0.0

        values = [p.value for p in points]
        avg = mean(values)

        if avg == 0:
            return 0.0

        std = stdev(values)
        return std / avg

    def _assess_financial_stability(self, organization: Organization) -> float:
        """Assess financial stability (0-100)"""
        score = 50.0

        # Revenue/budget presence
        if organization.annual_revenue or organization.annual_budget:
            score += 20

        # Size indicator
        revenue = organization.annual_revenue or organization.annual_budget or 0
        if revenue > 1000000:
            score += 20
        elif revenue > 100000:
            score += 10

        # Maturity
        score += organization.maturity_level * 2

        return min(score, 100)

    def _create_baseline_prediction(
        self,
        organization: Organization,
        prediction_type: str,
        timeframe_months: int,
        value: float,
        confidence: float,
        assumptions: List[str]
    ) -> Prediction:
        """Create a baseline prediction with minimal data"""
        return Prediction(
            twin_id=organization.twin_id,
            prediction_type=prediction_type,
            timeframe_months=timeframe_months,
            predicted_value=value,
            confidence=confidence,
            lower_bound=value * 0.8,
            upper_bound=value * 1.2,
            assumptions=assumptions,
            factors={'data_availability': 'limited'},
            methodology='Baseline estimation'
        )

    async def _predict_impact_baseline(
        self,
        organization: Organization,
        timeframe_months: int
    ) -> Prediction:
        """Baseline impact prediction without historical data"""
        current_impact = organization.health_score or 50

        # Factor in maturity
        maturity_bonus = organization.maturity_level * 3
        predicted_impact = min(current_impact + maturity_bonus, 100)

        return Prediction(
            twin_id=organization.twin_id,
            prediction_type='impact',
            timeframe_months=timeframe_months,
            predicted_value=predicted_impact,
            confidence=0.5,
            lower_bound=max(current_impact * 0.9, 0),
            upper_bound=min(predicted_impact * 1.1, 100),
            assumptions=[
                'Based on current state and maturity',
                'Assumes gradual improvement',
                'No historical trend data'
            ],
            factors={
                'current_impact': current_impact,
                'maturity_level': organization.maturity_level
            },
            methodology='Maturity-adjusted baseline'
        )
