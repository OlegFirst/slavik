"""
Response Module - Database Models (SQLAlchemy)
ISO 22301:2019 Clause 8.4 - Incident Response

All SQLAlchemy ORM models for database tables in 'response' schema
"""

import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from typing import Optional, List

from sqlalchemy import (
    Column, String, DateTime, Boolean, Float, Integer, Text,
    ForeignKey, JSON, Index, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Add shared database to path
shared_db_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "platform-services" / "community-service" / "shared"
if str(shared_db_path) not in sys.path:
    sys.path.insert(0, str(shared_db_path))

from database import Base

# Import enums from domain models for database enum columns
from models.domain import (
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    ActionStatus,
    ActionPriority,
    CommunicationType,
    TeamMemberRole
)


# ============================================================================
# Incidents Table
# ============================================================================

class IncidentDB(Base):
    """
    Incidents table - Main incident records
    Schema: response
    """
    __tablename__ = "incidents"
    __table_args__ = (
        Index("idx_incidents_org_id", "organization_id"),
        Index("idx_incidents_status", "status"),
        Index("idx_incidents_severity", "severity"),
        Index("idx_incidents_type", "incident_type"),
        Index("idx_incidents_detected_at", "detected_at"),
        Index("idx_incidents_number", "incident_number", unique=True),
        Index("idx_incidents_org_status", "organization_id", "status"),
        CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name="check_severity"),
        CheckConstraint("status IN ('detected', 'investigating', 'contained', 'resolved', 'closed')", name="check_status"),
        {"schema": "response"}
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Organization (Multi-tenancy)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Incident Identity
    incident_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Classification
    incident_type = Column(
        SQLEnum(IncidentType, name="incident_type_enum", schema="response"),
        nullable=False,
        index=True
    )
    severity = Column(
        SQLEnum(IncidentSeverity, name="incident_severity_enum", schema="response"),
        nullable=False,
        index=True
    )
    status = Column(
        SQLEnum(IncidentStatus, name="incident_status_enum", schema="response"),
        nullable=False,
        default=IncidentStatus.DETECTED,
        index=True
    )

    # Impact
    affected_systems = Column(ARRAY(String), nullable=False, default=list)
    affected_locations = Column(ARRAY(String), nullable=True)
    estimated_impact = Column(Text, nullable=True)

    # Timeline
    detected_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    detected_by = Column(String(200), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    duration_hours = Column(Float, nullable=True)

    # Analysis
    root_cause = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True)

    # References
    external_reference = Column(String(200), nullable=True)
    response_team_id = Column(UUID(as_uuid=True), ForeignKey("response.response_teams.id"), nullable=True)

    # Tags & Metadata
    tags = Column(ARRAY(String), nullable=True)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    response_team = relationship("ResponseTeamDB", back_populates="incidents", lazy="selectin")
    actions = relationship("ResponseActionDB", back_populates="incident", cascade="all, delete-orphan", lazy="selectin")
    communications = relationship("CommunicationLogDB", back_populates="incident", cascade="all, delete-orphan", lazy="selectin")
    timeline = relationship("IncidentTimelineDB", back_populates="incident", cascade="all, delete-orphan", lazy="selectin")
    metrics = relationship("RecoveryMetricsDB", back_populates="incident", cascade="all, delete-orphan", lazy="selectin")


# ============================================================================
# Response Teams Table
# ============================================================================

class ResponseTeamDB(Base):
    """
    Response Teams table - Incident response teams
    Schema: response
    """
    __tablename__ = "response_teams"
    __table_args__ = (
        Index("idx_response_teams_org_id", "organization_id"),
        Index("idx_response_teams_is_active", "is_active"),
        {"schema": "response"}
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Organization (Multi-tenancy)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Team Information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Configuration
    activation_criteria = Column(JSON, nullable=True)
    escalation_procedures = Column(JSON, nullable=True)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    members = relationship("ResponseTeamMemberDB", back_populates="team", cascade="all, delete-orphan", lazy="selectin")
    incidents = relationship("IncidentDB", back_populates="response_team")


# ============================================================================
# Response Team Members Table
# ============================================================================

class ResponseTeamMemberDB(Base):
    """
    Response Team Members table - Team member details
    Schema: response
    """
    __tablename__ = "response_team_members"
    __table_args__ = (
        Index("idx_team_members_team_id", "team_id"),
        Index("idx_team_members_user_id", "user_id"),
        Index("idx_team_members_role", "role"),
        {"schema": "response"}
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    team_id = Column(UUID(as_uuid=True), ForeignKey("response.response_teams.id"), nullable=False)

    # Member Information
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    role = Column(
        SQLEnum(TeamMemberRole, name="team_member_role_enum", schema="response"),
        nullable=False
    )
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)

    # Status
    is_primary = Column(Boolean, nullable=False, default=False)
    availability_status = Column(String(50), nullable=False, default="available")
    notes = Column(Text, nullable=True)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    team = relationship("ResponseTeamDB", back_populates="members")


# ============================================================================
# Response Actions Table
# ============================================================================

class ResponseActionDB(Base):
    """
    Response Actions table - Actions taken during incident response
    Schema: response
    """
    __tablename__ = "response_actions"
    __table_args__ = (
        Index("idx_response_actions_incident_id", "incident_id"),
        Index("idx_response_actions_status", "status"),
        Index("idx_response_actions_priority", "priority"),
        Index("idx_response_actions_assigned_to", "assigned_to"),
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'cancelled')", name="check_action_status"),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name="check_action_priority"),
        {"schema": "response"}
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    incident_id = Column(UUID(as_uuid=True), ForeignKey("response.incidents.id"), nullable=False)

    # Action Details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String(100), nullable=False)

    # Priority & Status
    priority = Column(
        SQLEnum(ActionPriority, name="action_priority_enum", schema="response"),
        nullable=False
    )
    status = Column(
        SQLEnum(ActionStatus, name="action_status_enum", schema="response"),
        nullable=False,
        default=ActionStatus.PENDING
    )

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), nullable=True, index=True)
    assigned_to_name = Column(String(200), nullable=True)

    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Details
    completion_notes = Column(Text, nullable=True)
    dependencies = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    checklist = Column(JSON, nullable=True)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    incident = relationship("IncidentDB", back_populates="actions")


