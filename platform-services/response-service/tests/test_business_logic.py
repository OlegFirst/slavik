"""
Response Module - Business Logic Tests
ISO 22301:2019 Clause 8.4 - Incident Response

Unit tests for ResponseService business logic
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call

from models.domain import (
    Incident, IncidentCreate, IncidentUpdate, IncidentStatus, IncidentSeverity,
    IncidentType, IncidentListQuery, IncidentEscalation, ActionStatus,
    ResponseAction, ResponseTeam
)
from services.business_logic import ResponseService
from repositories.repository import ResponseRepository


# ============================================================================
# Incident Management Tests
# ============================================================================

@pytest.mark.asyncio
class TestIncidentManagement:
    """Test incident management business logic"""

    async def test_create_incident_success(
        self, mock_db_session, org_id, user_id, sample_incident_create, mock_event_publisher
    ):
        """Test successful incident creation"""
        # Arrange
        service = ResponseService(mock_db_session)
        service.event_publisher = mock_event_publisher

        mock_incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            **sample_incident_create.model_dump(),
            status=IncidentStatus.DETECTED,
            detected_at=datetime.utcnow(),
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=sample_incident_create.tags or []
        )

        with patch.object(service.repository, 'create_incident', return_value=mock_incident) as mock_create, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline, \
             patch.object(service.repository, 'list_incidents', return_value=([], 0)) as mock_list:

            # Act
            result = await service.create_incident(
                organization_id=org_id,
                incident_data=sample_incident_create,
                created_by=user_id
            )

            # Assert
            assert result is not None
            assert result.incident_number == "INC-2025-TEST-0001"
            mock_create.assert_awaited_once()
            mock_timeline.assert_awaited_once()
            mock_event_publisher.publish_incident_created.assert_awaited_once_with(result)

    async def test_create_critical_incident_auto_escalates(
        self, mock_db_session, org_id, user_id, mock_event_publisher
    ):
        """Test critical incident triggers auto-escalation"""
        # Arrange
        service = ResponseService(mock_db_session)
        service.event_publisher = mock_event_publisher

        critical_incident_data = IncidentCreate(
            title="Critical Security Breach",
            description="Unauthorized access detected",
            incident_type=IncidentType.SECURITY_BREACH,
            severity=IncidentSeverity.CRITICAL,
            affected_systems=["auth-server"],
            detected_by="Security System"
        )

        mock_incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-CRIT-0001",
            **critical_incident_data.model_dump(),
            status=IncidentStatus.DETECTED,
            detected_at=datetime.utcnow(),
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.object(service.repository, 'create_incident', return_value=mock_incident), \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()), \
             patch.object(service.repository, 'list_incidents', return_value=([], 0)), \
             patch.object(service, 'escalate_incident', return_value=mock_incident) as mock_escalate:

            # Act
            result = await service.create_incident(
                organization_id=org_id,
                incident_data=critical_incident_data,
                created_by=user_id
            )

            # Assert
            assert result.severity == IncidentSeverity.CRITICAL
            mock_escalate.assert_awaited_once()

    async def test_get_incident(self, mock_db_session, incident_id):
        """Test getting incident by ID"""
        # Arrange
        service = ResponseService(mock_db_session)

        mock_incident = Incident(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.DETECTED,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.object(service.repository, 'get_incident', return_value=mock_incident) as mock_get:
            # Act
            result = await service.get_incident(incident_id)

            # Assert
            assert result is not None
            assert result.id == incident_id
            mock_get.assert_awaited_once_with(incident_id)

    async def test_list_incidents(self, mock_db_session, org_id):
        """Test listing incidents with pagination"""
        # Arrange
        service = ResponseService(mock_db_session)

        query = IncidentListQuery(
            organization_id=org_id,
            status=IncidentStatus.DETECTED,
            skip=0,
            limit=10
        )

        mock_incidents = [
            Incident(
                id=uuid4(),
                organization_id=org_id,
                incident_number=f"INC-2025-{i:04d}",
                title=f"Incident {i}",
                description="Test",
                incident_type=IncidentType.SYSTEM_FAILURE,
                severity=IncidentSeverity.HIGH,
                status=IncidentStatus.DETECTED,
                affected_systems=[],
                detected_at=datetime.utcnow(),
                detected_by="Test",
                response_team=None,
                actions=[],
                communications=[],
                timeline=[],
                metrics=[],
                tags=[]
            )
            for i in range(5)
        ]

        with patch.object(service.repository, 'list_incidents', return_value=(mock_incidents, 5)) as mock_list:
            # Act
            result = await service.list_incidents(query)

            # Assert
            assert result.total == 5
            assert len(result.items) == 5
            mock_list.assert_awaited_once_with(query)

    async def test_update_incident(
        self, mock_db_session, incident_id, user_id, sample_incident_update, mock_event_publisher
    ):
        """Test updating incident"""
        # Arrange
        service = ResponseService(mock_db_session)
        service.event_publisher = mock_event_publisher

        updated_incident = Incident(
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
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.object(service.repository, 'update_incident', return_value=updated_incident) as mock_update, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline:

            # Act
            result = await service.update_incident(
                incident_id=incident_id,
                incident_data=sample_incident_update,
                updated_by=user_id
            )

            # Assert
            assert result is not None
            assert result.title == sample_incident_update.title
            mock_update.assert_awaited_once()
            mock_timeline.assert_awaited_once()
            mock_event_publisher.publish_incident_updated.assert_awaited_once_with(result)


# ============================================================================
# Status Management Tests
# ============================================================================

@pytest.mark.asyncio
class TestStatusManagement:
    """Test incident status management"""

    async def test_change_status_success(
        self, mock_db_session, incident_id, user_id, mock_event_publisher
    ):
        """Test changing incident status"""
        # Arrange
        service = ResponseService(mock_db_session)
        service.event_publisher = mock_event_publisher

        old_incident = Incident(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.DETECTED,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        new_incident = Incident(**{**old_incident.model_dump(), 'status': IncidentStatus.INVESTIGATING})

        with patch.object(service.repository, 'get_incident', return_value=old_incident) as mock_get, \
             patch.object(service.repository, 'update_incident', return_value=new_incident) as mock_update, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline:

            # Act
            result = await service.change_status(
                incident_id=incident_id,
                new_status=IncidentStatus.INVESTIGATING,
                reason="Investigation started",
                changed_by=user_id
            )

            # Assert
            assert result is not None
            assert result.status == IncidentStatus.INVESTIGATING
            mock_timeline.assert_awaited_once()
            mock_event_publisher.publish_incident_status_changed.assert_awaited_once()

    async def test_resolve_incident(
        self, mock_db_session, incident_id, user_id, mock_event_publisher
    ):
        """Test resolving incident with root cause"""
        # Arrange
        service = ResponseService(mock_db_session)
        service.event_publisher = mock_event_publisher

        resolved_incident = Incident(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.RESOLVED,
            root_cause="Hardware failure",
            lessons_learned="Implement redundancy",
            affected_systems=[],
            detected_at=datetime.utcnow() - timedelta(hours=5),
            detected_by="Test",
            resolved_at=datetime.utcnow(),
            duration_hours=5.0,
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.object(service.repository, 'update_incident', return_value=resolved_incident) as mock_update, \
             patch.object(service.repository, 'set_resolved_at', return_value=AsyncMock()) as mock_resolved, \
             patch.object(service.repository, 'update_incident_duration', return_value=AsyncMock()) as mock_duration, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline, \
             patch.object(service.repository, 'get_metrics', return_value=[]) as mock_metrics:

            # Act
            result = await service.resolve_incident(
                incident_id=incident_id,
                root_cause="Hardware failure",
                lessons_learned="Implement redundancy",
                resolved_by=user_id
            )

            # Assert
            assert result is not None
            assert result.status == IncidentStatus.RESOLVED
            assert result.root_cause == "Hardware failure"
            mock_resolved.assert_awaited_once()
            mock_duration.assert_awaited_once()
            mock_event_publisher.publish_incident_resolved.assert_awaited_once_with(result)


# ============================================================================
# Escalation Tests
# ============================================================================

@pytest.mark.asyncio
class TestEscalation:
    """Test incident escalation"""

    async def test_escalate_incident(
        self, mock_db_session, incident_id, user_id, mock_event_publisher
    ):
        """Test escalating incident"""
        # Arrange
        service = ResponseService(mock_db_session)
        service.event_publisher = mock_event_publisher

        incident = Incident(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.INVESTIGATING,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        escalation_data = IncidentEscalation(
            escalation_reason="Issue not resolved in 4 hours",
            escalation_level="executive",
            notify_stakeholders=True,
            additional_notes="Requires executive attention"
        )

        with patch.object(service.repository, 'get_incident', return_value=incident) as mock_get, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline, \
             patch.object(service, 'notify_stakeholders', return_value=AsyncMock()) as mock_notify:

            # Act
            result = await service.escalate_incident(
                incident_id=incident_id,
                escalation_data=escalation_data,
                escalated_by=user_id
            )

            # Assert
            assert result is not None
            mock_timeline.assert_awaited_once()
            mock_notify.assert_awaited_once()
            mock_event_publisher.publish_incident_escalated.assert_awaited_once()


# ============================================================================
# Response Actions Tests
# ============================================================================

@pytest.mark.asyncio
class TestResponseActions:
    """Test response action management"""

    async def test_add_action(
        self, mock_db_session, incident_id, user_id, sample_action_create
    ):
        """Test adding response action"""
        # Arrange
        service = ResponseService(mock_db_session)

        mock_action = ResponseAction(
            id=uuid4(),
            incident_id=incident_id,
            **sample_action_create.model_dump(),
            status=ActionStatus.PENDING,
            created_at=datetime.utcnow()
        )

        with patch.object(service.repository, 'create_action', return_value=mock_action) as mock_create, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline:

            # Act
            result = await service.add_action(
                incident_id=incident_id,
                action_data=sample_action_create,
                created_by=user_id
            )

            # Assert
            assert result is not None
            assert result.title == sample_action_create.title
            mock_create.assert_awaited_once()
            mock_timeline.assert_awaited_once()

    async def test_update_action_to_completed(
        self, mock_db_session, action_id, sample_action_update
    ):
        """Test updating action to completed status"""
        # Arrange
        service = ResponseService(mock_db_session)

        mock_action = ResponseAction(
            id=action_id,
            incident_id=uuid4(),
            title="Test Action",
            description="Test",
            action_type="recovery",
            priority="high",
            status=ActionStatus.COMPLETED,
            assigned_to=uuid4(),
            assigned_to_name="Test User",
            completed_at=datetime.utcnow(),
            completion_notes=sample_action_update.completion_notes,
            actual_hours=sample_action_update.actual_hours,
            created_at=datetime.utcnow()
        )

        sample_action_update.status = ActionStatus.COMPLETED

        with patch.object(service.repository, 'update_action', return_value=mock_action) as mock_update, \
             patch.object(service.repository, 'set_action_completed', return_value=AsyncMock()) as mock_completed, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline:

            # Act
            result = await service.update_action(
                action_id=action_id,
                action_data=sample_action_update
            )

            # Assert
            assert result is not None
            assert result.status == ActionStatus.COMPLETED
            mock_completed.assert_awaited_once()


# ============================================================================
# Response Teams Tests
# ============================================================================

@pytest.mark.asyncio
class TestResponseTeams:
    """Test response team management"""

    async def test_create_team(
        self, mock_db_session, org_id, user_id, sample_team_create
    ):
        """Test creating response team"""
        # Arrange
        service = ResponseService(mock_db_session)

        mock_team = ResponseTeam(
            id=uuid4(),
            organization_id=org_id,
            **sample_team_create.model_dump(),
            created_at=datetime.utcnow()
        )

        with patch.object(service.repository, 'create_team', return_value=mock_team) as mock_create:
            # Act
            result = await service.create_team(
                organization_id=org_id,
                team_data=sample_team_create,
                created_by=user_id
            )

            # Assert
            assert result is not None
            assert result.name == sample_team_create.name
            mock_create.assert_awaited_once()

    async def test_assign_team(
        self, mock_db_session, incident_id, team_id, user_id
    ):
        """Test assigning team to incident"""
        # Arrange
        service = ResponseService(mock_db_session)

        mock_team = ResponseTeam(
            id=team_id,
            organization_id=uuid4(),
            name="Test Team",
            description="Test",
            is_active=True,
            members=[],
            created_at=datetime.utcnow()
        )

        mock_incident = Incident(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.DETECTED,
            response_team_id=team_id,
            response_team=mock_team,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.object(service.repository, 'assign_team', return_value=mock_incident) as mock_assign, \
             patch.object(service.repository, 'get_team', return_value=mock_team) as mock_get_team, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline:

            # Act
            result = await service.assign_team(
                incident_id=incident_id,
                team_id=team_id,
                assigned_by=user_id
            )

            # Assert
            assert result is not None
            assert result.response_team_id == team_id
            mock_assign.assert_awaited_once()
            mock_timeline.assert_awaited_once()


# ============================================================================
# Recovery Metrics Tests
# ============================================================================

@pytest.mark.asyncio
class TestRecoveryMetrics:
    """Test recovery metrics management"""

    async def test_add_metrics_rto_met(
        self, mock_db_session, incident_id, sample_metrics_create
    ):
        """Test adding metrics when RTO is met"""
        # Arrange
        service = ResponseService(mock_db_session)

        from models.domain import RecoveryMetrics

        mock_metrics = RecoveryMetrics(
            id=uuid4(),
            incident_id=incident_id,
            **sample_metrics_create.model_dump(),
            rto_met=True,
            rpo_met=True,
            created_at=datetime.utcnow()
        )

        with patch.object(service.repository, 'create_metrics', return_value=mock_metrics) as mock_create, \
             patch.object(service.repository, 'update_metrics_compliance', return_value=AsyncMock()) as mock_compliance, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()) as mock_timeline:

            # Act
            result = await service.add_metrics(
                incident_id=incident_id,
                metrics_data=sample_metrics_create
            )

            # Assert
            assert result is not None
            assert result.service_name == sample_metrics_create.service_name
            assert mock_compliance.call_count == 2  # Called for RTO and RPO

    async def test_add_metrics_rto_not_met(
        self, mock_db_session, incident_id
    ):
        """Test adding metrics when RTO is not met"""
        # Arrange
        service = ResponseService(mock_db_session)

        from models.domain import RecoveryMetrics, RecoveryMetricsCreate

        metrics_create = RecoveryMetricsCreate(
            service_name="Production API",
            target_rto_hours=2.0,
            target_rpo_hours=1.0,
            actual_rto_hours=4.0,  # Exceeded RTO
            actual_rpo_hours=0.5,  # Met RPO
            downtime_start=datetime.utcnow(),
            downtime_end=datetime.utcnow()
        )

        mock_metrics = RecoveryMetrics(
            id=uuid4(),
            incident_id=incident_id,
            **metrics_create.model_dump(),
            rto_met=False,
            rpo_met=True,
            created_at=datetime.utcnow()
        )

        with patch.object(service.repository, 'create_metrics', return_value=mock_metrics) as mock_create, \
             patch.object(service.repository, 'update_metrics_compliance', return_value=AsyncMock()) as mock_compliance, \
             patch.object(service.repository, 'add_timeline_entry', return_value=AsyncMock()):

            # Act
            result = await service.add_metrics(
                incident_id=incident_id,
                metrics_data=metrics_create
            )

            # Assert
            assert result is not None
            assert result.rto_met is False
            assert result.rpo_met is True


# ============================================================================
# Dashboard and Reporting Tests
# ============================================================================

@pytest.mark.asyncio
class TestDashboardAndReporting:
    """Test dashboard and reporting functionality"""

    async def test_generate_report(
        self, mock_db_session, incident_id
    ):
        """Test generating incident report"""
        # Arrange
        service = ResponseService(mock_db_session)

        mock_incident = Incident(
            id=incident_id,
            organization_id=uuid4(),
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.RESOLVED,
            duration_hours=5.0,
            affected_systems=["api-server"],
            detected_at=datetime.utcnow() - timedelta(hours=5),
            detected_by="Test",
            resolved_at=datetime.utcnow(),
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.object(service.repository, 'get_incident', return_value=mock_incident), \
             patch.object(service.repository, 'list_actions', return_value=[]), \
             patch.object(service.repository, 'list_communications', return_value=[]), \
             patch.object(service.repository, 'get_timeline', return_value=[]), \
             patch.object(service.repository, 'get_metrics', return_value=[]):

            # Act
            result = await service.generate_report(incident_id)

            # Assert
            assert result is not None
            assert result.incident.id == incident_id
            assert "incident_number" in result.summary
            assert "impact_analysis" in result.model_dump()

    async def test_get_dashboard(
        self, mock_db_session, org_id
    ):
        """Test getting dashboard statistics"""
        # Arrange
        service = ResponseService(mock_db_session)

        mock_incidents = [
            Incident(
                id=uuid4(),
                organization_id=org_id,
                incident_number=f"INC-2025-{i:04d}",
                title=f"Incident {i}",
                description="Test",
                incident_type=IncidentType.SYSTEM_FAILURE,
                severity=IncidentSeverity.HIGH if i % 2 == 0 else IncidentSeverity.CRITICAL,
                status=IncidentStatus.RESOLVED if i % 3 == 0 else IncidentStatus.INVESTIGATING,
                duration_hours=float(i + 1),
                affected_systems=[],
                detected_at=datetime.utcnow(),
                detected_by="Test",
                response_team=None,
                actions=[],
                communications=[],
                timeline=[],
                metrics=[],
                tags=[],
                created_at=datetime.utcnow()
            )
            for i in range(10)
        ]

        with patch.object(service.repository, 'list_incidents', return_value=(mock_incidents, 10)), \
             patch.object(service.repository, 'get_metrics_bulk', return_value={}):

            # Act
            result = await service.get_dashboard(
                organization_id=org_id,
                from_date=datetime.utcnow() - timedelta(days=30),
                to_date=datetime.utcnow()
            )

            # Assert
            assert result is not None
            assert result.total_incidents == 10
            assert result.critical_incidents > 0
            assert len(result.incidents_by_status) > 0

    async def test_calculate_metrics(
        self, mock_db_session, org_id
    ):
        """Test calculating organization metrics"""
        # Arrange
        service = ResponseService(mock_db_session)

        mock_incidents = [
            Incident(
                id=uuid4(),
                organization_id=org_id,
                incident_number=f"INC-2025-{i:04d}",
                title=f"Incident {i}",
                description="Test",
                incident_type=IncidentType.SYSTEM_FAILURE,
                severity=IncidentSeverity.HIGH,
                status=IncidentStatus.RESOLVED,
                duration_hours=float(i + 1),
                affected_systems=[],
                detected_at=datetime.utcnow() - timedelta(days=i),
                detected_by="Test",
                response_team=None,
                actions=[],
                communications=[],
                timeline=[],
                metrics=[],
                tags=[],
                created_at=datetime.utcnow() - timedelta(days=i)
            )
            for i in range(10)
        ]

        with patch.object(service.repository, 'list_incidents', return_value=(mock_incidents, 10)), \
             patch.object(service.repository, 'get_actions_count_bulk', return_value={}), \
             patch.object(service.repository, 'get_communications_count_bulk', return_value={}):

            # Act
            result = await service.calculate_metrics(org_id)

            # Assert
            assert result is not None
            assert result.total_incidents == 10
            assert result.mttr is not None
            assert result.avg_incident_duration_hours is not None
