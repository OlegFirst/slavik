"""
Response Module - Data Access Repository
ISO 22301:2019 Clause 8.4 - Incident Response

Complete data access layer for all database operations
"""

from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
import logging

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.database import (
    IncidentDB, ResponseActionDB, ResponseTeamDB, ResponseTeamMemberDB,
    CommunicationLogDB, IncidentTimelineDB, RecoveryMetricsDB
)
from models.domain import (
    Incident, IncidentCreate, IncidentUpdate, IncidentListQuery, IncidentStatus,
    ResponseAction, ResponseActionCreate, ResponseActionUpdate,
    ResponseTeam, ResponseTeamCreate, ResponseTeamUpdate,
    ResponseTeamMember, ResponseTeamMemberCreate, ResponseTeamMemberUpdate,
    CommunicationLog, CommunicationLogCreate, CommunicationLogUpdate,
    IncidentTimelineEntry, RecoveryMetrics, RecoveryMetricsCreate, RecoveryMetricsUpdate
)

logger = logging.getLogger(__name__)


class ResponseRepository:
    """
    Data access repository for incident response

    Handles all database CRUD operations
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # Incident CRUD Operations
    # ========================================================================

    async def create_incident(
        self,
        organization_id: UUID,
        incident_number: str,
        incident_data: IncidentCreate,
        detected_at: datetime,
        created_by: Optional[UUID] = None
    ) -> Incident:
        """Create new incident"""
        db_incident = IncidentDB(
            organization_id=organization_id,
            incident_number=incident_number,
            title=incident_data.title,
            description=incident_data.description,
            incident_type=incident_data.incident_type,
            severity=incident_data.severity,
            status=IncidentStatus.DETECTED,
            affected_systems=incident_data.affected_systems,
            affected_locations=incident_data.affected_locations,
            estimated_impact=incident_data.estimated_impact,
            detected_at=detected_at,
            detected_by=incident_data.detected_by,
            root_cause=incident_data.root_cause,
            lessons_learned=incident_data.lessons_learned,
            external_reference=incident_data.external_reference,
            tags=incident_data.tags,
            created_by=created_by
        )

        self.db.add(db_incident)
        await self.db.commit()
        await self.db.refresh(db_incident)

        return self._map_incident_to_domain(db_incident)

    async def get_incident(self, incident_id: UUID) -> Optional[Incident]:
        """Get incident by ID with all relationships"""
        query = (
            select(IncidentDB)
            .where(IncidentDB.id == incident_id)
            .options(
                selectinload(IncidentDB.response_team).selectinload(ResponseTeamDB.members),
                selectinload(IncidentDB.actions),
                selectinload(IncidentDB.communications),
                selectinload(IncidentDB.timeline),
                selectinload(IncidentDB.metrics)
            )
        )

        result = await self.db.execute(query)
        db_incident = result.scalar_one_or_none()

        if db_incident:
            return self._map_incident_to_domain(db_incident)
        return None

    async def list_incidents(
        self,
        query_params: IncidentListQuery
    ) -> Tuple[List[Incident], int]:
        """List incidents with filters and pagination"""
        # Build base query
        query = select(IncidentDB)

        # Apply filters
        filters = []

        if query_params.organization_id:
            filters.append(IncidentDB.organization_id == query_params.organization_id)

        if query_params.status:
            filters.append(IncidentDB.status == query_params.status)

        if query_params.severity:
            filters.append(IncidentDB.severity == query_params.severity)

        if query_params.incident_type:
            filters.append(IncidentDB.incident_type == query_params.incident_type)

        if query_params.from_date:
            filters.append(IncidentDB.detected_at >= query_params.from_date)

        if query_params.to_date:
            filters.append(IncidentDB.detected_at <= query_params.to_date)

        if query_params.search:
            search_term = f"%{query_params.search}%"
            filters.append(
                or_(
                    IncidentDB.title.ilike(search_term),
                    IncidentDB.description.ilike(search_term),
                    IncidentDB.incident_number.ilike(search_term)
                )
            )

        if query_params.tags:
            # Filter by any of the tags
            filters.append(IncidentDB.tags.overlap(query_params.tags))

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = (
            query
            .options(
                selectinload(IncidentDB.response_team).selectinload(ResponseTeamDB.members),
                selectinload(IncidentDB.actions),
                selectinload(IncidentDB.communications),
                selectinload(IncidentDB.timeline),
                selectinload(IncidentDB.metrics)
            )
            .order_by(IncidentDB.detected_at.desc())
            .offset(query_params.skip)
            .limit(query_params.limit)
        )

        result = await self.db.execute(query)
        db_incidents = result.scalars().all()

        incidents = [self._map_incident_to_domain(db_incident) for db_incident in db_incidents]

        return incidents, total

    async def update_incident(
        self,
        incident_id: UUID,
        incident_data: IncidentUpdate,
        updated_by: Optional[UUID] = None
    ) -> Optional[Incident]:
        """Update incident"""
        # Build update dict with only provided fields
        update_dict = incident_data.model_dump(exclude_none=True)

        if not update_dict:
            return await self.get_incident(incident_id)

        # Add metadata
        update_dict["updated_at"] = datetime.utcnow()
        if updated_by:
            update_dict["updated_by"] = updated_by

        query = (
            update(IncidentDB)
            .where(IncidentDB.id == incident_id)
            .values(**update_dict)
        )

        await self.db.execute(query)
        await self.db.commit()

        return await self.get_incident(incident_id)

    async def delete_incident(self, incident_id: UUID) -> bool:
        """Delete incident (soft delete or hard delete)"""
        query = delete(IncidentDB).where(IncidentDB.id == incident_id)
        result = await self.db.execute(query)
        await self.db.commit()

        return result.rowcount > 0

    async def set_resolved_at(self, incident_id: UUID, resolved_at: datetime):
        """Set incident resolved timestamp"""
        query = (
            update(IncidentDB)
            .where(IncidentDB.id == incident_id)
            .values(resolved_at=resolved_at, updated_at=datetime.utcnow())
        )
        await self.db.execute(query)
        await self.db.commit()

    async def set_closed_at(self, incident_id: UUID, closed_at: datetime):
        """Set incident closed timestamp"""
        query = (
            update(IncidentDB)
            .where(IncidentDB.id == incident_id)
            .values(closed_at=closed_at, updated_at=datetime.utcnow())
        )
        await self.db.execute(query)
        await self.db.commit()

    async def update_incident_duration(self, incident_id: UUID, duration_hours: float):
        """Update incident duration"""
        query = (
            update(IncidentDB)
            .where(IncidentDB.id == incident_id)
            .values(duration_hours=duration_hours, updated_at=datetime.utcnow())
        )
        await self.db.execute(query)
        await self.db.commit()

    async def assign_team(self, incident_id: UUID, team_id: UUID) -> Optional[Incident]:
        """Assign response team to incident"""
        query = (
            update(IncidentDB)
            .where(IncidentDB.id == incident_id)
            .values(response_team_id=team_id, updated_at=datetime.utcnow())
        )
        await self.db.execute(query)
        await self.db.commit()

        return await self.get_incident(incident_id)

    # ========================================================================
    # Response Action CRUD Operations
    # ========================================================================

    async def create_action(
        self,
        incident_id: UUID,
        action_data: ResponseActionCreate,
        created_by: Optional[UUID] = None
    ) -> ResponseAction:
        """Create response action"""
        db_action = ResponseActionDB(
            incident_id=incident_id,
            title=action_data.title,
            description=action_data.description,
            action_type=action_data.action_type,
            priority=action_data.priority,
            assigned_to=action_data.assigned_to,
            assigned_to_name=action_data.assigned_to_name,
            due_date=action_data.due_date,
            estimated_hours=action_data.estimated_hours,
            dependencies=action_data.dependencies,
            checklist=action_data.checklist,
            created_by=created_by
        )

        self.db.add(db_action)
        await self.db.commit()
        await self.db.refresh(db_action)

        return self._map_action_to_domain(db_action)

    async def get_action(self, action_id: UUID) -> Optional[ResponseAction]:
        """Get action by ID"""
        query = select(ResponseActionDB).where(ResponseActionDB.id == action_id)
        result = await self.db.execute(query)
        db_action = result.scalar_one_or_none()

        if db_action:
            return self._map_action_to_domain(db_action)
        return None

    async def list_actions(self, incident_id: UUID) -> List[ResponseAction]:
        """List all actions for incident"""
        query = (
            select(ResponseActionDB)
            .where(ResponseActionDB.incident_id == incident_id)
            .order_by(ResponseActionDB.priority.desc(), ResponseActionDB.created_at)
        )

        result = await self.db.execute(query)
        db_actions = result.scalars().all()

        return [self._map_action_to_domain(db_action) for db_action in db_actions]

    async def update_action(
        self,
        action_id: UUID,
        action_data: ResponseActionUpdate
    ) -> Optional[ResponseAction]:
        """Update action"""
        update_dict = action_data.model_dump(exclude_none=True)

        if not update_dict:
            return await self.get_action(action_id)

        update_dict["updated_at"] = datetime.utcnow()

        query = (
            update(ResponseActionDB)
            .where(ResponseActionDB.id == action_id)
            .values(**update_dict)
        )

        await self.db.execute(query)
        await self.db.commit()

        return await self.get_action(action_id)

    async def set_action_completed(self, action_id: UUID, completed_at: datetime):
        """Set action completed timestamp"""
        query = (
            update(ResponseActionDB)
            .where(ResponseActionDB.id == action_id)
            .values(completed_at=completed_at, updated_at=datetime.utcnow())
        )
        await self.db.execute(query)
        await self.db.commit()

    # ========================================================================
    # Response Team CRUD Operations
    # ========================================================================

    async def create_team(
        self,
        organization_id: UUID,
        team_data: ResponseTeamCreate,
        created_by: Optional[UUID] = None
    ) -> ResponseTeam:
        """Create response team with members"""
        db_team = ResponseTeamDB(
            organization_id=organization_id,
            name=team_data.name,
            description=team_data.description,
            is_active=team_data.is_active,
            activation_criteria=team_data.activation_criteria,
            escalation_procedures=team_data.escalation_procedures,
            created_by=created_by
        )

        self.db.add(db_team)
        await self.db.flush()

        # Add members
        for member_data in team_data.members:
            db_member = ResponseTeamMemberDB(
                team_id=db_team.id,
                user_id=member_data.user_id,
                role=member_data.role,
                name=member_data.name,
                email=member_data.email,
                phone=member_data.phone,
                is_primary=member_data.is_primary,
                availability_status=member_data.availability_status,
                notes=member_data.notes
            )
            self.db.add(db_member)

        await self.db.commit()
        await self.db.refresh(db_team)

        return self._map_team_to_domain(db_team)

    async def get_team(self, team_id: UUID) -> Optional[ResponseTeam]:
        """Get team by ID with members"""
        query = (
            select(ResponseTeamDB)
            .where(ResponseTeamDB.id == team_id)
            .options(selectinload(ResponseTeamDB.members))
        )

        result = await self.db.execute(query)
        db_team = result.scalar_one_or_none()

        if db_team:
            return self._map_team_to_domain(db_team)
        return None

    async def list_teams(
        self,
        organization_id: UUID,
        is_active: Optional[bool] = None
    ) -> List[ResponseTeam]:
        """List teams for organization"""
        query = (
            select(ResponseTeamDB)
            .where(ResponseTeamDB.organization_id == organization_id)
            .options(selectinload(ResponseTeamDB.members))
        )

        if is_active is not None:
            query = query.where(ResponseTeamDB.is_active == is_active)

        query = query.order_by(ResponseTeamDB.name)

        result = await self.db.execute(query)
        db_teams = result.scalars().all()

        return [self._map_team_to_domain(db_team) for db_team in db_teams]

    async def update_team(
        self,
        team_id: UUID,
        team_data: ResponseTeamUpdate
    ) -> Optional[ResponseTeam]:
        """Update team"""
        update_dict = team_data.model_dump(exclude_none=True)

        if not update_dict:
            return await self.get_team(team_id)

        update_dict["updated_at"] = datetime.utcnow()

        query = (
            update(ResponseTeamDB)
            .where(ResponseTeamDB.id == team_id)
            .values(**update_dict)
        )

        await self.db.execute(query)
        await self.db.commit()

        return await self.get_team(team_id)

    async def add_team_member(
        self,
        team_id: UUID,
        member_data: ResponseTeamMemberCreate
    ) -> ResponseTeamMember:
        """Add member to team"""
        db_member = ResponseTeamMemberDB(
            team_id=team_id,
            user_id=member_data.user_id,
            role=member_data.role,
            name=member_data.name,
            email=member_data.email,
            phone=member_data.phone,
            is_primary=member_data.is_primary,
            availability_status=member_data.availability_status,
            notes=member_data.notes
        )

        self.db.add(db_member)
        await self.db.commit()
        await self.db.refresh(db_member)

        return self._map_team_member_to_domain(db_member)

    async def update_team_member(
        self,
        member_id: UUID,
        member_data: ResponseTeamMemberUpdate
    ) -> Optional[ResponseTeamMember]:
        """Update team member"""
        update_dict = member_data.model_dump(exclude_none=True)

        if not update_dict:
            query = select(ResponseTeamMemberDB).where(ResponseTeamMemberDB.id == member_id)
            result = await self.db.execute(query)
            db_member = result.scalar_one_or_none()
            if db_member:
                return self._map_team_member_to_domain(db_member)
            return None

        update_dict["updated_at"] = datetime.utcnow()

        query = (
            update(ResponseTeamMemberDB)
            .where(ResponseTeamMemberDB.id == member_id)
            .values(**update_dict)
        )

        await self.db.execute(query)
        await self.db.commit()

        # Get updated member
        query = select(ResponseTeamMemberDB).where(ResponseTeamMemberDB.id == member_id)
        result = await self.db.execute(query)
        db_member = result.scalar_one_or_none()

        if db_member:
            return self._map_team_member_to_domain(db_member)
        return None

    # ========================================================================
    # Communication Log CRUD Operations
    # ========================================================================

    async def create_communication(
        self,
        incident_id: UUID,
        communication_data: CommunicationLogCreate,
        created_by: Optional[UUID] = None
    ) -> CommunicationLog:
        """Create communication log"""
        db_communication = CommunicationLogDB(
            incident_id=incident_id,
            communication_type=communication_data.communication_type,
            subject=communication_data.subject,
            content=communication_data.content,
            sender=communication_data.sender,
            recipients=communication_data.recipients,
            cc_recipients=communication_data.cc_recipients,
            channel=communication_data.channel,
            is_stakeholder_notification=communication_data.is_stakeholder_notification,
            metadata=communication_data.metadata,
            created_by=created_by
        )

        self.db.add(db_communication)
        await self.db.commit()
        await self.db.refresh(db_communication)

        return self._map_communication_to_domain(db_communication)

    async def list_communications(self, incident_id: UUID) -> List[CommunicationLog]:
        """List all communications for incident"""
        query = (
            select(CommunicationLogDB)
            .where(CommunicationLogDB.incident_id == incident_id)
            .order_by(CommunicationLogDB.created_at.desc())
        )

        result = await self.db.execute(query)
        db_communications = result.scalars().all()

        return [self._map_communication_to_domain(db_comm) for db_comm in db_communications]

    # ========================================================================
    # Incident Timeline Operations
    # ========================================================================

    async def add_timeline_entry(
        self,
        incident_id: UUID,
        event_type: str,
        description: str,
        actor: Optional[str] = None,
        actor_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> IncidentTimelineEntry:
        """Add entry to incident timeline"""
        db_entry = IncidentTimelineDB(
            incident_id=incident_id,
            timestamp=timestamp or datetime.utcnow(),
            event_type=event_type,
            description=description,
            actor=actor,
            actor_id=actor_id,
            metadata=metadata
        )

        self.db.add(db_entry)
        await self.db.commit()
        await self.db.refresh(db_entry)

        return self._map_timeline_entry_to_domain(db_entry)

    async def get_timeline(self, incident_id: UUID) -> List[IncidentTimelineEntry]:
        """Get incident timeline"""
        query = (
            select(IncidentTimelineDB)
            .where(IncidentTimelineDB.incident_id == incident_id)
            .order_by(IncidentTimelineDB.timestamp.desc())
        )

        result = await self.db.execute(query)
        db_entries = result.scalars().all()

        return [self._map_timeline_entry_to_domain(db_entry) for db_entry in db_entries]

    # ========================================================================
    # Recovery Metrics CRUD Operations
    # ========================================================================

    async def create_metrics(
        self,
        incident_id: UUID,
        metrics_data: RecoveryMetricsCreate
    ) -> RecoveryMetrics:
        """Create recovery metrics"""
        db_metrics = RecoveryMetricsDB(
            incident_id=incident_id,
            service_name=metrics_data.service_name,
            target_rto_hours=metrics_data.target_rto_hours,
            target_rpo_hours=metrics_data.target_rpo_hours,
            actual_rto_hours=metrics_data.actual_rto_hours,
            actual_rpo_hours=metrics_data.actual_rpo_hours,
            downtime_start=metrics_data.downtime_start,
            downtime_end=metrics_data.downtime_end,
            data_loss_start=metrics_data.data_loss_start,
            data_loss_end=metrics_data.data_loss_end,
            impact_description=metrics_data.impact_description,
            recovery_actions=metrics_data.recovery_actions
        )

        self.db.add(db_metrics)
        await self.db.commit()
        await self.db.refresh(db_metrics)

        return self._map_metrics_to_domain(db_metrics)

    async def get_metrics(self, incident_id: UUID) -> List[RecoveryMetrics]:
        """Get all recovery metrics for incident"""
        query = (
            select(RecoveryMetricsDB)
            .where(RecoveryMetricsDB.incident_id == incident_id)
            .order_by(RecoveryMetricsDB.created_at)
        )

        result = await self.db.execute(query)
        db_metrics = result.scalars().all()

        return [self._map_metrics_to_domain(db_metric) for db_metric in db_metrics]

    async def update_metrics(
        self,
        metrics_id: UUID,
        metrics_data: RecoveryMetricsUpdate
    ) -> Optional[RecoveryMetrics]:
        """Update recovery metrics"""
        update_dict = metrics_data.model_dump(exclude_none=True)

        if not update_dict:
            query = select(RecoveryMetricsDB).where(RecoveryMetricsDB.id == metrics_id)
            result = await self.db.execute(query)
            db_metrics = result.scalar_one_or_none()
            if db_metrics:
                return self._map_metrics_to_domain(db_metrics)
            return None

        update_dict["updated_at"] = datetime.utcnow()

        query = (
            update(RecoveryMetricsDB)
            .where(RecoveryMetricsDB.id == metrics_id)
            .values(**update_dict)
        )

        await self.db.execute(query)
        await self.db.commit()

        # Get updated metrics
        query = select(RecoveryMetricsDB).where(RecoveryMetricsDB.id == metrics_id)
        result = await self.db.execute(query)
        db_metrics = result.scalar_one_or_none()

        if db_metrics:
            return self._map_metrics_to_domain(db_metrics)
        return None

    async def update_metrics_compliance(
        self,
        metrics_id: UUID,
        rto_met: Optional[bool] = None,
        rpo_met: Optional[bool] = None
    ):
        """Update metrics compliance flags"""
        update_dict = {"updated_at": datetime.utcnow()}

        if rto_met is not None:
            update_dict["rto_met"] = rto_met

        if rpo_met is not None:
            update_dict["rpo_met"] = rpo_met

        query = (
            update(RecoveryMetricsDB)
            .where(RecoveryMetricsDB.id == metrics_id)
            .values(**update_dict)
        )

        await self.db.execute(query)
        await self.db.commit()

    # ========================================================================
    # Bulk Query Methods (Performance Optimization)
    # ========================================================================

    async def get_metrics_bulk(self, incident_ids: List[UUID]) -> Dict[UUID, List[RecoveryMetrics]]:
        """Get metrics for multiple incidents in ONE query"""
        if not incident_ids:
            return {}

        query = (
            select(RecoveryMetricsDB)
            .where(RecoveryMetricsDB.incident_id.in_(incident_ids))
            .order_by(RecoveryMetricsDB.incident_id, RecoveryMetricsDB.created_at)
        )

        result = await self.db.execute(query)
        db_metrics_list = result.scalars().all()

        # Group by incident_id
        metrics_by_incident: Dict[UUID, List[RecoveryMetrics]] = {}
        for db_metric in db_metrics_list:
            incident_id = db_metric.incident_id
            if incident_id not in metrics_by_incident:
                metrics_by_incident[incident_id] = []
            metrics_by_incident[incident_id].append(self._map_metrics_to_domain(db_metric))

        return metrics_by_incident

    async def get_actions_count_bulk(self, incident_ids: List[UUID]) -> Dict[UUID, int]:
        """Get actions count for multiple incidents in ONE query"""
        if not incident_ids:
            return {}

        query = (
            select(
                ResponseActionDB.incident_id,
                func.count(ResponseActionDB.id).label("count")
            )
            .where(ResponseActionDB.incident_id.in_(incident_ids))
            .group_by(ResponseActionDB.incident_id)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return {row.incident_id: row.count for row in rows}

    async def get_communications_count_bulk(self, incident_ids: List[UUID]) -> Dict[UUID, int]:
        """Get communications count for multiple incidents in ONE query"""
        if not incident_ids:
            return {}

        query = (
            select(
                CommunicationLogDB.incident_id,
                func.count(CommunicationLogDB.id).label("count")
            )
            .where(CommunicationLogDB.incident_id.in_(incident_ids))
            .group_by(CommunicationLogDB.incident_id)
        )

        result = await self.db.execute(query)
        rows = result.all()

        return {row.incident_id: row.count for row in rows}

    async def list_incidents_light(
        self,
        query_params: IncidentListQuery
    ) -> Tuple[List[Incident], int]:
        """List incidents WITHOUT relationships - for performance in list views"""
        # Build base query
        query = select(IncidentDB)

        # Apply filters
        filters = []

        if query_params.organization_id:
            filters.append(IncidentDB.organization_id == query_params.organization_id)

        if query_params.status:
            filters.append(IncidentDB.status == query_params.status)

        if query_params.severity:
            filters.append(IncidentDB.severity == query_params.severity)

        if query_params.incident_type:
            filters.append(IncidentDB.incident_type == query_params.incident_type)

        if query_params.from_date:
            filters.append(IncidentDB.detected_at >= query_params.from_date)

        if query_params.to_date:
            filters.append(IncidentDB.detected_at <= query_params.to_date)

        if query_params.search:
            search_term = f"%{query_params.search}%"
            filters.append(
                or_(
                    IncidentDB.title.ilike(search_term),
                    IncidentDB.description.ilike(search_term),
                    IncidentDB.incident_number.ilike(search_term)
                )
            )

        if query_params.tags:
            filters.append(IncidentDB.tags.overlap(query_params.tags))

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering - NO selectinload
        query = (
            query
            .order_by(IncidentDB.detected_at.desc())
            .offset(query_params.skip)
            .limit(query_params.limit)
        )

        result = await self.db.execute(query)
        db_incidents = result.scalars().all()

        # Map to domain WITHOUT relationships
        incidents = []
        for db_incident in db_incidents:
            incident = Incident(
                id=db_incident.id,
                organization_id=db_incident.organization_id,
                incident_number=db_incident.incident_number,
                title=db_incident.title,
                description=db_incident.description,
                incident_type=db_incident.incident_type,
                severity=db_incident.severity,
                status=db_incident.status,
                affected_systems=db_incident.affected_systems or [],
                affected_locations=db_incident.affected_locations,
                estimated_impact=db_incident.estimated_impact,
                detected_at=db_incident.detected_at,
                detected_by=db_incident.detected_by,
                resolved_at=db_incident.resolved_at,
                closed_at=db_incident.closed_at,
                duration_hours=db_incident.duration_hours,
                root_cause=db_incident.root_cause,
                lessons_learned=db_incident.lessons_learned,
                external_reference=db_incident.external_reference,
                response_team_id=db_incident.response_team_id,
                response_team=None,  # No relationship loading
                actions=[],  # No relationship loading
                communications=[],  # No relationship loading
                timeline=[],  # No relationship loading
                metrics=[],  # No relationship loading
                tags=db_incident.tags,
                created_at=db_incident.created_at,
                updated_at=db_incident.updated_at,
                created_by=db_incident.created_by,
                updated_by=db_incident.updated_by
            )
            incidents.append(incident)

        return incidents, total

    # ========================================================================
    # Mapping Methods (Database -> Domain)
    # ========================================================================

    def _map_incident_to_domain(self, db_incident: IncidentDB) -> Incident:
        """Map database incident to domain model"""
        return Incident(
            id=db_incident.id,
            organization_id=db_incident.organization_id,
            incident_number=db_incident.incident_number,
            title=db_incident.title,
            description=db_incident.description,
            incident_type=db_incident.incident_type,
            severity=db_incident.severity,
            status=db_incident.status,
            affected_systems=db_incident.affected_systems or [],
            affected_locations=db_incident.affected_locations,
            estimated_impact=db_incident.estimated_impact,
            detected_at=db_incident.detected_at,
            detected_by=db_incident.detected_by,
            resolved_at=db_incident.resolved_at,
            closed_at=db_incident.closed_at,
            duration_hours=db_incident.duration_hours,
            root_cause=db_incident.root_cause,
            lessons_learned=db_incident.lessons_learned,
            external_reference=db_incident.external_reference,
            response_team_id=db_incident.response_team_id,
            response_team=self._map_team_to_domain(db_incident.response_team) if db_incident.response_team else None,
            actions=[self._map_action_to_domain(a) for a in db_incident.actions] if db_incident.actions else [],
            communications=[self._map_communication_to_domain(c) for c in db_incident.communications] if db_incident.communications else [],
            timeline=[self._map_timeline_entry_to_domain(t) for t in db_incident.timeline] if db_incident.timeline else [],
            metrics=[self._map_metrics_to_domain(m) for m in db_incident.metrics] if db_incident.metrics else [],
            tags=db_incident.tags,
            created_at=db_incident.created_at,
            updated_at=db_incident.updated_at,
            created_by=db_incident.created_by,
            updated_by=db_incident.updated_by
        )

    def _map_action_to_domain(self, db_action: ResponseActionDB) -> ResponseAction:
        """Map database action to domain model"""
        return ResponseAction(
            id=db_action.id,
            incident_id=db_action.incident_id,
            title=db_action.title,
            description=db_action.description,
            action_type=db_action.action_type,
            priority=db_action.priority,
            status=db_action.status,
            assigned_to=db_action.assigned_to,
            assigned_to_name=db_action.assigned_to_name,
            due_date=db_action.due_date,
            estimated_hours=db_action.estimated_hours,
            actual_hours=db_action.actual_hours,
            started_at=db_action.started_at,
            completed_at=db_action.completed_at,
            completion_notes=db_action.completion_notes,
            dependencies=db_action.dependencies,
            checklist=db_action.checklist,
            created_at=db_action.created_at,
            updated_at=db_action.updated_at,
            created_by=db_action.created_by
        )

    def _map_team_to_domain(self, db_team: ResponseTeamDB) -> ResponseTeam:
        """Map database team to domain model"""
        return ResponseTeam(
            id=db_team.id,
            organization_id=db_team.organization_id,
            name=db_team.name,
            description=db_team.description,
            is_active=db_team.is_active,
            activation_criteria=db_team.activation_criteria,
            escalation_procedures=db_team.escalation_procedures,
            members=[self._map_team_member_to_domain(m) for m in db_team.members] if db_team.members else [],
            created_at=db_team.created_at,
            updated_at=db_team.updated_at,
            created_by=db_team.created_by
        )

    def _map_team_member_to_domain(self, db_member: ResponseTeamMemberDB) -> ResponseTeamMember:
        """Map database team member to domain model"""
        return ResponseTeamMember(
            id=db_member.id,
            team_id=db_member.team_id,
            user_id=db_member.user_id,
            role=db_member.role,
            name=db_member.name,
            email=db_member.email,
            phone=db_member.phone,
            is_primary=db_member.is_primary,
            availability_status=db_member.availability_status,
            notes=db_member.notes,
            created_at=db_member.created_at,
            updated_at=db_member.updated_at
        )

    def _map_communication_to_domain(self, db_communication: CommunicationLogDB) -> CommunicationLog:
        """Map database communication to domain model"""
        return CommunicationLog(
            id=db_communication.id,
            incident_id=db_communication.incident_id,
            communication_type=db_communication.communication_type,
            subject=db_communication.subject,
            content=db_communication.content,
            sender=db_communication.sender,
            recipients=db_communication.recipients or [],
            cc_recipients=db_communication.cc_recipients,
            channel=db_communication.channel,
            is_stakeholder_notification=db_communication.is_stakeholder_notification,
            metadata=db_communication.metadata,
            created_at=db_communication.created_at,
            updated_at=db_communication.updated_at,
            created_by=db_communication.created_by
        )

    def _map_timeline_entry_to_domain(self, db_entry: IncidentTimelineDB) -> IncidentTimelineEntry:
        """Map database timeline entry to domain model"""
        return IncidentTimelineEntry(
            id=db_entry.id,
            incident_id=db_entry.incident_id,
            timestamp=db_entry.timestamp,
            event_type=db_entry.event_type,
            description=db_entry.description,
            actor=db_entry.actor,
            actor_id=db_entry.actor_id,
            metadata=db_entry.metadata,
            created_at=db_entry.created_at
        )

    def _map_metrics_to_domain(self, db_metrics: RecoveryMetricsDB) -> RecoveryMetrics:
        """Map database metrics to domain model"""
        return RecoveryMetrics(
            id=db_metrics.id,
            incident_id=db_metrics.incident_id,
            service_name=db_metrics.service_name,
            target_rto_hours=db_metrics.target_rto_hours,
            target_rpo_hours=db_metrics.target_rpo_hours,
            actual_rto_hours=db_metrics.actual_rto_hours,
            actual_rpo_hours=db_metrics.actual_rpo_hours,
            downtime_start=db_metrics.downtime_start,
            downtime_end=db_metrics.downtime_end,
            data_loss_start=db_metrics.data_loss_start,
            data_loss_end=db_metrics.data_loss_end,
            rto_met=db_metrics.rto_met,
            rpo_met=db_metrics.rpo_met,
            impact_description=db_metrics.impact_description,
            recovery_actions=db_metrics.recovery_actions,
            created_at=db_metrics.created_at,
            updated_at=db_metrics.updated_at
        )