# ============================================================================
# Communication Logs Table
# ============================================================================

class CommunicationLogDB(Base):
    """
    Communication Logs table - Incident communications tracking
    Schema: response
    """
    __tablename__ = "communication_logs"
    __table_args__ = (
        Index("idx_communication_logs_incident_id", "incident_id"),
        Index("idx_communication_logs_type", "communication_type"),
        Index("idx_communication_logs_created_at", "created_at"),
        {"schema": "response"}
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    incident_id = Column(UUID(as_uuid=True), ForeignKey("response.incidents.id"), nullable=False)

    # Communication Details
    communication_type = Column(
        SQLEnum(CommunicationType, name="communication_type_enum", schema="response"),
        nullable=False
    )
    subject = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)

    # Participants
    sender = Column(String(200), nullable=False)
    recipients = Column(ARRAY(String), nullable=False)
    cc_recipients = Column(ARRAY(String), nullable=True)

    # Channel
    channel = Column(String(100), nullable=True)
    is_stakeholder_notification = Column(Boolean, nullable=False, default=False)

    # Metadata
    additional_metadata = Column(JSON, nullable=True)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    incident = relationship("IncidentDB", back_populates="communications")


# ============================================================================
# Incident Timeline Table
# ============================================================================

class IncidentTimelineDB(Base):
    """
    Incident Timeline table - Chronological event tracking
    Schema: response
    """
    __tablename__ = "incident_timeline"
    __table_args__ = (
        Index("idx_incident_timeline_incident_id", "incident_id"),
        Index("idx_incident_timeline_timestamp", "timestamp"),
        Index("idx_incident_timeline_event_type", "event_type"),
        {"schema": "response"}
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    incident_id = Column(UUID(as_uuid=True), ForeignKey("response.incidents.id"), nullable=False)

    # Event Details
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    # Actor
    actor = Column(String(200), nullable=True)
    actor_id = Column(UUID(as_uuid=True), nullable=True)

    # Metadata
    additional_metadata = Column(JSON, nullable=True)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationships
    incident = relationship("IncidentDB", back_populates="timeline")


# ============================================================================
# Recovery Metrics Table
# ============================================================================

class RecoveryMetricsDB(Base):
    """
    Recovery Metrics table - RTO/RPO tracking
    Schema: response
    """
    __tablename__ = "recovery_metrics"
    __table_args__ = (
        Index("idx_recovery_metrics_incident_id", "incident_id"),
        Index("idx_recovery_metrics_service", "service_name"),
        {"schema": "response"}
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Keys
    incident_id = Column(UUID(as_uuid=True), ForeignKey("response.incidents.id"), nullable=False)

    # Service Information
    service_name = Column(String(200), nullable=False)

    # Target Objectives
    target_rto_hours = Column(Float, nullable=False)
    target_rpo_hours = Column(Float, nullable=False)

    # Actual Metrics
    actual_rto_hours = Column(Float, nullable=True)
    actual_rpo_hours = Column(Float, nullable=True)

    # Downtime Tracking
    downtime_start = Column(DateTime(timezone=True), nullable=False)
    downtime_end = Column(DateTime(timezone=True), nullable=True)

    # Data Loss Tracking
    data_loss_start = Column(DateTime(timezone=True), nullable=True)
    data_loss_end = Column(DateTime(timezone=True), nullable=True)

    # Compliance
    rto_met = Column(Boolean, nullable=True)
    rpo_met = Column(Boolean, nullable=True)

    # Details
    impact_description = Column(Text, nullable=True)
    recovery_actions = Column(ARRAY(String), nullable=True)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    incident = relationship("IncidentDB", back_populates="metrics")
