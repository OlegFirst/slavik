"""
Input Validation Tests
Tests for Pydantic validators in domain models
"""

import pytest
from pydantic import ValidationError

from plans_service.models.domain import (
    PlanCreate, PlanUpdate, ProcedureCreate, ProcedureUpdate,
    ResourceCreate, ResourceUpdate, ContactListCreate,
    Contact, RecoveryPriority, ActivationCreate,
    PlanType, PlanPriority, ProcedureType, ResourceType,
    ResourceCriticality, AvailabilityRequirement, ContactListType,
    ActivationType, ReviewFrequency
)


class TestPlanValidation:
    """Test plan validation rules"""

    def test_plan_name_valid(self):
        """Test valid plan name (3-255 chars)"""
        plan = PlanCreate(
            tenant_id="test-tenant",
            plan_code="TEST-001",
            plan_name="Valid Plan Name",
            plan_type=PlanType.BUSINESS_CONTINUITY,
            plan_owner_user_id="user_001"
        )
        assert plan.plan_name == "Valid Plan Name"

    def test_plan_name_too_short(self):
        """Test name < 3 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            PlanCreate(
                tenant_id="test-tenant",
                plan_code="TEST-001",
                plan_name="AB",  # Only 2 chars
                plan_type=PlanType.BUSINESS_CONTINUITY,
                plan_owner_user_id="user_001"
            )

        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error['msg']).lower() for error in errors)

    def test_plan_name_whitespace_stripped(self):
        """Test plan name whitespace is stripped"""
        plan = PlanCreate(
            tenant_id="test-tenant",
            plan_code="TEST-001",
            plan_name="  Valid Plan  ",
            plan_type=PlanType.BUSINESS_CONTINUITY,
            plan_owner_user_id="user_001"
        )
        assert plan.plan_name == "Valid Plan"

    def test_plan_name_too_short_after_strip(self):
        """Test plan name too short after stripping whitespace"""
        with pytest.raises(ValidationError) as exc_info:
            PlanCreate(
                tenant_id="test-tenant",
                plan_code="TEST-001",
                plan_name="  AB  ",  # Only 2 chars after strip
                plan_type=PlanType.BUSINESS_CONTINUITY,
                plan_owner_user_id="user_001"
            )

        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error['msg']).lower() for error in errors)

    def test_rto_valid(self):
        """Test valid RTO (0-8760 hours)"""
        plan = PlanCreate(
            tenant_id="test-tenant",
            plan_code="TEST-001",
            plan_name="Test Plan",
            plan_type=PlanType.BUSINESS_CONTINUITY,
            plan_owner_user_id="user_001",
            rto_hours=24
        )
        assert plan.rto_hours == 24

    def test_rto_zero_valid(self):
        """Test RTO of 0 is valid"""
        plan = PlanCreate(
            tenant_id="test-tenant",
            plan_code="TEST-001",
            plan_name="Test Plan",
            plan_type=PlanType.BUSINESS_CONTINUITY,
            plan_owner_user_id="user_001",
            rto_hours=0
        )
        assert plan.rto_hours == 0

    def test_rto_exceeds_limit(self):
        """Test RTO > 8760 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            PlanCreate(
                tenant_id="test-tenant",
                plan_code="TEST-001",
                plan_name="Test Plan",
                plan_type=PlanType.BUSINESS_CONTINUITY,
                plan_owner_user_id="user_001",
                rto_hours=9000  # Exceeds 1 year
            )

        errors = exc_info.value.errors()
        assert any("8760" in str(error['msg']) for error in errors)

    def test_rto_negative(self):
        """Test negative RTO raises error"""
        with pytest.raises(ValidationError) as exc_info:
            PlanCreate(
                tenant_id="test-tenant",
                plan_code="TEST-001",
                plan_name="Test Plan",
                plan_type=PlanType.BUSINESS_CONTINUITY,
                plan_owner_user_id="user_001",
                rto_hours=-5
            )

        errors = exc_info.value.errors()
        assert any("negative" in str(error['msg']).lower() or "greater than or equal to 0" in str(error['msg']).lower() for error in errors)

    def test_rpo_valid(self):
        """Test valid RPO"""
        plan = PlanCreate(
            tenant_id="test-tenant",
            plan_code="TEST-001",
            plan_name="Test Plan",
            plan_type=PlanType.BUSINESS_CONTINUITY,
            plan_owner_user_id="user_001",
            rpo_hours=4
        )
        assert plan.rpo_hours == 4

    def test_mtpd_valid(self):
        """Test valid MTPD"""
        plan = PlanCreate(
            tenant_id="test-tenant",
            plan_code="TEST-001",
            plan_name="Test Plan",
            plan_type=PlanType.BUSINESS_CONTINUITY,
            plan_owner_user_id="user_001",
            mtpd_hours=72
        )
        assert plan.mtpd_hours == 72

    def test_objective_too_short(self):
        """Test objective < 10 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            PlanCreate(
                tenant_id="test-tenant",
                plan_code="TEST-001",
                plan_name="Test Plan",
                plan_type=PlanType.BUSINESS_CONTINUITY,
                plan_owner_user_id="user_001",
                objective="Short"  # Too short
            )

        errors = exc_info.value.errors()
        assert any("at least 10 characters" in str(error['msg']).lower() for error in errors)

    def test_scope_too_short(self):
        """Test scope < 10 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            PlanCreate(
                tenant_id="test-tenant",
                plan_code="TEST-001",
                plan_name="Test Plan",
                plan_type=PlanType.BUSINESS_CONTINUITY,
                plan_owner_user_id="user_001",
                scope="Brief"  # Too short
            )

        errors = exc_info.value.errors()
        assert any("at least 10 characters" in str(error['msg']).lower() for error in errors)


