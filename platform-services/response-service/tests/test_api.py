"""
Response Module - API Routes Tests
ISO 22301:2019 Clause 8.4 - Incident Response

Unit tests for REST API endpoints
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from fastapi import status as http_status
from fastapi.testclient import TestClient

from models.domain import (
    Incident, IncidentCreate, IncidentUpdate, IncidentStatus, IncidentSeverity,
    IncidentType, IncidentListResponse, IncidentStatusChange, IncidentEscalation,
    ResponseAction, ResponseTeam, CommunicationLog, RecoveryMetrics,
    IncidentDashboard, OrganizationMetrics, IncidentReport
)


# ============================================================================
# Test Client Setup
# ============================================================================

@pytest.fixture
def test_app():
    """Create test FastAPI application"""
    from fastapi import FastAPI
    from api.routes import router

    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def test_client(test_app):
    """Create test client"""
    return TestClient(test_app)


@pytest.fixture
def mock_service():
    """Create mock ResponseService"""
    service = AsyncMock()
    return service


@pytest.fixture
def auth_headers(user_id, org_id):
    """Create authentication headers"""
    return {
        "Authorization": f"Bearer mock_token_{user_id}",
        "X-User-ID": str(user_id),
        "X-Tenant-ID": str(org_id)
    }


# ============================================================================
# Incident Endpoints Tests
# ============================================================================

@pytest.mark.asyncio
class TestIncidentEndpoints:
    """Test incident API endpoints"""

    def test_create_incident_success(
        self, test_client, mock_user, sample_incident_create, org_id, user_id
    ):
        """Test POST /incidents - successful creation"""
        # Arrange
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
            tags=sample_incident_create.tags or [],
            created_at=datetime.utcnow()
        )

        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.create_incident.return_value = mock_incident
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.post(
                "/api/v1/response/incidents",
                json=sample_incident_create.model_dump(mode='json')
            )

            # Assert
            assert response.status_code == http_status.HTTP_201_CREATED
            data = response.json()
            assert data["incident_number"] == "INC-2025-TEST-0001"
            assert data["title"] == sample_incident_create.title

    def test_create_incident_unauthorized(self, test_client, sample_incident_create):
        """Test POST /incidents - unauthorized access"""
        # Arrange
        with patch('api.routes.get_current_user', side_effect=Exception("Unauthorized")):
            # Act
            response = test_client.post(
                "/api/v1/response/incidents",
                json=sample_incident_create.model_dump(mode='json')
            )

            # Assert
            assert response.status_code in [http_status.HTTP_401_UNAUTHORIZED, http_status.HTTP_500_INTERNAL_SERVER_ERROR]

    def test_list_incidents(self, test_client, mock_user, org_id):
        """Test GET /incidents - list with filters"""
        # Arrange
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
                tags=[],
                created_at=datetime.utcnow()
            )
            for i in range(5)
        ]

        mock_response = IncidentListResponse(
            items=mock_incidents,
            total=5,
            skip=0,
            limit=20
        )

        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.list_incidents.return_value = mock_response
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get(
                "/api/v1/response/incidents?status=detected&limit=20"
            )

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 5
            assert len(data["items"]) == 5

    def test_get_incident_by_id(self, test_client, mock_user, incident_id, org_id):
        """Test GET /incidents/{incident_id}"""
        # Arrange
        mock_incident = Incident(
            id=incident_id,
            organization_id=org_id,
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
            tags=[],
            created_at=datetime.utcnow()
        )

        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.get_incident.return_value = mock_incident
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get(f"/api/v1/response/incidents/{incident_id}")

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["id"] == str(incident_id)

    def test_get_incident_not_found(self, test_client, mock_user, incident_id):
        """Test GET /incidents/{incident_id} - not found"""
        # Arrange
        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.get_incident.return_value = None
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get(f"/api/v1/response/incidents/{incident_id}")

            # Assert
            assert response.status_code == http_status.HTTP_404_NOT_FOUND

    def test_update_incident(
        self, test_client, mock_user, incident_id, org_id, sample_incident_update
    ):
        """Test PUT /incidents/{incident_id}"""
        # Arrange
        updated_incident = Incident(
            id=incident_id,
            organization_id=org_id,
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
            tags=[],
            created_at=datetime.utcnow()
        )

        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.update_incident.return_value = updated_incident
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.put(
                f"/api/v1/response/incidents/{incident_id}",
                json=sample_incident_update.model_dump(mode='json', exclude_none=True)
            )

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["title"] == sample_incident_update.title

    def test_change_incident_status(self, test_client, incident_id, org_id):
        """Test PATCH /incidents/{incident_id}/status"""
        # Arrange
        status_change = IncidentStatusChange(
            status=IncidentStatus.INVESTIGATING,
            reason="Investigation started",
            notes="Initial assessment complete"
        )

        updated_incident = Incident(
            id=incident_id,
            organization_id=org_id,
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
            tags=[],
            created_at=datetime.utcnow()
        )

        with patch('api.routes.get_response_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.change_status.return_value = updated_incident
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.patch(
                f"/api/v1/response/incidents/{incident_id}/status",
                json=status_change.model_dump(mode='json')
            )

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["status"] == IncidentStatus.INVESTIGATING.value

    def test_resolve_incident(self, test_client, incident_id, org_id):
        """Test POST /incidents/{incident_id}/resolve"""
        # Arrange
        resolved_incident = Incident(
            id=incident_id,
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.RESOLVED,
            root_cause="Hardware failure",
            lessons_learned="Implement redundancy",
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            resolved_at=datetime.utcnow(),
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[],
            created_at=datetime.utcnow()
        )

        with patch('api.routes.get_response_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.resolve_incident.return_value = resolved_incident
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.post(
                f"/api/v1/response/incidents/{incident_id}/resolve",
                params={
                    "root_cause": "Hardware failure",
                    "lessons_learned": "Implement redundancy"
                }
            )

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["status"] == IncidentStatus.RESOLVED.value
            assert data["root_cause"] == "Hardware failure"

    def test_escalate_incident(self, test_client, incident_id, org_id):
        """Test POST /incidents/{incident_id}/escalate"""
        # Arrange
        escalation = IncidentEscalation(
            escalation_reason="Critical issue requires executive attention",
            escalation_level="executive",
            notify_stakeholders=True
        )

        escalated_incident = Incident(
            id=incident_id,
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.INVESTIGATING,
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

        with patch('api.routes.get_response_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.escalate_incident.return_value = escalated_incident
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.post(
                f"/api/v1/response/incidents/{incident_id}/escalate",
                json=escalation.model_dump(mode='json')
            )

            # Assert
            assert response.status_code == http_status.HTTP_200_OK


# ============================================================================
# Response Action Endpoints Tests
# ============================================================================

@pytest.mark.asyncio
class TestResponseActionEndpoints:
    """Test response action API endpoints"""

    def test_add_response_action(
        self, test_client, incident_id, sample_action_create
    ):
        """Test POST /incidents/{incident_id}/actions"""
        # Arrange
        mock_action = ResponseAction(
            id=uuid4(),
            incident_id=incident_id,
            **sample_action_create.model_dump(),
            status="pending",
            created_at=datetime.utcnow()
        )

        with patch('api.routes.get_response_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.add_action.return_value = mock_action
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.post(
                f"/api/v1/response/incidents/{incident_id}/actions",
                json=sample_action_create.model_dump(mode='json')
            )

            # Assert
            assert response.status_code == http_status.HTTP_201_CREATED
            data = response.json()
            assert data["title"] == sample_action_create.title

    def test_list_incident_actions(self, test_client, incident_id):
        """Test GET /incidents/{incident_id}/actions"""
        # Arrange
        mock_actions = [
            ResponseAction(
                id=uuid4(),
                incident_id=incident_id,
                title=f"Action {i}",
                description="Test",
                action_type="recovery",
                priority="high",
                status="pending",
                assigned_to=uuid4(),
                assigned_to_name="Test User",
                created_at=datetime.utcnow()
            )
            for i in range(3)
        ]

        with patch('api.routes.get_response_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.list_actions.return_value = mock_actions
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get(
                f"/api/v1/response/incidents/{incident_id}/actions"
            )

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert len(data) == 3


# ============================================================================
# Response Team Endpoints Tests
# ============================================================================

@pytest.mark.asyncio
class TestResponseTeamEndpoints:
    """Test response team API endpoints"""

    def test_create_response_team(
        self, test_client, mock_user, org_id, sample_team_create
    ):
        """Test POST /teams"""
        # Arrange
        mock_team = ResponseTeam(
            id=uuid4(),
            organization_id=org_id,
            **sample_team_create.model_dump(),
            created_at=datetime.utcnow()
        )

        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.create_team.return_value = mock_team
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.post(
                "/api/v1/response/teams",
                json=sample_team_create.model_dump(mode='json')
            )

            # Assert
            assert response.status_code == http_status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == sample_team_create.name

    def test_list_response_teams(self, test_client, mock_user, org_id):
        """Test GET /teams"""
        # Arrange
        mock_teams = [
            ResponseTeam(
                id=uuid4(),
                organization_id=org_id,
                name=f"Team {i}",
                description="Test",
                is_active=True,
                members=[],
                created_at=datetime.utcnow()
            )
            for i in range(3)
        ]

        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.list_teams.return_value = mock_teams
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get("/api/v1/response/teams")

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert len(data) == 3

    def test_assign_response_team(self, test_client, incident_id, team_id, org_id):
        """Test POST /incidents/{incident_id}/team"""
        # Arrange
        mock_incident = Incident(
            id=incident_id,
            organization_id=org_id,
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
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[],
            created_at=datetime.utcnow()
        )

        with patch('api.routes.get_response_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.assign_team.return_value = mock_incident
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.post(
                f"/api/v1/response/incidents/{incident_id}/team?team_id={team_id}"
            )

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["response_team_id"] == str(team_id)


# ============================================================================
# Dashboard and Metrics Endpoints Tests
# ============================================================================

@pytest.mark.asyncio
class TestDashboardEndpoints:
    """Test dashboard and metrics API endpoints"""

    def test_get_incident_dashboard(self, test_client, mock_user, org_id):
        """Test GET /dashboard"""
        # Arrange
        mock_dashboard = IncidentDashboard(
            organization_id=org_id,
            total_incidents=50,
            active_incidents=10,
            critical_incidents=3,
            incidents_by_status={"detected": 5, "investigating": 5},
            incidents_by_severity={"high": 7, "critical": 3},
            incidents_by_type={"system_failure": 10},
            avg_resolution_hours=4.5,
            recent_incidents=[],
            trending_types=[],
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            generated_at=datetime.utcnow()
        )

        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.get_dashboard.return_value = mock_dashboard
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get("/api/v1/response/dashboard")

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["total_incidents"] == 50
            assert data["active_incidents"] == 10

    def test_get_organization_metrics(self, test_client, mock_user, org_id):
        """Test GET /metrics"""
        # Arrange
        mock_metrics = OrganizationMetrics(
            organization_id=org_id,
            total_incidents=100,
            total_actions=250,
            total_communications=150,
            avg_incident_duration_hours=5.2,
            avg_actions_per_incident=2.5,
            incidents_this_month=15,
            incidents_last_month=12,
            trend_percentage=25.0,
            mttr=4.8,
            mtbf=168.0,
            calculated_at=datetime.utcnow()
        )

        with patch('api.routes.get_current_user', return_value=mock_user), \
             patch('api.routes.get_response_service') as mock_get_service:

            mock_service = AsyncMock()
            mock_service.calculate_metrics.return_value = mock_metrics
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get("/api/v1/response/metrics")

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["total_incidents"] == 100
            assert data["mttr"] == 4.8

    def test_generate_incident_report(self, test_client, incident_id, org_id):
        """Test GET /incidents/{incident_id}/report"""
        # Arrange
        mock_incident = Incident(
            id=incident_id,
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.RESOLVED,
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

        mock_report = IncidentReport(
            incident=mock_incident,
            summary={"incident_number": "INC-2025-TEST-0001"},
            impact_analysis={"severity": "high"},
            timeline_summary=[],
            actions_summary={"total_actions": 0},
            metrics_summary={"total_services": 0},
            recommendations=[],
            generated_at=datetime.utcnow()
        )

        with patch('api.routes.get_response_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.generate_report.return_value = mock_report
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get(
                f"/api/v1/response/incidents/{incident_id}/report"
            )

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert "incident" in data
            assert "summary" in data


# ============================================================================
# Health Check Tests
# ============================================================================

@pytest.mark.asyncio
class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self, test_client):
        """Test GET /health"""
        # Arrange
        with patch('api.routes.get_response_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_get_service.return_value = mock_service

            # Act
            response = test_client.get("/api/v1/response/health")

            # Assert
            assert response.status_code == http_status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "response"
