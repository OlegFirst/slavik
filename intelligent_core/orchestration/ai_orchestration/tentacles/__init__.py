"""
Tentacles - External Integrations

Orchestrator's connections to external services
"""

from .knowledge_orchestrator import KnowledgeOrchestrator
from .ai_office_connector import AIOfficeConnector, get_ai_office_connector, AIColleague

__all__ = [
    'KnowledgeOrchestrator',
    'AIOfficeConnector',
    'get_ai_office_connector',
    'AIColleague'
]
