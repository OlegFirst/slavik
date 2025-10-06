"""
TOP Managers

Three segment managers that coordinate experts
"""

from .governance_manager import GovernanceManager
from .platform_manager import PlatformManager
from .domain_manager import DomainManager

__all__ = [
    'GovernanceManager',
    'PlatformManager',
    'DomainManager'
]
