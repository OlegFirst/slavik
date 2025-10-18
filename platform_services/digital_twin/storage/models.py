"""
SQLAlchemy Database Models

Database models for Digital Twin Universal Service
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, Text, Enum as SQLEnum, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

from core.models.base import (
    OrganizationType,
    SimulationScenarioType,
    SimulationStatus,
    DataSourceType
)


# ============================================
# BASE
# ============================================

class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models"""
    pass


# ============================================
# TENANT & USER MODELS (Multi-tenancy + Auth)
# ============================================

class TenantModel(Base):
    """Tenant model for multi-tenancy"""
    __tablename__ = "tenants"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    # Identity
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # Subscription & Limits
    plan: Mapped[str] = mapped_column(String(50), default="free")
    max_users: Mapped[int] = mapped_column(Integer, default=5)
    max_digital_twins: Mapped[int] = mapped_column(Integer, default=10)
    max_simulations_per_month: Mapped[int] = mapped_column(Integer, default=50)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=True)
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Settings
    settings: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users: Mapped[list["UserModel"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    organizations: Mapped[list["OrganizationModel"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_tenant_slug', 'slug'),
        Index('idx_tenant_active', 'is_active'),
    )


class UserModel(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Identity
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Role within tenant
    role: Mapped[str] = mapped_column(String(50), default="member")  # admin, member, viewer

    # Preferences
    language: Mapped[str] = mapped_column(String(10), default="en")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    # Activity
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Metadata
    custom_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    tenant: Mapped["TenantModel"] = relationship(back_populates="users")

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_tenant', 'tenant_id'),
        Index('idx_user_active', 'is_active'),
    )


# ============================================
# ORGANIZATION MODELS
# ============================================

class OrganizationModel(Base):
    """Organization/Digital Twin database model"""
    __tablename__ = "organizations"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    twin_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # Multi-tenancy
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Identity
    name: Mapped[str] = mapped_column(String(255), index=True)
    canonical_name: Mapped[Optional[str]] = mapped_column(String(255))
    aliases: Mapped[Optional[dict]] = mapped_column(JSON)  # List stored as JSON

    # Classification
    org_type: Mapped[str] = mapped_column(SQLEnum(OrganizationType))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    industry_codes: Mapped[Optional[dict]] = mapped_column(JSON)

    # Size & Financials
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    annual_revenue: Mapped[Optional[float]] = mapped_column(Float)
    annual_budget: Mapped[Optional[float]] = mapped_column(Float)

    # Location (JSON)
    headquarters: Mapped[Optional[dict]] = mapped_column(JSON)
    locations: Mapped[Optional[dict]] = mapped_column(JSON)

    # Contacts (JSON)
    contacts: Mapped[Optional[dict]] = mapped_column(JSON)
    email_domain: Mapped[Optional[str]] = mapped_column(String(255))

    # Data Sources (JSON)
    source_ids: Mapped[Optional[dict]] = mapped_column(JSON)

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    tags: Mapped[Optional[dict]] = mapped_column(JSON)  # List
    custom_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Digital Twin Metrics
    health_score: Mapped[float] = mapped_column(Float, default=0.0)
    maturity_level: Mapped[int] = mapped_column(Integer, default=1)
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Frontend-Compatible Twin Fields (from TypeScript interfaces)
    twin_health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_landscape: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Format: {total_risks, critical_risks, mitigation_coverage}
    compliance_status: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Format: {overall_score, frameworks: [{name, compliance_percentage, last_assessment}]}
    departments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Format: [{name, twin_count, avg_health_score, key_metrics}]

    # BCM Specific (JSON)
    bcm_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant: Mapped["TenantModel"] = relationship(back_populates="organizations")
    simulations: Mapped[list["SimulationResultModel"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    data_sources: Mapped[list["DataSourceModel"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    personal_twins: Mapped[list["PersonalDigitalTwinModel"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index('idx_org_name', 'name'),
        Index('idx_org_type', 'org_type'),
        Index('idx_org_created', 'created_at'),
    )


class DataSourceModel(Base):
    """Data source connection"""
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.id"))

    # Source info
    source_type: Mapped[str] = mapped_column(SQLEnum(DataSourceType))
    source_id: Mapped[str] = mapped_column(String(255))

    # Status
    last_sync: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sync_status: Mapped[str] = mapped_column(String(50), default="active")

    # Metadata
    custom_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationship
    organization: Mapped["OrganizationModel"] = relationship(back_populates="data_sources")

    __table_args__ = (
        Index('idx_source_org', 'organization_id'),
        Index('idx_source_type', 'source_type'),
    )


class PersonalDigitalTwinModel(Base):
    """
    Personal Digital Twin - User-level digital twin for workspace customization

    Based on frontend TypeScript interface for frontend-backend compatibility
    """
    __tablename__ = "personal_digital_twins"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), index=True, unique=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("organizations.id"), nullable=True, index=True)

    # Identity
    display_name: Mapped[str] = mapped_column(String(255))

    # Workspace Configuration
    workspace_config: Mapped[dict] = mapped_column(JSON)
    # Format: {theme, language, dashboard_layout, widgets: {widget_name: bool}}

    # Personal Metrics
    personal_metrics: Mapped[dict] = mapped_column(JSON)
    # Format: {login_count_month, features_used: [], total_sessions,
    #          avg_session_hours, bcm_modules_used: [], data_quality_score}

    # Activity Patterns
    activity_patterns: Mapped[dict] = mapped_column(JSON)
    # Format: {activity_level: 'high'|'medium'|'low', peak_usage_hours: [],
    #          preferred_modules: [], engagement_trend: 'increasing'|'stable'|'decreasing',
    #          behavioral_insights: []}

    # Twin Health & Activity
    twin_health_score: Mapped[float] = mapped_column(Float, default=0.0)
    activity_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Sync Status
    last_sync: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sync_status: Mapped[str] = mapped_column(String(50), default="active")
    # Status: active, syncing, offline, error

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["UserModel"] = relationship()
    organization: Mapped[Optional["OrganizationModel"]] = relationship(back_populates="personal_twins")

    __table_args__ = (
        Index('idx_personal_twin_user', 'user_id'),
        Index('idx_personal_twin_org', 'organization_id'),
        Index('idx_personal_twin_sync', 'sync_status'),
    )


# ============================================
# SIMULATION MODELS
# ============================================

class SimulationResultModel(Base):
    """Simulation result database model"""
    __tablename__ = "simulation_results"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.twin_id"), index=True)

    # Scenario
    scenario: Mapped[str] = mapped_column(SQLEnum(SimulationScenarioType), index=True)
    status: Mapped[str] = mapped_column(SQLEnum(SimulationStatus), default=SimulationStatus.PENDING)

    # Parameters (JSON)
    parameters: Mapped[dict] = mapped_column(JSON)

    # Results
    impact_score: Mapped[Optional[float]] = mapped_column(Float)
    financial_impact: Mapped[Optional[float]] = mapped_column(Float)
    operational_impact: Mapped[Optional[float]] = mapped_column(Float)
    recovery_time_days: Mapped[Optional[int]] = mapped_column(Integer)

    # Detailed results (JSON)
    timeline: Mapped[Optional[dict]] = mapped_column(JSON)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON)  # List
    recovery_plan: Mapped[Optional[dict]] = mapped_column(JSON)

    # Execution info
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    organization: Mapped["OrganizationModel"] = relationship(back_populates="simulations")

    __table_args__ = (
        Index('idx_sim_twin', 'twin_id'),
        Index('idx_sim_scenario', 'scenario'),
        Index('idx_sim_status', 'status'),
        Index('idx_sim_created', 'created_at'),
    )


# ============================================
# METRICS MODELS
# ============================================

class MetricSeriesModel(Base):
    """Time series metrics"""
    __tablename__ = "metric_series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.twin_id"), index=True)

    # Metric info
    metric_name: Mapped[str] = mapped_column(String(100), index=True)
    aggregation: Mapped[Optional[str]] = mapped_column(String(20))

    # Data points (JSON array)
    points: Mapped[dict] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_metric_twin', 'twin_id'),
        Index('idx_metric_name', 'metric_name'),
    )


class HealthScoreModel(Base):
    """Health score snapshots"""
    __tablename__ = "health_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.twin_id"), index=True)

    # Scores
    overall: Mapped[float] = mapped_column(Float)
    financial: Mapped[float] = mapped_column(Float)
    operational: Mapped[float] = mapped_column(Float)
    impact: Mapped[float] = mapped_column(Float)
    sustainability: Mapped[float] = mapped_column(Float)

    # Timestamp
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_health_twin', 'twin_id'),
        Index('idx_health_calc', 'calculated_at'),
    )


