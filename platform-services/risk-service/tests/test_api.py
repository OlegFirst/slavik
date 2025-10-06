"""
Test Risk API Routes
Tests all API endpoints with authentication and authorization
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
from pathlib import Path

# Add shared models to path
shared_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Import common models
import importlib.util
spec = importlib.util.spec_from_file_location("common", shared_path / "models" / "common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
User = common.User

from main import app
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
from services.business_logic import RiskService


# =============================================================================
# API Client Fixtures
# =============================================================================

@pytest_asyncio.fixture
async def async_client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers with mock token"""
    # In real tests, you'd generate a valid JWT token
    return {
        "Authorization": "Bearer mock-token-123"
    }


# =============================================================================
# Risk CRUD API Tests
# =============================================================================

class TestRiskAPI:
    """Test Risk CRUD API endpoints"""

    @pytest.mark.asyncio
    async def test_create_risk_authenticated(self, async_client, auth_headers, sample_risk, test_user):
        """Test creating risk with authentication"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                # Mock database session
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                # Mock service
                with patch.object(RiskService, 'create_risk') as mock_create:
                    sample_risk.id = uuid4()
                    mock_create.return_value = sample_risk

                    response = await async_client.post(
                        "/api/v1/risk/assessments",
                        json=sample_risk.model_dump(mode='json'),
                        headers=auth_headers
                    )

                    assert response.status_code == 201
                    data = response.json()
                    assert data["risk_title"] == sample_risk.risk_title

    @pytest.mark.asyncio
    async def test_create_risk_unauthenticated(self, async_client, sample_risk):
        """Test creating risk without authentication fails"""
        with patch('config.settings.JWT_AUTH_ENABLED', True):
            response = await async_client.post(
                "/api/v1/risk/assessments",
                json=sample_risk.model_dump(mode='json')
            )

            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_risks(self, async_client, auth_headers, test_user, test_organization_id):
        """Test listing risks for organization"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                # Create sample risks
                risks = [
                    Risk(
                        id=uuid4(),
                        organization_id=test_organization_id,
                        risk_title=f"Risk {i}",
                        risk_category=RiskCategory.OPERATIONAL,
                        description=f"Description {i}",
                        likelihood=RiskLikelihood.POSSIBLE,
                        impact=RiskImpact.MODERATE,
                        inherent_risk_score=9,
                        status=RiskStatus.IDENTIFIED
                    )
                    for i in range(3)
                ]

                with patch.object(RiskService, 'list_risks', return_value=risks):
                    response = await async_client.get(
                        "/api/v1/risk/assessments",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 3

    @pytest.mark.asyncio
    async def test_list_risks_with_filters(self, async_client, auth_headers, test_user):
        """Test listing risks with query filters"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                with patch.object(RiskService, 'list_risks', return_value=[]):
                    response = await async_client.get(
                        "/api/v1/risk/assessments?category=cybersecurity&status=identified&min_score=15",
                        headers=auth_headers
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_risk_by_id(self, async_client, auth_headers, test_user, sample_risk):
        """Test getting risk by ID"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                sample_risk.id = uuid4()

                with patch.object(RiskService, 'get_risk', return_value=sample_risk):
                    response = await async_client.get(
                        f"/api/v1/risk/assessments/{sample_risk.id}",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["risk_title"] == sample_risk.risk_title

    @pytest.mark.asyncio
    async def test_get_risk_not_found(self, async_client, auth_headers, test_user):
        """Test getting non-existent risk returns 404"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                with patch.object(RiskService, 'get_risk', return_value=None):
                    fake_id = uuid4()
                    response = await async_client.get(
                        f"/api/v1/risk/assessments/{fake_id}",
                        headers=auth_headers
                    )

                    assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_risk(self, async_client, auth_headers, test_user, sample_risk):
        """Test updating risk"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                sample_risk.id = uuid4()
                sample_risk.risk_title = "Updated Title"

                with patch.object(RiskService, 'update_risk', return_value=sample_risk):
                    response = await async_client.put(
                        f"/api/v1/risk/assessments/{sample_risk.id}",
                        json=sample_risk.model_dump(mode='json'),
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["risk_title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete_risk(self, async_client, auth_headers, test_user):
        """Test deleting risk"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                risk_id = uuid4()

                with patch.object(RiskService, 'delete_risk', return_value=True):
                    response = await async_client.delete(
                        f"/api/v1/risk/assessments/{risk_id}",
                        headers=auth_headers
                    )

                    assert response.status_code == 204


# =============================================================================
# FAIR Analysis API Tests
# =============================================================================

class TestFAIRAnalysisAPI:
    """Test FAIR Analysis API endpoints"""

    @pytest.mark.asyncio
    async def test_perform_fair_analysis(self, async_client, auth_headers, test_user, sample_fair_analysis):
        """Test performing FAIR analysis"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                sample_fair_analysis.loss_event_frequency = 3.6
                sample_fair_analysis.annual_loss_expectancy = 450000.0
                sample_fair_analysis.risk_rating = "high"

                with patch.object(RiskService, 'perform_fair_analysis', return_value=sample_fair_analysis):
                    response = await async_client.post(
                        f"/api/v1/risk/assessments/{sample_fair_analysis.risk_id}/fair-analysis",
                        json=sample_fair_analysis.model_dump(mode='json'),
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["risk_rating"] == "high"

    @pytest.mark.asyncio
    async def test_get_fair_analysis(self, async_client, auth_headers, test_user, sample_fair_analysis):
        """Test getting FAIR analysis"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                with patch.object(RiskService, 'get_fair_analysis', return_value=sample_fair_analysis):
                    response = await async_client.get(
                        f"/api/v1/risk/assessments/{sample_fair_analysis.risk_id}/fair-analysis",
                        headers=auth_headers
                    )

                    assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_fair_analysis_not_found(self, async_client, auth_headers, test_user):
        """Test getting non-existent FAIR analysis returns 404"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                with patch.object(RiskService, 'get_fair_analysis', return_value=None):
                    fake_id = uuid4()
                    response = await async_client.get(
                        f"/api/v1/risk/assessments/{fake_id}/fair-analysis",
                        headers=auth_headers
                    )

                    assert response.status_code == 404


# =============================================================================
# Monte Carlo Simulation API Tests
# =============================================================================

class TestMonteCarloAPI:
    """Test Monte Carlo Simulation API endpoints"""

    @pytest.mark.asyncio
    async def test_run_monte_carlo_simulation(self, async_client, auth_headers, test_user, sample_monte_carlo):
        """Test running Monte Carlo simulation"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                sample_monte_carlo.mean_loss = 75000.0
                sample_monte_carlo.median_loss = 70000.0
                sample_monte_carlo.percentile_95 = 150000.0
                sample_monte_carlo.percentile_99 = 180000.0

                with patch.object(RiskService, 'run_monte_carlo', return_value=sample_monte_carlo):
                    response = await async_client.post(
                        f"/api/v1/risk/assessments/{sample_monte_carlo.risk_id}/monte-carlo",
                        json=sample_monte_carlo.model_dump(mode='json'),
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["mean_loss"] == 75000.0

    @pytest.mark.asyncio
    async def test_get_monte_carlo_results(self, async_client, auth_headers, test_user, sample_monte_carlo):
        """Test getting Monte Carlo results"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                with patch.object(RiskService, 'get_monte_carlo_results', return_value=sample_monte_carlo):
                    response = await async_client.get(
                        f"/api/v1/risk/assessments/{sample_monte_carlo.risk_id}/monte-carlo",
                        headers=auth_headers
                    )

                    assert response.status_code == 200


# =============================================================================
# Treatment Plan API Tests
# =============================================================================

class TestTreatmentPlanAPI:
    """Test Treatment Plan API endpoints"""

    @pytest.mark.asyncio
    async def test_create_treatment_plan(self, async_client, auth_headers, test_user, sample_treatment_plan):
        """Test creating treatment plan"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                sample_treatment_plan.id = uuid4()

                with patch.object(RiskService, 'create_treatment_plan', return_value=sample_treatment_plan):
                    response = await async_client.post(
                        f"/api/v1/risk/assessments/{sample_treatment_plan.risk_id}/treatment-plans",
                        json=sample_treatment_plan.model_dump(mode='json'),
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["description"] == sample_treatment_plan.description

    @pytest.mark.asyncio
    async def test_list_treatment_plans(self, async_client, auth_headers, test_user):
        """Test listing treatment plans"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                risk_id = uuid4()
                plans = [
                    RiskTreatmentPlan(
                        id=uuid4(),
                        risk_id=risk_id,
                        strategy=TreatmentStrategy.MITIGATE,
                        description=f"Plan {i}",
                        status="planned"
                    )
                    for i in range(3)
                ]

                with patch.object(RiskService, 'list_treatment_plans', return_value=plans):
                    response = await async_client.get(
                        f"/api/v1/risk/assessments/{risk_id}/treatment-plans",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 3

    @pytest.mark.asyncio
    async def test_update_treatment_plan(self, async_client, auth_headers, test_user, sample_treatment_plan):
        """Test updating treatment plan"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                sample_treatment_plan.id = uuid4()
                sample_treatment_plan.status = "completed"

                with patch.object(RiskService, 'update_treatment_plan', return_value=sample_treatment_plan):
                    response = await async_client.put(
                        f"/api/v1/risk/treatment-plans/{sample_treatment_plan.id}",
                        json=sample_treatment_plan.model_dump(mode='json'),
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "completed"


# =============================================================================
# Risk Reports API Tests
# =============================================================================

class TestRiskReportsAPI:
    """Test Risk Reports API endpoints"""

    @pytest.mark.asyncio
    async def test_generate_risk_report(self, async_client, auth_headers, test_user, test_organization_id):
        """Test generating comprehensive risk report"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                # Mock report
                from models.domain import RiskReport
                mock_report = RiskReport(
                    organization_id=test_organization_id,
                    total_risks=10,
                    critical_risks=2,
                    high_risks=3,
                    medium_risks=3,
                    low_risks=2,
                    top_risks=[],
                    risks_by_category={},
                    risks_by_status={},
                    trend_data={},
                    generated_at=datetime.utcnow()
                )

                with patch.object(RiskService, 'generate_risk_report', return_value=mock_report):
                    response = await async_client.get(
                        "/api/v1/risk/reports",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["total_risks"] == 10

    @pytest.mark.asyncio
    async def test_get_risk_matrix_position(self, async_client, auth_headers, test_user, sample_risk):
        """Test getting risk matrix position"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                sample_risk.id = uuid4()

                with patch.object(RiskService, 'get_risk', return_value=sample_risk):
                    response = await async_client.get(
                        f"/api/v1/risk/assessments/{sample_risk.id}/matrix-position",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "likelihood" in data
                    assert "impact" in data
                    assert "severity" in data

    @pytest.mark.asyncio
    async def test_get_risk_heat_map(self, async_client, auth_headers, test_user):
        """Test getting risk heat map"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                mock_heat_map = {
                    "organization_id": str(uuid4()),
                    "matrix": [[0 for _ in range(5)] for _ in range(5)],
                    "labels": {}
                }

                with patch.object(RiskService, 'get_risk_heat_map', return_value=mock_heat_map):
                    response = await async_client.get(
                        "/api/v1/risk/risk-heat-map",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "matrix" in data

    @pytest.mark.asyncio
    async def test_get_risk_trends(self, async_client, auth_headers, test_user):
        """Test getting risk trends"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                mock_trends = {
                    "organization_id": str(uuid4()),
                    "period_days": 90,
                    "daily_data": [],
                    "summary": {},
                    "activity": {}
                }

                with patch.object(RiskService, 'get_risk_trends', return_value=mock_trends):
                    response = await async_client.get(
                        "/api/v1/risk/risk-trends?days=90",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "period_days" in data
                    assert data["period_days"] == 90

    @pytest.mark.asyncio
    async def test_get_risk_trends_custom_period(self, async_client, auth_headers, test_user):
        """Test getting risk trends with custom period"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                mock_trends = {
                    "organization_id": str(uuid4()),
                    "period_days": 30,
                    "daily_data": [],
                    "summary": {},
                    "activity": {}
                }

                with patch.object(RiskService, 'get_risk_trends', return_value=mock_trends):
                    response = await async_client.get(
                        "/api/v1/risk/risk-trends?days=30",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["period_days"] == 30


# =============================================================================
# Authorization Tests
# =============================================================================

class TestAuthorization:
    """Test API authorization and access control"""

    @pytest.mark.asyncio
    async def test_organization_isolation(self, async_client, auth_headers, test_user):
        """Test that users can only access their organization's data"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                # Mock service to verify organization_id is used from token
                with patch.object(RiskService, 'list_risks', return_value=[]) as mock_list:
                    response = await async_client.get(
                        "/api/v1/risk/assessments",
                        headers=auth_headers
                    )

                    assert response.status_code == 200
                    # Verify that the service was called with the user's organization ID
                    mock_list.assert_called_once()
                    call_args = mock_list.call_args
                    assert str(call_args[0][0]) == test_user.tenant_id

    @pytest.mark.asyncio
    async def test_missing_token(self, async_client):
        """Test that requests without token are rejected when auth is enabled"""
        with patch('config.settings.JWT_AUTH_ENABLED', True):
            response = await async_client.get("/api/v1/risk/assessments")
            assert response.status_code == 401


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test API error handling"""

    @pytest.mark.asyncio
    async def test_invalid_risk_id_format(self, async_client, auth_headers, test_user):
        """Test handling of invalid UUID format"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                response = await async_client.get(
                    "/api/v1/risk/assessments/invalid-uuid",
                    headers=auth_headers
                )

                assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_invalid_query_parameters(self, async_client, auth_headers, test_user):
        """Test handling of invalid query parameters"""
        with patch('api.routes.get_current_user', return_value=test_user):
            with patch('api.routes.get_db') as mock_get_db:
                mock_db = AsyncMock()
                mock_get_db.return_value = mock_db

                # min_score must be between 1 and 25
                response = await async_client.get(
                    "/api/v1/risk/assessments?min_score=100",
                    headers=auth_headers
                )

                assert response.status_code == 422
