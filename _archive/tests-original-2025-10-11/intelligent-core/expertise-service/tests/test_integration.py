"""
Integration Tests

End-to-end workflow tests combining multiple experts and analyzers.
"""

import pytest
import httpx

BASE_URL = "http://localhost:8035"


@pytest.mark.asyncio
async def test_full_bcm_workflow():
    """
    Test complete BCM workflow:
    1. BIA Analysis
    2. Risk Assessment
    3. Plan Generation
    4. Compliance Check
    5. Validation
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        org_context = {
            "industry": "finance",
            "organization_size": "medium",
            "organization_id": "workflow-test-org"
        }

        # Step 1: BIA Analysis
        bia_request = {
            "query": "Analyze critical business processes",
            "context": org_context
        }
        bia_response = await client.post(
            f"{BASE_URL}/expertise/tactical/bia/analyze",
            json=bia_request
        )
        assert bia_response.status_code == 200
        bia_data = bia_response.json()
        assert "response" in bia_data

        # Step 2: Risk Assessment
        risk_request = {
            "query": "Assess risks for identified critical processes",
            "context": org_context
        }
        risk_response = await client.post(
            f"{BASE_URL}/expertise/tactical/risk/assess",
            json=risk_request
        )
        assert risk_response.status_code == 200
        risk_data = risk_response.json()
        assert "response" in risk_data

        # Step 3: Plan Generation
        plan_request = {
            "query": "Generate business continuity plan",
            "context": {**org_context, "rto": "4_hours"}
        }
        plan_response = await client.post(
            f"{BASE_URL}/expertise/tactical/plan/generate",
            json=plan_request
        )
        assert plan_response.status_code == 200
        plan_data = plan_response.json()
        assert "response" in plan_data

        # Step 4: Compliance Check
        compliance_request = {
            "query": "Check ISO 22301 compliance",
            "context": {**org_context, "standard": "iso22301"}
        }
        compliance_response = await client.post(
            f"{BASE_URL}/expertise/tactical/compliance/check",
            json=compliance_request
        )
        assert compliance_response.status_code == 200
        compliance_data = compliance_response.json()
        assert "response" in compliance_data

        # Step 5: Validation
        validation_request = {
            "query": "Validate BCM program readiness",
            "context": org_context
        }
        validation_response = await client.post(
            f"{BASE_URL}/expertise/tactical/validation/validate",
            json=validation_request
        )
        assert validation_response.status_code == 200
        validation_data = validation_response.json()
        assert "response" in validation_data


@pytest.mark.asyncio
async def test_analysis_workflow():
    """
    Test analysis workflow combining multiple analyzers:
    1. Compliance Analysis
    2. Risk Analysis
    3. Performance Analysis
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        context = {
            "organization_id": "analysis-test-org",
            "standard": "iso22301"
        }

        # Compliance Analysis
        compliance_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/compliance/analyze",
            json={
                "query": "Analyze overall compliance status",
                "context": context
            }
        )
        assert compliance_response.status_code == 200

        # Risk Analysis
        risk_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/risk/analyze",
            json={
                "query": "Analyze risk landscape",
                "context": context
            }
        )
        assert risk_response.status_code == 200

        # Performance Analysis
        performance_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/performance/analyze",
            json={
                "query": "Analyze BCM program performance",
                "context": context
            }
        )
        assert performance_response.status_code == 200


