"""
Models package for Simulation Service

Contains Pydantic models for data validation and SQLAlchemy ORM models for persistence.
"""

from .pydantic_models import (
    # Enums
    EngineType,
    SimulationStatus,
    ExerciseType,
    ScenarioCategory,
    MetricType,
    DashboardType,
    ChartType,

    # Core Models
    TaskSpecification,
    Simulation,
    Scenario,
    SimulationResult,
    SimulationEvent,

    # Configuration Models
    VisualizationConfig,
    IntegrationConfig,
    EngineConfig,
    ReportConfig,

    # Request/Response Models
    SimulationRequest,
    SimulationState,
    ExerciseMetrics,
)

from .communication_models import (
    # Communication Enums
    CrisisLevel,
    CommunicationType,
    NotificationType,
    NotificationStatus,
    IncidentType,
    PriorityLevel,

    # Communication Models
    CommunicationTemplate,
    CrisisCommunicationPlan,
    StakeholderNotification,

    # AI Response Models
    AIResponseTemplate,
    AIClassificationRule,
    AIEscalationRule,
    AILearningPattern,

    # Analytics Models
    CommunicationMetrics,
    CommunicationTimeline,

    # Helper Functions
    create_notification,
    calculate_communication_metrics
)

__all__ = [
    # Enums
    "EngineType",
    "SimulationStatus",
    "ExerciseType",
    "ScenarioCategory",
    "MetricType",
    "DashboardType",
    "ChartType",

    # Core Models
    "TaskSpecification",
    "Simulation",
    "Scenario",
    "SimulationResult",
    "SimulationEvent",

    # Configuration Models
    "VisualizationConfig",
    "IntegrationConfig",
    "EngineConfig",
    "ReportConfig",

    # Request/Response Models
    "SimulationRequest",
    "SimulationState",
    "ExerciseMetrics",

    # Communication Enums
    "CrisisLevel",
    "CommunicationType",
    "NotificationType",
    "NotificationStatus",
    "IncidentType",
    "PriorityLevel",

    # Communication Models
    "CommunicationTemplate",
    "CrisisCommunicationPlan",
    "StakeholderNotification",
    "AIResponseTemplate",
    "AIClassificationRule",
    "AIEscalationRule",
    "AILearningPattern",
    "CommunicationMetrics",
    "CommunicationTimeline",
    "create_notification",
    "calculate_communication_metrics"
]
