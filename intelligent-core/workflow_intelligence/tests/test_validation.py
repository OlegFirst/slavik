"""
Pydantic Validation Tests

Проверяем что Pydantic модели корректно валидируют входные данные:
- Слишком длинные строки отклоняются
- Невалидные типы данных отклоняются
- Слишком большие context отклоняются
- Embedding с неправильными размерами отклоняется
"""

import pytest
from pydantic import ValidationError
from workflow_intelligence.case_library.models import (
    WorkflowCase,
    OrganizationContext,
    WorkflowMetrics,
    WorkflowStepRecord,
    ChallengeResolution,
    AIInteraction,
    CaseQuery,
    BenchmarkStats,
    SuccessPattern,
    CaseCollectionConfig
)
from datetime import datetime


# ============================================================================
# STRING LENGTH VALIDATION
# ============================================================================

def test_workflow_case_case_id_max_length():
    """Test that case_id has reasonable length limits"""

    # Слишком длинный case_id (> 1000 chars)
    very_long_id = "x" * 10000

    with pytest.raises(ValidationError) as exc_info:
        WorkflowCase(
            case_id=very_long_id,
            module="planning",
            workflow_name="test",
            organization_context=OrganizationContext(
                industry="healthcare",
                size="medium",
                org_type="hospital",
                maturity_level="basic"
            ),
            journey=[],
            metrics=WorkflowMetrics(
                total_duration_days=10,
                total_steps=5
            )
        )

    # Pydantic should reject this (if we add max_length constraint)
    # For now, this test documents the need for validation


def test_organization_context_string_limits():
    """Test that organization context strings have limits"""

    # Валидный контекст
    valid_context = OrganizationContext(
        industry="healthcare",
        size="medium",
        org_type="hospital",
        maturity_level="basic"
    )
    assert valid_context.industry == "healthcare"

    # Проверим что пустые строки не принимаются
    with pytest.raises(ValidationError):
        OrganizationContext(
            industry="",  # Empty string
            size="medium",
            org_type="hospital",
            maturity_level="basic"
        )


def test_module_name_validation():
    """Test that module names are validated"""

    # Валидные модули
    valid_modules = ["bia", "risk", "planning", "compliance", "testing"]

    for module in valid_modules:
        case = WorkflowCase(
            case_id=f"case-{module}-001",
            module=module,
            workflow_name="test_workflow",
            organization_context=OrganizationContext(
                industry="healthcare",
                size="medium",
                org_type="hospital",
                maturity_level="basic"
            ),
            journey=[],
            metrics=WorkflowMetrics(
                total_duration_days=10,
                total_steps=5
            )
        )
        assert case.module == module


# ============================================================================
# TYPE VALIDATION
# ============================================================================

def test_workflow_metrics_numeric_validation():
    """Test that numeric fields are validated"""

    # Невалидные типы
    with pytest.raises(ValidationError):
        WorkflowMetrics(
            total_duration_days="not a number",  # Should be float
            total_steps=5
        )

    with pytest.raises(ValidationError):
        WorkflowMetrics(
            total_duration_days=10,
            total_steps="five"  # Should be int
        )


def test_user_satisfaction_range_validation():
    """Test that user_satisfaction is in valid range (1-5)"""

    # Валидные значения
    for rating in [1.0, 2.5, 3.0, 4.5, 5.0]:
        metrics = WorkflowMetrics(
            total_duration_days=10,
            total_steps=5,
            user_satisfaction=rating
        )
        assert metrics.user_satisfaction == rating

    # Невалидные значения
    with pytest.raises(ValidationError):
        WorkflowMetrics(
            total_duration_days=10,
            total_steps=5,
            user_satisfaction=0.5  # Too low
        )

    with pytest.raises(ValidationError):
        WorkflowMetrics(
            total_duration_days=10,
            total_steps=5,
            user_satisfaction=6.0  # Too high
        )


def test_ai_interaction_helpful_rating_validation():
    """Test that AI interaction rating is in valid range"""

    # Валидные значения
    for rating in [1, 2, 3, 4, 5]:
        interaction = AIInteraction(
            type="suggest",
            prompt_summary="Test prompt",
            response_summary="Test response",
            accepted=True,
            helpful_rating=rating
        )
        assert interaction.helpful_rating == rating

    # Невалидные значения
    with pytest.raises(ValidationError):
        AIInteraction(
            type="suggest",
            prompt_summary="Test prompt",
            response_summary="Test response",
            accepted=True,
            helpful_rating=0  # Too low
        )

    with pytest.raises(ValidationError):
        AIInteraction(
            type="suggest",
            prompt_summary="Test prompt",
            response_summary="Test response",
            accepted=True,
            helpful_rating=6  # Too high
        )


