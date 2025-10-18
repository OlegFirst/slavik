"""
Validation Service Models

Exports both domain models (Pydantic) and database models (SQLAlchemy).
"""

# Domain models (Pydantic)
from .domain import (
    # Enums
    ExerciseType, ExerciseStatus, ObservationType, ObservationSeverity,
    PerformanceDirection, MeasurementFrequency, PerformanceStatus, TrendDirection,
    DataQuality, CollectionMethod,
    AuditType, AuditStatus, FindingType, FindingSeverity,
    CAPAType, CAPAStatus, CAPASource,
    # Models
    Exercise, ExerciseScenario, ExerciseObservation,
    KPI, KPIMeasurement,
    AuditPlan, AuditFinding,
    CAPA,
    ManagementReview,
)

# Database models (SQLAlchemy)
from .database import (
    Base,
    Exercise as ExerciseDB,
    ExerciseScenario as ExerciseScenarioDB,
    ExerciseObservation as ExerciseObservationDB,
    ExerciseAction as ExerciseActionDB,
    KPI as KPIDB,
    KPICategory as KPICategoryDB,
    KPIMeasurement as KPIMeasurementDB,
    KPIDashboard as KPIDashboardDB,
    AuditPlan as AuditPlanDB,
    AuditFinding as AuditFindingDB,
    CAPA as CAPADB,
    ManagementReview as ManagementReviewDB,
    KPIAlert as KPIAlertDB,
)

__all__ = [
    # Enums
    "ExerciseType", "ExerciseStatus", "ObservationType", "ObservationSeverity",
    "PerformanceDirection", "MeasurementFrequency", "PerformanceStatus", "TrendDirection",
    "DataQuality", "CollectionMethod",
    "AuditType", "AuditStatus", "FindingType", "FindingSeverity",
    "CAPAType", "CAPAStatus", "CAPASource",
    # Domain models
    "Exercise", "ExerciseScenario", "ExerciseObservation",
    "KPI", "KPIMeasurement",
    "AuditPlan", "AuditFinding",
    "CAPA",
    "ManagementReview",
    # Database models
    "Base",
    "ExerciseDB", "ExerciseScenarioDB", "ExerciseObservationDB", "ExerciseActionDB",
    "KPIDB", "KPICategoryDB", "KPIMeasurementDB", "KPIDashboardDB",
    "AuditPlanDB", "AuditFindingDB",
    "CAPADB",
    "ManagementReviewDB",
    "KPIAlertDB",
]
