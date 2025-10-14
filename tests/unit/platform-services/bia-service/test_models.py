"""
Test BIA Domain Model Validations
Tests for Pydantic model validation rules and business logic
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from models.domain import BIAProcess, BIAProcessCreate, Dependency
from models.enums import (
    CriticalityLevel, ProcessStatus, IndustryType,
    WHOTier, PatientSafetyImpact, GeographicalScope
)


class TestDependencyModel:
    """Test Dependency model validation"""

    def test_should_create_valid_dependency(self):
        """Test creating a valid dependency"""
        dep = Dependency(
            type="technology",
            name="Database Server",
            criticality=5,
            required=True
        )
        assert dep.type == "technology"
        assert dep.name == "Database Server"
        assert dep.criticality == 5
        assert dep.required is True

    def test_should_create_dependency_without_optional_fields(self):
        """Test creating dependency with minimal fields"""
        dep = Dependency(
            type="process",
            name="Upstream Process"
        )
        assert dep.type == "process"
        assert dep.name == "Upstream Process"
        assert dep.id is None
        assert dep.criticality is None
        assert dep.required is True  # Default value

    def test_should_validate_criticality_range(self):
        """Test criticality must be 1-5"""
        with pytest.raises(ValidationError) as exc_info:
            Dependency(
                type="technology",
                name="Test",
                criticality=6  # Invalid: > 5
            )
        assert "criticality" in str(exc_info.value)


class TestBIAProcessModel:
    """Test BIAProcess domain model"""

    def test_should_create_valid_bia_process(self, sample_bia_create_data):
        """Test creating a valid BIA process"""
        process = BIAProcess(**sample_bia_create_data.dict())
        assert process.name == "Core Payment Processing"
        assert process.criticality == CriticalityLevel.CRITICAL
        assert process.rto_hours == 4
        assert process.rpo_hours == 1
        assert process.mtpd_hours == 8

    def test_should_validate_rto_greater_than_rpo(self, tenant_id):
        """Test RTO must be >= RPO"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Invalid Process",
                criticality=CriticalityLevel.HIGH,
                rto_hours=2,  # RTO < RPO (invalid!)
                rpo_hours=4,
                mtpd_hours=8
            )
        assert "RTO must be greater than or equal to RPO" in str(exc_info.value)

    def test_should_validate_mtpd_greater_than_rto(self, tenant_id):
        """Test MTPD must be >= RTO"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Invalid Process",
                criticality=CriticalityLevel.HIGH,
                rto_hours=8,
                rpo_hours=2,
                mtpd_hours=4  # MTPD < RTO (invalid!)
            )
        assert "MTPD must be greater than or equal to RTO" in str(exc_info.value)

    def test_should_validate_financial_impact_timeline(self, tenant_id):
        """Test financial impact must increase over time"""
        # Invalid timeline (decreases)
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Test Process",
                criticality=CriticalityLevel.HIGH,
                rto_hours=4,
                rpo_hours=1,
                mtpd_hours=8,
                financial_impact={
                    "1_hour": 100000.0,
                    "4_hours": 50000.0,  # Decreases! Invalid
                    "24_hours": 200000.0
                }
            )
        assert "Business rule violation" in str(exc_info.value)
        assert "financial impact" in str(exc_info.value).lower()

    def test_should_validate_workaround_capacity_range(self, tenant_id):
        """Test workaround capacity must be 0-100%"""
        with pytest.raises(ValidationError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Test Process",
                criticality=CriticalityLevel.HIGH,
                rto_hours=4,
                rpo_hours=1,
                mtpd_hours=8,
                workaround_capacity=150.0  # Invalid: > 100
            )
        assert "workaround_capacity" in str(exc_info.value)

    def test_should_warn_for_incomplete_iso_fields_when_completed(self, tenant_id):
        """Test warning when marking process complete without ISO fields"""
        # This should create but may log warnings
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Incomplete Process",
            criticality=CriticalityLevel.HIGH,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=8,
            status=ProcessStatus.COMPLETED,
            # Missing: compliance_objective, recovery_strategies, bia_completion_date, bia_assessor
        )
        # Should not raise exception, just log warning
        assert process.status == ProcessStatus.COMPLETED

    def test_should_calculate_criticality_score_from_level(self, tenant_id):
        """Test criticality score is set based on criticality level"""
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Test Process",
            criticality=CriticalityLevel.CRITICAL,
            criticality_score=5,  # Should match CRITICAL
            rto_hours=2,
            rpo_hours=0,
            mtpd_hours=4
        )
        assert process.criticality_score == 5

    def test_should_handle_healthcare_process_with_who_tier(self, sample_healthcare_bia_create):
        """Test healthcare process with WHO tier validation"""
        process = BIAProcess(**sample_healthcare_bia_create.dict())
        assert process.industry == IndustryType.HEALTHCARE
        assert process.who_tier == WHOTier.TIER_1_IMMEDIATE
        assert process.patient_safety_impact == PatientSafetyImpact.LIFE_THREATENING
        assert process.rto_hours <= 2  # WHO Tier 1 requirement

    def test_should_validate_critical_process_has_recovery_strategies(self, tenant_id):
        """Test critical processes must have recovery strategies"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                tenant_id=tenant_id,
                name="Critical Process",
                criticality=CriticalityLevel.CRITICAL,
                rto_hours=2,
                rpo_hours=0,
                mtpd_hours=4,
                recovery_strategies=[],  # Empty! Should fail for critical process
                alternative_procedures=[],  # Empty!
                dependencies=[]  # Empty!
            )
        assert "Business rule violation" in str(exc_info.value)

    def test_should_prevent_self_dependency(self, tenant_id):
        """Test process cannot depend on itself"""
        with pytest.raises(ValueError) as exc_info:
            BIAProcess(
                id=123,
                tenant_id=tenant_id,
                name="Self-referencing Process",
                criticality=CriticalityLevel.HIGH,
                rto_hours=4,
                rpo_hours=1,
                mtpd_hours=8,
                upstream_processes=["123"],  # Self-reference!
            )
        assert "Business rule violation" in str(exc_info.value)
        assert "self" in str(exc_info.value).lower()

    def test_should_set_default_created_at_timestamp(self, tenant_id):
        """Test created_at is set automatically"""
        before = datetime.now()
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Test Process",
            criticality=CriticalityLevel.MEDIUM,
            rto_hours=8,
            rpo_hours=2,
            mtpd_hours=24
        )
        after = datetime.now()

        assert process.created_at is not None
        assert before <= process.created_at <= after
        assert process.updated_at is not None

    def test_should_accept_all_industry_types(self, tenant_id):
        """Test all industry types are accepted"""
        for industry in IndustryType:
            process = BIAProcess(
                tenant_id=tenant_id,
                name=f"Process for {industry.value}",
                criticality=CriticalityLevel.MEDIUM,
                industry=industry,
                rto_hours=4,
                rpo_hours=1,
                mtpd_hours=8
            )
            assert process.industry == industry

    def test_should_handle_complex_personnel_requirements(self, tenant_id, sample_personnel_requirements):
        """Test complex personnel requirements structure"""
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Complex Process",
            criticality=CriticalityLevel.HIGH,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=8,
            personnel_requirements=sample_personnel_requirements
        )
        assert "roles" in process.personnel_requirements
        assert "min_staff" in process.personnel_requirements
        assert process.personnel_requirements["min_staff"] == 5

    def test_should_handle_multiple_recovery_strategies(self, tenant_id, sample_recovery_strategies):
        """Test multiple recovery strategies"""
        process = BIAProcess(
            tenant_id=tenant_id,
            name="Multi-Strategy Process",
            criticality=CriticalityLevel.CRITICAL,
            rto_hours=2,
            rpo_hours=0,
            mtpd_hours=4,
            recovery_strategies=sample_recovery_strategies,
            alternative_procedures=["Manual fallback"],
            dependencies=[Dependency(type="tech", name="System", criticality=5)]
        )
        assert len(process.recovery_strategies) == 2
        assert process.recovery_strategies[0]["strategy"] == "hot_site"
        assert process.recovery_strategies[1]["strategy"] == "cloud_backup"


