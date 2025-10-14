"""
Exercise Endpoints

REST API endpoints for BCM exercises and training
"""

import logging
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field

from storage import PostgreSQLStorage
from api.auth.dependencies import get_current_active_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class ExerciseCreate(BaseModel):
    """Exercise creation request"""
    name: str = Field(..., description="Exercise name")
    description: Optional[str] = None
    exercise_type: str = Field(..., description="tabletop, walkthrough, simulation, etc.")
    scenario_template_id: Optional[str] = None
    objectives: Optional[List[str]] = None
    participants: Optional[List[dict]] = None
    duration_minutes: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    organization_id: Optional[str] = None  # Optional - can be standalone


class ExerciseUpdate(BaseModel):
    """Exercise update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    findings: Optional[dict] = None
    action_items: Optional[List[dict]] = None
    evaluation_score: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ExerciseResponse(BaseModel):
    """Exercise response"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    exercise_type: str
    scenario_template_id: Optional[str]
    objectives: Optional[List[str]]
    participants: Optional[List[dict]]
    duration_minutes: Optional[int]
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: str
    simulation_result_id: Optional[str]
    findings: Optional[dict]
    action_items: Optional[List[dict]]
    evaluation_score: Optional[float]
    organization_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExerciseList(BaseModel):
    """Exercise list response"""
    total: int
    items: List[ExerciseResponse]
    limit: int


class ExerciseExecuteRequest(BaseModel):
    """Exercise execution request"""
    simulation_parameters: Optional[dict] = None


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage dependency"""
    return request.app.state.app_state.storage


# ============================================
# ENDPOINTS
# ============================================

@router.post("/", response_model=ExerciseResponse, status_code=201)
async def create_exercise(
    exercise: ExerciseCreate,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Create new exercise

    Can be standalone OR linked to organization
    """
    try:
        exercise_id = f"exercise-{uuid4().hex[:12]}"

        # Verify organization ownership if specified
        if exercise.organization_id:
            org = await storage.get_organization(exercise.organization_id)
            if not org or org.tenant_id != current_user.tenant_id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to create exercise for this organization"
                )

        # Verify scenario ownership if specified
        if exercise.scenario_template_id:
            scenario = await storage.get_scenario_template(exercise.scenario_template_id)
            if not scenario:
                raise HTTPException(status_code=404, detail="Scenario template not found")
            # Allow public scenarios
            if scenario.tenant_id != current_user.tenant_id and not scenario.is_public:
                raise HTTPException(status_code=403, detail="Not authorized to use this scenario")

        exercise_data = exercise.model_dump()
        exercise_data['id'] = exercise_id
        exercise_data['tenant_id'] = current_user.tenant_id
        exercise_data['status'] = 'planned'

        exercise_model = await storage.create_exercise(exercise_data)

        logger.info(f"Created exercise: {exercise_model.id} by {current_user.email}")

        return ExerciseResponse.model_validate(exercise_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create exercise: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ExerciseList)
