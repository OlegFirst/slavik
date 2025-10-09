"""
Scenario Management API
"""

import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from database.base import get_db

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.simulation_model import Scenario

router = APIRouter()

# Pydantic schemas
class ScenarioCreate(BaseModel):
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
    id: int
    tenant_id: Optional[str]
    title: str
    category: str
    complexity: int
    scenario_type: str
    is_ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/scenarios", response_model=ScenarioResponse, status_code=201)
def create_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(get_db)
):
    """Create new scenario"""

    db_scenario = Scenario(
        tenant_id=scenario.tenant_id,
        title=scenario.title,
        category=scenario.category,
        complexity=scenario.complexity,
        scenario_type=scenario.scenario_type,
        content=scenario.content,
        timeline=scenario.timeline,
        injects=scenario.injects,
        success_metrics=scenario.success_metrics,
        is_ai_generated=False
    )

    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)

    return db_scenario


@router.get("/scenarios", response_model=List[ScenarioResponse])
def list_scenarios(
    category: Optional[str] = Query(None),
    complexity: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List scenarios"""

    query = db.query(Scenario)

    if category:
        query = query.filter(Scenario.category == category)

    if complexity:
        query = query.filter(Scenario.complexity == complexity)

    scenarios = query.order_by(Scenario.created_at.desc()).offset(skip).limit(limit).all()

    return scenarios


@router.get("/scenarios/{scenario_id}")
def get_scenario(
    scenario_id: int,
    db: Session = Depends(get_db)
):
    """Get scenario by ID"""

    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return {
        "id": scenario.id,
        "tenant_id": scenario.tenant_id,
        "title": scenario.title,
        "category": scenario.category,
        "complexity": scenario.complexity,
        "scenario_type": scenario.scenario_type,
        "content": scenario.content,
        "timeline": scenario.timeline,
        "injects": scenario.injects,
        "success_metrics": scenario.success_metrics,
        "is_ai_generated": scenario.is_ai_generated,
        "created_at": scenario.created_at
    }


@router.delete("/scenarios/{scenario_id}", status_code=204)
def delete_scenario(
    scenario_id: int,
    db: Session = Depends(get_db)
):
    """Delete scenario"""

    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    db.delete(scenario)
    db.commit()

    return None
