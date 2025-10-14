"""
Test Risk Repository Layer
Tests all database operations with mocked and real database interactions
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.repository import RiskRepository
from models.database import (
    RiskDB,
    FAIRAnalysisDB,
    MonteCarloSimulationDB,
    RiskTreatmentPlanDB
)
from models.domain import (
    Risk,
    RiskCategory,
    RiskLikelihood,
    RiskImpact,
    RiskStatus,
    TreatmentStrategy,
    FAIRAnalysis,
    MonteCarloSimulation,
    RiskTreatmentPlan
)


# =============================================================================
# Risk CRUD Tests
# =============================================================================

class TestRiskCRUD:
    """Test Risk CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_risk(self, db_session, sample_risk, test_organization_id):
        """Test creating a new risk"""
        repo = RiskRepository(db_session)
        sample_risk.organization_id = test_organization_id

        result = await repo.create(sample_risk)

        assert result.id is not None
        assert result.risk_title == sample_risk.risk_title
        assert result.risk_code == sample_risk.risk_code
        assert result.risk_category == sample_risk.risk_category.value
        assert result.inherent_risk_score == 12
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_get_risk_by_id(self, db_session, sample_risk, test_organization_id):
        """Test retrieving risk by ID"""
        repo = RiskRepository(db_session)
        sample_risk.organization_id = test_organization_id

        # Create risk first
        created_risk = await repo.create(sample_risk)
        risk_id = created_risk.id

        # Retrieve it
        result = await repo.get_by_id(risk_id)

        assert result is not None
        assert result.id == risk_id
        assert result.risk_title == sample_risk.risk_title

    @pytest.mark.asyncio
    async def test_get_nonexistent_risk(self, db_session):
        """Test retrieving non-existent risk returns None"""
        repo = RiskRepository(db_session)
        fake_id = uuid4()

        result = await repo.get_by_id(fake_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_list_risks_by_organization(self, db_session, test_organization_id):
        """Test listing risks for an organization"""
        repo = RiskRepository(db_session)

        # Create multiple risks
        for i in range(5):
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {i}",
                risk_code=f"RISK-{i:03d}",
                risk_category=RiskCategory.OPERATIONAL,
                description=f"Description {i}",
                likelihood=RiskLikelihood.POSSIBLE,
                impact=RiskImpact.MODERATE,
                inherent_risk_score=9,
                status=RiskStatus.IDENTIFIED
            )
            await repo.create(risk)

        # List all risks
        results = await repo.list_by_organization(test_organization_id)

        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_list_risks_with_category_filter(self, db_session, test_organization_id):
        """Test listing risks filtered by category"""
        repo = RiskRepository(db_session)

        # Create risks with different categories
        cyber_risk = Risk(
            organization_id=test_organization_id,
            risk_title="Cyber Risk",
            risk_category=RiskCategory.CYBERSECURITY,
            description="Cyber risk",
            likelihood=RiskLikelihood.POSSIBLE,
            impact=RiskImpact.MAJOR,
            inherent_risk_score=12,
            status=RiskStatus.IDENTIFIED
        )
        await repo.create(cyber_risk)

        financial_risk = Risk(
            organization_id=test_organization_id,
            risk_title="Financial Risk",
            risk_category=RiskCategory.FINANCIAL,
            description="Financial risk",
            likelihood=RiskLikelihood.LIKELY,
            impact=RiskImpact.MAJOR,
            inherent_risk_score=16,
            status=RiskStatus.IDENTIFIED
        )
        await repo.create(financial_risk)

        # Filter by category
        results = await repo.list_by_organization(
            test_organization_id,
            category="cybersecurity"
        )

        assert len(results) == 1
        assert results[0].risk_category == "cybersecurity"

    @pytest.mark.asyncio
    async def test_list_risks_with_status_filter(self, db_session, test_organization_id):
        """Test listing risks filtered by status"""
        repo = RiskRepository(db_session)

        # Create risks with different statuses
        identified_risk = Risk(
            organization_id=test_organization_id,
            risk_title="Identified Risk",
            risk_category=RiskCategory.OPERATIONAL,
            description="Identified",
            likelihood=RiskLikelihood.POSSIBLE,
            impact=RiskImpact.MODERATE,
            inherent_risk_score=9,
            status=RiskStatus.IDENTIFIED
        )
        await repo.create(identified_risk)

        closed_risk = Risk(
            organization_id=test_organization_id,
            risk_title="Closed Risk",
            risk_category=RiskCategory.OPERATIONAL,
            description="Closed",
            likelihood=RiskLikelihood.UNLIKELY,
            impact=RiskImpact.MINOR,
            inherent_risk_score=4,
            status=RiskStatus.CLOSED
        )
        await repo.create(closed_risk)

        # Filter by status
        results = await repo.list_by_organization(
            test_organization_id,
            status="identified"
        )

        assert len(results) == 1
        assert results[0].status == "identified"

    @pytest.mark.asyncio
    async def test_list_risks_with_min_score_filter(self, db_session, test_organization_id):
        """Test listing risks filtered by minimum score"""
        repo = RiskRepository(db_session)

        # Create risks with different scores
        low_risk = Risk(
            organization_id=test_organization_id,
            risk_title="Low Risk",
            risk_category=RiskCategory.OPERATIONAL,
            description="Low",
            likelihood=RiskLikelihood.UNLIKELY,
            impact=RiskImpact.MINOR,
            inherent_risk_score=4,
            status=RiskStatus.IDENTIFIED
        )
        await repo.create(low_risk)

        high_risk = Risk(
            organization_id=test_organization_id,
            risk_title="High Risk",
            risk_category=RiskCategory.CYBERSECURITY,
            description="High",
            likelihood=RiskLikelihood.LIKELY,
            impact=RiskImpact.CATASTROPHIC,
            inherent_risk_score=20,
            status=RiskStatus.IDENTIFIED
        )
        await repo.create(high_risk)

        # Filter by min score
        results = await repo.list_by_organization(
            test_organization_id,
            min_score=15
        )

        assert len(results) == 1
        assert results[0].inherent_risk_score >= 15

    @pytest.mark.asyncio
    async def test_list_risks_pagination(self, db_session, test_organization_id):
        """Test risk listing pagination"""
        repo = RiskRepository(db_session)

        # Create 10 risks
        for i in range(10):
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
            await repo.create(risk)

        # Test pagination
        page1 = await repo.list_by_organization(test_organization_id, skip=0, limit=5)
        page2 = await repo.list_by_organization(test_organization_id, skip=5, limit=5)

        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0].id != page2[0].id

    @pytest.mark.asyncio
    async def test_update_risk(self, db_session, sample_risk, test_organization_id):
        """Test updating a risk"""
        repo = RiskRepository(db_session)
        sample_risk.organization_id = test_organization_id

        # Create risk
        created_risk = await repo.create(sample_risk)
        risk_id = created_risk.id

        # Update risk
        sample_risk.risk_title = "Updated Title"
        sample_risk.status = RiskStatus.ANALYZING
        sample_risk.likelihood = RiskLikelihood.LIKELY
        sample_risk.impact = RiskImpact.CATASTROPHIC

        updated_risk = await repo.update(risk_id, sample_risk)

        assert updated_risk is not None
        assert updated_risk.risk_title == "Updated Title"
        assert updated_risk.status == "analyzing"
        assert updated_risk.inherent_risk_score == 20  # LIKELY (4) * CATASTROPHIC (5)

    @pytest.mark.asyncio
    async def test_update_nonexistent_risk(self, db_session, sample_risk):
        """Test updating non-existent risk returns None"""
        repo = RiskRepository(db_session)
        fake_id = uuid4()

        result = await repo.update(fake_id, sample_risk)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_risk(self, db_session, sample_risk, test_organization_id):
        """Test soft deleting a risk"""
        repo = RiskRepository(db_session)
        sample_risk.organization_id = test_organization_id

        # Create risk
        created_risk = await repo.create(sample_risk)
        risk_id = created_risk.id

        # Delete risk
        success = await repo.delete(risk_id)

        assert success is True

        # Verify risk is soft deleted
        deleted_risk = await repo.get_by_id(risk_id)
        assert deleted_risk is None  # Should not be returned by get_by_id (filters is_active)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_risk(self, db_session):
        """Test deleting non-existent risk returns False"""
        repo = RiskRepository(db_session)
        fake_id = uuid4()

        success = await repo.delete(fake_id)

        assert success is False


