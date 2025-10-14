"""
Unit Tests for Process Framework

Tests the core functionality of the Process Framework including:
- Process definitions and steps
- Form field validation
- Process instance execution
- Step navigation
- State management

Author: AI Platform Team
Date: 2025-10-11
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

# Import Process Framework components
import sys
sys.path.append("/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence")

from process_framework import (
    ProcessDefinition,
    ProcessStep,
    ProcessInstance,
    ProcessFramework,
    FormField,
    FieldValidation,
    StepType,
    ValidationRule,
    StepExecution
)


# =====================================================
# Test Data Fixtures
# =====================================================

@pytest.fixture
def sample_form_field():
    """Sample form field with validation"""
    return FormField(
        id="organization_name",
        label="Organization Name",
        field_type="text",
        required=True,
        validations=[
            FieldValidation(
                rule=ValidationRule.REQUIRED,
                message="Organization name is required"
            ),
            FieldValidation(
                rule=ValidationRule.MIN_LENGTH,
                value=3,
                message="Minimum 3 characters"
            )
        ]
    )


@pytest.fixture
def sample_process_step():
    """Sample process step"""
    return ProcessStep(
        id="bia_initiation",
        name="BIA Initiation",
        description="Initiate Business Impact Analysis",
        step_type=StepType.FORM_INPUT,
        form_fields=[
            FormField(
                id="scope",
                label="Analysis Scope",
                field_type="textarea",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.REQUIRED,
                        message="Scope is required"
                    )
                ]
            )
        ],
        next_steps=["critical_functions"],
        allowed_roles=["bcm_analyst", "admin"]
    )


@pytest.fixture
def sample_process_definition(sample_process_step):
    """Sample process definition"""
    return ProcessDefinition(
        id="test_process_v1",
        name="Test Process",
        version="1.0",
        description="Test process for unit testing",
        category="testing",
        steps={
            "bia_initiation": sample_process_step,
            "END": ProcessStep(
                id="END",
                name="End",
                description="Process end",
                step_type=StepType.EXECUTION,
                form_fields=[],
                next_steps=[],
                allowed_roles=[]
            )
        },
        start_step_id="bia_initiation",
        end_step_ids=["END"],
        iso_clause="8.2.2"
    )


@pytest.fixture
def process_framework(sample_process_definition):
    """Process Framework instance"""
    framework = ProcessFramework()
    framework.register_process(sample_process_definition)
    return framework


# =====================================================
# Test FormField and Validation
# =====================================================

class TestFormField:
    """Test FormField dataclass and validation"""

    def test_form_field_creation(self, sample_form_field):
        """Test FormField creation"""
        assert sample_form_field.id == "organization_name"
        assert sample_form_field.required is True
        assert len(sample_form_field.validations) == 2

    def test_validation_rule_required(self, sample_form_field):
        """Test REQUIRED validation rule"""
        validation = sample_form_field.validations[0]
        assert validation.rule == ValidationRule.REQUIRED
        assert validation.message == "Organization name is required"

    def test_validation_rule_min_length(self, sample_form_field):
        """Test MIN_LENGTH validation rule"""
        validation = sample_form_field.validations[1]
        assert validation.rule == ValidationRule.MIN_LENGTH
        assert validation.value == 3

    def test_form_field_optional(self):
        """Test optional form field"""
        field = FormField(
            id="notes",
            label="Notes",
            field_type="textarea",
            required=False,
            validations=[]
        )
        assert field.required is False
        assert len(field.validations) == 0

    def test_form_field_enum_validation(self):
        """Test ENUM validation rule"""
        field = FormField(
            id="status",
            label="Status",
            field_type="select",
            required=True,
            validations=[
                FieldValidation(
                    rule=ValidationRule.ENUM,
                    value=["active", "inactive", "pending"],
                    message="Invalid status"
                )
            ]
        )
        assert field.validations[0].rule == ValidationRule.ENUM
        assert "active" in field.validations[0].value

    def test_form_field_pattern_validation(self):
        """Test PATTERN validation rule"""
        field = FormField(
            id="email",
            label="Email",
            field_type="email",
            required=True,
            validations=[
                FieldValidation(
                    rule=ValidationRule.PATTERN,
                    value=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    message="Invalid email format"
                )
            ]
        )
        assert field.validations[0].rule == ValidationRule.PATTERN

    def test_form_field_numeric_range_validation(self):
        """Test NUMERIC_RANGE validation rule"""
        field = FormField(
            id="rto_hours",
            label="RTO (hours)",
            field_type="number",
            required=True,
            validations=[
                FieldValidation(
                    rule=ValidationRule.NUMERIC_RANGE,
                    value={"min": 0, "max": 168},
                    message="RTO must be between 0 and 168 hours"
                )
            ]
        )
        assert field.validations[0].rule == ValidationRule.NUMERIC_RANGE
        assert field.validations[0].value["min"] == 0
        assert field.validations[0].value["max"] == 168


# =====================================================
# Test ProcessStep
# =====================================================

class TestProcessStep:
    """Test ProcessStep dataclass"""

    def test_process_step_creation(self, sample_process_step):
        """Test ProcessStep creation"""
        assert sample_process_step.id == "bia_initiation"
        assert sample_process_step.step_type == StepType.FORM_INPUT
        assert len(sample_process_step.form_fields) == 1
        assert sample_process_step.next_steps == ["critical_functions"]

    def test_process_step_allowed_roles(self, sample_process_step):
        """Test allowed roles"""
        assert "bcm_analyst" in sample_process_step.allowed_roles
        assert "admin" in sample_process_step.allowed_roles

    def test_process_step_approval_type(self):
        """Test APPROVAL step type"""
        step = ProcessStep(
            id="manager_approval",
            name="Manager Approval",
            description="Requires manager approval",
            step_type=StepType.APPROVAL,
            form_fields=[],
            next_steps=["END"],
            allowed_roles=["manager"],
            auto_approve=False
        )
        assert step.step_type == StepType.APPROVAL
        assert step.auto_approve is False

    def test_process_step_analysis_type(self):
        """Test ANALYSIS step type with AI agent"""
        step = ProcessStep(
            id="impact_analysis",
            name="Impact Analysis",
            description="AI-powered impact analysis",
            step_type=StepType.ANALYSIS,
            form_fields=[],
            next_steps=["report_generation"],
            allowed_roles=["system"],
            ai_agent="analytics_specialist"
        )
        assert step.step_type == StepType.ANALYSIS
        assert step.ai_agent == "analytics_specialist"

    def test_process_step_document_generation(self):
        """Test DOCUMENT_GENERATION step type"""
        step = ProcessStep(
            id="generate_report",
            name="Generate BIA Report",
            description="Generate BIA report from template",
            step_type=StepType.DOCUMENT_GENERATION,
            form_fields=[],
            next_steps=["approval"],
            allowed_roles=["system"],
            document_template="bia_report_v1"
        )
        assert step.step_type == StepType.DOCUMENT_GENERATION
        assert step.document_template == "bia_report_v1"

    def test_process_step_decision_type(self):
        """Test DECISION step type with conditional transitions"""
        step = ProcessStep(
            id="risk_decision",
            name="Risk Decision",
            description="Decide on risk treatment",
            step_type=StepType.DECISION,
            form_fields=[],
            next_steps=["high_risk_path", "low_risk_path"],
            allowed_roles=["risk_manager"],
            transition_conditions={
                "high_risk_path": {"risk_level": "high"},
                "low_risk_path": {"risk_level": "low"}
            }
        )
        assert step.step_type == StepType.DECISION
        assert "high_risk_path" in step.transition_conditions


# =====================================================
# Test ProcessDefinition
# =====================================================

class TestProcessDefinition:
    """Test ProcessDefinition dataclass"""

    def test_process_definition_creation(self, sample_process_definition):
        """Test ProcessDefinition creation"""
        assert sample_process_definition.id == "test_process_v1"
        assert sample_process_definition.version == "1.0"
        assert sample_process_definition.category == "testing"
        assert sample_process_definition.iso_clause == "8.2.2"

    def test_process_definition_steps(self, sample_process_definition):
        """Test process steps dictionary"""
        assert "bia_initiation" in sample_process_definition.steps
        assert "END" in sample_process_definition.steps
        assert len(sample_process_definition.steps) == 2

    def test_process_definition_navigation(self, sample_process_definition):
        """Test process navigation (start/end)"""
        assert sample_process_definition.start_step_id == "bia_initiation"
        assert "END" in sample_process_definition.end_step_ids

    def test_process_definition_compliance(self, sample_process_definition):
        """Test compliance requirements"""
        assert sample_process_definition.iso_clause == "8.2.2"

    def test_process_definition_get_step(self, sample_process_definition):
        """Test getting a step by ID"""
        step = sample_process_definition.steps.get("bia_initiation")
        assert step is not None
        assert step.id == "bia_initiation"


# =====================================================
# Test ProcessFramework - Registration
# =====================================================

class TestProcessFrameworkRegistration:
    """Test process registration"""

    def test_register_process(self, process_framework, sample_process_definition):
        """Test registering a process"""
        assert sample_process_definition.id in process_framework.processes
        registered = process_framework.processes[sample_process_definition.id]
        assert registered.name == "Test Process"

    def test_register_duplicate_process(self, process_framework, sample_process_definition):
        """Test registering duplicate process raises error"""
        with pytest.raises(ValueError, match="already registered"):
            process_framework.register_process(sample_process_definition)

    def test_get_process(self, process_framework):
        """Test getting a registered process"""
        process = process_framework.get_process("test_process_v1")
        assert process is not None
        assert process.id == "test_process_v1"

    def test_get_nonexistent_process(self, process_framework):
        """Test getting nonexistent process returns None"""
        process = process_framework.get_process("nonexistent")
        assert process is None

    def test_list_processes(self, process_framework):
        """Test listing all registered processes"""
        processes = process_framework.list_processes()
        assert len(processes) == 1
        assert processes[0]["id"] == "test_process_v1"
        assert processes[0]["name"] == "Test Process"


# =====================================================
# Test ProcessFramework - Instance Creation
# =====================================================

class TestProcessFrameworkInstanceCreation:
    """Test process instance creation and management"""

    def test_start_process(self, process_framework):
        """Test starting a new process instance"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com",
            initial_data={"organization": "Test Org"}
        )

        assert instance is not None
        assert instance.process_id == "test_process_v1"
        assert instance.status == "active"
        assert instance.current_step_id == "bia_initiation"
        assert instance.started_by == "test_user@example.com"
        assert instance.data["organization"] == "Test Org"

    def test_start_nonexistent_process(self, process_framework):
        """Test starting nonexistent process raises error"""
        with pytest.raises(ValueError, match="not found"):
            process_framework.start_process(
                process_id="nonexistent",
                started_by="test_user@example.com"
            )

    def test_get_instance(self, process_framework):
        """Test getting a process instance"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com"
        )

        retrieved = process_framework.get_instance(instance.instance_id)
        assert retrieved is not None
        assert retrieved.instance_id == instance.instance_id

    def test_get_nonexistent_instance(self, process_framework):
        """Test getting nonexistent instance returns None"""
        instance = process_framework.get_instance("nonexistent-id")
        assert instance is None

    def test_instance_id_format(self, process_framework):
        """Test instance ID format"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com"
        )

        # Format: process_id-timestamp
        assert instance.instance_id.startswith("test_process_v1-")


