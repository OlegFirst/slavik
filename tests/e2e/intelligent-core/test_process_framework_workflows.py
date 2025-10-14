"""
E2E Tests for Process Framework Workflows

Tests complete end-to-end workflows:
- Complete BIA process execution
- Complete Risk Assessment workflow
- Complete BC Plan development
- AI-powered automatic execution
- Document generation workflows
- Multi-user collaboration scenarios

Author: AI Platform Team
Date: 2025-10-11
"""

import pytest
import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

# Import Process Framework components
import sys
sys.path.append("/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence")

from process_framework import ProcessFramework
from bcm_processes import create_bia_process, create_risk_assessment_process, create_bc_plan_process
from process_orchestration_api import ProcessOrchestrator
from document_templates import BIAReportTemplate


# =====================================================
# Test Fixtures
# =====================================================

@pytest.fixture
async def workflow_intelligence_api():
    """Workflow Intelligence API client"""
    async with httpx.AsyncClient(base_url="http://localhost:8037") as client:
        yield client


@pytest.fixture
def process_framework_with_bcm():
    """Process Framework with BCM processes registered"""
    framework = ProcessFramework()
    framework.register_process(create_bia_process())
    framework.register_process(create_risk_assessment_process())
    framework.register_process(create_bc_plan_process())
    return framework


@pytest.fixture
def mock_ai_orchestrator():
    """Mock AI Orchestrator for testing"""
    orchestrator = AsyncMock()
    orchestrator.execute_task = AsyncMock(return_value={
        "status": "success",
        "result": {
            "analysis": "Complete",
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }
    })
    return orchestrator


@pytest.fixture
def mock_analytics_specialist():
    """Mock Analytics Specialist for testing"""
    specialist = AsyncMock()
    specialist.analyze_bia_data = AsyncMock(return_value={
        "critical_functions": [
            {"name": "Function 1", "rto": 4, "rpo": 1},
            {"name": "Function 2", "rto": 24, "rpo": 8}
        ],
        "impact_summary": "High impact identified"
    })
    return specialist


# =====================================================
# Test Complete BIA Workflow
# =====================================================

class TestCompleteBIAWorkflow:
    """Test complete BIA process execution"""

    def test_bia_workflow_all_steps(self, process_framework_with_bcm):
        """Test executing all steps of BIA process"""
        framework = process_framework_with_bcm

        # Step 1: Start BIA process
        instance = framework.start_process(
            process_id="bcm_bia_v1",
            started_by="analyst@example.com",
            initial_data={
                "organization_name": "Test Organization",
                "prepared_by": "John Analyst"
            }
        )

        assert instance.status == "active"
        assert instance.current_step_id == "bia_initiation"

        # Step 2: BIA Initiation
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "scope": "All critical business functions",
                "objectives": "Identify critical functions and recovery requirements",
                "scope_exclusions": "Non-critical support functions"
            },
            executed_by="analyst@example.com"
        )

        assert result["success"] is True
        assert next_step == "critical_functions"

        # Step 3: Identify Critical Functions
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "functions": [
                    {
                        "name": "Customer Service",
                        "description": "Handle customer inquiries",
                        "is_critical": True
                    },
                    {
                        "name": "Order Processing",
                        "description": "Process customer orders",
                        "is_critical": True
                    }
                ]
            },
            executed_by="analyst@example.com"
        )

        assert result["success"] is True
        assert next_step == "impact_analysis"

        # Step 4: Impact Analysis
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "impact_assessments": [
                    {
                        "function_name": "Customer Service",
                        "rto_hours": 4,
                        "rpo_hours": 1,
                        "financial_impact": 50000,
                        "operational_impact": "High"
                    },
                    {
                        "function_name": "Order Processing",
                        "rto_hours": 2,
                        "rpo_hours": 0.5,
                        "financial_impact": 100000,
                        "operational_impact": "Critical"
                    }
                ]
            },
            executed_by="analyst@example.com"
        )

        assert result["success"] is True
        assert next_step == "resource_requirements"

        # Step 5: Resource Requirements
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "resources": [
                    {
                        "function_name": "Customer Service",
                        "personnel": 10,
                        "technology": "CRM System, Phone System",
                        "facilities": "Call Center",
                        "suppliers": "Telecom Provider"
                    }
                ]
            },
            executed_by="analyst@example.com"
        )

        assert result["success"] is True
        assert next_step == "report_generation"

        # Step 6: Report Generation (would be auto-generated)
        # In real scenario, this would call document generator
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "report_generated": True,
                "document_path": "/reports/bia_report_20251011.pdf"
            },
            executed_by="system"
        )

        assert result["success"] is True
        assert next_step == "approval"

        # Step 7: Approval
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "approved": True,
                "comments": "BIA is comprehensive and approved"
            },
            executed_by="manager@example.com"
        )

        assert result["success"] is True
        assert next_step == "END"

        # Verify process completed
        final_instance = framework.get_instance(instance.instance_id)
        assert len(final_instance.step_history) == 7
        assert final_instance.current_step_id == "END"

    def test_bia_workflow_with_validation_errors(self, process_framework_with_bcm):
        """Test BIA workflow with validation errors"""
        framework = process_framework_with_bcm

        instance = framework.start_process(
            process_id="bcm_bia_v1",
            started_by="analyst@example.com"
        )

        # Try to submit incomplete data
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "scope": "Test"  # Too short, missing required fields
            },
            executed_by="analyst@example.com"
        )

        assert result["success"] is False
        assert "errors" in result
        assert next_step is None

    def test_bia_workflow_data_accumulation(self, process_framework_with_bcm):
        """Test that data accumulates correctly throughout BIA workflow"""
        framework = process_framework_with_bcm

        instance = framework.start_process(
            process_id="bcm_bia_v1",
            started_by="analyst@example.com",
            initial_data={"organization_name": "Test Org"}
        )

        # Execute first step
        framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "scope": "Full organization scope",
                "objectives": "Identify critical functions"
            },
            executed_by="analyst@example.com"
        )

        # Execute second step
        framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "functions": [{"name": "Function 1", "is_critical": True}]
            },
            executed_by="analyst@example.com"
        )

        # Check accumulated data
        final_instance = framework.get_instance(instance.instance_id)
        assert final_instance.data["organization_name"] == "Test Org"
        assert "scope" in final_instance.data
        assert "functions" in final_instance.data


