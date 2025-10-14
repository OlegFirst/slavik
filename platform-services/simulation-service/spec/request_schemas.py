"""
Request Schemas

Pydantic models for API request validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from enum import Enum


class SimulationType(str, Enum):
    """Simulation type enumeration"""
    WHAT_IF = "what_if"
    MONTE_CARLO = "monte_carlo"
    SCENARIO = "scenario"
    BIA = "bia"
    JAAMSIM = "jaamsim"


class ScenarioCategory(str, Enum):
    """Scenario category enumeration"""
    CYBER = "cyber"
    PANDEMIC = "pandemic"
    DISASTER = "disaster"
    SUPPLY_CHAIN = "supply_chain"
    DATA_BREACH = "data_breach"
    POWER_OUTAGE = "power_outage"


class SimulationCreateRequest(BaseModel):
    """Request schema for creating a simulation"""

    name: str = Field(..., min_length=1, max_length=255, description="Simulation name")
    description: Optional[str] = Field(None, max_length=2000, description="Simulation description")
    simulation_type: SimulationType = Field(..., description="Type of simulation")
    parameters: Dict[str, Any] = Field(..., description="Simulation parameters")
    tags: Optional[List[str]] = Field(default=[], description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "IT System Failure Analysis",
                "description": "Monte Carlo analysis of IT recovery times",
                "simulation_type": "monte_carlo",
                "parameters": {
                    "iterations": 1000,
                    "variables": {
                        "recovery_time": {"distribution": "normal", "mean": 4, "std": 1}
                    }
                },
                "tags": ["IT", "recovery", "analysis"]
            }
        }


class SimulationExecuteRequest(BaseModel):
    """Request schema for executing a simulation"""

    parameters_override: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Override simulation parameters for this execution"
    )
    async_execution: bool = Field(
        default=False,
        description="Execute asynchronously (return immediately)"
    )
    save_results: bool = Field(
        default=True,
        description="Save execution results to database"
    )
    execution_metadata: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional metadata for this execution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "parameters_override": {
                    "iterations": 5000
                },
                "async_execution": True,
                "save_results": True
            }
        }


class ScenarioCreateRequest(BaseModel):
    """Request schema for creating a BCM scenario"""

    title: str = Field(..., min_length=1, max_length=255, description="Scenario title")
    description: Optional[str] = Field(None, max_length=5000, description="Scenario description")
    category: ScenarioCategory = Field(..., description="Scenario category")
    complexity: int = Field(..., ge=1, le=5, description="Complexity level (1-5)")
    scenario_type: Optional[str] = Field(None, description="Scenario type (tabletop, functional, etc.)")
    content: Optional[str] = Field(None, description="Scenario content/narrative")
    timeline: Optional[Dict[str, Any]] = Field(default={}, description="Scenario timeline")
    injects: Optional[List[Dict[str, Any]]] = Field(default=[], description="Scenario injects")
    success_metrics: Optional[Dict[str, Any]] = Field(default={}, description="Success metrics")
    participant_roles: Optional[List[str]] = Field(default=[], description="Required participant roles")
    recommended_participants_count: Optional[int] = Field(None, ge=1, description="Recommended number of participants")
    industry: Optional[str] = Field(None, description="Target industry")
    organization_size: Optional[str] = Field(None, description="Organization size")
    tags: Optional[List[str]] = Field(default=[], description="Tags")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Ransomware Attack on Healthcare Facility",
                "description": "Simulation of ransomware attack affecting patient systems",
                "category": "cyber",
                "complexity": 4,
                "scenario_type": "tabletop",
                "industry": "healthcare",
                "organization_size": "medium",
                "tags": ["ransomware", "healthcare", "patient_safety"]
            }
        }


class ScenarioGenerateRequest(BaseModel):
    """Request schema for AI-generated scenarios"""

    category: ScenarioCategory = Field(..., description="Scenario category")
    complexity: int = Field(..., ge=1, le=5, description="Complexity level (1-5)")
    industry: Optional[str] = Field(None, description="Target industry")
    organization_size: Optional[str] = Field(None, description="Organization size (small/medium/large)")
    custom_requirements: Optional[str] = Field(None, max_length=2000, description="Custom requirements")
    include_timeline: bool = Field(default=True, description="Generate timeline")
    include_injects: bool = Field(default=True, description="Generate injects")
    participant_count: Optional[int] = Field(None, ge=1, le=100, description="Number of participants")

    @field_validator("organization_size")
    def validate_org_size(cls, v):
        """Validate organization size"""
        if v and v not in ["small", "medium", "large", "enterprise"]:
            raise ValueError("Organization size must be: small, medium, large, or enterprise")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "category": "pandemic",
                "complexity": 3,
                "industry": "healthcare",
                "organization_size": "large",
                "custom_requirements": "Focus on patient care continuity",
                "include_timeline": True,
                "include_injects": True,
                "participant_count": 15
            }
        }


class LibrarySearchRequest(BaseModel):
    """Request schema for library search"""

    query: Optional[str] = Field(None, description="Search query")
    category: Optional[ScenarioCategory] = Field(None, description="Filter by category")
    complexity: Optional[int] = Field(None, ge=1, le=5, description="Filter by complexity")
    industry: Optional[str] = Field(None, description="Filter by industry")
    tags: Optional[List[str]] = Field(default=[], description="Filter by tags")
    include_public: bool = Field(default=True, description="Include public scenarios")
    include_tenant: bool = Field(default=True, description="Include tenant scenarios")
    limit: int = Field(default=50, ge=1, le=200, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "ransomware",
                "category": "cyber",
                "complexity": 3,
                "industry": "healthcare",
                "limit": 20
            }
        }


class BulkSimulationRequest(BaseModel):
    """Request schema for bulk simulation creation"""

    simulations: List[SimulationCreateRequest] = Field(..., min_length=1, max_length=100)
    execute_immediately: bool = Field(default=False, description="Execute all simulations immediately")

    @field_validator("simulations")
    def validate_simulations(cls, v):
        """Ensure at least one simulation"""
        if not v:
            raise ValueError("At least one simulation required")
        return v
