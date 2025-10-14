"""
SQL Injection Protection Tests

Проверяем что SQL injection НЕВОЗМОЖЕН во всех точках входа.
Все запросы должны использовать параметризацию ($1, $2, etc).
"""

import pytest
from workflow_intelligence.storage.postgres_adapter import PostgresStorageAdapter


@pytest.mark.asyncio
async def test_sql_injection_in_workflow_id(storage: PostgresStorageAdapter):
    """Test that SQL injection in workflow_id is prevented"""

    # Попытка SQL injection через workflow_id
    malicious_id = "123'; DROP TABLE workflow_intelligence.workflow_contexts; --"

    # Не должно упасть и не должно выполнить DROP
    result = await storage.get_workflow_context(
        workflow_id=malicious_id,
        tenant_id="test-tenant"
    )

    # Должно просто не найти (None), а не выполнить инъекцию
    assert result is None

    # Проверим что таблица все еще существует
    async with storage.pool.acquire() as conn:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'workflow_intelligence'
                AND table_name = 'workflow_contexts'
            )
        """)
        assert exists is True, "Table was dropped! SQL injection vulnerability!"


@pytest.mark.asyncio
async def test_sql_injection_in_tenant_id(storage: PostgresStorageAdapter):
    """Test that SQL injection in tenant_id is prevented"""

    # Попытка SQL injection через tenant_id
    malicious_tenant = "tenant' OR '1'='1"

    result = await storage.get_workflow_context(
        workflow_id="valid-workflow-id",
        tenant_id=malicious_tenant
    )

    # Должно вернуть None (не найдено), а не все записи
    assert result is None


@pytest.mark.asyncio
async def test_sql_injection_in_module(storage: PostgresStorageAdapter):
    """Test that SQL injection in module parameter is prevented"""

    # Создаем валидный workflow
    await storage.save_workflow_context(
        workflow_id="test-workflow-001",
        module="planning",
        context={"stage": "draft"},
        tenant_id="tenant-test"
    )

    # Попытка SQL injection через module
    malicious_module = "planning'; DROP TABLE workflow_intelligence.workflow_cases; --"

    # Сохраняем с malicious module
    await storage.save_workflow_context(
        workflow_id="test-workflow-002",
        module=malicious_module,
        context={"stage": "draft"},
        tenant_id="tenant-test"
    )

    # Проверим что таблица все еще существует
    async with storage.pool.acquire() as conn:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'workflow_intelligence'
                AND table_name = 'workflow_cases'
            )
        """)
        assert exists is True, "Table was dropped! SQL injection vulnerability!"


@pytest.mark.asyncio
async def test_sql_injection_in_case_id(storage: PostgresStorageAdapter):
    """Test that SQL injection in case_id is prevented"""

    malicious_case_id = "case-123'; UPDATE workflow_intelligence.benchmarks SET success_rate=0; --"

    case_data = {
        "org_context": {
            "industry": "healthcare",
            "size": "medium",
            "maturity_level": "basic"
        },
        "journey": [{"stage": "draft", "duration": 2}],
        "metrics": {
            "total_duration_days": 10,
            "completed_successfully": True,
            "user_satisfaction": 4.5
        },
        "success_patterns": ["pattern1"],
        "lessons_learned": ["lesson1"]
    }

    # Сохраняем case с malicious ID
    await storage.save_case(
        case_id=malicious_case_id,
        module="planning",
        case_data=case_data,
        tenant_id="tenant-test"
    )

    # Case должен быть сохранен с malicious ID как строкой
    # но SQL injection не должна выполниться


@pytest.mark.asyncio
async def test_sql_injection_in_industry_filter(storage: PostgresStorageAdapter):
    """Test that SQL injection in industry filter is prevented"""

    # Создаем валидный case
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
                "completed_successfully": True
            },
            "success_patterns": [],
            "lessons_learned": []
        },
        tenant_id="tenant-test"
    )

    # Попытка SQL injection через industry filter
    malicious_industry = "healthcare' OR '1'='1"

    results = await storage.find_similar_cases(
        module="planning",
        org_context={
            "industry": malicious_industry,
            "size": "medium"
        },
        current_stage="draft",
        limit=10
    )

    # Должно вернуть 0 результатов (не найдено точное совпадение)
    # а не все записи (что было бы при успешной инъекции)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_sql_injection_in_benchmarks_query(storage: PostgresStorageAdapter):
    """Test that SQL injection in benchmarks query is prevented"""

    malicious_module = "planning'; DROP SCHEMA workflow_intelligence CASCADE; --"

    # Не должно упасть
    result = await storage.get_benchmarks(
        module=malicious_module,
        industry="healthcare",
        org_size="medium"
    )

    # Должно вернуть пустые данные
    assert result['total_cases'] == 0

    # Проверим что схема все еще существует
    async with storage.pool.acquire() as conn:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.schemata
                WHERE schema_name = 'workflow_intelligence'
            )
        """)
        assert exists is True, "Schema was dropped! SQL injection vulnerability!"


@pytest.mark.asyncio
async def test_sql_injection_in_json_context(storage: PostgresStorageAdapter):
    """Test that SQL injection in JSON context data is prevented"""

    # Попытка инъекции через JSON данные
    malicious_context = {
        "stage": "draft'; DROP TABLE workflow_intelligence.ml_predictions; --",
        "data": {
            "user_input": "'; DELETE FROM workflow_intelligence.workflow_contexts WHERE '1'='1"
        }
    }

    await storage.save_workflow_context(
        workflow_id="test-workflow-json",
        module="planning",
        context=malicious_context,
        tenant_id="tenant-test"
    )

    # Проверим что таблица все еще существует
    async with storage.pool.acquire() as conn:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'workflow_intelligence'
                AND table_name = 'ml_predictions'
            )
        """)
        assert exists is True, "Table was dropped! SQL injection vulnerability!"

    # Проверим что данные сохранены как строки в JSON
    result = await storage.get_workflow_context(
        workflow_id="test-workflow-json",
        tenant_id="tenant-test"
    )

    assert result is not None
    assert result['stage'] == malicious_context['stage']  # Сохранено как строка