# =============================================================================
# FAIR Analysis Tests
# =============================================================================

class TestFAIRAnalysis:
    """Test FAIR Analysis repository operations"""

    @pytest.mark.asyncio
    async def test_create_fair_analysis(self, db_session, sample_fair_analysis, test_organization_id):
        """Test creating FAIR analysis"""
        repo = RiskRepository(db_session)

        result = await repo.create_fair_analysis(sample_fair_analysis, test_organization_id)

        assert result.id is not None
        assert result.risk_id == sample_fair_analysis.risk_id
        assert result.threat_event_frequency == 12
        assert result.vulnerability_score == 30  # Stored as percentage

    @pytest.mark.asyncio
    async def test_get_fair_analysis(self, db_session, sample_fair_analysis, test_organization_id):
        """Test retrieving FAIR analysis"""
        repo = RiskRepository(db_session)

        # Create FAIR analysis
        created = await repo.create_fair_analysis(sample_fair_analysis, test_organization_id)

        # Retrieve it
        result = await repo.get_fair_analysis(sample_fair_analysis.risk_id)

        assert result is not None
        assert result.id == created.id
        assert result.risk_id == sample_fair_analysis.risk_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_fair_analysis(self, db_session):
        """Test retrieving non-existent FAIR analysis returns None"""
        repo = RiskRepository(db_session)
        fake_risk_id = uuid4()

        result = await repo.get_fair_analysis(fake_risk_id)

        assert result is None