# =====================================================
# Test ProcessFramework - Step Execution
# =====================================================

class TestProcessFrameworkStepExecution:
    """Test process step execution"""

    def test_get_current_step_form(self, process_framework):
        """Test getting form for current step"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com"
        )

        form = process_framework.get_current_step_form(instance.instance_id)
        assert form is not None
        assert form["step_id"] == "bia_initiation"
        assert form["step_name"] == "BIA Initiation"
        assert len(form["fields"]) == 1
        assert form["fields"][0]["id"] == "scope"

    def test_execute_step_success(self, process_framework):
        """Test successful step execution"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com"
        )

        result, next_step = process_framework.execute_step(
            instance_id=instance.instance_id,
            step_data={"scope": "This is a valid scope description"},
            executed_by="test_user@example.com"
        )

        assert result["success"] is True
        assert next_step == "critical_functions"

    def test_execute_step_validation_failure(self, process_framework):
        """Test step execution with validation failure"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com"
        )

        result, next_step = process_framework.execute_step(
            instance_id=instance.instance_id,
            step_data={},  # Missing required field
            executed_by="test_user@example.com"
        )

        assert result["success"] is False
        assert "errors" in result
        assert next_step is None

    def test_step_execution_history(self, process_framework):
        """Test step execution is recorded in history"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com"
        )

        process_framework.execute_step(
            instance_id=instance.instance_id,
            step_data={"scope": "Valid scope"},
            executed_by="test_user@example.com"
        )

        updated_instance = process_framework.get_instance(instance.instance_id)
        assert len(updated_instance.step_history) > 0
        last_execution = updated_instance.step_history[-1]
        assert last_execution["step_id"] == "bia_initiation"
        assert last_execution["executed_by"] == "test_user@example.com"

    def test_process_data_accumulation(self, process_framework):
        """Test process data accumulates across steps"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com",
            initial_data={"organization": "Test Org"}
        )

        process_framework.execute_step(
            instance_id=instance.instance_id,
            step_data={"scope": "Valid scope"},
            executed_by="test_user@example.com"
        )

        updated_instance = process_framework.get_instance(instance.instance_id)
        assert updated_instance.data["organization"] == "Test Org"
        assert updated_instance.data["scope"] == "Valid scope"


# =====================================================
# Test ProcessFramework - Validation
# =====================================================

class TestProcessFrameworkValidation:
    """Test form validation logic"""

    def test_validate_required_field(self, process_framework):
        """Test REQUIRED validation"""
        field = FormField(
            id="test_field",
            label="Test",
            field_type="text",
            required=True,
            validations=[
                FieldValidation(
                    rule=ValidationRule.REQUIRED,
                    message="Required"
                )
            ]
        )

        # Empty value
        errors = process_framework._validate_field(field, "")
        assert len(errors) > 0
        assert "Required" in errors[0]

        # Valid value
        errors = process_framework._validate_field(field, "Value")
        assert len(errors) == 0

    def test_validate_min_length(self, process_framework):
        """Test MIN_LENGTH validation"""
        field = FormField(
            id="test_field",
            label="Test",
            field_type="text",
            required=True,
            validations=[
                FieldValidation(
                    rule=ValidationRule.MIN_LENGTH,
                    value=5,
                    message="Minimum 5 characters"
                )
            ]
        )

        # Too short
        errors = process_framework._validate_field(field, "ABC")
        assert len(errors) > 0

        # Valid
        errors = process_framework._validate_field(field, "ABCDE")
        assert len(errors) == 0

    def test_validate_max_length(self, process_framework):
        """Test MAX_LENGTH validation"""
        field = FormField(
            id="test_field",
            label="Test",
            field_type="text",
            required=True,
            validations=[
                FieldValidation(
                    rule=ValidationRule.MAX_LENGTH,
                    value=10,
                    message="Maximum 10 characters"
                )
            ]
        )

        # Too long
        errors = process_framework._validate_field(field, "A" * 20)
        assert len(errors) > 0

        # Valid
        errors = process_framework._validate_field(field, "ABCDE")
        assert len(errors) == 0

    def test_validate_enum(self, process_framework):
        """Test ENUM validation"""
        field = FormField(
            id="status",
            label="Status",
            field_type="select",
            required=True,
            validations=[
                FieldValidation(
                    rule=ValidationRule.ENUM,
                    value=["active", "inactive"],
                    message="Invalid status"
                )
            ]
        )

        # Invalid value
        errors = process_framework._validate_field(field, "pending")
        assert len(errors) > 0

        # Valid value
        errors = process_framework._validate_field(field, "active")
        assert len(errors) == 0

    def test_validate_numeric_range(self, process_framework):
        """Test NUMERIC_RANGE validation"""
        field = FormField(
            id="hours",
            label="Hours",
            field_type="number",
            required=True,
            validations=[
                FieldValidation(
                    rule=ValidationRule.NUMERIC_RANGE,
                    value={"min": 0, "max": 100},
                    message="Must be between 0 and 100"
                )
            ]
        )

        # Below min
        errors = process_framework._validate_field(field, -5)
        assert len(errors) > 0

        # Above max
        errors = process_framework._validate_field(field, 150)
        assert len(errors) > 0

        # Valid
        errors = process_framework._validate_field(field, 50)
        assert len(errors) == 0


# =====================================================
# Test ProcessFramework - Process Completion
# =====================================================

class TestProcessFrameworkCompletion:
    """Test process completion"""

    def test_process_reaches_end(self, process_framework):
        """Test process reaches END step"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com"
        )

        # Execute first step
        process_framework.execute_step(
            instance_id=instance.instance_id,
            step_data={"scope": "Valid scope"},
            executed_by="test_user@example.com"
        )

        # Check if we can reach END (would need more steps in real process)
        updated_instance = process_framework.get_instance(instance.instance_id)
        assert updated_instance.current_step_id == "critical_functions"

    def test_complete_process(self, process_framework):
        """Test marking process as completed"""
        instance = process_framework.start_process(
            process_id="test_process_v1",
            started_by="test_user@example.com"
        )

        # Manually complete (would normally happen when reaching END)
        process_framework._complete_process(instance.instance_id)

        updated_instance = process_framework.get_instance(instance.instance_id)
        assert updated_instance.status == "completed"
        assert updated_instance.completed_at is not None


