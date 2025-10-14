"""
FastAPI Endpoints for Process Framework

Provides REST API for Process Framework functionality:
- List available processes
- Start process instances
- Execute process steps
- Query instance status
- Get execution history
- AI-powered automatic execution

Author: AI Platform Team
Date: 2025-10-11
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from process_framework import ProcessFramework, ProcessInstance
from process_orchestration_api import ProcessOrchestrator
from visualization import ProcessVisualizer
from metrics.process_metrics import process_metrics

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/processes", tags=["Process Framework"])

# Global instances (will be injected in production)
_framework: Optional[ProcessFramework] = None
_orchestrator: Optional[ProcessOrchestrator] = None
_visualizer: Optional[ProcessVisualizer] = None


# =====================================================
# Dependency Injection
# =====================================================

def get_framework() -> ProcessFramework:
    """Get ProcessFramework instance"""
    if _framework is None:
        raise HTTPException(status_code=500, detail="ProcessFramework not initialized")
    return _framework


def get_orchestrator() -> ProcessOrchestrator:
    """Get ProcessOrchestrator instance"""
    if _orchestrator is None:
        raise HTTPException(status_code=500, detail="ProcessOrchestrator not initialized")
    return _orchestrator


def get_visualizer() -> ProcessVisualizer:
    """Get ProcessVisualizer instance"""
    if _visualizer is None:
        return ProcessVisualizer()  # Create on-demand
    return _visualizer


def init_api(framework: ProcessFramework, orchestrator: ProcessOrchestrator, visualizer: ProcessVisualizer):
    """Initialize API with dependencies"""
    global _framework, _orchestrator, _visualizer
    _framework = framework
    _orchestrator = orchestrator
    _visualizer = visualizer
    logger.info("Process Framework API initialized")


# =====================================================
# Request/Response Models
# =====================================================

class StartProcessRequest(BaseModel):
    """Request to start a process"""
    started_by: str = Field(..., description="Email of user starting the process")
    initial_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial process data")


class StartProcessResponse(BaseModel):
    """Response after starting a process"""
    instance_id: str = Field(..., description="Unique instance ID")
    process_id: str = Field(..., description="Process definition ID")
    status: str = Field(..., description="Current status")
    current_step_id: str = Field(..., description="Current step ID")
    started_at: datetime = Field(..., description="Start timestamp")


class ExecuteStepRequest(BaseModel):
    """Request to execute a process step"""
    step_data: Dict[str, Any] = Field(..., description="Data for the step")
    executed_by: str = Field(..., description="Email of user executing the step")


class ExecuteStepResponse(BaseModel):
    """Response after executing a step"""
    success: bool = Field(..., description="Whether execution succeeded")
    next_step_id: Optional[str] = Field(None, description="Next step ID")
    errors: Optional[List[str]] = Field(None, description="Validation errors if any")
    current_step_id: str = Field(..., description="Current step after execution")
    status: str = Field(..., description="Current process status")


class ProcessStatusResponse(BaseModel):
    """Process instance status"""
    instance_id: str
    process_id: str
    status: str
    current_step_id: str
    started_by: str
    started_at: datetime
    completed_at: Optional[datetime]
    progress_percentage: float
    step_count: int
    completed_steps: int


class AutoExecuteRequest(BaseModel):
    """Request for AI-powered automatic execution"""
    started_by: str = Field(..., description="Email of user starting the process")
    initial_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial process data")


# =====================================================
# API Endpoints
# =====================================================

@router.get("/", response_model=List[Dict[str, Any]])
async def list_processes(framework: ProcessFramework = Depends(get_framework)):
    """
    List all available process definitions

    Returns list of processes with metadata:
    - id, name, version
    - category, ISO clause
    - step count
    """
    try:
        processes = framework.list_processes()

        # Track metric
        logger.info(f"Listed {len(processes)} processes")

        return processes
    except Exception as e:
        logger.error(f"Error listing processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{process_id}", response_model=Dict[str, Any])
async def get_process_definition(
    process_id: str,
    framework: ProcessFramework = Depends(get_framework)
):
    """
    Get detailed process definition

    Returns:
    - Process metadata
    - All steps with forms
    - Navigation structure
    """
    try:
        process = framework.get_process(process_id)

        if not process:
            raise HTTPException(status_code=404, detail=f"Process {process_id} not found")

        return {
            "id": process.id,
            "name": process.name,
            "version": process.version,
            "description": process.description,
            "category": process.category,
            "iso_clause": process.iso_clause,
            "start_step_id": process.start_step_id,
            "end_step_ids": process.end_step_ids,
            "step_count": len(process.steps),
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "description": step.description,
                    "step_type": step.step_type.value,
                    "next_steps": step.next_steps,
                    "allowed_roles": step.allowed_roles,
                    "form_fields_count": len(step.form_fields)
                }
                for step in process.steps.values()
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting process {process_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{process_id}/start", response_model=StartProcessResponse)
async def start_process(
    process_id: str,
    request: StartProcessRequest,
    framework: ProcessFramework = Depends(get_framework)
):
    """
    Start a new process instance

    Creates new instance and returns instance ID for tracking
    """
    try:
        # Start process
        instance = framework.start_process(
            process_id=process_id,
            started_by=request.started_by,
            initial_data=request.initial_data
        )

        # Track metric
        process_metrics.track_process_start(process_id)

        logger.info(f"Started process {process_id} as {instance.instance_id} by {request.started_by}")

        return StartProcessResponse(
            instance_id=instance.instance_id,
            process_id=instance.process_id,
            status=instance.status,
            current_step_id=instance.current_step_id,
            started_at=instance.started_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting process {process_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}", response_model=ProcessStatusResponse)
async def get_instance(
    instance_id: str,
    framework: ProcessFramework = Depends(get_framework)
):
    """
    Get process instance status

    Returns current state, progress, and metadata
    """
    try:
        instance = framework.get_instance(instance_id)

        if not instance:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        # Calculate progress
        process = framework.get_process(instance.process_id)
        total_steps = len(process.steps) if process else 0
        completed_steps = len(instance.step_history)
        progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0

        return ProcessStatusResponse(
            instance_id=instance.instance_id,
            process_id=instance.process_id,
            status=instance.status,
            current_step_id=instance.current_step_id,
            started_by=instance.started_by,
            started_at=instance.started_at,
            completed_at=instance.completed_at,
            progress_percentage=round(progress, 2),
            step_count=total_steps,
            completed_steps=completed_steps
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting instance {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}/current-form")
async def get_current_form(
    instance_id: str,
    framework: ProcessFramework = Depends(get_framework)
):
    """
    Get form for current step

    Returns form fields with validations for user to fill
    """
    try:
        form = framework.get_current_step_form(instance_id)

        if not form:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        logger.info(f"Retrieved form for instance {instance_id}, step {form['step_id']}")

        return form
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting form for {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/instances/{instance_id}/execute", response_model=ExecuteStepResponse)
async def execute_step(
    instance_id: str,
    request: ExecuteStepRequest,
    framework: ProcessFramework = Depends(get_framework)
):
    """
    Execute current process step

    Validates data and transitions to next step if successful
    """
    try:
        instance = framework.get_instance(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        current_step_before = instance.current_step_id

        # Execute step with timing
        import time
        start_time = time.time()

        result, next_step = framework.execute_step(
            instance_id=instance_id,
            step_data=request.step_data,
            executed_by=request.executed_by
        )

        duration = time.time() - start_time

        # Track metrics
        process_metrics.track_step_execution(
            instance.process_id,
            current_step_before,
            duration,
            "success" if result.get("success") else "failure"
        )

        # Get updated instance
        updated_instance = framework.get_instance(instance_id)

        logger.info(
            f"Executed step {current_step_before} for {instance_id} by {request.executed_by}: "
            f"{'success' if result['success'] else 'failure'}"
        )

        return ExecuteStepResponse(
            success=result["success"],
            next_step_id=next_step,
            errors=result.get("errors"),
            current_step_id=updated_instance.current_step_id,
            status=updated_instance.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing step for {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}/history")
async def get_execution_history(
    instance_id: str,
    framework: ProcessFramework = Depends(get_framework)
):
    """
    Get execution history for instance

    Returns chronological list of all step executions
    """
    try:
        instance = framework.get_instance(instance_id)

        if not instance:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        return {
            "instance_id": instance_id,
            "process_id": instance.process_id,
            "status": instance.status,
            "history": instance.step_history,
            "step_count": len(instance.step_history)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history for {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{process_id}/execute-auto")
async def execute_automatically(
    process_id: str,
    request: AutoExecuteRequest,
    background_tasks: BackgroundTasks,
    orchestrator: ProcessOrchestrator = Depends(get_orchestrator)
):
    """
    Execute process automatically with AI

    AI Orchestrator will:
    - Fill forms automatically
    - Perform analysis steps
    - Make decisions
    - Generate documents

    Returns immediately with instance_id, execution continues in background
    """
    try:
        # Start in background
        async def run_auto_execution():
            try:
                result = await orchestrator.execute_process_automatically(
                    process_id=process_id,
                    initial_data=request.initial_data,
                    user_email=request.started_by
                )
                logger.info(f"Auto-execution completed for {process_id}: {result}")
            except Exception as e:
                logger.error(f"Auto-execution failed for {process_id}: {e}")

        background_tasks.add_task(run_auto_execution)

        # Return immediately with tracking info
        return {
            "message": "Process execution started in background",
            "process_id": process_id,
            "started_by": request.started_by,
            "status": "running"
        }
    except Exception as e:
        logger.error(f"Error starting auto-execution for {process_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}/visualize/mermaid")
async def get_mermaid_diagram(
    instance_id: str,
    framework: ProcessFramework = Depends(get_framework),
    visualizer: ProcessVisualizer = Depends(get_visualizer)
):
    """
    Get Mermaid diagram for process visualization

    Returns Mermaid markdown syntax for rendering
    """
    try:
        instance = framework.get_instance(instance_id)

        if not instance:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        diagram = visualizer.generate_mermaid_diagram(instance.process_id)

        return {
            "instance_id": instance_id,
            "process_id": instance.process_id,
            "diagram": diagram,
            "format": "mermaid"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating diagram for {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}/visualize/status")
async def get_visual_status(
    instance_id: str,
    framework: ProcessFramework = Depends(get_framework),
    visualizer: ProcessVisualizer = Depends(get_visualizer)
):
    """
    Get visual status data for frontend visualization

    Returns JSON optimized for progress bars, timelines, etc.
    """
    try:
        instance = framework.get_instance(instance_id)

        if not instance:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        status = visualizer.generate_process_status(instance_id)

        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating visual status for {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_id}/visualize/timeline")
async def get_timeline(
    instance_id: str,
    framework: ProcessFramework = Depends(get_framework),
    visualizer: ProcessVisualizer = Depends(get_visualizer)
):
    """
    Get execution timeline for Gantt chart visualization

    Returns timeline data with durations and timestamps
    """
    try:
        instance = framework.get_instance(instance_id)

        if not instance:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")

        timeline = visualizer.generate_timeline(instance_id)

        return timeline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating timeline for {instance_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# Health Check
# =====================================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Process Framework API",
        "timestamp": datetime.now().isoformat(),
        "framework_initialized": _framework is not None,
        "orchestrator_initialized": _orchestrator is not None
    }


# =====================================================
# Metrics Endpoint
# =====================================================

@router.get("/metrics/summary")
async def get_metrics_summary(framework: ProcessFramework = Depends(get_framework)):
    """
    Get summary of process metrics

    Returns aggregated statistics across all processes
    """
    try:
        # Get all instances
        all_instances = []
        for process_id in framework.processes.keys():
            # This would need to be implemented in ProcessFramework
            # For now, return placeholder
            pass

        return {
            "total_processes": len(framework.processes),
            "message": "Full metrics available via Prometheus /metrics endpoint"
        }
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
