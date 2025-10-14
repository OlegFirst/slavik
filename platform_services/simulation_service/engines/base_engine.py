"""
Base Simulation Engine
======================

Abstract class for all simulation engines.

Provides common interface and utilities for:
- JaamSim Engine
- Monte Carlo Engine
- Scenario Engine
- What-If Engine
- BIA CIW Engine
- Any future engines
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseSimulationEngine(ABC):
    """
    Abstract base class for all simulation engines

    All engines must implement:
    - run() - Execute simulation
    - validate_parameters() - Validate input parameters

    Provides:
    - log_progress() - Standardized progress logging
    - Common initialization
    """

    def __init__(self, simulation_id: str, parameters: Dict[str, Any]):
        """
        Initialize simulation engine

        Args:
            simulation_id: Unique simulation identifier
            parameters: Engine-specific parameters
        """
        self.simulation_id = simulation_id
        self.parameters = parameters
        self.logger = logger
        self._progress = 0.0

    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """
        Run simulation

        Returns:
            Simulation results as dict with standard structure:
            {
                "status": "success" | "failed",
                "results": {...},
                "metrics": {...},
                "duration_seconds": float,
                "error": str (if failed)
            }
        """
        pass

    @abstractmethod
    def validate_parameters(self) -> bool:
        """
        Validate simulation parameters

        Returns:
            True if valid

        Raises:
            ValueError: If parameters are invalid
        """
        pass

    def log_progress(self, message: str, progress: Optional[float] = None):
        """
        Log simulation progress

        Args:
            message: Progress message
            progress: Progress percentage (0-100), optional
        """
        if progress is not None:
            self._progress = progress
            log_msg = f"[Simulation {self.simulation_id}] {message} ({progress:.1f}%)"
        else:
            log_msg = f"[Simulation {self.simulation_id}] {message}"

        self.logger.info(log_msg)

    @property
    def progress(self) -> float:
        """Get current progress (0-100)"""
        return self._progress

    def set_progress(self, progress: float):
        """Update progress"""
        self._progress = max(0.0, min(100.0, progress))
