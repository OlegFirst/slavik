"""
Scenario Intelligence Integration Adapters

Provides integration with all intelligent-core modules:
- predictive_adapter: Predictive Intelligence integration
- community_adapter: Community Intelligence integration
- workflow_adapter: Workflow Engine (Temporal) integration
- orchestration_adapter: AI Orchestration integration
- event_intelligence_adapter: Event Intelligence integration
- bcm_adapter: System BCM Service integration
- workflow_intel_adapter: Workflow Intelligence integration
"""

from .predictive_adapter import (
    ScenarioPredictiveAdapter,
    get_predictive_adapter
)
from .community_adapter import (
    ScenarioCommunityAdapter,
    get_community_adapter
)
from .workflow_adapter import (
    ScenarioWorkflowAdapter,
    get_workflow_adapter
)
from .orchestration_adapter import (
    ScenarioOrchestrationAdapter,
    get_orchestration_adapter
)
from .event_intelligence_adapter import (
    ScenarioEventIntelligenceAdapter,
    get_event_intelligence_adapter
)
from .bcm_adapter import (
    ScenarioBCMAdapter,
    get_bcm_adapter
)
from .workflow_intel_adapter import (
    ScenarioWorkflowIntelAdapter,
    get_workflow_intel_adapter
)
from .simulation_adapter import (
    ScenarioSimulationAdapter,
    get_simulation_adapter
)

__all__ = [
    # Adapters
    "ScenarioPredictiveAdapter",
    "ScenarioCommunityAdapter",
    "ScenarioWorkflowAdapter",
    "ScenarioOrchestrationAdapter",
    "ScenarioEventIntelligenceAdapter",
    "ScenarioBCMAdapter",
    "ScenarioWorkflowIntelAdapter",
    "ScenarioSimulationAdapter",
    # Global getters
    "get_predictive_adapter",
    "get_community_adapter",
    "get_workflow_adapter",
    "get_orchestration_adapter",
    "get_event_intelligence_adapter",
    "get_bcm_adapter",
    "get_workflow_intel_adapter",
    "get_simulation_adapter",
]
