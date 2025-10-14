"""
Scenario Management API
========================

CRUD operations for BCM scenarios.

Adapted from: /simulation/api/scenario_router.py
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scenarios", tags=["Scenarios"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ScenarioCreate(BaseModel):
    """Create scenario request"""
    tenant_id: Optional[str] = None
    title: str
    category: str
    complexity: int = 3
    scenario_type: str = "tabletop"
    content: Optional[str] = None
    timeline: Optional[dict] = None
    injects: Optional[dict] = None
    success_metrics: Optional[dict] = None


class ScenarioResponse(BaseModel):
    """Scenario response"""
    id: int
    tenant_id: Optional[str]
    title: str
    category: str
    complexity: int
    scenario_type: str
    is_ai_generated: bool
    created_at: datetime


class ScenarioDetail(BaseModel):
    """Full scenario details"""
    id: int
    tenant_id: Optional[str]
    title: str
    category: str
    complexity: int
    scenario_type: str
    content: Optional[str]
    timeline: Optional[dict]
    injects: Optional[dict]
    success_metrics: Optional[dict]
    is_ai_generated: bool
    created_at: datetime


# ============================================================================
# In-Memory Storage
# ============================================================================

scenarios_db: dict = {}
scenario_id_counter = 1


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("", response_model=ScenarioResponse, status_code=201)
def create_scenario(scenario: ScenarioCreate):
    """
    Create new scenario

    Types:
    - tabletop: Discussion-based exercise
    - functional: Department-level exercise
    - full_scale: Organization-wide exercise
    """
    global scenario_id_counter

    scenario_id = scenario_id_counter
    scenario_id_counter += 1

    scenario_data = {
        "id": scenario_id,
        "tenant_id": scenario.tenant_id,
        "title": scenario.title,
        "category": scenario.category,
        "complexity": scenario.complexity,
        "scenario_type": scenario.scenario_type,
        "content": scenario.content,
        "timeline": scenario.timeline,
        "injects": scenario.injects,
        "success_metrics": scenario.success_metrics,
        "is_ai_generated": False,
        "created_at": datetime.now()
    }

    scenarios_db[scenario_id] = scenario_data

    logger.info(f"Created scenario: {scenario_id} ({scenario.title})")

    return ScenarioResponse(**scenario_data)


@router.get("", response_model=List[ScenarioResponse])
def list_scenarios(
    category: Optional[str] = Query(None),
    complexity: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100
):
    """
    List scenarios

    Filters:
    - category: Filter by category (cyber, natural, operational, etc.)
    - complexity: Filter by complexity (1-5)
    """
    scenarios = list(scenarios_db.values())

    # Apply filters
    if category:
        scenarios = [s for s in scenarios if s["category"] == category]

    if complexity:
        scenarios = [s for s in scenarios if s["complexity"] == complexity]

    # Sort by creation date
    scenarios.sort(key=lambda x: x["created_at"], reverse=True)

    # Apply pagination
    scenarios = scenarios[skip:skip + limit]

    return [ScenarioResponse(**s) for s in scenarios]


@router.get("/{scenario_id}", response_model=ScenarioDetail)
def get_scenario(scenario_id: int):
    """Get scenario by ID with full details"""
    scenario = scenarios_db.get(scenario_id)

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return ScenarioDetail(**scenario)


@router.delete("/{scenario_id}", status_code=204)
def delete_scenario(scenario_id: int):
    """Delete scenario"""
    scenario = scenarios_db.get(scenario_id)

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    del scenarios_db[scenario_id]

    logger.info(f"Deleted scenario: {scenario_id}")

    return None


@router.get("/categories", deprecated=True)
def list_categories():
    """
    List scenario categories

    DEPRECATED: Use standard categorization
    """
    return {
        "categories": [
            "cyber",
            "natural_disaster",
            "pandemic",
            "supply_chain",
            "infrastructure",
            "terrorism",
            "data_breach",
            "operational"
        ]
    }