# =====================================================
# Test StepExecution
# =====================================================

class TestStepExecution:
    """Test StepExecution dataclass"""

    def test_step_execution_creation(self):
        """Test StepExecution creation"""
        execution = StepExecution(
            step_id="bia_initiation",
            executed_by="test_user@example.com",
            executed_at=datetime.now(),
            input_data={"scope": "Test"},
            output_data={"validated": True},
            result="success",
            duration_ms=150
        )

        assert execution.step_id == "bia_initiation"
        assert execution.result == "success"
        assert execution.duration_ms == 150

    def test_step_execution_with_ai(self):
        """Test StepExecution with AI involvement"""
        execution = StepExecution(
            step_id="impact_analysis",
            executed_by="AI_System",
            executed_at=datetime.now(),
            input_data={},
            output_data={"analysis": "Complete"},
            result="success",
            ai_agent_used="analytics_specialist",
            ai_confidence=0.95
        )

        assert execution.executed_by == "AI_System"
        assert execution.ai_agent_used == "analytics_specialist"
        assert execution.ai_confidence == 0.95

    def test_step_execution_failure(self):
        """Test StepExecution with failure"""
        execution = StepExecution(
            step_id="approval",
            executed_by="manager@example.com",
            executed_at=datetime.now(),
            input_data={},
            output_data={},
            result="failure",
            error_message="Insufficient permissions"
        )

        assert execution.result == "failure"
        assert execution.error_message == "Insufficient permissions"


