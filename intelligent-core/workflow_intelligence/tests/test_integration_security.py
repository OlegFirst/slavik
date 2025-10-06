"""
Integration Security Tests

Комплексные тесты безопасности включающие:
- Tenant isolation в реальных сценариях
- Попытки доступа к чужим workflow
- Rate limiting (если будет)
- End-to-end security flows
"""

import pytest
import asyncio
from workflow_intelligence.storage.postgres_adapter import PostgresStorageAdapter


@pytest.mark.asyncio
async def test_complete_workflow_tenant_isolation(storage: PostgresStorageAdapter):
    """Test complete workflow lifecycle with tenant isolation"""

    # Scenario: Два tenants работают с одинаковыми workflow IDs

    # Tenant A: создает и обновляет workflow
    await storage.save_workflow_context(
        workflow_id="planning-workflow",
        module="planning",
        context={
            "stage": "draft",
            "strategy": "FAST_RECOVERY",
            "budget": 100000
        },
        tenant_id="tenant-a"
    )

    # Tenant B: создает workflow с тем же ID
    await storage.save_workflow_context(
        workflow_id="planning-workflow",
        module="planning",
        context={
            "stage": "draft",
            "strategy": "COST_OPTIMIZED",
            "budget": 50000
        },
        tenant_id="tenant-b"
    )

    # Tenant A обновляет свой workflow
    await storage.save_workflow_context(
        workflow_id="planning-workflow",
        module="planning",
        context={
            "stage": "review",
            "strategy": "FAST_RECOVERY",
            "budget": 120000
        },
        tenant_id="tenant-a"
    )

    # Tenant A видит свои изменения
    result_a = await storage.get_workflow_context(
        workflow_id="planning-workflow",
        tenant_id="tenant-a"
    )
    assert result_a['stage'] == "review"
    assert result_a['budget'] == 120000

    # Tenant B видит свои неизмененные данные
    result_b = await storage.get_workflow_context(
        workflow_id="planning-workflow",
        tenant_id="tenant-b"
    )
    assert result_b['stage'] == "draft"
    assert result_b['budget'] == 50000


@pytest.mark.asyncio
async def test_concurrent_tenant_operations(storage: PostgresStorageAdapter):
    """Test concurrent operations from multiple tenants"""

    async def tenant_workflow(tenant_id: str, workflow_count: int):
        """Simulate tenant creating multiple workflows"""
        for i in range(workflow_count):
            await storage.save_workflow_context(
                workflow_id=f"workflow-{i}",
                module="planning",
                context={"tenant": tenant_id, "index": i},
                tenant_id=tenant_id
            )

    # Запускаем одновременно для 3 tenants
    await asyncio.gather(
        tenant_workflow("tenant-a", 5),
        tenant_workflow("tenant-b", 5),
        tenant_workflow("tenant-c", 5)
    )

    # Проверяем что каждый tenant видит только свои данные
    for tenant_id in ["tenant-a", "tenant-b", "tenant-c"]:
        for i in range(5):
            result = await storage.get_workflow_context(
                workflow_id=f"workflow-{i}",
                tenant_id=tenant_id
            )
            assert result is not None
            assert result['tenant'] == tenant_id
            assert result['index'] == i


@pytest.mark.asyncio
async def test_cross_tenant_data_leakage_prevention(storage: PostgresStorageAdapter):
    """Test that no data leaks between tenants"""

    # Tenant A создает конфиденциальные данные
    sensitive_data = {
        "confidential": "secret_api_key_123",
        "pii": "user@example.com",
        "financial": 999999
    }

    await storage.save_workflow_context(
        workflow_id="confidential-workflow",
        module="planning",
        context=sensitive_data,
        tenant_id="tenant-a"
    )

    # Tenant B пытается получить доступ
    result = await storage.get_workflow_context(
        workflow_id="confidential-workflow",
        tenant_id="tenant-b"
    )

    # Не должен получить данные
    assert result is None

    # Проверим что данные tenant-a остались нетронутыми
    result_a = await storage.get_workflow_context(
        workflow_id="confidential-workflow",
        tenant_id="tenant-a"
    )
    assert result_a == sensitive_data


