"""
🧪 ТЕСТЫ - Case Library

Тестирование сбора cases, поиска и benchmarking
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from case_library.models import (
    WorkflowCase,
    OrganizationContext,
    WorkflowMetrics,
    WorkflowStepRecord,
    ChallengeResolution,
    AIInteraction,
    CaseQuery,
    extract_features_for_ml
)

from case_library.collector import CaseCollector
from core.workflow_engine import WorkflowEngine, InMemoryStorageAdapter


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def org_context():
    """Organization context fixture"""
    return OrganizationContext(
        industry="healthcare",
        size="medium",
        org_type="hospital",
        maturity_level="basic"
    )


@pytest.fixture
def workflow_metrics():
    """Workflow metrics fixture"""
    return WorkflowMetrics(
        total_duration_days=14,
        total_steps=8,
        processes_identified=12,
        critical_processes=4,
        ai_recommendations_used=15,
        ai_recommendations_rejected=3,
        user_satisfaction=4.5,
        completed_successfully=True,
        certification_ready=True
    )


@pytest.fixture
def workflow_step():
    """Workflow step fixture"""
    return WorkflowStepRecord(
        stage="identify_processes",
        started_at=datetime.utcnow() - timedelta(hours=10),
        completed_at=datetime.utcnow() - timedelta(hours=2),
        duration_hours=8.0,
        actions_taken=[
            {"action": "add_process", "data": {"name": "Emergency Dept"}},
            {"action": "add_process", "data": {"name": "Patient Records"}}
        ],
        challenges=[
            ChallengeResolution(
                type="insufficient_data",
                description="Only 2 processes initially identified",
                resolution="AI suggested 10 typical healthcare processes",
                time_to_resolve_hours=2.0,
                ai_assisted=True
            )
        ],
        ai_interactions=[
            AIInteraction(
                type="suggest",
                prompt_summary="Suggest processes for healthcare",
                response_summary="10 typical processes suggested",
                accepted=True,
                helpful_rating=5
            )
        ]
    )


@pytest.fixture
def workflow_case(org_context, workflow_metrics, workflow_step):
    """Complete workflow case fixture"""
    return WorkflowCase(
        case_id="case-test-001",
        module="bia",
        workflow_name="bia_process",
        organization_context=org_context,
        journey=[workflow_step],
        metrics=workflow_metrics,
        success_patterns=[
            "Used AI early - saved 2 days",
            "Involved process owners"
        ],
        lessons_learned=[
            "Start with critical processes first"
        ],
        best_practices=[
            "Used industry templates"
        ]
    )


# ============================================================================
# TESTS: Case Models
# ============================================================================

def test_organization_context_creation(org_context):
    """Тест: Создание organization context"""
    assert org_context.industry == "healthcare"
    assert org_context.size == "medium"
    assert org_context.maturity_level == "basic"


def test_workflow_metrics_creation(workflow_metrics):
    """Тест: Создание workflow metrics"""
    assert workflow_metrics.total_duration_days == 14
    assert workflow_metrics.processes_identified == 12
    assert workflow_metrics.completed_successfully is True


def test_workflow_metrics_ai_acceptance_rate(workflow_metrics):
    """Тест: Расчёт AI acceptance rate"""
    # 15 used, 3 rejected = 15/18 = 0.833...
    assert workflow_metrics.ai_acceptance_rate > 0.83
    assert workflow_metrics.ai_acceptance_rate < 0.84


def test_workflow_step_ai_assistance_level(workflow_step):
    """Тест: Уровень AI помощи"""
    # 1 AI interaction accepted -> "low"
    assert workflow_step.ai_assistance_level == "low"


def test_workflow_step_ai_assistance_level_high():
    """Тест: Высокий уровень AI помощи"""
    step = WorkflowStepRecord(
        stage="test",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_hours=1.0,
        ai_interactions=[
            AIInteraction(
                type="suggest",
                prompt_summary="test",
                response_summary="test",
                accepted=True
            )
            for _ in range(10)  # 10 interactions -> "high"
        ]
    )

    assert step.ai_assistance_level == "high"


def test_workflow_case_creation(workflow_case):
    """Тест: Создание полного case"""
    assert workflow_case.case_id == "case-test-001"
    assert workflow_case.module == "bia"
    assert len(workflow_case.journey) == 1
    assert len(workflow_case.success_patterns) == 2
    assert workflow_case.anonymized is True


def test_case_features_extraction(workflow_case):
    """Тест: Извлечение features для ML"""
    features = extract_features_for_ml(workflow_case)

    assert features["industry"] == "healthcare"
    assert features["size"] == "medium"
    assert features["maturity_level"] == "basic"
    assert features["total_steps"] == 1
    assert features["success"] is True
    assert features["duration_days"] == 14
    assert features["processes_identified"] == 12


# ============================================================================
# TESTS: Case Collector
# ============================================================================

class MockWorkflowEngine:
    """Mock workflow engine для тестов"""

    def __init__(self):
        self.module = "bia"
        self.event_bus = MockEventBus()
        self.storage = InMemoryStorageAdapter()

    async def get_context(self, workflow_id):
        """Mock context"""
        from core.workflow_engine import WorkflowContext

        return WorkflowContext(
            workflow_id=workflow_id,
            module="bia",
            current_stage="completed",
            current_stage_label="Completed",
            progress_percentage=100.0,
            started_at=datetime.utcnow() - timedelta(days=14),
            updated_at=datetime.utcnow(),
            workflow_data={
                "organization_id": "org-123",
                "industry": "healthcare",
                "org_size": "medium",
                "maturity_level": "basic",
                "processes": [
                    {"name": "Emergency Dept", "tier": 1},
                    {"name": "Patient Records", "tier": 1},
                    {"name": "Lab Services", "tier": 2}
                ]
            },
            completed_steps=[
                {
                    "action": "create",
                    "from_state": "initial",
                    "to_state": "draft",
                    "timestamp": (datetime.utcnow() - timedelta(days=14)).isoformat(),
                    "data": {}
                },
                {
                    "action": "suggest_rto",
                    "from_state": "draft",
                    "to_state": "rto_suggested",
                    "timestamp": (datetime.utcnow() - timedelta(days=10)).isoformat(),
                    "data": {}
                }
            ]
        )


class MockEventBus:
    """Mock event bus"""

    def subscribe(self, pattern, handler):
        pass


class MockCaseRepository:
    """Mock case repository"""

    def __init__(self):
        self.cases = []

    async def save(self, case):
        self.cases.append(case)
        return case


@pytest.fixture
def case_collector():
    """Case collector fixture"""
    workflow_engine = MockWorkflowEngine()
    repository = MockCaseRepository()

    return CaseCollector(
        workflow_engine=workflow_engine,
        case_repository=repository
    )


@pytest.mark.asyncio
async def test_case_collector_create_case(case_collector):
    """Тест: Создание case из workflow"""

    workflow_id = "test-workflow-001"

    case = await case_collector.create_case(workflow_id)

    assert case is not None
    assert case.module == "bia"
    assert case.organization_context.industry == "healthcare"
    assert len(case.journey) > 0


@pytest.mark.asyncio
async def test_case_collector_quality_filters(case_collector):
    """Тест: Фильтры качества"""

    # Mock workflow with insufficient steps
    case_collector.workflow_engine.get_context = async def _(workflow_id):
        from core.workflow_engine import WorkflowContext
        return WorkflowContext(
            workflow_id=workflow_id,
            module="bia",
            current_stage="draft",
            current_stage_label="Draft",
            progress_percentage=10.0,
            started_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            workflow_data={},
            completed_steps=[]  # Not enough steps
        )

    case = await case_collector.create_case("test-002")

    # Should be None because doesn't pass quality filters
    assert case is None


# ============================================================================
# TESTS: Case Query
# ============================================================================

def test_case_query_creation():
    """Тест: Создание case query"""
    query = CaseQuery(
        module="bia",
        industry="healthcare",
        org_size="medium",
        current_stage="identify_processes",
        min_success_rate=0.8,
        limit=5
    )

    assert query.module == "bia"
    assert query.industry == "healthcare"
    assert query.limit == 5
    assert query.sort_by == "similarity"


def test_case_query_defaults():
    """Тест: Дефолтные значения query"""
    query = CaseQuery(module="bia")

    assert query.sort_by == "similarity"
    assert query.limit == 5
    assert query.industry is None


# ============================================================================
# TESTS: Case Patterns
# ============================================================================

def test_success_pattern_extraction(workflow_case):
    """Тест: Success patterns в case"""
    assert len(workflow_case.success_patterns) > 0
    assert "Used AI early" in workflow_case.success_patterns[0]


def test_lessons_learned_extraction(workflow_case):
    """Тест: Lessons learned в case"""
    assert len(workflow_case.lessons_learned) > 0
    assert "critical processes" in workflow_case.lessons_learned[0]


# ============================================================================
# TESTS: Benchmark Stats
# ============================================================================

def test_benchmark_stats_creation():
    """Тест: Создание benchmark stats"""
    from case_library.models import BenchmarkStats

    stats = BenchmarkStats(
        module="bia",
        industry="healthcare",
        total_cases=45,
        avg_duration_days=18.5,
        median_duration_days=16.0,
        p95_duration_days=25.0,
        success_rate=0.87,
        avg_user_satisfaction=4.2,
        avg_ai_usage=12.0,
        ai_acceptance_rate=0.78,
        common_challenges=[
            {"type": "data_quality", "frequency": 0.6}
        ],
        best_practices=[
            "Start with critical processes",
            "Use AI early"
        ]
    )

    assert stats.total_cases == 45
    assert stats.success_rate == 0.87
    assert len(stats.best_practices) == 2


# ============================================================================
# TESTS: Data Validation
# ============================================================================

def test_workflow_case_validation():
    """Тест: Валидация workflow case"""

    # Valid case
    case = WorkflowCase(
        case_id="valid-001",
        module="bia",
        workflow_name="bia_process",
        organization_context=OrganizationContext(
            industry="tech",
            size="small",
            org_type="startup",
            maturity_level="none"
        ),
        journey=[],
        metrics=WorkflowMetrics(
            total_duration_days=7,
            total_steps=5,
            completed_successfully=True
        )
    )

    assert case.case_id == "valid-001"


def test_metrics_validation_ai_acceptance():
    """Тест: Валидация AI acceptance rate"""

    metrics = WorkflowMetrics(
        total_duration_days=10,
        total_steps=5,
        ai_recommendations_used=10,
        ai_recommendations_rejected=0
    )

    assert metrics.ai_acceptance_rate == 1.0  # 100%

    metrics2 = WorkflowMetrics(
        total_duration_days=10,
        total_steps=5,
        ai_recommendations_used=0,
        ai_recommendations_rejected=0
    )

    assert metrics2.ai_acceptance_rate == 0.0  # No recommendations


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
