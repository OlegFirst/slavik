"""
AI Orchestrator - The Brain of BCM Platform
============================================

Autonomous decision-making system with:
- Multi-layered memory (working, short-term, long-term, procedural)
- Safety monitoring and constitution enforcement
- Self-evolution capabilities (data, models, code)
- Context aggregation from all platform sources
- Priority-based strategy selection

Quick Start:
    ```python
    from . import AIOrchestrator

    # Initialize orchestrator
    orchestrator = AIOrchestrator()
    await orchestrator.initialize()

    # Make decision
    situation = {
        'workflow_stuck': True,
        'workflow_id': 'bia_001',
        'stuck_duration_minutes': 30
    }

    decision = await orchestrator.decide(situation)
    result = await orchestrator.execute(decision)
    ```

Architecture:
    - DecisionCenter: Context aggregation, priority, strategy selection
    - DistributedMemory: 4-layer memory system
    - SafetyMonitor: Constitution enforcement, loop detection
    - EvolutionEngine: Self-improvement (data, models, code)

Safety:
    - Constitution rules (immutable)
    - Human escalation on low confidence
    - No production code changes without review
    - Audit trail for all decisions
"""

from .orchestrator import AIOrchestrator
from .models import (
    Decision,
    Strategy,
    Priority,
    FullContext,
    SafetyResult,
    SafetyConcern,
    ActionType,
    PriorityLevel,
    MemoryType
)

__all__ = [
    'AIOrchestrator',
    'Decision',
    'Strategy',
    'Priority',
    'FullContext',
    'SafetyResult',
    'SafetyConcern',
    'ActionType',
    'PriorityLevel',
    'MemoryType'
]

__version__ = '1.0.0'