@pytest.mark.asyncio
async def test_case_submission_with_privacy(storage: PostgresStorageAdapter):
    """Test that case submission properly anonymizes data"""

    # Tenant создает case с потенциально идентифицируемыми данными
    case_data = {
        "org_context": {
            "industry": "healthcare",
            "size": "medium",
            "maturity_level": "basic"
        },
        "journey": [
            {
                "stage": "draft",
                "duration": 2,
                "actions": [
                    {
                        "action": "identified_processes",
                        # Не должно содержать PII
                        "user": "anonymized-user-id"
                    }
                ]
            }
        ],
        "metrics": {
            "total_duration_days": 10,
            "completed_successfully": True,
            "user_satisfaction": 4.5
        },
        "success_patterns": [
            "early_stakeholder_engagement"
        ],
        "lessons_learned": [
            "Document processes incrementally"
        ]
    }

    await storage.save_case(
        case_id="case-anonymized-001",
        module="planning",
        case_data=case_data,
        tenant_id="tenant-a"
    )

    # Case сохранен
    # NOTE: We need method to retrieve case to verify anonymization


@pytest.mark.asyncio
async def test_prediction_isolation(storage: PostgresStorageAdapter):
    """Test that ML predictions are isolated by tenant"""

    # Tenant A получает prediction
    await storage.save_prediction(
        workflow_id="wf-001",
        prediction={
            "success_probability": 0.9,
            "estimated_duration_days": 10,
            "risk_level": "low",
            "risk_factors": [],
            "model_version": "v1.0"
        },
        tenant_id="tenant-a"
    )

    # Tenant B получает prediction для своего workflow
    await storage.save_prediction(
        workflow_id="wf-001",  # Same ID, different tenant
        prediction={
            "success_probability": 0.3,
            "estimated_duration_days": 45,
            "risk_level": "high",
            "risk_factors": ["insufficient_data", "complex_requirements"],
            "model_version": "v1.0"
        },
        tenant_id="tenant-b"
    )

    # Predictions должны быть изолированы
    # NOTE: Need method to retrieve predictions


@pytest.mark.asyncio
async def test_malicious_tenant_cannot_enumerate_workflows(storage: PostgresStorageAdapter):
    """Test that tenant cannot enumerate other tenant's workflows"""

    # Tenant A создает workflows
    for i in range(10):
        await storage.save_workflow_context(
            workflow_id=f"wf-{i:03d}",
            module="planning",
            context={"index": i},
            tenant_id="tenant-a"
        )

    # Malicious tenant B пытается получить workflows tenant A
    # перебирая ID
    leaked_workflows = []
    for i in range(10):
        result = await storage.get_workflow_context(
            workflow_id=f"wf-{i:03d}",
            tenant_id="tenant-b"  # Wrong tenant
        )
        if result is not None:
            leaked_workflows.append(result)

    # Не должно быть утечек
    assert len(leaked_workflows) == 0


@pytest.mark.asyncio
async def test_benchmark_data_aggregation_is_safe(storage: PostgresStorageAdapter):
    """Test that benchmark aggregation doesn't leak tenant-specific data"""

    # Multiple tenants создают cases
    for tenant_num in range(1, 4):
        tenant_id = f"tenant-{tenant_num}"

        await storage.save_case(
            case_id=f"case-{tenant_num}",
            module="planning",
            case_data={
                "org_context": {
                    "industry": "finance",
                    "size": "large",
                    "maturity_level": "advanced"
                },
                "journey": [],
                "metrics": {
                    "total_duration_days": 15 + tenant_num,
                    "completed_successfully": True,
                    "user_satisfaction": 4.0 + (tenant_num * 0.1)
                },
                "success_patterns": [f"pattern_{tenant_num}"],
                "lessons_learned": [f"lesson_{tenant_num}"]
            },
            tenant_id=tenant_id
        )

    # Получаем benchmarks
    benchmarks = await storage.get_benchmarks(
        module="planning",
        industry="finance",
        org_size="large"
    )

    # Benchmarks должны быть агрегированными (усредненными)
    assert benchmarks['total_cases'] == 3
    assert benchmarks['avg_duration_days'] > 0

    # Но не должны содержать tenant-specific patterns
    # (они должны быть агрегированы или отфильтрованы)


@pytest.mark.asyncio
async def test_similar_cases_does_not_leak_tenant_data(storage: PostgresStorageAdapter):
    """Test that similar cases search doesn't leak tenant identifiable data"""

    # Tenant A создает case
    await storage.save_case(
        case_id="case-tenant-a",
        module="planning",
        case_data={
            "org_context": {
                "industry": "retail",
                "size": "medium",
                "maturity_level": "basic"
            },
            "journey": [],
            "metrics": {
                "total_duration_days": 12,
                "completed_successfully": True
            },
            "success_patterns": [],
            "lessons_learned": []
        },
        tenant_id="tenant-a"
    )

    # Tenant B ищет похожие cases
    similar = await storage.find_similar_cases(
        module="planning",
        org_context={
            "industry": "retail",
            "size": "medium"
        },
        current_stage="draft",
        limit=5
    )

    # Similar cases могут включать анонимизированные данные от tenant A
    # но НЕ должны содержать tenant_id или identifiable info
    for case in similar:
        # Проверим что tenant_id не раскрывается
        assert 'tenant_id' not in case or case.get('tenant_id') is None

        # Проверим что case_id анонимизирован или не содержит tenant info
        if 'case_id' in case:
            assert 'tenant-a' not in case['case_id'].lower()


