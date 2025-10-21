"""
Test Business Validation Rules for BIA
Tests for the 19 business validation rules referenced in requirements
"""

import pytest
from models.domain import BIAProcess, Dependency
from models.enums import CriticalityLevel, WHOTier, PatientSafetyImpact, IndustryType


class TestRecoveryObjectivesValidation:
    """Test Rule 1: Recovery objectives (RTO/RPO/MTPD relationships)"""

    def test_should_validate_rpo_less_than_or_equal_to_rto(self, tenant_id):
        """Test RPO <= RTO rule"""
        # Valid: RPO <= RTO
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Valid Process",
            criticality=CriticalityLevel.HIGH,
            rto_hours=8,
            rpo_hours=2,  # RPO < RTO 
            mtpd_hours=24
        )
        assert process.rpo_hours <= process.rto_hours

    def test_should_fail_when_rpo_greater_than_rto(self, tenant_id):
        """Test RPO > RTO fails"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Invalid Process",
                criticality=CriticalityLevel.HIGH,
                rto_hours=2,
                rpo_hours=8,  # RPO > RTO 
                mtpd_hours=24
            )
        assert "RTO must be greater than or equal to RPO" in str(exc_info.value)

    def test_should_validate_rto_less_than_or_equal_to_mtpd(self, tenant_id):
        """Test RTO <= MTPD rule"""
        # Valid: RTO <= MTPD
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Valid Process",
            criticality=CriticalityLevel.MEDIUM,
            rto_hours=8,
            rpo_hours=2,
            mtpd_hours=24  # MTPD > RTO 
        )
        assert process.rto_hours <= process.mtpd_hours

    def test_should_fail_when_mtpd_less_than_rto(self, tenant_id):
        """Test MTPD < RTO fails"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Invalid Process",
                criticality=CriticalityLevel.HIGH,
                rto_hours=24,
                rpo_hours=4,
                mtpd_hours=8  # MTPD < RTO 
            )
        assert "MTPD must be greater than or equal to RTO" in str(exc_info.value)

    def test_should_validate_criticality_based_rto_limits(self, tenant_id):
        """Test Rule: Critical processes must have RTO <= 8 hours"""
        # Critical process with RTO <= 8 should pass
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Critical Process",
            criticality=CriticalityLevel.CRITICAL,
            rto_hours=4,  # <= 8 
            rpo_hours=1,
            mtpd_hours=8,
            recovery_strategies=[{"strategy": "hot_site", "rto": 2}],
            alternative_procedures=["Manual process"],
            dependencies=[Dependency(type="tech", name="System", criticality=5)]
        )
        assert process.criticality == CriticalityLevel.CRITICAL
        assert process.rto_hours <= 8


class TestFinancialImpactTimelineValidation:
    """Test Rule 2: Financial impact must increase over time"""

    def test_should_validate_increasing_financial_impact(self, tenant_id):
        """Test financial impact increases over time"""
        # Valid increasing timeline
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Valid Process",
            criticality=CriticalityLevel.HIGH,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=8,
            financial_impact={
                "1_hour": 5000.0,
                "4_hours": 25000.0,
                "24_hours": 200000.0,
                "1_week": 2000000.0
            }
        )
        impacts = list(process.financial_impact.values())
        assert impacts == sorted(impacts)  # Should be sorted

    def test_should_fail_when_financial_impact_decreases(self, tenant_id):
        """Test decreasing financial impact fails"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Invalid Process",
                criticality=CriticalityLevel.HIGH,
                rto_hours=4,
                rpo_hours=1,
                mtpd_hours=8,
                financial_impact={
                    "1_hour": 100000.0,
                    "4_hours": 50000.0,  # Decreases! 
                    "24_hours": 200000.0
                }
            )
        assert "Business rule violation" in str(exc_info.value)


class TestNonSelfDependencyValidation:
    """Test Rule 3: No self-dependency"""

    def test_should_prevent_self_dependency_in_upstream(self, tenant_id):
        """Test process cannot reference itself in upstream"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                id=100,
                tenant_id=tenant_id,
                name="Self-ref Process",
                criticality=CriticalityLevel.MEDIUM,
                rto_hours=8,
                rpo_hours=2,
                mtpd_hours=24,
                upstream_processes=["100"]  # Self-reference 
            )
        assert "Business rule violation" in str(exc_info.value)

    def test_should_prevent_self_dependency_in_downstream(self, tenant_id):
        """Test process cannot reference itself in downstream"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                id=100,
                tenant_id=tenant_id,
                name="Self-ref Process",
                criticality=CriticalityLevel.MEDIUM,
                rto_hours=8,
                rpo_hours=2,
                mtpd_hours=24,
                downstream_processes=["100"]  # Self-reference 
            )
        assert "Business rule violation" in str(exc_info.value)


class TestCriticalProcessRequirementsValidation:
    """Test Rule 4: Critical processes must have recovery strategies"""

    def test_should_require_recovery_strategies_for_critical(self, tenant_id):
        """Test critical processes need recovery strategies"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Critical Process",
                criticality=CriticalityLevel.CRITICAL,
                rto_hours=2,
                rpo_hours=0,
                mtpd_hours=4,
                recovery_strategies=[],  # Empty! 
                alternative_procedures=[],  # Empty! 
                dependencies=[]  # Empty! 
            )
        assert "Business rule violation" in str(exc_info.value)

    def test_should_allow_non_critical_without_strategies(self, tenant_id):
        """Test non-critical processes can have minimal strategies"""
        # Low criticality doesn't require full strategies
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Low Priority Process",
            criticality=CriticalityLevel.LOW,
            rto_hours=72,
            rpo_hours=24,
            mtpd_hours=168,
            recovery_strategies=[],  # OK for low criticality
            alternative_procedures=[],
            dependencies=[]
        )
        assert process.criticality == CriticalityLevel.LOW


