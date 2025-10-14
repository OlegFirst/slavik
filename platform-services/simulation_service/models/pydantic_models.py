"""
Pydantic models for Simulation & Modeling Service

Type-safe data validation models for simulation specifications, scenarios,
results, and configuration.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class EngineType(str, Enum):
    """Simulation engine types"""
    JAAMSIM = "jaamsim"
    SIMPY = "simpy"
    MONTE_CARLO = "monte_carlo"
    WHAT_IF = "what_if"
    WORKFLOW = "workflow"  # For platform internal testing
    MOCK = "mock"


class SimulationStatus(str, Enum):
    """Simulation execution status"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExerciseType(str, Enum):
    """Types of BCM exercises"""
    TABLETOP = "tabletop"
    WALKTHROUGH = "walkthrough"
    FUNCTIONAL = "functional"
    FULL_SCALE = "full_scale"
    SIMULATION = "simulation"
    DRILL = "drill"


class ScenarioCategory(str, Enum):
    """Scenario categories"""
    DISASTER_RECOVERY = "disaster_recovery"
    CYBER_SECURITY = "cyber_security"
    SUPPLY_CHAIN = "supply_chain"
    PANDEMIC = "pandemic"
    FACILITY_DAMAGE = "facility_damage"
    SYSTEM_FAILURE = "system_failure"
    COMMUNICATION = "communication"
    BIA_EXERCISE = "bia_exercise"
    INCIDENT_RESPONSE = "incident_response"
    CRISIS_MANAGEMENT = "crisis_management"
    CUSTOM = "custom"


class MetricType(str, Enum):
    """Types of simulation metrics"""
    RTO_ACHIEVEMENT = "rto_achievement"
    RPO_ACHIEVEMENT = "rpo_achievement"
    RESOURCE_UTILIZATION = "resource_utilization"
    COST_IMPACT = "cost_impact"
    COMMUNICATION_EFFECTIVENESS = "communication_effectiveness"
    DECISION_SPEED = "decision_speed"
    RECOVERY_SUCCESS_RATE = "recovery_success_rate"
    PARTICIPANT_ENGAGEMENT = "participant_engagement"


class DashboardType(str, Enum):
    """Dashboard visualization types"""
    REAL_TIME = "real_time"
    SUMMARY = "summary"
    DETAILED = "detailed"
    EXECUTIVE = "executive"
    COMPARATIVE = "comparative"


class ChartType(str, Enum):
    """Chart types for visualization"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GANTT = "gantt"
    TIMELINE = "timeline"


class ReportFormat(str, Enum):
    """Report output formats"""
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    JSON = "json"


class ReportTemplate(str, Enum):
    """Report templates"""
    ISO_22301 = "iso_22301"
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_REPORT = "technical_report"
    COMPARATIVE_ANALYSIS = "comparative_analysis"


# ============================================================================
# CORE MODELS
# ============================================================================

class TaskSpecification(BaseModel):
    """
    AI-generated task specification for simulation

    This model represents a complete specification for a simulation,
    including the goal, constraints, context, and execution parameters.
    """

    id: str = Field(
        default_factory=lambda: f"spec_{uuid.uuid4().hex[:12]}",
        description="Unique specification identifier"
    )

    goal: str = Field(
        ...,
        description="Primary objective of the simulation",
        min_length=10,
        max_length=500
    )

    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Constraints for simulation execution"
    )

    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context information (organization type, size, etc.)"
    )

    engine_preference: Optional[EngineType] = Field(
        default=None,
        description="Preferred simulation engine"
    )

    max_duration: int = Field(
        default=3600,
        description="Maximum simulation duration in seconds",
        ge=60,
        le=28800  # 8 hours max
    )

    processes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Process definitions for simulation"
    )

    resources: Dict[str, int] = Field(
        default_factory=dict,
        description="Resource allocations (staff, equipment, etc.)"
    )

    scenarios: List[str] = Field(
        default_factory=list,
        description="Scenario IDs to include"
    )

    alternatives: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative scenarios for what-if analysis"
    )

    monte_carlo_iterations: Optional[int] = Field(
        default=None,
        description="Number of Monte Carlo iterations",
        ge=100,
        le=100000
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )

    created_by: str = Field(
        ...,
        description="User ID who created this specification"
    )

    organization_id: str = Field(
        ...,
        description="Organization ID"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    @field_validator('goal')
    @classmethod
    def validate_goal(cls, v: str) -> str:
        """Validate goal is not empty and reasonable"""
        if not v.strip():
            raise ValueError("Goal cannot be empty")
        if len(v.strip()) < 10:
            raise ValueError("Goal too short, provide more detail (min 10 characters)")
        return v.strip()

    @field_validator('max_duration')
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Validate duration is reasonable"""
        if v < 60:
            raise ValueError("Duration must be at least 60 seconds")
        if v > 28800:
            raise ValueError("Duration cannot exceed 8 hours (28800 seconds)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "goal": "Test BIA process resilience under cyber incident scenario",
                "constraints": {
                    "max_duration": 7200,
                    "participants": 10,
                    "complexity": "high"
                },
                "context": {
                    "organization_type": "hospital",
                    "organization_size": "large",
                    "department": "emergency",
                    "previous_exercises": []
                },
                "engine_preference": "jaamsim",
                "max_duration": 7200,
                "processes": [
                    {"name": "patient_admission", "priority": "critical"},
                    {"name": "emergency_response", "priority": "critical"}
                ],
                "resources": {
                    "medical_staff": 50,
                    "beds": 100,
                    "equipment": 30
                },
                "created_by": "user_123",
                "organization_id": "org_456"
            }
        }


