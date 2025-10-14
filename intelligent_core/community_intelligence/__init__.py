"""
Community Intelligence Foundation Module

Provides:
- Case Contributions & Peer Review
- Multi-dimensional Reputation System
- Living Documentation (community + AI synthesis)
- Predictive Timeline Generation
- Specialized Assistants
"""

__version__ = "1.0.0"

from .services.contribution_service import ContributionService
from .services.living_docs import LivingDocumentationService
from .services.predictive_timeline import PredictiveTimelineService
from .services.anonymizer import SmartAnonymizer

__all__ = [
    "ContributionService",
    "LivingDocumentationService",
    "PredictiveTimelineService",
    "SmartAnonymizer"
]
