"""
SQLAlchemy ORM Models for Simulation Service
==============================================

Database models for:
- Simulations (configuration and lifecycle)
- Scenarios (BCM exercises and templates)
- Simulation Executions (run history)
- Simulation Results (time-series data)

Schema: simulation
Database: PostgreSQL with TimescaleDB extension for results
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Simulation(Base):
    """
    Simulation Configuration and Lifecycle Model

    Represents a simulation configuration that can be executed multiple times.

    Fields:
    - id: Primary key
    - tenant_id: Multi-tenant isolation
    - name: Human-readable simulation name
    - simulation_type: what_if, monte_carlo, scenario, optimization
    - engine: internal, jaamsim, external
    - parameters: Engine-specific configuration (JSON)
    - status: draft → ready → running → completed/failed
    - metadata: Additional custom metadata
    """

    __tablename__ = "simulations"
    __table_args__ = {'schema': 'simulation'}

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Simulation configuration
    simulation_type = Column(String(50), nullable=False, index=True)
    # Types: what_if, monte_carlo, scenario, optimization, bia, jaamsim
    engine = Column(String(50), nullable=True)
    # Engines: internal, jaamsim, ciw, external
    parameters = Column(JSON, nullable=False, default={})

    # Status tracking
    status = Column(String(50), default='draft', index=True)
    # draft → ready → running → completed | failed | cancelled
    created_by = Column(String(255), nullable=True)

    # Metadata and tags
    metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    executions = relationship("SimulationExecution", back_populates="simulation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Simulation(id={self.id}, name='{self.name}', type='{self.simulation_type}', status='{self.status}')>"


class Scenario(Base):
    """
    BCM Exercise Scenario Model

    Represents a BCM scenario/exercise that can be simulated.
    Can be manually created or AI-generated.

    Fields:
    - id: Primary key
    - title: Scenario title
    - category: cyber, pandemic, disaster, supply_chain, etc.
    - complexity: 1-5 (tabletop → full-scale)
    - content: Markdown description
    - timeline: Hour-by-hour event timeline
    - injects: Exercise injects (events injected during exercise)
    - success_metrics: KPIs and success criteria
    """

    __tablename__ = "scenarios"
    __table_args__ = {'schema': 'simulation'}

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=True, index=True)

    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Scenario metadata
    category = Column(String(50), nullable=True, index=True)
    # Categories: cyber, pandemic, natural_disaster, supply_chain, operational, financial
    complexity = Column(Integer, nullable=True)  # 1-5
    scenario_type = Column(String(50), nullable=True)
    # Types: tabletop, functional, full_scale, hybrid

    # Content
    content = Column(Text, nullable=True)  # Markdown description
    timeline = Column(JSON, nullable=True)  # [{hour: 1, event: "...", inject: {...}}]
    injects = Column(JSON, nullable=True)  # [{id, time, type, content}]
    success_metrics = Column(JSON, nullable=True)  # {metric_name: target_value}

    # Participants
    participant_roles = Column(JSON, nullable=True)  # [role definitions]
    recommended_participants_count = Column(Integer, nullable=True)

    # AI generation metadata
    is_ai_generated = Column(Boolean, default=False, index=True)
    ai_generation_params = Column(JSON, nullable=True)
    ai_confidence_score = Column(Float, nullable=True)

    # Tags and classification
    tags = Column(JSON, default=[])
    industry = Column(String(100), nullable=True)
    organization_size = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Scenario(id={self.id}, title='{self.title}', category='{self.category}', complexity={self.complexity})>"


class SimulationExecution(Base):
    """
    Simulation Execution History

    Represents a single execution/run of a simulation.
    One simulation can have multiple executions with different parameters.

    Fields:
    - id: Primary key
    - simulation_id: Foreign key to simulation
    - execution_number: Sequential run number (1, 2, 3...)
    - parameters: Execution-specific parameters (can override simulation params)
    - status: running → completed | failed
    - results: Final results summary
    """

    __tablename__ = "executions"
    __table_args__ = {'schema': 'simulation'}

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key
    simulation_id = Column(Integer, ForeignKey('simulation.simulations.id'), nullable=False, index=True)

    # Execution info
    execution_number = Column(Integer, nullable=True)  # Sequential: 1, 2, 3...
    run_id = Column(String(100), nullable=True, index=True)  # UUID for external tracking

    # Execution parameters (can override simulation defaults)
    parameters = Column(JSON, nullable=True)

    # Status tracking
    status = Column(String(50), nullable=False, index=True)
    # running → completed | failed | cancelled
    progress = Column(Float, default=0.0)  # 0-100%

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Results summary
    results = Column(JSON, nullable=True)  # Final results
    metrics = Column(JSON, nullable=True)  # Performance metrics
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)

    # Metadata
    executed_by = Column(String(255), nullable=True)
    metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    simulation = relationship("Simulation", back_populates="executions")

    def __repr__(self):
        return f"<SimulationExecution(id={self.id}, sim_id={self.simulation_id}, #={self.execution_number}, status='{self.status}')>"


class SimulationResult(Base):
    """
    Simulation Time-Series Results

    Stores time-series simulation results (optimized for TimescaleDB).
    Can store:
    - Final results
    - Intermediate results
    - Real-time metrics
    - Event logs

    Fields:
    - id: Primary key
    - simulation_id: Foreign key to simulation
    - execution_id: Optional foreign key to execution
    - result_type: final, intermediate, metric, event
    - result_data: JSON result payload
    - recorded_at: Timestamp (indexed for time-series queries)
    """

    __tablename__ = "results"
    __table_args__ = {'schema': 'simulation'}

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign keys
    simulation_id = Column(Integer, nullable=False, index=True)
    execution_id = Column(Integer, nullable=True, index=True)

    # Result classification
    result_type = Column(String(50), nullable=False, index=True)
    # Types: final, intermediate, metric, event, log
    metric_name = Column(String(100), nullable=True, index=True)

    # Result payload
    result_data = Column(JSON, nullable=False)

    # Quality indicators
    confidence_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)

    # Metadata
    metadata = Column(JSON, default={})

    # Timestamp (TimescaleDB hypertable on this column)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SimulationResult(id={self.id}, sim_id={self.simulation_id}, type='{self.result_type}', recorded_at='{self.recorded_at}')>"


# Export all models
__all__ = [
    "Base",
    "Simulation",
    "Scenario",
    "SimulationExecution",
    "SimulationResult"
]