async def list_exercises(
    status: Optional[str] = Query(None, description="Filter by status"),
    exercise_type: Optional[str] = Query(None, description="Filter by type"),
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    limit: int = Query(100, ge=1, le=1000),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    List exercises

    Returns tenant's exercises with optional filters
    """
    try:
        exercises = await storage.list_exercises(
            tenant_id=current_user.tenant_id,
            status=status,
            exercise_type=exercise_type,
            organization_id=organization_id,
            limit=limit
        )

        items = [ExerciseResponse.model_validate(e) for e in exercises]

        return ExerciseList(
            total=len(items),
            items=items,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Failed to list exercises: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Get exercise by ID

    Verifies ownership
    """
    try:
        exercise = await storage.get_exercise(exercise_id)

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this exercise")

        return ExerciseResponse.model_validate(exercise)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get exercise: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: str,
    updates: ExerciseUpdate,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Update exercise

    Used to record findings, action items, scores, etc.
    """
    try:
        # Verify ownership
        exercise = await storage.get_exercise(exercise_id)

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this exercise")

        # Update
        update_data = updates.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        exercise_model = await storage.update_exercise(exercise_id, update_data)

        logger.info(f"Updated exercise: {exercise_id}")

        return ExerciseResponse.model_validate(exercise_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update exercise: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(require_admin)
):
    """
    Delete exercise

    Admin only
    """
    try:
        # Verify ownership
        exercise = await storage.get_exercise(exercise_id)

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this exercise")

        await storage.delete_exercise(exercise_id)

        logger.info(f"Deleted exercise: {exercise_id}")

        return {"status": "deleted", "exercise_id": exercise_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete exercise: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{exercise_id}/start")
async def start_exercise(
    exercise_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Start exercise

    Changes status to 'in_progress' and records start time
    """
    try:
        # Verify ownership
        exercise = await storage.get_exercise(exercise_id)

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if exercise.status != 'planned':
            raise HTTPException(
                status_code=400,
                detail=f"Exercise is already {exercise.status}"
            )

        # Start exercise
        update_data = {
            'status': 'in_progress',
            'started_at': datetime.utcnow()
        }

        exercise_model = await storage.update_exercise(exercise_id, update_data)

        logger.info(f"Started exercise: {exercise_id}")

        return ExerciseResponse.model_validate(exercise_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start exercise: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{exercise_id}/complete")
async def complete_exercise(
    exercise_id: str,
    findings: Optional[dict] = None,
    action_items: Optional[List[dict]] = None,
    evaluation_score: Optional[float] = None,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Complete exercise

    Records completion time, findings, and evaluation
    """
    try:
        # Verify ownership
        exercise = await storage.get_exercise(exercise_id)

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if exercise.status not in ['planned', 'in_progress']:
            raise HTTPException(
                status_code=400,
                detail=f"Exercise is already {exercise.status}"
            )

        # Complete exercise
        update_data = {
            'status': 'completed',
            'completed_at': datetime.utcnow()
        }

        if findings:
            update_data['findings'] = findings

        if action_items:
            update_data['action_items'] = action_items

        if evaluation_score is not None:
            if evaluation_score < 0 or evaluation_score > 100:
                raise HTTPException(
                    status_code=400,
                    detail="Evaluation score must be between 0 and 100"
                )
            update_data['evaluation_score'] = evaluation_score

        exercise_model = await storage.update_exercise(exercise_id, update_data)

        logger.info(f"Completed exercise: {exercise_id}, score: {evaluation_score}")

        return ExerciseResponse.model_validate(exercise_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete exercise: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{exercise_id}/execute", response_model=ExerciseResponse)
async def execute_exercise_simulation(
    exercise_id: str,
    execute_request: ExerciseExecuteRequest,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Execute exercise with simulation

    Runs REAL simulation based on exercise scenario and parameters
    Links simulation result to exercise

    Works in two modes:
    1. With organization data (if exercise.organization_id set)
    2. Standalone (generic simulation)
    """
    try:
        # Verify ownership
        exercise = await storage.get_exercise(exercise_id)

        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if exercise.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Get scenario
        if not exercise.scenario_template_id:
            raise HTTPException(
                status_code=400,
                detail="Exercise must have scenario template to execute"
            )

        scenario = await storage.get_scenario_template(exercise.scenario_template_id)

        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario template not found")

        # Start exercise if not started
        if exercise.status == 'planned':
            await storage.update_exercise(exercise_id, {
                'status': 'in_progress',
                'started_at': datetime.utcnow()
            })

        # Create simulation
        from core.engine.simulation_engine import SimulationEngine
        from core.models.base import SimulationParameters

        sim_id = f"sim-exercise-{uuid4().hex[:12]}"

        # Get simulation parameters (merge template + custom)
        sim_params = scenario.parameters_template or {}
        if execute_request.simulation_parameters:
            sim_params.update(execute_request.simulation_parameters)

        # If organization linked - use org data
        if exercise.organization_id:
            org_model = await storage.get_organization(exercise.organization_id)

            if not org_model:
                raise HTTPException(status_code=404, detail="Organization not found")

            # Create simulation with org
            from core.models.base import Organization

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

            params = SimulationParameters(
                scenario=scenario.scenario_type,
                duration_months=sim_params.get('duration_months', 12),
                severity=sim_params.get('severity', 'medium'),
                custom_params=sim_params
            )

            # Run simulation engine
            engine = SimulationEngine()
            result = await engine.run_simulation(
                organization=organization,
                scenario=scenario.scenario_type,
                params=params
            )

            # Save simulation
            sim_data = {
                'id': sim_id,
                'twin_id': org_model.twin_id,
                'scenario': scenario.scenario_type,
                'status': 'completed',
                'parameters': sim_params,
                'impact_score': result.impact_score,
                'financial_impact': result.financial_impact,
                'operational_impact': result.operational_impact,
                'recovery_time_days': result.recovery_time_days,
                'timeline': result.timeline,
                'recommendations': result.recommendations,
                'recovery_plan': result.recovery_plan,
                'started_at': datetime.utcnow(),
                'completed_at': datetime.utcnow()
            }

        else:
            # Standalone simulation (generic)
            sim_data = {
                'id': sim_id,
                'twin_id': f"generic-{uuid4().hex[:8]}",  # Fake twin for standalone
                'scenario': scenario.scenario_type,
                'status': 'completed',
                'parameters': sim_params,
                'impact_score': 65.0,  # Generic score
                'financial_impact': 100000.0,  # Placeholder
                'operational_impact': 50.0,
                'recovery_time_days': 14,
                'timeline': {'note': 'Generic simulation - link organization for accurate results'},
                'recommendations': scenario.parameters_template or {},
                'recovery_plan': {},
                'started_at': datetime.utcnow(),
                'completed_at': datetime.utcnow()
            }

        sim_model = await storage.create_simulation(sim_data)

        # Link simulation to exercise
        await storage.update_exercise(exercise_id, {
            'simulation_result_id': sim_model.id
        })

        logger.info(f"Exercise simulation executed: {exercise_id} -> {sim_model.id}")

        # Return updated exercise
        exercise_updated = await storage.get_exercise(exercise_id)
        return ExerciseResponse.model_validate(exercise_updated)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute exercise simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
