"""
Evolution Engine
================

Self-improvement system with 3 levels:

Level 1: Data Evolution (Daily)
- Learn from new cases
- Update case library
- Automatic, no human review

Level 2: Model Evolution (Weekly)
- Retrain ML models
- Update strategies
- Performance-based updates
- Automatic, but monitored

Level 3: Code Evolution (Monthly)
- Suggest code improvements
- Generate new features
- REQUIRES HUMAN REVIEW before deployment
"""

from intelligent_core.ai_orchestration.evolution.evolution_engine import EvolutionEngine
from intelligent_core.ai_orchestration.evolution.data_evolution import DataEvolution
from intelligent_core.ai_orchestration.evolution.model_evolution import ModelEvolution
from intelligent_core.ai_orchestration.evolution.code_evolution import CodeEvolution

__all__ = [
    'EvolutionEngine',
    'DataEvolution',
    'ModelEvolution',
    'CodeEvolution'
]