class TestProcedureValidation:
    """Test procedure validation rules"""

    def test_procedure_name_valid(self):
        """Test valid procedure name"""
        procedure = ProcedureCreate(
            tenant_id="test-tenant",
            procedure_name="Activate Emergency Response",
            procedure_type=ProcedureType.IMMEDIATE_RESPONSE
        )
        assert procedure.procedure_name == "Activate Emergency Response"

    def test_procedure_name_too_short(self):
        """Test procedure name < 3 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ProcedureCreate(
                tenant_id="test-tenant",
                procedure_name="AB",
                procedure_type=ProcedureType.IMMEDIATE_RESPONSE
            )

        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error['msg']).lower() for error in errors)

    def test_procedure_duration_valid(self):
        """Test valid procedure duration"""
        procedure = ProcedureCreate(
            tenant_id="test-tenant",
            procedure_name="Test Procedure",
            procedure_type=ProcedureType.IMMEDIATE_RESPONSE,
            estimated_duration_minutes=60
        )
        assert procedure.estimated_duration_minutes == 60

    def test_procedure_duration_exceeds_week(self):
        """Test duration > 10080 minutes raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ProcedureCreate(
                tenant_id="test-tenant",
                procedure_name="Test Procedure",
                procedure_type=ProcedureType.IMMEDIATE_RESPONSE,
                estimated_duration_minutes=11000  # More than 1 week
            )

        errors = exc_info.value.errors()
        assert any("10080" in str(error['msg']) or "week" in str(error['msg']).lower() for error in errors)

    def test_procedure_duration_negative(self):
        """Test negative duration raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ProcedureCreate(
                tenant_id="test-tenant",
                procedure_name="Test Procedure",
                procedure_type=ProcedureType.IMMEDIATE_RESPONSE,
                estimated_duration_minutes=-30
            )

        errors = exc_info.value.errors()
        assert any("negative" in str(error['msg']).lower() or "greater than or equal to 0" in str(error['msg']).lower() for error in errors)

    def test_sequence_valid(self):
        """Test valid sequence number"""
        procedure = ProcedureCreate(
            tenant_id="test-tenant",
            procedure_name="Test Procedure",
            procedure_type=ProcedureType.IMMEDIATE_RESPONSE,
            sequence=50
        )
        assert procedure.sequence == 50

    def test_sequence_negative(self):
        """Test negative sequence raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ProcedureCreate(
                tenant_id="test-tenant",
                procedure_name="Test Procedure",
                procedure_type=ProcedureType.IMMEDIATE_RESPONSE,
                sequence=-10
            )

        errors = exc_info.value.errors()
        assert any("negative" in str(error['msg']).lower() or "greater than or equal to 0" in str(error['msg']).lower() for error in errors)

    def test_sequence_exceeds_limit(self):
        """Test sequence > 10000 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ProcedureCreate(
                tenant_id="test-tenant",
                procedure_name="Test Procedure",
                procedure_type=ProcedureType.IMMEDIATE_RESPONSE,
                sequence=10001
            )

        errors = exc_info.value.errors()
        assert any("10000" in str(error['msg']) or "reasonable limit" in str(error['msg']).lower() for error in errors)


class TestResourceValidation:
    """Test resource validation rules"""

    def test_resource_name_valid(self):
        """Test valid resource name"""
        resource = ResourceCreate(
            tenant_id="test-tenant",
            resource_name="Backup Server",
            resource_type=ResourceType.TECHNOLOGY,
            availability_requirement=AvailabilityRequirement.IMMEDIATE,
            criticality=ResourceCriticality.CRITICAL
        )
        assert resource.resource_name == "Backup Server"

    def test_quantity_valid(self):
        """Test valid quantity (>= 1)"""
        resource = ResourceCreate(
            tenant_id="test-tenant",
            resource_name="Server",
            resource_type=ResourceType.TECHNOLOGY,
            availability_requirement=AvailabilityRequirement.IMMEDIATE,
            criticality=ResourceCriticality.CRITICAL,
            quantity_required=5
        )
        assert resource.quantity_required == 5

    def test_quantity_minimum(self):
        """Test resource quantity >= 1"""
        with pytest.raises(ValidationError) as exc_info:
            ResourceCreate(
                tenant_id="test-tenant",
                resource_name="Server",
                resource_type=ResourceType.TECHNOLOGY,
                availability_requirement=AvailabilityRequirement.IMMEDIATE,
                criticality=ResourceCriticality.CRITICAL,
                quantity_required=0  # Must be at least 1
            )

        errors = exc_info.value.errors()
        assert any("at least 1" in str(error['msg']).lower() or "greater than or equal to 1" in str(error['msg']).lower() for error in errors)

    def test_quantity_exceeds_limit(self):
        """Test quantity exceeds reasonable limit"""
        with pytest.raises(ValidationError) as exc_info:
            ResourceCreate(
                tenant_id="test-tenant",
                resource_name="Server",
                resource_type=ResourceType.TECHNOLOGY,
                availability_requirement=AvailabilityRequirement.IMMEDIATE,
                criticality=ResourceCriticality.CRITICAL,
                quantity_required=2000000  # Exceeds limit
            )

        errors = exc_info.value.errors()
        assert any("1,000,000" in str(error['msg']) or "1000000" in str(error['msg']) for error in errors)


class TestContactValidation:
    """Test contact validation rules"""

    def test_contact_email_format(self):
        """Test email must contain '@'"""
        with pytest.raises(ValidationError) as exc_info:
            Contact(
                name="John Doe",
                role="Manager",
                primary_phone="+1-555-0001",
                email="invalid-email"  # Missing @
            )

        errors = exc_info.value.errors()
        assert any("@" in str(error['msg']) for error in errors)

    def test_contact_email_valid(self):
        """Test valid email format"""
        contact = Contact(
            name="John Doe",
            role="Manager",
            primary_phone="+1-555-0001",
            email="john.doe@company.com"
        )
        assert contact.email == "john.doe@company.com"

    def test_contact_email_lowercase(self):
        """Test email is converted to lowercase"""
        contact = Contact(
            name="John Doe",
            role="Manager",
            primary_phone="+1-555-0001",
            email="John.Doe@Company.COM"
        )
        assert contact.email == "john.doe@company.com"

    def test_contact_name_too_short(self):
        """Test contact name < 2 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            Contact(
                name="J",
                role="Manager",
                primary_phone="+1-555-0001",
                email="j@company.com"
            )

        errors = exc_info.value.errors()
        assert any("at least 2 characters" in str(error['msg']).lower() for error in errors)

    def test_contact_role_too_short(self):
        """Test contact role < 2 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            Contact(
                name="John Doe",
                role="M",
                primary_phone="+1-555-0001",
                email="john@company.com"
            )

        errors = exc_info.value.errors()
        assert any("at least 2 characters" in str(error['msg']).lower() for error in errors)

    def test_contact_phone_too_short(self):
        """Test phone number < 7 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            Contact(
                name="John Doe",
                role="Manager",
                primary_phone="12345",  # Too short
                email="john@company.com"
            )

        errors = exc_info.value.errors()
        assert any("at least 7 characters" in str(error['msg']).lower() for error in errors)

    def test_contact_priority_valid(self):
        """Test valid notification priority"""
        contact = Contact(
            name="John Doe",
            role="Manager",
            primary_phone="+1-555-0001",
            email="john@company.com",
            notification_priority=5
        )
        assert contact.notification_priority == 5

    def test_contact_priority_exceeds_limit(self):
        """Test notification priority > 10 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            Contact(
                name="John Doe",
                role="Manager",
                primary_phone="+1-555-0001",
                email="john@company.com",
                notification_priority=15
            )

        errors = exc_info.value.errors()
        assert any("10" in str(error['msg']) or "less than or equal to 10" in str(error['msg']).lower() for error in errors)


class TestRecoveryPriorityValidation:
    """Test recovery priority validation"""

    def test_recovery_priority_valid(self):
        """Test valid recovery priority"""
        priority = RecoveryPriority(
            priority_order=1,
            activity="Restore critical systems",
            rto_hours=24
        )
        assert priority.priority_order == 1

    def test_priority_order_too_low(self):
        """Test priority order < 1 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            RecoveryPriority(
                priority_order=0,
                activity="Restore systems",
                rto_hours=24
            )

        errors = exc_info.value.errors()
        assert any("at least 1" in str(error['msg']).lower() or "greater than or equal to 1" in str(error['msg']).lower() for error in errors)

    def test_priority_order_exceeds_limit(self):
        """Test priority order > 1000 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            RecoveryPriority(
                priority_order=1001,
                activity="Restore systems",
                rto_hours=24
            )

        errors = exc_info.value.errors()
        assert any("1000" in str(error['msg']) for error in errors)

    def test_activity_too_short(self):
        """Test activity < 3 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            RecoveryPriority(
                priority_order=1,
                activity="AB",
                rto_hours=24
            )

        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error['msg']).lower() for error in errors)

    def test_rto_hours_negative(self):
        """Test negative RTO hours raises error"""
        with pytest.raises(ValidationError) as exc_info:
            RecoveryPriority(
                priority_order=1,
                activity="Restore systems",
                rto_hours=-5
            )

        errors = exc_info.value.errors()
        assert any("negative" in str(error['msg']).lower() or "greater than or equal to 0" in str(error['msg']).lower() for error in errors)

    def test_rto_hours_exceeds_year(self):
        """Test RTO hours > 8760 raises error"""
        with pytest.raises(ValidationError) as exc_info:
            RecoveryPriority(
                priority_order=1,
                activity="Restore systems",
                rto_hours=10000
            )

        errors = exc_info.value.errors()
        assert any("8760" in str(error['msg']) for error in errors)


