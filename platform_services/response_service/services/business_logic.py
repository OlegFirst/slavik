"""
Response Module - Business Logic Service
ISO 22301:2019 Clause 8.4 - Incident Response

Complete business logic for incident response management
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from models.domain import (
    Incident, IncidentCreate, IncidentUpdate, IncidentStatus, IncidentSeverity,
    IncidentListQuery, IncidentListResponse, IncidentReport, IncidentDashboard,
    ResponseAction, ResponseActionCreate, ResponseActionUpdate,
    ResponseTeam, ResponseTeamCreate, ResponseTeamUpdate,
    CommunicationLog, CommunicationLogCreate, CommunicationLogUpdate,
    IncidentTimelineEntry, RecoveryMetrics, RecoveryMetricsCreate, RecoveryMetricsUpdate,
    OrganizationMetrics, IncidentEscalation, ActionStatus
)
from repositories.repository import ResponseRepository
from events.publishers import ResponseEventPublisher
from services.transactions import transaction

logger = logging.getLogger(__name__)


class ResponseService:
    """
    Business logic service for incident response management

    Implements ISO 22301:2019 Clause 8.4 - Incident response
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ResponseRepository(db)
        self.event_publisher = ResponseEventPublisher()

    # ========================================================================
    # Incident Management
    # ========================================================================

    async def create_incident(
        self,
        organization_id: UUID,
        incident_data: IncidentCreate,
        created_by: Optional[UUID] = None
    ) -> Incident:
        """
        Create a new incident

        ISO 22301:2019 Clause 8.4.3 - Incident response structure
        """
        try:
            # Generate incident number
            incident_number = await self._generate_incident_number(organization_id)

            # Set detected_at if not provided
            detected_at = incident_data.detected_at or datetime.utcnow()

            # Use transaction to ensure atomic operation
            async with transaction(self.db):
                # Create incident
                incident = await self.repository.create_incident(
                    organization_id=organization_id,
                    incident_number=incident_number,
                    incident_data=incident_data,
                    detected_at=detected_at,
                    created_by=created_by
                )

                # Create initial timeline entry
                await self.repository.add_timeline_entry(
                    incident_id=incident.id,
                    event_type="incident_created",
                    description=f"Incident created: {incident.title}",
                    actor=incident_data.detected_by,
                    actor_id=created_by,
                    metadata={"severity": incident.severity.value, "type": incident.incident_type.value}
                )

                # Auto-escalate if critical (within same transaction)
                if incident.severity == IncidentSeverity.CRITICAL:
                    await self._auto_escalate_critical(incident)

            # After successful commit - publish events
            await self.event_publisher.publish_incident_created(incident)

            logger.info(f"Incident {incident.incident_number} created for org {organization_id}")
            return incident

        except Exception as e:
            logger.error(f"Failed to create incident: {e}")
            raise

    async def get_incident(self, incident_id: UUID) -> Optional[Incident]:
        """Get incident by ID with all related data"""
        return await self.repository.get_incident(incident_id)

    async def list_incidents(self, query: IncidentListQuery) -> IncidentListResponse:
        """List incidents with filters and pagination"""
        incidents, total = await self.repository.list_incidents(query)

        return IncidentListResponse(
            items=incidents,
            total=total,
            skip=query.skip,
            limit=query.limit
        )

    async def update_incident(
        self,
        incident_id: UUID,
        incident_data: IncidentUpdate,
        updated_by: Optional[UUID] = None
    ) -> Optional[Incident]:
        """Update incident details"""
        try:
            incident = await self.repository.update_incident(
                incident_id=incident_id,
                incident_data=incident_data,
                updated_by=updated_by
            )

            if incident:
                # Add timeline entry
                await self.repository.add_timeline_entry(
                    incident_id=incident_id,
                    event_type="incident_updated",
                    description="Incident details updated",
                    actor_id=updated_by,
                    metadata=incident_data.model_dump(exclude_none=True)
                )

                # Publish event
                await self.event_publisher.publish_incident_updated(incident)

            return incident

        except Exception as e:
            logger.error(f"Failed to update incident {incident_id}: {e}")
            raise

    async def change_status(
        self,
        incident_id: UUID,
        new_status: IncidentStatus,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        changed_by: Optional[UUID] = None
    ) -> Optional[Incident]:
        """
        Change incident status

        Status flow: detected → investigating → contained → resolved → closed
        """
        try:
            incident = await self.repository.get_incident(incident_id)
            if not incident:
                return None

            old_status = incident.status

            # Update status
            incident = await self.repository.update_incident(
                incident_id=incident_id,
                incident_data=IncidentUpdate(status=new_status),
                updated_by=changed_by
            )

            # Add timeline entry
            description = f"Status changed from {old_status.value} to {new_status.value}"
            if reason:
                description += f": {reason}"

            await self.repository.add_timeline_entry(
                incident_id=incident_id,
                event_type="status_changed",
                description=description,
                actor_id=changed_by,
                metadata={
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "reason": reason,
                    "notes": notes
                }
            )

            # Handle status-specific actions
            if new_status == IncidentStatus.RESOLVED:
                await self._handle_incident_resolved(incident)
            elif new_status == IncidentStatus.CLOSED:
                await self._handle_incident_closed(incident)

            # Publish event
            await self.event_publisher.publish_incident_status_changed(
                incident, old_status, new_status
            )

            logger.info(f"Incident {incident.incident_number} status changed to {new_status.value}")
            return incident

        except Exception as e:
            logger.error(f"Failed to change incident status: {e}")
            raise

    async def resolve_incident(
        self,
        incident_id: UUID,
        root_cause: Optional[str] = None,
        lessons_learned: Optional[str] = None,
        resolved_by: Optional[UUID] = None
    ) -> Optional[Incident]:
        """
        Resolve incident with root cause analysis

        ISO 22301:2019 Clause 8.4.5 - Incident analysis
        """
        try:
            resolved_at = datetime.utcnow()

            # Use transaction to ensure atomic operation
            async with transaction(self.db):
                # Update incident
                update_data = IncidentUpdate(
                    status=IncidentStatus.RESOLVED,
                    root_cause=root_cause,
                    lessons_learned=lessons_learned
                )

                incident = await self.repository.update_incident(
                    incident_id=incident_id,
                    incident_data=update_data,
                    updated_by=resolved_by
                )

                if incident:
                    # Set resolved timestamp
                    await self.repository.set_resolved_at(incident_id, resolved_at)

                    # Calculate duration
                    duration_hours = await self._calculate_incident_duration(incident)
                    await self.repository.update_incident_duration(incident_id, duration_hours)

                    # Add timeline entry
                    await self.repository.add_timeline_entry(
                        incident_id=incident_id,
                        event_type="incident_resolved",
                        description="Incident resolved",
                        actor_id=resolved_by,
                        metadata={
                            "duration_hours": duration_hours,
                            "root_cause_provided": root_cause is not None,
                            "lessons_learned_provided": lessons_learned is not None
                        }
                    )

                    # Calculate and validate metrics
                    await self._validate_recovery_metrics(incident)

            # After successful commit - publish event
            if incident:
                await self.event_publisher.publish_incident_resolved(incident)
                logger.info(f"Incident {incident.incident_number} resolved after {duration_hours:.2f} hours")

            return incident

        except Exception as e:
            logger.error(f"Failed to resolve incident: {e}")
            raise

    async def escalate_incident(
        self,
        incident_id: UUID,
        escalation_data: IncidentEscalation,
        escalated_by: Optional[UUID] = None
    ) -> Optional[Incident]:
        """
        Escalate incident to higher severity or management

        ISO 22301:2019 Clause 8.4.2 - Incident escalation
        """
        try:
            incident = await self.repository.get_incident(incident_id)
            if not incident:
                return None

            # Add timeline entry
            await self.repository.add_timeline_entry(
                incident_id=incident_id,
                event_type="incident_escalated",
                description=f"Incident escalated: {escalation_data.escalation_reason}",
                actor_id=escalated_by,
                metadata={
                    "escalation_level": escalation_data.escalation_level,
                    "escalate_to": [str(uid) for uid in escalation_data.escalate_to] if escalation_data.escalate_to else [],
                    "notes": escalation_data.additional_notes
                }
            )

            # Notify stakeholders if requested
            if escalation_data.notify_stakeholders:
                await self.notify_stakeholders(
                    incident=incident,
                    message=f"Incident escalated to {escalation_data.escalation_level}: {escalation_data.escalation_reason}",
                    escalate_to=escalation_data.escalate_to
                )

            # Publish event
            await self.event_publisher.publish_incident_escalated(incident, escalation_data)

            logger.info(f"Incident {incident.incident_number} escalated to {escalation_data.escalation_level}")
            return incident

        except Exception as e:
            logger.error(f"Failed to escalate incident: {e}")
            raise

    # ========================================================================
    # Response Actions
    # ========================================================================

    async def add_action(
        self,
        incident_id: UUID,
        action_data: ResponseActionCreate,
        created_by: Optional[UUID] = None
    ) -> ResponseAction:
        """Add response action to incident"""
        try:
            # Use transaction to ensure atomic operation
            async with transaction(self.db):
                action = await self.repository.create_action(
                    incident_id=incident_id,
                    action_data=action_data,
                    created_by=created_by
                )

                # Add timeline entry
                await self.repository.add_timeline_entry(
                    incident_id=incident_id,
                    event_type="action_added",
                    description=f"Action added: {action.title}",
                    actor_id=created_by,
                    metadata={
                        "action_id": str(action.id),
                        "priority": action.priority.value,
                        "assigned_to": str(action.assigned_to) if action.assigned_to else None
                    }
                )

            logger.info(f"Action {action.id} added to incident {incident_id}")
            return action

        except Exception as e:
            logger.error(f"Failed to add action: {e}")
            raise

    async def list_actions(self, incident_id: UUID) -> List[ResponseAction]:
        """List all actions for an incident"""
        return await self.repository.list_actions(incident_id)

    async def update_action(
        self,
        action_id: UUID,
        action_data: ResponseActionUpdate
    ) -> Optional[ResponseAction]:
        """Update response action"""
        try:
            # Use transaction to ensure atomic operation
            async with transaction(self.db):
                action = await self.repository.update_action(action_id, action_data)

                if action:
                    # If status changed to completed, set completion timestamp
                    if action_data.status == ActionStatus.COMPLETED and not action.completed_at:
                        await self.repository.set_action_completed(action_id, datetime.utcnow())

                    # Add timeline entry
                    await self.repository.add_timeline_entry(
                        incident_id=action.incident_id,
                        event_type="action_updated",
                        description=f"Action updated: {action.title}",
                        metadata={
                            "action_id": str(action.id),
                            "status": action.status.value
                        }
                    )

            return action

        except Exception as e:
            logger.error(f"Failed to update action: {e}")
            raise

    # ========================================================================
    # Response Teams
    # ========================================================================

    async def create_team(
        self,
        organization_id: UUID,
        team_data: ResponseTeamCreate,
        created_by: Optional[UUID] = None
    ) -> ResponseTeam:
        """Create response team"""
        try:
            team = await self.repository.create_team(
                organization_id=organization_id,
                team_data=team_data,
                created_by=created_by
            )

            logger.info(f"Response team {team.id} created for org {organization_id}")
            return team

        except Exception as e:
            logger.error(f"Failed to create team: {e}")
            raise

    async def list_teams(
        self,
        organization_id: UUID,
        is_active: Optional[bool] = None
    ) -> List[ResponseTeam]:
        """List response teams"""
        return await self.repository.list_teams(organization_id, is_active)

    async def assign_team(
        self,
        incident_id: UUID,
        team_id: UUID,
        assigned_by: Optional[UUID] = None
    ) -> Optional[Incident]:
        """
        Assign response team to incident

        ISO 22301:2019 Clause 8.4.1 - Incident response team
        """
        try:
            # Use transaction to ensure atomic operation
            async with transaction(self.db):
                incident = await self.repository.assign_team(incident_id, team_id)

                if incident:
                    team = await self.repository.get_team(team_id)

                    # Add timeline entry
                    await self.repository.add_timeline_entry(
                        incident_id=incident_id,
                        event_type="team_assigned",
                        description=f"Response team assigned: {team.name if team else 'Unknown'}",
                        actor_id=assigned_by,
                        metadata={"team_id": str(team_id)}
                    )

            if incident:
                logger.info(f"Team {team_id} assigned to incident {incident_id}")

            return incident

        except Exception as e:
            logger.error(f"Failed to assign team: {e}")
            raise

    async def get_incident_team(self, incident_id: UUID) -> Optional[ResponseTeam]:
        """Get response team for incident"""
        incident = await self.repository.get_incident(incident_id)
        if incident and incident.response_team_id:
            return await self.repository.get_team(incident.response_team_id)
        return None

    # ========================================================================
    # Communications
    # ========================================================================

    async def log_communication(
        self,
        incident_id: UUID,
        communication_data: CommunicationLogCreate,
        created_by: Optional[UUID] = None
    ) -> CommunicationLog:
        """
        Log communication related to incident

        ISO 22301:2019 Clause 7.4 - Communication
        """
        try:
            communication = await self.repository.create_communication(
                incident_id=incident_id,
                communication_data=communication_data,
                created_by=created_by
            )

            # Add timeline entry
            await self.repository.add_timeline_entry(
                incident_id=incident_id,
                event_type="communication_logged",
                description=f"Communication: {communication.subject}",
                actor=communication.sender,
                actor_id=created_by,
                metadata={
                    "communication_id": str(communication.id),
                    "type": communication.communication_type.value,
                    "recipients_count": len(communication.recipients)
                }
            )

            logger.info(f"Communication {communication.id} logged for incident {incident_id}")
            return communication

        except Exception as e:
            logger.error(f"Failed to log communication: {e}")
            raise

    async def list_communications(self, incident_id: UUID) -> List[CommunicationLog]:
        """List all communications for incident"""
        return await self.repository.list_communications(incident_id)

    # ========================================================================
    # Timeline
    # ========================================================================

    async def get_timeline(self, incident_id: UUID) -> List[IncidentTimelineEntry]:
        """Get incident timeline"""
        return await self.repository.get_timeline(incident_id)

    # ========================================================================
    # Recovery Metrics
    # ========================================================================

    async def add_metrics(
        self,
        incident_id: UUID,
        metrics_data: RecoveryMetricsCreate
    ) -> RecoveryMetrics:
        """
        Add recovery metrics (RTO/RPO)

        ISO 22301:2019 Clause 8.4.4 - Recovery time and point objectives
        """
        try:
            # Use transaction to ensure atomic operation
            async with transaction(self.db):
                metrics = await self.repository.create_metrics(incident_id, metrics_data)

                # Calculate if objectives were met
                if metrics_data.actual_rto_hours is not None:
                    rto_met = metrics_data.actual_rto_hours <= metrics_data.target_rto_hours
                    await self.repository.update_metrics_compliance(metrics.id, rto_met=rto_met)

                if metrics_data.actual_rpo_hours is not None:
                    rpo_met = metrics_data.actual_rpo_hours <= metrics_data.target_rpo_hours
                    await self.repository.update_metrics_compliance(metrics.id, rpo_met=rpo_met)

                # Add timeline entry
                await self.repository.add_timeline_entry(
                    incident_id=incident_id,
                    event_type="metrics_added",
                    description=f"Recovery metrics added for {metrics.service_name}",
                    metadata={
                        "metrics_id": str(metrics.id),
                        "service": metrics.service_name,
                        "target_rto": metrics.target_rto_hours,
                        "target_rpo": metrics.target_rpo_hours
                    }
                )

            logger.info(f"Metrics {metrics.id} added for incident {incident_id}")
            return metrics

        except Exception as e:
            logger.error(f"Failed to add metrics: {e}")
            raise

    async def update_metrics(
        self,
        metrics_id: UUID,
        metrics_data: RecoveryMetricsUpdate
    ) -> Optional[RecoveryMetrics]:
        """Update recovery metrics"""
        try:
            metrics = await self.repository.update_metrics(metrics_id, metrics_data)

            if metrics:
                # Recalculate compliance
                if metrics_data.actual_rto_hours is not None:
                    rto_met = metrics_data.actual_rto_hours <= metrics.target_rto_hours
                    await self.repository.update_metrics_compliance(metrics_id, rto_met=rto_met)

                if metrics_data.actual_rpo_hours is not None:
                    rpo_met = metrics_data.actual_rpo_hours <= metrics.target_rpo_hours
                    await self.repository.update_metrics_compliance(metrics_id, rpo_met=rpo_met)

            return metrics

        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            raise

    async def get_metrics(self, incident_id: UUID) -> List[RecoveryMetrics]:
        """Get all recovery metrics for incident"""
        return await self.repository.get_metrics(incident_id)

    # ========================================================================
    # Reports & Analytics
    # ========================================================================

    async def generate_report(self, incident_id: UUID) -> Optional[IncidentReport]:
        """
        Generate comprehensive incident report

        ISO 22301:2019 Clause 8.4.5 - Incident reporting
        """
        try:
            incident = await self.repository.get_incident(incident_id)
            if not incident:
                return None

            # Get all related data
            actions = await self.repository.list_actions(incident_id)
            communications = await self.repository.list_communications(incident_id)
            timeline = await self.repository.get_timeline(incident_id)
            metrics = await self.repository.get_metrics(incident_id)

            # Build summary
            summary = {
                "incident_number": incident.incident_number,
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "detected_at": incident.detected_at.isoformat(),
                "duration_hours": incident.duration_hours,
                "affected_systems": incident.affected_systems,
                "response_team": incident.response_team.name if incident.response_team else None
            }

            # Impact analysis
            impact_analysis = {
                "estimated_impact": incident.estimated_impact,
                "affected_systems_count": len(incident.affected_systems),
                "affected_locations": incident.affected_locations or [],
                "severity_level": incident.severity.value
            }

            # Timeline summary (key events)
            timeline_summary = [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "event_type": entry.event_type,
                    "description": entry.description,
                    "actor": entry.actor
                }
                for entry in timeline[:10]  # Last 10 events
            ]

            # Actions summary
            actions_completed = sum(1 for a in actions if a.status == ActionStatus.COMPLETED)
            actions_summary = {
                "total_actions": len(actions),
                "completed_actions": actions_completed,
                "pending_actions": len(actions) - actions_completed,
                "completion_rate": (actions_completed / len(actions) * 100) if actions else 0
            }

            # Metrics summary
            metrics_summary = {
                "total_services": len(metrics),
                "rto_met_count": sum(1 for m in metrics if m.rto_met),
                "rpo_met_count": sum(1 for m in metrics if m.rpo_met),
                "rto_compliance_rate": (sum(1 for m in metrics if m.rto_met) / len(metrics) * 100) if metrics else None,
                "rpo_compliance_rate": (sum(1 for m in metrics if m.rpo_met) / len(metrics) * 100) if metrics else None
            }

            # Recommendations
            recommendations = self._generate_recommendations(incident, actions, metrics)

            report = IncidentReport(
                incident=incident,
                summary=summary,
                impact_analysis=impact_analysis,
                timeline_summary=timeline_summary,
                actions_summary=actions_summary,
                metrics_summary=metrics_summary,
                recommendations=recommendations,
                generated_at=datetime.utcnow()
            )

            logger.info(f"Report generated for incident {incident.incident_number}")
            return report

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise

    async def get_dashboard(
        self,
        organization_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> IncidentDashboard:
        """
        Get incident dashboard with statistics

        ISO 22301:2019 Clause 9.1 - Monitoring, measurement, analysis and evaluation
        """
        try:
            # Default to last 30 days if not specified
            if not to_date:
                to_date = datetime.utcnow()
            if not from_date:
                from_date = to_date - timedelta(days=30)

            # Get incidents
            query = IncidentListQuery(
                organization_id=organization_id,
                from_date=from_date,
                to_date=to_date,
                skip=0,
                limit=1000
            )
            incidents, total = await self.repository.list_incidents(query)

            # Calculate statistics
            active_incidents = sum(
                1 for i in incidents
                if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
            )
            critical_incidents = sum(
                1 for i in incidents
                if i.severity == IncidentSeverity.CRITICAL
            )

            # Group by status
            incidents_by_status = {}
            for status in IncidentStatus:
                incidents_by_status[status.value] = sum(1 for i in incidents if i.status == status)

            # Group by severity
            incidents_by_severity = {}
            for severity in IncidentSeverity:
                incidents_by_severity[severity.value] = sum(1 for i in incidents if i.severity == severity)

            # Group by type
            from models.domain import IncidentType
            incidents_by_type = {}
            for incident_type in IncidentType:
                incidents_by_type[incident_type.value] = sum(1 for i in incidents if i.incident_type == incident_type)

            # Calculate average resolution time
            resolved_incidents = [i for i in incidents if i.duration_hours is not None]
            avg_resolution_hours = (
                sum(i.duration_hours for i in resolved_incidents) / len(resolved_incidents)
                if resolved_incidents else None
            )

            # Calculate RTO/RPO compliance - FIXED: Use bulk query instead of N+1
            incident_ids = [i.id for i in incidents]
            metrics_dict = await self.repository.get_metrics_bulk(incident_ids)
            all_metrics = []
            for metrics_list in metrics_dict.values():
                all_metrics.extend(metrics_list)

            rto_compliance_rate = None
            rpo_compliance_rate = None
            if all_metrics:
                rto_metrics = [m for m in all_metrics if m.rto_met is not None]
                rpo_metrics = [m for m in all_metrics if m.rpo_met is not None]

                if rto_metrics:
                    rto_compliance_rate = sum(1 for m in rto_metrics if m.rto_met) / len(rto_metrics) * 100

                if rpo_metrics:
                    rpo_compliance_rate = sum(1 for m in rpo_metrics if m.rpo_met) / len(rpo_metrics) * 100

            # Get recent incidents (last 10)
            recent_incidents = incidents[:10]

            # Trending types
            trending_types = [
                {"type": incident_type, "count": count}
                for incident_type, count in incidents_by_type.items()
                if count > 0
            ]
            trending_types.sort(key=lambda x: x["count"], reverse=True)

            dashboard = IncidentDashboard(
                organization_id=organization_id,
                total_incidents=total,
                active_incidents=active_incidents,
                critical_incidents=critical_incidents,
                incidents_by_status=incidents_by_status,
                incidents_by_severity=incidents_by_severity,
                incidents_by_type=incidents_by_type,
                avg_resolution_hours=avg_resolution_hours,
                avg_response_hours=None,  # TODO: Calculate from timeline
                rto_compliance_rate=rto_compliance_rate,
                rpo_compliance_rate=rpo_compliance_rate,
                recent_incidents=recent_incidents,
                trending_types=trending_types,
                period_start=from_date,
                period_end=to_date,
                generated_at=datetime.utcnow()
            )

            logger.info(f"Dashboard generated for org {organization_id}")
            return dashboard

        except Exception as e:
            logger.error(f"Failed to generate dashboard: {e}")
            raise

    async def calculate_metrics(self, organization_id: UUID) -> OrganizationMetrics:
        """
        Calculate organization-level metrics

        Includes: MTTR, MTBF, incident trends
        """
        try:
            # Get all incidents
            query = IncidentListQuery(
                organization_id=organization_id,
                skip=0,
                limit=10000
            )
            incidents, total = await self.repository.list_incidents(query)

            # Get current month and last month incidents
            now = datetime.utcnow()
            first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

            incidents_this_month = sum(
                1 for i in incidents
                if i.created_at >= first_day_this_month
            )
            incidents_last_month = sum(
                1 for i in incidents
                if first_day_last_month <= i.created_at < first_day_this_month
            )

            # Calculate trend
            trend_percentage = None
            if incidents_last_month > 0:
                trend_percentage = ((incidents_this_month - incidents_last_month) / incidents_last_month) * 100

            # Calculate average duration
            incidents_with_duration = [i for i in incidents if i.duration_hours is not None]
            avg_duration = (
                sum(i.duration_hours for i in incidents_with_duration) / len(incidents_with_duration)
                if incidents_with_duration else None
            )

            # Calculate MTTR (Mean Time To Resolve)
            resolved_incidents = [
                i for i in incidents
                if i.status == IncidentStatus.RESOLVED and i.duration_hours is not None
            ]
            mttr = (
                sum(i.duration_hours for i in resolved_incidents) / len(resolved_incidents)
                if resolved_incidents else None
            )

            # Calculate MTBF (Mean Time Between Failures) - simplified
            # Time span / number of incidents
            if len(incidents) >= 2:
                oldest = min(incidents, key=lambda x: x.detected_at)
                newest = max(incidents, key=lambda x: x.detected_at)
                time_span_hours = (newest.detected_at - oldest.detected_at).total_seconds() / 3600
                mtbf = time_span_hours / len(incidents) if incidents else None
            else:
                mtbf = None

            # Count actions and communications - FIXED: Use bulk queries instead of N+1
            incident_ids = [i.id for i in incidents]
            actions_count_dict = await self.repository.get_actions_count_bulk(incident_ids)
            communications_count_dict = await self.repository.get_communications_count_bulk(incident_ids)
            total_actions = sum(actions_count_dict.values())
            total_communications = sum(communications_count_dict.values())

            avg_actions_per_incident = total_actions / total if total > 0 else None

            metrics = OrganizationMetrics(
                organization_id=organization_id,
                total_incidents=total,
                total_actions=total_actions,
                total_communications=total_communications,
                avg_incident_duration_hours=avg_duration,
                avg_actions_per_incident=avg_actions_per_incident,
                incidents_this_month=incidents_this_month,
                incidents_last_month=incidents_last_month,
                trend_percentage=trend_percentage,
                mttr=mttr,
                mtbf=mtbf,
                calculated_at=datetime.utcnow()
            )

            logger.info(f"Metrics calculated for org {organization_id}")
            return metrics

        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
            raise

    # ========================================================================
    # Notifications
    # ========================================================================

    async def notify_stakeholders(
        self,
        incident: Incident,
        message: str,
        escalate_to: Optional[List[UUID]] = None
    ):
        """
        Send notifications to stakeholders

        ISO 22301:2019 Clause 7.4 - Communication
        """
        try:
            # Create communication log
            recipients = []
            if escalate_to:
                recipients = [str(uid) for uid in escalate_to]

            # Add response team members
            if incident.response_team:
                for member in incident.response_team.members:
                    if member.email not in recipients:
                        recipients.append(member.email)

            if recipients:
                await self.log_communication(
                    incident_id=incident.id,
                    communication_data=CommunicationLogCreate(
                        communication_type="notification",
                        subject=f"Incident {incident.incident_number}: {incident.title}",
                        content=message,
                        sender="System",
                        recipients=recipients,
                        is_stakeholder_notification=True
                    )
                )

                # Publish event for external notification services
                await self.event_publisher.publish_stakeholder_notification(
                    incident, message, recipients
                )

                logger.info(f"Stakeholder notifications sent for incident {incident.incident_number}")

        except Exception as e:
            logger.error(f"Failed to send stakeholder notifications: {e}")
            # Don't raise - notifications are not critical

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    async def _generate_incident_number(self, organization_id: UUID) -> str:
        """Generate unique incident number"""
        # Get count of incidents for this org
        query = IncidentListQuery(organization_id=organization_id, skip=0, limit=1)
        _, total = await self.repository.list_incidents(query)

        # Format: INC-{YEAR}-{ORG_PREFIX}-{NUMBER}
        year = datetime.utcnow().year
        org_prefix = str(organization_id)[:8].upper()
        number = total + 1

        return f"INC-{year}-{org_prefix}-{number:04d}"

    async def _calculate_incident_duration(self, incident: Incident) -> float:
        """Calculate incident duration in hours"""
        if incident.resolved_at and incident.detected_at:
            delta = incident.resolved_at - incident.detected_at
            return delta.total_seconds() / 3600
        return 0.0

    async def _auto_escalate_critical(self, incident: Incident):
        """Auto-escalate critical incidents"""
        try:
            escalation = IncidentEscalation(
                escalation_reason="Auto-escalated due to critical severity",
                escalation_level="executive",
                notify_stakeholders=True,
                additional_notes="Automatic escalation triggered by system"
            )

            await self.escalate_incident(
                incident_id=incident.id,
                escalation_data=escalation,
                escalated_by=None
            )

        except Exception as e:
            logger.error(f"Auto-escalation failed: {e}")

    async def _handle_incident_resolved(self, incident: Incident):
        """Handle incident resolution"""
        # Calculate final metrics
        await self._validate_recovery_metrics(incident)

        # Set resolved timestamp
        await self.repository.set_resolved_at(incident.id, datetime.utcnow())

    async def _handle_incident_closed(self, incident: Incident):
        """Handle incident closure"""
        # Set closed timestamp
        await self.repository.set_closed_at(incident.id, datetime.utcnow())

        # Publish closed event
        await self.event_publisher.publish_incident_closed(incident)

    async def _validate_recovery_metrics(self, incident: Incident):
        """Validate recovery metrics against targets"""
        metrics = await self.repository.get_metrics(incident.id)

        for metric in metrics:
            if metric.actual_rto_hours and metric.actual_rpo_hours:
                rto_met = metric.actual_rto_hours <= metric.target_rto_hours
                rpo_met = metric.actual_rpo_hours <= metric.target_rpo_hours

                await self.repository.update_metrics_compliance(
                    metric.id,
                    rto_met=rto_met,
                    rpo_met=rpo_met
                )

                if not rto_met or not rpo_met:
                    logger.warning(
                        f"Recovery objectives not met for {metric.service_name} "
                        f"in incident {incident.incident_number}"
                    )

    def _generate_recommendations(
        self,
        incident: Incident,
        actions: List[ResponseAction],
        metrics: List[RecoveryMetrics]
    ) -> List[str]:
        """Generate recommendations based on incident analysis"""
        recommendations = []

        # Check resolution time
        if incident.duration_hours and incident.duration_hours > 24:
            recommendations.append(
                "Consider reviewing incident response procedures to reduce resolution time"
            )

        # Check actions completion
        if actions:
            completed = sum(1 for a in actions if a.status == ActionStatus.COMPLETED)
            if completed < len(actions):
                recommendations.append(
                    f"Complete remaining {len(actions) - completed} response actions"
                )

        # Check metrics compliance
        if metrics:
            rto_failures = sum(1 for m in metrics if m.rto_met is False)
            rpo_failures = sum(1 for m in metrics if m.rpo_met is False)

            if rto_failures > 0:
                recommendations.append(
                    f"Review RTO targets for {rto_failures} service(s) that did not meet objectives"
                )

            if rpo_failures > 0:
                recommendations.append(
                    f"Review RPO targets and backup procedures for {rpo_failures} service(s)"
                )

        # Check root cause
        if not incident.root_cause:
            recommendations.append("Conduct thorough root cause analysis")

        # Check lessons learned
        if not incident.lessons_learned:
            recommendations.append("Document lessons learned for future improvements")

        # Severity-specific recommendations
        if incident.severity == IncidentSeverity.CRITICAL:
            recommendations.append("Schedule post-incident review with executive team")

        return recommendations