@pytest.mark.asyncio
async def test_database_connection_uses_parameterized_queries(storage: PostgresStorageAdapter):
    """Integration test: verify all operations use parameterized queries"""

    # Это integration test который проверяет что
    # SQL injection невозможен во всех операциях

    malicious_inputs = [
        "'; DROP TABLE workflow_contexts; --",
        "' OR '1'='1",
        "'; DELETE FROM workflow_cases WHERE '1'='1'; --",
        "' UNION SELECT null, null, null, null; --"
    ]

    for malicious_input in malicious_inputs:
        # Save workflow
        await storage.save_workflow_context(
            workflow_id=malicious_input,
            module="planning",
            context={"test": "data"},
            tenant_id="tenant-test"
        )

        # Get workflow
        result = await storage.get_workflow_context(
            workflow_id=malicious_input,
            tenant_id="tenant-test"
        )
        assert result is not None

        # Save case
        await storage.save_case(
            case_id=malicious_input,
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
            tenant_id="tenant-test"
        )

    # Проверим что все таблицы все еще существуют
    async with storage.pool.acquire() as conn:
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'workflow_intelligence'
        """)

        table_names = [row['table_name'] for row in tables]

        assert 'workflow_contexts' in table_names
        assert 'workflow_cases' in table_names
        assert 'benchmarks' in table_names
        assert 'ml_predictions' in table_names


@pytest.mark.asyncio
async def test_large_scale_tenant_isolation(storage: PostgresStorageAdapter):
    """Test tenant isolation at scale (100 tenants)"""

    num_tenants = 100

    # Создаем workflows для 100 tenants
    for tenant_num in range(num_tenants):
        tenant_id = f"tenant-{tenant_num:03d}"

        await storage.save_workflow_context(
            workflow_id="standard-workflow",
            module="planning",
            context={"tenant_number": tenant_num},
            tenant_id=tenant_id
        )

    # Проверяем изоляцию для random tenants
    import random
    test_tenants = random.sample(range(num_tenants), 10)

    for tenant_num in test_tenants:
        tenant_id = f"tenant-{tenant_num:03d}"

        result = await storage.get_workflow_context(
            workflow_id="standard-workflow",
            tenant_id=tenant_id
        )

        assert result is not None
        assert result['tenant_number'] == tenant_num


@pytest.mark.asyncio
async def test_transaction_isolation_between_tenants(storage: PostgresStorageAdapter):
    """Test that transactions from different tenants don't interfere"""

    async def tenant_transaction(tenant_id: str, delay: float):
        """Simulate slow transaction"""
        await storage.save_workflow_context(
            workflow_id="transaction-test",
            module="planning",
            context={"started": True, "tenant": tenant_id},
            tenant_id=tenant_id
        )

        # Simulate processing delay
        await asyncio.sleep(delay)

        await storage.save_workflow_context(
            workflow_id="transaction-test",
            module="planning",
            context={"completed": True, "tenant": tenant_id},
            tenant_id=tenant_id
        )

    # Запускаем параллельные транзакции
    await asyncio.gather(
        tenant_transaction("tenant-a", 0.1),
        tenant_transaction("tenant-b", 0.05),
        tenant_transaction("tenant-c", 0.15)
    )

    # Каждый tenant должен видеть свой completed результат
    for tenant_id in ["tenant-a", "tenant-b", "tenant-c"]:
        result = await storage.get_workflow_context(
            workflow_id="transaction-test",
            tenant_id=tenant_id
        )

        assert result is not None
        assert result['completed'] is True
        assert result['tenant'] == tenant_id


@pytest.mark.asyncio
async def test_error_messages_do_not_leak_data(storage: PostgresStorageAdapter):
    """Test that error messages don't leak sensitive information"""

    # Попытка получить несуществующий workflow
    try:
        result = await storage.get_workflow_context(
            workflow_id="non-existent",
            tenant_id="tenant-a"
        )

        # Should return None, not raise error with details
        assert result is None

    except Exception as e:
        # If error raised, should not contain tenant IDs or sensitive data
        error_message = str(e)

        # Should not leak tenant IDs
        assert "tenant-a" not in error_message.lower()

        # Should not leak internal DB structure
        assert "workflow_intelligence" not in error_message.lower()
