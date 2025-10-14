"""
Tests for Expert Agents
"""

import pytest
from ..specialists.bcm_advisor import BCMAdvisor
from ..specialists.compliance_auditor import ComplianceAuditor
from ..specialists.strategic_planner import StrategicPlanner


class TestBCMAdvisor:
    """Test BCM Advisor expert"""

    @pytest.mark.asyncio
    async def test_bcm_advisor_initialization(self):
        """Test BCM Advisor initialization"""
        advisor = BCMAdvisor()
        assert advisor.name == "BCM Advisor"

    @pytest.mark.asyncio
    async def test_bcm_advisor_advise(self, mock_context):
        """Test BCM Advisor advice generation"""
        advisor = BCMAdvisor()

        advice = await advisor.advise(
            query="How do I identify critical processes?",
            context=mock_context
        )

        assert isinstance(advice, str)
        assert len(advice) > 0


class TestComplianceAuditor:
    """Test Compliance Auditor expert"""

    @pytest.mark.asyncio
    async def test_compliance_auditor_initialization(self):
        """Test Compliance Auditor initialization"""
        auditor = ComplianceAuditor()
        assert auditor.name == "Compliance Auditor"

    @pytest.mark.asyncio
    async def test_compliance_auditor_advise(self, mock_context):
        """Test Compliance Auditor advice generation"""
        auditor = ComplianceAuditor()

        advice = await auditor.advise(
            query="What evidence do I need for ISO 22301 clause 8.2.2?",
            context=mock_context
        )

        assert isinstance(advice, str)
        assert len(advice) > 0


class TestStrategicPlanner:
    """Test Strategic Planner expert"""

    @pytest.mark.asyncio
    async def test_strategic_planner_initialization(self):
        """Test Strategic Planner initialization"""
        planner = StrategicPlanner()
        assert planner.name == "Strategic Planner"

    @pytest.mark.asyncio
    async def test_strategic_planner_advise(self, mock_context):
        """Test Strategic Planner advice generation"""
        planner = StrategicPlanner()

        advice = await planner.advise(
            query="How long will it take to complete BIA?",
            context=mock_context
        )

        assert isinstance(advice, str)
        assert len(advice) > 0
