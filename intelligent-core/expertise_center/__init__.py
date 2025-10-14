"""
Expertise Center - Domain Plugin Manager

Manages domain-specific AI experts:
- Specialists (strategic)
- Colleagues (tactical)
- Analyzers (heavy AI)
"""

from .core import ChiefExecutive, ExpertRegistry, DomainLoader
from .shared.base import BaseSpecialist, BaseColleague, BaseAnalyzer

__version__ = "1.0.0"

__all__ = [
    "ChiefExecutive",
    "ExpertRegistry",
    "DomainLoader",
    "BaseSpecialist",
    "BaseColleague",
    "BaseAnalyzer",
]
