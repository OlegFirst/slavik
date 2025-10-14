"""
AI Organs - Specialized Intelligence Units

10 AI Organs for BCM Intelligence (migrated from ai_office)
"""

from .base_organ import BaseAIOrgan
from .governance_brain import GovernanceBrain
from .emergency_response import EmergencyResponse
from .impact_oracle import ImpactOracle
from .scenario_creator import ScenarioCreator
from .risk_advisor import RiskAdvisor
from .compliance_guardian import ComplianceGuardian
from .performance_analyst import PerformanceAnalyst
from .learning_coach import LearningCoach
from .plan_generator import PlanGenerator
from .lifecycle_monitor import LifecycleMonitor

__all__ = [
    "BaseAIOrgan",
    "GovernanceBrain",
    "EmergencyResponse",
    "ImpactOracle",
    "ScenarioCreator",
    "RiskAdvisor",
    "ComplianceGuardian",
    "PerformanceAnalyst",
    "LearningCoach",
    "PlanGenerator",
    "LifecycleMonitor"
]

# Organ registry for dynamic access
ORGAN_REGISTRY = {
    "governance_brain": GovernanceBrain,
    "emergency_response": EmergencyResponse,
    "impact_oracle": ImpactOracle,
    "scenario_creator": ScenarioCreator,
    "risk_advisor": RiskAdvisor,
    "compliance_guardian": ComplianceGuardian,
    "performance_analyst": PerformanceAnalyst,
    "learning_coach": LearningCoach,
    "plan_generator": PlanGenerator,
    "lifecycle_monitor": LifecycleMonitor
}
