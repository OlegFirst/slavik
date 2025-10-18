"""
Adapter Router
Routes experiments to appropriate external adapters

Automatically routes simulation requests based on experiment type
"""

import logging
from typing import Dict, Any, Optional
from core.adapters.external_adapter_client import ExternalAdapterClient

logger = logging.getLogger(__name__)


class AdapterRouter:
    """
    Routes experiments to appropriate external adapters

    Experiment routing:
    - simpy_queue → SimPy Adapter (Port 7001)
    - mesa_abm → Mesa Adapter (Port 7002)
    - ml_* → ML/AI Adapter (Port 7004)
    - donor_prediction, impact_forecast, budget_optimization, risk_assessment → ML Adapter
    """

    # Experiment → Adapter mapping
    ROUTING_MAP = {
        # SimPy experiments
        "simpy_queue": "simpy",
        "discrete_event": "simpy",
        "queue_management": "simpy",
        "capacity_planning": "simpy",

        # Mesa experiments
        "mesa_abm": "mesa",
        "agent_based": "mesa",
        "stakeholder_simulation": "mesa",
        "policy_simulation": "mesa",

        # ML/AI experiments
        "ml_prediction": "ml",
        "donor_prediction": "ml",
        "impact_forecast": "ml",
        "budget_optimization": "ml",
        "risk_assessment": "ml",
        "predictive_analytics": "ml",
    }

    def __init__(self, client: Optional[ExternalAdapterClient] = None):
        """
        Initialize router

        Args:
            client: External adapter client (creates new if None)
        """
        self.client = client or ExternalAdapterClient()
        self._own_client = client is None  # Track if we created the client

    def get_adapter_for_experiment(self, experiment: str) -> str:
        """
        Get adapter name for experiment type

        Args:
            experiment: Experiment type

        Returns:
            Adapter name (simpy, mesa, ml)

        Raises:
            ValueError: If experiment type unknown
        """
        adapter = self.ROUTING_MAP.get(experiment)
        if not adapter:
            raise ValueError(f"Unknown experiment type: {experiment}. "
                             f"Known types: {list(self.ROUTING_MAP.keys())}")
        return adapter

    async def route_experiment(
        self,
        experiment: str,
        params: Dict[str, Any],
        monte_carlo_runs: int = 100
    ) -> Dict[str, Any]:
        """
        Route experiment to appropriate adapter

        Args:
            experiment: Experiment type
            params: Experiment parameters
            monte_carlo_runs: Number of Monte Carlo iterations

        Returns:
            Simulation/prediction results

        Raises:
            ValueError: If experiment type unknown
            Exception: If adapter call fails
        """
        adapter_name = self.get_adapter_for_experiment(experiment)

        logger.info(f"Routing experiment '{experiment}' to {adapter_name} adapter")

        # Route to appropriate adapter
        if adapter_name == "simpy":
            return await self._route_to_simpy(params, monte_carlo_runs)

        elif adapter_name == "mesa":
            return await self._route_to_mesa(params, monte_carlo_runs)

        elif adapter_name == "ml":
            return await self._route_to_ml(experiment, params, monte_carlo_runs)

        else:
            raise ValueError(f"Unknown adapter: {adapter_name}")

    async def _route_to_simpy(
        self,
        params: Dict[str, Any],
        monte_carlo_runs: int
    ) -> Dict[str, Any]:
        """Route to SimPy adapter"""
        # Extract parameters with defaults
        arrival_rate = params.get("arrival_rate", 12)
        service_time = params.get("service_time", {})
        capacity_agents = params.get("capacity_agents", [6, 8, 10, 12])
        targets = params.get("targets", {})

        return await self.client.run_simpy_simulation(
            arrival_rate=arrival_rate,
            service_time_dist=service_time.get("dist", "lognormal"),
            service_time_mu=service_time.get("mu", "10m"),
            service_time_sigma=service_time.get("sigma", 0.5),
            capacity_agents=capacity_agents,
            sla_target=targets.get("sla_target", 0.95),
            wait_p50_min=targets.get("wait_p50_min", "15m"),
            monte_carlo_runs=monte_carlo_runs
        )

    async def _route_to_mesa(
        self,
        params: Dict[str, Any],
        monte_carlo_runs: int
    ) -> Dict[str, Any]:
        """Route to Mesa adapter"""
        steps = params.get("steps", 200)
        population_size = params.get("population_size", 2000)
        policies = params.get("policies", {})

        return await self.client.run_mesa_simulation(
            steps=steps,
            population_size=population_size,
            policies=policies,
            monte_carlo_runs=monte_carlo_runs
        )

    async def _route_to_ml(
        self,
        experiment: str,
        params: Dict[str, Any],
        monte_carlo_runs: int
    ) -> Dict[str, Any]:
        """Route to ML/AI adapter"""
        # Determine model type from experiment
        model_type_map = {
            "ml_prediction": params.get("model_type", "donor_prediction"),
            "donor_prediction": "donor_prediction",
            "impact_forecast": "impact_forecast",
            "budget_optimization": "budget_optimization",
            "risk_assessment": "risk_assessment",
            "predictive_analytics": params.get("model_type", "impact_forecast")
        }

        model_type = model_type_map.get(experiment, "donor_prediction")

        return await self.client.run_ml_prediction(
            model_type=model_type,
            prediction_horizon=params.get("prediction_horizon", 12),
            confidence_level=params.get("confidence_level", 0.95),
            historical_data=params.get("historical_data"),
            optimization_target=params.get("optimization_target"),
            monte_carlo_runs=monte_carlo_runs
        )

    async def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all adapters

        Returns:
            Dict mapping adapter name to health status
        """
        results = {}

        for adapter_name in ["simpy", "mesa", "ml"]:
            try:
                is_healthy = await self.client.health_check(adapter_name)
                results[adapter_name] = is_healthy
            except Exception as e:
                logger.error(f"Health check failed for {adapter_name}: {e}")
                results[adapter_name] = False

        return results

    async def close(self):
        """Close router and client if owned"""
        if self._own_client:
            await self.client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
