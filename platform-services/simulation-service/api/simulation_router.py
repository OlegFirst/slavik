"""
Simulation CRUD API
===================

Basic CRUD operations for simulations.

Adapted from: /simulation/api/simulation_router.py
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simulations", tags=["Simulations"])


# ============================================================================
# Pydantic Models
# ============================================================================

class SimulationCreate(BaseModel):
    """Create simulation request"""
    tenant_id: str
    name: str
    simulation_type: str  # what_if, monte_carlo, scenario, optimization
    engine: Optional[str] = "internal"
    parameters: dict
    metadata: dict = {}


class SimulationResponse(BaseModel):
    """Simulation response"""
    id: int
    tenant_id: str
    name: str
    simulation_type: str
    engine: str
    parameters: dict
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ============================================================================
# In-Memory Storage (replace with database in production)
# ============================================================================

simulations_db: dict = {}
simulation_id_counter = 1


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("", response_model=SimulationResponse, status_code=201)
async def create_simulation(sim: SimulationCreate):
    """
    Create new simulation

    Types:
    - what_if: What-if analysis
    - monte_carlo: Monte Carlo statistical simulation
    - scenario: BCM scenario exercise
    - optimization: Optimization simulation
    """
    global simulation_id_counter

    sim_id = simulation_id_counter
    simulation_id_counter += 1

    simulation = {
        "id": sim_id,
        "tenant_id": sim.tenant_id,
        "name": sim.name,
        "simulation_type": sim.simulation_type,
        "engine": sim.engine,
        "parameters": sim.parameters,
        "metadata": sim.metadata,
        "status": "draft",
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None
    }

    simulations_db[sim_id] = simulation

    logger.info(f"Created simulation: {sim_id} ({sim.name})")

    return SimulationResponse(**simulation)


@router.get("", response_model=List[SimulationResponse])
def list_simulations(
    tenant_id: Optional[str] = Query(None),
    simulation_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100
):
    """
    List simulations

    Filters:
    - tenant_id: Filter by tenant
    - simulation_type: Filter by type
    - status: Filter by status
    """
    simulations = list(simulations_db.values())

    # Apply filters
    if tenant_id:
        simulations = [s for s in simulations if s["tenant_id"] == tenant_id]

    if simulation_type:
        simulations = [s for s in simulations if s["simulation_type"] == simulation_type]

    if status:
        simulations = [s for s in simulations if s["status"] == status]

    # Sort by creation date
    simulations.sort(key=lambda x: x["created_at"], reverse=True)

    # Apply pagination
    simulations = simulations[skip:skip + limit]

    return [SimulationResponse(**s) for s in simulations]


@router.get("/{sim_id}", response_model=SimulationResponse)
def get_simulation(sim_id: int):
    """Get simulation by ID"""
    simulation = simulations_db.get(sim_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return SimulationResponse(**simulation)


@router.delete("/{sim_id}", status_code=204)
async def delete_simulation(sim_id: int):
    """Delete simulation"""
    simulation = simulations_db.get(sim_id)

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if simulation["status"] == "running":
        raise HTTPException(status_code=400, detail="Cannot delete running simulation")

    del simulations_db[sim_id]

    logger.info(f"Deleted simulation: {sim_id}")

    return None


@router.get("/engines", deprecated=True)
def list_engines():
    """
    List available simulation engines

    DEPRECATED: Use /api/engines instead
    """
    return {
        "engines": [
            {
                "name": "what_if",
                "description": "What-if analysis engine",
                "capabilities": ["impact_analysis", "dependency_analysis"]
            },
            {
                "name": "monte_carlo",
                "description": "Monte Carlo statistical simulation",
                "capabilities": ["risk_quantification", "uncertainty_analysis"]
            },
            {
                "name": "scenario",
                "description": "BCM scenario exercise engine",
                "capabilities": ["exercise_simulation", "training"]
            }
        ]
    }
