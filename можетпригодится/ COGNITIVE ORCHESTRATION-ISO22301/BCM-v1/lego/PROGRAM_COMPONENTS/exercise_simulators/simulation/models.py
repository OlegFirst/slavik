"""Pydantic models for Simulation Adapter"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum

class SimulationEngine(str, Enum):
    """Supported simulation engines"""
    JAAMSIM = "jaamsim"
    ANYLOGIC = "anylogic"
    CUSTOM = "custom"
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

class ScenarioCategory(str, Enum):
    """Scenario categories"""
    DISASTER_RECOVERY = "disaster_recovery"
    CYBER_SECURITY = "cyber_security"
    SUPPLY_CHAIN = "supply_chain"
    PANDEMIC = "pandemic"
    FACILITY_DAMAGE = "facility_damage"
    SYSTEM_FAILURE = "system_failure"
    COMMUNICATION = "communication"
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

class SimulationParameter(BaseModel):
    """Simulation parameter configuration"""
    name: str = Field(..., description="Parameter name")
    value: Union[str, int, float, bool] = Field(..., description="Parameter value")
    type: str = Field(..., description="Parameter type")
    description: Optional[str] = Field(None, description="Parameter description")
    min_value: Optional[float] = Field(None, description="Minimum allowed value")
    max_value: Optional[float] = Field(None, description="Maximum allowed value")
    unit: Optional[str] = Field(None, description="Value unit")

class ExerciseScenario(BaseModel):
    """BCM exercise scenario definition"""
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    category: ScenarioCategory = Field(..., description="Scenario category")
    exercise_type: ExerciseType = Field(..., description="Exercise type")
    
    # Scenario parameters
    duration_minutes: int = Field(..., gt=0, description="Expected duration in minutes")
    complexity_level: int = Field(default=1, ge=1, le=5, description="Complexity level (1-5)")
    participant_count: int = Field(default=1, gt=0, description="Number of participants")
    
    # Simulation configuration
    simulation_engine: SimulationEngine = Field(default=SimulationEngine.MOCK, description="Simulation engine")
    parameters: List[SimulationParameter] = Field(default_factory=list, description="Simulation parameters")
    
    # BCM specific settings
    affected_processes: List[str] = Field(default_factory=list, description="Affected business processes")
    impact_areas: List[str] = Field(default_factory=list, description="Impact areas")
    recovery_objectives: Dict[str, Any] = Field(default_factory=dict, description="Recovery objectives")
    
    # Evaluation criteria
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    key_metrics: List[str] = Field(default_factory=list, description="Key metrics to measure")
    
    # Resources and constraints
    available_resources: Dict[str, Any] = Field(default_factory=dict, description="Available resources")
    constraints: List[str] = Field(default_factory=list, description="Scenario constraints")
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v > 480:  # 8 hours max
            raise ValueError('Exercise duration cannot exceed 8 hours (480 minutes)')
        return v

class SimulationRequest(BaseModel):
    """Request to start simulation"""
    tenant_id: str = Field(..., description="Tenant identifier")
    exercise_id: str = Field(..., description="Exercise identifier")
    scenario: ExerciseScenario = Field(..., description="Exercise scenario")
    
    # Execution settings
    auto_start: bool = Field(default=True, description="Start simulation immediately")
    save_results: bool = Field(default=True, description="Save simulation results")
    notify_on_completion: bool = Field(default=True, description="Send notification on completion")
    
    # Participants
    participants: List[str] = Field(default_factory=list, description="Participant user IDs")
    observers: List[str] = Field(default_factory=list, description="Observer user IDs")
    
    # Custom settings
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="Custom configuration")

class SimulationState(BaseModel):
    """Current simulation state"""
    simulation_id: str = Field(..., description="Simulation identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    exercise_id: str = Field(..., description="Exercise identifier")
    status: SimulationStatus = Field(..., description="Current status")
    
    # Progress tracking
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Completion percentage")
    current_phase: Optional[str] = Field(None, description="Current simulation phase")
    elapsed_time: int = Field(default=0, description="Elapsed time in seconds")
    estimated_remaining: Optional[int] = Field(None, description="Estimated remaining time in seconds")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # Status details
    message: Optional[str] = Field(None, description="Status message")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Resource usage
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    memory_usage: Optional[float] = Field(None, description="Memory usage MB")
    
class ExerciseMetrics(BaseModel):
    """Exercise performance metrics"""
    exercise_id: str = Field(..., description="Exercise identifier")
    simulation_id: str = Field(..., description="Simulation identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    
    # Core BCM metrics
    rto_achieved: Dict[str, float] = Field(default_factory=dict, description="RTO achievements by process")
    rpo_achieved: Dict[str, float] = Field(default_factory=dict, description="RPO achievements by process")
    recovery_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall recovery success rate")
    
    # Performance metrics
    decision_times: List[float] = Field(default_factory=list, description="Decision times in minutes")
    communication_delays: List[float] = Field(default_factory=list, description="Communication delays in minutes")
    resource_utilization: Dict[str, float] = Field(default_factory=dict, description="Resource utilization rates")
    
    # Cost metrics
    estimated_cost: float = Field(default=0.0, description="Estimated exercise cost")
    recovery_cost: float = Field(default=0.0, description="Estimated recovery cost")
    downtime_cost: float = Field(default=0.0, description="Estimated downtime cost")
    
    # Quality metrics
    participant_satisfaction: Optional[float] = Field(None, ge=1.0, le=5.0, description="Participant satisfaction (1-5)")
    learning_objectives_met: float = Field(default=0.0, ge=0.0, le=1.0, description="Learning objectives achievement rate")
    
    # Compliance metrics
    regulatory_requirements_tested: int = Field(default=0, description="Number of regulatory requirements tested")
    compliance_gaps_identified: int = Field(default=0, description="Number of compliance gaps found")
    
    # Timestamps
    measured_at: datetime = Field(default_factory=datetime.utcnow, description="Measurement timestamp")

class SimulationResult(BaseModel):
    """Complete simulation results"""
    simulation_id: str = Field(..., description="Simulation identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    exercise_id: str = Field(..., description="Exercise identifier")
    scenario_name: str = Field(..., description="Scenario name")
    
    # Execution summary
    status: SimulationStatus = Field(..., description="Final status")
    duration_seconds: int = Field(..., description="Total duration in seconds")
    participants_count: int = Field(default=0, description="Number of participants")
    
    # Results
    metrics: ExerciseMetrics = Field(..., description="Exercise metrics")
    success_criteria_met: Dict[str, bool] = Field(default_factory=dict, description="Success criteria results")
    key_findings: List[str] = Field(default_factory=list, description="Key findings and observations")
    
    # Detailed results
    timeline: List[Dict[str, Any]] = Field(default_factory=list, description="Simulation timeline")
    decisions_made: List[Dict[str, Any]] = Field(default_factory=list, description="Decisions made during exercise")
    issues_encountered: List[Dict[str, Any]] = Field(default_factory=list, description="Issues encountered")
    
    # Recommendations
    improvement_areas: List[str] = Field(default_factory=list, description="Areas for improvement")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")
    follow_up_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Follow-up actions")
    
    # File attachments
    report_files: List[str] = Field(default_factory=list, description="Generated report file paths")
    log_files: List[str] = Field(default_factory=list, description="Simulation log file paths")
    
    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Result generation timestamp")

class ScenarioTemplate(BaseModel):
    """Scenario template for creating custom scenarios"""
    template_id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: ScenarioCategory = Field(..., description="Template category")
    
    # Template structure
    default_parameters: List[SimulationParameter] = Field(default_factory=list, description="Default parameters")
    configurable_fields: List[str] = Field(default_factory=list, description="Configurable fields")
    required_inputs: List[str] = Field(default_factory=list, description="Required inputs")
    
    # Metadata
    difficulty_level: int = Field(default=1, ge=1, le=5, description="Difficulty level")
    estimated_duration: int = Field(default=60, description="Estimated duration in minutes")
    min_participants: int = Field(default=1, description="Minimum participants")
    max_participants: int = Field(default=20, description="Maximum participants")
    
    # Usage statistics
    usage_count: int = Field(default=0, description="Number of times used")
    average_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Average user rating")

class BatchSimulationRequest(BaseModel):
    """Request to run multiple simulations in batch"""
    tenant_id: str = Field(..., description="Tenant identifier")
    batch_name: str = Field(..., description="Batch identifier")
    
    # Simulations to run
    simulations: List[SimulationRequest] = Field(..., description="List of simulations")
    
    # Execution settings
    run_sequential: bool = Field(default=False, description="Run simulations sequentially")
    max_concurrent: int = Field(default=3, ge=1, le=10, description="Maximum concurrent simulations")
    
    # Aggregation settings
    generate_summary_report: bool = Field(default=True, description="Generate summary report")
    compare_results: bool = Field(default=True, description="Compare simulation results")

class SimulationComparison(BaseModel):
    """Comparison between simulation results"""
    comparison_id: str = Field(..., description="Comparison identifier")
    simulation_ids: List[str] = Field(..., description="Compared simulation IDs")
    tenant_id: str = Field(..., description="Tenant identifier")
    
    # Comparison metrics
    rto_comparison: Dict[str, List[float]] = Field(default_factory=dict, description="RTO comparison by process")
    rpo_comparison: Dict[str, List[float]] = Field(default_factory=dict, description="RPO comparison by process")
    cost_comparison: List[float] = Field(default_factory=list, description="Cost comparison")
    
    # Analysis
    best_performing: Dict[str, str] = Field(default_factory=dict, description="Best performing simulation by metric")
    improvement_trends: Dict[str, float] = Field(default_factory=dict, description="Improvement trends")
    recommendations: List[str] = Field(default_factory=list, description="Comparative recommendations")
    
    # Timestamps
    compared_at: datetime = Field(default_factory=datetime.utcnow, description="Comparison timestamp")

class EventData(BaseModel):
    """Event data for EventBus integration"""
    event_type: str = Field(..., description="Event type")
    tenant_id: str = Field(..., description="Tenant identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    source: str = Field(default="simulation-adapter", description="Event source")

class SimulationEngineConfig(BaseModel):
    """Simulation engine configuration"""
    engine_type: SimulationEngine = Field(..., description="Engine type")
    executable_path: Optional[str] = Field(None, description="Engine executable path")
    working_directory: Optional[str] = Field(None, description="Working directory")
    
    # Resource limits
    max_memory_mb: int = Field(default=1024, description="Maximum memory usage in MB")
    max_cpu_cores: int = Field(default=2, description="Maximum CPU cores to use")
    timeout_seconds: int = Field(default=3600, description="Simulation timeout in seconds")
    
    # Engine-specific settings
    jaamsim_settings: Dict[str, Any] = Field(default_factory=dict, description="JaamSim specific settings")
    anylogic_settings: Dict[str, Any] = Field(default_factory=dict, description="AnyLogic specific settings")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom engine settings")

class AdapterStatistics(BaseModel):
    """Simulation adapter statistics"""
    tenant_id: str = Field(..., description="Tenant identifier")
    
    # Usage statistics
    total_simulations: int = Field(default=0, description="Total simulations run")
    successful_simulations: int = Field(default=0, description="Successful simulations")
    failed_simulations: int = Field(default=0, description="Failed simulations")
    
    # Performance statistics
    average_duration: float = Field(default=0.0, description="Average simulation duration in minutes")
    total_cpu_hours: float = Field(default=0.0, description="Total CPU hours consumed")
    total_exercises: int = Field(default=0, description="Total exercises conducted")
    
    # Period statistics
    simulations_this_week: int = Field(default=0, description="Simulations this week")
    simulations_this_month: int = Field(default=0, description="Simulations this month")
    
    # Quality metrics
    average_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Average success rate")
    average_participant_satisfaction: Optional[float] = Field(None, description="Average satisfaction rating")
    
    # Most used
    most_used_scenarios: List[str] = Field(default_factory=list, description="Most used scenarios")
    most_used_engine: SimulationEngine = Field(default=SimulationEngine.MOCK, description="Most used engine")
    
    # Timestamps
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="Statistics calculation time")
