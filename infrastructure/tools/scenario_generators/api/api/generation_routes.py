"""
API routes for scenario generation control
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
import uuid
from typing import Dict, Any
from datetime import datetime

from models.requests import (
    GenerationRequest,
    GenerationResponse,
    ProgressResponse,
    ErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/generate", tags=["generation"])

# Global state for generation jobs (in production, use Redis/PostgreSQL)
generation_jobs: Dict[str, Dict[str, Any]] = {}
current_job: Dict[str, Any] = {
    "job_id": None,
    "status": "idle",
    "manager": None
}


async def run_generation_async(job_id: str, levels: list):
    """Run generation in background."""
    try:
        # Import here to avoid circular dependency
        import sys
        from pathlib import Path

        # Now we're in infrastructure/tools/scenario-generators/api/api/
        # Need to go up to scenario-generators root and to intelligent-core
        intelligent_core_path = Path(__file__).parent.parent.parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
        generators_root = Path(__file__).parent.parent.parent  # Up to scenario-generators/
        sys.path.insert(0, str(intelligent_core_path))
        sys.path.insert(0, str(generators_root))

        from managers.generation_manager import GenerationManager

        # Create manager
        manager = GenerationManager()
        current_job["manager"] = manager

        # Run generation
        logger.info(f"Job {job_id}: Starting generation for levels {levels}")
        report = await manager.generate_all(levels=levels)

        # Update job status
        generation_jobs[job_id].update({
            "status": report["status"],
            "completed_at": report["completed_at"],
            "duration_seconds": report["duration_seconds"],
            "total_scenarios": report["total_scenarios_generated"],
            "report": report
        })

        logger.info(f"Job {job_id}: Generation completed with status {report['status']}")

    except Exception as e:
        logger.error(f"Job {job_id}: Generation failed: {e}", exc_info=True)
        generation_jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat()
        })


@router.post("/start", response_model=GenerationResponse)
async def start_generation(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start scenario generation for specified levels.

    ## Request Body
    ```json
    {
        "levels": ["l1_platform", "l1_applications"],
        "force_regenerate": false,
        "async_mode": true
    }
    ```

    ## Response
    Returns job ID and status. Use `/progress/{job_id}` to track progress.
    """
    # Check if generation is already running
    if current_job["status"] == "running":
        return GenerationResponse(
            job_id=current_job["job_id"],
            status="already_running",
            message=f"Generation already in progress: {current_job['job_id']}",
            started_at=generation_jobs[current_job["job_id"]]["started_at"]
        )

    # Create new job
    job_id = str(uuid.uuid4())
    started_at = datetime.utcnow().isoformat()

    generation_jobs[job_id] = {
        "job_id": job_id,
        "status": "started",
        "levels": request.levels,
        "force_regenerate": request.force_regenerate,
        "started_at": started_at,
        "completed_at": None,
        "total_scenarios": 0
    }

    current_job["job_id"] = job_id
    current_job["status"] = "running"

    # Start generation in background
    if request.async_mode:
        background_tasks.add_task(run_generation_async, job_id, request.levels)

        return GenerationResponse(
            job_id=job_id,
            status="started",
            message=f"Generation started for levels: {', '.join(request.levels)}",
            started_at=started_at,
            estimated_duration_seconds=60  # Rough estimate
        )
    else:
        # Synchronous mode (for testing)
        await run_generation_async(job_id, request.levels)
        job = generation_jobs[job_id]

        return GenerationResponse(
            job_id=job_id,
            status=job["status"],
            message=f"Generation completed: {job.get('total_scenarios', 0)} scenarios",
            started_at=job["started_at"]
        )


@router.get("/progress/{job_id}", response_model=ProgressResponse)
async def get_progress(job_id: str):
    """
    Get generation progress for a specific job.

    ## Path Parameters
    - `job_id`: Generation job ID from start request

    ## Response
    Returns current progress, status, and statistics.
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = generation_jobs[job_id]

    # Get progress from manager if available
    progress_data = {}
    if current_job.get("manager") and job_id == current_job["job_id"]:
        progress_info = await current_job["manager"].get_progress()
        progress_data = progress_info["progress"]

    # Convert to response format
    from models.requests import LevelProgress
    formatted_progress = {}
    for level, data in progress_data.items():
        formatted_progress[level] = LevelProgress(**data)

    return ProgressResponse(
        job_id=job_id,
        status=job["status"],
        current_level=job.get("current_level"),
        progress=formatted_progress,
        total_scenarios=job.get("total_scenarios", 0),
        started_at=job["started_at"],
        estimated_completion=None  # TODO: Calculate estimate
    )


@router.get("/status")
async def get_status():
    """
    Get current generation status.

    Returns information about currently running job (if any).
    """
    if current_job["status"] == "idle":
        return {
            "status": "idle",
            "message": "No generation currently running"
        }

    job_id = current_job["job_id"]
    job = generation_jobs.get(job_id, {})

    return {
        "status": current_job["status"],
        "job_id": job_id,
        "started_at": job.get("started_at"),
        "levels": job.get("levels", []),
        "total_scenarios": job.get("total_scenarios", 0)
    }


@router.post("/stop")
async def stop_generation():
    """
    Stop currently running generation.

    Note: Stops gracefully after current item completes.
    """
    if current_job["status"] != "running":
        return {
            "status": "not_running",
            "message": "No generation currently running"
        }

    # TODO: Implement graceful stop
    # For now, just mark as stopped
    job_id = current_job["job_id"]
    if job_id and job_id in generation_jobs:
        generation_jobs[job_id]["status"] = "stopped"

    current_job["status"] = "idle"
    current_job["job_id"] = None

    return {
        "status": "stopped",
        "message": "Generation stop requested",
        "job_id": job_id
    }


@router.post("/l1/platform", response_model=GenerationResponse)
async def generate_l1_platform(background_tasks: BackgroundTasks):
    """Generate L1 Platform Service scenarios only."""
    request = GenerationRequest(levels=["l1_platform"])
    return await start_generation(request, background_tasks)


@router.post("/l1/applications", response_model=GenerationResponse)
async def generate_l1_applications(background_tasks: BackgroundTasks):
    """Generate L1 Application scenarios only."""
    request = GenerationRequest(levels=["l1_applications"])
    return await start_generation(request, background_tasks)


@router.post("/l2", response_model=GenerationResponse)
async def generate_l2(background_tasks: BackgroundTasks):
    """Generate L2 Subsystem scenarios only."""
    request = GenerationRequest(levels=["l2"])
    return await start_generation(request, background_tasks)


@router.post("/l3", response_model=GenerationResponse)
async def generate_l3(background_tasks: BackgroundTasks):
    """Generate L3 System scenarios only."""
    request = GenerationRequest(levels=["l3"])
    return await start_generation(request, background_tasks)


@router.post("/l4", response_model=GenerationResponse)
async def generate_l4(background_tasks: BackgroundTasks):
    """Generate L4 Workflow scenarios only (AI-powered)."""
    request = GenerationRequest(levels=["l4"])
    return await start_generation(request, background_tasks)


@router.get("/jobs")
async def list_jobs():
    """List all generation jobs."""
    return {
        "total_jobs": len(generation_jobs),
        "jobs": list(generation_jobs.values())
    }


@router.get("/jobs/{job_id}")
async def get_job_details(job_id: str):
    """Get detailed information about a specific job."""
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return generation_jobs[job_id]
