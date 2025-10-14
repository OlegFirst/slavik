"""
SQLAlchemy ORM models for Simulation Service

Database persistence layer using PostgreSQL with async support.
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from models.pydantic_models import (
    EngineType,
    SimulationStatus,
    ExerciseType,
    ScenarioCategory,
    DashboardType,
    ReportFormat,
)

Base = declarative_base()


# ============================================================================
# CORE ORM MODELS
# ============================================================================

class TaskSpecificationORM(Base):
    """Task specification persistence"""
    __tablename__ = "task_specifications"

    id = Column(String(50), primary_key=True)
    goal = Column(Text, nullable=False)
    constraints = Column(JSON, nullable=False, default={})
    context = Column(JSON, nullable=False, default={})

    engine_preference = Column(SQLEnum(EngineType), nullable=True)
    max_duration = Column(Integer, nullable=False, default=3600)

    processes = Column(JSON, nullable=False, default=[])
    resources = Column(JSON, nullable=False, default={})
    scenarios = Column(ARRAY(String), nullable=False, default=[])
    alternatives = Column(JSON, nullable=False, default=[])
    monte_carlo_iterations = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(50), nullable=False)
    organization_id = Column(String(50), nullable=False, index=True)

    metadata_ = Column("metadata", JSON, nullable=False, default={})

    # Relationships
    simulations = relationship("SimulationORM", back_populates="specification")

    __table_args__ = (
        Index('ix_task_specifications_org_created', 'organization_id', 'created_at'),
        Index('ix_task_specifications_created_by', 'created_by'),
    )


class ScenarioORM(Base):
    """Scenario persistence"""
    __tablename__ = "scenarios"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    category = Column(SQLEnum(ScenarioCategory), nullable=False, index=True)
    exercise_type = Column(SQLEnum(ExerciseType), nullable=False)

    # Duration and complexity
    duration_minutes = Column(Integer, nullable=False)
    complexity_level = Column(Integer, nullable=False, default=1)

    # Scenario content
    incidents = Column(JSON, nullable=False, default=[])
    affected_processes = Column(ARRAY(String), nullable=False, default=[])
    impact_areas = Column(ARRAY(String), nullable=False, default=[])
    recovery_objectives = Column(JSON, nullable=False, default={})

    # Evaluation
    success_criteria = Column(ARRAY(String), nullable=False, default=[])
    key_metrics = Column(ARRAY(String), nullable=False, default=[])

    # Resources
    required_participants = Column(Integer, nullable=False, default=1)
    available_resources = Column(JSON, nullable=False, default={})
    constraints = Column(ARRAY(String), nullable=False, default=[])

    # Metadata
    tags = Column(ARRAY(String), nullable=False, default=[], index=True)
    source = Column(String(50), nullable=False, default="custom")
    quality_score = Column(Float, nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(50), nullable=False)
    organization_id = Column(String(50), nullable=False, index=True)

    # Relationships
    simulations = relationship("SimulationORM", back_populates="scenario")

    __table_args__ = (
        Index('ix_scenarios_category_quality', 'category', 'quality_score'),
        Index('ix_scenarios_org_created', 'organization_id', 'created_at'),
        Index('ix_scenarios_source', 'source'),
    )


class SimulationORM(Base):
    """Main simulation persistence"""
    __tablename__ = "simulations"

    id = Column(String(50), primary_key=True)

    # Foreign keys
    specification_id = Column(String(50), ForeignKey("task_specifications.id"), nullable=False, index=True)
    scenario_id = Column(String(50), ForeignKey("scenarios.id"), nullable=False, index=True)

    # Engine and configuration
    engine = Column(SQLEnum(EngineType), nullable=False)
    engine_config = Column(JSON, nullable=False)
    visualization_config = Column(JSON, nullable=False, default={})
    integration_config = Column(JSON, nullable=False, default={})
    report_config = Column(JSON, nullable=False, default={})

    # Status tracking
    status = Column(SQLEnum(SimulationStatus), nullable=False, default=SimulationStatus.PENDING, index=True)
    progress_percentage = Column(Float, nullable=False, default=0.0)
    current_phase = Column(String(200), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Participants
    created_by = Column(String(50), nullable=False)
    organization_id = Column(String(50), nullable=False, index=True)
    participants = Column(ARRAY(String), nullable=False, default=[])
    observers = Column(ARRAY(String), nullable=False, default=[])

    # Results
    result_id = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Metadata
    metadata_ = Column("metadata", JSON, nullable=False, default={})

    # Relationships
    specification = relationship("TaskSpecificationORM", back_populates="simulations")
    scenario = relationship("ScenarioORM", back_populates="simulations")
    events = relationship("SimulationEventORM", back_populates="simulation", cascade="all, delete-orphan")
    result = relationship("SimulationResultORM", back_populates="simulation", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_simulations_status_org', 'status', 'organization_id'),
        Index('ix_simulations_created_at', 'created_at'),
        Index('ix_simulations_created_by', 'created_by'),
        Index('ix_simulations_engine', 'engine'),
    )


class SimulationEventORM(Base):
    """Simulation events persistence"""
    __tablename__ = "simulation_events"

    id = Column(String(50), primary_key=True)
    simulation_id = Column(String(50), ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)

    event_type = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    elapsed_seconds = Column(Integer, nullable=False)

    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=True, index=True)

    actors = Column(ARRAY(String), nullable=False, default=[])
    data = Column(JSON, nullable=False, default={})
    metadata_ = Column("metadata", JSON, nullable=False, default={})

    # Relationships
    simulation = relationship("SimulationORM", back_populates="events")

    __table_args__ = (
        Index('ix_simulation_events_sim_timestamp', 'simulation_id', 'timestamp'),
        Index('ix_simulation_events_type_severity', 'event_type', 'severity'),
    )


class ExerciseMetricsORM(Base):
    """Exercise metrics persistence"""
    __tablename__ = "exercise_metrics"

    id = Column(String(50), primary_key=True, default=lambda: f"metrics_{uuid.uuid4().hex[:12]}")
    result_id = Column(String(50), ForeignKey("simulation_results.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Core BCM metrics
    rto_achieved = Column(JSON, nullable=False, default={})
    rpo_achieved = Column(JSON, nullable=False, default={})
    recovery_success_rate = Column(Float, nullable=False, default=0.0)

    # Performance metrics
    decision_times = Column(ARRAY(Float), nullable=False, default=[])
    communication_delays = Column(ARRAY(Float), nullable=False, default=[])
    resource_utilization = Column(JSON, nullable=False, default={})

    # Cost metrics
    estimated_cost = Column(Float, nullable=False, default=0.0)
    recovery_cost = Column(Float, nullable=False, default=0.0)
    downtime_cost = Column(Float, nullable=False, default=0.0)

    # Quality metrics
    participant_satisfaction = Column(Float, nullable=True)
    learning_objectives_met = Column(Float, nullable=False, default=0.0)

    # Compliance metrics
    regulatory_requirements_tested = Column(Integer, nullable=False, default=0)
    compliance_gaps_identified = Column(Integer, nullable=False, default=0)

    # Incident metrics
    incidents_total = Column(Integer, nullable=False, default=0)
    incidents_handled = Column(Integer, nullable=False, default=0)
    average_response_time = Column(Float, nullable=False, default=0.0)

    measured_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    result = relationship("SimulationResultORM", back_populates="metrics")


class SimulationResultORM(Base):
    """Simulation results persistence"""
    __tablename__ = "simulation_results"

    id = Column(String(50), primary_key=True)
    simulation_id = Column(String(50), ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, unique=True)
    scenario_id = Column(String(50), nullable=False)
    specification_id = Column(String(50), nullable=False)

    # Execution summary
    status = Column(SQLEnum(SimulationStatus), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    participants_count = Column(Integer, nullable=False, default=0)

    # Results
    success_criteria_met = Column(JSON, nullable=False, default={})
    key_findings = Column(ARRAY(Text), nullable=False, default=[])
    lessons_learned = Column(ARRAY(Text), nullable=False, default=[])
    best_practices = Column(ARRAY(Text), nullable=False, default=[])

    # Detailed results
    timeline = Column(JSON, nullable=False, default=[])
    decisions_made = Column(JSON, nullable=False, default=[])
    issues_encountered = Column(JSON, nullable=False, default=[])

    # Recommendations
    improvement_areas = Column(ARRAY(Text), nullable=False, default=[])
    recommendations = Column(ARRAY(Text), nullable=False, default=[])
    next_steps = Column(ARRAY(Text), nullable=False, default=[])

    # Quality assessment
    quality_score = Column(Float, nullable=False, default=0.0, index=True)
    contribution_worthy = Column(Boolean, nullable=False, default=False, index=True)

    # Summary
    summary = Column(Text, nullable=False, default="")

    # Files
    report_files = Column(ARRAY(String), nullable=False, default=[])
    log_files = Column(ARRAY(String), nullable=False, default=[])

    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    simulation = relationship("SimulationORM", back_populates="result")
    metrics = relationship("ExerciseMetricsORM", back_populates="result", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_simulation_results_quality', 'quality_score'),
        Index('ix_simulation_results_contribution', 'contribution_worthy'),
        Index('ix_simulation_results_generated_at', 'generated_at'),
    )


# ============================================================================
# UTILITY MODELS
# ============================================================================

class SimulationLogORM(Base):
    """Simulation execution logs"""
    __tablename__ = "simulation_logs"

    id = Column(String(50), primary_key=True, default=lambda: f"log_{uuid.uuid4().hex[:12]}")
    simulation_id = Column(String(50), ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False, index=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    context = Column(JSON, nullable=False, default={})

    __table_args__ = (
        Index('ix_simulation_logs_sim_timestamp', 'simulation_id', 'timestamp'),
        Index('ix_simulation_logs_level', 'level'),
    )


class PDCACycleORM(Base):
    """PDCA cycles created from simulations"""
    __tablename__ = "pdca_cycles"

    id = Column(String(50), primary_key=True)
    simulation_id = Column(String(50), ForeignKey("simulations.id"), nullable=False, index=True)

    workflow_intelligence_cycle_id = Column(String(50), nullable=True, unique=True)

    cycle_type = Column(String(50), nullable=False, default="simulation_improvement")
    status = Column(String(50), nullable=False, default="plan", index=True)

    plan_data = Column(JSON, nullable=False, default={})
    do_data = Column(JSON, nullable=False, default={})
    check_data = Column(JSON, nullable=False, default={})
    act_data = Column(JSON, nullable=False, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    organization_id = Column(String(50), nullable=False, index=True)

    __table_args__ = (
        Index('ix_pdca_cycles_org_status', 'organization_id', 'status'),
        Index('ix_pdca_cycles_created_at', 'created_at'),
    )


class CommunityContributionORM(Base):
    """Community contributions from simulations"""
    __tablename__ = "community_contributions"

    id = Column(String(50), primary_key=True)
    simulation_id = Column(String(50), ForeignKey("simulations.id"), nullable=False, index=True)

    community_intelligence_contribution_id = Column(String(50), nullable=True, unique=True)

    anonymized_data = Column(JSON, nullable=False)
    quality_score = Column(Float, nullable=False, index=True)

    contribution_status = Column(String(50), nullable=False, default="pending", index=True)
    peer_review_score = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    organization_id = Column(String(50), nullable=False, index=True)

    __table_args__ = (
        Index('ix_community_contributions_quality', 'quality_score'),
        Index('ix_community_contributions_status', 'contribution_status'),
    )


class KnowledgeStorageORM(Base):
    """Knowledge stored from simulations"""
    __tablename__ = "knowledge_storage"

    id = Column(String(50), primary_key=True)
    simulation_id = Column(String(50), ForeignKey("simulations.id"), nullable=False, index=True)

    knowledge_center_knowledge_id = Column(String(50), nullable=True, unique=True)

    category = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)

    tags = Column(ARRAY(String), nullable=False, default=[], index=True)
    quality_score = Column(Float, nullable=False, default=0.0)

    stored_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    organization_id = Column(String(50), nullable=False, index=True)

    __table_args__ = (
        Index('ix_knowledge_storage_category', 'category'),
        Index('ix_knowledge_storage_quality', 'quality_score'),
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def to_pydantic(orm_obj, pydantic_class):
    """
    Convert ORM object to Pydantic model

    Args:
        orm_obj: SQLAlchemy ORM instance
        pydantic_class: Pydantic model class

    Returns:
        Pydantic model instance
    """
    if orm_obj is None:
        return None

    # Get all column names
    data = {}
    for column in orm_obj.__table__.columns:
        column_name = column.name
        # Handle metadata_ special case
        if column_name == "metadata":
            data["metadata"] = getattr(orm_obj, "metadata_")
        else:
            data[column_name] = getattr(orm_obj, column_name)

    return pydantic_class(**data)


def from_pydantic(pydantic_obj, orm_class):
    """
    Convert Pydantic model to ORM object

    Args:
        pydantic_obj: Pydantic model instance
        orm_class: SQLAlchemy ORM class

    Returns:
        SQLAlchemy ORM instance
    """
    if pydantic_obj is None:
        return None

    # Get dict from Pydantic model
    data = pydantic_obj.model_dump()

    # Handle metadata special case
    if "metadata" in data:
        data["metadata_"] = data.pop("metadata")

    return orm_class(**data)
