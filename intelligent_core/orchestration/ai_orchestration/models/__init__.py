"""
Data models for orchestrator

All Pydantic models and data classes used across orchestrators
"""

# Import core orchestrator models from parent models.py file
# (This models/ directory coexists with models.py file one level up)
import sys
from pathlib import Path

# Temporarily add parent directory to import the sibling models.py
_parent = Path(__file__).parent.parent
_models_file = _parent / 'models.py'
if _models_file.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("orchestrator_core_models", _models_file)
    if spec and spec.loader:
        _core_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_core_models)

        # Import classes from the loaded module
        PriorityLevel = _core_models.PriorityLevel
        ActionType = _core_models.ActionType
        MemoryType = _core_models.MemoryType
        Priority = _core_models.Priority
        Strategy = _core_models.Strategy
        Decision = _core_models.Decision
        FullContext = _core_models.FullContext
        SafetyConcern = _core_models.SafetyConcern
        SafetyResult = _core_models.SafetyResult
        Memory = _core_models.Memory
        Loop = _core_models.Loop
        HallucinationScore = _core_models.HallucinationScore

from .platform_models import (
    EventPublishRequest,
    WorkflowStartRequest,
    BIAStartRequest,
    IncidentReportRequest,
    AuditStartRequest
)

from .ai_models import (
    RiskLevel,
    IncidentCategory,
    ActionType,
    BusinessProcess,
    Incident,
    NaturalLanguageQuery,
    AIDecision,
    Decision,
    OrchestratorRule,
    RecommendationRequest,
    RecommendationResponse,
    AuditSummaryRequest,
    AuditSummaryResponse,
    DecisionApprovalRequest
)

from .scenario_models import (
    ScenarioGenerationRequest,
    ExerciseResult,
    ScenarioLearning,
    Scenario
)

from .deployment_models import (
    DeploymentPlan,
    DeploymentResult
)

__all__ = [
    # Core orchestrator models (from parent models.py)
    'PriorityLevel',
    'ActionType',
    'MemoryType',
    'Priority',
    'Strategy',
    'Decision',
    'FullContext',
    'SafetyConcern',
    'SafetyResult',
    'Memory',
    'Loop',
    'HallucinationScore',

    # Platform models
    'EventPublishRequest',
    'WorkflowStartRequest',
    'BIAStartRequest',
    'IncidentReportRequest',
    'AuditStartRequest',

    # AI models
    'RiskLevel',
    'IncidentCategory',
    'ActionType',
    'BusinessProcess',
    'Incident',
    'NaturalLanguageQuery',
    'AIDecision',
    'Decision',
    'OrchestratorRule',
    'RecommendationRequest',
    'RecommendationResponse',
    'AuditSummaryRequest',
    'AuditSummaryResponse',
    'DecisionApprovalRequest',

    # Scenario models
    'ScenarioGenerationRequest',
    'ExerciseResult',
    'ScenarioLearning',
    'Scenario',

    # Deployment models
    'DeploymentPlan',
    'DeploymentResult',
]