@pytest.mark.asyncio
async def test_sql_injection_union_attack(storage: PostgresStorageAdapter):
    """Test that UNION-based SQL injection is prevented"""

    # UNION attack попытка
    malicious_id = "test' UNION SELECT null, 'admin', 'hacked', null, null, null, null--"

    result = await storage.get_workflow_context(
        workflow_id=malicious_id,
        tenant_id="tenant-test"
    )

    # Должно вернуть None, а не результат UNION запроса
    assert result is None


@pytest.mark.asyncio
async def test_sql_injection_stacked_queries(storage: PostgresStorageAdapter):
    """Test that stacked queries are prevented"""

    # Попытка выполнить несколько запросов
    malicious_id = "test'; INSERT INTO workflow_intelligence.workflow_contexts (workflow_id, module, tenant_id, context) VALUES ('hacked', 'hacked', 'hacked', '{}'); --"

    result = await storage.get_workflow_context(
        workflow_id=malicious_id,
        tenant_id="tenant-test"
    )

    assert result is None

    # Проверим что запись 'hacked' НЕ была создана
    async with storage.pool.acquire() as conn:
        hacked = await conn.fetchrow("""
            SELECT * FROM workflow_intelligence.workflow_contexts
            WHERE workflow_id = 'hacked' AND module = 'hacked'
        """)
        assert hacked is None, "Stacked query was executed! SQL injection vulnerability!"


@pytest.mark.asyncio
async def test_parametrized_queries_workflow_context(storage: PostgresStorageAdapter):
    """Verify that workflow context queries use parameterization"""

    # Создаем workflow с специальными символами
    special_chars_id = "test-workflow-'\"\\--"
    special_tenant = "tenant-'\"\\--"

    await storage.save_workflow_context(
        workflow_id=special_chars_id,
        module="planning",
        context={"test": "data"},
        tenant_id=special_tenant
    )

    # Должно корректно сохранить и получить
    result = await storage.get_workflow_context(
        workflow_id=special_chars_id,
        tenant_id=special_tenant
    )

    assert result is not None
    assert result['test'] == 'data'


@pytest.mark.asyncio
async def test_parametrized_queries_save_prediction(storage: PostgresStorageAdapter):
    """Verify that prediction saving uses parameterization"""

    malicious_workflow_id = "wf'; DROP TABLE workflow_intelligence.ml_predictions; --"

    prediction = {
        "success_probability": 0.8,
        "estimated_duration_days": 15,
        "risk_level": "medium",
        "risk_factors": ["factor1"],
        "model_version": "v1.0"
    }

    # Не должно упасть
    await storage.save_prediction(
        workflow_id=malicious_workflow_id,
        prediction=prediction,
        tenant_id="tenant-test"
    )

    # Проверим что таблица существует
    async with storage.pool.acquire() as conn:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'workflow_intelligence'
                AND table_name = 'ml_predictions'
            )
        """)
        assert exists is True, "Table was dropped! SQL injection vulnerability!"


@pytest.mark.asyncio
async def test_sql_injection_with_encoding_tricks(storage: PostgresStorageAdapter):
    """Test SQL injection using encoding tricks"""

    # URL encoding попытка
    malicious_id = "test%27%3B%20DROP%20TABLE%20workflow_contexts%3B%20--"

    result = await storage.get_workflow_context(
        workflow_id=malicious_id,
        tenant_id="tenant-test"
    )

    assert result is None

    # Unicode encoding попытка
    malicious_id2 = "test\u0027; DROP TABLE workflow_contexts; --"

    result2 = await storage.get_workflow_context(
        workflow_id=malicious_id2,
        tenant_id="tenant-test"
    )

    assert result2 is None
