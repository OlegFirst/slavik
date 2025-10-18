"""
Community Level Module

Enables organization twins to interact, share knowledge, and connect people.

Key Features:
- Twin Matching: Find similar organizations based on multi-dimensional similarity
- Knowledge Exchange: Share anonymized best practices and learnings
- People Matching: Connect BCM professionals for mentorship and collaboration
- Privacy Protection: Anonymization engine for data privacy
"""

from .twin_matching_engine import TwinMatchingEngine, SimilarityScore, MatchFilters
from .knowledge_exchange import KnowledgeExchangeService, Learning, LearningContribution
from .people_matching import PeopleMatchingService, PeerMatch, PeerCriteria
from .anonymization_engine import AnonymizationEngine

__all__ = [
    "TwinMatchingEngine",
    "SimilarityScore",
    "MatchFilters",
    "KnowledgeExchangeService",
    "Learning",
    "LearningContribution",
    "PeopleMatchingService",
    "PeerMatch",
    "PeerCriteria",
    "AnonymizationEngine",
]
