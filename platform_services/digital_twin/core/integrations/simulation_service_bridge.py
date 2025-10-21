"""
Simulation Service Bridge
Integration bridge to simulation_service (Port 8095)

Provides:
- Access to 7 simulation engines
- EventBus integration
- Real-time simulation monitoring
- Result aggregation
"""

import logging
import httpx
from typing import Dict, Any, Optional, List, Literal
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SimulationEngineInfo:
    """Information about a simulation engine"""
    name: str
    engine_type: str
    description: str
    available: bool = True


class SimulationServiceBridge:
    """
    Simulation Service Bridge

    Integration layer between Digital Twin and simulation_service.
    Provides unified access to all simulation engines and features.

    Features:
    - 7 simulation engines (JaamSim, MonteCarlo, Scenario, WhatIf, BCMQueue, AdvancedBIA, JaamSimClient)
    - Real-time execution monitoring
    - Result aggregation
    - EventBus subscriptions
    """

    # Known simulation engines
    ENGINES = {
        "jaamsim": SimulationEngineInfo(
            "JaamSim Engine",
            "discrete_event",
            "Discrete event simulation using JaamSim"
        ),
        "monte_carlo": SimulationEngineInfo(
            "Monte Carlo Engine",
            "probabilistic",
            "Monte Carlo probabilistic analysis"
        ),
        "scenario": SimulationEngineInfo(
            "Scenario Engine",
            "bcm",
            "BCM scenario execution"
        ),
        "what_if": SimulationEngineInfo(
            "What-If Engine",
            "decision",
            "What-if decision analysis"
        ),
        "bcm_queue": SimulationEngineInfo(
            "BCM Queue Simulator",
            "queue",
            "Queue theory simulation (M/M/c)"
        ),
        "advanced_bia": SimulationEngineInfo(
            "Advanced BIA Engine",
            "bia",
            "Multi-resource BIA simulation"
        ),
        "jaamsim_client": SimulationEngineInfo(
            "JaamSim Client",
            "bcm_exercise",
            "BCM exercise orchestrator"
        )
    }

    def __init__(self, base_url: str = "http://localhost:8095", timeout: float = 60.0):
        """
        Initialize simulation service bridge

        Args:
            base_url: Base URL of simulation_service
            timeout: HTTP request timeout
        """
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.is_connected = False

    async def connect(self) -> bool:
        """
        Connect to simulation_service and verify availability

        Returns:
            True if connected successfully
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")

            if response.status_code == 200:
                health_data = response.json()
                logger.info(
                    f" Connected to simulation_service v{health_data.get('version', 'unknown')}"
                )
                self.is_connected = True
                return True

        except Exception as error:
            logger.error(f"Failed to connect to simulation_service: {error}")
            self.is_connected = False

        return False

    async def get_available_engines(self) -> List[Dict[str, Any]]:
        """
        Get list of available simulation engines

        Returns:
            List of engine information
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/engines")

            if response.status_code == 200:
                return response.json()

        except Exception as error:
            logger.error(f"Failed to get engines: {error}")

        # Fallback to known engines
        return [
            {
                "name": engine.name,
                "type": engine.engine_type,
                "description": engine.description,
                "available": engine.available
            }
            for engine in self.ENGINES.values()
        ]

    async def create_simulation(
        self,
        name: str,
        simulation_type: str,
        parameters: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new simulation

        Args:
            name: Simulation name
            simulation_type: Type (monte_carlo, what_if, scenario, etc.)
            parameters: Simulation parameters
            tenant_id: Tenant ID for multi-tenancy

        Returns:
            Created simulation details
        """
        payload = {
            "name": name,
            "simulation_type": simulation_type,
            "parameters": parameters
        }

        if tenant_id:
            payload["tenant_id"] = tenant_id

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/simulations",
                json=payload
            )

            response.raise_for_status()
            simulation = response.json()

            logger.info(f" Created simulation: {simulation['id']}")
            return simulation

        except Exception as error:
            logger.error(f"Failed to create simulation: {error}")
            raise

    async def execute_simulation(
        self,
        simulation_id: str,
        auto_start: bool = True
    ) -> Dict[str, Any]:
        """
        Execute simulation

        Args:
            simulation_id: Simulation ID to execute
            auto_start: Whether to auto-start execution

        Returns:
            Execution details
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/simulations/{simulation_id}/execute",
                json={"auto_start": auto_start}
            )

            response.raise_for_status()
            execution = response.json()

            logger.info(f" Started execution: {execution['id']}")
            return execution

        except Exception as error:
            logger.error(f"Failed to execute simulation: {error}")
            raise

    async def get_simulation_status(self, simulation_id: str) -> Dict[str, Any]:
        """
        Get simulation status

        Args:
            simulation_id: Simulation ID

        Returns:
            Simulation status
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/simulations/{simulation_id}"
            )

            response.raise_for_status()
            return response.json()

        except Exception as error:
            logger.error(f"Failed to get simulation status: {error}")
            raise

    async def get_execution_results(self, execution_id: str) -> Dict[str, Any]:
        """
        Get execution results

        Args:
            execution_id: Execution ID

        Returns:
            Execution results
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/executions/{execution_id}"
            )

            response.raise_for_status()
            return response.json()

        except Exception as error:
            logger.error(f"Failed to get execution results: {error}")
            raise

    async def run_monte_carlo_simulation(
        self,
        name: str,
        variables: Dict[str, Dict[str, Any]],
        iterations: int = 1000,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation (convenience method)

        Args:
            name: Simulation name
            variables: Variable definitions with distributions
            iterations: Number of Monte Carlo iterations
            tenant_id: Tenant ID

        Returns:
            Simulation results
        """
        # Create simulation
        simulation = await self.create_simulation(
            name=name,
            simulation_type="monte_carlo",
            parameters={
                "iterations": iterations,
                "variables": variables
            },
            tenant_id=tenant_id
        )

        # Execute
        execution = await self.execute_simulation(simulation["id"])

        # Wait for completion and get results
        # In production, use WebSocket or polling
        results = await self.get_execution_results(execution["id"])

        return results

    async def run_what_if_analysis(
        self,
        name: str,
        baseline: Dict[str, Any],
        scenarios: List[Dict[str, Any]],
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run What-If analysis (convenience method)

        Args:
            name: Analysis name
            baseline: Baseline scenario
            scenarios: Alternative scenarios to compare
            tenant_id: Tenant ID

        Returns:
            Analysis results
        """
        simulation = await self.create_simulation(
            name=name,
            simulation_type="what_if",
            parameters={
                "baseline": baseline,
                "scenarios": scenarios
            },
            tenant_id=tenant_id
        )

        execution = await self.execute_simulation(simulation["id"])
        results = await self.get_execution_results(execution["id"])

        return results

    async def run_bcm_scenario(
        self,
        name: str,
        scenario_id: str,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run BCM scenario (convenience method)

        Args:
            name: Execution name
            scenario_id: Scenario ID to run
            tenant_id: Tenant ID

        Returns:
            Scenario execution results
        """
        simulation = await self.create_simulation(
            name=name,
            simulation_type="scenario",
            parameters={
                "scenario_id": scenario_id
            },
            tenant_id=tenant_id
        )

        execution = await self.execute_simulation(simulation["id"])
        results = await self.get_execution_results(execution["id"])

        return results

    async def generate_scenario(
        self,
        category: str,
        complexity: int = 3,
        industry: Optional[str] = None,
        organization_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered scenario

        Args:
            category: Scenario category (cyber, pandemic, etc.)
            complexity: Complexity level 1-5
            industry: Industry type
            organization_size: Organization size

        Returns:
            Generated scenario
        """
        payload = {
            "category": category,
            "complexity": complexity
        }

        if industry:
            payload["industry"] = industry
        if organization_size:
            payload["organization_size"] = organization_size

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/scenarios/generate",
                json=payload
            )

            response.raise_for_status()
            scenario = response.json()

            logger.info(f" Generated scenario: {scenario['id']}")
            return scenario

        except Exception as error:
            logger.error(f"Failed to generate scenario: {error}")
            raise

    async def search_scenarios(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search scenario library

        Args:
            query: Search query
            category: Filter by category
            limit: Max results

        Returns:
            Matching scenarios
        """
        params = {
            "query": query,
            "limit": limit
        }

        if category:
            params["category"] = category

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/scenarios/search",
                params=params
            )

            response.raise_for_status()
            return response.json()

        except Exception as error:
            logger.error(f"Failed to search scenarios: {error}")
            return []

    async def get_service_metrics(self) -> Dict[str, Any]:
        """
        Get simulation service metrics

        Returns:
            Service metrics
        """
        try:
            response = await self.client.get(f"{self.base_url}/metrics")

            if response.status_code == 200:
                # Parse Prometheus metrics
                return {
                    "format": "prometheus",
                    "raw": response.text
                }

        except Exception as error:
            logger.error(f"Failed to get metrics: {error}")

        return {}

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
