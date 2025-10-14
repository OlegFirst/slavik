"""
Simulation Execution API
=========================

Execute and monitor simulations.

Adapted from: /simulation/api/execution_router.py
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simulations", tags=["Simulation Execution"])


# ============================================================================
# Import from simulation_router
# ============================================================================

# Reference to simulations database (shared with simulation_router)
from .simulation_router import simulations_db


# ============================================================================
# Background Execution
# ============================================================================

async def run_simulation_background(sim_id: int):
    """Background task to run simulation"""
    simulation = simulations_db.get(sim_id)

    if not simulation:
        return

    try:
        # Update status
        simulation["status"] = "running"
        simulation["started_at"] = datetime.now()

        logger.info(f"Starting simulation: {sim_id}")

        # Simulate work (replace with actual engine execution)
        simulation_type = simulation["simulation_type"]

        if simulation_type == "what_if":
            results = await _run_what_if_simulation(simulation)
        elif simulation_type == "monte_carlo":
            results = await _run_monte_carlo_simulation(simulation)
        elif simulation_type == "scenario":
            results = await _run_scenario_simulation(simulation)
        else:
            results = {"status": "unknown_type"}

        # Store results
        simulation["results"] = results
        simulation["status"] = "completed"
        simulation["completed_at"] = datetime.now()

        logger.info(f"Simulation {sim_id} completed successfully")

    except Exception as e:
        logger.error(f"Simulation {sim_id} failed: {e}")
        simulation["status"] = "failed"
        simulation["completed_at"] = datetime.now()
        simulation["error"] = str(e)


async def _run_what_if_simulation(simulation: Dict) -> Dict[str, Any]:
    """Execute what-if simulation"""
    await asyncio.sleep(2)  # Simulate work

    return {
        "simulation_type": "what_if",
        "impact_score": 7.5,
        "affected_processes": 12,
        "recovery_time_estimate": 4.5
    }


async def _run_monte_carlo_simulation(simulation: Dict) -> Dict[str, Any]:
    """Execute Monte Carlo simulation"""
    await asyncio.sleep(3)  # Simulate work

    return {
        "simulation_type": "monte_carlo",
        "iterations": 10000,
        "mean_value": 125.4,
        "std_deviation": 23.1,
        "confidence_interval_95": [80.2, 170.6]
    }


async def _run_scenario_simulation(simulation: Dict) -> Dict[str, Any]:
    """Execute scenario simulation"""
    await asyncio.sleep(2)  # Simulate work

    return {
        "simulation_type": "scenario",
        "scenario_name": simulation.get("name", "Unknown"),
        "events_processed": 25,
        "success_rate": 0.85,
        "performance_score": 8.2
    }


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/{sim_id}/run")
async def run_simulation(
    sim_id: int,
    background_tasks: BackgroundTasks
):
    """
    Run simulation

    Starts simulation execution in background
    """
    simulation = simulations_db.get(sim_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation["status"] == "running":
        raise HTTPException(status_code=400, detail="Simulation already running")

    # Run in background
    background_tasks.add_task(run_simulation_background, sim_id)

    return {
        "simulation_id": sim_id,
        "status": "started",
        "message": "Simulation started in background"
    }


@router.get("/{sim_id}/status")
def get_simulation_status(sim_id: int):
    """Get simulation status"""
    simulation = simulations_db.get(sim_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return {
        "simulation_id": sim_id,
        "status": simulation["status"],
        "started_at": simulation.get("started_at"),
        "completed_at": simulation.get("completed_at")
    }


@router.get("/{sim_id}/results")
def get_simulation_results(sim_id: int):
    """Get simulation results"""
    simulation = simulations_db.get(sim_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Simulation not completed (status: {simulation['status']})"
        )

    return {
        "simulation_id": sim_id,
        "status": simulation["status"],
        "results": simulation.get("results", {}),
        "completed_at": simulation.get("completed_at")
    }


@router.post("/{sim_id}/stop")
async def stop_simulation(sim_id: int):
    """Stop running simulation"""
    simulation = simulations_db.get(sim_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation["status"] != "running":
        raise HTTPException(status_code=400, detail="Simulation not running")

    # Mark as stopped
    simulation["status"] = "stopped"
    simulation["completed_at"] = datetime.now()

    logger.info(f"Simulation {sim_id} stopped")

    return {
        "simulation_id": sim_id,
        "status": "stopped"
    }
