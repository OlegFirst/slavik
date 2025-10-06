"""
Tests for AI Insights API endpoint
"""

import pytest
from httpx import AsyncClient


class TestAIInsightsEndpoint:
    """Test AI Insights generation endpoint"""

    @pytest.mark.asyncio
    async def test_get_insights_for_healthy_org(self, async_client: AsyncClient, auth_headers: dict):
        """Test insights for healthy organization"""

        # Create healthy organization
        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "healthy-org",
                "twin_id": "twin-healthy-001",
                "name": "Healthy Organization",
                "org_type": "corporate",
                "industry": "Technology",
                "health_score": 85.0,
                "risk_score": 25.0,
                "quality_score": 90.0,
                "maturity_level": 4
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/healthy-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "organization_id" in data
        assert data["organization_id"] == "healthy-org"
        assert "total_insights" in data
        assert "insights" in data
        assert "risk_count" in data
        assert "opportunity_count" in data
        assert "warning_count" in data
        assert "recommendation_count" in data

        # Healthy org should have fewer warnings
        assert data["total_insights"] >= 0
        assert isinstance(data["insights"], list)

    @pytest.mark.asyncio
    async def test_get_insights_for_unhealthy_org(self, async_client: AsyncClient, auth_headers: dict):
        """Test insights for unhealthy organization with multiple issues"""

        # Create unhealthy organization
        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "unhealthy-org",
                "twin_id": "twin-unhealthy-001",
                "name": "Unhealthy Organization",
                "org_type": "corporate",
                "industry": "Finance",
                "health_score": 35.0,     # Low health
                "risk_score": 85.0,       # High risk
                "quality_score": 45.0,    # Low quality
                "maturity_level": 1       # Low maturity
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/unhealthy-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Unhealthy org should have multiple insights
        assert data["total_insights"] > 0
        assert len(data["insights"]) > 0

        # Should have risks and warnings
        assert data["risk_count"] > 0 or data["warning_count"] > 0

        # Check insight structure
        for insight in data["insights"]:
            assert "id" in insight
            assert "type" in insight
            assert insight["type"] in ["risk", "opportunity", "warning", "recommendation"]
            assert "title" in insight
            assert "description" in insight
            assert "confidence" in insight
            assert 0 <= insight["confidence"] <= 100
            assert "impact" in insight
            assert insight["impact"] in ["low", "medium", "high", "critical"]
            assert "source" in insight
            assert "actionable" in insight
            assert "suggested_actions" in insight
            assert isinstance(insight["suggested_actions"], list)

    @pytest.mark.asyncio
    async def test_get_insights_with_low_health_score(self, async_client: AsyncClient, auth_headers: dict):
        """Test that low health score generates warning insight"""

        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "low-health-org",
                "twin_id": "twin-low-health-001",
                "name": "Low Health Org",
                "org_type": "corporate",
                "health_score": 30.0,  # < 50 should trigger warning
                "risk_score": 50.0,
                "quality_score": 70.0,
                "maturity_level": 3
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/low-health-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should have warning about health score
        health_warnings = [
            i for i in data["insights"]
            if i["type"] == "warning" and "health" in i["title"].lower()
        ]
        assert len(health_warnings) > 0

    @pytest.mark.asyncio
    async def test_get_insights_with_high_risk_score(self, async_client: AsyncClient, auth_headers: dict):
        """Test that high risk score generates risk insight"""

        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "high-risk-org",
                "twin_id": "twin-high-risk-001",
                "name": "High Risk Org",
                "org_type": "corporate",
                "health_score": 70.0,
                "risk_score": 85.0,  # > 70 should trigger risk alert
                "quality_score": 70.0,
                "maturity_level": 3
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/high-risk-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should have risk insight
        risk_insights = [
            i for i in data["insights"]
            if i["type"] == "risk" and "risk" in i["title"].lower()
        ]
        assert len(risk_insights) > 0
        assert data["risk_count"] > 0

    @pytest.mark.asyncio
    async def test_get_insights_with_low_data_quality(self, async_client: AsyncClient, auth_headers: dict):
        """Test that low data quality generates warning"""

        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "low-quality-org",
                "twin_id": "twin-low-quality-001",
                "name": "Low Quality Org",
                "org_type": "corporate",
                "health_score": 70.0,
                "risk_score": 50.0,
                "quality_score": 45.0,  # < 60 should trigger warning
                "maturity_level": 3
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/low-quality-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should have warning about data quality
        quality_warnings = [
            i for i in data["insights"]
            if i["type"] == "warning" and "quality" in i["title"].lower()
        ]
        assert len(quality_warnings) > 0

    @pytest.mark.asyncio
    async def test_get_insights_with_low_maturity(self, async_client: AsyncClient, auth_headers: dict):
        """Test that low maturity generates opportunity insight"""

        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "low-maturity-org",
                "twin_id": "twin-low-maturity-001",
                "name": "Low Maturity Org",
                "org_type": "corporate",
                "health_score": 70.0,
                "risk_score": 50.0,
                "quality_score": 70.0,
                "maturity_level": 2  # <= 2 should trigger opportunity
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/low-maturity-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should have opportunity about maturity
        maturity_opportunities = [
            i for i in data["insights"]
            if i["type"] == "opportunity" and "maturity" in i["title"].lower()
        ]
        assert len(maturity_opportunities) > 0
        assert data["opportunity_count"] > 0

    @pytest.mark.asyncio
    async def test_get_insights_nonexistent_org(self, async_client: AsyncClient, auth_headers: dict):
        """Test insights for non-existent organization"""

        response = await async_client.get(
            "/api/v1/organizations/nonexistent-org-id/insights",
            headers=auth_headers
        )

        # Should return 404
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_insights_unauthorized(self, async_client: AsyncClient):
        """Test insights endpoint without authentication"""

        response = await async_client.get(
            "/api/v1/organizations/some-org/insights"
            # No auth headers
        )

        # Should require authentication
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_insights_summary_counts(self, async_client: AsyncClient, auth_headers: dict):
        """Test that summary counts match actual insights"""

        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "count-test-org",
                "twin_id": "twin-count-001",
                "name": "Count Test Org",
                "org_type": "corporate",
                "health_score": 40.0,  # Will trigger warning
                "risk_score": 80.0,    # Will trigger risk
                "quality_score": 50.0, # Will trigger warning
                "maturity_level": 2    # Will trigger opportunity
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/count-test-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Verify counts match actual insights
        actual_risk_count = sum(1 for i in data["insights"] if i["type"] == "risk")
        actual_opportunity_count = sum(1 for i in data["insights"] if i["type"] == "opportunity")
        actual_warning_count = sum(1 for i in data["insights"] if i["type"] == "warning")
        actual_recommendation_count = sum(1 for i in data["insights"] if i["type"] == "recommendation")

        assert data["risk_count"] == actual_risk_count
        assert data["opportunity_count"] == actual_opportunity_count
        assert data["warning_count"] == actual_warning_count
        assert data["recommendation_count"] == actual_recommendation_count
        assert data["total_insights"] == len(data["insights"])

    @pytest.mark.asyncio
    async def test_insights_have_priorities(self, async_client: AsyncClient, auth_headers: dict):
        """Test that critical insights have high priorities"""

        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "priority-test-org",
                "twin_id": "twin-priority-001",
                "name": "Priority Test Org",
                "org_type": "corporate",
                "health_score": 30.0,
                "risk_score": 90.0,  # Very high - should be priority 1
                "quality_score": 70.0,
                "maturity_level": 3
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/priority-test-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Critical risk insights should have priority
        critical_risks = [
            i for i in data["insights"]
            if i["type"] == "risk" and i["impact"] == "critical"
        ]

        for risk in critical_risks:
            if "priority" in risk:
                assert risk["priority"] <= 2  # High priority (1 or 2)

    @pytest.mark.asyncio
    async def test_insights_timestamp(self, async_client: AsyncClient, auth_headers: dict):
        """Test that insights have timestamp"""

        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "id": "timestamp-test-org",
                "twin_id": "twin-timestamp-001",
                "name": "Timestamp Test Org",
                "org_type": "corporate",
                "health_score": 70.0,
                "risk_score": 50.0,
                "quality_score": 70.0,
                "maturity_level": 3
            },
            headers=auth_headers
        )

        response = await async_client.get(
            "/api/v1/organizations/timestamp-test-org/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Response should have generated_at timestamp
        assert "generated_at" in data

        # Each insight should have timestamp
        for insight in data["insights"]:
            assert "timestamp" in insight