# =====================================================
# Test ProcessInstance
# =====================================================

class TestProcessInstance:
    """Test ProcessInstance dataclass"""

    def test_process_instance_creation(self):
        """Test ProcessInstance creation"""
        instance = ProcessInstance(
            instance_id="test_process_v1-20251011120000",
            process_id="test_process_v1",
            status="active",
            current_step_id="bia_initiation",
            step_history=[],
            data={},
            started_by="test_user@example.com",
            started_at=datetime.now()
        )

        assert instance.status == "active"
        assert instance.current_step_id == "bia_initiation"

    def test_process_instance_with_participants(self):
        """Test ProcessInstance with multiple participants"""
        instance = ProcessInstance(
            instance_id="test_process_v1-20251011120000",
            process_id="test_process_v1",
            status="active",
            current_step_id="bia_initiation",
            step_history=[],
            data={},
            started_by="test_user@example.com",
            started_at=datetime.now(),
            participants=["user1@example.com", "user2@example.com"]
        )

        assert len(instance.participants) == 2

    def test_process_instance_completed(self):
        """Test completed ProcessInstance"""
        now = datetime.now()
        instance = ProcessInstance(
            instance_id="test_process_v1-20251011120000",
            process_id="test_process_v1",
            status="completed",
            current_step_id="END",
            step_history=[],
            data={},
            started_by="test_user@example.com",
            started_at=now,
            completed_at=now
        )

        assert instance.status == "completed"
        assert instance.completed_at is not None


# =====================================================
# Run Tests
# =====================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
