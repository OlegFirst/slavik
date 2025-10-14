"""
System BCM Integrations
Интеграция с существующими компонентами платформы
"""

from .learning_integration import LearningIntegration
from .expertise_integration import ExpertiseIntegration
from .collective_integration import CollectiveIntegration
from .ai_integration import AIIntegration

__all__ = [
    "LearningIntegration",
    "ExpertiseIntegration",
    "CollectiveIntegration",
    "AIIntegration"
]
