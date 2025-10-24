"""
Federated Subsystem Protocols
==============================

Protocol interfaces for distributed AI subsystems across the platform.

Philosophy:
-----------
ai_foundation defines PROTOCOLS and COORDINATES, not monopolizes.
Each module (workflow_intelligence, expertise_center, orchestration, etc.)
implements these protocols with their own domain-specific logic.

Like a nervous system:
- Nerves (subsystems) are EVERYWHERE
- Brain (coordinator) COORDINATES but doesn't control every nerve

Subsystems:
-----------
- IMLSubsystem: Machine Learning protocol
- IRAGSubsystem: Retrieval-Augmented Generation protocol
- ILearningSubsystem: Self-learning and pattern recognition protocol
"""

from .iml_subsystem import IMLSubsystem
from .irag_subsystem import IRAGSubsystem
from .ilearning_subsystem import ILearningSubsystem

__all__ = [
    "IMLSubsystem",
    "IRAGSubsystem",
    "ILearningSubsystem",
]
