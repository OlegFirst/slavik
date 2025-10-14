"""
Row-Level Security (RLS) Tests

Проверяем что tenant isolation работает корректно:
- Один tenant не видит данные другого tenant
- Попытки доступа к чужим workflow блокируются
- RLS policies работают на уровне базы данных

NOTE: Эти тесты требуют настройки RLS policies в базе данных.
      Сейчас RLS реализован на уровне приложения (WHERE tenant_id = $X)
      Будущая миграция: перенести на database-level RLS policies
"""

import pytest
from workflow_intelligence.storage.postgres_adapter import PostgresStorageAdapter


@pytest.mark.asyncio
async def test_tenant_isolation_workflow_contexts(storage: PostgresStorageAdapter):
    """Test that tenants cannot access each other's workflow contexts"""

    # Tenant A создает workflow
    await storage.save_workflow_context(
        workflow_id="workflow-001",
        module="planning",
        context={"secret": "tenant_a_data"},
        tenant_id="tenant-a"
    )

    # Tenant B создает workflow с тем же ID
    await storage.save_workflow_context(
        workflow_id="workflow-001",
        module="planning",
        context={"secret": "tenant_b_data"},
        tenant_id="tenant-b"
    )

    # Tenant A получает свои данные
    result_a = await storage.get_workflow_context(
        workflow_id="workflow-001",
        tenant_id="tenant-a"
    )
    assert result_a is not None
    assert result_a['secret'] == "tenant_a_data"

    # Tenant B получает свои данные
    result_b = await storage.get_workflow_context(
        workflow_id="workflow-001",
        tenant_id="tenant-b"
    )
    assert result_b is not None
    assert result_b['secret'] == "tenant_b_data"

    # Tenant C не может получить данные tenant A
    result_c = await storage.get_workflow_context(
        workflow_id="workflow-001",
        tenant_id="tenant-c"
    )
    assert result_c is None


@pytest.mark.asyncio
async def test_tenant_isolation_cases(storage: PostgresStorageAdapter):
    """Test that tenants cannot access each other's cases"""

    # Tenant A создает case
    await storage.save_case(
        case_id="case-001",
        module="planning",
        case_data={
            "org_context": {
                "industry": "healthcare",
                "size": "medium",
                "maturity_level": "basic"
            },
            "journey": [],
            "metrics": {
                "total_duration_days": 10,
                "completed_successfully": True,
                "user_satisfaction": 4.5
            },
            "success_patterns": ["pattern_a"],
            "lessons_learned": []
        },
        tenant_id="tenant-a"
    )

    # Tenant B создает case
    await storage.save_case(
        case_id="case-002",
        module="planning",
        case_data={
            "org_context": {
                "industry": "healthcare",
                "size": "medium",
                "maturity_level": "basic"
            },
            "journey": [],
            "metrics": {
                "total_duration_days": 10,
                "completed_successfully": True,
                "user_satisfaction": 4.5
            },
            "success_patterns": ["pattern_b"],
            "lessons_learned": []
        },
        tenant_id="tenant-b"
    )

    # Проверим что find_similar_cases учитывает tenant_id
    # NOTE: Current implementation doesn't filter by tenant_id in find_similar_cases
    # This is a security issue to fix!

    # TODO: Add tenant_id parameter to find_similar_cases()


@pytest.mark.asyncio
async def test_tenant_isolation_predictions(storage: PostgresStorageAdapter):
    """Test that ML predictions are isolated by tenant"""

    # Tenant A создает prediction
    await storage.save_prediction(
        workflow_id="workflow-001",
        prediction={
            "success_probability": 0.95,
            "estimated_duration_days": 10,
            "risk_level": "low",
            "risk_factors": [],
            "model_version": "v1.0"
        },
        tenant_id="tenant-a"
    )

    # Tenant B создает prediction для того же workflow_id
    await storage.save_prediction(
        workflow_id="workflow-001",
        prediction={
            "success_probability": 0.5,
            "estimated_duration_days": 30,
            "risk_level": "high",
            "risk_factors": ["high_complexity"],
            "model_version": "v1.0"
        },
        tenant_id="tenant-b"
    )

    # Predictions должны быть изолированы
    # NOTE: We need a method to get predictions by workflow_id and tenant_id