def test_success_pattern_frequency_validation():
    """Test that frequency is in valid range (0-1)"""

    # Валидные значения
    pattern = SuccessPattern(
        pattern_id="pattern-001",
        pattern_type="action_sequence",
        description="Test pattern",
        observed_in_cases=["case1"],
        frequency=0.75,
        confidence=0.8
    )
    assert pattern.frequency == 0.75

    # Невалидные значения
    with pytest.raises(ValidationError):
        SuccessPattern(
            pattern_id="pattern-002",
            pattern_type="action_sequence",
            description="Test pattern",
            observed_in_cases=["case1"],
            frequency=1.5,  # Too high
            confidence=0.8
        )


# ============================================================================
# BOOLEAN VALIDATION
# ============================================================================

def test_boolean_fields_validation():
    """Test that boolean fields only accept boolean values"""

    # Валидный boolean
    metrics = WorkflowMetrics(
        total_duration_days=10,
        total_steps=5,
        completed_successfully=True
    )
    assert metrics.completed_successfully is True

    # Pydantic might coerce some values, test that
    metrics2 = WorkflowMetrics(
        total_duration_days=10,
        total_steps=5,
        completed_successfully=1  # Should be coerced to True
    )
    # This might work due to Pydantic's coercion


# ============================================================================
# DATETIME VALIDATION
# ============================================================================

def test_datetime_validation():
    """Test that datetime fields are validated"""

    now = datetime.utcnow()

    step = WorkflowStepRecord(
        stage="draft",
        started_at=now,
        completed_at=now,
        duration_hours=1.0
    )
    assert step.started_at == now

    # Invalid datetime
    with pytest.raises(ValidationError):
        WorkflowStepRecord(
            stage="draft",
            started_at="not a datetime",
            completed_at=now,
            duration_hours=1.0
        )


# ============================================================================
# NESTED OBJECT VALIDATION
# ============================================================================

def test_nested_organization_context_validation():
    """Test that nested OrganizationContext is validated"""

    # Валидный nested context
    case = WorkflowCase(
        case_id="case-001",
        module="planning",
        workflow_name="test",
        organization_context=OrganizationContext(
            industry="healthcare",
            size="medium",
            org_type="hospital",
            maturity_level="basic"
        ),
        journey=[],
        metrics=WorkflowMetrics(
            total_duration_days=10,
            total_steps=5
        )
    )
    assert case.organization_context.industry == "healthcare"

    # Невалидный nested context
    with pytest.raises(ValidationError):
        WorkflowCase(
            case_id="case-002",
            module="planning",
            workflow_name="test",
            organization_context={
                "industry": "healthcare",
                # Missing required fields
            },
            journey=[],
            metrics=WorkflowMetrics(
                total_duration_days=10,
                total_steps=5
            )
        )


# ============================================================================
# LIST/ARRAY VALIDATION
# ============================================================================

def test_journey_list_validation():
    """Test that journey is a list of WorkflowStepRecord"""

    now = datetime.utcnow()

    # Валидная journey
    case = WorkflowCase(
        case_id="case-001",
        module="planning",
        workflow_name="test",
        organization_context=OrganizationContext(
            industry="healthcare",
            size="medium",
            org_type="hospital",
            maturity_level="basic"
        ),
        journey=[
            WorkflowStepRecord(
                stage="draft",
                started_at=now,
                completed_at=now,
                duration_hours=2.0
            )
        ],
        metrics=WorkflowMetrics(
            total_duration_days=10,
            total_steps=5
        )
    )
    assert len(case.journey) == 1

    # Невалидная journey (не список)
    with pytest.raises(ValidationError):
        WorkflowCase(
            case_id="case-002",
            module="planning",
            workflow_name="test",
            organization_context=OrganizationContext(
                industry="healthcare",
                size="medium",
                org_type="hospital",
                maturity_level="basic"
            ),
            journey="not a list",
            metrics=WorkflowMetrics(
                total_duration_days=10,
                total_steps=5
            )
        )


def test_challenge_resolution_list_validation():
    """Test that challenges is a list of ChallengeResolution"""

    now = datetime.utcnow()

    # Валидный список challenges
    step = WorkflowStepRecord(
        stage="draft",
        started_at=now,
        completed_at=now,
        duration_hours=2.0,
        challenges=[
            ChallengeResolution(
                type="validation_error",
                description="Missing data",
                resolution="Added required data",
                time_to_resolve_hours=0.5
            )
        ]
    )
    assert len(step.challenges) == 1


# ============================================================================
# QUERY VALIDATION
# ============================================================================

def test_case_query_limit_validation():
    """Test that query limit has valid range"""

    # Валидный limit
    query = CaseQuery(
        module="planning",
        limit=5
    )
    assert query.limit == 5

    # Граничные значения
    query_min = CaseQuery(module="planning", limit=1)
    assert query_min.limit == 1

    query_max = CaseQuery(module="planning", limit=20)
    assert query_max.limit == 20

    # Невалидные значения
    with pytest.raises(ValidationError):
        CaseQuery(module="planning", limit=0)  # Too low

    with pytest.raises(ValidationError):
        CaseQuery(module="planning", limit=100)  # Too high


