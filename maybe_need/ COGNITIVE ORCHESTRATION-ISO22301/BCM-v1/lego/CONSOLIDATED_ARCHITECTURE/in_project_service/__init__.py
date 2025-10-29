"""
In-Project Orchestration Service
Embeddable service for direct integration into user projects
"""

from .orchestrator import (
    InProjectOrchestrator,
    analyze_project,
    generate_architecture
)

__version__ = "1.0.0"
__all__ = ["InProjectOrchestrator", "analyze_project", "generate_architecture"]