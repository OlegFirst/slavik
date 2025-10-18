"""
External Adapter Client
HTTP client for communicating with external simulation adapters

Connects Digital Twin Core to:
- SimPy Adapter (Port 7001)
- Mesa Adapter (Port 7002)
- ML/AI Adapter (Port 7004)
"""

import httpx
import logging
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AdapterConfig:
    """Configuration for an external adapter"""
    name: str
    host: str
    port: int
    timeout: float = 30.0

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class ExternalAdapterClient:
    """Client for external simulation adapters"""

    # Default adapter configurations
    DEFAULT_ADAPTERS = {
        "simpy": AdapterConfig("simpy", "localhost", 7001),
        "mesa": AdapterConfig("mesa", "localhost", 7002),
        "ml": AdapterConfig("ml", "localhost", 7004),
    }

    def __init__(self, adapters: Optional[Dict[str, AdapterConfig]] = None):
        """
        Initialize adapter client

        Args:
            adapters: Custom adapter configurations (uses defaults if None)
        """
        self.adapters = adapters or self.DEFAULT_ADAPTERS
        self.client = httpx.AsyncClient(timeout=60.0)

    async def health_check(self, adapter_name: str) -> bool:
        """
        Check if adapter is healthy

        Args:
            adapter_name: Name of adapter (simpy, mesa, ml)

        Returns:
            True if healthy, False otherwise
        """
        adapter = self.adapters.get(adapter_name)
        if not adapter:
            logger.error(f"Unknown adapter: {adapter_name}")
            return False

        try:
            response = await self.client.get(
                f"{adapter.base_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {adapter_name}: {e}")
            return False

    async def run_simpy_simulation(
        self,
        arrival_rate: float,
        service_time_dist: str = "lognormal",
        service_time_mu: str = "10m",
        service_time_sigma: float = 0.5,
        capacity_agents: list[int] = None,
        sla_target: float = 0.95,
        wait_p50_min: str = "15m",
        monte_carlo_runs: int = 200
    ) -> Dict[str, Any]:
        """
        Run SimPy discrete event simulation

        Args:
            arrival_rate: Arrivals per hour
            service_time_dist: Distribution type (lognormal, normal, exponential)
            service_time_mu: Mean service time (e.g., "10m", "1h")
            service_time_sigma: Standard deviation
            capacity_agents: List of agent capacities to test
            sla_target: SLA target (0-1)
            wait_p50_min: Median wait time target
            monte_carlo_runs: Number of MC iterations

        Returns:
            Simulation results with best configuration and frontier
        """
        if capacity_agents is None:
            capacity_agents = [6, 8, 10, 12]

        adapter = self.adapters["simpy"]

        payload = {
            "experiment": "simpy_queue",
            "params": {
                "arrival_rate": arrival_rate,
                "service_time": {
                    "dist": service_time_dist,
                    "mu": service_time_mu,
                    "sigma": service_time_sigma
                },
                "capacity_agents": capacity_agents,
                "targets": {
                    "sla_target": sla_target,
                    "wait_p50_min": wait_p50_min
                }
            },
            "monte_carlo_runs": monte_carlo_runs
        }

        logger.info(f"Running SimPy simulation: arrival_rate={arrival_rate}, capacities={capacity_agents}")

        try:
            response = await self.client.post(
                f"{adapter.base_url}/run",
                json=payload,
                timeout=adapter.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"SimPy simulation failed: {e}")
            raise

    async def run_mesa_simulation(
        self,
        steps: int = 200,
        population_size: int = 2000,
        policies: Optional[Dict[str, float]] = None,
        monte_carlo_runs: int = 100
    ) -> Dict[str, Any]:
        """
        Run Mesa agent-based model simulation

        Args:
            steps: Number of simulation steps
            population_size: Agent population size
            policies: Policy interventions (e.g., {"sms": 1.5, "vouchers": 1.1})
            monte_carlo_runs: Number of MC iterations

        Returns:
            ABM simulation results
        """
        if policies is None:
            policies = {}

        adapter = self.adapters["mesa"]

        payload = {
            "experiment": "mesa_abm",
            "params": {
                "steps": steps,
                "population_size": population_size,
                "policies": policies
            },
            "monte_carlo_runs": monte_carlo_runs
        }

        logger.info(f"Running Mesa ABM: steps={steps}, population={population_size}, policies={policies}")

        try:
            response = await self.client.post(
                f"{adapter.base_url}/run",
                json=payload,
                timeout=adapter.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Mesa simulation failed: {e}")
            raise

    async def run_ml_prediction(
        self,
        model_type: Literal["donor_prediction", "impact_forecast", "budget_optimization", "risk_assessment"],
        prediction_horizon: int = 12,
        confidence_level: float = 0.95,
        historical_data: Optional[list[Dict[str, Any]]] = None,
        optimization_target: Optional[str] = None,
        monte_carlo_runs: int = 100
    ) -> Dict[str, Any]:
        """
        Run ML/AI prediction or optimization model

        Args:
            model_type: Type of ML model to run
            prediction_horizon: Months to predict ahead
            confidence_level: Confidence level (0-1)
            historical_data: Historical training data
            optimization_target: Optimization target metric
            monte_carlo_runs: Number of MC iterations

        Returns:
            ML model results with predictions and metrics
        """
        adapter = self.adapters["ml"]

        payload = {
            "experiment": "ml_prediction",
            "params": {
                "model_type": model_type,
                "prediction_horizon": prediction_horizon,
                "confidence_level": confidence_level,
                "historical_data": historical_data,
                "optimization_target": optimization_target
            },
            "monte_carlo_runs": monte_carlo_runs
        }

        logger.info(f"Running ML model: type={model_type}, horizon={prediction_horizon}mo")

        try:
            response = await self.client.post(
                f"{adapter.base_url}/run",
                json=payload,
                timeout=adapter.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            raise

    async def list_ml_models(self) -> Dict[str, Any]:
        """
        Get list of available ML models

        Returns:
            List of ML models with metadata
        """
        adapter = self.adapters["ml"]

        try:
            response = await self.client.get(
                f"{adapter.base_url}/models",
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list ML models: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
