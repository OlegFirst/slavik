"""
Scenario Library Router

Access to pre-built BCM scenarios
"""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Add shared scenario library to path
shared_path = Path(__file__).parent.parent.parent / "shared" / "scenario-library"
sys.path.insert(0, str(shared_path))

from scenarios import (
    get_scenario,
    list_scenarios,
    get_scenario_summary,
    ThreatType,
    ComplexityLevel,
    SCENARIO_LIBRARY
)

router = APIRouter()


# Pydantic schemas
class ScenarioSummary(BaseModel):
    """Scenario summary"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    threat_type: str
    complexity: str
    duration_hours: int
    description: str
    inject_count: int
    learning_objectives: List[str]


class ScenarioDetail(BaseModel):
    """Full scenario details"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    threat_type: str
    complexity: str
    duration_hours: int
    description: str
    initial_situation: str
    timeline: List[dict]
    injects: List[dict]
    success_criteria: List[str]
    learning_objectives: List[str]
    debrief_questions: List[str]


@router.get("/library", response_model=List[ScenarioSummary])
async def list_scenario_library(
    threat_type: Optional[ThreatType] = None,
    complexity: Optional[ComplexityLevel] = None
):
    """
    List all scenarios in library

    Filters:
    - threat_type: cyber/natural_disaster/pandemic/supply_chain/infrastructure/etc
    - complexity: Beginner/Intermediate/Advanced/Expert
    """
    scenarios = list_scenarios(threat_type=threat_type, complexity=complexity)

    return [
        ScenarioSummary(
            id=s["id"],
            name=s["name"],
            threat_type=s["threat_type"],
            complexity=s["complexity"],
            duration_hours=s["duration_hours"],
            description=s["description"],
            inject_count=len(s.get("injects", [])),
            learning_objectives=s.get("learning_objectives", [])
        )
        for s in scenarios
    ]


@router.get("/library/{scenario_id}", response_model=ScenarioDetail)
async def get_scenario_details(scenario_id: str):
    """
    Get full scenario details

    Returns complete scenario including:
    - Initial situation
    - Timeline
    - Injects
    - Success criteria
    - Learning objectives
    - Debrief questions
    """
    scenario = get_scenario(scenario_id)

    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    return ScenarioDetail(
        id=scenario["id"],
        name=scenario["name"],
        threat_type=scenario["threat_type"],
        complexity=scenario["complexity"],
        duration_hours=scenario["duration_hours"],
        description=scenario["description"],
        initial_situation=scenario["initial_situation"],
        timeline=scenario.get("timeline", []),
        injects=scenario.get("injects", []),
        success_criteria=scenario.get("success_criteria", []),
        learning_objectives=scenario.get("learning_objectives", []),
        debrief_questions=scenario.get("debrief_questions", [])
    )


@router.get("/library/threat-types")
async def list_threat_types():
    """List all available threat types"""
    return {
        "threat_types": [t.value for t in ThreatType]
    }


@router.get("/library/complexity-levels")
async def list_complexity_levels():
    """List all complexity levels"""
    return {
        "complexity_levels": [c.value for c in ComplexityLevel]
    }


@router.get("/library/stats")
async def library_stats():
    """Get scenario library statistics"""
    all_scenarios = list(SCENARIO_LIBRARY.values())

    # Count by threat type
    threat_counts = {}
    for scenario in all_scenarios:
        threat = scenario["threat_type"]
        threat_counts[threat] = threat_counts.get(threat, 0) + 1

    # Count by complexity
    complexity_counts = {}
    for scenario in all_scenarios:
        complexity = scenario["complexity"]
        complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1

    return {
        "total_scenarios": len(all_scenarios),
        "by_threat_type": threat_counts,
        "by_complexity": complexity_counts,
        "avg_duration_hours": sum(s["duration_hours"] for s in all_scenarios) / len(all_scenarios) if all_scenarios else 0,
        "total_injects": sum(len(s.get("injects", [])) for s in all_scenarios)
    }