# ============================================
# THEORY OF CHANGE MODELS
# ============================================

class TheoryOfChangeModel(Base):
    """Theory of Change model"""
    __tablename__ = "theories_of_change"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.twin_id"), index=True)

    # ToC Components (all JSON)
    inputs: Mapped[dict] = mapped_column(JSON)
    activities: Mapped[dict] = mapped_column(JSON)
    outputs: Mapped[dict] = mapped_column(JSON)
    outcomes: Mapped[dict] = mapped_column(JSON)
    impact: Mapped[dict] = mapped_column(JSON)

    # Supporting data (JSON)
    assumptions: Mapped[Optional[dict]] = mapped_column(JSON)
    indicators: Mapped[Optional[dict]] = mapped_column(JSON)
    pathways: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_toc_twin', 'twin_id'),
    )


# ============================================
# IMPACT PASSPORT MODELS
# ============================================

class ImpactPassportModel(Base):
    """Impact Passport model"""
    __tablename__ = "impact_passports"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.twin_id"), index=True)

    # Identity
    passport_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    organization_name: Mapped[str] = mapped_column(String(255))

    # Claims (JSON)
    claims: Mapped[dict] = mapped_column(JSON)
    evidence: Mapped[dict] = mapped_column(JSON)
    verification_status: Mapped[str] = mapped_column(String(50), default="pending")

    # Metadata
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    qr_code: Mapped[Optional[str]] = mapped_column(Text)
    verification_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_passport_twin', 'twin_id'),
        Index('idx_passport_number', 'passport_number'),
    )


