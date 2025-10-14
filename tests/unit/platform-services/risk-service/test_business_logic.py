"""
Test Risk Service Business Logic Layer
Tests all business methods including risk trends, FAIR analysis, and Monte Carlo simulations
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timedelta
import numpy as np

from services.business_logic import RiskService
from repositories.repository import RiskRepository
from models.domain import (
    Risk,
    RiskCategory,
    RiskLikelihood,
    RiskImpact,
    RiskStatus,
    TreatmentStrategy,
    FAIRAnalysis,
    MonteCarloSimulation,
    RiskTreatmentPlan,
    RiskReport
)
from models.database import RiskDB, FAIRAnalysisDB, MonteCarloSimulationDB


# =============================================================================
# Risk CRUD Business Logic Tests
# =============================================================================

class TestRiskServiceCRUD:
    """Test Risk Service CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_risk(self, db_session, sample_risk):
        """Test creating risk through service"""
        service = RiskService(db_session)

        result = await service.create_risk(sample_risk)

        assert result is not None
        assert result.risk_title == sample_risk.risk_title
        assert result.inherent_risk_score == 12

    @pytest.mark.asyncio
    async def test_get_risk(self, db_session, sample_risk):
        """Test retrieving risk through service"""
        service = RiskService(db_session)

        # Create risk
        created = await service.create_risk(sample_risk)

        # Get risk
        result = await service.get_risk(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.risk_title == sample_risk.risk_title

    @pytest.mark.asyncio
    async def test_get_nonexistent_risk(self, db_session):
        """Test getting non-existent risk returns None"""
        service = RiskService(db_session)

        result = await service.get_risk(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_list_risks(self, db_session, test_organization_id):
        """Test listing risks through service"""
        service = RiskService(db_session)

        # Create risks
        for i in range(3):
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {i}",
                risk_category=RiskCategory.OPERATIONAL,
                description=f"Description {i}",
                likelihood=RiskLikelihood.POSSIBLE,
                impact=RiskImpact.MODERATE,
                inherent_risk_score=9,
                status=RiskStatus.IDENTIFIED
            )
            await service.create_risk(risk)

        # List risks
        results = await service.list_risks(test_organization_id)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_update_risk(self, db_session, sample_risk):
        """Test updating risk through service"""
        service = RiskService(db_session)

        # Create risk
        created = await service.create_risk(sample_risk)

        # Update risk
        sample_risk.risk_title = "Updated Title"
        sample_risk.status = RiskStatus.MONITORING

        updated = await service.update_risk(created.id, sample_risk)

        assert updated is not None
        assert updated.risk_title == "Updated Title"
        assert updated.status == RiskStatus.MONITORING

    @pytest.mark.asyncio
    async def test_delete_risk(self, db_session, sample_risk):
        """Test deleting risk through service"""
        service = RiskService(db_session)

        # Create risk
        created = await service.create_risk(sample_risk)

        # Delete risk
        success = await service.delete_risk(created.id)

        assert success is True

        # Verify deletion
        deleted = await service.get_risk(created.id)
        assert deleted is None


# =============================================================================
# FAIR Analysis Business Logic Tests
# =============================================================================

class TestFAIRAnalysis:
    """Test FAIR Analysis business logic"""

    @pytest.mark.asyncio
    async def test_perform_fair_analysis(self, db_session, sample_risk, sample_fair_analysis):
        """Test performing FAIR analysis with valid data"""
        service = RiskService(db_session)

        # Create risk first
        created_risk = await service.create_risk(sample_risk)
        sample_fair_analysis.risk_id = created_risk.id

        # Perform FAIR analysis
        result = await service.perform_fair_analysis(created_risk.id, sample_fair_analysis)

        assert result is not None
        assert result.risk_id == created_risk.id
        assert result.loss_event_frequency > 0  # Should be calculated
        assert result.annual_loss_expectancy > 0  # Should be calculated
        assert result.risk_rating in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_fair_analysis_calculations(self, db_session, sample_risk):
        """Test FAIR analysis calculation accuracy"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create FAIR analysis with known values
        fair_data = FAIRAnalysis(
            risk_id=created_risk.id,
            threat_event_frequency=10.0,  # 10 threats per year
            vulnerability_score=0.5,  # 50% vulnerability
            primary_loss_min=10000.0,
            primary_loss_max=100000.0,
            primary_loss_most_likely=50000.0,
            secondary_loss_min=5000.0,
            secondary_loss_max=20000.0
        )

        result = await service.perform_fair_analysis(created_risk.id, fair_data)

        # Loss Event Frequency = TEF * VS = 10 * 0.5 = 5
        assert result.loss_event_frequency == 5.0

        # Verify ALE is calculated
        assert result.annual_loss_expectancy > 0

        # Verify confidence intervals
        assert result.confidence_interval_low < result.annual_loss_expectancy
        assert result.confidence_interval_high > result.annual_loss_expectancy

    @pytest.mark.asyncio
    async def test_fair_analysis_invalid_threat_frequency(self, db_session, sample_risk):
        """Test FAIR analysis with invalid threat frequency"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create FAIR analysis with invalid threat frequency
        fair_data = FAIRAnalysis(
            risk_id=created_risk.id,
            threat_event_frequency=0.0,  # Invalid: must be positive
            vulnerability_score=0.5,
            primary_loss_min=10000.0,
            primary_loss_max=100000.0,
            primary_loss_most_likely=50000.0,
            secondary_loss_min=5000.0,
            secondary_loss_max=20000.0
        )

        with pytest.raises(ValueError, match="Threat event frequency must be positive"):
            await service.perform_fair_analysis(created_risk.id, fair_data)

    @pytest.mark.asyncio
    async def test_fair_analysis_invalid_vulnerability_score(self, db_session, sample_risk):
        """Test FAIR analysis with invalid vulnerability score"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create FAIR analysis with invalid vulnerability score
        fair_data = FAIRAnalysis(
            risk_id=created_risk.id,
            threat_event_frequency=10.0,
            vulnerability_score=1.5,  # Invalid: must be between 0 and 1
            primary_loss_min=10000.0,
            primary_loss_max=100000.0,
            primary_loss_most_likely=50000.0,
            secondary_loss_min=5000.0,
            secondary_loss_max=20000.0
        )

        with pytest.raises(ValueError, match="Vulnerability score must be between 0 and 1"):
            await service.perform_fair_analysis(created_risk.id, fair_data)

    @pytest.mark.asyncio
    async def test_fair_analysis_invalid_loss_distribution(self, db_session, sample_risk):
        """Test FAIR analysis with invalid loss distribution"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create FAIR analysis with invalid triangular distribution
        fair_data = FAIRAnalysis(
            risk_id=created_risk.id,
            threat_event_frequency=10.0,
            vulnerability_score=0.5,
            primary_loss_min=100000.0,  # Min > most_likely (invalid)
            primary_loss_max=200000.0,
            primary_loss_most_likely=50000.0,
            secondary_loss_min=5000.0,
            secondary_loss_max=20000.0
        )

        with pytest.raises(ValueError, match="Invalid primary loss distribution"):
            await service.perform_fair_analysis(created_risk.id, fair_data)

    @pytest.mark.asyncio
    async def test_fair_analysis_risk_rating_low(self, db_session, sample_risk):
        """Test FAIR analysis risk rating for low ALE"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create FAIR analysis that should result in low rating
        fair_data = FAIRAnalysis(
            risk_id=created_risk.id,
            threat_event_frequency=1.0,
            vulnerability_score=0.1,
            primary_loss_min=100.0,
            primary_loss_max=1000.0,
            primary_loss_most_likely=500.0,
            secondary_loss_min=0.0,
            secondary_loss_max=100.0
        )

        result = await service.perform_fair_analysis(created_risk.id, fair_data)

        assert result.risk_rating == "low"

    @pytest.mark.asyncio
    async def test_fair_analysis_risk_rating_critical(self, db_session, sample_risk):
        """Test FAIR analysis risk rating for critical ALE"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create FAIR analysis that should result in critical rating
        fair_data = FAIRAnalysis(
            risk_id=created_risk.id,
            threat_event_frequency=100.0,
            vulnerability_score=0.8,
            primary_loss_min=100000.0,
            primary_loss_max=10000000.0,
            primary_loss_most_likely=5000000.0,
            secondary_loss_min=50000.0,
            secondary_loss_max=1000000.0
        )

        result = await service.perform_fair_analysis(created_risk.id, fair_data)

        assert result.risk_rating == "critical"

    @pytest.mark.asyncio
    async def test_get_fair_analysis(self, db_session, sample_risk, sample_fair_analysis):
        """Test retrieving FAIR analysis"""
        service = RiskService(db_session)

        # Create risk and FAIR analysis
        created_risk = await service.create_risk(sample_risk)
        sample_fair_analysis.risk_id = created_risk.id
        await service.perform_fair_analysis(created_risk.id, sample_fair_analysis)

        # Retrieve FAIR analysis
        result = await service.get_fair_analysis(created_risk.id)

        assert result is not None
        assert result.risk_id == created_risk.id


# =============================================================================
# Monte Carlo Simulation Business Logic Tests
# =============================================================================

class TestMonteCarloSimulation:
    """Test Monte Carlo Simulation business logic"""

    @pytest.mark.asyncio
    async def test_run_monte_carlo(self, db_session, sample_risk, sample_monte_carlo):
        """Test running Monte Carlo simulation"""
        service = RiskService(db_session)

        # Create risk first
        created_risk = await service.create_risk(sample_risk)
        sample_monte_carlo.risk_id = created_risk.id

        # Run simulation
        result = await service.run_monte_carlo(created_risk.id, sample_monte_carlo)

        assert result is not None
        assert result.risk_id == created_risk.id
        assert result.mean_loss > 0
        assert result.median_loss > 0
        assert result.percentile_95 > result.median_loss
        assert result.percentile_99 > result.percentile_95
        assert result.distribution_data is not None

    @pytest.mark.asyncio
    async def test_monte_carlo_statistics(self, db_session, sample_risk):
        """Test Monte Carlo simulation statistics"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create simulation with simple factors
        simulation = MonteCarloSimulation(
            risk_id=created_risk.id,
            iterations=10000,
            factors=[
                {"name": "Loss", "min": 10000, "most_likely": 50000, "max": 100000}
            ]
        )

        result = await service.run_monte_carlo(created_risk.id, simulation)

        # Verify statistics are in reasonable range
        assert 10000 <= result.mean_loss <= 100000
        assert 10000 <= result.median_loss <= 100000
        assert result.percentile_95 > result.mean_loss
        assert result.distribution_data.get("min") >= 10000
        assert result.distribution_data.get("max") <= 100000

    @pytest.mark.asyncio
    async def test_monte_carlo_invalid_iterations_negative(self, db_session, sample_risk):
        """Test Monte Carlo with invalid iterations (negative)"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create simulation with invalid iterations
        simulation = MonteCarloSimulation(
            risk_id=created_risk.id,
            iterations=0,  # Invalid
            factors=[{"name": "Loss", "min": 1000, "most_likely": 5000, "max": 10000}]
        )

        with pytest.raises(ValueError, match="Number of iterations must be positive"):
            await service.run_monte_carlo(created_risk.id, simulation)

    @pytest.mark.asyncio
    async def test_monte_carlo_invalid_iterations_too_high(self, db_session, sample_risk):
        """Test Monte Carlo with too many iterations"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create simulation with too many iterations
        simulation = MonteCarloSimulation(
            risk_id=created_risk.id,
            iterations=2000000,  # Exceeds max
            factors=[{"name": "Loss", "min": 1000, "most_likely": 5000, "max": 10000}]
        )

        with pytest.raises(ValueError, match="Number of iterations cannot exceed"):
            await service.run_monte_carlo(created_risk.id, simulation)

    @pytest.mark.asyncio
    async def test_monte_carlo_no_factors(self, db_session, sample_risk):
        """Test Monte Carlo with no factors"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create simulation with no factors
        simulation = MonteCarloSimulation(
            risk_id=created_risk.id,
            iterations=10000,
            factors=[]  # No factors
        )

        with pytest.raises(ValueError, match="At least one factor must be provided"):
            await service.run_monte_carlo(created_risk.id, simulation)

    @pytest.mark.asyncio
    async def test_monte_carlo_invalid_factor_distribution(self, db_session, sample_risk):
        """Test Monte Carlo with invalid factor distribution"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create simulation with invalid triangular distribution
        simulation = MonteCarloSimulation(
            risk_id=created_risk.id,
            iterations=10000,
            factors=[
                {"name": "Loss", "min": 10000, "most_likely": 5000, "max": 20000}  # most_likely < min
            ]
        )

        with pytest.raises(ValueError, match="Invalid triangular distribution"):
            await service.run_monte_carlo(created_risk.id, simulation)

    @pytest.mark.asyncio
    async def test_get_monte_carlo_results(self, db_session, sample_risk, sample_monte_carlo):
        """Test retrieving Monte Carlo results"""
        service = RiskService(db_session)

        # Create risk and run simulation
        created_risk = await service.create_risk(sample_risk)
        sample_monte_carlo.risk_id = created_risk.id
        await service.run_monte_carlo(created_risk.id, sample_monte_carlo)

        # Retrieve results
        result = await service.get_monte_carlo_results(created_risk.id)

        assert result is not None
        assert result.risk_id == created_risk.id


# =============================================================================
# Treatment Plan Business Logic Tests
# =============================================================================

class TestTreatmentPlanService:
    """Test Treatment Plan service operations"""

    @pytest.mark.asyncio
    async def test_create_treatment_plan(self, db_session, sample_risk, sample_treatment_plan):
        """Test creating treatment plan"""
        service = RiskService(db_session)

        # Create risk first
        created_risk = await service.create_risk(sample_risk)

        # Create treatment plan
        result = await service.create_treatment_plan(created_risk.id, sample_treatment_plan)

        assert result is not None
        assert result.risk_id == created_risk.id
        assert result.strategy == sample_treatment_plan.strategy

    @pytest.mark.asyncio
    async def test_list_treatment_plans(self, db_session, sample_risk):
        """Test listing treatment plans"""
        service = RiskService(db_session)

        # Create risk
        created_risk = await service.create_risk(sample_risk)

        # Create multiple treatment plans
        for i in range(3):
            plan = RiskTreatmentPlan(
                risk_id=created_risk.id,
                strategy=TreatmentStrategy.MITIGATE,
                description=f"Plan {i}",
                status="planned"
            )
            await service.create_treatment_plan(created_risk.id, plan)

        # List plans
        results = await service.list_treatment_plans(created_risk.id)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_update_treatment_plan(self, db_session, sample_risk, sample_treatment_plan):
        """Test updating treatment plan"""
        service = RiskService(db_session)

        # Create risk and treatment plan
        created_risk = await service.create_risk(sample_risk)
        created_plan = await service.create_treatment_plan(created_risk.id, sample_treatment_plan)

        # Update plan
        sample_treatment_plan.description = "Updated description"
        sample_treatment_plan.status = "completed"

        updated = await service.update_treatment_plan(created_plan.id, sample_treatment_plan)

        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.status == "completed"


# =============================================================================
# Risk Trends Business Logic Tests (NEW)
# =============================================================================

class TestRiskTrends:
    """Test Risk Trends business logic including get_risk_trends()"""

    @pytest.mark.asyncio
    async def test_get_risk_trends_empty_data(self, db_session, test_organization_id):
        """Test get_risk_trends with no historical data"""
        service = RiskService(db_session)

        # Get trends with no data
        result = await service.get_risk_trends(test_organization_id, days=90)

        assert result is not None
        assert result["organization_id"] == str(test_organization_id)
        assert result["period_days"] == 90
        assert result["daily_data"] == []
        assert result["summary"]["total_risks"]["current"] == 0
        assert result["summary"]["total_risks"]["change"] == 0
        assert result["summary"]["total_risks"]["change_percent"] == 0
        assert result["activity"]["total_new_risks"] == 0
        assert result["activity"]["total_resolved_risks"] == 0

    @pytest.mark.asyncio
    async def test_get_risk_trends_with_data(self, db_session, test_organization_id):
        """Test get_risk_trends with historical data"""
        service = RiskService(db_session)

        # Create risks to generate historical data
        for i in range(5):
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {i}",
                risk_category=RiskCategory.OPERATIONAL,
                description="Test risk",
                likelihood=RiskLikelihood.POSSIBLE,
                impact=RiskImpact.MODERATE,
                inherent_risk_score=9,
                status=RiskStatus.IDENTIFIED if i < 3 else RiskStatus.CLOSED
            )
            await service.create_risk(risk)

        # Get trends
        result = await service.get_risk_trends(test_organization_id, days=90)

        assert result is not None
        assert result["organization_id"] == str(test_organization_id)
        assert result["period_days"] == 90
        assert isinstance(result["daily_data"], list)
        assert "summary" in result
        assert "activity" in result

    @pytest.mark.asyncio
    async def test_get_risk_trends_single_day(self, db_session, test_organization_id):
        """Test get_risk_trends with single day of data"""
        service = RiskService(db_session)

        # Create risk
        risk = Risk(
            organization_id=test_organization_id,
            risk_title="Single Day Risk",
            risk_category=RiskCategory.CYBERSECURITY,
            description="Test risk",
            likelihood=RiskLikelihood.LIKELY,
            impact=RiskImpact.MAJOR,
            inherent_risk_score=16,
            status=RiskStatus.IDENTIFIED
        )
        await service.create_risk(risk)

        # Get trends
        result = await service.get_risk_trends(test_organization_id, days=7)

        assert result is not None
        assert result["period_days"] == 7

    @pytest.mark.asyncio
    async def test_get_risk_trends_multiple_days(self, db_session, test_organization_id):
        """Test get_risk_trends with multiple days of data"""
        service = RiskService(db_session)

        # Create multiple risks
        for i in range(10):
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {i}",
                risk_category=RiskCategory.OPERATIONAL,
                description="Test risk",
                likelihood=RiskLikelihood((i % 5) + 1),
                impact=RiskImpact((i % 5) + 1),
                inherent_risk_score=((i % 5) + 1) * ((i % 5) + 1),
                status=RiskStatus.IDENTIFIED
            )
            await service.create_risk(risk)

        # Get trends
        result = await service.get_risk_trends(test_organization_id, days=30)

        assert result is not None
        assert "summary" in result
        assert "total_risks" in result["summary"]
        assert "critical_risks" in result["summary"]
        assert "high_risks" in result["summary"]
        assert "medium_risks" in result["summary"]
        assert "low_risks" in result["summary"]

    @pytest.mark.asyncio
    async def test_get_risk_trends_different_periods(self, db_session, test_organization_id):
        """Test get_risk_trends with different time periods"""
        service = RiskService(db_session)

        # Create risk
        risk = Risk(
            organization_id=test_organization_id,
            risk_title="Test Risk",
            risk_category=RiskCategory.OPERATIONAL,
            description="Test risk",
            likelihood=RiskLikelihood.POSSIBLE,
            impact=RiskImpact.MODERATE,
            inherent_risk_score=9,
            status=RiskStatus.IDENTIFIED
        )
        await service.create_risk(risk)

        # Test different periods
        for days in [7, 30, 90, 365]:
            result = await service.get_risk_trends(test_organization_id, days=days)
            assert result["period_days"] == days


# =============================================================================
# Risk Report Business Logic Tests
# =============================================================================

class TestRiskReports:
    """Test Risk Report generation"""

    @pytest.mark.asyncio
    async def test_generate_risk_report(self, db_session, test_organization_id):
        """Test generating comprehensive risk report"""
        service = RiskService(db_session)

        # Create various risks
        risk_data = [
            (RiskCategory.CYBERSECURITY, RiskLikelihood.ALMOST_CERTAIN, RiskImpact.CATASTROPHIC, RiskStatus.IDENTIFIED, 25),
            (RiskCategory.FINANCIAL, RiskLikelihood.LIKELY, RiskImpact.MAJOR, RiskStatus.ANALYZING, 16),
            (RiskCategory.OPERATIONAL, RiskLikelihood.POSSIBLE, RiskImpact.MODERATE, RiskStatus.TREATED, 9),
            (RiskCategory.COMPLIANCE, RiskLikelihood.UNLIKELY, RiskImpact.MINOR, RiskStatus.CLOSED, 4),
        ]

        for category, likelihood, impact, status, score in risk_data:
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {category.value}",
                risk_category=category,
                description="Test risk",
                likelihood=likelihood,
                impact=impact,
                inherent_risk_score=score,
                status=status
            )
            await service.create_risk(risk)

        # Generate report
        report = await service.generate_risk_report(test_organization_id)

        assert isinstance(report, RiskReport)
        assert report.organization_id == test_organization_id
        assert report.total_risks == 4
        assert report.critical_risks == 1
        assert report.high_risks == 1
        assert report.medium_risks == 1
        assert report.low_risks == 1
        assert len(report.top_risks) > 0
        assert report.risks_by_category is not None
        assert report.risks_by_status is not None
        assert report.trend_data is not None

    @pytest.mark.asyncio
    async def test_generate_risk_report_empty(self, db_session, test_organization_id):
        """Test generating report with no risks"""
        service = RiskService(db_session)

        # Generate report with no risks
        report = await service.generate_risk_report(test_organization_id)

        assert isinstance(report, RiskReport)
        assert report.total_risks == 0
        assert report.critical_risks == 0


# =============================================================================
# Utility Functions Tests
# =============================================================================

class TestUtilities:
    """Test utility functions"""

    def test_get_risk_severity_critical(self, db_session):
        """Test risk severity calculation - critical"""
        service = RiskService(db_session)

        severity = service.get_risk_severity(25)
        assert severity == "critical"

    def test_get_risk_severity_high(self, db_session):
        """Test risk severity calculation - high"""
        service = RiskService(db_session)

        severity = service.get_risk_severity(16)
        assert severity == "high"

    def test_get_risk_severity_medium(self, db_session):
        """Test risk severity calculation - medium"""
        service = RiskService(db_session)

        severity = service.get_risk_severity(9)
        assert severity == "medium"

    def test_get_risk_severity_low(self, db_session):
        """Test risk severity calculation - low"""
        service = RiskService(db_session)

        severity = service.get_risk_severity(4)
        assert severity == "low"

    @pytest.mark.asyncio
    async def test_get_risk_heat_map(self, db_session, test_organization_id):
        """Test risk heat map generation"""
        service = RiskService(db_session)

        # Create risks with different likelihood/impact combinations
        for likelihood in range(1, 6):
            for impact in range(1, 6):
                risk = Risk(
                    organization_id=test_organization_id,
                    risk_title=f"Risk L{likelihood}I{impact}",
                    risk_category=RiskCategory.OPERATIONAL,
                    description="Test risk",
                    likelihood=RiskLikelihood(likelihood),
                    impact=RiskImpact(impact),
                    inherent_risk_score=likelihood * impact,
                    status=RiskStatus.IDENTIFIED
                )
                await service.create_risk(risk)

        # Generate heat map
        heat_map = await service.get_risk_heat_map(test_organization_id)

        assert heat_map is not None
        assert "organization_id" in heat_map
        assert "matrix" in heat_map
        assert len(heat_map["matrix"]) == 5
        assert len(heat_map["matrix"][0]) == 5