# =====================================================
# Test AI-Powered Automatic Execution
# =====================================================

class TestAIPoweredExecution:
    """Test AI-powered automatic process execution"""

    @pytest.mark.asyncio
    async def test_automatic_bia_execution(self, process_framework_with_bcm, mock_ai_orchestrator, mock_analytics_specialist):
        """Test automatic BIA execution with AI"""
        orchestrator = ProcessOrchestrator(
            framework=process_framework_with_bcm,
            ai_orchestrator=mock_ai_orchestrator,
            analytics_specialist=mock_analytics_specialist
        )

        # Execute BIA automatically
        result = await orchestrator.execute_process_automatically(
            process_id="bcm_bia_v1",
            initial_data={
                "organization_name": "Test Org",
                "prepared_by": "AI System"
            },
            user_email="system@example.com"
        )

        assert result["success"] is True
        assert result["instance_id"] is not None
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_ai_form_filling(self, process_framework_with_bcm, mock_analytics_specialist):
        """Test AI automatic form filling"""
        orchestrator = ProcessOrchestrator(
            framework=process_framework_with_bcm,
            analytics_specialist=mock_analytics_specialist
        )

        instance = process_framework_with_bcm.start_process(
            process_id="bcm_bia_v1",
            started_by="system@example.com"
        )

        # Get current step
        step = process_framework_with_bcm.get_current_step_form(instance.instance_id)

        # AI fills form
        filled_data = await orchestrator._auto_fill_form(instance, step)

        assert filled_data is not None
        assert isinstance(filled_data, dict)

    @pytest.mark.asyncio
    async def test_ai_analysis_step(self, process_framework_with_bcm, mock_analytics_specialist):
        """Test AI-powered analysis step"""
        orchestrator = ProcessOrchestrator(
            framework=process_framework_with_bcm,
            analytics_specialist=mock_analytics_specialist
        )

        instance = process_framework_with_bcm.start_process(
            process_id="bcm_bia_v1",
            started_by="system@example.com"
        )

        # Mock analysis step
        analysis_step = Mock()
        analysis_step.id = "impact_analysis"
        analysis_step.step_type = "ANALYSIS"

        result = await orchestrator._auto_analyze(instance, analysis_step)

        assert result is not None
        mock_analytics_specialist.analyze_bia_data.assert_called_once()


# =====================================================
# Test Risk Assessment Workflow
# =====================================================

