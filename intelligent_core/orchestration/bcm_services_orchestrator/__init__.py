"""
BCM Services Orchestrator
========================

Coordinates:
- 10 BCM Analyzers (stateless AI-powered analysis)
- Workflow Intelligence (THE BRAIN)
- 10 BCM Microservices
- Temporal workflows for durable execution

Architecture:
- Analyzer Coordinator → routes requests to analyzers
- Workflow Intelligence Integration → delegates to workflow engine
- Service Registry → maps ISO clauses to services
- Temporal Client → starts durable workflows
"""

from .bcm_orchestrator import BCMServicesOrchestrator
from .analyzer_coordinator import AnalyzerCoordinator, AnalyzerType
from .service_registry import BCMServiceRegistry

__all__ = [
    'BCMServicesOrchestrator',
    'AnalyzerCoordinator',
    'AnalyzerType',
    'BCMServiceRegistry'
]
