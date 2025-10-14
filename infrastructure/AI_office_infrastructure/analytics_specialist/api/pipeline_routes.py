"""
Pipeline API Routes
==================

API endpoints for triggering and monitoring the Automated Knowledge Pipeline.

Integrates with:
- analytics-specialist FastAPI app
- mio-manager (for scheduled automation)
- monitoring service (for metrics)
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import asyncio
import json

from ..workflows.automated_knowledge_pipeline import AutomatedKnowledgePipeline

# Create router
router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])


# === Request/Response Models ===

class PipelineTriggerRequest(BaseModel):
    """Request to trigger pipeline"""
    mode: str = Field(
        default="full",
        description="Pipeline mode: full, analyze, docs, index"
    )
    output_dir: Optional[str] = Field(
        None,
        description="Custom output directory"
    )
    async_execution: bool = Field(
        default=True,
        description="Run in background"
    )


class PipelineStatusResponse(BaseModel):
    """Pipeline status response"""
    run_id: str
    status: str  # "running", "completed", "failed"
    mode: str
    started_at: str
    completed_at: Optional[str]
    duration_seconds: Optional[float]
    stages_completed: List[str]
    errors: List[str]
    outputs: Dict[str, Any]


class PipelineListResponse(BaseModel):
    """List of pipeline runs"""
    total: int
    runs: List[PipelineStatusResponse]


# === Global state for tracking runs ===
active_runs: Dict[str, Dict[str, Any]] = {}


# === API Endpoints ===

@router.post("/trigger", response_model=Dict[str, str])
async def trigger_pipeline(
    request: PipelineTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger the Automated Knowledge Pipeline

    **Modes:**
    - `full`: Complete pipeline (all stages)
    - `analyze`: System analysis + pattern extraction
    - `docs`: Documentation generation only
    - `index`: RAG indexing only

    **Example:**
    ```bash
    curl -X POST http://localhost:8007/api/v1/pipeline/trigger \
      -H "Content-Type: application/json" \
      -d '{"mode": "full", "async_execution": true}'
    ```
    """

    # Validate mode
    valid_modes = ["full", "analyze", "docs", "index"]
    if request.mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Must be one of: {valid_modes}"
        )

    # Generate run ID
    run_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Initialize pipeline
    output_dir = Path(request.output_dir) if request.output_dir else None
    pipeline = AutomatedKnowledgePipeline(output_dir=output_dir)

    if request.async_execution:
        # Run in background
        background_tasks.add_task(
            _run_pipeline_background,
            run_id,
            pipeline,
            request.mode
        )

        active_runs[run_id] = {
            "status": "running",
            "mode": request.mode,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "errors": []
        }

        return {
            "run_id": run_id,
            "status": "running",
            "message": f"Pipeline '{request.mode}' started in background",
            "poll_url": f"/api/v1/pipeline/status/{run_id}"
        }

    else:
        # Run synchronously (blocking)
        try:
            await _execute_pipeline(pipeline, request.mode)

            return {
                "run_id": run_id,
                "status": "completed",
                "message": f"Pipeline '{request.mode}' completed successfully"
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline execution failed: {str(e)}"
            )


