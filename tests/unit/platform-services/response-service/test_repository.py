"""
Response Module - Repository Layer Tests
ISO 22301:2019 Clause 8.4 - Incident Response

Unit tests for ResponseRepository database operations
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, Mock, patch

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import (
    IncidentDB, ResponseActionDB, ResponseTeamDB, ResponseTeamMemberDB,
    CommunicationLogDB, IncidentTimelineDB, RecoveryMetricsDB
)
from models.domain import (
    IncidentStatus, IncidentSeverity, IncidentType, IncidentListQuery,
    ActionStatus, ActionPriority
)
from repositories.repository import ResponseRepository


# ============================================================================
# Incident CRUD Tests
# ============================================================================

@pytest.mark.asyncio
class TestIncidentCRUD:
    """Test incident CRUD operations"""

    async def test_create_incident(self, mock_db_session, org_id, user_id, sample_incident_create):
        """Test creating a new incident"""
        # Arrange
        repo = ResponseRepository(mock_db_session)
        incident_number = "INC-2025-TEST-0001"
        detected_at = datetime.utcnow()

        # Mock the database response
        mock_incident = IncidentDB(
            id=uuid4(),
            organization_id=org_id,
            incident_number=incident_number,
            **sample_incident_create.model_dump()
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_incident.id)

        # Act
        result = await repo.create_incident(
            organization_id=org_id,
            incident_number=incident_number,
            incident_data=sample_incident_create,
            detected_at=detected_at,
            created_by=user_id
        )

        # Assert
        assert result is not None
        assert result.title == sample_incident_create.title
        assert result.severity == sample_incident_create.severity
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_get_incident(self, mock_db_session, incident_id):
        """Test getting incident by ID"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_incident = IncidentDB(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test Description",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.DETECTED,
            affected_systems=["system1"],
            detected_at=datetime.utcnow(),
            detected_by="Test User",
            actions=[],
            communications=[],
            timeline=[],
            metrics=[]
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_incident
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.get_incident(incident_id)

        # Assert
        assert result is not None
        assert result.id == incident_id
        assert result.title == "Test Incident"
        mock_db_session.execute.assert_awaited_once()

    async def test_get_incident_not_found(self, mock_db_session, incident_id):
        """Test getting non-existent incident returns None"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.get_incident(incident_id)

        # Assert
        assert result is None

    async def test_list_incidents_with_filters(self, mock_db_session, org_id):
        """Test listing incidents with filters"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        query_params = IncidentListQuery(
            organization_id=org_id,
            status=IncidentStatus.DETECTED,
            severity=IncidentSeverity.CRITICAL,
            skip=0,
            limit=10
        )

        mock_incidents = [
            IncidentDB(
                id=uuid4(),
                organization_id=org_id,
                incident_number=f"INC-2025-TEST-{i:04d}",
                title=f"Test Incident {i}",
                description="Test",
                incident_type=IncidentType.SYSTEM_FAILURE,
                severity=IncidentSeverity.CRITICAL,
                status=IncidentStatus.DETECTED,
                affected_systems=[],
                detected_at=datetime.utcnow(),
                detected_by="Test",
                actions=[],
                communications=[],
                timeline=[],
                metrics=[]
            )
            for i in range(3)
        ]

        # Mock count query
        count_result = MagicMock()
        count_result.scalar.return_value = 3

        # Mock list query
        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = mock_incidents

        mock_db_session.execute.side_effect = [count_result, list_result]

        # Act
        incidents, total = await repo.list_incidents(query_params)

        # Assert
        assert total == 3
        assert len(incidents) == 3
        assert all(inc.severity == IncidentSeverity.CRITICAL for inc in incidents)

    async def test_update_incident(self, mock_db_session, incident_id, user_id, sample_incident_update):
        """Test updating incident"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        # Mock get_incident to return updated incident
        mock_incident = IncidentDB(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title=sample_incident_update.title,
            description=sample_incident_update.description,
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=sample_incident_update.status,
            root_cause=sample_incident_update.root_cause,
            lessons_learned=sample_incident_update.lessons_learned,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            actions=[],
            communications=[],
            timeline=[],
            metrics=[]
        )

        mock_execute_result = MagicMock()
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_incident

        mock_db_session.execute.side_effect = [mock_execute_result, mock_get_result]

        # Act
        result = await repo.update_incident(
            incident_id=incident_id,
            incident_data=sample_incident_update,
            updated_by=user_id
        )

        # Assert
        assert result is not None
        assert result.title == sample_incident_update.title
        assert result.status == sample_incident_update.status
        mock_db_session.commit.assert_awaited()

    async def test_delete_incident(self, mock_db_session, incident_id):
        """Test deleting incident"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.delete_incident(incident_id)

        # Assert
        assert result is True
        mock_db_session.commit.assert_awaited_once()

    async def test_set_resolved_at(self, mock_db_session, incident_id):
        """Test setting incident resolved timestamp"""
        # Arrange
        repo = ResponseRepository(mock_db_session)
        resolved_at = datetime.utcnow()

        # Act
        await repo.set_resolved_at(incident_id, resolved_at)

        # Assert
        mock_db_session.execute.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_assign_team(self, mock_db_session, incident_id, team_id):
        """Test assigning team to incident"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_incident = IncidentDB(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.DETECTED,
            response_team_id=team_id,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            actions=[],
            communications=[],
            timeline=[],
            metrics=[]
        )

        mock_execute_result = MagicMock()
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_incident

        mock_db_session.execute.side_effect = [mock_execute_result, mock_get_result]

        # Act
        result = await repo.assign_team(incident_id, team_id)

        # Assert
        assert result is not None
        assert result.response_team_id == team_id


# ============================================================================
# Response Action Tests
# ============================================================================

@pytest.mark.asyncio
class TestResponseActions:
    """Test response action operations"""

    async def test_create_action(self, mock_db_session, incident_id, user_id, sample_action_create):
        """Test creating response action"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_action = ResponseActionDB(
            id=uuid4(),
            incident_id=incident_id,
            **sample_action_create.model_dump()
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_action.id)

        # Act
        result = await repo.create_action(
            incident_id=incident_id,
            action_data=sample_action_create,
            created_by=user_id
        )

        # Assert
        assert result is not None
        assert result.title == sample_action_create.title
        assert result.priority == sample_action_create.priority
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_get_action(self, mock_db_session, action_id, incident_id):
        """Test getting action by ID"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_action = ResponseActionDB(
            id=action_id,
            incident_id=incident_id,
            title="Test Action",
            description="Test",
            action_type="recovery",
            priority=ActionPriority.HIGH,
            status=ActionStatus.PENDING,
            assigned_to=uuid4(),
            assigned_to_name="Test User"
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_action
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.get_action(action_id)

        # Assert
        assert result is not None
        assert result.id == action_id
        assert result.title == "Test Action"

    async def test_list_actions(self, mock_db_session, incident_id):
        """Test listing actions for incident"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_actions = [
            ResponseActionDB(
                id=uuid4(),
                incident_id=incident_id,
                title=f"Action {i}",
                description="Test",
                action_type="recovery",
                priority=ActionPriority.HIGH,
                status=ActionStatus.PENDING,
                assigned_to=uuid4(),
                assigned_to_name="Test User"
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_actions
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.list_actions(incident_id)

        # Assert
        assert len(result) == 3
        assert all(action.incident_id == incident_id for action in result)

    async def test_update_action(self, mock_db_session, action_id, sample_action_update):
        """Test updating action"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_action = ResponseActionDB(
            id=action_id,
            incident_id=uuid4(),
            title="Test Action",
            description="Test",
            action_type="recovery",
            priority=ActionPriority.HIGH,
            status=sample_action_update.status,
            assigned_to=uuid4(),
            assigned_to_name="Test User",
            completion_notes=sample_action_update.completion_notes,
            actual_hours=sample_action_update.actual_hours
        )

        mock_execute_result = MagicMock()
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_action

        mock_db_session.execute.side_effect = [mock_execute_result, mock_get_result]

        # Act
        result = await repo.update_action(action_id, sample_action_update)

        # Assert
        assert result is not None
        assert result.status == sample_action_update.status
        mock_db_session.commit.assert_awaited()


# ============================================================================
# Response Team Tests
# ============================================================================

@pytest.mark.asyncio
class TestResponseTeams:
    """Test response team operations"""

    async def test_create_team(self, mock_db_session, org_id, user_id, sample_team_create):
        """Test creating response team"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_team = ResponseTeamDB(
            id=uuid4(),
            organization_id=org_id,
            name=sample_team_create.name,
            description=sample_team_create.description,
            is_active=sample_team_create.is_active,
            activation_criteria=sample_team_create.activation_criteria,
            escalation_procedures=sample_team_create.escalation_procedures,
            members=[]
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_team.id)

        # Act
        result = await repo.create_team(
            organization_id=org_id,
            team_data=sample_team_create,
            created_by=user_id
        )

        # Assert
        assert result is not None
        assert result.name == sample_team_create.name
        assert result.is_active == sample_team_create.is_active
        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_awaited_once()

    async def test_get_team(self, mock_db_session, team_id, org_id):
        """Test getting team by ID"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_team = ResponseTeamDB(
            id=team_id,
            organization_id=org_id,
            name="Test Team",
            description="Test",
            is_active=True,
            members=[]
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.get_team(team_id)

        # Assert
        assert result is not None
        assert result.id == team_id
        assert result.name == "Test Team"

    async def test_list_teams(self, mock_db_session, org_id):
        """Test listing teams for organization"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_teams = [
            ResponseTeamDB(
                id=uuid4(),
                organization_id=org_id,
                name=f"Team {i}",
                description="Test",
                is_active=True,
                members=[]
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_teams
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.list_teams(org_id)

        # Assert
        assert len(result) == 3
        assert all(team.organization_id == org_id for team in result)


# ============================================================================
# Communication Tests
# ============================================================================

@pytest.mark.asyncio
class TestCommunications:
    """Test communication log operations"""

    async def test_create_communication(self, mock_db_session, incident_id, user_id, sample_communication_create):
        """Test creating communication log"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_comm = CommunicationLogDB(
            id=uuid4(),
            incident_id=incident_id,
            **sample_communication_create.model_dump()
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_comm.id)

        # Act
        result = await repo.create_communication(
            incident_id=incident_id,
            communication_data=sample_communication_create,
            created_by=user_id
        )

        # Assert
        assert result is not None
        assert result.subject == sample_communication_create.subject
        assert result.communication_type == sample_communication_create.communication_type
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_list_communications(self, mock_db_session, incident_id):
        """Test listing communications for incident"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_comms = [
            CommunicationLogDB(
                id=uuid4(),
                incident_id=incident_id,
                communication_type=CommunicationType.EMAIL,
                subject=f"Communication {i}",
                content="Test",
                sender="test@example.com",
                recipients=["user@example.com"],
                channel="email"
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_comms
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.list_communications(incident_id)

        # Assert
        assert len(result) == 3
        assert all(comm.incident_id == incident_id for comm in result)


# ============================================================================
# Timeline Tests
# ============================================================================

@pytest.mark.asyncio
class TestTimeline:
    """Test incident timeline operations"""

    async def test_add_timeline_entry(self, mock_db_session, incident_id, user_id):
        """Test adding timeline entry"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_entry = IncidentTimelineDB(
            id=uuid4(),
            incident_id=incident_id,
            timestamp=datetime.utcnow(),
            event_type="incident_created",
            description="Incident created",
            actor="Test User",
            actor_id=user_id
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_entry.id)

        # Act
        result = await repo.add_timeline_entry(
            incident_id=incident_id,
            event_type="incident_created",
            description="Incident created",
            actor="Test User",
            actor_id=user_id
        )

        # Assert
        assert result is not None
        assert result.event_type == "incident_created"
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_get_timeline(self, mock_db_session, incident_id):
        """Test getting incident timeline"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_entries = [
            IncidentTimelineDB(
                id=uuid4(),
                incident_id=incident_id,
                timestamp=datetime.utcnow() - timedelta(minutes=i),
                event_type=f"event_{i}",
                description=f"Event {i}",
                actor="Test User"
            )
            for i in range(5)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_entries
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.get_timeline(incident_id)

        # Assert
        assert len(result) == 5
        assert all(entry.incident_id == incident_id for entry in result)


# ============================================================================
# Recovery Metrics Tests
# ============================================================================

@pytest.mark.asyncio
class TestRecoveryMetrics:
    """Test recovery metrics operations"""

    async def test_create_metrics(self, mock_db_session, incident_id, sample_metrics_create):
        """Test creating recovery metrics"""
        # Arrange
        repo = ResponseRepository(mock_db_session)

        mock_metrics = RecoveryMetricsDB(
            id=uuid4(),
            incident_id=incident_id,
            **sample_metrics_create.model_dump()
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_metrics.id)

        # Act
        result = await repo.create_metrics(incident_id, sample_metrics_create)

        # Assert
        assert result is not None
        assert result.service_name == sample_metrics_create.service_name
        assert result.target_rto_hours == sample_metrics_create.target_rto_hours
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_update_metrics_compliance(self, mock_db_session):
        """Test updating metrics compliance flags"""
        # Arrange
        repo = ResponseRepository(mock_db_session)
        metrics_id = uuid4()

        # Act
        await repo.update_metrics_compliance(
            metrics_id=metrics_id,
            rto_met=True,
            rpo_met=False
        )

        # Assert
        mock_db_session.execute.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()

    async def test_get_metrics_bulk(self, mock_db_session):
        """Test bulk metrics retrieval"""
        # Arrange
        repo = ResponseRepository(mock_db_session)
        incident_ids = [uuid4() for _ in range(3)]

        mock_metrics = [
            RecoveryMetricsDB(
                id=uuid4(),
                incident_id=incident_ids[0],
                service_name="Service A",
                target_rto_hours=4.0,
                target_rpo_hours=1.0,
                rto_met=True,
                rpo_met=True
            ),
            RecoveryMetricsDB(
                id=uuid4(),
                incident_id=incident_ids[0],
                service_name="Service B",
                target_rto_hours=2.0,
                target_rpo_hours=0.5,
                rto_met=False,
                rpo_met=True
            )
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_metrics
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await repo.get_metrics_bulk(incident_ids)

        # Assert
        assert incident_ids[0] in result
        assert len(result[incident_ids[0]]) == 2