class VisualizationConfig(BaseModel):
    """
    Configuration for simulation visualization

    Controls how simulation results are displayed in real-time
    and in final reports.
    """

    dashboard_type: DashboardType = Field(
        default=DashboardType.REAL_TIME,
        description="Type of dashboard to display"
    )

    metrics: List[str] = Field(
        default_factory=lambda: ["progress", "events", "resources"],
        description="Metrics to track and display"
    )

    update_interval: int = Field(
        default=5,
        description="Update interval in seconds",
        ge=1,
        le=60
    )

    chart_types: List[ChartType] = Field(
        default_factory=lambda: [ChartType.LINE, ChartType.BAR],
        description="Chart types to use"
    )

    enable_3d: bool = Field(
        default=False,
        description="Enable 3D visualization (experimental)"
    )

    enable_real_time_streaming: bool = Field(
        default=True,
        description="Enable WebSocket streaming"
    )

    max_datapoints: int = Field(
        default=1000,
        description="Maximum datapoints to display",
        ge=100,
        le=10000
    )

    show_predictions: bool = Field(
        default=True,
        description="Show ML predictions during simulation"
    )

    @field_validator('update_interval')
    @classmethod
    def validate_interval(cls, v: int) -> int:
        """Validate update interval is reasonable"""
        if v < 1:
            raise ValueError("Update interval must be at least 1 second")
        if v > 60:
            raise ValueError("Update interval cannot exceed 60 seconds")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "dashboard_type": "real_time",
                "metrics": ["progress", "events", "resources", "incidents"],
                "update_interval": 5,
                "chart_types": ["line", "bar", "heatmap"],
                "enable_3d": False,
                "enable_real_time_streaming": True,
                "max_datapoints": 1000,
                "show_predictions": True
            }
        }


class IntegrationConfig(BaseModel):
    """
    Configuration for platform integrations

    Controls which platform services are enabled for this simulation
    and what auto-integration features should be active.
    """

    eventbus_enabled: bool = Field(
        default=True,
        description="Enable EventBus integration (CRITICAL)"
    )

    orchestrator_enabled: bool = Field(
        default=True,
        description="Enable AI Orchestrator integration"
    )

    workflow_enabled: bool = Field(
        default=True,
        description="Enable Workflow Intelligence integration"
    )

    knowledge_enabled: bool = Field(
        default=True,
        description="Enable Knowledge Center integration"
    )

    community_enabled: bool = Field(
        default=True,
        description="Enable Community Intelligence integration"
    )

    predictive_enabled: bool = Field(
        default=False,
        description="Enable Predictive Journey integration"
    )

    digital_twin_enabled: bool = Field(
        default=False,
        description="Enable Digital Twin integration (optional)"
    )

    foundation_enabled: bool = Field(
        default=True,
        description="Enable AI Foundation integration (RAG, LLM, ML)"
    )

    auto_pdca: bool = Field(
        default=True,
        description="Automatically create PDCA cycle after simulation"
    )

    auto_knowledge_storage: bool = Field(
        default=True,
        description="Automatically store knowledge in Knowledge Center"
    )

    auto_community_contribution: bool = Field(
        default=True,
        description="Automatically contribute to Community Intelligence"
    )

    auto_contribution_min_quality_score: float = Field(
        default=8.0,
        description="Minimum quality score for auto-contribution",
        ge=0.0,
        le=10.0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "eventbus_enabled": True,
                "orchestrator_enabled": True,
                "workflow_enabled": True,
                "knowledge_enabled": True,
                "community_enabled": True,
                "predictive_enabled": False,
                "digital_twin_enabled": False,
                "foundation_enabled": True,
                "auto_pdca": True,
                "auto_knowledge_storage": True,
                "auto_community_contribution": True,
                "auto_contribution_min_quality_score": 8.0
            }
        }


