"""
Risk Service - Business Logic Layer
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import random
import numpy as np

from models.domain import (
    Risk,
    RiskReport,
    FAIRAnalysis,
    MonteCarloSimulation,
    RiskTreatmentPlan,
    RiskCategory,
    RiskLikelihood,
    RiskImpact,
    RiskStatus,
    TreatmentStrategy
)
from repositories.repository import RiskRepository


class RiskService:
    """Business logic for Risk Management"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RiskRepository(db)

    # =========================================================================
    # Risk CRUD
    # =========================================================================

    async def create_risk(self, risk: Risk) -> Risk:
        """Create new risk assessment"""
        db_risk = await self.repo.create(risk)
        return self._map_to_domain(db_risk)

    async def get_risk(self, risk_id: UUID) -> Optional[Risk]:
        """Get risk by ID"""
        db_risk = await self.repo.get_by_id(risk_id)
        if not db_risk:
            return None
        return self._map_to_domain(db_risk)

    async def list_risks(
        self,
        organization_id: UUID,
        category: Optional[str] = None,
        status: Optional[str] = None,
        min_score: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Risk]:
        """List risks with filters"""
        db_risks = await self.repo.list_by_organization(
            organization_id=organization_id,
            category=category,
            status=status,
            min_score=min_score,
            skip=skip,
            limit=limit
        )
        return [self._map_to_domain(r) for r in db_risks]

    async def update_risk(self, risk_id: UUID, risk_update: Risk) -> Optional[Risk]:
        """Update risk"""
        db_risk = await self.repo.update(risk_id, risk_update)
        if not db_risk:
            return None
        return self._map_to_domain(db_risk)

    async def delete_risk(self, risk_id: UUID) -> bool:
        """Delete risk"""
        return await self.repo.delete(risk_id)

    # =========================================================================
    # FAIR Analysis
    # =========================================================================

    async def perform_fair_analysis(self, risk_id: UUID, fair_data: FAIRAnalysis) -> FAIRAnalysis:
        """
        Perform FAIR (Factor Analysis of Information Risk) quantitative analysis

        FAIR Formula:
        - Loss Event Frequency (LEF) = Threat Event Frequency (TEF) × Vulnerability (V)
        - Annual Loss Expectancy (ALE) = LEF × Average Loss Magnitude
        """
        # Get risk to validate it exists and get organization_id
        db_risk = await self.repo.get_by_id(risk_id)
        if not db_risk:
            raise ValueError(f"Risk {risk_id} not found")

        # VALIDATE INPUT DATA
        if fair_data.threat_event_frequency <= 0:
            raise ValueError("Threat event frequency must be positive")

        if not (0 <= fair_data.vulnerability_score <= 1):
            raise ValueError("Vulnerability score must be between 0 and 1")

        # Validate triangular distribution parameters for primary loss
        if not (fair_data.primary_loss_min <= fair_data.primary_loss_most_likely <= fair_data.primary_loss_max):
            raise ValueError(
                f"Invalid primary loss distribution: min ({fair_data.primary_loss_min}) <= "
                f"most_likely ({fair_data.primary_loss_most_likely}) <= max ({fair_data.primary_loss_max})"
            )

        # Validate non-negative loss values
        if fair_data.primary_loss_min < 0 or fair_data.primary_loss_max < 0:
            raise ValueError("Primary loss values must be non-negative")

        if fair_data.secondary_loss_min < 0 or fair_data.secondary_loss_max < 0:
            raise ValueError("Secondary loss values must be non-negative")

        if fair_data.secondary_loss_min > fair_data.secondary_loss_max:
            raise ValueError(
                f"Invalid secondary loss range: min ({fair_data.secondary_loss_min}) > "
                f"max ({fair_data.secondary_loss_max})"
            )

        # Calculate Loss Event Frequency
        lef = fair_data.threat_event_frequency * fair_data.vulnerability_score

        # Calculate Average Loss Magnitude (using PERT: (min + 4*most_likely + max) / 6)
        avg_primary_loss = (
            fair_data.primary_loss_min +
            4 * fair_data.primary_loss_most_likely +
            fair_data.primary_loss_max
        ) / 6

        avg_secondary_loss = (fair_data.secondary_loss_min + fair_data.secondary_loss_max) / 2

        avg_total_loss = avg_primary_loss + avg_secondary_loss

        # Calculate Annual Loss Expectancy
        ale = lef * avg_total_loss

        # Determine risk rating based on ALE
        risk_rating = self._calculate_fair_risk_rating(ale)

        # Calculate confidence intervals (simplified - using ±20% of ALE)
        confidence_low = ale * 0.8
        confidence_high = ale * 1.2

        # Update FAIR analysis
        fair_data.loss_event_frequency = lef
        fair_data.annual_loss_expectancy = ale
        fair_data.risk_rating = risk_rating
        fair_data.confidence_interval_low = confidence_low
        fair_data.confidence_interval_high = confidence_high

        # Save to database
        db_analysis = await self.repo.create_fair_analysis(fair_data, db_risk.organization_id)

        return self._map_fair_to_domain(db_analysis)

    async def get_fair_analysis(self, risk_id: UUID) -> Optional[FAIRAnalysis]:
        """Get latest FAIR analysis"""
        db_analysis = await self.repo.get_fair_analysis(risk_id)
        if not db_analysis:
            return None
        return self._map_fair_to_domain(db_analysis)

    def _calculate_fair_risk_rating(self, ale: float) -> str:
        """Calculate risk rating from ALE"""
        if ale < 10000:
            return "low"
        elif ale < 100000:
            return "medium"
        elif ale < 1000000:
            return "high"
        else:
            return "critical"

    # =========================================================================
    # Monte Carlo Simulation
    # =========================================================================

    async def run_monte_carlo(self, risk_id: UUID, simulation: MonteCarloSimulation) -> MonteCarloSimulation:
        """
        Run Monte Carlo simulation for risk

        Simulates thousands of scenarios with variable inputs
        to produce probability distribution of outcomes
        """
        # Get risk to validate and get organization_id
        db_risk = await self.repo.get_by_id(risk_id)
        if not db_risk:
            raise ValueError(f"Risk {risk_id} not found")

        # VALIDATE SIMULATION PARAMETERS
        if simulation.iterations <= 0:
            raise ValueError("Number of iterations must be positive")

        if simulation.iterations > 1000000:
            raise ValueError("Number of iterations cannot exceed 1,000,000")

        if not simulation.factors or len(simulation.factors) == 0:
            raise ValueError("At least one factor must be provided for simulation")

        # Validate each factor BEFORE running simulation
        for idx, factor in enumerate(simulation.factors):
            min_val = factor.get('min', 0)
            most_likely = factor.get('most_likely', 0)
            max_val = factor.get('max', 0)

            # Validate triangular distribution parameters
            if not (min_val <= most_likely <= max_val):
                raise ValueError(
                    f"Invalid triangular distribution for factor {idx}: "
                    f"min ({min_val}) <= most_likely ({most_likely}) <= max ({max_val})"
                )

            # Validate non-negative loss values
            if min_val < 0 or max_val < 0:
                raise ValueError(f"Loss values for factor {idx} must be non-negative")

            # Warn if most_likely is exactly at min or max (degenerate distribution)
            if most_likely == min_val == max_val:
                logger = logging.getLogger(__name__)
                logger.warning(f"Factor {idx} has constant value {min_val} (no variation)")

        # Run simulation
        iterations = simulation.iterations
        results = []

        for _ in range(iterations):
            # Simulate each factor with random variation
            scenario_loss = 0
            for factor in simulation.factors:
                # Use triangular distribution (min, most_likely, max)
                min_val = factor.get('min', 0)
                most_likely = factor.get('most_likely', 0)
                max_val = factor.get('max', 0)

                # Generate random value using triangular distribution
                value = np.random.triangular(min_val, most_likely, max_val)
                scenario_loss += value

            results.append(scenario_loss)

        # Calculate statistics
        results_array = np.array(results)
        mean_loss = float(np.mean(results_array))
        median_loss = float(np.median(results_array))
        percentile_95 = float(np.percentile(results_array, 95))
        percentile_99 = float(np.percentile(results_array, 99))

        # Create distribution data (histogram)
        hist, bin_edges = np.histogram(results_array, bins=50)
        distribution_data = {
            "histogram": hist.tolist(),
            "bin_edges": bin_edges.tolist(),
            "min": float(np.min(results_array)),
            "max": float(np.max(results_array)),
            "std_dev": float(np.std(results_array))
        }

        # Update simulation results
        simulation.mean_loss = mean_loss
        simulation.median_loss = median_loss
        simulation.percentile_95 = percentile_95
        simulation.percentile_99 = percentile_99
        simulation.distribution_data = distribution_data

        # Save to database
        db_sim = await self.repo.create_monte_carlo(simulation, db_risk.organization_id)

        return self._map_monte_carlo_to_domain(db_sim)

    async def get_monte_carlo_results(self, risk_id: UUID) -> Optional[MonteCarloSimulation]:
        """Get latest Monte Carlo results"""
        db_sim = await self.repo.get_monte_carlo(risk_id)
        if not db_sim:
            return None
        return self._map_monte_carlo_to_domain(db_sim)

    # =========================================================================
    # Treatment Plans
    # =========================================================================

    async def create_treatment_plan(self, risk_id: UUID, plan: RiskTreatmentPlan) -> RiskTreatmentPlan:
        """Create treatment plan"""
        # Get risk to validate and get organization_id
        db_risk = await self.repo.get_by_id(risk_id)
        if not db_risk:
            raise ValueError(f"Risk {risk_id} not found")

        plan.risk_id = risk_id
        db_plan = await self.repo.create_treatment_plan(plan, db_risk.organization_id)

        return self._map_treatment_plan_to_domain(db_plan)

    async def list_treatment_plans(self, risk_id: UUID) -> List[RiskTreatmentPlan]:
        """List treatment plans for risk"""
        db_plans = await self.repo.list_treatment_plans(risk_id)
        return [self._map_treatment_plan_to_domain(p) for p in db_plans]

    async def update_treatment_plan(self, plan_id: UUID, plan_update: RiskTreatmentPlan) -> Optional[RiskTreatmentPlan]:
        """Update treatment plan"""
        db_plan = await self.repo.update_treatment_plan(plan_id, plan_update)
        if not db_plan:
            return None
        return self._map_treatment_plan_to_domain(db_plan)

    # =========================================================================
    # Reports & Analytics
    # =========================================================================

    async def generate_risk_report(self, organization_id: UUID) -> RiskReport:
        """Generate comprehensive risk report"""
        # Get statistics
        stats = await self.repo.get_risk_stats(organization_id)

        # Get top risks
        top_risks_db = await self.repo.get_top_risks(organization_id, limit=10)
        top_risks = [self._map_to_domain(r) for r in top_risks_db]

        # Get category breakdown
        risks_by_category = await self.repo.get_risks_by_category(organization_id)

        # Get status breakdown
        risks_by_status = await self.repo.get_risks_by_status(organization_id)

        # Get trend data (last 90 days)
        trend_data = await self.get_risk_trends(organization_id, days=90)

        return RiskReport(
            organization_id=organization_id,
            total_risks=stats["total"],
            critical_risks=stats["critical"],
            high_risks=stats["high"],
            medium_risks=stats["medium"],
            low_risks=stats["low"],
            top_risks=top_risks,
            risks_by_category=risks_by_category,
            risks_by_status=risks_by_status,
            trend_data=trend_data,
            generated_at=datetime.utcnow(),
            generated_by=None
        )

    async def get_risk_heat_map(self, organization_id: UUID) -> Dict[str, Any]:
        """Generate risk heat map (5x5 matrix)"""
        risks = await self.repo.list_by_organization(organization_id)

        # Create 5x5 matrix
        matrix = [[0 for _ in range(5)] for _ in range(5)]

        for risk in risks:
            if risk.likelihood and risk.impact:
                # Likelihood on Y-axis (1-5), Impact on X-axis (1-5)
                # Convert to 0-indexed
                y = risk.likelihood - 1
                x = risk.impact - 1
                matrix[y][x] += 1

        return {
            "organization_id": str(organization_id),
            "matrix": matrix,
            "labels": {
                "x_axis": "Impact",
                "y_axis": "Likelihood",
                "levels": ["Insignificant", "Minor", "Moderate", "Major", "Catastrophic"]
            }
        }

    async def get_risk_trends(self, organization_id: UUID, days: int = 90) -> Dict[str, Any]:
        """
        Get risk trends over time

        Analyzes risk history to show:
        - Daily/weekly risk counts by severity
        - Average risk score trends
        - New vs resolved risks over time
        """
        # Get historical data grouped by date
        history = await self.repo.get_risk_history(organization_id, days)

        # Get current statistics
        current_stats = await self.repo.get_risk_stats(organization_id)

        # Calculate trends (empty data handling)
        if not history:
            return {
                "organization_id": str(organization_id),
                "period_days": days,
                "start_date": (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d'),
                "end_date": datetime.utcnow().strftime('%Y-%m-%d'),
                "daily_data": [],
                "summary": {
                    "total_risks": {
                        "current": current_stats.get("total", 0),
                        "change": 0,
                        "change_percent": 0
                    },
                    "critical_risks": {
                        "current": current_stats.get("critical", 0),
                        "change": 0,
                        "change_percent": 0
                    },
                    "high_risks": {
                        "current": current_stats.get("high", 0),
                        "change": 0,
                        "change_percent": 0
                    },
                    "medium_risks": {
                        "current": current_stats.get("medium", 0),
                        "change": 0,
                        "change_percent": 0
                    },
                    "low_risks": {
                        "current": current_stats.get("low", 0),
                        "change": 0,
                        "change_percent": 0
                    },
                    "avg_risk_score": {
                        "current": 0,
                        "change": 0
                    }
                },
                "activity": {
                    "total_new_risks": 0,
                    "total_resolved_risks": 0,
                    "net_change": 0
                }
            }

        # Calculate summary statistics
        first_period = history[0] if history else {}
        latest_period = history[-1] if history else {}

        # Calculate changes from first to last period
        total_change = latest_period.get('total_count', 0) - first_period.get('total_count', 0)
        critical_change = latest_period.get('critical_count', 0) - first_period.get('critical_count', 0)
        high_change = latest_period.get('high_count', 0) - first_period.get('high_count', 0)
        medium_change = latest_period.get('medium_count', 0) - first_period.get('medium_count', 0)
        low_change = latest_period.get('low_count', 0) - first_period.get('low_count', 0)
        avg_score_change = latest_period.get('avg_risk_score', 0) - first_period.get('avg_risk_score', 0)

        # Calculate percentage changes
        total_change_pct = (total_change / first_period.get('total_count', 1)) * 100 if first_period.get('total_count', 0) > 0 else 0
        critical_change_pct = (critical_change / first_period.get('critical_count', 1)) * 100 if first_period.get('critical_count', 0) > 0 else 0
        high_change_pct = (high_change / first_period.get('high_count', 1)) * 100 if first_period.get('high_count', 0) > 0 else 0
        medium_change_pct = (medium_change / first_period.get('medium_count', 1)) * 100 if first_period.get('medium_count', 0) > 0 else 0
        low_change_pct = (low_change / first_period.get('low_count', 1)) * 100 if first_period.get('low_count', 0) > 0 else 0

        # Calculate activity totals
        total_new = sum(day.get('new_risks', 0) for day in history)
        total_resolved = sum(day.get('resolved_risks', 0) for day in history)

        return {
            "organization_id": str(organization_id),
            "period_days": days,
            "start_date": history[0]['date'] if history else None,
            "end_date": history[-1]['date'] if history else None,
            "daily_data": history,
            "summary": {
                "total_risks": {
                    "current": current_stats.get("total", 0),
                    "change": total_change,
                    "change_percent": round(total_change_pct, 2)
                },
                "critical_risks": {
                    "current": current_stats.get("critical", 0),
                    "change": critical_change,
                    "change_percent": round(critical_change_pct, 2)
                },
                "high_risks": {
                    "current": current_stats.get("high", 0),
                    "change": high_change,
                    "change_percent": round(high_change_pct, 2)
                },
                "medium_risks": {
                    "current": current_stats.get("medium", 0),
                    "change": medium_change,
                    "change_percent": round(medium_change_pct, 2)
                },
                "low_risks": {
                    "current": current_stats.get("low", 0),
                    "change": low_change,
                    "change_percent": round(low_change_pct, 2)
                },
                "avg_risk_score": {
                    "current": round(latest_period.get('avg_risk_score', 0), 2),
                    "change": round(avg_score_change, 2)
                }
            },
            "activity": {
                "total_new_risks": total_new,
                "total_resolved_risks": total_resolved,
                "net_change": total_new - total_resolved
            }
        }

    # =========================================================================
    # Utilities
    # =========================================================================

    def get_risk_severity(self, score: int) -> str:
        """Get risk severity label from score"""
        if score >= 20:
            return "critical"
        elif score >= 15:
            return "high"
        elif score >= 8:
            return "medium"
        else:
            return "low"

    # =========================================================================
    # Mappers
    # =========================================================================

    def _map_to_domain(self, db_risk) -> Risk:
        """Map database model to domain model"""
        return Risk(
            id=db_risk.id,
            organization_id=db_risk.organization_id,
            risk_title=db_risk.risk_title,
            risk_code=db_risk.risk_code,
            risk_category=RiskCategory(db_risk.risk_category) if db_risk.risk_category else RiskCategory.OPERATIONAL,
            description=db_risk.description,
            threat_source=db_risk.threat_source,
            vulnerabilities=db_risk.vulnerabilities or [],
            likelihood=RiskLikelihood(db_risk.likelihood) if db_risk.likelihood else RiskLikelihood.POSSIBLE,
            impact=RiskImpact(db_risk.impact) if db_risk.impact else RiskImpact.MODERATE,
            inherent_risk_score=db_risk.inherent_risk_score or 0,
            treatment_strategy=TreatmentStrategy(db_risk.treatment_strategy) if db_risk.treatment_strategy else None,
            residual_likelihood=RiskLikelihood(db_risk.residual_likelihood) if db_risk.residual_likelihood else None,
            residual_impact=RiskImpact(db_risk.residual_impact) if db_risk.residual_impact else None,
            residual_risk_score=db_risk.residual_risk_score,
            risk_owner_id=db_risk.risk_owner_id,
            related_processes=db_risk.related_processes or [],
            related_assets=db_risk.related_assets or [],
            status=RiskStatus(db_risk.status) if db_risk.status else RiskStatus.IDENTIFIED,
            last_reviewed_at=db_risk.last_reviewed_at,
            next_review_date=db_risk.next_review_date,
            is_active=db_risk.is_active,
            created_at=db_risk.created_at,
            updated_at=db_risk.updated_at
        )

    def _map_fair_to_domain(self, db_analysis) -> FAIRAnalysis:
        """Map FAIR analysis DB to domain"""
        return FAIRAnalysis(
            risk_id=db_analysis.risk_id,
            threat_event_frequency=float(db_analysis.threat_event_frequency),
            vulnerability_score=float(db_analysis.vulnerability_score / 100),
            loss_event_frequency=float(db_analysis.loss_event_frequency),
            primary_loss_min=float(db_analysis.primary_loss_min),
            primary_loss_max=float(db_analysis.primary_loss_max),
            primary_loss_most_likely=float(db_analysis.primary_loss_most_likely),
            secondary_loss_min=float(db_analysis.secondary_loss_min),
            secondary_loss_max=float(db_analysis.secondary_loss_max),
            annual_loss_expectancy=float(db_analysis.annual_loss_expectancy),
            risk_rating=db_analysis.risk_rating,
            confidence_interval_low=float(db_analysis.confidence_interval_low),
            confidence_interval_high=float(db_analysis.confidence_interval_high),
            analyzed_at=db_analysis.analyzed_at,
            analyzed_by=db_analysis.analyzed_by
        )

    def _map_monte_carlo_to_domain(self, db_sim) -> MonteCarloSimulation:
        """Map Monte Carlo simulation DB to domain"""
        return MonteCarloSimulation(
            risk_id=db_sim.risk_id,
            iterations=db_sim.iterations,
            factors=db_sim.factors,
            mean_loss=float(db_sim.mean_loss),
            median_loss=float(db_sim.median_loss),
            percentile_95=float(db_sim.percentile_95),
            percentile_99=float(db_sim.percentile_99),
            distribution_data=db_sim.distribution_data,
            simulated_at=db_sim.simulated_at
        )

    def _map_treatment_plan_to_domain(self, db_plan) -> RiskTreatmentPlan:
        """Map treatment plan DB to domain"""
        return RiskTreatmentPlan(
            id=db_plan.id,
            risk_id=db_plan.risk_id,
            strategy=TreatmentStrategy(db_plan.strategy) if db_plan.strategy else TreatmentStrategy.MITIGATE,
            description=db_plan.description,
            actions=db_plan.actions,
            responsible_party=db_plan.responsible_party,
            start_date=db_plan.start_date,
            target_date=db_plan.target_date,
            completion_date=db_plan.completion_date,
            estimated_cost=float(db_plan.estimated_cost) if db_plan.estimated_cost else None,
            actual_cost=float(db_plan.actual_cost) if db_plan.actual_cost else None,
            expected_residual_likelihood=RiskLikelihood(db_plan.expected_residual_likelihood) if db_plan.expected_residual_likelihood else None,
            expected_residual_impact=RiskImpact(db_plan.expected_residual_impact) if db_plan.expected_residual_impact else None,
            status=db_plan.status,
            created_at=db_plan.created_at,
            updated_at=db_plan.updated_at
        )
