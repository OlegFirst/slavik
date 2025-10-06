"""
Base classes for AI Platform

Unified architecture for all AI components
"""

from .base_expert import BaseExpert
from .base_tool import BaseTool
from .base_organ import BaseOrgan
from .base_manager import BaseManager

__all__ = [
    'BaseExpert',
    'BaseTool',
    'BaseOrgan',
    'BaseManager'
]