class EngineConfig(BaseModel):
    """
    Configuration for simulation engine

    Engine-specific settings and resource limits.
    """

    engine_type: EngineType = Field(
        ...,
        description="Simulation engine type"
    )

    # Resource limits
    max_memory_mb: int = Field(
        default=2048,
        description="Maximum memory usage in MB",
        ge=512,
        le=16384
    )

    max_cpu_cores: int = Field(
        default=2,
        description="Maximum CPU cores to use",
        ge=1,
        le=8
    )

    timeout_seconds: int = Field(
        default=3600,
        description="Simulation timeout in seconds",
        ge=60,
        le=28800
    )

    # Engine-specific paths
    executable_path: Optional[str] = Field(
        default=None,
        description="Path to engine executable (for JaamSim)"
    )

    working_directory: Optional[str] = Field(
        default=None,
        description="Working directory for simulation files"
    )

    # Engine-specific settings
    jaamsim_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="JaamSim specific settings"
    )

    simpy_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="SimPy specific settings"
    )

    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom engine settings"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "engine_type": "jaamsim",
                "max_memory_mb": 2048,
                "max_cpu_cores": 2,
                "timeout_seconds": 7200,
                "executable_path": "/opt/jaamsim/JaamSim2023-03.jar",
                "working_directory": "/tmp/simulations",
                "jaamsim_settings": {
                    "graphics_mode": "headless",
                    "log_level": "INFO"
                }
            }
        }


class ReportConfig(BaseModel):
    """
    Configuration for report generation

    Controls report format, template, and content.
    """

    format: ReportFormat = Field(
        default=ReportFormat.PDF,
        description="Report output format"
    )

    template: ReportTemplate = Field(
        default=ReportTemplate.ISO_22301,
        description="Report template to use"
    )

    include_charts: bool = Field(
        default=True,
        description="Include visualization charts"
    )

    include_timeline: bool = Field(
        default=True,
        description="Include simulation timeline"
    )

    include_recommendations: bool = Field(
        default=True,
        description="Include recommendations section"
    )

    include_raw_data: bool = Field(
        default=False,
        description="Include raw simulation data"
    )

    language: str = Field(
        default="en",
        description="Report language (ISO 639-1 code)"
    )

    custom_sections: List[str] = Field(
        default_factory=list,
        description="Custom sections to include"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "format": "pdf",
                "template": "iso_22301",
                "include_charts": True,
                "include_timeline": True,
                "include_recommendations": True,
                "include_raw_data": False,
                "language": "en"
            }
        }


