"""
Test BIA Repository Layer
Tests for database operations and data persistence
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import BIAProcessDB
from models.domain import BIAProcess, BIAProcessCreate
from models.enums import CriticalityLevel, ProcessStatus, IndustryType
from repositories.bia_repository import BIARepository


class TestBIARepository:
    """Test BIA Repository CRUD operations"""

    @pytest.fixture
    async def repository(self, db_session: AsyncSession):
        """Create repository instance"""
        return BIARepository(db_session)

    async def test_should_create_bia_process(
        self,
        repository: BIARepository,
        sample_bia_create_data: BIAProcessCreate
    ):
        """Test creating a BIA process in the database"""
        process = BIAProcess(**sample_bia_create_data.dict())
        created = await repository.create(process)

        assert created.id is not None
        assert created.name == sample_bia_create_data.name
        assert created.tenant_id == sample_bia_create_data.tenant_id
        assert created.criticality == sample_bia_create_data.criticality

    async def test_should_get_bia_process_by_id(
        self,
        repository: BIARepository,
        sample_bia_process_db: BIAProcessDB
    ):
        """Test retrieving a BIA process by ID"""
        retrieved = await repository.get(sample_bia_process_db.id)

        assert retrieved is not None
        assert retrieved.id == sample_bia_process_db.id
        assert retrieved.name == sample_bia_process_db.name
        assert retrieved.tenant_id == sample_bia_process_db.tenant_id

    async def test_should_return_none_for_nonexistent_process(self, repository: BIARepository):
        """Test getting non-existent process returns None"""
        retrieved = await repository.get(99999)
        assert retrieved is None

    async def test_should_list_all_processes_for_tenant(
        self,
        repository: BIARepository,
        db_session: AsyncSession,
        tenant_id: str
    ):
        """Test listing all processes for a tenant"""
        # Create multiple processes
        for i in range(3):
            process_db = BIAProcessDB(
                tenant_id=tenant_id,
                name=f"Process {i}",
                criticality=CriticalityLevel.MEDIUM.value,
                industry=IndustryType.TECHNOLOGY.value,
                rto_hours=4,
                rpo_hours=1,
                mtpd_hours=8,
                status=ProcessStatus.DRAFT.value
            )
            db_session.add(process_db)
        await db_session.commit()

        processes = await repository.list(tenant_id)

        assert len(processes) >= 3
        for process in processes:
            assert process.tenant_id == tenant_id

    async def test_should_isolate_tenants_in_list(
        self,
        repository: BIARepository,
        db_session: AsyncSession,
        tenant_id: str
    ):
        """Test tenant isolation in list operation"""
        # Create process for tenant_id
        process1 = BIAProcessDB(
            tenant_id=tenant_id,
            name="Tenant 1 Process",
            criticality=CriticalityLevel.HIGH.value,
            industry=IndustryType.TECHNOLOGY.value,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=8,
            status=ProcessStatus.DRAFT.value
        )
        db_session.add(process1)

        # Create process for different tenant
        process2 = BIAProcessDB(
            tenant_id="other-tenant-999",
            name="Other Tenant Process",
            criticality=CriticalityLevel.HIGH.value,
            industry=IndustryType.TECHNOLOGY.value,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=8,
            status=ProcessStatus.DRAFT.value
        )
        db_session.add(process2)
        await db_session.commit()

        # List should only return tenant_id processes
        processes = await repository.list(tenant_id)

        assert all(p.tenant_id == tenant_id for p in processes)
        assert not any(p.tenant_id == "other-tenant-999" for p in processes)

    async def test_should_update_bia_process(
        self,
        repository: BIARepository,
        sample_bia_process_db: BIAProcessDB
    ):
        """Test updating a BIA process"""
        updates = {
            "rto_hours": 2,
            "rpo_hours": 0,
            "status": ProcessStatus.COMPLETED,
            "name": "Updated Process Name"
        }

        updated = await repository.update(sample_bia_process_db.id, updates)

        assert updated.id == sample_bia_process_db.id
        assert updated.rto_hours == 2
        assert updated.rpo_hours == 0
        assert updated.status == ProcessStatus.COMPLETED
        assert updated.name == "Updated Process Name"
        # Original tenant_id should be unchanged
        assert updated.tenant_id == sample_bia_process_db.tenant_id

    async def test_should_update_partial_fields(
        self,
        repository: BIARepository,
        sample_bia_process_db: BIAProcessDB
    ):
        """Test updating only specific fields"""
        original_name = sample_bia_process_db.name
        original_rto = sample_bia_process_db.rto_hours

        updates = {
            "description": "Updated description only"
        }

        updated = await repository.update(sample_bia_process_db.id, updates)

        assert updated.description == "Updated description only"
        # Other fields unchanged
        assert updated.name == original_name
        assert updated.rto_hours == original_rto

    async def test_should_delete_bia_process(
        self,
        repository: BIARepository,
        db_session: AsyncSession,
        sample_bia_process_db: BIAProcessDB
    ):
        """Test deleting a BIA process"""
        process_id = sample_bia_process_db.id

        await repository.delete(process_id)

        # Verify deletion
        stmt = select(BIAProcessDB).where(BIAProcessDB.id == process_id)
        result = await db_session.execute(stmt)
        deleted_process = result.scalar_one_or_none()

        assert deleted_process is None

    async def test_should_handle_delete_of_nonexistent_process(self, repository: BIARepository):
        """Test deleting non-existent process doesn't raise error"""
        # Should not raise exception
        await repository.delete(99999)

    async def test_should_preserve_json_fields_in_create(
        self,
        repository: BIARepository,
        sample_bia_create_data: BIAProcessCreate
    ):
        """Test JSON fields are properly preserved"""
        process = BIAProcess(**sample_bia_create_data.dict())
        created = await repository.create(process)

        assert created.financial_impact == sample_bia_create_data.financial_impact
        assert created.operational_impact == sample_bia_create_data.operational_impact
        assert len(created.dependencies) == len(sample_bia_create_data.dependencies)
        assert created.personnel_requirements == sample_bia_create_data.personnel_requirements

    async def test_should_preserve_json_fields_in_update(
        self,
        repository: BIARepository,
        sample_bia_process_db: BIAProcessDB
    ):
        """Test updating JSON fields"""
        new_financial_impact = {
            "1_hour": 10000.0,
            "24_hours": 500000.0
        }
        new_personnel_reqs = {
            "roles": ["New Role"],
            "min_staff": 10
        }

        updates = {
            "financial_impact": new_financial_impact,
            "personnel_requirements": new_personnel_reqs
        }

        updated = await repository.update(sample_bia_process_db.id, updates)

        assert updated.financial_impact == new_financial_impact
        assert updated.personnel_requirements == new_personnel_reqs

    async def test_should_filter_by_criticality(
        self,
        repository: BIARepository,
        db_session: AsyncSession,
        tenant_id: str
    ):
        """Test filtering processes by criticality"""
        # Create processes with different criticality levels
        for criticality in [CriticalityLevel.CRITICAL, CriticalityLevel.HIGH, CriticalityLevel.MEDIUM]:
            process_db = BIAProcessDB(
                tenant_id=tenant_id,
                name=f"Process {criticality.value}",
                criticality=criticality.value,
                industry=IndustryType.TECHNOLOGY.value,
                rto_hours=4,
                rpo_hours=1,
                mtpd_hours=8,
                status=ProcessStatus.DRAFT.value
            )
            db_session.add(process_db)
        await db_session.commit()

        # Get all processes and filter
        all_processes = await repository.list(tenant_id)
        critical_processes = [p for p in all_processes if p.criticality == CriticalityLevel.CRITICAL]

        assert len(critical_processes) >= 1
        assert all(p.criticality == CriticalityLevel.CRITICAL for p in critical_processes)

    async def test_should_filter_by_status(
        self,
        repository: BIARepository,
        db_session: AsyncSession,
        tenant_id: str
    ):
        """Test filtering processes by status"""
        # Create processes with different statuses
        for status in [ProcessStatus.DRAFT, ProcessStatus.IN_PROGRESS, ProcessStatus.COMPLETED]:
            process_db = BIAProcessDB(
                tenant_id=tenant_id,
                name=f"Process {status.value}",
                criticality=CriticalityLevel.MEDIUM.value,
                industry=IndustryType.TECHNOLOGY.value,
                rto_hours=4,
                rpo_hours=1,
                mtpd_hours=8,
                status=status.value
            )
            db_session.add(process_db)
        await db_session.commit()

        # Get all processes and filter
        all_processes = await repository.list(tenant_id)
        completed_processes = [p for p in all_processes if p.status == ProcessStatus.COMPLETED]

        assert len(completed_processes) >= 1
        assert all(p.status == ProcessStatus.COMPLETED for p in completed_processes)

    async def test_should_handle_concurrent_updates(
        self,
        repository: BIARepository,
        sample_bia_process_db: BIAProcessDB
    ):
        """Test handling concurrent updates to same process"""
        # First update
        await repository.update(sample_bia_process_db.id, {"rto_hours": 2})

        # Second update (should not conflict)
        await repository.update(sample_bia_process_db.id, {"rpo_hours": 0})

        # Verify both updates applied
        updated = await repository.get(sample_bia_process_db.id)
        assert updated.rto_hours == 2
        assert updated.rpo_hours == 0

    async def test_should_handle_large_json_fields(
        self,
        repository: BIARepository,
        tenant_id: str
    ):
        """Test handling large JSON data structures"""
        # Create large dependencies list
        large_dependencies = [
            {
                "type": "technology",
                "name": f"System {i}",
                "criticality": (i % 5) + 1,
                "required": True
            }
            for i in range(100)
        ]

        process = BIAProcess(
            tenant_id=tenant_id,
            name="Process with Large Dependencies",
            criticality=CriticalityLevel.HIGH,
            industry=IndustryType.TECHNOLOGY,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=8,
            dependencies=large_dependencies
        )

        created = await repository.create(process)

        assert len(created.dependencies) == 100
        assert created.dependencies[0]["name"] == "System 0"
        assert created.dependencies[99]["name"] == "System 99"