# ============================================
# SIMULATION HUB MODELS (Universal Simulation Center)
# ============================================

class ScenarioTemplateModel(Base):
    """
    Scenario Templates - Universal scenario library

    Can be used WITHOUT organizations (standalone scenarios)
    """
    __tablename__ = "scenario_templates"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Identity
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Categorization
    category: Mapped[str] = mapped_column(String(100), index=True)  # BCM, Risk, Compliance
    scenario_type: Mapped[str] = mapped_column(String(100), index=True)
    # Types: cyber_attack, natural_disaster, pandemic, supply_chain, etc.

    # Scenario Details
    detailed_scenario: Mapped[Optional[str]] = mapped_column(Text)  # Full description
    parameters_template: Mapped[Optional[dict]] = mapped_column(JSON)  # Default parameters
    severity_levels: Mapped[Optional[dict]] = mapped_column(JSON)  # low, medium, high, critical

    # AI Generation
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_prompt: Mapped[Optional[str]] = mapped_column(Text)

    # Metadata
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    source: Mapped[Optional[str]] = mapped_column(String(255))  # User-created, AI, imported

    # Status
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)  # Share with community
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    exercises: Mapped[list["ExerciseModel"]] = relationship(back_populates="scenario_template")
    predictions: Mapped[list["PredictionModel"]] = relationship(back_populates="scenario_template")

    __table_args__ = (
        Index('idx_scenario_tenant', 'tenant_id'),
        Index('idx_scenario_type', 'scenario_type'),
        Index('idx_scenario_category', 'category'),
    )


class ExerciseModel(Base):
    """
    Exercises & Training - BCM exercises and drills

    Can run standalone OR with organization data
    """
    __tablename__ = "exercises"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Identity
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Exercise Type
    exercise_type: Mapped[str] = mapped_column(String(100), index=True)
    # Types: tabletop, walkthrough, simulation, full_scale, functional

    # Scenario
    scenario_template_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("scenario_templates.id"),
        nullable=True,
        index=True
    )

    # Exercise Parameters
    objectives: Mapped[Optional[list]] = mapped_column(JSON)  # Learning objectives
    participants: Mapped[Optional[list]] = mapped_column(JSON)  # Who's involved
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)

    # Execution
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="planned", index=True)
    # Status: planned, in_progress, completed, cancelled

    # Results
    simulation_result_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("simulation_results.id"),
        nullable=True
    )

    findings: Mapped[Optional[dict]] = mapped_column(JSON)  # What was learned
    action_items: Mapped[Optional[list]] = mapped_column(JSON)  # Follow-up actions
    evaluation_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-100

    # Optional Organization Link (can be standalone)
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("organizations.id"),
        nullable=True,
        index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    scenario_template: Mapped[Optional["ScenarioTemplateModel"]] = relationship(back_populates="exercises")
    simulation_result: Mapped[Optional["SimulationResultModel"]] = relationship()
    organization: Mapped[Optional["OrganizationModel"]] = relationship()

    __table_args__ = (
        Index('idx_exercise_tenant', 'tenant_id'),
        Index('idx_exercise_status', 'status'),
        Index('idx_exercise_scheduled', 'scheduled_at'),
    )


