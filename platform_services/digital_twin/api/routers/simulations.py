"""
Simulation Endpoints

REST API endpoints for BCM simulation operations
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field

from storage import PostgreSQLStorage, RedisCache
from core.models.base import SimulationScenarioType, SimulationStatus
from api.auth.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class SimulationCreate(BaseModel):
    """Simulation creation request"""
    id: str = Field(..., description="Simulation ID")
    twin_id: str = Field(..., description="Digital Twin ID")
    scenario: SimulationScenarioType = Field(..., description="Scenario type")
    parameters: dict = Field(..., description="Simulation parameters")


class SimulationUpdate(BaseModel):
    """Simulation update request"""
    status: Optional[SimulationStatus] = None
    impact_score: Optional[float] = None
    financial_impact: Optional[float] = None
    operational_impact: Optional[float] = None
    recovery_time_days: Optional[int] = None
    timeline: Optional[dict] = None
    recommendations: Optional[dict] = None
    recovery_plan: Optional[dict] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


class SimulationResponse(BaseModel):
    """Simulation response"""
    id: str
    twin_id: str
    scenario: str
    status: str
    parameters: dict
    impact_score: Optional[float]
    financial_impact: Optional[float]
    operational_impact: Optional[float]
    recovery_time_days: Optional[int]
    timeline: Optional[dict]
    recommendations: Optional[dict]
    recovery_plan: Optional[dict]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SimulationList(BaseModel):
    """Simulation list response"""
    total: int
    items: List[SimulationResponse]
    limit: int


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage dependency"""
    return request.app.state.app_state.storage


def get_cache(request: Request) -> RedisCache:
    """Get cache dependency"""
    return request.app.state.app_state.cache


# ============================================
# ENDPOINTS
# ============================================

