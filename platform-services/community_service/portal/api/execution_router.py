"""
Simulation Execution API
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from database.connection import get_db
from database.simulation_model import Simulation, SimulationExecution, SimulationResult

# Import engines
from engines.what_if_engine import WhatIfEngine
from engines.monte_carlo_engine import MonteCarloEngine
from engines.scenario_engine import ScenarioEngine

router = APIRouter()


async def run_simulation_background(sim_id: int, db: AsyncSession):
    """Background task to run simulation"""
    import asyncio

    stmt = select(Simulation).where(Simulation.id == sim_id)
    result = await db.execute(stmt)
    sim = result.scalar_one_or_none()

    if not sim:
        return

    try:
        # Update status
        sim.status = 'running'
        sim.started_at = datetime.utcnow()
        await db.commit()

        # Select engine
        engine_class = None
        if sim.simulation_type == 'what_if':
            engine_class = WhatIfEngine
        elif sim.simulation_type == 'monte_carlo':
            engine_class = MonteCarloEngine
        elif sim.simulation_type == 'scenario':
            engine_class = ScenarioEngine

        if not engine_class:
            raise ValueError(f"Unknown simulation type: {sim.simulation_type}")

        # Run simulation
        engine = engine_class(sim.id, sim.parameters)
        results = await engine.run()

        # Save results
        db_result = SimulationResult(
            simulation_id=sim.id,
            result_type='final',
            result_data=results
        )
        db.add(db_result)

        # Update simulation
        sim.status = 'completed'
        sim.completed_at = datetime.utcnow()
        await db.commit()

        # await publish_simulation_event(
        #     "completed",
        #     sim.id,
        #     {"results_summary": results},
        #     tenant_id=sim.tenant_id
        # )

    except Exception as e:
        sim.status = 'failed'
        sim.completed_at = datetime.utcnow()
        await db.commit()

        # await publish_simulation_event(
        #     "failed",
        #     sim.id,
        #     {"error": str(e)},
        #     tenant_id=sim.tenant_id
        # )


@router.post("/simulations/{sim_id}/run")
async def run_simulation(
    sim_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Run simulation"""

    stmt = select(Simulation).where(Simulation.id == sim_id)
    result = await db.execute(stmt)
    sim = result.scalar_one_or_none()

    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if sim.status == 'running':
        raise HTTPException(status_code=400, detail="Simulation already running")

    # Run in background
    background_tasks.add_task(run_simulation_background, sim_id, db)

    return {
        "simulation_id": sim.id,
        "status": "started",
        "message": "Simulation started in background"
    }


@router.get("/simulations/{sim_id}/status")
async def get_simulation_status(
    sim_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get simulation status"""

    stmt = select(Simulation).where(Simulation.id == sim_id)
    result = await db.execute(stmt)
    sim = result.scalar_one_or_none()

    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    return {
        "simulation_id": sim.id,
        "status": sim.status,
        "started_at": sim.started_at,
        "completed_at": sim.completed_at
    }


@router.get("/simulations/{sim_id}/results")
async def get_simulation_results(
    sim_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get simulation results"""

    stmt = select(Simulation).where(Simulation.id == sim_id)
    result = await db.execute(stmt)
    sim = result.scalar_one_or_none()

    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if sim.status != 'completed':
        raise HTTPException(status_code=400, detail=f"Simulation not completed (status: {sim.status})")

    # Get results
    results_stmt = select(SimulationResult)\
        .where(SimulationResult.simulation_id == sim_id)\
        .order_by(SimulationResult.recorded_at.desc())

    results_result = await db.execute(results_stmt)
    results = results_result.scalars().all()

    return {
        "simulation_id": sim.id,
        "status": sim.status,
        "results": [
            {
                "id": r.id,
                "result_type": r.result_type,
                "result_data": r.result_data,
                "confidence_score": r.confidence_score,
                "recorded_at": r.recorded_at
            }
            for r in results
        ]
    }


@router.post("/simulations/{sim_id}/stop")
async def stop_simulation(
    sim_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Stop running simulation"""

    stmt = select(Simulation).where(Simulation.id == sim_id)
    result = await db.execute(stmt)
    sim = result.scalar_one_or_none()

    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if sim.status != 'running':
        raise HTTPException(status_code=400, detail="Simulation not running")

    # Mark as stopped (in real implementation would kill background task)
    sim.status = 'failed'
    sim.completed_at = datetime.utcnow()
    await db.commit()

    # await publish_simulation_event(
    #     "stopped",
    #     sim.id,
    #     {},
    #     tenant_id=sim.tenant_id
    # )

    return {
        "simulation_id": sim.id,
        "status": "stopped"
    }
