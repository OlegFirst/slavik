"""
SQLAlchemy Database Models for BIA Module

Database persistence layer for Business Impact Analysis processes.
Replaces in-memory Dict storage with PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from shared.database.base import Base


class BIAProcessModel(Base):
    """
    BIA Process - Business Impact Analysis Database Model

    SQLAlchemy model for persisting BIA processes to PostgreSQL.
    Maps to Pydantic BIAProcess domain model.
    """
    __tablename__ = "bia_processes"

    # Composite indexes for optimized queries
    __table_args__ = (
        # Tenant isolation + filtering by criticality
        Index('ix_bia_tenant_criticality', 'tenant_id', 'criticality'),
        # Tenant isolation + filtering by process owner
        Index('ix_bia_tenant_owner', 'tenant_id', 'process_owner'),
        # Tenant isolation + ordering by creation date (descending)
        Index('ix_bia_tenant_created_desc', 'tenant_id', 'created_at'),
        # Tenant isolation + status filtering
        Index('ix_bia_tenant_status', 'tenant_id', 'status'),
        # Range queries on RTO for recovery time analysis
        Index('ix_bia_rto_hours', 'rto_hours'),
        # Range queries on RPO for data loss analysis
        Index('ix_bia_rpo_hours', 'rpo_hours'),
        # Range queries on MTPD for downtime analysis
        Index('ix_bia_mtpd_hours', 'mtpd_hours'),
        # Essential service tier filtering (WHO tier classification)
        Index('ix_bia_who_tier', 'who_tier'),
        # Multi-column index for status + creation date ordering
        Index('ix_bia_status_created', 'status', 'created_at'),
        # Partial index for active (non-completed) processes
        Index('ix_bia_active_processes', 'tenant_id', 'status',
              postgresql_where=Column('status') != 'completed'),
    )

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Process details
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    department = Column(String(255), nullable=True)
    process_owner = Column(String(255), nullable=True)

    # Criticality
    criticality = Column(String(50), nullable=False)  # low, minor, moderate, high, critical (indexed in composite)
    criticality_score = Column(Integer, nullable=True)  # 1-5
    who_tier = Column(String(20), nullable=True)  # tier_1, tier_2, tier_3, tier_4 (indexed)

    # Industry context
    industry = Column(String(100), nullable=True, index=True)  # Industry-specific filtering
    geographical_scope = Column(String(50), nullable=True)

    # Time objectives (in hours)
    rto_hours = Column(Integer, nullable=False)
    rpo_hours = Column(Integer, nullable=False)
    mtpd_hours = Column(Integer, nullable=False)

    # Impact assessment
    financial_impact = Column(JSON, nullable=True)  # Dict with timeline: {1_hour: 5000, 4_hours: 20000}
    operational_impact = Column(JSON, nullable=True)  # Dict with timeline
    annual_revenue_impact = Column(Float, nullable=True)

    # Impact levels (enums stored as strings)
    reputational_impact = Column(String(50), nullable=True)
    regulatory_impact = Column(String(50), nullable=True)
    patient_safety_impact = Column(String(50), nullable=True)  # healthcare-specific

    # Resources and dependencies
    resources_required = Column(JSON, nullable=True)  # List of dicts
    dependencies = Column(JSON, nullable=True)  # List of dependency objects

    # Process metrics
    peak_concurrent_users = Column(Integer, nullable=True)
    staff_count = Column(Integer, nullable=True)

    # AI analysis results
    ai_suggested_rto = Column(Float, nullable=True)
    ai_suggested_rpo = Column(Float, nullable=True)
    ai_suggested_mtpd = Column(Float, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_recommendations = Column(Text, nullable=True)

    # Status tracking
    status = Column(String(50), nullable=False, default="draft")  # indexed in composite
    completed_at = Column(DateTime, nullable=True)

    # ISO 22301 Compliance Fields
    compliance_objective = Column(Text, nullable=True)
    legal_regulatory_requirements = Column(JSON, nullable=True)

    # Resource Requirements (Detailed)
    personnel_requirements = Column(JSON, nullable=True)
    facility_requirements = Column(JSON, nullable=True)
    technology_requirements = Column(JSON, nullable=True)
    information_requirements = Column(JSON, nullable=True)

    # Recovery Strategies
    recovery_strategies = Column(JSON, nullable=True)
    alternative_procedures = Column(JSON, nullable=True)
    workaround_capacity = Column(Float, nullable=True)

    # Dependencies (Enhanced)
    upstream_processes = Column(JSON, nullable=True)
    downstream_processes = Column(JSON, nullable=True)
    critical_suppliers = Column(JSON, nullable=True)

    # Operating Characteristics
    minimum_resource_level = Column(JSON, nullable=True)
    peak_periods = Column(JSON, nullable=True)
    seasonality = Column(String(255), nullable=True)

    # ISO 22301 Assessment
    bia_completion_date = Column(DateTime, nullable=True)
    bia_assessor = Column(String(255), nullable=True)
    bia_reviewer = Column(String(255), nullable=True)
    next_review_date = Column(DateTime, nullable=True, index=True)

    # Audit fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # indexed in composite
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, index=True)  # For recent updates
    created_by = Column(String(255), nullable=True, index=True)  # For creator-based queries

    def __repr__(self):
        return f"<BIAProcess(id={self.id}, name='{self.name}', criticality='{self.criticality}')>"