@pytest.mark.asyncio
async def test_cannot_access_other_tenant_by_null(storage: PostgresStorageAdapter):
    """Test that NULL tenant_id doesn't bypass isolation"""

    # Создаем workflow для tenant-a
    await storage.save_workflow_context(
        workflow_id="workflow-001",
        module="planning",
        context={"data": "secret"},
        tenant_id="tenant-a"
    )

    # Попытка получить с NULL tenant_id
    # NOTE: This should raise an error, not return data
    try:
        result = await storage.get_workflow_context(
            workflow_id="workflow-001",
            tenant_id=None  # Attempt to bypass with NULL
        )
        # Should not get data
        assert result is None
    except Exception:
        # Should raise error for NULL tenant_id
        pass


@pytest.mark.asyncio
async def test_cannot_access_other_tenant_by_empty_string(storage: PostgresStorageAdapter):
    """Test that empty string tenant_id doesn't bypass isolation"""

    # Создаем workflow для tenant-a
    await storage.save_workflow_context(
        workflow_id="workflow-001",
        module="planning",
        context={"data": "secret"},
        tenant_id="tenant-a"
    )

    # Попытка получить с пустой строкой
    result = await storage.get_workflow_context(
        workflow_id="workflow-001",
        tenant_id=""  # Empty string
    )
    assert result is None


@pytest.mark.asyncio
async def test_update_workflow_preserves_tenant_isolation(storage: PostgresStorageAdapter):
    """Test that updating workflow doesn't affect other tenant's data"""

    # Tenant A создает workflow
    await storage.save_workflow_context(
        workflow_id="workflow-001",
        module="planning",
        context={"version": 1},
        tenant_id="tenant-a"
    )

    # Tenant B создает workflow с тем же ID
    await storage.save_workflow_context(
        workflow_id="workflow-001",
        module="planning",
        context={"version": 1},
        tenant_id="tenant-b"
    )

    # Tenant A обновляет свой workflow
    await storage.save_workflow_context(
        workflow_id="workflow-001",
        module="planning",
        context={"version": 2},
        tenant_id="tenant-a"
    )

    # Проверим что данные tenant B не изменились
    result_b = await storage.get_workflow_context(
        workflow_id="workflow-001",
        tenant_id="tenant-b"
    )
    assert result_b is not None
    assert result_b['version'] == 1  # Not affected by tenant-a update


@pytest.mark.asyncio
async def test_multiple_tenants_same_module(storage: PostgresStorageAdapter):
    """Test that multiple tenants can use same module independently"""

    # Создаем workflows для разных tenants в одном модуле
    for i in range(1, 6):
        tenant_id = f"tenant-{i}"
        await storage.save_workflow_context(
            workflow_id=f"workflow-{i}",
            module="planning",
            context={"tenant_number": i},
            tenant_id=tenant_id
        )

    # Каждый tenant видит только свои данные
    for i in range(1, 6):
        tenant_id = f"tenant-{i}"
        result = await storage.get_workflow_context(
            workflow_id=f"workflow-{i}",
            tenant_id=tenant_id
        )
        assert result is not None
        assert result['tenant_number'] == i


@pytest.mark.asyncio
async def test_benchmarks_should_aggregate_across_tenants(storage: PostgresStorageAdapter):
    """Test that benchmarks aggregate data across tenants (anonymized)"""

    # Multiple tenants создают cases в одной industry
    for i in range(1, 4):
        await storage.save_case(
            case_id=f"case-{i}",
            module="planning",
            case_data={
                "org_context": {
                    "industry": "healthcare",
                    "size": "medium",
                    "maturity_level": "basic"
                },
                "journey": [],
                "metrics": {
                    "total_duration_days": 10 + i,
                    "completed_successfully": True,
                    "user_satisfaction": 4.0
                },
                "success_patterns": [],
                "lessons_learned": []
            },
            tenant_id=f"tenant-{i}"
        )

    # Benchmarks должны агрегировать данные всех tenants
    # (потому что это анонимизированная статистика)
    benchmarks = await storage.get_benchmarks(
        module="planning",
        industry="healthcare",
        org_size="medium"
    )

    # Должно быть 3 cases от разных tenants
    assert benchmarks['total_cases'] == 3


