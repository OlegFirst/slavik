"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class GenerationRequest(BaseModel):
    """Request to start scenario generation."""

    levels: Optional[List[str]] = Field(
        default=["l1_platform", "l1_applications", "l2", "l3", "l4"],
        description="Levels to generate scenarios for"
    )
    force_regenerate: bool = Field(
        default=False,
        description="Force regeneration even if scenarios exist"
    )
    async_mode: bool = Field(
        default=True,
        description="Run generation asynchronously"
    )


class GenerationResponse(BaseModel):
    """Response from generation request."""

    job_id: str = Field(description="Generation job ID")
    status: str = Field(description="Job status: started, running, completed, failed")
    message: str = Field(description="Human-readable status message")
    started_at: Optional[str] = Field(None, description="Job start timestamp")
    estimated_duration_seconds: Optional[int] = Field(None, description="Estimated duration")


class LevelProgress(BaseModel):
    """Progress for a specific level."""

    status: str = Field(description="Status: pending, running, completed, failed, skipped")
    generated: int = Field(default=0, description="Number of scenarios generated")
    total: int = Field(default=0, description="Total scenarios to generate")
    failed: int = Field(default=0, description="Number of failures")


class ProgressResponse(BaseModel):
    """Current generation progress."""

    job_id: str = Field(description="Generation job ID")
    status: str = Field(description="Overall status")
    current_level: Optional[str] = Field(None, description="Currently generating level")
    progress: Dict[str, LevelProgress] = Field(description="Progress by level")
    total_scenarios: int = Field(default=0, description="Total scenarios generated so far")
    started_at: Optional[str] = Field(None, description="Job start timestamp")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")


class StatisticsResponse(BaseModel):
    """Generation statistics."""

    total_scenarios: int = Field(description="Total scenarios in registry")
    by_level: Dict[str, int] = Field(description="Scenarios count by level")
    by_type: Dict[str, int] = Field(description="Scenarios count by type")
    by_category: Dict[str, int] = Field(description="Scenarios count by category")
    last_generation: Optional[Dict[str, Any]] = Field(None, description="Last generation info")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Service status: healthy, degraded, unhealthy")
    version: str = Field(description="Service version")
    uptime_seconds: float = Field(description="Service uptime in seconds")
    components: Dict[str, str] = Field(description="Component health status")
    timestamp: str = Field(description="Check timestamp")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(description="Error timestamp")
