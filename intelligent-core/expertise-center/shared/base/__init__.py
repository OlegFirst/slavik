"""
Base Classes for Expertise Center Domain Plugins
"""

from .base_specialist import BaseSpecialist
from .base_tactical_assistant import BaseTacticalAssistant
from .base_analyzer import BaseAnalyzer

# Legacy alias for backwards compatibility
BaseColleague = BaseTacticalAssistant

__all__ = [
    "BaseSpecialist",
    "BaseTacticalAssistant",
    "BaseAnalyzer",
    "BaseColleague",  # Legacy
]
