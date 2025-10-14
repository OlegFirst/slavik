"""
Scenario Generators - Infrastructure Tool

Generates test scenarios from templates for the BCM platform.

This is an infrastructure tool that:
- Uses templates and knowledge from intelligent-core/scenario-intelligence
- Generates executable test scenarios
- Coordinates with MIO Manager for orchestration
- Provides CLI and API interfaces

Architecture:
- intelligent-core/scenario-intelligence: Templates, knowledge, policies
- infrastructure/tools/scenario-generators: Generation tools
- infrastructure/AI-office-infrastructure/scenario-orchestrator: REST API
"""

from .generators import (
    BaseGenerator,
    L1PlatformGenerator,
    L1ApplicationGenerator,
    L2SubsystemGenerator,
    L3SystemGenerator
)

from .managers import GenerationManager

__all__ = [
    "BaseGenerator",
    "L1PlatformGenerator",
    "L1ApplicationGenerator",
    "L2SubsystemGenerator",
    "L3SystemGenerator",
    "GenerationManager"
]

__version__ = "1.0.0"
