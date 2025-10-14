"""
Response Schemas

Pydantic models for API response serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SimulationStatus(str, Enum):
    """Simulation status enumeration"""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionStatus(str, Enum):
    """Execution status enumeration"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HealthResponse(BaseModel):
    """Response schema for health check"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    engines: List[str] = Field(..., description="Available simulation engines")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    dependencies: Optional[Dict[str, str]] = Field(default={}, description="Dependency status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "engines": ["JaamSim", "MonteCarlo", "Scenario", "WhatIf", "BIA"],
                "uptime_seconds": 3600,
                "dependencies": {
                    "database": "connected",
                    "redis": "connected",
                    "eventbus": "connected"
                }
            }
        }


class SimulationResponse(BaseModel):
    """Response schema for simulation"""

    id: int = Field(..., description="Simulation ID")
    tenant_id: str = Field(..., description="Tenant ID")
    name: str = Field(..., description="Simulation name")
    description: Optional[str] = Field(None, description="Description")
    simulation_type: str = Field(..., description="Simulation type")
    engine: Optional[str] = Field(None, description="Engine used")
    status: SimulationStatus = Field(..., description="Current status")
    parameters: Dict[str, Any] = Field(..., description="Simulation parameters")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadata")
    tags: Optional[List[str]] = Field(default=[], description="Tags")
    created_by: Optional[str] = Field(None, description="Creator")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "tenant_id": "org-456",
                "name": "IT Recovery Analysis",
                "simulation_type": "monte_carlo",
                "status": "completed",
                "parameters": {"iterations": 1000},
                "created_at": "2025-10-14T12:00:00Z",
                "updated_at": "2025-10-14T12:05:00Z"
            }
        }


class ScenarioResponse(BaseModel):
    """Response schema for BCM scenario"""

    id: int = Field(..., description="Scenario ID")
    tenant_id: Optional[str] = Field(None, description="Tenant ID (null for public)")
    title: str = Field(..., description="Scenario title")
    description: Optional[str] = Field(None, description="Description")
    category: str = Field(..., description="Scenario category")
    complexity: int = Field(..., description="Complexity level (1-5)")
    scenario_type: Optional[str] = Field(None, description="Scenario type")
    content: Optional[str] = Field(None, description="Scenario content")
    timeline: Optional[Dict[str, Any]] = Field(default={}, description="Timeline")
    injects: Optional[List[Dict[str, Any]]] = Field(default=[], description="Injects")
    success_metrics: Optional[Dict[str, Any]] = Field(default={}, description="Success metrics")
    participant_roles: Optional[List[str]] = Field(default=[], description="Participant roles")
    recommended_participants_count: Optional[int] = Field(None, description="Recommended participants")
    is_ai_generated: bool = Field(..., description="AI generated flag")
    ai_generation_params: Optional[Dict[str, Any]] = Field(None, description="AI generation parameters")
    ai_confidence_score: Optional[float] = Field(None, description="AI confidence score")
    tags: Optional[List[str]] = Field(default=[], description="Tags")
    industry: Optional[str] = Field(None, description="Industry")
    organization_size: Optional[str] = Field(None, description="Organization size")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    """Response schema for simulation execution"""

    id: int = Field(..., description="Execution ID")
    simulation_id: int = Field(..., description="Simulation ID")
    execution_number: Optional[int] = Field(None, description="Execution number")
    run_id: Optional[str] = Field(None, description="Run identifier")
    status: ExecutionStatus = Field(..., description="Execution status")
    progress: float = Field(..., description="Progress percentage (0-100)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Execution parameters")
    results: Optional[Dict[str, Any]] = Field(None, description="Execution results")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Execution metrics")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    duration_seconds: Optional[float] = Field(None, description="Duration in seconds")
    executed_by: Optional[str] = Field(None, description="Executor")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadata")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class ResultResponse(BaseModel):
    """Response schema for simulation result"""

    id: int = Field(..., description="Result ID")
    simulation_id: int = Field(..., description="Simulation ID")
    execution_id: Optional[int] = Field(None, description="Execution ID")
    result_type: str = Field(..., description="Result type")
    metric_name: Optional[str] = Field(None, description="Metric name")
    result_data: Dict[str, Any] = Field(..., description="Result data")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    quality_score: Optional[float] = Field(None, description="Quality score")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadata")
    recorded_at: datetime = Field(..., description="Recording timestamp")

    class Config:
        from_attributes = True


class EngineInfoResponse(BaseModel):
    """Response schema for engine information"""

    name: str = Field(..., description="Engine name")
    type: str = Field(..., description="Engine type")
    description: str = Field(..., description="Engine description")
    status: str = Field(..., description="Engine status")
    capabilities: List[str] = Field(..., description="Engine capabilities")
    supported_simulation_types: List[str] = Field(..., description="Supported simulation types")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "MonteCarloEngine",
                "type": "probabilistic",
                "description": "Monte Carlo simulation for risk analysis",
                "status": "available",
                "capabilities": ["probabilistic_modeling", "risk_analysis"],
                "supported_simulation_types": ["monte_carlo"]
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for errors"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid simulation parameters",
                "details": {"field": "iterations", "issue": "must be >= 100"},
                "timestamp": "2025-10-14T12:00:00Z"
            }
        }


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""

    items: List[Any] = Field(..., description="Result items")
    total: int = Field(..., description="Total count")
    limit: int = Field(..., description="Limit per page")
    offset: int = Field(..., description="Offset")
    has_more: bool = Field(..., description="Has more results")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 150,
                "limit": 50,
                "offset": 0,
                "has_more": True
            }
        }
