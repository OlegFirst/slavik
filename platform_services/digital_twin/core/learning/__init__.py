"""
Passive Learning System

Automatically learns about organizations from their interactions with the platform.

Key Features:
- Transparent learning (user doesn't need to do anything special)
- Context accumulation from BIA, Risk, Incident, Training, etc.
- Pattern recognition
- Behavioral insights
- Auto-enrichment of digital twin
"""

from .passive_learning_engine import PassiveLearningEngine, LearningEvent
from .context_builder import ContextBuilder, OrganizationContext

__all__ = [
    "PassiveLearningEngine",
    "LearningEvent",
    "ContextBuilder",
    "OrganizationContext",
]
