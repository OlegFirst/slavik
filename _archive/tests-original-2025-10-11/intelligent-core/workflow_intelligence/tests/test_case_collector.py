"""Tests for CaseCollector"""

import pytest
from workflow_intelligence.case_collector import CaseCollector
from workflow_intelligence.workflow_engine import WorkflowEngine


@pytest.mark.asyncio
async def test_case_collector_initialization(storage):
    """Test CaseCollector initialization"""
    collector = CaseCollector(storage_adapter=storage)

    assert collector.storage_adapter == storage


@pytest.mark.asyncio
async def test_create_case_from_workflow(storage):
    """Test creating a case from completed workflow"""
    engine = WorkflowEngine(module="planning", storage_adapter=storage)
    collector = CaseCollector(storage_adapter=storage)

    workflow_id = "completed-workflow-001"
    tenant_id = "tenant-test"

    # Create workflow with multiple actions
    await engine.execute_action(
        workflow_id=workflow_id,
        action="create_strategy",
        data={"strategy_type": "FAST_RECOVERY", "target_rto_hours": 2},
        tenant_id=tenant_id
    )

    await engine.execute_action(
        workflow_id=workflow_id,
        action="submit_review",
        data={"reviewer": "user-123"},
        tenant_id=tenant_id
    )

    await engine.execute_action(
        workflow_id=workflow_id,
        action="approve",
        data={"approver": "manager-456"},
        tenant_id=tenant_id
    )

    # Create case
    case = await collector.create_case(
        workflow_id=workflow_id,
        module="planning",
        tenant_id=tenant_id
    )

    assert case is not None
    assert case.workflow_id == workflow_id
    assert case.module == "planning"
    assert case.case_id is not None


@pytest.mark.asyncio
async def test_case_anonymization(storage):
    """Test that cases are properly anonymized"""
    collector = CaseCollector(storage_adapter=storage)
    engine = WorkflowEngine(module="planning", storage_adapter=storage)

    workflow_id = "sensitive-workflow-001"
    tenant_id = "acme-corp"

    # Create workflow with sensitive data
    await engine.execute_action(
        workflow_id=workflow_id,
        action="create_strategy",
        data={
            "organization_name": "ACME Corporation",  # Should be removed
            "contact_email": "john@acme.com",  # Should be removed
            "strategy_type": "FAST_RECOVERY",  # Should be kept
            "industry": "healthcare",  # Should be kept
            "estimated_cost": 500000  # Should be removed/anonymized
        },
        tenant_id=tenant_id
    )

    # Create case
    case = await collector.create_case(
        workflow_id=workflow_id,
        module="planning",
        tenant_id=tenant_id
    )

    case_dict = case.dict()

    # Sensitive data should be removed
    assert "organization_name" not in str(case_dict)
    assert "contact_email" not in str(case_dict)
    assert "acme" not in str(case_dict).lower()

    # Pattern data should be kept
    assert case_dict.get("industry") == "healthcare"


@pytest.mark.asyncio
async def test_case_with_success_outcome(storage):
    """Test case creation with success outcome"""
    collector = CaseCollector(storage_adapter=storage)
    engine = WorkflowEngine(module="planning", storage_adapter=storage)

    workflow_id = "successful-workflow-001"
    tenant_id = "tenant-test"

    await engine.execute_action(
        workflow_id=workflow_id,
        action="create_strategy",
        data={"strategy_type": "FAST_RECOVERY"},
        tenant_id=tenant_id
    )

    await engine.execute_action(
        workflow_id=workflow_id,
        action="approve",
        data={"status": "approved", "outcome": "success"},
        tenant_id=tenant_id
    )

    case = await collector.create_case(
        workflow_id=workflow_id,
        module="planning",
        tenant_id=tenant_id,
        success=True
    )

    assert case.success is True


@pytest.mark.asyncio
async def test_case_with_challenges_and_best_practices(storage):
    """Test case with challenges and best practices"""
    collector = CaseCollector(storage_adapter=storage)
    engine = WorkflowEngine(module="planning", storage_adapter=storage)

    workflow_id = "learning-workflow-001"
    tenant_id = "tenant-test"

    await engine.execute_action(
        workflow_id=workflow_id,
        action="create_strategy",
        data={"strategy_type": "FAST_RECOVERY"},
        tenant_id=tenant_id
    )

    case = await collector.create_case(
        workflow_id=workflow_id,
        module="planning",
        tenant_id=tenant_id,
        success=True,
        challenges=["budget_constraints", "timeline_pressure"],
        best_practices=["early_stakeholder_engagement", "iterative_reviews"]
    )

    assert len(case.challenges) == 2
    assert len(case.best_practices) == 2
    assert "budget_constraints" in case.challenges
    assert "early_stakeholder_engagement" in case.best_practices


@pytest.mark.asyncio
async def test_cross_module_learning(storage):
    """Test that cases from one module can help another"""
    planning_engine = WorkflowEngine(module="planning", storage_adapter=storage)
    bia_engine = WorkflowEngine(module="bia", storage_adapter=storage)
    collector = CaseCollector(storage_adapter=storage)

    # Create planning case
    await planning_engine.execute_action(
        workflow_id="planning-wf-001",
        action="create_strategy",
        data={"strategy_type": "FAST_RECOVERY", "industry": "healthcare"},
        tenant_id="tenant-test"
    )

    planning_case = await collector.create_case(
        workflow_id="planning-wf-001",
        module="planning",
        tenant_id="tenant-test",
        success=True
    )

    # Save case
    await storage.save_case(
        case_id=planning_case.case_id,
        module="planning",
        case_data=planning_case.dict(),
        tenant_id="tenant-test"
    )

    # BIA module should be able to find this case
    similar_cases = await storage.find_similar_cases(
        module="planning",
        org_context={"industry": "healthcare", "size": "medium"},
        current_stage="draft",
        limit=5
    )

    # Should find the planning case
    assert len(similar_cases) > 0
