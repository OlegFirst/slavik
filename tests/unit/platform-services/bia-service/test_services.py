"""
Test BIA Service Layer
Tests for business logic, caching, events, and audit logging
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from models.domain import BIAProcess, BIAProcessCreate
from models.enums import CriticalityLevel, ProcessStatus
from models.database import BIAProcessDB
from repositories.bia_repository import BIARepository
from services.bia_service import BIAService
from shared.exceptions import EntityNotFoundError, TenantMismatchError


class TestBIAServiceCreate:
    """Test BIA Service create operations"""

    @pytest.fixture
    async def bia_service(self, db_session, mock_audit_logger):
        """Create BIA service instance"""
        repository = BIARepository(db_session)
        return BIAService(repository, mock_audit_logger)

    async def test_should_create_process_with_all_fields(
        self,
        bia_service: BIAService,
        sample_bia_create_data: BIAProcessCreate,
        user_id: str
    ):
        """Test creating BIA process with all fields populated"""
        with patch('services.bia_service.publish_event', new=AsyncMock()):
            created = await bia_service.create_process(
                data=sample_bia_create_data,
                user_id=user_id
            )

        assert created.id is not None
        assert created.name == sample_bia_create_data.name
        assert created.criticality == sample_bia_create_data.criticality
        assert created.criticality_score is not None
        assert created.rto_hours == sample_bia_create_data.rto_hours

    async def test_should_calculate_criticality_score_on_create(
        self,
        bia_service: BIAService,
        sample_bia_create_data: BIAProcessCreate,
        user_id: str
    ):
        """Test criticality score is auto-calculated"""
        with patch('services.bia_service.publish_event', new=AsyncMock()):
            created = await bia_service.create_process(
                data=sample_bia_create_data,
                user_id=user_id
            )

        # CRITICAL should have score of 5
        assert created.criticality == CriticalityLevel.CRITICAL
        assert created.criticality_score == 5

    async def test_should_auto_calculate_who_tier_for_healthcare(
        self,
        bia_service: BIAService,
        sample_healthcare_bia_create: BIAProcessCreate,
        user_id: str
    ):
        """Test WHO tier is auto-calculated for healthcare processes"""
        with patch('services.bia_service.publish_event', new=AsyncMock()):
            created = await bia_service.create_process(
                data=sample_healthcare_bia_create,
                user_id=user_id
            )

        assert created.who_tier is not None
        # Critical healthcare with RTO <= 2 hours should be Tier 1
        assert created.who_tier.value in ["tier_1_immediate", "tier_2_critical"]

    async def test_should_publish_event_on_create(
        self,
        bia_service: BIAService,
        sample_bia_create_data: BIAProcessCreate,
        user_id: str
    ):
        """Test event is published when process created"""
        mock_publish = AsyncMock()
        with patch('services.bia_service.publish_event', new=mock_publish):
            created = await bia_service.create_process(
                data=sample_bia_create_data,
                user_id=user_id
            )

        # Verify event was published
        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[0][0] == "bcm.bia.started"
        assert call_args[0][1]["tenant_id"] == sample_bia_create_data.tenant_id
        assert call_args[0][1]["bia_process_id"] == created.id

    async def test_should_log_audit_on_create(
        self,
        bia_service: BIAService,
        sample_bia_create_data: BIAProcessCreate,
        user_id: str,
        mock_audit_logger
    ):
        """Test audit log is created"""
        with patch('services.bia_service.publish_event', new=AsyncMock()):
            created = await bia_service.create_process(
                data=sample_bia_create_data,
                user_id=user_id
            )

        # Verify audit log was called
        mock_audit_logger.log_create.assert_called_once()
        call_args = mock_audit_logger.log_create.call_args
        assert call_args[1]["user_id"] == user_id
        assert call_args[1]["tenant_id"] == sample_bia_create_data.tenant_id
        assert call_args[1]["entity_type"] == "BIAProcess"


class TestBIAServiceRead:
    """Test BIA Service read operations"""

    @pytest.fixture
    async def bia_service(self, db_session, mock_audit_logger):
        """Create BIA service instance"""
        repository = BIARepository(db_session)
        return BIAService(repository, mock_audit_logger)

    async def test_should_get_process_by_id(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str
    ):
        """Test retrieving process by ID"""
        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            retrieved = await bia_service.get_process(
                process_id=sample_bia_process_db.id,
                tenant_id=tenant_id
            )

        assert retrieved.id == sample_bia_process_db.id
        assert retrieved.name == sample_bia_process_db.name

    async def test_should_raise_not_found_for_invalid_id(
        self,
        bia_service: BIAService,
        tenant_id: str
    ):
        """Test EntityNotFoundError for non-existent process"""
        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            with pytest.raises(EntityNotFoundError) as exc_info:
                await bia_service.get_process(
                    process_id=99999,
                    tenant_id=tenant_id
                )

        assert "BIAProcess" in str(exc_info.value)
        assert "99999" in str(exc_info.value)

    async def test_should_raise_tenant_mismatch_error(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB
    ):
        """Test TenantMismatchError for wrong tenant"""
        wrong_tenant = "wrong-tenant-999"
        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            with pytest.raises(TenantMismatchError) as exc_info:
                await bia_service.get_process(
                    process_id=sample_bia_process_db.id,
                    tenant_id=wrong_tenant
                )

        assert wrong_tenant in str(exc_info.value)

    async def test_should_list_all_processes_for_tenant(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str
    ):
        """Test listing all processes"""
        processes = await bia_service.list_processes(tenant_id)

        assert len(processes) >= 1
        assert all(p.tenant_id == tenant_id for p in processes)

    async def test_should_filter_processes_by_criticality(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str
    ):
        """Test filtering by criticality"""
        processes = await bia_service.list_processes(
            tenant_id=tenant_id,
            criticality=CriticalityLevel.HIGH
        )

        assert all(p.criticality == CriticalityLevel.HIGH for p in processes)

    async def test_should_filter_processes_by_status(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str
    ):
        """Test filtering by status"""
        processes = await bia_service.list_processes(
            tenant_id=tenant_id,
            status=ProcessStatus.DRAFT
        )

        assert all(p.status == ProcessStatus.DRAFT for p in processes)


class TestBIAServiceUpdate:
    """Test BIA Service update operations"""

    @pytest.fixture
    async def bia_service(self, db_session, mock_audit_logger):
        """Create BIA service instance"""
        repository = BIARepository(db_session)
        return BIAService(repository, mock_audit_logger)

    async def test_should_update_process_fields(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str,
        user_id: str
    ):
        """Test updating process fields"""
        updates = {
            "rto_hours": 2,
            "rpo_hours": 0,
            "name": "Updated Name"
        }

        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            updated = await bia_service.update_process(
                process_id=sample_bia_process_db.id,
                tenant_id=tenant_id,
                updates=updates,
                user_id=user_id
            )

        assert updated.rto_hours == 2
        assert updated.rpo_hours == 0
        assert updated.name == "Updated Name"

    async def test_should_recalculate_who_tier_on_update(
        self,
        bia_service: BIAService,
        db_session,
        tenant_id: str,
        user_id: str,
        mock_audit_logger
    ):
        """Test WHO tier recalculation when relevant fields change"""
        # Create healthcare process
        from models.enums import IndustryType, PatientSafetyImpact
        repository = BIARepository(db_session)
        healthcare_process = BIAProcessDB(
            tenant_id=tenant_id,
            name="Healthcare Process",
            criticality=CriticalityLevel.CRITICAL.value,
            industry=IndustryType.HEALTHCARE.value,
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=8,
            patient_safety_impact=PatientSafetyImpact.LIFE_THREATENING.value,
            status=ProcessStatus.DRAFT.value
        )
        db_session.add(healthcare_process)
        await db_session.commit()
        await db_session.refresh(healthcare_process)

        service = BIAService(repository, mock_audit_logger)

        # Update RTO (should trigger WHO tier recalculation)
        updates = {"rto_hours": 1}

        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            updated = await service.update_process(
                process_id=healthcare_process.id,
                tenant_id=tenant_id,
                updates=updates,
                user_id=user_id
            )

        # WHO tier should be calculated
        assert updated.who_tier is not None

    async def test_should_invalidate_cache_on_update(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str,
        user_id: str
    ):
        """Test cache invalidation after update"""
        mock_cache = AsyncMock()
        updates = {"name": "New Name"}

        with patch('services.bia_service.get_cache', return_value=mock_cache):
            await bia_service.update_process(
                process_id=sample_bia_process_db.id,
                tenant_id=tenant_id,
                updates=updates,
                user_id=user_id
            )

        # Verify cache delete was called
        mock_cache.delete.assert_called_once()

    async def test_should_log_audit_on_update(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str,
        user_id: str,
        mock_audit_logger
    ):
        """Test audit logging on update"""
        updates = {"rto_hours": 2}

        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            await bia_service.update_process(
                process_id=sample_bia_process_db.id,
                tenant_id=tenant_id,
                updates=updates,
                user_id=user_id
            )

        # Verify audit log was called
        mock_audit_logger.log_update.assert_called_once()


class TestBIAServiceDelete:
    """Test BIA Service delete operations"""

    @pytest.fixture
    async def bia_service(self, db_session, mock_audit_logger):
        """Create BIA service instance"""
        repository = BIARepository(db_session)
        return BIAService(repository, mock_audit_logger)

    async def test_should_delete_process(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str,
        user_id: str
    ):
        """Test deleting a process"""
        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            result = await bia_service.delete_process(
                process_id=sample_bia_process_db.id,
                tenant_id=tenant_id,
                user_id=user_id
            )

        assert result["status"] == "deleted"
        assert result["process_id"] == sample_bia_process_db.id

    async def test_should_log_audit_on_delete(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str,
        user_id: str,
        mock_audit_logger
    ):
        """Test audit logging on delete"""
        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            await bia_service.delete_process(
                process_id=sample_bia_process_db.id,
                tenant_id=tenant_id,
                user_id=user_id
            )

        # Verify audit log was called BEFORE delete
        mock_audit_logger.log_delete.assert_called_once()


class TestBIAServiceComplete:
    """Test BIA Service completion workflow"""

    @pytest.fixture
    async def bia_service(self, db_session, mock_audit_logger):
        """Create BIA service instance"""
        repository = BIARepository(db_session)
        return BIAService(repository, mock_audit_logger)

    async def test_should_complete_process(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str,
        user_id: str
    ):
        """Test marking process as completed"""
        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            with patch('services.bia_service.publish_event', new=AsyncMock()) as mock_publish:
                result = await bia_service.complete_process(
                    process_id=sample_bia_process_db.id,
                    tenant_id=tenant_id,
                    user_id=user_id
                )

        assert result["status"] == "completed"
        assert result["process"].status == ProcessStatus.COMPLETED
        assert result["process"].completed_at is not None

    async def test_should_publish_completion_event(
        self,
        bia_service: BIAService,
        sample_bia_process_db: BIAProcessDB,
        tenant_id: str,
        user_id: str
    ):
        """Test completion event is published"""
        mock_publish = AsyncMock()
        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            with patch('services.bia_service.publish_event', new=mock_publish):
                await bia_service.complete_process(
                    process_id=sample_bia_process_db.id,
                    tenant_id=tenant_id,
                    user_id=user_id
                )

        # Should publish at least completion event
        assert mock_publish.call_count >= 1
        first_call = mock_publish.call_args_list[0]
        assert first_call[0][0] == "bcm.bia.completed"

    async def test_should_publish_critical_process_event(
        self,
        bia_service: BIAService,
        db_session,
        tenant_id: str,
        user_id: str,
        mock_audit_logger
    ):
        """Test critical process event for high criticality"""
        # Create critical process
        repository = BIARepository(db_session)
        critical_process = BIAProcessDB(
            tenant_id=tenant_id,
            name="Critical Process",
            criticality=CriticalityLevel.CRITICAL.value,
            criticality_score=5,
            rto_hours=2,
            rpo_hours=0,
            mtpd_hours=4,
            status=ProcessStatus.DRAFT.value
        )
        db_session.add(critical_process)
        await db_session.commit()
        await db_session.refresh(critical_process)

        service = BIAService(repository, mock_audit_logger)
        mock_publish = AsyncMock()

        with patch('services.bia_service.get_cache', return_value=AsyncMock()):
            with patch('services.bia_service.publish_event', new=mock_publish):
                await service.complete_process(
                    process_id=critical_process.id,
                    tenant_id=tenant_id,
                    user_id=user_id
                )

        # Should publish both completion and critical process events
        assert mock_publish.call_count == 2
        events = [call[0][0] for call in mock_publish.call_args_list]
        assert "bcm.bia.completed" in events
        assert "bcm.bia.critical_process_identified" in events