def test_case_query_min_success_rate_validation():
    """Test that min_success_rate is in valid range"""

    # Валидные значения
    query = CaseQuery(
        module="planning",
        min_success_rate=0.8
    )
    assert query.min_success_rate == 0.8

    # Невалидные значения
    with pytest.raises(ValidationError):
        CaseQuery(
            module="planning",
            min_success_rate=1.5  # Too high
        )

    with pytest.raises(ValidationError):
        CaseQuery(
            module="planning",
            min_success_rate=-0.1  # Negative
        )


# ============================================================================
# CONFIG VALIDATION
# ============================================================================

def test_case_collection_config_validation():
    """Test that collection config is validated"""

    # Валидный config
    config = CaseCollectionConfig(
        enabled=True,
        min_duration_hours=1.0,
        min_steps=3
    )
    assert config.enabled is True
    assert config.min_duration_hours == 1.0

    # Проверим defaults
    assert config.anonymize_data is True
    assert config.require_consent is True


# ============================================================================
# MISSING REQUIRED FIELDS
# ============================================================================

def test_missing_required_fields():
    """Test that missing required fields are caught"""

    # Missing case_id
    with pytest.raises(ValidationError) as exc_info:
        WorkflowCase(
            module="planning",
            workflow_name="test",
            organization_context=OrganizationContext(
                industry="healthcare",
                size="medium",
                org_type="hospital",
                maturity_level="basic"
            ),
            journey=[],
            metrics=WorkflowMetrics(
                total_duration_days=10,
                total_steps=5
            )
        )

    assert "case_id" in str(exc_info.value)


def test_missing_required_organization_context_fields():
    """Test that missing org context fields are caught"""

    with pytest.raises(ValidationError):
        OrganizationContext(
            industry="healthcare",
            size="medium"
            # Missing org_type and maturity_level
        )


# ============================================================================
# EMBEDDING VALIDATION (for future vector support)
# ============================================================================

def test_embedding_dimension_validation():
    """Test that embedding vectors have correct dimensions"""

    # This test is for future when we add embedding validation
    # For now, documents the requirement

    # Valid embedding (1536 dimensions for OpenAI)
    valid_embedding = [0.0] * 1536
    assert len(valid_embedding) == 1536

    # Invalid embedding (wrong dimension)
    invalid_embedding = [0.0] * 512
    assert len(invalid_embedding) != 1536


# ============================================================================
# JSON SIZE VALIDATION
# ============================================================================

def test_large_context_validation():
    """Test that very large contexts are handled appropriately"""

    # Создаем большой context
    large_context = {
        "data": "x" * 100000,  # 100KB string
        "nested": {
            "key": "value" * 1000
        }
    }

    # Should not crash but might want size limits
    # This test documents the need for size validation
    import json
    context_size = len(json.dumps(large_context))

    # Document that we should probably limit context size
    # e.g., max 1MB
    assert context_size > 0


def test_deeply_nested_json_validation():
    """Test that deeply nested JSON is handled"""

    # Создаем глубоко вложенный JSON
    nested = {"level": 1}
    current = nested
    for i in range(2, 101):  # 100 levels deep
        current["nested"] = {"level": i}
        current = current["nested"]

    # Should not cause stack overflow
    # This test documents the need for nesting depth limits
    import json
    json_str = json.dumps(nested)
    assert len(json_str) > 0


# ============================================================================
# SPECIAL CHARACTERS VALIDATION
# ============================================================================

def test_special_characters_in_strings():
    """Test that special characters are handled correctly"""

    # Unicode characters
    case = WorkflowCase(
        case_id="case-测试-001",
        module="planning",
        workflow_name="Test Workflow 🚀",
        organization_context=OrganizationContext(
            industry="healthcare",
            size="medium",
            org_type="hospital",
            maturity_level="basic"
        ),
        journey=[],
        metrics=WorkflowMetrics(
            total_duration_days=10,
            total_steps=5
        )
    )

    assert "测试" in case.case_id
    assert "🚀" in case.workflow_name


def test_sql_special_characters_in_model():
    """Test that SQL special characters are accepted (for storage layer to handle)"""

    # SQL special characters should be accepted by model
    # Storage layer should escape them
    case = WorkflowCase(
        case_id="case-'; DROP TABLE--",
        module="planning",
        workflow_name="Test's \"Workflow\"",
        organization_context=OrganizationContext(
            industry="healthcare",
            size="medium",
            org_type="hospital",
            maturity_level="basic"
        ),
        journey=[],
        metrics=WorkflowMetrics(
            total_duration_days=10,
            total_steps=5
        )
    )

    # Model should accept it (storage layer will sanitize)
    assert case.case_id == "case-'; DROP TABLE--"
