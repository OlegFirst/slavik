"""Tests for PostgresStorageAdapter"""

import pytest
from datetime import datetime
from workflow_intelligence.storage.postgres_adapter import PostgresStorageAdapter


@pytest.mark.asyncio
async def test_connect_and_schema_creation(database_url):
    """Test database connection and automatic schema creation"""
    adapter = PostgresStorageAdapter(database_url)
    await adapter.connect()

    # Verify schema exists
    async with adapter.pool.acquire() as conn:
        schema_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'workflow_intelligence')"
        )
        assert schema_exists, "Schema workflow_intelligence should be created"

        # Verify tables exist
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'workflow_intelligence'"
        )
        table_names = [row['table_name'] for row in tables]

        assert 'workflow_contexts' in table_names
        assert 'workflow_cases' in table_names
        assert 'benchmarks' in table_names
        assert 'ml_predictions' in table_names

    await adapter.close()


@pytest.mark.asyncio
async def test_save_and_get_workflow_context(storage, sample_workflow_context):
    """Test saving and retrieving workflow context"""
    # Save context
    await storage.save_workflow_context(
        workflow_id=sample_workflow_context["workflow_id"],
        module=sample_workflow_context["module"],
        context=sample_workflow_context,
        tenant_id=sample_workflow_context["tenant_id"]
    )

    # Retrieve context
    retrieved = await storage.get_workflow_context(
        workflow_id=sample_workflow_context["workflow_id"],
        tenant_id=sample_workflow_context["tenant_id"]
    )

    assert retrieved is not None
    assert retrieved["workflow_id"] == sample_workflow_context["workflow_id"]
    assert retrieved["module"] == sample_workflow_context["module"]
    assert retrieved["current_stage"] == sample_workflow_context["current_stage"]


@pytest.mark.asyncio
async def test_update_workflow_context(storage, sample_workflow_context):
    """Test updating existing workflow context"""
    # Save initial context
    await storage.save_workflow_context(
        workflow_id=sample_workflow_context["workflow_id"],
        module=sample_workflow_context["module"],
        context=sample_workflow_context,
        tenant_id=sample_workflow_context["tenant_id"]
    )

    # Update context
    updated_context = sample_workflow_context.copy()
    updated_context["current_stage"] = "review"
    updated_context["data"]["approved_by"] = "user-123"

    await storage.save_workflow_context(
        workflow_id=sample_workflow_context["workflow_id"],
        module=sample_workflow_context["module"],
        context=updated_context,
        tenant_id=sample_workflow_context["tenant_id"]
    )

    # Retrieve and verify
    retrieved = await storage.get_workflow_context(
        workflow_id=sample_workflow_context["workflow_id"],
        tenant_id=sample_workflow_context["tenant_id"]
    )

    assert retrieved["current_stage"] == "review"
    assert retrieved["data"]["approved_by"] == "user-123"


@pytest.mark.asyncio
async def test_save_and_retrieve_case(storage, sample_case_data):
    """Test saving and retrieving completed cases"""
    case_id = "case-planning-001"

    # Save case
    await storage.save_case(
        case_id=case_id,
        module=sample_case_data["module"],
        case_data=sample_case_data,
        tenant_id="tenant-test"
    )

    # Retrieve case
    retrieved = await storage.get_case(case_id)

    assert retrieved is not None
    assert retrieved["case_id"] == case_id
    assert retrieved["module"] == sample_case_data["module"]
    assert retrieved["industry"] == sample_case_data["industry"]
    assert retrieved["success"] is True


@pytest.mark.asyncio
async def test_find_similar_cases(storage):
    """Test finding similar cases by industry and org size"""
    # Create multiple cases
    cases = [
        {
            "workflow_id": "wf-001",
            "module": "planning",
            "industry": "healthcare",
            "org_size": "medium",
            "total_duration_days": 15,
            "success": True
        },
        {
            "workflow_id": "wf-002",
            "module": "planning",
            "industry": "healthcare",
            "org_size": "large",
            "total_duration_days": 20,
            "success": True
        },
        {
            "workflow_id": "wf-003",
            "module": "planning",
            "industry": "finance",
            "org_size": "medium",
            "total_duration_days": 18,
            "success": True
        }
    ]

    for i, case in enumerate(cases):
        await storage.save_case(
            case_id=f"case-{i}",
            module=case["module"],
            case_data=case,
            tenant_id="tenant-test"
        )

    # Find similar cases (healthcare + medium)
    similar = await storage.find_similar_cases(
        module="planning",
        org_context={"industry": "healthcare", "size": "medium"},
        current_stage="draft",
        limit=5
    )

    assert len(similar) > 0
    # Should prefer healthcare cases
    healthcare_cases = [c for c in similar if c.get("industry") == "healthcare"]
    assert len(healthcare_cases) > 0


@pytest.mark.asyncio
async def test_get_benchmarks(storage):
    """Test benchmark calculation from cases"""
    # Create successful cases
    for i in range(5):
        case_data = {
            "workflow_id": f"wf-{i}",
            "module": "planning",
            "industry": "healthcare",
            "org_size": "medium",
            "total_duration_days": 15 + i,
            "success": True
        }
        await storage.save_case(
            case_id=f"case-{i}",
            module="planning",
            case_data=case_data,
            tenant_id="tenant-test"
        )

    # Get benchmarks
    benchmarks = await storage.get_benchmarks(
        module="planning",
        industry="healthcare"
    )

    assert benchmarks is not None
    # Should have calculated average duration
    if benchmarks:
        assert "avg_duration_days" in benchmarks or "total_cases" in benchmarks


@pytest.mark.asyncio
async def test_tenant_isolation(storage, sample_workflow_context):
    """Test that contexts are isolated by tenant"""
    # Save context for tenant-1
    await storage.save_workflow_context(
        workflow_id="wf-001",
        module="planning",
        context=sample_workflow_context,
        tenant_id="tenant-1"
    )

    # Try to retrieve with wrong tenant
    retrieved = await storage.get_workflow_context(
        workflow_id="wf-001",
        tenant_id="tenant-2"
    )

    # Should not find context for different tenant
    assert retrieved is None or retrieved["workflow_id"] != "wf-001"


@pytest.mark.asyncio
async def test_close_connection(database_url):
    """Test proper connection cleanup"""
    adapter = PostgresStorageAdapter(database_url)
    await adapter.connect()

    assert adapter.pool is not None

    await adapter.close()

    # Pool should be closed
    assert adapter.pool is None or adapter.pool._closed
