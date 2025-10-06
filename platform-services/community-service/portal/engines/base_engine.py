"""
Base Simulation Engine

Abstract class for all simulation engines
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseSimulationEngine(ABC):
    """Base class for all simulation engines"""

    def __init__(self, simulation_id: int, parameters: Dict[str, Any]):
        self.simulation_id = simulation_id
        self.parameters = parameters
        self.logger = logger

    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """
        Run simulation

        Returns:
            Simulation results as dict
        """
        pass

    @abstractmethod
    def validate_parameters(self) -> bool:
        """
        Validate simulation parameters

        Returns:
            True if valid, raises exception otherwise
        """
        pass

    def log_progress(self, message: str, progress: float = None):
        """Log simulation progress"""
        log_msg = f"[Simulation {self.simulation_id}] {message}"
        if progress is not None:
            log_msg += f" ({progress:.1f}%)"
        self.logger.info(log_msg)
