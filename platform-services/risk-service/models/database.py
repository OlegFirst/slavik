"""
Risk Management - Database Models (SQLAlchemy)
Maps to risk.risks table in Supabase
"""

from sqlalchemy import Column, String, Integer, Text, Boolean, Date, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import sys
from pathlib import Path

# Add shared database to Python path
shared_db_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "platform-services" / "community-service" / "shared"
if str(shared_db_path) not in sys.path:
    sys.path.insert(0, str(shared_db_path))

from database.connection import Base


class RiskDB(Base):
    """Risk Assessment - Database Model"""

    __tablename__ = "risks"
    __table_args__ = {'schema': 'risk'}

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Organization (Multi-tenancy)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identification
    risk_title = Column(String(255), nullable=False, index=True)
    risk_code = Column(String(50), index=True)
    risk_category = Column(String(100), index=True)

    # Description
    description = Column(Text, nullable=False)
    threat_source = Column(String(255))
    vulnerabilities = Column(ARRAY(Text), default=[])

    # Analysis (1-5 scale)
    likelihood = Column(Integer, CheckConstraint('likelihood BETWEEN 1 AND 5'))
    impact = Column(Integer, CheckConstraint('impact BETWEEN 1 AND 5'))
    inherent_risk_score = Column(Integer)  # Computed: likelihood * impact

    # Treatment
    treatment_strategy = Column(String(50))
    residual_likelihood = Column(Integer, CheckConstraint('residual_likelihood BETWEEN 1 AND 5'))
    residual_impact = Column(Integer, CheckConstraint('residual_impact BETWEEN 1 AND 5'))
    residual_risk_score = Column(Integer)  # Computed: residual_likelihood * residual_impact

    # Ownership
    risk_owner_id = Column(UUID(as_uuid=True))

    # Related Entities
    related_processes = Column(JSONB, default=[])
    related_assets = Column(JSONB, default=[])

    # Status
    status = Column(String(50), default='identified', index=True)

    # Review
    last_reviewed_at = Column(TIMESTAMP(timezone=True))
    next_review_date = Column(Date)

    # Audit
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    fair_analyses = relationship("FAIRAnalysisDB", back_populates="risk", cascade="all, delete-orphan")
    monte_carlo_simulations = relationship("MonteCarloSimulationDB", back_populates="risk", cascade="all, delete-orphan")
    treatment_plans = relationship("RiskTreatmentPlanDB", back_populates="risk", cascade="all, delete-orphan")
    ai_advisor_sessions = relationship("AIRiskAdvisorDB", back_populates="risk", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Risk(id={self.id}, title='{self.risk_title}', score={self.inherent_risk_score})>"


class FAIRAnalysisDB(Base):
    """FAIR Analysis - Database Model"""

    __tablename__ = "fair_analysis"
    __table_args__ = {'schema': 'risk'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risk.risks.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Loss Event Frequency
    threat_event_frequency = Column(Integer, nullable=False)  # per year
    vulnerability_score = Column(Integer, nullable=False)  # 0-100
    loss_event_frequency = Column(Integer)  # TEF * VS/100

    # Loss Magnitude
    primary_loss_min = Column(Integer, nullable=False)
    primary_loss_max = Column(Integer, nullable=False)
    primary_loss_most_likely = Column(Integer, nullable=False)
    secondary_loss_min = Column(Integer, default=0)
    secondary_loss_max = Column(Integer, default=0)

    # Results
    annual_loss_expectancy = Column(Integer)
    risk_rating = Column(String(50), default='medium')
    confidence_interval_low = Column(Integer)
    confidence_interval_high = Column(Integer)

    # Metadata
    analyzed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    analyzed_by = Column(UUID(as_uuid=True))

    # Relationships
    risk = relationship("RiskDB", back_populates="fair_analyses")

    def __repr__(self):
        return f"<FAIRAnalysis(risk_id={self.risk_id}, ALE={self.annual_loss_expectancy})>"


class MonteCarloSimulationDB(Base):
    """Monte Carlo Simulation - Database Model"""

    __tablename__ = "monte_carlo_simulations"
    __table_args__ = {'schema': 'risk'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risk.risks.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    iterations = Column(Integer, default=10000)

    # Variable Inputs
    factors = Column(JSONB, default=[])

    # Results
    mean_loss = Column(Integer)
    median_loss = Column(Integer)
    percentile_95 = Column(Integer)
    percentile_99 = Column(Integer)

    # Distribution Data
    distribution_data = Column(JSONB)

    # Metadata
    simulated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    risk = relationship("RiskDB", back_populates="monte_carlo_simulations")

    def __repr__(self):
        return f"<MonteCarloSimulation(risk_id={self.risk_id}, iterations={self.iterations})>"


class RiskTreatmentPlanDB(Base):
    """Risk Treatment Plan - Database Model"""

    __tablename__ = "risk_treatment_plans"
    __table_args__ = {'schema': 'risk'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risk.risks.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Strategy
    strategy = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)

    # Actions
    actions = Column(JSONB, default=[])
    responsible_party = Column(UUID(as_uuid=True))

    # Timeline
    start_date = Column(Date)
    target_date = Column(Date)
    completion_date = Column(Date)

    # Cost
    estimated_cost = Column(Integer)
    actual_cost = Column(Integer)

    # Expected Results
    expected_residual_likelihood = Column(Integer, CheckConstraint('expected_residual_likelihood BETWEEN 1 AND 5'))
    expected_residual_impact = Column(Integer, CheckConstraint('expected_residual_impact BETWEEN 1 AND 5'))

    # Status
    status = Column(String(50), default='planned', index=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    risk = relationship("RiskDB", back_populates="treatment_plans")

    def __repr__(self):
        return f"<RiskTreatmentPlan(risk_id={self.risk_id}, strategy='{self.strategy}')>"


class AIRiskAdvisorDB(Base):
    """AI Risk Advisor - Database Model"""

    __tablename__ = "ai_risk_advisor_sessions"
    __table_args__ = {'schema': 'risk'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risk.risks.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # AI Analysis
    ai_risk_analysis = Column(Text)
    risk_prediction = Column(JSONB)
    mitigation_recommendations = Column(JSONB, default=[])

    # FAIR Insights
    fair_quantification = Column(JSONB)

    # Context
    context_data = Column(JSONB, default={})

    # Results
    confidence_score = Column(Integer)  # 0-100

    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True))

    # Relationships
    risk = relationship("RiskDB", back_populates="ai_advisor_sessions")

    def __repr__(self):
        return f"<AIRiskAdvisor(risk_id={self.risk_id}, confidence={self.confidence_score})>"