@router.get("/status/{run_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(run_id: str):
    """
    Get status of a specific pipeline run

    **Example:**
    ```bash
    curl http://localhost:8007/api/v1/pipeline/status/pipeline_20251009_120000
    ```
    """

    # Check active runs
    if run_id in active_runs:
        run_data = active_runs[run_id]
        return PipelineStatusResponse(
            run_id=run_id,
            **run_data
        )

    # Check completed runs (from report files)
    reports_dir = Path("infrastructure/AI-office-infrastructure/analytics-specialist/reports")
    report_file = reports_dir / f"{run_id}.json"

    if report_file.exists():
        with open(report_file) as f:
            report = json.load(f)

        return PipelineStatusResponse(
            run_id=run_id,
            status="completed" if report["pipeline_run"]["success"] else "failed",
            mode="full",  # TODO: extract from report
            started_at=report["pipeline_run"]["started_at"],
            completed_at=report["pipeline_run"]["completed_at"],
            duration_seconds=report["pipeline_run"]["duration_seconds"],
            stages_completed=report.get("stages", {}).get("completed", []),
            errors=report.get("errors", []),
            outputs=report.get("outputs", {})
        )

    # Not found
    raise HTTPException(
        status_code=404,
        detail=f"Pipeline run '{run_id}' not found"
    )


@router.get("/list", response_model=PipelineListResponse)
async def list_pipeline_runs(
    limit: int = 20,
    status: Optional[str] = None
):
    """
    List recent pipeline runs

    **Query Parameters:**
    - `limit`: Max number of runs to return (default: 20)
    - `status`: Filter by status: running, completed, failed

    **Example:**
    ```bash
    curl "http://localhost:8007/api/v1/pipeline/list?limit=10&status=completed"
    ```
    """

    runs = []

    # Get active runs
    for run_id, run_data in active_runs.items():
        if status and run_data["status"] != status:
            continue

        runs.append(PipelineStatusResponse(
            run_id=run_id,
            stages_completed=[],
            outputs={},
            **run_data
        ))

    # Get completed runs from report files
    reports_dir = Path("infrastructure/AI-office-infrastructure/analytics-specialist/reports")
    if reports_dir.exists():
        for report_file in sorted(reports_dir.glob("pipeline_report_*.json"), reverse=True):
            if len(runs) >= limit:
                break

            run_id = report_file.stem.replace("pipeline_report_", "pipeline_")

            with open(report_file) as f:
                report = json.load(f)

            run_status = "completed" if report["pipeline_run"]["success"] else "failed"

            if status and run_status != status:
                continue

            runs.append(PipelineStatusResponse(
                run_id=run_id,
                status=run_status,
                mode="full",
                started_at=report["pipeline_run"]["started_at"],
                completed_at=report["pipeline_run"]["completed_at"],
                duration_seconds=report["pipeline_run"]["duration_seconds"],
                stages_completed=report.get("stages_completed", []),
                errors=report.get("errors", []),
                outputs=report.get("outputs", {})
            ))

    return PipelineListResponse(
        total=len(runs),
        runs=runs[:limit]
    )


@router.get("/latest", response_model=PipelineStatusResponse)
async def get_latest_run():
    """
    Get the most recent pipeline run

    **Example:**
    ```bash
    curl http://localhost:8007/api/v1/pipeline/latest
    ```
    """

    # Check active runs first
    if active_runs:
        latest_run_id = max(active_runs.keys())
        return await get_pipeline_status(latest_run_id)

    # Check completed runs
    reports_dir = Path("infrastructure/AI-office-infrastructure/analytics-specialist/reports")
    if reports_dir.exists():
        report_files = sorted(reports_dir.glob("pipeline_report_*.json"), reverse=True)

        if report_files:
            latest_report = report_files[0]
            run_id = latest_report.stem.replace("pipeline_report_", "pipeline_")
            return await get_pipeline_status(run_id)

    # No runs found
    raise HTTPException(
        status_code=404,
        detail="No pipeline runs found"
    )


@router.delete("/cancel/{run_id}")
async def cancel_pipeline_run(run_id: str):
    """
    Cancel a running pipeline

    **Example:**
    ```bash
    curl -X DELETE http://localhost:8007/api/v1/pipeline/cancel/pipeline_20251009_120000
    ```
    """

    if run_id not in active_runs:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline run '{run_id}' not found or already completed"
        )

    if active_runs[run_id]["status"] != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline run '{run_id}' is not running (status: {active_runs[run_id]['status']})"
        )

    # Mark as cancelled
    active_runs[run_id]["status"] = "cancelled"
    active_runs[run_id]["completed_at"] = datetime.now().isoformat()

    return {
        "run_id": run_id,
        "status": "cancelled",
        "message": "Pipeline run cancelled successfully"
    }


@router.get("/config")
async def get_pipeline_config():
    """
    Get current pipeline configuration

    **Example:**
    ```bash
    curl http://localhost:8007/api/v1/pipeline/config
    ```
    """

    config_file = Path("infrastructure/AI-office-infrastructure/analytics-specialist/config/pipeline_config.yaml")

    if not config_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Pipeline configuration not found"
        )

    # Read YAML config
    import yaml
    with open(config_file) as f:
        config = yaml.safe_load(f)

    return config


@router.get("/health")
async def pipeline_health_check():
    """
    Health check for pipeline service

    **Example:**
    ```bash
    curl http://localhost:8007/api/v1/pipeline/health
    ```
    """

    # Check if pipeline module can be imported
    try:
        from ..workflows.automated_knowledge_pipeline import AutomatedKnowledgePipeline
        pipeline_available = True
    except Exception as e:
        pipeline_available = False

    # Check if required directories exist
    reports_dir = Path("infrastructure/AI-office-infrastructure/analytics-specialist/reports")
    reports_dir_exists = reports_dir.exists()

    # Check if System Behavior Analyzer is available
    try:
        from ..tools.system_behavior_analyzer import SystemBehaviorAnalyzer
        analyzer_available = True
    except Exception as e:
        analyzer_available = False

    status = "healthy" if (pipeline_available and reports_dir_exists and analyzer_available) else "degraded"

    return {
        "status": status,
        "components": {
            "pipeline": "ok" if pipeline_available else "error",
            "reports_dir": "ok" if reports_dir_exists else "error",
            "analyzer": "ok" if analyzer_available else "error"
        },
        "active_runs": len(active_runs),
        "timestamp": datetime.now().isoformat()
    }


# === Background execution helpers ===

async def _run_pipeline_background(run_id: str, pipeline: AutomatedKnowledgePipeline, mode: str):
    """Run pipeline in background task"""
    try:
        await _execute_pipeline(pipeline, mode)

        # Update status
        active_runs[run_id]["status"] = "completed"
        active_runs[run_id]["completed_at"] = datetime.now().isoformat()

    except Exception as e:
        # Update status on failure
        active_runs[run_id]["status"] = "failed"
        active_runs[run_id]["completed_at"] = datetime.now().isoformat()
        active_runs[run_id]["errors"].append(str(e))


async def _execute_pipeline(pipeline: AutomatedKnowledgePipeline, mode: str):
    """Execute pipeline based on mode"""
    if mode == "full":
        await pipeline.run_full_pipeline()
    elif mode == "analyze":
        await pipeline._stage_system_analysis()
        await pipeline._stage_pattern_extraction()
    elif mode == "docs":
        await pipeline._stage_documentation_generation()
    elif mode == "index":
        await pipeline._stage_rag_integration()
    else:
        raise ValueError(f"Invalid mode: {mode}")
