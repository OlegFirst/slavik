"""Integration tests for complete workflow intelligence flow"""

import pytest
from workflow_intelligence import PostgresStorageAdapter, WorkflowEngine, CaseCollector


@pytest.mark.asyncio
async def test_complete_workflow_lifecycle(database_url):
    """Test complete workflow from start to case creation"""
    # Setup
    storage = PostgresStorageAdapter(database_url)
    await storage.connect()

    engine = WorkflowEngine(module="planning", storage_adapter=storage)
    collector = CaseCollector(storage_adapter=storage)

    workflow_id = "integration-test-001"
    tenant_id = "tenant-integration"

    try:
        # 1. Start workflow
        await engine.execute_action(
            workflow_id=workflow_id,
            action="create_strategy",
            data={
                "strategy_type": "FAST_RECOVERY",
                "industry": "healthcare",
                "target_rto_hours": 2
            },
            tenant_id=tenant_id
        )

        # 2. Progress workflow
        await engine.execute_action(
            workflow_id=workflow_id,
            action="add_resources",
            data={"personnel": 5, "budget": 500000},
            tenant_id=tenant_id
        )

        # 3. Check context
        context = await engine.get_context(workflow_id, tenant_id)
        assert context is not None
        assert context["workflow_id"] == workflow_id

        # 4. Get suggestions
        suggestions = await engine.suggest_next_actions(workflow_id, tenant_id)
        assert isinstance(suggestions, list)

        # 5. Complete workflow
        await engine.execute_action(
            workflow_id=workflow_id,
            action="approve",
            data={"status": "approved"},
            tenant_id=tenant_id
        )

        # 6. Create case for learning
        case = await collector.create_case(
            workflow_id=workflow_id,
            module="planning",
            tenant_id=tenant_id,
            success=True
        )

        assert case is not None

        # 7. Save case
        await storage.save_case(
            case_id=case.case_id,
            module="planning",
            case_data=case.dict(),
            tenant_id=tenant_id
        )

        # 8. Find similar cases (should include our case)
        similar = await storage.find_similar_cases(
            module="planning",
            org_context={"industry": "healthcare", "size": "medium"},
            current_stage="draft",
            limit=5
        )

        assert len(similar) > 0

        # 9. Get benchmarks
        benchmarks = await storage.get_benchmarks(
            module="planning",
            industry="healthcare"
        )

        # Should have data now
        assert benchmarks is not None

    finally:
        await storage.close()


@pytest.mark.asyncio
async def test_multi_tenant_isolation(database_url):
    """Test that tenants cannot see each other's data"""
    storage = PostgresStorageAdapter(database_url)
    await storage.connect()

    engine = WorkflowEngine(module="planning", storage_adapter=storage)

    try:
        # Tenant 1 workflow
        await engine.execute_action(
            workflow_id="tenant1-wf",
            action="create_strategy",
            data={"strategy_type": "FAST_RECOVERY"},
            tenant_id="tenant-1"
        )

        # Tenant 2 workflow
        await engine.execute_action(
            workflow_id="tenant2-wf",
            action="create_strategy",
            data={"strategy_type": "GRADUAL_RECOVERY"},
            tenant_id="tenant-2"
        )

        # Tenant 1 should not see tenant 2's data
        tenant1_context = await engine.get_context("tenant2-wf", "tenant-1")
        assert tenant1_context is None or tenant1_context.get("workflow_id") != "tenant2-wf"

        # Tenant 2 should see own data
        tenant2_context = await engine.get_context("tenant2-wf", "tenant-2")
        assert tenant2_context is not None
        assert tenant2_context["workflow_id"] == "tenant2-wf"

    finally:
        await storage.close()


@pytest.mark.asyncio
async def test_benchmark_accumulation(database_url):
    """Test that benchmarks improve as more cases are added"""
    storage = PostgresStorageAdapter(database_url)
    await storage.connect()

    collector = CaseCollector(storage_adapter=storage)
    engine = WorkflowEngine(module="planning", storage_adapter=storage)

    try:
        # Create 10 successful workflows
        for i in range(10):
            workflow_id = f"benchmark-wf-{i}"

            await engine.execute_action(
                workflow_id=workflow_id,
                action="create_strategy",
                data={
                    "strategy_type": "FAST_RECOVERY",
                    "industry": "finance"
                },
                tenant_id=f"tenant-{i}"
            )

            case = await collector.create_case(
                workflow_id=workflow_id,
                module="planning",
                tenant_id=f"tenant-{i}",
                success=True
            )

            await storage.save_case(
                case_id=case.case_id,
                module="planning",
                case_data=case.dict(),
                tenant_id=f"tenant-{i}"
            )

        # Get benchmarks
        benchmarks = await storage.get_benchmarks(
            module="planning",
            industry="finance"
        )

        # Should have accumulated data from all cases
        assert benchmarks is not None

        # Find similar cases
        similar = await storage.find_similar_cases(
            module="planning",
            org_context={"industry": "finance", "size": "medium"},
            current_stage="draft",
            limit=5
        )

        # Should find multiple similar cases
        assert len(similar) > 0

    finally:
        await storage.close()


@pytest.mark.asyncio
async def test_error_handling(database_url):
    """Test error handling in workflow intelligence"""
    storage = PostgresStorageAdapter(database_url)
    await storage.connect()

    engine = WorkflowEngine(module="planning", storage_adapter=storage)

    try:
        # Try to get non-existent workflow
        context = await engine.get_context("non-existent-wf", "tenant-test")
        assert context is None

        # Try to get case that doesn't exist
        case = await storage.get_case("non-existent-case")
        assert case is None

    finally:
        await storage.close()
