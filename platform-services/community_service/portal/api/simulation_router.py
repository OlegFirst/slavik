"""
Simulation CRUD API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database.connection import get_db
from database.simulation_model import Simulation

router = APIRouter()

# Pydantic schemas
class SimulationCreate(BaseModel):
    tenant_id: str
    name: str
    simulation_type: str  # what_if, monte_carlo, scenario, optimization
    engine: Optional[str] = "internal"
    parameters: dict
    metadata: dict = {}

class SimulationResponse(BaseModel):
    id: int
    tenant_id: str
    name: str
    simulation_type: str
    engine: str
    parameters: dict
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/simulations", response_model=SimulationResponse, status_code=201)
async def create_simulation(
    sim: SimulationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new simulation"""

    db_sim = Simulation(
        tenant_id=sim.tenant_id,
        name=sim.name,
        simulation_type=sim.simulation_type,
        engine=sim.engine,
        parameters=sim.parameters,
        sim_metadata=sim.metadata,
        status='draft'
    )

    db.add(db_sim)
    await db.commit()
    await db.refresh(db_sim)

    # await publish_simulation_event(
    #     "created",
    #     db_sim.id,
    #     {"name": db_sim.name, "type": db_sim.simulation_type},
    #     tenant_id=db_sim.tenant_id
    # )

    return db_sim


@router.get("/simulations", response_model=List[SimulationResponse])
async def list_simulations(
    tenant_id: Optional[str] = Query(None),
    simulation_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List simulations"""

    stmt = select(Simulation)

    if tenant_id:
        stmt = stmt.where(Simulation.tenant_id == tenant_id)

    if simulation_type:
        stmt = stmt.where(Simulation.simulation_type == simulation_type)

    if status:
        stmt = stmt.where(Simulation.status == status)

    stmt = stmt.order_by(Simulation.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    simulations = result.scalars().all()

    return simulations


@router.get("/simulations/{sim_id}", response_model=SimulationResponse)
async def get_simulation(
    sim_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get simulation by ID"""

    stmt = select(Simulation).where(Simulation.id == sim_id)
    result = await db.execute(stmt)
    sim = result.scalar_one_or_none()

    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return sim


@router.delete("/simulations/{sim_id}", status_code=204)
async def delete_simulation(
    sim_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete simulation"""

    stmt = select(Simulation).where(Simulation.id == sim_id)
    result = await db.execute(stmt)
    sim = result.scalar_one_or_none()

    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if sim.status == 'running':
        raise HTTPException(status_code=400, detail="Cannot delete running simulation")

    tenant_id = sim.tenant_id

    await db.delete(sim)
    await db.commit()

    # await publish_simulation_event(
    #     "deleted",
    #     sim_id,
    #     {},
    #     tenant_id=tenant_id
    # )

    return None


@router.get("/engines")
def list_engines():
    """List available simulation engines"""
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