class PredictionModel(Base):
    """
    Predictions & Forecasts - Predictive analytics

    Can work standalone OR with organization data
    """
    __tablename__ = "predictions"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Prediction Type
    prediction_type: Mapped[str] = mapped_column(String(100), index=True)
    # Types: incident_forecast, recovery_time, impact_assessment, risk_probability,
    #        financial_forecast, resource_needs

    # Input
    scenario_template_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("scenario_templates.id"),
        nullable=True
    )
    input_parameters: Mapped[dict] = mapped_column(JSON)  # What we're predicting from

    # Output
    prediction_result: Mapped[Optional[dict]] = mapped_column(JSON)  # Prediction outcome
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)  # 0.0 - 1.0
    predicted_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    predicted_value: Mapped[Optional[float]] = mapped_column(Float)

    # Analysis
    factors: Mapped[Optional[dict]] = mapped_column(JSON)  # Contributing factors
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON)  # What to do
    assumptions: Mapped[Optional[list]] = mapped_column(JSON)  # Model assumptions

    # Model Info
    model_used: Mapped[Optional[str]] = mapped_column(String(100))
    # Models: linear_regression, monte_carlo, arima, bayesian, ml_model
    model_version: Mapped[Optional[str]] = mapped_column(String(50))
    methodology: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    # Status: pending, running, completed, failed

    # Optional Organization Link
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("organizations.id"),
        nullable=True,
        index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    scenario_template: Mapped[Optional["ScenarioTemplateModel"]] = relationship(back_populates="predictions")
    organization: Mapped[Optional["OrganizationModel"]] = relationship()

    __table_args__ = (
        Index('idx_prediction_tenant', 'tenant_id'),
        Index('idx_prediction_type', 'prediction_type'),
        Index('idx_prediction_status', 'status'),
    )


class BIAAnalysisModel(Base):
    """
    BIA Analysis Results - Business Impact Analysis

    Independent from organizations - analyze any processes
    """
    __tablename__ = "bia_analyses"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Identity
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Analysis Type
    analysis_type: Mapped[str] = mapped_column(String(100), index=True)
    # Types: full_bia, quick_assessment, rto_rpo_optimization, dependency_analysis

    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    # Status: pending, in_progress, completed, failed

    # Input Data
    processes: Mapped[dict] = mapped_column(JSON)  # Business processes analyzed
    context: Mapped[Optional[dict]] = mapped_column(JSON)  # Industry, size, geography

    # Results
    rto_recommendations: Mapped[Optional[dict]] = mapped_column(JSON)
    # Recovery Time Objective recommendations per process

    rpo_recommendations: Mapped[Optional[dict]] = mapped_column(JSON)
    # Recovery Point Objective recommendations per process

    financial_impact: Mapped[Optional[dict]] = mapped_column(JSON)
    # Financial impact analysis by process and time period

    recovery_strategies: Mapped[Optional[dict]] = mapped_column(JSON)
    # Recommended recovery strategies

    dependencies: Mapped[Optional[dict]] = mapped_column(JSON)
    # Process dependencies and criticality

    criticality_scores: Mapped[Optional[dict]] = mapped_column(JSON)
    # Criticality scores per process (0-100)

    # Analysis Settings
    time_horizons: Mapped[Optional[list]] = mapped_column(JSON)
    # Time periods analyzed: [1h, 4h, 24h, 3d, 7d, 30d]

    impact_categories: Mapped[Optional[list]] = mapped_column(JSON)
    # Categories: financial, operational, reputational, legal, safety

    # Optional Organization Link
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        ForeignKey("organizations.id"),
        nullable=True,
        index=True
    )

    # Execution Info
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    organization: Mapped[Optional["OrganizationModel"]] = relationship()

    __table_args__ = (
        Index('idx_bia_tenant', 'tenant_id'),
        Index('idx_bia_type', 'analysis_type'),
        Index('idx_bia_status', 'status'),
    )