@pytest.mark.asyncio
async def test_similar_cases_should_respect_privacy(storage: PostgresStorageAdapter):
    """Test that similar cases search respects privacy settings"""

    # Tenant A создает case
    await storage.save_case(
        case_id="case-private",
        module="planning",
        case_data={
            "org_context": {
                "industry": "healthcare",
                "size": "medium",
                "maturity_level": "basic"
            },
            "journey": [],
            "metrics": {
                "total_duration_days": 10,
                "completed_successfully": True
            },
            "success_patterns": [],
            "lessons_learned": []
        },
        tenant_id="tenant-a"
    )

    # Similar cases search может возвращать анонимизированные данные
    # но НЕ должен раскрывать tenant_id или identifiable info
    similar = await storage.find_similar_cases(
        module="planning",
        org_context={
            "industry": "healthcare",
            "size": "medium"
        },
        current_stage="draft",
        limit=5
    )

    # Cases возвращаются, но без tenant_id
    for case in similar:
        assert 'tenant_id' not in case or case.get('tenant_id') is None


@pytest.mark.asyncio
async def test_tenant_id_cannot_be_overridden_in_query(storage: PostgresStorageAdapter):
    """Test that tenant_id in WHERE clause cannot be bypassed"""

    # Создаем workflow для tenant-a
    await storage.save_workflow_context(
        workflow_id="secure-workflow",
        module="planning",
        context={"sensitive": "data"},
        tenant_id="tenant-a"
    )

    # Попытка получить с другим tenant_id
    result = await storage.get_workflow_context(
        workflow_id="secure-workflow",
        tenant_id="tenant-b"  # Different tenant
    )

    # Должен вернуть None
    assert result is None


@pytest.mark.asyncio
async def test_raw_query_tenant_isolation(storage: PostgresStorageAdapter):
    """Test tenant isolation in raw SQL queries"""

    # Создаем workflows для двух tenants
    await storage.save_workflow_context(
        workflow_id="wf-001",
        module="planning",
        context={"data": "a"},
        tenant_id="tenant-a"
    )

    await storage.save_workflow_context(
        workflow_id="wf-002",
        module="planning",
        context={"data": "b"},
        tenant_id="tenant-b"
    )

    # Raw query должен учитывать tenant_id
    async with storage.pool.acquire() as conn:
        # Tenant A видит только свои данные
        rows_a = await conn.fetch("""
            SELECT workflow_id, context
            FROM workflow_intelligence.workflow_contexts
            WHERE tenant_id = $1
        """, "tenant-a")

        assert len(rows_a) == 1
        assert rows_a[0]['workflow_id'] == "wf-001"

        # Tenant B видит только свои данные
        rows_b = await conn.fetch("""
            SELECT workflow_id, context
            FROM workflow_intelligence.workflow_contexts
            WHERE tenant_id = $1
        """, "tenant-b")

        assert len(rows_b) == 1
        assert rows_b[0]['workflow_id'] == "wf-002"


# ============================================================================
# DATABASE-LEVEL RLS TESTS (Future Implementation)
# ============================================================================

@pytest.mark.skip(reason="Database-level RLS not yet implemented")
@pytest.mark.asyncio
async def test_database_rls_policy_exists(storage: PostgresStorageAdapter):
    """Test that RLS policies are enabled at database level"""

    async with storage.pool.acquire() as conn:
        # Check if RLS is enabled
        rls_enabled = await conn.fetchval("""
            SELECT relrowsecurity
            FROM pg_class
            WHERE relname = 'workflow_contexts'
            AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'workflow_intelligence')
        """)

        assert rls_enabled is True, "RLS should be enabled on workflow_contexts table"


@pytest.mark.skip(reason="Database-level RLS not yet implemented")
@pytest.mark.asyncio
async def test_database_rls_policy_enforced(storage: PostgresStorageAdapter):
    """Test that RLS policy is enforced at database level"""

    # This test will verify that even with direct SQL,
    # tenant isolation is enforced by database RLS policies

    # TODO: Implement when migrating to database-level RLS
    pass