@router.post("/", response_model=SimulationResponse, status_code=201)
async def create_simulation(
    simulation: SimulationCreate,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Create new simulation

    Creates a simulation in PENDING status, ready to be executed
    """
    try:
        # Verify twin exists and belongs to user's tenant
        org = await storage.get_organization(twin_id=simulation.twin_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        if org.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to create simulation for this organization")

        # Create simulation
        sim_data = simulation.model_dump()
        sim_data['status'] = SimulationStatus.PENDING
        sim_data['started_at'] = datetime.utcnow()

        sim_model = await storage.create_simulation(sim_data)

        # Cache it
        await cache.cache_simulation(sim_model.id, simulation.model_dump())

        logger.info(f"Created simulation: {sim_model.id}")

        return SimulationResponse.model_validate(sim_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sim_id}", response_model=SimulationResponse)
async def get_simulation(
    sim_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Get simulation by ID

    Retrieves simulation result with caching
    """
    try:
        # Try cache first
        cached = await cache.get_simulation(sim_id)
        if cached:
            # Verify ownership via twin_id
            twin_id = cached.get('twin_id')
            if twin_id:
                org = await storage.get_organization(twin_id=twin_id)
                if org and org.tenant_id != current_user.tenant_id:
                    raise HTTPException(status_code=403, detail="Not authorized to access this simulation")
            logger.debug(f"Cache hit for simulation: {sim_id}")
            return SimulationResponse(**cached)

        # Cache miss - get from database
        sim_model = await storage.get_simulation(sim_id)

        if not sim_model:
            raise HTTPException(status_code=404, detail="Simulation not found")

        # Verify ownership
        org = await storage.get_organization(twin_id=sim_model.twin_id)
        if org and org.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this simulation")

        # Cache for next time
        sim_dict = {
            'id': sim_model.id,
            'twin_id': sim_model.twin_id,
            'scenario': sim_model.scenario,
            'status': sim_model.status,
            'parameters': sim_model.parameters,
            'impact_score': sim_model.impact_score,
            'financial_impact': sim_model.financial_impact,
            'operational_impact': sim_model.operational_impact,
            'recovery_time_days': sim_model.recovery_time_days,
            'timeline': sim_model.timeline,
            'recommendations': sim_model.recommendations,
            'recovery_plan': sim_model.recovery_plan,
            'started_at': sim_model.started_at.isoformat() if sim_model.started_at else None,
            'completed_at': sim_model.completed_at.isoformat() if sim_model.completed_at else None,
            'duration_seconds': sim_model.duration_seconds,
            'error_message': sim_model.error_message,
            'created_at': sim_model.created_at.isoformat(),
            'updated_at': sim_model.updated_at.isoformat()
        }
        await cache.cache_simulation(sim_id, sim_dict)

        return SimulationResponse.model_validate(sim_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{sim_id}", response_model=SimulationResponse)
async def update_simulation(
    sim_id: str,
    updates: SimulationUpdate,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Update simulation

    Updates simulation status, results, or error information
    """
    try:
        # Verify ownership first
        sim_model = await storage.get_simulation(sim_id)

        if not sim_model:
            raise HTTPException(status_code=404, detail="Simulation not found")

        # Verify ownership via twin_id
        org = await storage.get_organization(twin_id=sim_model.twin_id)
        if org and org.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this simulation")

        # Update in database
        update_data = updates.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        sim_model = await storage.update_simulation(sim_id, update_data)

        # Invalidate cache
        await cache.delete('simulation', sim_id)

        logger.info(f"Updated simulation: {sim_id}")

        return SimulationResponse.model_validate(sim_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=SimulationList)
async def list_simulations(
    twin_id: Optional[str] = Query(None, description="Filter by twin ID"),
    scenario: Optional[SimulationScenarioType] = Query(None, description="Filter by scenario"),
    status: Optional[SimulationStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    List simulations

    Returns list of simulations with optional filters
    """
    try:
        # Get simulations (filtered by tenant)
        simulations = await storage.list_simulations(
            tenant_id=current_user.tenant_id,  # ← TENANT FILTER
            twin_id=twin_id,
            scenario=scenario,
            status=status,
            limit=limit
        )

        # Convert to response models
        items = [SimulationResponse.model_validate(sim) for sim in simulations]

        return SimulationList(
            total=len(items),
            items=items,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Failed to list simulations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/twin/{twin_id}/latest", response_model=SimulationResponse)
async def get_latest_simulation(
    twin_id: str,
    scenario: Optional[SimulationScenarioType] = Query(None, description="Filter by scenario"),
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get latest simulation for twin

    Returns most recent simulation, optionally filtered by scenario
    """
    try:
        # Get simulations (already sorted by created_at desc)
        simulations = await storage.list_simulations(
            twin_id=twin_id,
            scenario=scenario,
            status=None,
            limit=1
        )

        if not simulations:
            raise HTTPException(status_code=404, detail="No simulations found")

        return SimulationResponse.model_validate(simulations[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{sim_id}/execute")
async def execute_simulation(
    sim_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Execute simulation

    Triggers REAL simulation execution with SimulationEngine
    """
    try:
        # Get simulation
        sim_model = await storage.get_simulation(sim_id)

        if not sim_model:
            raise HTTPException(status_code=404, detail="Simulation not found")

        if sim_model.status != SimulationStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Simulation already {sim_model.status}"
            )

        # Update to RUNNING
        await storage.update_simulation(sim_id, {
            'status': SimulationStatus.RUNNING,
            'started_at': datetime.utcnow()
        })

        # Get organization/digital twin
        org_model = await storage.get_organization(twin_id=sim_model.twin_id)

        if not org_model:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Import simulation engine
        from core.engine.simulation_engine import SimulationEngine
        from core.models.base import Organization, SimulationParameters

        # Convert to core models
        organization = Organization(
            id=org_model.id,
            twin_id=org_model.twin_id,
            name=org_model.name,
            org_type=org_model.org_type,
            industry=org_model.industry,
            employee_count=org_model.employee_count or 100,
            annual_revenue=org_model.annual_revenue or 1000000.0,
            annual_budget=org_model.annual_budget or 500000.0,
            headquarters=org_model.headquarters or {},
            contacts=org_model.contacts or {},
            metadata=org_model.metadata or {}
        )

        # Create simulation parameters
        params = SimulationParameters(
            scenario=sim_model.scenario,
            duration_months=sim_model.parameters.get('duration_months', 12),
            severity=sim_model.parameters.get('severity', 'medium'),
            custom_params=sim_model.parameters
        )

        # Run simulation ENGINE
        engine = SimulationEngine()
        result = await engine.run_simulation(
            organization=organization,
            scenario=sim_model.scenario,
            params=params
        )

        # Update simulation with results
        update_data = {
            'status': SimulationStatus.COMPLETED,
            'impact_score': result.impact_score,
            'financial_impact': result.financial_impact,
            'operational_impact': result.operational_impact,
            'recovery_time_days': result.recovery_time_days,
            'timeline': result.timeline,
            'recommendations': result.recommendations,
            'recovery_plan': result.recovery_plan,
            'completed_at': datetime.utcnow(),
            'duration_seconds': (datetime.utcnow() - sim_model.started_at).total_seconds()
        }

        await storage.update_simulation(sim_id, update_data)

        # Invalidate cache
        await cache.delete('simulation', sim_id)

        logger.info(f"Simulation completed: {sim_id} - Impact: {result.impact_score}")

        return {
            'simulation_id': sim_id,
            'status': 'completed',
            'impact_score': result.impact_score,
            'financial_impact': result.financial_impact,
            'operational_impact': result.operational_impact,
            'recovery_time_days': result.recovery_time_days,
            'message': 'Simulation executed successfully'
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Simulation execution failed: {e}", exc_info=True)

        # Update to FAILED
        try:
            await storage.update_simulation(sim_id, {
                'status': SimulationStatus.FAILED,
                'error_message': str(e),
                'completed_at': datetime.utcnow()
            })
        except:
            pass

        raise HTTPException(status_code=500, detail=str(e))


@router.get("/twin/{twin_id}/summary")
async def get_simulation_summary(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get simulation summary for twin

    Returns summary of all simulations grouped by scenario
    """
    try:
        # Verify twin exists
        org = await storage.get_organization(twin_id=twin_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Get all simulations
        simulations = await storage.list_simulations(
            twin_id=twin_id,
            scenario=None,
            status=None,
            limit=1000
        )

        # Group by scenario
        summary = {}
        for sim in simulations:
            scenario = sim.scenario
            if scenario not in summary:
                summary[scenario] = {
                    'total': 0,
                    'completed': 0,
                    'pending': 0,
                    'running': 0,
                    'failed': 0,
                    'latest': None
                }

            summary[scenario]['total'] += 1
            summary[scenario][sim.status] = summary[scenario].get(sim.status, 0) + 1

            # Track latest
            if not summary[scenario]['latest'] or sim.created_at > summary[scenario]['latest']['created_at']:
                summary[scenario]['latest'] = {
                    'id': sim.id,
                    'status': sim.status,
                    'created_at': sim.created_at.isoformat(),
                    'impact_score': sim.impact_score
                }

        return {
            'twin_id': twin_id,
            'organization_name': org.name,
            'total_simulations': len(simulations),
            'by_scenario': summary
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get simulation summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
