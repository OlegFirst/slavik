"""
ACE Engine - Agentic Context Engineering

Implements the ACE framework for evolving context playbooks:
- Generator: Creates context with accumulated strategies
- Reflector: Analyzes trajectories and identifies insights
- Curator: Updates playbooks incrementally without context collapse

Source: arXiv:2510.04618
"""

from .ace_engine import (
    ACEEngine,
    ACEGenerator,
    ACEReflector,
    ACECurator,
    get_ace_engine
)

__all__ = [
    "ACEEngine",
    "ACEGenerator",
    "ACEReflector",
    "ACECurator",
    "get_ace_engine"
]
