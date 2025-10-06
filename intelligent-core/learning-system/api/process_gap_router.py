"""
Process Gap Analysis API Router

Endpoints for BCM process coverage analysis
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from engines.process_gap_analyzer import ProcessGapAnalyzer, ProcessCoverageMatrix

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize engines
gap_analyzer = ProcessGapAnalyzer()
matrix_generator = ProcessCoverageMatrix(gap_analyzer)


# =====================================================
# Request/Response Models
# =====================================================

class ExerciseResultForGapAnalysis(BaseModel):
    """Exercise result for gap analysis"""
    scenario_type: str
    objectives_met: List[str] = []
    key_issues: List[str] = []
    overall_score: float
    conducted_at: datetime


class ProcessCoverageRequest(BaseModel):
    """Request for process coverage analysis"""
    scenario_type: str
    exercise_results: List[ExerciseResultForGapAnalysis]


class MatrixRequest(BaseModel):
    """Request for coverage matrix"""
    exercise_results: List[ExerciseResultForGapAnalysis]


# =====================================================
# Endpoints
# =====================================================

@router.post("/coverage/analyze")
async def analyze_process_coverage(request: ProcessCoverageRequest):
    """
    Analyze BCM process coverage for a scenario type

    Returns:
    - Step-by-step coverage
    - Success rates
    - Critical gaps
    - Improvement priorities
    """
    try:
        # Convert to dict
        results_dict = [r.dict() for r in request.exercise_results]

        # Analyze coverage
        analysis = gap_analyzer.analyze_process_coverage(
            scenario_type=request.scenario_type,
            exercise_results=results_dict
        )

        return analysis

    except Exception as e:
        logger.error(f"Error analyzing process coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/matrix/generate")
async def generate_coverage_matrix(request: MatrixRequest):
    """
    Generate BCM Process Coverage Matrix

    Process (rows) x Scenario Type (columns) heatmap
    """
    try:
        # Convert to dict
        results_dict = [r.dict() for r in request.exercise_results]

        # Generate matrix
        matrix = matrix_generator.generate_coverage_matrix(
            exercise_results=results_dict
        )

        return matrix

    except Exception as e:
        logger.error(f"Error generating coverage matrix: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes")
async def list_bcm_processes():
    """
    List all standard BCM processes

    With ISO 22301 mappings
    """
    processes = []

    for process_id, process_def in gap_analyzer.standard_processes.items():
        processes.append({
            'process_id': process_id,
            'name': process_def['name'],
            'iso_clause': process_def['iso_clause'],
            'steps': process_def['steps'],
            'total_steps': len(process_def['steps'])
        })

    return {
        'processes': processes,
        'total_processes': len(processes)
    }


@router.get("/processes/{process_id}")
async def get_process_details(process_id: str):
    """Get details for a specific BCM process"""
    process_def = gap_analyzer.standard_processes.get(process_id)

    if not process_def:
        raise HTTPException(
            status_code=404,
            detail=f"Process not found: {process_id}"
        )

    return {
        'process_id': process_id,
        **process_def
    }


@router.get("/gaps/critical")
async def get_critical_gaps(
    tenant_id: str = Query(..., description="Tenant ID"),
    scenario_type: Optional[str] = Query(None, description="Filter by scenario type")
):
    """
    Get critical process gaps for a tenant

    TODO: Fetch from database (learning.process_coverage)
    """
    # Placeholder - implement database fetch
    return {
        "message": "Critical gaps endpoint",
        "tenant_id": tenant_id,
        "scenario_type": scenario_type,
        "note": "Database fetch not yet implemented"
    }


@router.get("/coverage/summary")
async def get_coverage_summary(
    tenant_id: str = Query(..., description="Tenant ID")
):
    """
    Get overall process coverage summary

    Aggregated across all scenario types
    """
    # TODO: Implement database aggregation
    return {
        "message": "Coverage summary endpoint",
        "tenant_id": tenant_id,
        "note": "Implementation pending"
    }


@router.post("/coverage/save")
async def save_process_coverage(
    tenant_id: str,
    process_id: str,
    scenario_type: str,
    coverage_data: dict
):
    """
    Save process coverage analysis to database

    Stores in learning.process_coverage
    """
    try:
        # TODO: Implement database save
        # INSERT INTO learning.process_coverage

        return {
            "message": "Process coverage saved",
            "tenant_id": tenant_id,
            "process_id": process_id,
            "scenario_type": scenario_type,
            "note": "Database save not yet implemented"
        }

    except Exception as e:
        logger.error(f"Error saving process coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/iso-mapping")
async def get_iso_22301_mapping():
    """
    Get mapping of BCM processes to ISO 22301 clauses

    Useful for compliance audits
    """
    mapping = {}

    for process_id, process_def in gap_analyzer.standard_processes.items():
        clause = process_def['iso_clause']

        if clause not in mapping:
            mapping[clause] = []

        mapping[clause].append({
            'process_id': process_id,
            'process_name': process_def['name'],
            'total_steps': len(process_def['steps'])
        })

    return {
        'iso_clause_mapping': mapping,
        'total_clauses': len(mapping)
    }


@router.post("/priorities/generate")
async def generate_improvement_priorities(
    tenant_id: str,
    time_period_days: int = Query(90, description="Analysis period in days")
):
    """
    Generate improvement priorities based on gap analysis

    Returns prioritized action plan
    """
    try:
        # TODO: Fetch exercise results from database
        # Filter by time period
        # Run gap analysis
        # Generate priorities

        return {
            "message": "Improvement priorities generation",
            "tenant_id": tenant_id,
            "time_period_days": time_period_days,
            "note": "Implementation pending"
        }

    except Exception as e:
        logger.error(f"Error generating priorities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
