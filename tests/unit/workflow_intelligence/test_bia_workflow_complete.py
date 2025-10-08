"""
Complete real tests for BIA Workflow with actual data and full assertions
Tests entire BIA workflow with realistic healthcare organization data
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock


# Use sample data fixtures
pytestmark = pytest.mark.usefixtures("healthcare_organization", "critical_healthcare_processes", "mock_llm_bia_response")


@pytest.mark.asyncio
class TestBIAWorkflowComplete:
    """Complete BIA workflow tests with real data"""

    async def test_bia_identify_processes_with_healthcare_data(
        self,
        healthcare_organization,
        critical_healthcare_processes,
        mock_llm_bia_response
    ):
        """Test BIA process identification with real healthcare data"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            bia_activity_identify_processes
        )

        input_data = {
            "tenant_id": healthcare_organization["id"],
            "organization": healthcare_organization,
            "scope": {
                "departments": ["Emergency", "Laboratory", "Administration"],
                "timeframe": "2024-Q1"
            },
            "methodology": "ISO 22301",
            "llm_response": mock_llm_bia_response  # Mock LLM
        }

        # ACT
        with patch('intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow.llm_client') as mock_llm:
            mock_llm.query = AsyncMock(return_value=mock_llm_bia_response)

            result = await bia_activity_identify_processes(input_data)

        # ASSERT
        assert result is not None
        assert "processes_identified" in result
        assert result["processes_identified"] >= 20  # Healthcare org should have many processes
        assert "critical_processes" in result
        assert result["critical_processes"] >= 5  # At least 5 critical processes
        assert "processes" in result
        assert len(result["processes"]) > 0

        # Verify process structure
        first_process = result["processes"][0]
        assert "name" in first_process
        assert "criticality" in first_process
        assert first_process["criticality"] in ["critical", "high", "medium", "low"]
        assert "recommended_rto" in first_process
        assert "recommended_rpo" in first_process


    async def test_bia_analyze_dependencies_healthcare(
        self,
        critical_healthcare_processes
    ):
        """Test dependency analysis for healthcare processes"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            bia_activity_analyze_dependencies
        )

        input_data = {
            "processes": critical_healthcare_processes,
            "analysis_type": "comprehensive"
        }

        # ACT
        result = await bia_activity_analyze_dependencies(input_data)

        # ASSERT
        assert result is not None
        assert "dependencies_mapped" in result
        assert result["dependencies_mapped"] > 0

        # Check dependency structure
        assert "dependency_graph" in result
        assert "critical_dependencies" in result

        # Verify Emergency Room has dependencies on EHR, Lab, etc.
        emergency_deps = [
            d for d in result["critical_dependencies"]
            if "Emergency" in d.get("process_name", "")
        ]
        assert len(emergency_deps) > 0


    async def test_bia_assess_impact_with_realistic_scenarios(
        self,
        healthcare_organization,
        critical_healthcare_processes
    ):
        """Test impact assessment with realistic disruption scenarios"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            bia_activity_assess_impact
        )

        input_data = {
            "organization": healthcare_organization,
            "processes": critical_healthcare_processes,
            "disruption_scenarios": [
                {
                    "scenario": "EHR system failure",
                    "duration": "4h",
                    "affected_processes": ["Emergency Room", "Patient Registration", "Laboratory"]
                },
                {
                    "scenario": "Ransomware attack",
                    "duration": "24h",
                    "affected_processes": ["all_systems"]
                }
            ]
        }

        # ACT
        result = await bia_activity_assess_impact(input_data)

        # ASSERT
        assert result is not None
        assert "scenarios_analyzed" in result
        assert result["scenarios_analyzed"] == 2

        assert "impact_analysis" in result
        impact = result["impact_analysis"]

        # Verify impact categories
        assert "financial_impact" in impact
        assert "operational_impact" in impact
        assert "regulatory_impact" in impact
        assert "reputational_impact" in impact

        # Financial impact should be significant for hospital
        assert impact["financial_impact"]["total_exposure"] is not None
        assert "$" in str(impact["financial_impact"])


    async def test_bia_determine_rto_rpo_recommendations(
        self,
        critical_healthcare_processes
    ):
        """Test RTO/RPO determination for critical processes"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            bia_activity_determine_rto_rpo
        )

        input_data = {
            "processes": critical_healthcare_processes,
            "industry_standards": "healthcare",
            "regulatory_requirements": ["HIPAA", "ISO 22301"]
        }

        # ACT
        result = await bia_activity_determine_rto_rpo(input_data)

        # ASSERT
        assert result is not None
        assert "rto_rpo_recommendations" in result

        recommendations = result["rto_rpo_recommendations"]
        assert len(recommendations) > 0

        # Verify Emergency Room has aggressive RTO/RPO
        emergency_rec = [
            r for r in recommendations
            if "Emergency" in r.get("process_name", "")
        ][0]

        # Emergency Room should have RTO <= 4h
        rto_hours = self._parse_time_to_hours(emergency_rec["recommended_rto"])
        assert rto_hours <= 4

        # Emergency Room should have RPO <= 1h
        rpo_hours = self._parse_time_to_hours(emergency_rec["recommended_rpo"])
        assert rpo_hours <= 1


    async def test_bia_generate_report_completeness(
        self,
        healthcare_organization,
        bia_expected_output
    ):
        """Test BIA report generation with complete data"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            bia_activity_generate_report
        )

        input_data = {
            "organization": healthcare_organization,
            "analysis_results": bia_expected_output,
            "format": "pdf",
            "include_sections": [
                "executive_summary",
                "process_inventory",
                "impact_analysis",
                "rto_rpo_summary",
                "recommendations",
                "compliance_gaps"
            ]
        }

        # ACT
        result = await bia_activity_generate_report(input_data)

        # ASSERT
        assert result is not None
        assert "report_generated" in result
        assert result["report_generated"] is True

        assert "report_sections" in result
        sections = result["report_sections"]

        # Verify all required sections present
        required_sections = ["executive_summary", "process_inventory", "recommendations"]
        for section in required_sections:
            assert section in sections
            assert sections[section] is not None
            assert len(sections[section]) > 0

        # Verify compliance section exists
        assert "compliance_gaps" in sections
        gaps = sections["compliance_gaps"]
        assert isinstance(gaps, list)


    async def test_complete_bia_workflow_end_to_end(
        self,
        healthcare_organization,
        bia_workflow_input,
        mock_llm_bia_response
    ):
        """Test complete BIA workflow from start to finish"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            BIAWorkflow,
            bia_activity_identify_processes,
            bia_activity_analyze_dependencies,
            bia_activity_assess_impact,
            bia_activity_determine_rto_rpo,
            bia_activity_review_results,
            bia_activity_generate_report
        )

        workflow_input = bia_workflow_input

        # ACT - Execute full workflow
        with patch('intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow.llm_client') as mock_llm:
            mock_llm.query = AsyncMock(return_value=mock_llm_bia_response)

            # Step 1: Identify processes
            processes_result = await bia_activity_identify_processes(workflow_input)

            # Step 2: Analyze dependencies
            dependencies_input = {"processes": processes_result["processes"]}
            dependencies_result = await bia_activity_analyze_dependencies(dependencies_input)

            # Step 3: Assess impact
            impact_input = {
                "organization": healthcare_organization,
                "processes": processes_result["processes"],
                "dependencies": dependencies_result
            }
            impact_result = await bia_activity_assess_impact(impact_input)

            # Step 4: Determine RTO/RPO
            rto_rpo_input = {
                "processes": processes_result["processes"],
                "impact_analysis": impact_result
            }
            rto_rpo_result = await bia_activity_determine_rto_rpo(rto_rpo_input)

            # Step 5: Review results
            review_input = {
                "all_results": {
                    "processes": processes_result,
                    "dependencies": dependencies_result,
                    "impact": impact_result,
                    "rto_rpo": rto_rpo_result
                }
            }
            review_result = await bia_activity_review_results(review_input)

            # Step 6: Generate report
            report_input = {
                "organization": healthcare_organization,
                "analysis_results": review_result,
                "format": "pdf"
            }
            report_result = await bia_activity_generate_report(report_input)

        # ASSERT - Verify complete workflow
        assert processes_result is not None
        assert processes_result["processes_identified"] > 0

        assert dependencies_result is not None
        assert dependencies_result["dependencies_mapped"] > 0

        assert impact_result is not None
        assert "financial_impact" in impact_result

        assert rto_rpo_result is not None
        assert len(rto_rpo_result["rto_rpo_recommendations"]) > 0

        assert review_result is not None
        assert review_result["review_status"] == "approved"

        assert report_result is not None
        assert report_result["report_generated"] is True

        # Verify final report contains all key data
        assert "executive_summary" in report_result["report_sections"]
        assert "recommendations" in report_result["report_sections"]


    # Helper methods
    def _parse_time_to_hours(self, time_string: str) -> float:
        """Parse time string like '4h', '30m', '1d' to hours"""
        if "h" in time_string:
            return float(time_string.replace("h", ""))
        elif "m" in time_string:
            return float(time_string.replace("m", "")) / 60
        elif "d" in time_string:
            return float(time_string.replace("d", "")) * 24
        return 0


@pytest.mark.asyncio
class TestBIAWorkflowValidation:
    """Test BIA workflow validation and error handling"""

    async def test_bia_rejects_invalid_organization_data(self):
        """Test BIA rejects malformed organization data"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            bia_activity_identify_processes
        )

        invalid_input = {
            "tenant_id": None,  # Invalid
            "organization": {},  # Empty
            "scope": None  # Missing
        }

        # ACT & ASSERT
        with pytest.raises(ValueError) as exc_info:
            await bia_activity_identify_processes(invalid_input)

        assert "Invalid" in str(exc_info.value) or "required" in str(exc_info.value).lower()


    async def test_bia_handles_zero_processes_found(self):
        """Test BIA handles scenario where no processes identified"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            bia_activity_identify_processes
        )

        input_data = {
            "tenant_id": "test",
            "organization": {"id": "org-001", "name": "Empty Org"},
            "scope": {"departments": []},
            "llm_response": {"response": {"processes_identified": 0, "processes": []}}
        }

        # ACT
        with patch('intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow.llm_client') as mock_llm:
            mock_llm.query = AsyncMock(return_value={"response": {"processes_identified": 0, "processes": []}})

            result = await bia_activity_identify_processes(input_data)

        # ASSERT
        assert result is not None
        assert result["processes_identified"] == 0
        assert "warning" in result or "message" in result


    async def test_bia_validates_rto_rpo_business_rules(self):
        """Test RTO/RPO validation against business rules"""
        # ARRANGE
        from intelligent_core.workflow_intelligence.temporal_workflows.bia_workflow import (
            bia_activity_determine_rto_rpo
        )

        input_data = {
            "processes": [
                {
                    "name": "Critical Process",
                    "criticality": "critical",
                    "suggested_rto": "72h",  # Too long for critical!
                    "suggested_rpo": "24h"   # Too long for critical!
                }
            ]
        }

        # ACT
        result = await bia_activity_determine_rto_rpo(input_data)

        # ASSERT
        assert result is not None
        assert "validation_warnings" in result

        warnings = result["validation_warnings"]
        assert len(warnings) > 0
        assert any("critical" in w.lower() and "rto" in w.lower() for w in warnings)