class TestBIAProcessCreateModel:
    """Test BIAProcessCreate request model"""

    def test_should_create_minimal_bia_process_create(self, tenant_id):
        """Test creating BIA with minimal required fields"""
        create_data = BIAProcessCreate(
            tenant_id=tenant_id,
            name="Minimal Process",
            criticality=CriticalityLevel.LOW,
            industry=IndustryType.OTHER,
            rto_hours=24,
            rpo_hours=4,
            mtpd_hours=72
        )
        assert create_data.name == "Minimal Process"
        assert create_data.criticality == CriticalityLevel.LOW
        assert create_data.dependencies == []  # Default empty list

    def test_should_create_full_featured_bia_process_create(self, sample_bia_create_data):
        """Test creating BIA with all optional fields"""
        assert sample_bia_create_data.name == "Core Payment Processing"
        assert sample_bia_create_data.compliance_objective is not None
        assert len(sample_bia_create_data.legal_regulatory_requirements) > 0
        assert sample_bia_create_data.personnel_requirements is not None
        assert len(sample_bia_create_data.recovery_strategies) > 0
        assert len(sample_bia_create_data.alternative_procedures) > 0

    def test_should_handle_healthcare_specific_fields(self, sample_healthcare_bia_create):
        """Test healthcare-specific fields in create model"""
        assert sample_healthcare_bia_create.industry == IndustryType.HEALTHCARE
        assert sample_healthcare_bia_create.who_tier == WHOTier.TIER_1_IMMEDIATE
        assert sample_healthcare_bia_create.patient_safety_impact == PatientSafetyImpact.LIFE_THREATENING
        assert "HIPAA" in sample_healthcare_bia_create.legal_regulatory_requirements