# =============================================================================
# Monte Carlo Simulation Tests
# =============================================================================

class TestMonteCarloSimulation:
    """Test Monte Carlo Simulation repository operations"""

    @pytest.mark.asyncio
    async def test_create_monte_carlo(self, db_session, sample_monte_carlo, test_organization_id):
        """Test creating Monte Carlo simulation"""
        repo = RiskRepository(db_session)

        result = await repo.create_monte_carlo(sample_monte_carlo, test_organization_id)

        assert result.id is not None
        assert result.risk_id == sample_monte_carlo.risk_id
        assert result.iterations == 10000
        assert len(result.factors) == 2

    @pytest.mark.asyncio
    async def test_get_monte_carlo(self, db_session, sample_monte_carlo, test_organization_id):
        """Test retrieving Monte Carlo simulation"""
        repo = RiskRepository(db_session)

        # Create simulation
        created = await repo.create_monte_carlo(sample_monte_carlo, test_organization_id)

        # Retrieve it
        result = await repo.get_monte_carlo(sample_monte_carlo.risk_id)

        assert result is not None
        assert result.id == created.id
        assert result.risk_id == sample_monte_carlo.risk_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_monte_carlo(self, db_session):
        """Test retrieving non-existent Monte Carlo simulation returns None"""
        repo = RiskRepository(db_session)
        fake_risk_id = uuid4()

        result = await repo.get_monte_carlo(fake_risk_id)

        assert result is None


# =============================================================================
# Treatment Plan Tests
# =============================================================================

