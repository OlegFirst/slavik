"""
Simulation Adapter for BCM Platform
=====================================

Integrates with simulation engines for business continuity exercise automation:
- JaamSim for discrete event simulation
- AnyLogic PLE for system dynamics
- Custom simulation scenarios for BCM exercises
- Automated metrics collection and analysis
- Event Bus integration for platform coordination

Adapted from: /simulation/simulation2/app.py
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models
# ============================================================================

class SimulationRequest(BaseModel):
    """Request to start simulation"""
    tenant_id: str
    exercise_id: Optional[str] = None
    scenario: Dict[str, Any]
    engine: str = "internal"  # internal, jaamsim, anylogic


class SimulationStatus(BaseModel):
    """Simulation status"""
    simulation_id: str
    tenant_id: str
    status: str  # draft, running, completed, failed
    progress: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    engine: str = "internal"


class SimulationResult(BaseModel):
    """Simulation results"""
    simulation_id: str
    tenant_id: str
    results: Dict[str, Any]
    metrics: Dict[str, float]
    confidence_score: float = 0.0
    completed_at: datetime


class ExerciseScenario(BaseModel):
    """Exercise scenario definition"""
    name: str
    duration_minutes: int
    parameters: Dict[str, Any]
    objectives: List[str] = []


# ============================================================================
# Simulation Adapter Service
# ============================================================================

class SimulationAdapter:
    """
    Adapter for managing multiple simulation engines

    Provides unified interface for:
    - Starting simulations
    - Monitoring progress
    - Collecting results
    - Publishing events
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.active_simulations: Dict[str, Dict[str, Any]] = {}
        self.simulation_engine = self.config.get("SIMULATION_ENGINE", "internal")

        logger.info(f"Simulation Adapter initialized with engine: {self.simulation_engine}")

    async def initialize(self):
        """Initialize simulation engines"""
        logger.info("Initializing simulation engines...")
        # Initialize engine-specific connections here
        logger.info("Simulation engines initialized")

    async def shutdown(self):
        """Cleanup on shutdown"""
        logger.info("Shutting down simulation engines...")
        # Cleanup active simulations
        for sim_id in list(self.active_simulations.keys()):
            await self.stop_simulation(sim_id, force=True)
        logger.info("Simulation engines shut down")

    def is_ready(self) -> bool:
        """Check if adapter is ready"""
        return True

    async def start_simulation(
        self,
        simulation_request: SimulationRequest
    ) -> Optional[str]:
        """
        Start a new simulation

        Args:
            simulation_request: Simulation parameters

        Returns:
            Simulation ID if successful, None otherwise
        """
        try:
            simulation_id = f"sim_{int(datetime.now().timestamp())}"

            # Store simulation metadata
            self.active_simulations[simulation_id] = {
                "simulation_id": simulation_id,
                "tenant_id": simulation_request.tenant_id,
                "exercise_id": simulation_request.exercise_id,
                "scenario": simulation_request.scenario,
                "engine": simulation_request.engine,
                "status": "running",
                "progress": 0.0,
                "started_at": datetime.now().isoformat(),
                "results": None
            }

            # Start simulation in background
            asyncio.create_task(
                self._run_simulation_task(simulation_id, simulation_request)
            )

            logger.info(f"Started simulation: {simulation_id}")
            return simulation_id

        except Exception as e:
            logger.error(f"Failed to start simulation: {e}")
            return None

    async def _run_simulation_task(
        self,
        simulation_id: str,
        request: SimulationRequest
    ):
        """Background task to run simulation"""
        try:
            sim_data = self.active_simulations[simulation_id]

            # Simulate processing (replace with actual engine calls)
            total_steps = 10
            for step in range(total_steps):
                await asyncio.sleep(1)  # Simulate work
                sim_data["progress"] = (step + 1) / total_steps

                logger.debug(f"Simulation {simulation_id} progress: {sim_data['progress']:.1%}")

            # Generate results
            results = {
                "scenario_name": request.scenario.get("name", "Unknown"),
                "duration_actual": total_steps,
                "events_simulated": 25,
                "success_rate": 0.85,
                "performance_metrics": {
                    "response_time_avg": 18.5,
                    "recovery_time_avg": 45.2,
                    "resource_utilization": 0.72
                }
            }

            sim_data["status"] = "completed"
            sim_data["completed_at"] = datetime.now().isoformat()
            sim_data["results"] = results
            sim_data["progress"] = 1.0

            logger.info(f"Simulation {simulation_id} completed successfully")

        except Exception as e:
            logger.error(f"Simulation {simulation_id} failed: {e}")
            if simulation_id in self.active_simulations:
                self.active_simulations[simulation_id]["status"] = "failed"
                self.active_simulations[simulation_id]["error"] = str(e)

    async def get_simulation_status(
        self,
        simulation_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get simulation status and progress"""
        sim_data = self.active_simulations.get(simulation_id)

        if not sim_data:
            return None

        if sim_data["tenant_id"] != tenant_id:
            return None

        return {
            "simulation_id": simulation_id,
            "status": sim_data["status"],
            "progress": sim_data["progress"],
            "started_at": sim_data["started_at"],
            "completed_at": sim_data.get("completed_at"),
            "engine": sim_data["engine"]
        }

    async def get_simulation_results(
        self,
        simulation_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get simulation results"""
        sim_data = self.active_simulations.get(simulation_id)

        if not sim_data:
            return None

        if sim_data["tenant_id"] != tenant_id:
            return None

        if sim_data["status"] != "completed":
            return None

        return {
            "simulation_id": simulation_id,
            "results": sim_data["results"],
            "completed_at": sim_data["completed_at"],
            "engine": sim_data["engine"]
        }

    async def stop_simulation(
        self,
        simulation_id: str,
        tenant_id: Optional[str] = None,
        force: bool = False
    ) -> bool:
        """Stop running simulation"""
        sim_data = self.active_simulations.get(simulation_id)

        if not sim_data:
            return False

        if not force and sim_data["tenant_id"] != tenant_id:
            return False

        if sim_data["status"] == "running":
            sim_data["status"] = "stopped"
            sim_data["completed_at"] = datetime.now().isoformat()
            logger.info(f"Simulation {simulation_id} stopped")
            return True

        return False

    async def validate_scenario(self, scenario: Dict[str, Any]) -> bool:
        """Validate simulation scenario"""
        required_fields = ["name"]

        for field in required_fields:
            if field not in scenario:
                return False

        return True

    async def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """List available simulation scenarios"""
        return [
            {
                "name": "cyber_attack_response",
                "description": "Ransomware attack response scenario",
                "duration_minutes": 120,
                "complexity": "medium"
            },
            {
                "name": "supply_chain_disruption",
                "description": "Major supplier failure scenario",
                "duration_minutes": 180,
                "complexity": "high"
            },
            {
                "name": "natural_disaster",
                "description": "Earthquake response scenario",
                "duration_minutes": 240,
                "complexity": "high"
            }
        ]

    async def get_scenario_details(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a scenario"""
        scenarios = await self.get_available_scenarios()

        for scenario in scenarios:
            if scenario["name"] == scenario_name:
                return scenario

        return None

    async def get_validation_errors(self, scenario: Dict[str, Any]) -> List[str]:
        """Get validation errors for scenario"""
        errors = []

        if "name" not in scenario:
            errors.append("Missing required field: name")

        return errors

    async def get_exercise_simulations(
        self,
        exercise_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Get all simulations for an exercise"""
        simulations = []

        for sim_id, sim_data in self.active_simulations.items():
            if (sim_data.get("exercise_id") == exercise_id and
                sim_data["tenant_id"] == tenant_id):
                simulations.append({
                    "simulation_id": sim_id,
                    "status": sim_data["status"],
                    "progress": sim_data["progress"],
                    "started_at": sim_data["started_at"]
                })

        return simulations

    async def get_simulation_metrics(
        self,
        tenant_id: str,
        period: str = "30d"
    ) -> Dict[str, Any]:
        """Get simulation metrics for tenant"""
        # Filter simulations by tenant
        tenant_sims = [
            sim for sim in self.active_simulations.values()
            if sim["tenant_id"] == tenant_id
        ]

        return {
            "tenant_id": tenant_id,
            "period": period,
            "total_simulations": len(tenant_sims),
            "completed": len([s for s in tenant_sims if s["status"] == "completed"]),
            "running": len([s for s in tenant_sims if s["status"] == "running"]),
            "failed": len([s for s in tenant_sims if s["status"] == "failed"])
        }

    async def create_custom_scenario(self, scenario_data: Dict[str, Any]) -> Optional[str]:
        """Create custom simulation scenario"""
        # Placeholder for custom scenario creation
        scenario_id = f"custom_{int(datetime.now().timestamp())}"
        logger.info(f"Custom scenario created: {scenario_id}")
        return scenario_id

    async def get_scenario_templates(self) -> List[Dict[str, Any]]:
        """Get available scenario templates"""
        return [
            {
                "template_id": "tpl_cyber",
                "name": "Cyber Incident Response",
                "category": "cyber",
                "description": "Template for cyber security incidents"
            },
            {
                "template_id": "tpl_natural",
                "name": "Natural Disaster",
                "category": "natural",
                "description": "Template for natural disaster scenarios"
            }
        ]

    async def start_batch_simulations(self, batch_request: Dict[str, Any]) -> Optional[str]:
        """Run multiple simulations in batch"""
        batch_id = f"batch_{int(datetime.now().timestamp())}"
        logger.info(f"Batch simulations started: {batch_id}")
        return batch_id

    async def generate_report(
        self,
        simulation_id: str,
        tenant_id: str,
        format: str = "json"
    ) -> Optional[Dict[str, Any]]:
        """Generate simulation report"""
        results = await self.get_simulation_results(simulation_id, tenant_id)

        if not results:
            return None

        return {
            "simulation_id": simulation_id,
            "report_format": format,
            "generated_at": datetime.now().isoformat(),
            "results": results["results"]
        }
