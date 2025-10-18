"""
Simulation Database Models
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func

from database.models import Base


class Simulation(Base):
    """Simulation Model"""

    __tablename__ = "simulations"
    __table_args__ = {'schema': 'simulation'}

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)

    # Simulation configuration
    simulation_type = Column(String(50), nullable=False)  # what_if, monte_carlo, scenario, optimization
    engine = Column(String(50))  # internal, jaamsim, external
    parameters = Column(JSON, nullable=False, default={})

    # Status
    status = Column(String(50), default='draft')  # draft, ready, running, completed, failed
    created_by = Column(String(255))

    # Metadata
    sim_metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Simulation(id={self.id}, name='{self.name}', type='{self.simulation_type}')>"


class Scenario(Base):
    """Scenario Model (BCM exercises)"""

    __tablename__ = "scenarios"
    __table_args__ = {'schema': 'simulation'}

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True)
    title = Column(String(255), nullable=False)

    # Scenario metadata
    category = Column(String(50))  # cyber, pandemic, disaster, etc.
    complexity = Column(Integer)  # 1-5
    scenario_type = Column(String(50))  # tabletop, functional, full_scale

    # Content
    content = Column(Text)  # Markdown description
    timeline = Column(JSON)  # Hour-by-hour timeline
    injects = Column(JSON)  # Exercise injects
    success_metrics = Column(JSON)

    # AI generation
    is_ai_generated = Column(Boolean, default=False)
    ai_generation_params = Column(JSON)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Scenario(id={self.id}, title='{self.title}', category='{self.category}')>"


class SimulationExecution(Base):
    """Simulation Execution (multiple runs of same simulation)"""

    __tablename__ = "executions"
    __table_args__ = {'schema': 'simulation'}

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, nullable=False, index=True)
    execution_number = Column(Integer)

    # Execution parameters (can override simulation params)
    parameters = Column(JSON)

    # Status
    status = Column(String(50))  # running, completed, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Results
    results = Column(JSON)
    error_message = Column(Text)

    def __repr__(self):
        return f"<SimulationExecution(id={self.id}, sim_id={self.simulation_id}, #={self.execution_number})>"


class SimulationResult(Base):
    """Simulation Results (time-series for TimescaleDB)"""

    __tablename__ = "results"
    __table_args__ = {'schema': 'simulation'}

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, nullable=False, index=True)

    # Result data
    result_type = Column(String(50))  # final, intermediate, metric
    result_data = Column(JSON, nullable=False)
    confidence_score = Column(Float)

    # Metadata
    result_metadata = Column(JSON, default={})

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<SimulationResult(id={self.id}, sim_id={self.simulation_id}, type='{self.result_type}')>"