class TestContactListValidation:
    """Test contact list validation"""

    def test_contact_list_valid(self):
        """Test valid contact list"""
        contact_list = ContactListCreate(
            tenant_id="test-tenant",
            list_name="Emergency Contacts",
            list_type=ContactListType.INTERNAL,
            contacts=[{"name": "John", "role": "Manager", "email": "j@test.com", "primary_phone": "1234567"}]
        )
        assert contact_list.list_name == "Emergency Contacts"

    def test_contact_list_name_too_short(self):
        """Test list name < 3 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ContactListCreate(
                tenant_id="test-tenant",
                list_name="AB",
                list_type=ContactListType.INTERNAL,
                contacts=[{"name": "John", "role": "Manager"}]
            )

        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error['msg']).lower() for error in errors)

    def test_contact_list_empty_contacts(self):
        """Test empty contacts list raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ContactListCreate(
                tenant_id="test-tenant",
                list_name="Emergency Contacts",
                list_type=ContactListType.INTERNAL,
                contacts=[]  # Empty list
            )

        errors = exc_info.value.errors()
        assert any("at least one contact" in str(error['msg']).lower() or "at least 1" in str(error['msg']).lower() for error in errors)


class TestActivationValidation:
    """Test activation validation"""

    def test_activation_name_valid(self):
        """Test valid activation name"""
        activation = ActivationCreate(
            tenant_id="test-tenant",
            activation_name="Test Exercise 2024",
            activation_type=ActivationType.TEST_EXERCISE
        )
        assert activation.activation_name == "Test Exercise 2024"

    def test_activation_name_too_short(self):
        """Test activation name < 3 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ActivationCreate(
                tenant_id="test-tenant",
                activation_name="AB",
                activation_type=ActivationType.TEST_EXERCISE
            )

        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error['msg']).lower() for error in errors)

    def test_trigger_event_too_short(self):
        """Test trigger event < 5 chars raises error"""
        with pytest.raises(ValidationError) as exc_info:
            ActivationCreate(
                tenant_id="test-tenant",
                activation_name="Test Exercise",
                activation_type=ActivationType.TEST_EXERCISE,
                trigger_event="Fire"  # Too short
            )

        errors = exc_info.value.errors()
        assert any("at least 5 characters" in str(error['msg']).lower() for error in errors)
