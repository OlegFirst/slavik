"""
Scenario Intelligence - верхний слой координации intelligent-core

Оркестрирует всю систему через сценарии
"""

# Lazy imports to avoid circular dependencies and allow testing
def __getattr__(name):
    if name == "ScenarioEngine":
        from engines.scenario_engine import ScenarioEngine
        return ScenarioEngine
    elif name == "global_registry":
        from storage.registry import global_registry
        return global_registry
    elif name == "global_learner":
        from learning.scenario_learner import global_learner
        return global_learner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ScenarioEngine",
    "global_registry",
    "global_learner"
]
