"""
AI Intelligence Layer for MIO Manager
======================================

Integrates ai-foundation capabilities into AI Office Manager:
- RAG for context-aware decisions
- LLM for conversational interface
- ML for predictive analytics
- Context building for comprehensive understanding
"""

from .ai_coordinator import AICoordinator
from .decision_engine import DecisionEngine
from .learning_tracker import LearningTracker

__all__ = [
    'AICoordinator',
    'DecisionEngine',
    'LearningTracker',
]