# ============================================
# COMMUNITY LEVEL MODELS
# ============================================

class CommunityLearningModel(Base):
    """
    Community Learning - Knowledge exchange (anonymized)

    Stores anonymized learnings shared across the community
    """
    __tablename__ = "community_learnings"

    # Primary Key
    learning_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Content
    title: Mapped[str] = mapped_column(String(500))
    challenge: Mapped[str] = mapped_column(Text)
    solution: Mapped[str] = mapped_column(Text)
    outcome: Mapped[str] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSON)

    # Context (anonymized)
    industry: Mapped[str] = mapped_column(String(100), index=True)
    size_category: Mapped[str] = mapped_column(String(50), index=True)
    maturity_level: Mapped[str] = mapped_column(String(50), index=True)

    # Metrics
    effectiveness_score: Mapped[float] = mapped_column(Float)
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    average_rating: Mapped[Optional[float]] = mapped_column(Float)

    # Anonymization
    anonymization_level: Mapped[str] = mapped_column(String(50), default='standard')
    contributor_twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.id"))
    # PRIVATE - not exposed via API

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    feedback: Mapped[list["LearningFeedbackModel"]] = relationship(
        back_populates="learning",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_learning_industry', 'industry'),
        Index('idx_learning_size', 'size_category'),
        Index('idx_learning_maturity', 'maturity_level'),
        Index('idx_learning_effectiveness', 'effectiveness_score'),
        Index('idx_learning_created', 'created_at'),
    )


class LearningFeedbackModel(Base):
    """Learning Feedback - Track usage and effectiveness"""
    __tablename__ = "learning_feedback"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    learning_id: Mapped[str] = mapped_column(String(50), ForeignKey("community_learnings.learning_id"), index=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.id"), index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Feedback
    applied: Mapped[bool] = mapped_column(Boolean)
    was_helpful: Mapped[Optional[bool]] = mapped_column(Boolean)
    outcome_rating: Mapped[Optional[float]] = mapped_column(Float)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    learning: Mapped["CommunityLearningModel"] = relationship(back_populates="feedback")

    __table_args__ = (
        Index('idx_feedback_learning', 'learning_id'),
        Index('idx_feedback_twin', 'twin_id'),
    )


class UserNetworkingProfileModel(Base):
    """
    User Networking Profile - Professional profiles for people matching
    """
    __tablename__ = "user_networking_profiles"

    # Primary Key
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), primary_key=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.id"), index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Profile
    display_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(100), index=True)
    experience_level: Mapped[str] = mapped_column(String(50), index=True)
    bio: Mapped[Optional[str]] = mapped_column(Text)

    # Skills and Interests (stored as JSON arrays)
    bcm_certifications: Mapped[Optional[list]] = mapped_column(JSON)
    expertise_areas: Mapped[Optional[list]] = mapped_column(JSON)
    current_challenges: Mapped[Optional[list]] = mapped_column(JSON)
    learning_interests: Mapped[Optional[list]] = mapped_column(JSON)

    # Preferences
    languages: Mapped[Optional[list]] = mapped_column(JSON)
    open_to_mentoring: Mapped[bool] = mapped_column(Boolean, default=False)
    seeking_mentor: Mapped[bool] = mapped_column(Boolean, default=False)
    open_to_collaboration: Mapped[bool] = mapped_column(Boolean, default=False)

    # Privacy
    visibility_level: Mapped[str] = mapped_column(String(50), default='connections_only')
    show_organization: Mapped[bool] = mapped_column(Boolean, default=True)
    show_real_name: Mapped[bool] = mapped_column(Boolean, default=True)

    # Activity
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_profile_twin', 'twin_id'),
        Index('idx_profile_role', 'role'),
        Index('idx_profile_experience', 'experience_level'),
    )


class CommunityPrivacySettingsModel(Base):
    """Privacy Settings for Community features"""
    __tablename__ = "community_privacy_settings"

    # Primary Key
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Twin Matching Privacy
    allow_twin_matching: Mapped[bool] = mapped_column(Boolean, default=True)
    twin_visibility: Mapped[str] = mapped_column(String(50), default='community')

    # Knowledge Sharing Privacy
    share_learnings: Mapped[bool] = mapped_column(Boolean, default=True)
    anonymize_contributions: Mapped[bool] = mapped_column(Boolean, default=True)

    # People Matching Privacy
    show_in_people_search: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_connection_requests: Mapped[bool] = mapped_column(Boolean, default=True)

    # Data Sharing
    share_organizational_data: Mapped[bool] = mapped_column(Boolean, default=False)
    share_behavioral_patterns: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================
