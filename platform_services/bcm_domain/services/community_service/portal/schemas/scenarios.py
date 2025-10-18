"""
Scenario Marketplace - Pydantic Schemas
Request/Response models for scenarios
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Scenario Schemas
# ============================================================================

class ScenarioResponse(BaseModel):
    """Response schema for scenario details"""

    id: int
    scenario_code: str
    scenario_name: str
    description: str

    # Type & Category
    scenario_type: str
    industry: Optional[str]
    threat_type: Optional[str]

    # Content
    full_scenario: str
    injects: List[dict]
    learning_objectives: List[str]
    duration_minutes: int

    # ISO Mapping
    iso_clauses: List[str]

    # Publishing
    published: bool
    published_at: Optional[datetime]

    # Authorship
    created_by: str
    author_type: str

    # Engagement
    view_count: int
    deployment_count: int
    average_rating: float
    review_count: int

    # Metadata
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScenarioListItem(BaseModel):
    """Simplified scenario for list views"""

    id: int
    scenario_code: str
    scenario_name: str
    description: str
    scenario_type: str
    industry: Optional[str]
    threat_type: Optional[str]
    duration_minutes: int
    average_rating: float
    review_count: int
    deployment_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ScenarioListResponse(BaseModel):
    """Paginated list of scenarios"""

    scenarios: List[ScenarioListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Deployment Schemas
# ============================================================================

class ScenarioDeployRequest(BaseModel):
    """Request schema for deploying a scenario"""

    tenant_id: str = Field(..., description="Target tenant ID for deployment")
    exercise_name_override: Optional[str] = Field(None, description="Override exercise name")


class ScenarioDeployResponse(BaseModel):
    """Response schema for scenario deployment"""

    scenario_id: int
    exercise_id: int
    exercise_code: str
    exercise_name: str
    message: str = "Scenario deployed successfully as exercise"


# ============================================================================
# Review Schemas
# ============================================================================

class ScenarioReviewCreate(BaseModel):
    """Request schema for creating a scenario review"""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, description="Review text")
    exercise_id: Optional[int] = Field(None, description="Exercise where scenario was used")


class ScenarioReviewResponse(BaseModel):
    """Response schema for scenario review"""

    id: int
    scenario_id: int
    user_id: str
    tenant_id: str
    rating: int
    review_text: Optional[str]
    exercise_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