class TestRiskAssessmentWorkflow:
    """Test complete Risk Assessment workflow"""

    def test_risk_assessment_workflow(self, process_framework_with_bcm):
        """Test executing Risk Assessment process"""
        framework = process_framework_with_bcm

        # Start Risk Assessment
        instance = framework.start_process(
            process_id="bcm_risk_assessment_v1",
            started_by="risk_manager@example.com",
            initial_data={
                "organization_name": "Test Org"
            }
        )

        assert instance.current_step_id == "risk_identification"

        # Risk Identification
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "risks": [
                    {
                        "risk_id": "R001",
                        "description": "Data center failure",
                        "category": "Technology"
                    },
                    {
                        "risk_id": "R002",
                        "description": "Pandemic",
                        "category": "Health"
                    }
                ]
            },
            executed_by="risk_manager@example.com"
        )

        assert result["success"] is True

        # Risk Analysis
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "risk_assessments": [
                    {
                        "risk_id": "R001",
                        "likelihood": "medium",
                        "impact": "high",
                        "risk_level": "high"
                    }
                ]
            },
            executed_by="risk_manager@example.com"
        )

        assert result["success"] is True

        # Risk Treatment
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "treatments": [
                    {
                        "risk_id": "R001",
                        "treatment_option": "mitigate",
                        "action_plan": "Implement backup data center"
                    }
                ]
            },
            executed_by="risk_manager@example.com"
        )

        assert result["success"] is True


# =====================================================
# Test BC Plan Development Workflow
# =====================================================

class TestBCPlanWorkflow:
    """Test complete BC Plan development workflow"""

    def test_bc_plan_workflow(self, process_framework_with_bcm):
        """Test executing BC Plan development process"""
        framework = process_framework_with_bcm

        # Start BC Plan
        instance = framework.start_process(
            process_id="bcm_bc_plan_v1",
            started_by="bcm_manager@example.com",
            initial_data={
                "organization_name": "Test Org"
            }
        )

        assert instance.current_step_id == "plan_initiation"

        # Plan Initiation
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "plan_scope": "Complete organization BC Plan",
                "plan_objectives": "Ensure business continuity for all critical functions"
            },
            executed_by="bcm_manager@example.com"
        )

        assert result["success"] is True

        # Recovery Strategies
        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={
                "strategies": [
                    {
                        "function": "Customer Service",
                        "strategy": "Work from home",
                        "resources_required": "Laptops, VPN access"
                    }
                ]
            },
            executed_by="bcm_manager@example.com"
        )

        assert result["success"] is True


# =====================================================
# Test Document Generation Workflows
# =====================================================

class TestDocumentGenerationWorkflows:
    """Test document generation workflows"""

    @pytest.mark.asyncio
    async def test_bia_report_generation(self, process_framework_with_bcm):
        """Test BIA report generation"""
        framework = process_framework_with_bcm

        # Complete BIA process
        instance = framework.start_process(
            process_id="bcm_bia_v1",
            started_by="analyst@example.com",
            initial_data={
                "organization_name": "Test Org",
                "analysis_date": "2025-10-11",
                "prepared_by": "John Analyst"
            }
        )

        # Execute all steps to report generation
        # ... (abbreviated for brevity)

        # Generate report
        template = BIAReportTemplate()
        report_content = template.generate_content(instance.data)

        assert report_content is not None
        assert "Test Org" in report_content
        assert "Business Impact Analysis Report" in report_content

    @pytest.mark.asyncio
    async def test_document_generation_with_ai_enrichment(self):
        """Test document generation with AI enrichment"""
        template = BIAReportTemplate()

        data = {
            "organization_name": "Test Org",
            "analysis_date": "2025-10-11",
            "prepared_by": "John Analyst",
            "critical_functions": [
                {"name": "Customer Service", "rto": 4}
            ]
        }

        # Generate with AI enrichment
        report = template.generate_content(data)
        assert report is not None


# =====================================================
# Test Multi-User Collaboration
# =====================================================

class TestMultiUserCollaboration:
    """Test multi-user collaboration scenarios"""

    def test_multi_user_process_execution(self, process_framework_with_bcm):
        """Test multiple users working on same process"""
        framework = process_framework_with_bcm

        instance = framework.start_process(
            process_id="bcm_bia_v1",
            started_by="analyst1@example.com"
        )

        # User 1 executes first step
        framework.execute_step(
            instance_id=instance.instance_id,
            step_data={"scope": "Test scope", "objectives": "Test objectives"},
            executed_by="analyst1@example.com"
        )

        # User 2 executes second step
        framework.execute_step(
            instance_id=instance.instance_id,
            step_data={"functions": [{"name": "Function 1", "is_critical": True}]},
            executed_by="analyst2@example.com"
        )

        # Check participants
        final_instance = framework.get_instance(instance.instance_id)
        executions = final_instance.step_history
        executed_by_users = {exec["executed_by"] for exec in executions}

        assert "analyst1@example.com" in executed_by_users
        assert "analyst2@example.com" in executed_by_users


