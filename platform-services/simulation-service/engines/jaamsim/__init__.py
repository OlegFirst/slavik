"""
JaamSim Integration Package

Provides BCM-specific JaamSim simulation capabilities:
- jaamsim_client.py: Full-featured BCM exercise simulation client
- Use for: BCM exercises, scenario templates, entity generation, monitoring
"""

from .jaamsim_client import (
    JaamSimClient,
    BCMExerciseSimulator,
    ExerciseScenario,
    SimulationEntity,
    SimulationEvent,
    ExerciseResult
)

__all__ = [
    "JaamSimClient",
    "BCMExerciseSimulator",
    "ExerciseScenario",
    "SimulationEntity",
    "SimulationEvent",
    "ExerciseResult"
]