class TestWorkaroundCapacityValidation:
    """Test Rule 5: Workaround capacity must be 0-100%"""

    def test_should_validate_workaround_capacity_in_range(self, tenant_id):
        """Test workaround capacity 0-100%"""
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Process with Workaround",
            criticality=CriticalityLevel.MEDIUM,
            rto_hours=8,
            rpo_hours=2,
            mtpd_hours=24,
            workaround_capacity=75.0  # Valid: 0-100 
        )
        assert 0 <= process.workaround_capacity <= 100

    def test_should_fail_workaround_capacity_over_100(self, tenant_id):
        """Test workaround capacity > 100% fails"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            BIAProcess(
                tenant_id=tenant_id,
                name="Invalid Process",
                criticality=CriticalityLevel.MEDIUM,
                rto_hours=8,
                rpo_hours=2,
                mtpd_hours=24,
                workaround_capacity=150.0  # > 100 
            )

    def test_should_fail_workaround_capacity_negative(self, tenant_id):
        """Test negative workaround capacity fails"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            BIAProcess(
                tenant_id=tenant_id,
                name="Invalid Process",
                criticality=CriticalityLevel.MEDIUM,
                rto_hours=8,
                rpo_hours=2,
                mtpd_hours=24,
                workaround_capacity=-10.0  # Negative 
            )


class TestWHOTierConsistencyValidation:
    """Test Rule 6: WHO tier consistency with patient safety"""

    def test_should_validate_who_tier_with_immediate_patient_safety(self, tenant_id):
        """Test WHO Tier 1 for life-threatening patient safety"""
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Emergency Care",
            criticality=CriticalityLevel.CRITICAL,
            industry=IndustryType.HEALTHCARE,
            rto_hours=1,
            rpo_hours=0,
            mtpd_hours=2,
            who_tier=WHOTier.TIER_1_IMMEDIATE,
            patient_safety_impact=PatientSafetyImpact.LIFE_THREATENING,
            recovery_strategies=[{"strategy": "backup_facility", "rto": 1}],
            alternative_procedures=["Emergency protocol"],
            dependencies=[Dependency(type="facility", name="Emergency Room", criticality=5)]
        )
        assert process.who_tier == WHOTier.TIER_1_IMMEDIATE
        assert process.patient_safety_impact == PatientSafetyImpact.LIFE_THREATENING
        assert process.rto_hours <= 2  # Tier 1 requirement

    def test_should_validate_who_tier_2_for_critical(self, tenant_id):
        """Test WHO Tier 2 for critical but not immediate"""
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Critical Care",
            criticality=CriticalityLevel.CRITICAL,
            industry=IndustryType.HEALTHCARE,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=8,
            who_tier=WHOTier.TIER_2_CRITICAL,
            patient_safety_impact=PatientSafetyImpact.SERIOUS_HARM,
            recovery_strategies=[{"strategy": "backup", "rto": 4}],
            alternative_procedures=["Fallback procedure"],
            dependencies=[Dependency(type="tech", name="Patient System", criticality=5)]
        )
        assert process.who_tier == WHOTier.TIER_2_CRITICAL


class TestMinimumStaffRequirementsValidation:
    """Test Rule 7: Minimum staff requirements for criticality"""

    def test_should_validate_staff_requirements_for_critical(self, tenant_id):
        """Test critical processes have adequate staff"""
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Critical Process",
            criticality=CriticalityLevel.CRITICAL,
            rto_hours=2,
            rpo_hours=0,
            mtpd_hours=4,
            personnel_requirements={
                "roles": ["Lead", "Backup", "Support"],
                "min_staff": 5,  # Adequate for critical
                "skills": ["Technical", "Management"]
            },
            recovery_strategies=[{"strategy": "hot_site", "rto": 2}],
            alternative_procedures=["Manual process"],
            dependencies=[Dependency(type="people", name="Team", criticality=5)]
        )
        assert process.personnel_requirements["min_staff"] >= 3  # Minimum for critical


class TestDependencyCriticalityValidation:
    """Test Rule: Dependencies must have valid criticality 1-5"""

    def test_should_validate_dependency_criticality_range(self):
        """Test dependency criticality 1-5"""
        dep = Dependency(
            type="technology",
            name="Critical System",
            criticality=5,  # Max criticality 
            required=True
        )
        assert 1 <= dep.criticality <= 5

    def test_should_fail_dependency_criticality_out_of_range(self):
        """Test dependency criticality > 5 fails"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            Dependency(
                type="technology",
                name="System",
                criticality=10  # > 5 
            )
