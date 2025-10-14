"""
Scenario Library Router
========================

Access to pre-built BCM scenarios from the shared library.

Adapted from: /simulation/api/scenario_library_router.py
"""

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/library", tags=["Scenario Library"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ScenarioSummary(BaseModel):
    """Scenario summary"""
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


# ============================================================================
# Mock Scenario Library
# ============================================================================

MOCK_SCENARIOS = {
    "cyber_ransomware_001": {
        "id": "cyber_ransomware_001",
        "name": "Ransomware Attack Response",
        "threat_type": "cyber",
        "complexity": "Advanced",
        "duration_hours": 4,
        "description": "Comprehensive ransomware incident response scenario",
        "initial_situation": "IT department detects encryption of critical files",
        "timeline": [
            {"hour": 0, "event": "Initial detection"},
            {"hour": 1, "event": "Containment measures"},
            {"hour": 2, "event": "Recovery initiation"},
            {"hour": 3, "event": "Communications"},
            {"hour": 4, "event": "Debrief"}
        ],
        "injects": [
            {
                "id": "inject_001",
                "time_minutes": 15,
                "type": "email",
                "content": "Ransom note discovered"
            },
            {
                "id": "inject_002",
                "time_minutes": 45,
                "type": "phone",
                "content": "Media inquiry received"
            }
        ],
        "success_criteria": [
            "Contain threat within 1 hour",
            "Activate backup systems",
            "Notify stakeholders within 2 hours"
        ],
        "learning_objectives": [
            "Practice incident response procedures",
            "Test communication protocols",
            "Evaluate backup/recovery capabilities"
        ],
        "debrief_questions": [
            "Were containment procedures effective?",
            "Was communication timely and clear?",
            "Are improvements needed?"
        ]
    },
    "natural_earthquake_001": {
        "id": "natural_earthquake_001",
        "name": "Earthquake Response",
        "threat_type": "natural_disaster",
        "complexity": "Intermediate",
        "duration_hours": 6,
        "description": "Major earthquake response and recovery scenario",
        "initial_situation": "7.5 magnitude earthquake strikes region",
        "timeline": [
            {"hour": 0, "event": "Earthquake occurs"},
            {"hour": 1, "event": "Damage assessment"},
            {"hour": 2, "event": "Emergency response"},
            {"hour": 4, "event": "Recovery planning"},
            {"hour": 6, "event": "Status review"}
        ],
        "injects": [
            {
                "id": "inject_001",
                "time_minutes": 10,
                "type": "alert",
                "content": "Building structural damage reported"
            },
            {
                "id": "inject_002",
                "time_minutes": 30,
                "type": "communication",
                "content": "Emergency services contact"
            }
        ],
        "success_criteria": [
            "Evacuate safely",
            "Account for all personnel",
            "Establish alternate operations"
        ],
        "learning_objectives": [
            "Test emergency evacuation",
            "Assess facility damage procedures",
            "Evaluate relocation capabilities"
        ],
        "debrief_questions": [
            "Was evacuation orderly?",
            "Were alternate sites viable?",
            "What gaps exist?"
        ]
    },
    "supply_disruption_001": {
        "id": "supply_disruption_001",
        "name": "Supply Chain Disruption",
        "threat_type": "supply_chain",
        "complexity": "Intermediate",
        "duration_hours": 3,
        "description": "Major supplier failure scenario",
        "initial_situation": "Critical supplier declares bankruptcy",
        "timeline": [
            {"hour": 0, "event": "Notification received"},
            {"hour": 1, "event": "Impact assessment"},
            {"hour": 2, "event": "Alternative sourcing"},
            {"hour": 3, "event": "Recovery plan"}
        ],
        "injects": [
            {
                "id": "inject_001",
                "time_minutes": 20,
                "type": "email",
                "content": "Inventory depletion warning"
            }
        ],
        "success_criteria": [
            "Identify alternative suppliers",
            "Maintain production",
            "Communicate with customers"
        ],
        "learning_objectives": [
            "Test supplier contingency plans",
            "Evaluate inventory buffers",
            "Practice stakeholder communication"
        ],
        "debrief_questions": [
            "Were alternatives identified quickly?",
            "Was production maintained?",
            "Are improvements needed?"
        ]
    }
}


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("", response_model=List[ScenarioSummary])
async def list_scenario_library(
    threat_type: Optional[str] = Query(None),
    complexity: Optional[str] = Query(None)
):
    """
    List all scenarios in library

    Filters:
    - threat_type: cyber, natural_disaster, pandemic, supply_chain, etc.
    - complexity: Beginner, Intermediate, Advanced, Expert
    """
    scenarios = list(MOCK_SCENARIOS.values())

    # Apply filters
    if threat_type:
        scenarios = [s for s in scenarios if s["threat_type"] == threat_type]

    if complexity:
        scenarios = [s for s in scenarios if s["complexity"] == complexity]

    # Convert to summaries
    summaries = []
    for s in scenarios:
        summaries.append(ScenarioSummary(
            id=s["id"],
            name=s["name"],
            threat_type=s["threat_type"],
            complexity=s["complexity"],
            duration_hours=s["duration_hours"],
            description=s["description"],
            inject_count=len(s.get("injects", [])),
            learning_objectives=s.get("learning_objectives", [])
        ))

    return summaries


@router.get("/{scenario_id}", response_model=ScenarioDetail)
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
    scenario = MOCK_SCENARIOS.get(scenario_id)

    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    return ScenarioDetail(**scenario)


@router.get("/threat-types")
async def list_threat_types():
    """List all available threat types"""
    return {
        "threat_types": [
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


@router.get("/complexity-levels")
async def list_complexity_levels():
    """List all complexity levels"""
    return {
        "complexity_levels": [
            "Beginner",
            "Intermediate",
            "Advanced",
            "Expert"
        ]
    }


@router.get("/stats")
async def library_stats():
    """Get scenario library statistics"""
    all_scenarios = list(MOCK_SCENARIOS.values())

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

    # Calculate averages
    total_duration = sum(s["duration_hours"] for s in all_scenarios)
    total_injects = sum(len(s.get("injects", [])) for s in all_scenarios)

    return {
        "total_scenarios": len(all_scenarios),
        "by_threat_type": threat_counts,
        "by_complexity": complexity_counts,
        "avg_duration_hours": total_duration / len(all_scenarios) if all_scenarios else 0,
        "total_injects": total_injects
    }