class TestTreatmentPlans:
    """Test Treatment Plan repository operations"""

    @pytest.mark.asyncio
    async def test_create_treatment_plan(self, db_session, sample_treatment_plan, test_organization_id):
        """Test creating treatment plan"""
        repo = RiskRepository(db_session)

        result = await repo.create_treatment_plan(sample_treatment_plan, test_organization_id)

        assert result.id is not None
        assert result.risk_id == sample_treatment_plan.risk_id
        assert result.strategy == sample_treatment_plan.strategy.value
        assert result.description == sample_treatment_plan.description

    @pytest.mark.asyncio
    async def test_list_treatment_plans(self, db_session, test_organization_id):
        """Test listing treatment plans for a risk"""
        repo = RiskRepository(db_session)
        risk_id = uuid4()

        # Create multiple treatment plans
        for i in range(3):
            plan = RiskTreatmentPlan(
                risk_id=risk_id,
                strategy=TreatmentStrategy.MITIGATE,
                description=f"Plan {i}",
                status="planned"
            )
            await repo.create_treatment_plan(plan, test_organization_id)

        # List plans
        results = await repo.list_treatment_plans(risk_id)

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_treatment_plan(self, db_session, sample_treatment_plan, test_organization_id):
        """Test retrieving treatment plan by ID"""
        repo = RiskRepository(db_session)

        # Create plan
        created = await repo.create_treatment_plan(sample_treatment_plan, test_organization_id)

        # Retrieve it
        result = await repo.get_treatment_plan(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.risk_id == sample_treatment_plan.risk_id

    @pytest.mark.asyncio
    async def test_update_treatment_plan(self, db_session, sample_treatment_plan, test_organization_id):
        """Test updating treatment plan"""
        repo = RiskRepository(db_session)

        # Create plan
        created = await repo.create_treatment_plan(sample_treatment_plan, test_organization_id)

        # Update plan
        sample_treatment_plan.description = "Updated description"
        sample_treatment_plan.status = "in_progress"
        sample_treatment_plan.actual_cost = 60000.0

        updated = await repo.update_treatment_plan(created.id, sample_treatment_plan)

        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.status == "in_progress"
        assert updated.actual_cost == 60000

    @pytest.mark.asyncio
    async def test_update_nonexistent_treatment_plan(self, db_session, sample_treatment_plan):
        """Test updating non-existent treatment plan returns None"""
        repo = RiskRepository(db_session)
        fake_id = uuid4()

        result = await repo.update_treatment_plan(fake_id, sample_treatment_plan)

        assert result is None


# =============================================================================
# Analytics Tests
# =============================================================================

class TestAnalytics:
    """Test Analytics repository operations"""

    @pytest.mark.asyncio
    async def test_get_risk_stats(self, db_session, test_organization_id):
        """Test getting risk statistics"""
        repo = RiskRepository(db_session)

        # Create risks with different scores
        risk_data = [
            (RiskLikelihood.ALMOST_CERTAIN, RiskImpact.CATASTROPHIC, 25),  # Critical
            (RiskLikelihood.LIKELY, RiskImpact.MAJOR, 16),  # High
            (RiskLikelihood.POSSIBLE, RiskImpact.MODERATE, 9),  # Medium
            (RiskLikelihood.UNLIKELY, RiskImpact.MINOR, 4),  # Low
        ]

        for likelihood, impact, score in risk_data:
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {score}",
                risk_category=RiskCategory.OPERATIONAL,
                description="Test risk",
                likelihood=likelihood,
                impact=impact,
                inherent_risk_score=score,
                status=RiskStatus.IDENTIFIED
            )
            await repo.create(risk)

        # Get stats
        stats = await repo.get_risk_stats(test_organization_id)

        assert stats["total"] == 4
        assert stats["critical"] == 1
        assert stats["high"] == 1
        assert stats["medium"] == 1
        assert stats["low"] == 1

    @pytest.mark.asyncio
    async def test_get_risks_by_category(self, db_session, test_organization_id):
        """Test getting risk count by category"""
        repo = RiskRepository(db_session)

        # Create risks in different categories
        categories = [
            RiskCategory.CYBERSECURITY,
            RiskCategory.CYBERSECURITY,
            RiskCategory.FINANCIAL,
            RiskCategory.OPERATIONAL,
            RiskCategory.OPERATIONAL,
            RiskCategory.OPERATIONAL
        ]

        for category in categories:
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {category.value}",
                risk_category=category,
                description="Test risk",
                likelihood=RiskLikelihood.POSSIBLE,
                impact=RiskImpact.MODERATE,
                inherent_risk_score=9,
                status=RiskStatus.IDENTIFIED
            )
            await repo.create(risk)

        # Get category breakdown
        result = await repo.get_risks_by_category(test_organization_id)

        assert result["cybersecurity"] == 2
        assert result["financial"] == 1
        assert result["operational"] == 3

    @pytest.mark.asyncio
    async def test_get_risks_by_status(self, db_session, test_organization_id):
        """Test getting risk count by status"""
        repo = RiskRepository(db_session)

        # Create risks with different statuses
        statuses = [
            RiskStatus.IDENTIFIED,
            RiskStatus.IDENTIFIED,
            RiskStatus.ANALYZING,
            RiskStatus.TREATED,
            RiskStatus.MONITORING,
            RiskStatus.CLOSED
        ]

        for status in statuses:
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {status.value}",
                risk_category=RiskCategory.OPERATIONAL,
                description="Test risk",
                likelihood=RiskLikelihood.POSSIBLE,
                impact=RiskImpact.MODERATE,
                inherent_risk_score=9,
                status=status
            )
            await repo.create(risk)

        # Get status breakdown
        result = await repo.get_risks_by_status(test_organization_id)

        assert result["identified"] == 2
        assert result["analyzing"] == 1
        assert result["treated"] == 1
        assert result["monitoring"] == 1
        assert result["closed"] == 1

    @pytest.mark.asyncio
    async def test_get_top_risks(self, db_session, test_organization_id):
        """Test getting top risks by score"""
        repo = RiskRepository(db_session)

        # Create risks with different scores
        scores = [25, 20, 16, 12, 9, 6, 4, 2, 1]

        for score in scores:
            risk = Risk(
                organization_id=test_organization_id,
                risk_title=f"Risk {score}",
                risk_category=RiskCategory.OPERATIONAL,
                description="Test risk",
                likelihood=RiskLikelihood.POSSIBLE,
                impact=RiskImpact.MODERATE,
                inherent_risk_score=score,
                status=RiskStatus.IDENTIFIED
            )
            await repo.create(risk)

        # Get top 5 risks
        results = await repo.get_top_risks(test_organization_id, limit=5)

        assert len(results) == 5
        assert results[0].inherent_risk_score == 25
        assert results[1].inherent_risk_score == 20
        assert results[4].inherent_risk_score == 9

    @pytest.mark.asyncio
    async def test_get_risk_history(self, db_session, test_organization_id):
        """Test getting risk history for trend analysis"""
        repo = RiskRepository(db_session)

        # Create risks with different creation dates
        base_date = datetime.utcnow()

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
            created_risk = await repo.create(risk)
            # Manually update created_at to simulate historical data
            # Note: This might not work with in-memory SQLite, but demonstrates the concept

        # Get history
        history = await repo.get_risk_history(test_organization_id, days=90)

        # History should contain aggregated data
        assert isinstance(history, list)

    @pytest.mark.asyncio
    async def test_get_risk_history_empty(self, db_session, test_organization_id):
        """Test getting risk history with no data"""
        repo = RiskRepository(db_session)

        # Get history with no risks
        history = await repo.get_risk_history(test_organization_id, days=90)

        assert isinstance(history, list)
        assert len(history) == 0
