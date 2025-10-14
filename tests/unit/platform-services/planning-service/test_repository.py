"""
Test Repository Layer (Data Access)
Tests for database operations and queries
"""

import pytest
from uuid import uuid4
from datetime import datetime

from repositories.repository import StrategyRepository
from models.database import Strategy
from models.domain import StrategyType, StrategyPhase, StrategyStatus


@pytest.mark.asyncio
class TestStrategyRepository:
    """Test StrategyRepository CRUD operations"""

    async def test_create_strategy(self, db_session):
        """Test creating a strategy"""
        repo = StrategyRepository(db_session)

        strategy = Strategy(
            id=uuid4(),
            tenant_id="test-tenant-123",
            strategy_number="STRAT-2025-001",
            name="Test Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Test recovery strategy objective",
            created_by="test-user"
        )

        created = await repo.create(strategy)

        assert created.id == strategy.id
        assert created.name == "Test Strategy"
        assert created.tenant_id == "test-tenant-123"
        assert created.strategy_type == StrategyType.RECOVERY
        assert created.status == StrategyStatus.DRAFT

    async def test_get_by_id(self, db_session):
        """Test retrieving strategy by ID"""
        repo = StrategyRepository(db_session)

        strategy_id = uuid4()
        strategy = Strategy(
            id=strategy_id,
            tenant_id="test-tenant-123",
            strategy_number="STRAT-2025-002",
            name="Findable Strategy",
            strategy_type=StrategyType.RESILIENCE,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Findable objective",
            created_by="test-user"
        )

        await repo.create(strategy)
        found = await repo.get_by_id(strategy_id)

        assert found is not None
        assert found.id == strategy_id
        assert found.name == "Findable Strategy"

    async def test_get_by_id_not_found(self, db_session):
        """Test retrieving non-existent strategy returns None"""
        repo = StrategyRepository(db_session)

        found = await repo.get_by_id(uuid4())

        assert found is None

    async def test_get_by_tenant(self, db_session):
        """Test retrieving strategies by tenant ID"""
        repo = StrategyRepository(db_session)

        # Create multiple strategies for same tenant
        tenant_id = "test-tenant-456"
        for i in range(3):
            strategy = Strategy(
                id=uuid4(),
                tenant_id=tenant_id,
                strategy_number=f"STRAT-2025-{100 + i}",
                name=f"Strategy {i + 1}",
                strategy_type=StrategyType.RECOVERY,
                strategy_phase=StrategyPhase.PRE_INCIDENT,
                status=StrategyStatus.DRAFT,
                objective="Test objective",
                created_by="test-user"
            )
            await repo.create(strategy)

        # Create strategy for different tenant
        other_strategy = Strategy(
            id=uuid4(),
            tenant_id="other-tenant",
            strategy_number="STRAT-2025-999",
            name="Other Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Other objective",
            created_by="test-user"
        )
        await repo.create(other_strategy)

        # Retrieve strategies for specific tenant
        strategies = await repo.get_by_tenant(tenant_id)

        assert len(strategies) == 3
        assert all(s.tenant_id == tenant_id for s in strategies)

    async def test_get_by_tenant_with_status_filter(self, db_session):
        """Test filtering strategies by status"""
        repo = StrategyRepository(db_session)

        tenant_id = "test-tenant-789"

        # Create draft strategy
        draft_strategy = Strategy(
            id=uuid4(),
            tenant_id=tenant_id,
            strategy_number="STRAT-2025-201",
            name="Draft Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Draft objective",
            created_by="test-user"
        )
        await repo.create(draft_strategy)

        # Create approved strategy
        approved_strategy = Strategy(
            id=uuid4(),
            tenant_id=tenant_id,
            strategy_number="STRAT-2025-202",
            name="Approved Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.APPROVED,
            objective="Approved objective",
            created_by="test-user"
        )
        await repo.create(approved_strategy)

        # Filter by DRAFT status
        draft_strategies = await repo.get_by_tenant(
            tenant_id=tenant_id,
            status=StrategyStatus.DRAFT
        )

        assert len(draft_strategies) == 1
        assert draft_strategies[0].status == StrategyStatus.DRAFT

        # Filter by APPROVED status
        approved_strategies = await repo.get_by_tenant(
            tenant_id=tenant_id,
            status=StrategyStatus.APPROVED
        )

        assert len(approved_strategies) == 1
        assert approved_strategies[0].status == StrategyStatus.APPROVED

    async def test_get_by_tenant_with_type_filter(self, db_session):
        """Test filtering strategies by type"""
        repo = StrategyRepository(db_session)

        tenant_id = "test-tenant-999"

        # Create recovery strategy
        recovery = Strategy(
            id=uuid4(),
            tenant_id=tenant_id,
            strategy_number="STRAT-2025-301",
            name="Recovery Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Recovery objective",
            created_by="test-user"
        )
        await repo.create(recovery)

        # Create prevention strategy
        prevention = Strategy(
            id=uuid4(),
            tenant_id=tenant_id,
            strategy_number="STRAT-2025-302",
            name="Prevention Strategy",
            strategy_type=StrategyType.PREVENTION,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Prevention objective",
            created_by="test-user"
        )
        await repo.create(prevention)

        # Filter by RECOVERY type
        recovery_strategies = await repo.get_by_tenant(
            tenant_id=tenant_id,
            strategy_type=StrategyType.RECOVERY
        )

        assert len(recovery_strategies) == 1
        assert recovery_strategies[0].strategy_type == StrategyType.RECOVERY

    async def test_get_by_tenant_with_pagination(self, db_session):
        """Test pagination with skip and limit"""
        repo = StrategyRepository(db_session)

        tenant_id = "test-tenant-pagination"

        # Create 10 strategies
        for i in range(10):
            strategy = Strategy(
                id=uuid4(),
                tenant_id=tenant_id,
                strategy_number=f"STRAT-2025-{400 + i}",
                name=f"Strategy {i + 1}",
                strategy_type=StrategyType.RECOVERY,
                strategy_phase=StrategyPhase.PRE_INCIDENT,
                status=StrategyStatus.DRAFT,
                objective="Test objective",
                created_by="test-user"
            )
            await repo.create(strategy)

        # Get first page (5 items)
        page1 = await repo.get_by_tenant(
            tenant_id=tenant_id,
            skip=0,
            limit=5
        )
        assert len(page1) == 5

        # Get second page (5 items)
        page2 = await repo.get_by_tenant(
            tenant_id=tenant_id,
            skip=5,
            limit=5
        )
        assert len(page2) == 5

        # Ensure different strategies
        page1_ids = {s.id for s in page1}
        page2_ids = {s.id for s in page2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_update_strategy(self, db_session):
        """Test updating strategy"""
        repo = StrategyRepository(db_session)

        strategy_id = uuid4()
        strategy = Strategy(
            id=strategy_id,
            tenant_id="test-tenant-update",
            strategy_number="STRAT-2025-500",
            name="Original Name",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Original objective",
            created_by="test-user"
        )

        await repo.create(strategy)

        # Update strategy
        update_data = {
            "name": "Updated Name",
            "status": StrategyStatus.REVIEW,
            "estimated_cost": 150000.0
        }

        updated = await repo.update(strategy_id, update_data)

        assert updated.name == "Updated Name"
        assert updated.status == StrategyStatus.REVIEW
        assert updated.estimated_cost == 150000.0

    async def test_soft_delete(self, db_session):
        """Test soft delete (active=False)"""
        repo = StrategyRepository(db_session)

        strategy_id = uuid4()
        strategy = Strategy(
            id=strategy_id,
            tenant_id="test-tenant-delete",
            strategy_number="STRAT-2025-600",
            name="To Be Deleted",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Delete me",
            created_by="test-user",
            active=True
        )

        await repo.create(strategy)

        # Delete strategy
        result = await repo.delete(strategy_id)
        assert result is True

        # Strategy should still exist but inactive
        deleted = await repo.get_by_id(strategy_id)
        assert deleted is not None
        assert deleted.active is False

    async def test_get_by_tenant_excludes_inactive(self, db_session):
        """Test that get_by_tenant only returns active strategies"""
        repo = StrategyRepository(db_session)

        tenant_id = "test-tenant-active"

        # Create active strategy
        active = Strategy(
            id=uuid4(),
            tenant_id=tenant_id,
            strategy_number="STRAT-2025-701",
            name="Active Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Active objective",
            created_by="test-user",
            active=True
        )
        await repo.create(active)

        # Create inactive strategy
        inactive = Strategy(
            id=uuid4(),
            tenant_id=tenant_id,
            strategy_number="STRAT-2025-702",
            name="Inactive Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Inactive objective",
            created_by="test-user",
            active=False
        )
        await repo.create(inactive)

        # Get strategies - should only return active
        strategies = await repo.get_by_tenant(tenant_id)

        assert len(strategies) == 1
        assert strategies[0].strategy_number == "STRAT-2025-701"

    async def test_get_by_number(self, db_session):
        """Test retrieving strategy by strategy_number"""
        repo = StrategyRepository(db_session)

        strategy = Strategy(
            id=uuid4(),
            tenant_id="test-tenant-800",
            strategy_number="STRAT-2025-UNIQUE",
            name="Unique Number Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Find by number",
            created_by="test-user"
        )

        await repo.create(strategy)
        found = await repo.get_by_number("STRAT-2025-UNIQUE")

        assert found is not None
        assert found.strategy_number == "STRAT-2025-UNIQUE"
        assert found.name == "Unique Number Strategy"

    async def test_get_by_number_not_found(self, db_session):
        """Test get_by_number returns None for non-existent number"""
        repo = StrategyRepository(db_session)

        found = await repo.get_by_number("STRAT-DOES-NOT-EXIST")

        assert found is None

    async def test_count_by_tenant(self, db_session):
        """Test counting strategies by tenant"""
        repo = StrategyRepository(db_session)

        tenant_id = "test-tenant-count"

        # Create 5 strategies
        for i in range(5):
            strategy = Strategy(
                id=uuid4(),
                tenant_id=tenant_id,
                strategy_number=f"STRAT-2025-{900 + i}",
                name=f"Count Strategy {i + 1}",
                strategy_type=StrategyType.RECOVERY,
                strategy_phase=StrategyPhase.PRE_INCIDENT,
                status=StrategyStatus.DRAFT,
                objective="Count objective",
                created_by="test-user"
            )
            await repo.create(strategy)

        count = await repo.count_by_tenant(tenant_id)

        assert count == 5

    async def test_count_by_tenant_with_status_filter(self, db_session):
        """Test counting strategies by tenant with status filter"""
        repo = StrategyRepository(db_session)

        tenant_id = "test-tenant-count-status"

        # Create 3 draft strategies
        for i in range(3):
            strategy = Strategy(
                id=uuid4(),
                tenant_id=tenant_id,
                strategy_number=f"STRAT-2025-{950 + i}",
                name=f"Draft {i + 1}",
                strategy_type=StrategyType.RECOVERY,
                strategy_phase=StrategyPhase.PRE_INCIDENT,
                status=StrategyStatus.DRAFT,
                objective="Draft objective",
                created_by="test-user"
            )
            await repo.create(strategy)

        # Create 2 approved strategies
        for i in range(2):
            strategy = Strategy(
                id=uuid4(),
                tenant_id=tenant_id,
                strategy_number=f"STRAT-2025-{960 + i}",
                name=f"Approved {i + 1}",
                strategy_type=StrategyType.RECOVERY,
                strategy_phase=StrategyPhase.PRE_INCIDENT,
                status=StrategyStatus.APPROVED,
                objective="Approved objective",
                created_by="test-user"
            )
            await repo.create(strategy)

        draft_count = await repo.count_by_tenant(tenant_id, status=StrategyStatus.DRAFT)
        approved_count = await repo.count_by_tenant(tenant_id, status=StrategyStatus.APPROVED)

        assert draft_count == 3
        assert approved_count == 2

    async def test_update_json_fields(self, db_session):
        """Test updating JSON fields like cost_breakdown"""
        repo = StrategyRepository(db_session)

        strategy_id = uuid4()
        strategy = Strategy(
            id=strategy_id,
            tenant_id="test-tenant-json",
            strategy_number="STRAT-2025-JSON",
            name="JSON Test Strategy",
            strategy_type=StrategyType.RECOVERY,
            strategy_phase=StrategyPhase.PRE_INCIDENT,
            status=StrategyStatus.DRAFT,
            objective="Test JSON updates",
            created_by="test-user"
        )

        await repo.create(strategy)

        # Update with JSON data
        cost_breakdown = {
            "capex": 100000,
            "opex": 5000,
            "training": 10000,
            "maintenance": 3000,
            "other": 2000,
            "currency": "USD"
        }

        update_data = {
            "cost_breakdown": cost_breakdown,
            "estimated_cost": 120000.0
        }

        updated = await repo.update(strategy_id, update_data)

        assert updated.cost_breakdown == cost_breakdown
        assert updated.cost_breakdown["capex"] == 100000
        assert updated.estimated_cost == 120000.0