# PASSIVE LEARNING MODELS
# ============================================

class LearningEventModel(Base):
    """
    Learning Event - Individual learning events from platform interactions
    """
    __tablename__ = "learning_events"

    # Primary Key
    event_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.id"), index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Event details
    source: Mapped[str] = mapped_column(String(50), index=True)
    # Sources: bia, risk_assessment, incident, training, document
    event_type: Mapped[Optional[str]] = mapped_column(String(100))
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Extracted insights (JSONB for flexible schema)
    insights: Mapped[dict] = mapped_column(JSON)

    # Metadata
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_event_twin', 'twin_id'),
        Index('idx_event_source', 'source'),
        Index('idx_event_created', 'created_at'),
    )


class LearningInsightModel(Base):
    """
    Learning Insight - Accumulated insights (aggregated from events)
    """
    __tablename__ = "learning_insights"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.id"), index=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Insight details
    insight_type: Mapped[str] = mapped_column(String(100), index=True)
    # Types: risk_tolerance, decision_speed, organizational_culture,
    #        communication_style, knowledge_level, etc.

    insight_value: Mapped[dict] = mapped_column(JSON)
    # Value can be string, number, array, or complex object

    # Metadata
    confidence: Mapped[float] = mapped_column(Float)
    source_event_count: Mapped[int] = mapped_column(Integer, default=1)
    last_updated_from_event_id: Mapped[Optional[str]] = mapped_column(String(50))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_insight_twin', 'twin_id'),
        Index('idx_insight_type', 'insight_type'),
        Index('idx_insight_updated', 'updated_at'),
        # Unique constraint: one insight per twin per type
        UniqueConstraint('twin_id', 'insight_type', name='uq_twin_insight_type'),
    )


class OrganizationContextModel(Base):
    """
    Organization Context - Pre-built context cache for performance

    Stores the complete organizational context built from insights
    """
    __tablename__ = "organization_contexts"

    # Primary Key
    twin_id: Mapped[str] = mapped_column(String(50), ForeignKey("organizations.id"), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tenants.id"), index=True)

    # Culture & Behavior
    organizational_culture: Mapped[Optional[str]] = mapped_column(String(100))
    decision_speed: Mapped[Optional[str]] = mapped_column(String(50))
    thoroughness: Mapped[Optional[str]] = mapped_column(String(50))
    learning_orientation: Mapped[Optional[str]] = mapped_column(String(50))

    # Risk Profile
    risk_tolerance: Mapped[Optional[str]] = mapped_column(String(50))
    risk_appetite: Mapped[Optional[str]] = mapped_column(String(50))
    control_preference: Mapped[Optional[str]] = mapped_column(String(50))

    # Communication
    communication_style: Mapped[Optional[str]] = mapped_column(String(50))
    response_speed: Mapped[Optional[str]] = mapped_column(String(50))

    # Operational Patterns
    avg_rto_hours: Mapped[Optional[float]] = mapped_column(Float)
    dependency_count: Mapped[Optional[int]] = mapped_column(Integer)
    primary_risk_focus: Mapped[Optional[str]] = mapped_column(String(100))

    # Knowledge & Capability
    knowledge_level: Mapped[Optional[str]] = mapped_column(String(50))
    knowledge_gaps: Mapped[Optional[list]] = mapped_column(JSON)
    engagement_level: Mapped[Optional[str]] = mapped_column(String(50))

    # BCM Maturity Indicators
    critical_functions: Mapped[Optional[list]] = mapped_column(JSON)
    recovery_time_hours: Mapped[Optional[float]] = mapped_column(Float)

    # Patterns & Trends (JSONB for flexibility)
    patterns: Mapped[Optional[dict]] = mapped_column(JSON)
    trends: Mapped[Optional[dict]] = mapped_column(JSON)

    # Metadata
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_context_twin', 'twin_id'),
        Index('idx_context_updated', 'last_updated'),
        Index('idx_context_confidence', 'confidence_score'),
    )