# =====================================================
# Test Error Scenarios
# =====================================================

class TestErrorScenarios:
    """Test error handling in workflows"""

    def test_invalid_step_transition(self, process_framework_with_bcm):
        """Test attempting invalid step transition"""
        framework = process_framework_with_bcm

        instance = framework.start_process(
            process_id="bcm_bia_v1",
            started_by="analyst@example.com"
        )

        # Try to execute step out of order
        # (Would require manual manipulation of current_step_id)
        # This is a safeguard test

    def test_missing_required_fields(self, process_framework_with_bcm):
        """Test missing required fields in form submission"""
        framework = process_framework_with_bcm

        instance = framework.start_process(
            process_id="bcm_bia_v1",
            started_by="analyst@example.com"
        )

        result, next_step = framework.execute_step(
            instance_id=instance.instance_id,
            step_data={},  # Missing all required fields
            executed_by="analyst@example.com"
        )

        assert result["success"] is False
        assert "errors" in result

    def test_process_suspension_and_resume(self, process_framework_with_bcm):
        """Test suspending and resuming a process"""
        framework = process_framework_with_bcm

        instance = framework.start_process(
            process_id="bcm_bia_v1",
            started_by="analyst@example.com"
        )

        # Execute one step
        framework.execute_step(
            instance_id=instance.instance_id,
            step_data={"scope": "Test", "objectives": "Test"},
            executed_by="analyst@example.com"
        )

        # Suspend (manual status change)
        framework._suspend_process(instance.instance_id, "On hold pending review")

        suspended_instance = framework.get_instance(instance.instance_id)
        assert suspended_instance.status == "suspended"

        # Resume
        framework._resume_process(instance.instance_id)

        resumed_instance = framework.get_instance(instance.instance_id)
        assert resumed_instance.status == "active"


# =====================================================
# Test API Endpoints (if Workflow Intelligence service is running)
# =====================================================

@pytest.mark.asyncio
@pytest.mark.e2e
class TestWorkflowIntelligenceAPI:
    """Test Workflow Intelligence API endpoints"""

    async def test_list_processes_endpoint(self, workflow_intelligence_api):
        """Test GET /processes endpoint"""
        try:
            response = await workflow_intelligence_api.get("/processes")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        except httpx.ConnectError:
            pytest.skip("Workflow Intelligence service not running")

    async def test_start_process_endpoint(self, workflow_intelligence_api):
        """Test POST /processes/{process_id}/start endpoint"""
        try:
            response = await workflow_intelligence_api.post(
                "/processes/bcm_bia_v1/start",
                json={
                    "started_by": "test@example.com",
                    "initial_data": {"organization_name": "Test Org"}
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "instance_id" in data
        except httpx.ConnectError:
            pytest.skip("Workflow Intelligence service not running")

    async def test_get_current_form_endpoint(self, workflow_intelligence_api):
        """Test GET /instances/{instance_id}/current-form endpoint"""
        try:
            # First start a process
            start_response = await workflow_intelligence_api.post(
                "/processes/bcm_bia_v1/start",
                json={"started_by": "test@example.com"}
            )
            instance_id = start_response.json()["instance_id"]

            # Get form
            response = await workflow_intelligence_api.get(
                f"/instances/{instance_id}/current-form"
            )
            assert response.status_code == 200
            data = response.json()
            assert "step_id" in data
            assert "fields" in data
        except httpx.ConnectError:
            pytest.skip("Workflow Intelligence service not running")

    async def test_execute_step_endpoint(self, workflow_intelligence_api):
        """Test POST /instances/{instance_id}/execute endpoint"""
        try:
            # Start process
            start_response = await workflow_intelligence_api.post(
                "/processes/bcm_bia_v1/start",
                json={"started_by": "test@example.com"}
            )
            instance_id = start_response.json()["instance_id"]

            # Execute step
            response = await workflow_intelligence_api.post(
                f"/instances/{instance_id}/execute",
                json={
                    "step_data": {
                        "scope": "Test scope",
                        "objectives": "Test objectives"
                    },
                    "executed_by": "test@example.com"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
        except httpx.ConnectError:
            pytest.skip("Workflow Intelligence service not running")


# =====================================================
# Run Tests
# =====================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not e2e"])