@pytest.mark.asyncio
async def test_incident_response_workflow():
    """
    Test incident response workflow:
    1. Incident Advisor
    2. Emergency Analyzer
    3. Impact Analyzer
    4. Plan Analyzer
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        incident_context = {
            "incident_type": "ransomware",
            "severity": "critical",
            "organization_id": "incident-test-org"
        }

        # Get incident advice
        advice_response = await client.post(
            f"{BASE_URL}/expertise/tactical/incident/advise",
            json={
                "query": "Ransomware attack detected - immediate actions?",
                "context": incident_context
            }
        )
        assert advice_response.status_code == 200

        # Analyze emergency response
        emergency_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/emergency/analyze",
            json={
                "query": "Analyze emergency response capability",
                "context": incident_context
            }
        )
        assert emergency_response.status_code == 200

        # Analyze impact
        impact_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/impact/analyze",
            json={
                "query": "Analyze business impact of ransomware",
                "context": incident_context
            }
        )
        assert impact_response.status_code == 200

        # Analyze plan effectiveness
        plan_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/plan/analyze",
            json={
                "query": "Analyze incident response plan effectiveness",
                "context": incident_context
            }
        )
        assert plan_response.status_code == 200


@pytest.mark.asyncio
async def test_training_development_workflow():
    """
    Test training and development workflow:
    1. Learning Specialist
    2. Exercise Designer
    3. Learning Analyzer
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        training_context = {
            "audience": "all_staff",
            "organization_id": "training-test-org"
        }

        # Design training program
        training_response = await client.post(
            f"{BASE_URL}/expertise/tactical/learning/design",
            json={
                "query": "Design comprehensive BCM awareness training",
                "context": training_context
            }
        )
        assert training_response.status_code == 200

        # Design exercise
        exercise_response = await client.post(
            f"{BASE_URL}/expertise/tactical/exercise/design",
            json={
                "query": "Design tabletop exercise",
                "context": training_context
            }
        )
        assert exercise_response.status_code == 200

        # Analyze learning effectiveness
        analysis_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/learning/analyze",
            json={
                "query": "Analyze training effectiveness",
                "context": training_context
            }
        )
        assert analysis_response.status_code == 200


@pytest.mark.asyncio
async def test_governance_workflow():
    """
    Test governance workflow:
    1. Governance Specialist
    2. Governance Analyzer
    3. Compliance Analyzer
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        gov_context = {
            "organization_type": "corporate",
            "organization_id": "gov-test-org"
        }

        # Governance assessment
        gov_response = await client.post(
            f"{BASE_URL}/expertise/tactical/governance/analyze",
            json={
                "query": "Assess governance structure",
                "context": gov_context
            }
        )
        assert gov_response.status_code == 200

        # Governance analysis
        analysis_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/governance/analyze",
            json={
                "query": "Analyze governance effectiveness",
                "context": gov_context
            }
        )
        assert analysis_response.status_code == 200

        # Compliance check
        compliance_response = await client.post(
            f"{BASE_URL}/expertise/analyzers/compliance/analyze",
            json={
                "query": "Analyze governance compliance",
                "context": gov_context
            }
        )
        assert compliance_response.status_code == 200


@pytest.mark.asyncio
async def test_generic_query_routing():
    """Test that generic query endpoint can route to different experts"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        experts_to_test = [
            "bia_specialist",
            "risk_analyst",
            "compliance_copilot"
        ]

        for expert in experts_to_test:
            request = {
                "expert_type": expert,
                "query": f"Test query for {expert}",
                "context": {"test": True}
            }
            response = await client.post(
                f"{BASE_URL}/expertise/query",
                json=request
            )
            assert response.status_code == 200
            data = response.json()
            assert data["expert"] == expert


@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling of concurrent requests to different endpoints"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        import asyncio

        # Create multiple concurrent requests
        tasks = [
            client.post(
                f"{BASE_URL}/expertise/tactical/bia/analyze",
                json={"query": "Test BIA"}
            ),
            client.post(
                f"{BASE_URL}/expertise/tactical/risk/assess",
                json={"query": "Test Risk"}
            ),
            client.post(
                f"{BASE_URL}/expertise/analyzers/compliance/analyze",
                json={"query": "Test Compliance"}
            )
        ]

        # Execute concurrently
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_service_info_consistency():
    """Test that service info is consistent across calls"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get info multiple times
        info1 = await client.get(f"{BASE_URL}/expertise/info")
        info2 = await client.get(f"{BASE_URL}/expertise/info")

        assert info1.status_code == 200
        assert info2.status_code == 200

        data1 = info1.json()
        data2 = info2.json()

        # Should be identical
        assert data1 == data2
        assert len(data1["tactical_assistants"]) == len(data2["tactical_assistants"])
        assert len(data1["analyzers"]) == len(data2["analyzers"])


@pytest.mark.asyncio
async def test_error_handling_in_workflow():
    """Test error handling when part of workflow fails"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Valid request
        valid_response = await client.post(
            f"{BASE_URL}/expertise/tactical/bia/analyze",
            json={"query": "Valid query"}
        )
        assert valid_response.status_code == 200

        # Invalid expert type in generic query
        invalid_response = await client.post(
            f"{BASE_URL}/expertise/query",
            json={
                "expert_type": "nonexistent_expert",
                "query": "Test"
            }
        )
        assert invalid_response.status_code in [404, 500]

        # Service should still be healthy after errors
        health_response = await client.get(f"{BASE_URL}/health")
        assert health_response.status_code == 200
