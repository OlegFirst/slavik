"""
Planning Service Database Models (SQLAlchemy)
ISO 22301 Clause 8.3 - Business Continuity Strategy
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from .domain import StrategyType, StrategyPhase, StrategyStatus


Base = declarative_base()


class Strategy(Base):
    """
    Business Continuity Strategy Model
    ISO 22301 Clause 8.3
    """
    __tablename__ = "strategies"
    __table_args__ = (
        # Composite indexes for common query patterns
        Index('ix_strategies_tenant_status', 'tenant_id', 'status'),
        Index('ix_strategies_tenant_type', 'tenant_id', 'strategy_type'),
        Index('ix_strategies_tenant_created', 'tenant_id', 'created_at'),
        Index('ix_strategies_tenant_status_created', 'tenant_id', 'status', 'created_at'),
        Index('ix_strategies_status_created', 'status', 'created_at'),
        # Additional indexes for optimization
        Index('ix_strategies_tenant_phase', 'tenant_id', 'strategy_phase'),
        Index('ix_strategies_approval_status', 'tenant_id', 'status', 'approved_at'),
        Index('ix_strategies_impl_status', 'implementation_status', 'implementation_started_at'),
        Index('ix_strategies_reviewed_by', 'reviewed_by', 'reviewed_at'),
        Index('ix_strategies_approved_by', 'approved_by', 'approved_at'),
        Index('ix_strategies_cost_benefit', 'cost_benefit_ratio'),
        {'schema': 'planning'}
    )

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(100), nullable=False, index=True)

    # Strategy Identification
    strategy_number = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Classification
    strategy_type = Column(SQLEnum(StrategyType), nullable=False)
    strategy_phase = Column(SQLEnum(StrategyPhase), nullable=False)
    status = Column(SQLEnum(StrategyStatus), default=StrategyStatus.DRAFT)

    # ISO 8.3 Requirements
    objective = Column(Text, nullable=False)
    scope = Column(JSON)  # List of business units/processes
    risk_mitigation = Column(JSON)  # List of risks addressed

    # Cost-Benefit Analysis
    estimated_cost = Column(Float)
    cost_breakdown = Column(JSON)  # CostBreakdown model as JSON
    expected_benefits = Column(JSON)  # BenefitAnalysis model as JSON
    roi_analysis = Column(JSON)  # ROIAnalysis model as JSON
    cost_benefit_ratio = Column(Float)

    # Resource Requirements
    resource_requirements = Column(JSON)  # List[ResourceRequirement]
    resource_availability = Column(JSON)
    resource_gaps = Column(JSON)  # List of gap descriptions

    # Implementation
    implementation_phases = Column(JSON)  # List[ImplementationPhase]
    dependencies = Column(JSON)  # List of dependencies
    success_criteria = Column(JSON)  # List of success criteria

    # ISO Compliance
    iso_clauses_addressed = Column(JSON)
    compliance_notes = Column(Text)

    # Relationships
    linked_bia_ids = Column(JSON)  # Link to BIA service
    linked_risk_ids = Column(JSON)  # Link to Risk service

    # Approval Workflow
    submitted_for_review_at = Column(DateTime(timezone=True))
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    approval_notes = Column(Text)

    # Implementation Tracking
    implementation_started_at = Column(DateTime(timezone=True))
    implementation_completed_at = Column(DateTime(timezone=True))
    implementation_status = Column(String(50))
    implementation_notes = Column(Text)

    # Audit Trail
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(String(255))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    active = Column(Boolean, default=True)