class Scenario(BaseModel):
    """
    Simulation scenario definition

    Describes a complete scenario including exercises, incidents, and evaluation criteria.
    Enhanced with AI classification and incident management fields from BCM Incident module.
    """

    id: str = Field(
        default_factory=lambda: f"scenario_{uuid.uuid4().hex[:12]}",
        description="Unique scenario identifier"
    )

    name: str = Field(
        ...,
        description="Scenario name",
        min_length=3,
        max_length=200
    )

    description: str = Field(
        ...,
        description="Detailed scenario description",
        min_length=10
    )

    category: ScenarioCategory = Field(
        ...,
        description="Scenario category"
    )

    exercise_type: ExerciseType = Field(
        ...,
        description="Type of exercise"
    )

    # Duration and complexity
    duration_minutes: int = Field(
        ...,
        description="Expected duration in minutes",
        gt=0,
        le=480  # 8 hours max
    )

    complexity_level: int = Field(
        default=1,
        description="Complexity level (1-5)",
        ge=1,
        le=5
    )

    # === AI CLASSIFICATION FIELDS (from BCM Incident) ===
    ai_classification_confidence: Optional[float] = Field(
        default=None,
        description="AI confidence in scenario classification (0-100%)",
        ge=0.0,
        le=100.0
    )

    ai_recommended_engine: Optional[str] = Field(
        default=None,
        description="AI-recommended simulation engine"
    )

    ai_risk_score: Optional[float] = Field(
        default=None,
        description="AI-calculated risk score (0-100)",
        ge=0.0,
        le=100.0
    )

    ai_matched_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords matched during AI classification"
    )

    # === SEVERITY AND PRIORITY (from BCM Incident) ===
    severity: Optional[str] = Field(
        default=None,
        description="Scenario severity: low, medium, high, critical"
    )

    priority: int = Field(
        default=0,
        description="Priority level (0=Normal, 1=Low, 2=High, 3=Very High, 4=Critical)",
        ge=0,
        le=4
    )

    crisis_level: Optional[int] = Field(
        default=None,
        description="Crisis level (0-5): 0=None, 1=Minor, 2=Significant, 3=Major, 4=Severe, 5=Catastrophic",
        ge=0,
        le=5
    )

    # === RTO/RPO METRICS (from BCM Incident) ===
    target_rto: Optional[float] = Field(
        default=None,
        description="Target Recovery Time Objective (hours)",
        ge=0.0
    )

    target_rpo: Optional[float] = Field(
        default=None,
        description="Target Recovery Point Objective (hours)",
        ge=0.0
    )

    # Scenario content
    incidents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Incident definitions"
    )

    affected_processes: List[str] = Field(
        default_factory=list,
        description="Affected business processes"
    )

    affected_systems: Optional[str] = Field(
        default=None,
        description="Systems affected by this scenario"
    )

    affected_locations: Optional[str] = Field(
        default=None,
        description="Geographical locations affected"
    )

    impact_areas: List[str] = Field(
        default_factory=list,
        description="Areas of impact"
    )

    business_impact_level: Optional[str] = Field(
        default=None,
        description="Business impact level: none, low, medium, high, critical"
    )

    estimated_financial_impact: Optional[float] = Field(
        default=None,
        description="Estimated financial impact (currency amount)",
        ge=0.0
    )

    recovery_objectives: Dict[str, Any] = Field(
        default_factory=dict,
        description="Recovery objectives (RTO, RPO)"
    )

    recovery_actions: Optional[str] = Field(
        default=None,
        description="Recommended recovery actions"
    )

    # Evaluation
    success_criteria: List[str] = Field(
        default_factory=list,
        description="Success criteria"
    )

    key_metrics: List[str] = Field(
        default_factory=list,
        description="Key metrics to measure"
    )

    # Resources and constraints
    required_participants: int = Field(
        default=1,
        description="Required number of participants",
        gt=0
    )

    available_resources: Dict[str, Any] = Field(
        default_factory=dict,
        description="Available resources"
    )

    constraints: List[str] = Field(
        default_factory=list,
        description="Scenario constraints"
    )

    # Metadata
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags"
    )

    source: str = Field(
        default="custom",
        description="Scenario source (custom, community, rag, ai_generated)"
    )

    quality_score: Optional[float] = Field(
        default=None,
        description="Quality score (0-10)",
        ge=0.0,
        le=10.0
    )

    usage_count: int = Field(
        default=0,
        description="Number of times used"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )

    created_by: str = Field(
        ...,
        description="Creator user ID"
    )

    organization_id: str = Field(
        ...,
        description="Organization ID"
    )

    @field_validator('duration_minutes')
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Validate duration is reasonable"""
        if v > 480:
            raise ValueError('Exercise duration cannot exceed 8 hours (480 minutes)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Hospital Cyber Attack Response",
                "description": "Simulated ransomware attack on hospital IT systems",
                "category": "cyber_security",
                "exercise_type": "functional",
                "duration_minutes": 120,
                "complexity_level": 4,
                "incidents": [
                    {"type": "ransomware", "timing": "T+15min", "severity": "critical"}
                ],
                "affected_processes": ["patient_records", "medication_management"],
                "success_criteria": ["System restored within RTO", "No data loss"],
                "required_participants": 8,
                "created_by": "user_123",
                "organization_id": "org_456"
            }
        }


class SimulationEvent(BaseModel):
    """
    Event that occurred during simulation

    Tracks all events, decisions, incidents, and state changes.
    """

    id: str = Field(
        default_factory=lambda: f"event_{uuid.uuid4().hex[:12]}",
        description="Unique event identifier"
    )

    simulation_id: str = Field(
        ...,
        description="Parent simulation ID"
    )

    event_type: str = Field(
        ...,
        description="Event type (incident, decision, state_change, etc.)"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp"
    )

    elapsed_seconds: int = Field(
        ...,
        description="Seconds elapsed since simulation start"
    )

    description: str = Field(
        ...,
        description="Event description"
    )

    severity: Optional[str] = Field(
        default=None,
        description="Event severity (low, medium, high, critical)"
    )

    actors: List[str] = Field(
        default_factory=list,
        description="Actors involved in event"
    )

    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event data payload"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "sim_abc123",
                "event_type": "incident",
                "elapsed_seconds": 900,
                "description": "Ransomware detected on file server",
                "severity": "critical",
                "actors": ["it_admin", "security_team"],
                "data": {
                    "affected_systems": ["file_server_01"],
                    "response_time": 45
                }
            }
        }


class ExerciseMetrics(BaseModel):
    """
    Exercise performance metrics

    Comprehensive metrics collected during and after simulation.
    """

    # Core BCM metrics
    rto_achieved: Dict[str, float] = Field(
        default_factory=dict,
        description="RTO achievements by process (in seconds)"
    )

    rpo_achieved: Dict[str, float] = Field(
        default_factory=dict,
        description="RPO achievements by process"
    )

    recovery_success_rate: float = Field(
        default=0.0,
        description="Overall recovery success rate",
        ge=0.0,
        le=1.0
    )

    # Performance metrics
    decision_times: List[float] = Field(
        default_factory=list,
        description="Decision times in seconds"
    )

    communication_delays: List[float] = Field(
        default_factory=list,
        description="Communication delays in seconds"
    )

    resource_utilization: Dict[str, float] = Field(
        default_factory=dict,
        description="Resource utilization rates (0-1)"
    )

    # Cost metrics
    estimated_cost: float = Field(
        default=0.0,
        description="Estimated exercise cost"
    )

    recovery_cost: float = Field(
        default=0.0,
        description="Estimated recovery cost"
    )

    downtime_cost: float = Field(
        default=0.0,
        description="Estimated downtime cost"
    )

    # Quality metrics
    participant_satisfaction: Optional[float] = Field(
        default=None,
        description="Participant satisfaction (1-5)",
        ge=1.0,
        le=5.0
    )

    learning_objectives_met: float = Field(
        default=0.0,
        description="Learning objectives achievement rate",
        ge=0.0,
        le=1.0
    )

    # Compliance metrics
    regulatory_requirements_tested: int = Field(
        default=0,
        description="Number of regulatory requirements tested"
    )

    compliance_gaps_identified: int = Field(
        default=0,
        description="Number of compliance gaps found"
    )

    # Incident metrics
    incidents_total: int = Field(
        default=0,
        description="Total incidents injected"
    )

    incidents_handled: int = Field(
        default=0,
        description="Incidents successfully handled"
    )

    average_response_time: float = Field(
        default=0.0,
        description="Average incident response time in seconds"
    )

    # Timestamps
    measured_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Measurement timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rto_achieved": {
                    "patient_records": 300,
                    "medication_system": 450
                },
                "recovery_success_rate": 0.95,
                "decision_times": [45, 60, 30, 90],
                "resource_utilization": {
                    "it_staff": 0.85,
                    "backup_systems": 0.70
                },
                "incidents_total": 5,
                "incidents_handled": 4,
                "average_response_time": 180
            }
        }


class SimulationResult(BaseModel):
    """
    Complete simulation results

    Comprehensive results including metrics, findings, and recommendations.
    """

    id: str = Field(
        default_factory=lambda: f"result_{uuid.uuid4().hex[:12]}",
        description="Unique result identifier"
    )

    simulation_id: str = Field(
        ...,
        description="Simulation identifier"
    )

    scenario_id: str = Field(
        ...,
        description="Scenario identifier"
    )

    specification_id: str = Field(
        ...,
        description="Specification identifier"
    )

    # Execution summary
    status: SimulationStatus = Field(
        ...,
        description="Final status"
    )

    duration_seconds: int = Field(
        ...,
        description="Total duration in seconds"
    )

    participants_count: int = Field(
        default=0,
        description="Number of participants"
    )

    # Results
    metrics: ExerciseMetrics = Field(
        ...,
        description="Exercise metrics"
    )

    success_criteria_met: Dict[str, bool] = Field(
        default_factory=dict,
        description="Success criteria results"
    )

    key_findings: List[str] = Field(
        default_factory=list,
        description="Key findings and observations"
    )

    lessons_learned: List[str] = Field(
        default_factory=list,
        description="Lessons learned during exercise"
    )

    best_practices: List[str] = Field(
        default_factory=list,
        description="Best practices identified"
    )

    # === RTO/RPO ACTUAL RESULTS (from BCM Incident) ===
    actual_rto: Optional[float] = Field(
        default=None,
        description="Actual Recovery Time Objective achieved (hours)",
        ge=0.0
    )

    actual_rpo: Optional[float] = Field(
        default=None,
        description="Actual Recovery Point Objective achieved (hours)",
        ge=0.0
    )

    rto_met: Optional[bool] = Field(
        default=None,
        description="Whether RTO target was met"
    )

    rpo_met: Optional[bool] = Field(
        default=None,
        description="Whether RPO target was met"
    )

    # === AI ANALYSIS (from BCM Incident) ===
    ai_recommendations: Optional[str] = Field(
        default=None,
        description="AI-generated recommendations"
    )

    ai_effectiveness_score: Optional[float] = Field(
        default=None,
        description="AI-calculated effectiveness score (0-100)",
        ge=0.0,
        le=100.0
    )

    ai_learning_progress: Optional[float] = Field(
        default=None,
        description="AI-assessed learning progress (0-100)",
        ge=0.0,
        le=100.0
    )

    similar_scenarios: List[str] = Field(
        default_factory=list,
        description="IDs of similar scenarios (AI-identified)"
    )

    # Detailed results
    timeline: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Simulation timeline"
    )

    decisions_made: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Decisions made during exercise"
    )

    issues_encountered: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Issues encountered"
    )

    # Recommendations
    improvement_areas: List[str] = Field(
        default_factory=list,
        description="Areas for improvement"
    )

    recommendations: List[str] = Field(
        default_factory=list,
        description="Specific recommendations"
    )

    next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next steps"
    )

    # === PREVENTIVE MEASURES (from BCM Incident) ===
    preventive_measures: List[str] = Field(
        default_factory=list,
        description="Preventive measures to avoid similar issues"
    )

    root_cause_analysis: Optional[str] = Field(
        default=None,
        description="Root cause analysis of failures/issues"
    )

    # Quality assessment
    quality_score: float = Field(
        default=0.0,
        description="Overall quality score (0-10)",
        ge=0.0,
        le=10.0
    )

    contribution_worthy: bool = Field(
        default=False,
        description="Worthy of community contribution"
    )

    # Summary
    summary: str = Field(
        default="",
        description="Executive summary"
    )

    # Files
    report_files: List[str] = Field(
        default_factory=list,
        description="Generated report file paths"
    )

    log_files: List[str] = Field(
        default_factory=list,
        description="Simulation log file paths"
    )

    # Timestamps
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Result generation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "sim_abc123",
                "scenario_id": "scenario_xyz789",
                "specification_id": "spec_def456",
                "status": "completed",
                "duration_seconds": 7200,
                "participants_count": 8,
                "key_findings": [
                    "Response time exceeded RTO by 15%",
                    "Backup systems performed well"
                ],
                "recommendations": [
                    "Increase backup capacity",
                    "Update recovery procedures"
                ],
                "quality_score": 8.5,
                "contribution_worthy": True
            }
        }


class Simulation(BaseModel):
    """
    Main simulation model

    Represents a complete simulation instance with all its configuration and state.
    """

    id: str = Field(
        default_factory=lambda: f"sim_{uuid.uuid4().hex[:12]}",
        description="Unique simulation identifier"
    )

    specification_id: str = Field(
        ...,
        description="Task specification ID"
    )

    scenario_id: str = Field(
        ...,
        description="Scenario ID"
    )

    # Engine and configuration
    engine: EngineType = Field(
        ...,
        description="Simulation engine to use"
    )

    engine_config: EngineConfig = Field(
        ...,
        description="Engine configuration"
    )

    visualization_config: VisualizationConfig = Field(
        default_factory=VisualizationConfig,
        description="Visualization configuration"
    )

    integration_config: IntegrationConfig = Field(
        default_factory=IntegrationConfig,
        description="Integration configuration"
    )

    report_config: ReportConfig = Field(
        default_factory=ReportConfig,
        description="Report configuration"
    )

    # Status tracking
    status: SimulationStatus = Field(
        default=SimulationStatus.PENDING,
        description="Current status"
    )

    progress_percentage: float = Field(
        default=0.0,
        description="Completion percentage",
        ge=0.0,
        le=100.0
    )

    current_phase: Optional[str] = Field(
        default=None,
        description="Current simulation phase"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )

    started_at: Optional[datetime] = Field(
        default=None,
        description="Start timestamp"
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        description="Completion timestamp"
    )

    # Participants
    created_by: str = Field(
        ...,
        description="Creator user ID"
    )

    organization_id: str = Field(
        ...,
        description="Organization ID"
    )

    participants: List[str] = Field(
        default_factory=list,
        description="Participant user IDs"
    )

    observers: List[str] = Field(
        default_factory=list,
        description="Observer user IDs"
    )

    # Results
    result_id: Optional[str] = Field(
        default=None,
        description="Result ID (when completed)"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )

    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "specification_id": "spec_abc123",
                "scenario_id": "scenario_xyz789",
                "engine": "jaamsim",
                "engine_config": {
                    "engine_type": "jaamsim",
                    "max_memory_mb": 2048,
                    "max_cpu_cores": 2
                },
                "status": "running",
                "progress_percentage": 45.5,
                "created_by": "user_123",
                "organization_id": "org_456"
            }
        }


class SimulationRequest(BaseModel):
    """
    Request to create and optionally start a simulation

    Used by API endpoints to create new simulations.
    """

    specification: TaskSpecification = Field(
        ...,
        description="Task specification"
    )

    scenario_id: Optional[str] = Field(
        default=None,
        description="Scenario ID (if not provided, will be generated)"
    )

    engine: Optional[EngineType] = Field(
        default=None,
        description="Preferred engine (auto-select if not provided)"
    )

    engine_config: Optional[EngineConfig] = Field(
        default=None,
        description="Engine configuration (use defaults if not provided)"
    )

    visualization_config: Optional[VisualizationConfig] = Field(
        default=None,
        description="Visualization configuration"
    )

    integration_config: Optional[IntegrationConfig] = Field(
        default=None,
        description="Integration configuration"
    )

    report_config: Optional[ReportConfig] = Field(
        default=None,
        description="Report configuration"
    )

    auto_start: bool = Field(
        default=False,
        description="Start simulation immediately after creation"
    )

    participants: List[str] = Field(
        default_factory=list,
        description="Participant user IDs"
    )

    observers: List[str] = Field(
        default_factory=list,
        description="Observer user IDs"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "specification": {
                    "goal": "Test BIA process resilience",
                    "created_by": "user_123",
                    "organization_id": "org_456"
                },
                "engine": "jaamsim",
                "auto_start": True,
                "participants": ["user_123", "user_456"]
            }
        }


class SimulationState(BaseModel):
    """
    Current simulation state for real-time monitoring

    Lightweight model for WebSocket streaming and status checks.
    """

    simulation_id: str = Field(
        ...,
        description="Simulation identifier"
    )

    status: SimulationStatus = Field(
        ...,
        description="Current status"
    )

    progress_percentage: float = Field(
        ...,
        description="Completion percentage",
        ge=0.0,
        le=100.0
    )

    current_phase: Optional[str] = Field(
        default=None,
        description="Current simulation phase"
    )

    elapsed_seconds: int = Field(
        default=0,
        description="Elapsed time in seconds"
    )

    estimated_remaining: Optional[int] = Field(
        default=None,
        description="Estimated remaining time in seconds"
    )

    message: Optional[str] = Field(
        default=None,
        description="Status message"
    )

    # Real-time metrics
    events_processed: int = Field(
        default=0,
        description="Events processed so far"
    )

    incidents_injected: int = Field(
        default=0,
        description="Incidents injected"
    )

    decisions_made: int = Field(
        default=0,
        description="Decisions made"
    )

    # Resource usage
    cpu_usage: Optional[float] = Field(
        default=None,
        description="CPU usage percentage"
    )

    memory_usage: Optional[float] = Field(
        default=None,
        description="Memory usage MB"
    )

    # Timestamps
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "sim_abc123",
                "status": "running",
                "progress_percentage": 65.5,
                "current_phase": "Incident injection phase",
                "elapsed_seconds": 3600,
                "estimated_remaining": 1800,
                "events_processed": 450,
                "incidents_injected": 3,
                "cpu_usage": 45.2,
                "memory_usage": 1024.5
            }
        }
