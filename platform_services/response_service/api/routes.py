"""
Response Module - API Routes
ISO 22301:2019 Clause 8.4 - Incident Response

All REST API endpoints for incident response management
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import sys
from pathlib import Path

# Add shared database to path
shared_db_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "platform-services" / "community-service" / "shared"
if str(shared_db_path) not in sys.path:
    sys.path.insert(0, str(shared_db_path))

# Add shared models to path
shared_models_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "shared"
if str(shared_models_path) not in sys.path:
    sys.path.insert(0, str(shared_models_path))

# Direct import from common module
import importlib.util
spec = importlib.util.spec_from_file_location("common", shared_models_path / "models" / "common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
User = common.User

from database import get_db

from models.domain import (
    Incident, IncidentCreate, IncidentUpdate, IncidentStatusChange,
    IncidentListResponse, IncidentListQuery, IncidentReport, IncidentDashboard,
    ResponseAction, ResponseActionCreate, ResponseActionUpdate,
    ResponseTeam, ResponseTeamCreate, ResponseTeamUpdate,
    CommunicationLog, CommunicationLogCreate, CommunicationLogUpdate,
    IncidentTimelineEntry, RecoveryMetrics, RecoveryMetricsCreate, RecoveryMetricsUpdate,
    OrganizationMetrics, IncidentEscalation, IncidentSeverity, IncidentStatus, IncidentType
)
from services.business_logic import ResponseService
from auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/response", tags=["Incident Response"])


# ============================================================================
# Dependency: Get Service
# ============================================================================

async def get_response_service(db: AsyncSession = Depends(get_db)) -> ResponseService:
    """Get ResponseService instance"""
    return ResponseService(db)


# ============================================================================
# Incident Endpoints
# ============================================================================

@router.post(
    "/incidents",
    response_model=Incident,
    status_code=status.HTTP_201_CREATED,
    summary="Create new incident"
)
async def create_incident(
    incident_data: IncidentCreate,
    current_user: User = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service)
) -> Incident:
    """
    Create a new incident record.

    ISO 22301:2019 Clause 8.4.3 - Incident response structure

    **Authentication**: Requires valid JWT token. Uses user's organization_id from token.
    """
    try:
        # Use organization_id and user_id from JWT token
        organization_id = UUID(current_user.tenant_id)
        current_user_id = UUID(current_user.user_id)

        return await service.create_incident(
            organization_id=organization_id,
            incident_data=incident_data,
            created_by=current_user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create incident: {str(e)}"
        )


@router.get(
    "/incidents",
    response_model=IncidentListResponse,
    summary="List incidents"
)
async def list_incidents(
    status_filter: Optional[IncidentStatus] = Query(None, description="Filter by status"),
    severity_filter: Optional[IncidentSeverity] = Query(None, description="Filter by severity"),
    incident_type_filter: Optional[IncidentType] = Query(None, description="Filter by type"),
    from_date: Optional[datetime] = Query(None, description="From date"),
    to_date: Optional[datetime] = Query(None, description="To date"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(20, ge=1, le=100, description="Limit records"),
    current_user: User = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service)
) -> IncidentListResponse:
    """
    List incidents with filters and pagination.

    **Authentication**: Requires valid JWT token. Returns incidents for user's organization only.
    """
    # Use organization_id from JWT token
    organization_id = UUID(current_user.tenant_id)

    query_params = IncidentListQuery(
        organization_id=organization_id,
        status=status_filter,
        severity=severity_filter,
        incident_type=incident_type_filter,
        from_date=from_date,
        to_date=to_date,
        search=search,
        skip=skip,
        limit=limit
    )

    return await service.list_incidents(query_params)


@router.get(
    "/incidents/{incident_id}",
    response_model=Incident,
    summary="Get incident details"
)
async def get_incident(
    incident_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service)
) -> Incident:
    """
    Get detailed incident information including actions, communications, and timeline.

    **Authentication**: Requires valid JWT token
    """
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
    return incident


@router.put(
    "/incidents/{incident_id}",
    response_model=Incident,
    summary="Update incident"
)
async def update_incident(
    incident_id: UUID,
    incident_data: IncidentUpdate,
    current_user: User = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service)
) -> Incident:
    """
    Update incident details.

    **Authentication**: Requires valid JWT token
    """
    try:
        # Use user_id from JWT token
        current_user_id = UUID(current_user.user_id)

        incident = await service.update_incident(
            incident_id=incident_id,
            incident_data=incident_data,
            updated_by=current_user_id
        )
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        return incident
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update incident: {str(e)}"
        )


@router.patch(
    "/incidents/{incident_id}/status",
    response_model=Incident,
    summary="Change incident status"
)
async def change_incident_status(
    incident_id: UUID,
    status_change: IncidentStatusChange,
    current_user_id: Optional[UUID] = Query(None, description="Current user ID"),
    service: ResponseService = Depends(get_response_service)
) -> Incident:
    """
    Change incident status with reason tracking.

    Status flow: detected → investigating → contained → resolved → closed
    """
    try:
        incident = await service.change_status(
            incident_id=incident_id,
            new_status=status_change.status,
            reason=status_change.reason,
            notes=status_change.notes,
            changed_by=current_user_id
        )
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        return incident
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change status: {str(e)}"
        )


@router.post(
    "/incidents/{incident_id}/resolve",
    response_model=Incident,
    summary="Resolve incident"
)
async def resolve_incident(
    incident_id: UUID,
    root_cause: Optional[str] = Query(None, description="Root cause analysis"),
    lessons_learned: Optional[str] = Query(None, description="Lessons learned"),
    current_user_id: Optional[UUID] = Query(None, description="Current user ID"),
    service: ResponseService = Depends(get_response_service)
) -> Incident:
    """
    Resolve incident with root cause and lessons learned.

    ISO 22301:2019 Clause 8.4.5 - Incident analysis
    """
    try:
        incident = await service.resolve_incident(
            incident_id=incident_id,
            root_cause=root_cause,
            lessons_learned=lessons_learned,
            resolved_by=current_user_id
        )
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        return incident
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve incident: {str(e)}"
        )


@router.post(
    "/incidents/{incident_id}/escalate",
    response_model=Incident,
    summary="Escalate incident"
)
async def escalate_incident(
    incident_id: UUID,
    escalation: IncidentEscalation,
    current_user_id: Optional[UUID] = Query(None, description="Current user ID"),
    service: ResponseService = Depends(get_response_service)
) -> Incident:
    """
    Escalate incident to higher severity or management level.

    ISO 22301:2019 Clause 8.4.2 - Incident escalation
    """
    try:
        incident = await service.escalate_incident(
            incident_id=incident_id,
            escalation_data=escalation,
            escalated_by=current_user_id
        )
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        return incident
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to escalate incident: {str(e)}"
        )


# ============================================================================
# Response Actions Endpoints
# ============================================================================

@router.post(
    "/incidents/{incident_id}/actions",
    response_model=ResponseAction,
    status_code=status.HTTP_201_CREATED,
    summary="Add response action"
)
async def add_response_action(
    incident_id: UUID,
    action_data: ResponseActionCreate,
    current_user_id: Optional[UUID] = Query(None, description="Current user ID"),
    service: ResponseService = Depends(get_response_service)
) -> ResponseAction:
    """
    Add a response action to an incident.
    """
    try:
        return await service.add_action(
            incident_id=incident_id,
            action_data=action_data,
            created_by=current_user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add action: {str(e)}"
        )


@router.get(
    "/incidents/{incident_id}/actions",
    response_model=List[ResponseAction],
    summary="List incident actions"
)
async def list_incident_actions(
    incident_id: UUID,
    service: ResponseService = Depends(get_response_service)
) -> List[ResponseAction]:
    """
    Get all actions for an incident.
    """
    return await service.list_actions(incident_id)


@router.put(
    "/actions/{action_id}",
    response_model=ResponseAction,
    summary="Update response action"
)
async def update_response_action(
    action_id: UUID,
    action_data: ResponseActionUpdate,
    service: ResponseService = Depends(get_response_service)
) -> ResponseAction:
    """
    Update a response action.
    """
    try:
        action = await service.update_action(action_id, action_data)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action {action_id} not found"
            )
        return action
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update action: {str(e)}"
        )


# ============================================================================
# Response Team Endpoints
# ============================================================================

@router.post(
    "/incidents/{incident_id}/team",
    response_model=Incident,
    summary="Assign response team"
)
async def assign_response_team(
    incident_id: UUID,
    team_id: UUID = Query(..., description="Response team ID"),
    current_user_id: Optional[UUID] = Query(None, description="Current user ID"),
    service: ResponseService = Depends(get_response_service)
) -> Incident:
    """
    Assign a response team to an incident.

    ISO 22301:2019 Clause 8.4.1 - Incident response team
    """
    try:
        incident = await service.assign_team(
            incident_id=incident_id,
            team_id=team_id,
            assigned_by=current_user_id
        )
        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        return incident
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign team: {str(e)}"
        )


@router.get(
    "/incidents/{incident_id}/team",
    response_model=Optional[ResponseTeam],
    summary="Get incident response team"
)
async def get_incident_team(
    incident_id: UUID,
    service: ResponseService = Depends(get_response_service)
) -> Optional[ResponseTeam]:
    """
    Get the response team assigned to an incident.
    """
    return await service.get_incident_team(incident_id)


@router.post(
    "/teams",
    response_model=ResponseTeam,
    status_code=status.HTTP_201_CREATED,
    summary="Create response team"
)
async def create_response_team(
    team_data: ResponseTeamCreate,
    current_user: User = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service)
) -> ResponseTeam:
    """
    Create a new response team for an organization.

    **Authentication**: Requires valid JWT token. Creates team for user's organization.
    """
    try:
        # Use organization_id and user_id from JWT token
        organization_id = UUID(current_user.tenant_id)
        current_user_id = UUID(current_user.user_id)

        return await service.create_team(
            organization_id=organization_id,
            team_data=team_data,
            created_by=current_user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create team: {str(e)}"
        )


@router.get(
    "/teams",
    response_model=List[ResponseTeam],
    summary="List response teams"
)
async def list_response_teams(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service)
) -> List[ResponseTeam]:
    """
    List all response teams for an organization.

    **Authentication**: Requires valid JWT token. Returns teams for user's organization only.
    """
    # Use organization_id from JWT token
    organization_id = UUID(current_user.tenant_id)
    return await service.list_teams(organization_id, is_active)


# ============================================================================
# Communication Endpoints
# ============================================================================

@router.post(
    "/incidents/{incident_id}/communications",
    response_model=CommunicationLog,
    status_code=status.HTTP_201_CREATED,
    summary="Log communication"
)
async def log_communication(
    incident_id: UUID,
    communication_data: CommunicationLogCreate,
    current_user_id: Optional[UUID] = Query(None, description="Current user ID"),
    service: ResponseService = Depends(get_response_service)
) -> CommunicationLog:
    """
    Log a communication related to an incident.

    ISO 22301:2019 Clause 7.4 - Communication
    """
    try:
        return await service.log_communication(
            incident_id=incident_id,
            communication_data=communication_data,
            created_by=current_user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log communication: {str(e)}"
        )


@router.get(
    "/incidents/{incident_id}/communications",
    response_model=List[CommunicationLog],
    summary="List incident communications"
)
async def list_incident_communications(
    incident_id: UUID,
    service: ResponseService = Depends(get_response_service)
) -> List[CommunicationLog]:
    """
    Get all communications for an incident.
    """
    return await service.list_communications(incident_id)


# ============================================================================
# Timeline Endpoints
# ============================================================================

@router.get(
    "/incidents/{incident_id}/timeline",
    response_model=List[IncidentTimelineEntry],
    summary="Get incident timeline"
)
async def get_incident_timeline(
    incident_id: UUID,
    service: ResponseService = Depends(get_response_service)
) -> List[IncidentTimelineEntry]:
    """
    Get chronological timeline of incident events.
    """
    return await service.get_timeline(incident_id)


# ============================================================================
# Recovery Metrics Endpoints
# ============================================================================

@router.post(
    "/incidents/{incident_id}/metrics",
    response_model=RecoveryMetrics,
    status_code=status.HTTP_201_CREATED,
    summary="Add recovery metrics"
)
async def add_recovery_metrics(
    incident_id: UUID,
    metrics_data: RecoveryMetricsCreate,
    service: ResponseService = Depends(get_response_service)
) -> RecoveryMetrics:
    """
    Add recovery metrics (RTO/RPO) for an incident.

    ISO 22301:2019 Clause 8.4.4 - Recovery time and point objectives
    """
    try:
        return await service.add_metrics(incident_id, metrics_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add metrics: {str(e)}"
        )


@router.put(
    "/metrics/{metrics_id}",
    response_model=RecoveryMetrics,
    summary="Update recovery metrics"
)
async def update_recovery_metrics(
    metrics_id: UUID,
    metrics_data: RecoveryMetricsUpdate,
    service: ResponseService = Depends(get_response_service)
) -> RecoveryMetrics:
    """
    Update recovery metrics.
    """
    try:
        metrics = await service.update_metrics(metrics_id, metrics_data)
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metrics {metrics_id} not found"
            )
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update metrics: {str(e)}"
        )


@router.get(
    "/incidents/{incident_id}/metrics",
    response_model=List[RecoveryMetrics],
    summary="Get incident metrics"
)
async def get_incident_metrics(
    incident_id: UUID,
    service: ResponseService = Depends(get_response_service)
) -> List[RecoveryMetrics]:
    """
    Get all recovery metrics for an incident.
    """
    return await service.get_metrics(incident_id)


# ============================================================================
# Reporting Endpoints
# ============================================================================

@router.get(
    "/incidents/{incident_id}/report",
    response_model=IncidentReport,
    summary="Generate incident report"
)
async def generate_incident_report(
    incident_id: UUID,
    service: ResponseService = Depends(get_response_service)
) -> IncidentReport:
    """
    Generate a comprehensive incident report.

    ISO 22301:2019 Clause 8.4.5 - Incident reporting
    """
    try:
        report = await service.generate_report(incident_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident {incident_id} not found"
            )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


# ============================================================================
# Dashboard & Metrics Endpoints
# ============================================================================

@router.get(
    "/dashboard",
    response_model=IncidentDashboard,
    summary="Get incident dashboard"
)
async def get_incident_dashboard(
    from_date: Optional[datetime] = Query(None, description="From date"),
    to_date: Optional[datetime] = Query(None, description="To date"),
    current_user: User = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service)
) -> IncidentDashboard:
    """
    Get incident response dashboard with statistics and trends.

    ISO 22301:2019 Clause 9.1 - Monitoring, measurement, analysis and evaluation

    **Authentication**: Requires valid JWT token. Returns dashboard for user's organization only.
    """
    try:
        # Use organization_id from JWT token
        organization_id = UUID(current_user.tenant_id)

        return await service.get_dashboard(
            organization_id=organization_id,
            from_date=from_date,
            to_date=to_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard: {str(e)}"
        )


@router.get(
    "/metrics",
    response_model=OrganizationMetrics,
    summary="Get organization metrics"
)
async def get_organization_metrics(
    current_user: User = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service)
) -> OrganizationMetrics:
    """
    Get organization-level incident response metrics.

    Includes: MTTR, MTBF, incident trends, RTO/RPO compliance

    **Authentication**: Requires valid JWT token. Returns metrics for user's organization only.
    """
    try:
        # Use organization_id from JWT token
        organization_id = UUID(current_user.tenant_id)

        return await service.calculate_metrics(organization_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate metrics: {str(e)}"
        )


# ============================================================================
# Health Check
# ============================================================================

@router.get(
    "/health",
    summary="Health check",
    tags=["Health"]
)
async def health_check(service: ResponseService = Depends(get_response_service)) -> dict:
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "response",
        "iso_standard": "ISO 22301:2019 Clause 8.4",
        "timestamp": datetime.utcnow().isoformat()
    }
