"""
Unit tests for frontend-compatible Pydantic models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from core.models.base import (
    TwinInsight, TwinInsightType, ImpactLevel,
    RiskLandscape, ComplianceStatus, ComplianceFramework,
    DepartmentTwin, PersonalDigitalTwin, OrganizationTwin,
    AIInsightsResponse
)


class TestTwinInsight:
    """Test TwinInsight model"""

    def test_create_valid_twin_insight(self):
        """Test creating valid TwinInsight"""

        insight = TwinInsight(
            type=TwinInsightType.RISK,
            title="Test Risk",
            description="This is a test risk",
            confidence=85.0,
            impact=ImpactLevel.HIGH,
            source="test_source",
            actionable=True,
            suggested_actions=["Action 1", "Action 2"]
        )

        assert insight.type == TwinInsightType.RISK
        assert insight.title == "Test Risk"
        assert insight.confidence == 85.0
        assert insight.impact == ImpactLevel.HIGH
        assert len(insight.suggested_actions) == 2
        assert insight.actionable is True

    def test_twin_insight_generates_id(self):
        """Test that TwinInsight auto-generates ID"""

        insight = TwinInsight(
            type=TwinInsightType.WARNING,
            title="Test",
            description="Test",
            confidence=80.0,
            impact=ImpactLevel.MEDIUM,
            source="test"
        )

        assert insight.id is not None
        assert isinstance(insight.id, str)
        assert len(insight.id) > 0

    def test_twin_insight_confidence_validation(self):
        """Test confidence score validation (0-100)"""

        # Valid confidence
        insight = TwinInsight(
            type=TwinInsightType.OPPORTUNITY,
            title="Test",
            description="Test",
            confidence=50.0,
            impact=ImpactLevel.LOW,
            source="test"
        )
        assert insight.confidence == 50.0

        # Invalid - too high
        with pytest.raises(ValidationError):
            TwinInsight(
                type=TwinInsightType.RISK,
                title="Test",
                description="Test",
                confidence=150.0,  # > 100
                impact=ImpactLevel.HIGH,
                source="test"
            )

        # Invalid - negative
        with pytest.raises(ValidationError):
            TwinInsight(
                type=TwinInsightType.RISK,
                title="Test",
                description="Test",
                confidence=-10.0,  # < 0
                impact=ImpactLevel.HIGH,
                source="test"
            )

    def test_twin_insight_priority_validation(self):
        """Test priority validation (1-5)"""

        # Valid priority
        insight = TwinInsight(
            type=TwinInsightType.RISK,
            title="Test",
            description="Test",
            confidence=80.0,
            impact=ImpactLevel.CRITICAL,
            source="test",
            priority=1
        )
        assert insight.priority == 1

        # Invalid priority
        with pytest.raises(ValidationError):
            TwinInsight(
                type=TwinInsightType.RISK,
                title="Test",
                description="Test",
                confidence=80.0,
                impact=ImpactLevel.HIGH,
                source="test",
                priority=10  # > 5
            )

    def test_twin_insight_all_types(self):
        """Test all TwinInsightType values"""

        types = [
            TwinInsightType.RISK,
            TwinInsightType.OPPORTUNITY,
            TwinInsightType.WARNING,
            TwinInsightType.RECOMMENDATION
        ]

        for insight_type in types:
            insight = TwinInsight(
                type=insight_type,
                title="Test",
                description="Test",
                confidence=75.0,
                impact=ImpactLevel.MEDIUM,
                source="test"
            )
            assert insight.type == insight_type

    def test_twin_insight_all_impact_levels(self):
        """Test all ImpactLevel values"""

        impacts = [
            ImpactLevel.LOW,
            ImpactLevel.MEDIUM,
            ImpactLevel.HIGH,
            ImpactLevel.CRITICAL
        ]

        for impact in impacts:
            insight = TwinInsight(
                type=TwinInsightType.RISK,
                title="Test",
                description="Test",
                confidence=75.0,
                impact=impact,
                source="test"
            )
            assert insight.impact == impact


class TestRiskLandscape:
    """Test RiskLandscape model"""

    def test_create_valid_risk_landscape(self):
        """Test creating valid RiskLandscape"""

        risk_landscape = RiskLandscape(
            total_risks=10,
            critical_risks=2,
            high_risks=3,
            medium_risks=4,
            low_risks=1,
            mitigation_coverage=75.0,
            by_category={"cyber": 5, "operational": 3, "financial": 2},
            trend="increasing"
        )

        assert risk_landscape.total_risks == 10
        assert risk_landscape.critical_risks == 2
        assert risk_landscape.mitigation_coverage == 75.0
        assert len(risk_landscape.by_category) == 3

    def test_risk_landscape_defaults(self):
        """Test RiskLandscape default values"""

        risk_landscape = RiskLandscape()

        assert risk_landscape.total_risks == 0
        assert risk_landscape.critical_risks == 0
        assert risk_landscape.mitigation_coverage == 0.0
        assert risk_landscape.by_category == {}
        assert risk_landscape.trend is None

    def test_risk_landscape_mitigation_validation(self):
        """Test mitigation coverage validation (0-100)"""

        # Valid
        risk_landscape = RiskLandscape(mitigation_coverage=50.0)
        assert risk_landscape.mitigation_coverage == 50.0

        # Invalid - too high
        with pytest.raises(ValidationError):
            RiskLandscape(mitigation_coverage=150.0)

        # Invalid - negative
        with pytest.raises(ValidationError):
            RiskLandscape(mitigation_coverage=-10.0)


class TestComplianceFramework:
    """Test ComplianceFramework model"""

    def test_create_valid_compliance_framework(self):
        """Test creating valid ComplianceFramework"""

        framework = ComplianceFramework(
            name="ISO 22301",
            compliance_percentage=85.0,
            status="in_progress",
            gaps=["Gap 1", "Gap 2"]
        )

        assert framework.name == "ISO 22301"
        assert framework.compliance_percentage == 85.0
        assert framework.status == "in_progress"
        assert len(framework.gaps) == 2

    def test_compliance_percentage_validation(self):
        """Test compliance percentage validation (0-100)"""

        # Valid
        framework = ComplianceFramework(
            name="Test",
            compliance_percentage=100.0
        )
        assert framework.compliance_percentage == 100.0

        # Invalid
        with pytest.raises(ValidationError):
            ComplianceFramework(
                name="Test",
                compliance_percentage=110.0
            )


class TestComplianceStatus:
    """Test ComplianceStatus model"""

    def test_create_valid_compliance_status(self):
        """Test creating valid ComplianceStatus"""

        frameworks = [
            ComplianceFramework(name="ISO 22301", compliance_percentage=80.0),
            ComplianceFramework(name="NIST", compliance_percentage=75.0)
        ]

        status = ComplianceStatus(
            overall_score=77.5,
            frameworks=frameworks
        )

        assert status.overall_score == 77.5
        assert len(status.frameworks) == 2
        assert status.last_updated is not None


class TestDepartmentTwin:
    """Test DepartmentTwin model"""

    def test_create_valid_department_twin(self):
        """Test creating valid DepartmentTwin"""

        dept = DepartmentTwin(
            name="IT Department",
            twin_count=15,
            avg_health_score=85.0,
            key_metrics={"active_users": 15, "avg_engagement": 0.85},
            head_of_department="John Doe",
            critical_processes=["Server Maintenance", "Security Monitoring"]
        )

        assert dept.name == "IT Department"
        assert dept.twin_count == 15
        assert dept.avg_health_score == 85.0
        assert dept.head_of_department == "John Doe"
        assert len(dept.critical_processes) == 2

    def test_department_twin_defaults(self):
        """Test DepartmentTwin default values"""

        dept = DepartmentTwin(name="Finance")

        assert dept.twin_count == 0
        assert dept.avg_health_score == 0.0
        assert dept.key_metrics == {}
        assert dept.head_of_department is None
        assert dept.critical_processes == []


class TestPersonalDigitalTwin:
    """Test PersonalDigitalTwin model"""

    def test_create_valid_personal_twin(self):
        """Test creating valid PersonalDigitalTwin"""

        twin = PersonalDigitalTwin(
            user_id="user-123",
            display_name="John Doe",
            workspace_config={"theme": "dark", "language": "en"},
            personal_metrics={"login_count_month": 45},
            activity_patterns={"activity_level": "high"},
            twin_health_score=85.0,
            activity_score=90.0,
            sync_status="active"
        )

        assert twin.user_id == "user-123"
        assert twin.display_name == "John Doe"
        assert twin.twin_health_score == 85.0
        assert twin.sync_status == "active"
        assert twin.id is not None

    def test_personal_twin_defaults(self):
        """Test PersonalDigitalTwin default values"""

        twin = PersonalDigitalTwin(
            user_id="user-123",
            display_name="Test User"
        )

        assert twin.workspace_config == {}
        assert twin.personal_metrics == {}
        assert twin.activity_patterns == {}
        assert twin.twin_health_score == 0.0
        assert twin.activity_score == 0.0
        assert twin.sync_status == "active"
        assert twin.organization_id is None

    def test_personal_twin_health_score_validation(self):
        """Test health score validation (0-100)"""

        # Valid
        twin = PersonalDigitalTwin(
            user_id="user-123",
            display_name="Test",
            twin_health_score=75.0
        )
        assert twin.twin_health_score == 75.0

        # Invalid
        with pytest.raises(ValidationError):
            PersonalDigitalTwin(
                user_id="user-123",
                display_name="Test",
                twin_health_score=150.0
            )


class TestOrganizationTwin:
    """Test OrganizationTwin model"""

    def test_create_valid_organization_twin(self):
        """Test creating valid OrganizationTwin"""

        departments = [
            DepartmentTwin(name="IT", twin_count=10, avg_health_score=85.0),
            DepartmentTwin(name="HR", twin_count=5, avg_health_score=80.0)
        ]

        org_twin = OrganizationTwin(
            id="org-123",
            name="Test Org",
            health_score=82.5,
            twin_health_score=85.0,
            personal_twins_count=15,
            departments=departments,
            industry="Technology",
            employee_count=100
        )

        assert org_twin.id == "org-123"
        assert org_twin.name == "Test Org"
        assert org_twin.personal_twins_count == 15
        assert len(org_twin.departments) == 2

    def test_organization_twin_defaults(self):
        """Test OrganizationTwin default values"""

        org_twin = OrganizationTwin(
            id="org-123",
            name="Test Org"
        )

        assert org_twin.health_score == 0.0
        assert org_twin.twin_health_score is None
        assert org_twin.personal_twins_count == 0
        assert org_twin.departments == []


class TestAIInsightsResponse:
    """Test AIInsightsResponse model"""

    def test_create_valid_ai_insights_response(self):
        """Test creating valid AIInsightsResponse"""

        insights = [
            TwinInsight(
                type=TwinInsightType.RISK,
                title="Test Risk",
                description="Test",
                confidence=85.0,
                impact=ImpactLevel.HIGH,
                source="test"
            ),
            TwinInsight(
                type=TwinInsightType.OPPORTUNITY,
                title="Test Opportunity",
                description="Test",
                confidence=75.0,
                impact=ImpactLevel.MEDIUM,
                source="test"
            )
        ]

        response = AIInsightsResponse(
            organization_id="org-123",
            total_insights=2,
            insights=insights,
            risk_count=1,
            opportunity_count=1,
            warning_count=0,
            recommendation_count=0
        )

        assert response.organization_id == "org-123"
        assert response.total_insights == 2
        assert len(response.insights) == 2
        assert response.risk_count == 1
        assert response.opportunity_count == 1

    def test_ai_insights_response_defaults(self):
        """Test AIInsightsResponse default values"""

        response = AIInsightsResponse(
            organization_id="org-123",
            total_insights=0,
            insights=[]
        )

        assert response.risk_count == 0
        assert response.opportunity_count == 0
        assert response.warning_count == 0
        assert response.recommendation_count == 0
        assert response.generated_at is not None
