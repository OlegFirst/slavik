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

from .evolution_engine import EvolutionEngine
from .data_evolution import DataEvolution
from .model_evolution import ModelEvolution
from .code_evolution import CodeEvolution

__all__ = [
    'EvolutionEngine',
    'DataEvolution',
    'ModelEvolution',
    'CodeEvolution'
]
