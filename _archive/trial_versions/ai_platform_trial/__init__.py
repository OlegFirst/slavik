"""
AI Platform - Unified AI System

Business-first architecture for all AI operations.

Management Hierarchy:
- Level 0: Chief Executive AI (CEO) - Routes requests
- Level 1: 3 TOP Managers - Coordinate segments
  - Governance Manager
  - Platform Manager
  - Domain/BCM Manager
- Level 2: 18 Experts - Domain specialists
- Level 3: Tools - Structured operations
- Level 4: Organs - Heavy computations

Three Segments:
1. GOVERNANCE - Compliance, audit, governance
2. PLATFORM - Workflow, architecture, technical
3. DOMAIN - Business continuity management (BCM)
"""

from .chief import ChiefExecutiveAI
from .managers import GovernanceManager, PlatformManager, DomainManager
from .shared.base import BaseExpert, BaseTool, BaseOrgan, BaseManager

__version__ = "1.0.0"

__all__ = [
    # Top-level
    'ChiefExecutiveAI',

    # Managers
    'GovernanceManager',
    'PlatformManager',
    'DomainManager',

    # Base classes
    'BaseExpert',
    'BaseTool',
    'BaseOrgan',
    'BaseManager',
]


def create_platform(llm_client=None):
    """
    Create fully initialized AI Platform

    Args:
        llm_client: AI client for all components

    Returns:
        ChiefExecutiveAI instance with all managers
    """
    # Create managers
    governance_manager = GovernanceManager(llm_client=llm_client)
    platform_manager = PlatformManager(llm_client=llm_client)
    domain_manager = DomainManager(llm_client=llm_client)

    # Create Chief Executive AI
    chief = ChiefExecutiveAI(
        governance_manager=governance_manager,
        platform_manager=platform_manager,
        domain_manager=domain_manager,
        llm_client=llm_client
    )

    return chief
