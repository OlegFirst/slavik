"""
Deployment Models - Data models for deployment orchestration
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class DeploymentPlan(BaseModel):
    """Deployment plan configuration"""
    environment: str = Field(..., description="Environment: development, staging, production")
    services: List[str] = Field(..., description="Services to deploy")
    strategy: str = Field(default="sequential", description="Deployment strategy: sequential, parallel, rolling")
    intelligence_level: str = Field(default="basic", description="AI intelligence level: basic, advanced, full")
    learning_enabled: bool = Field(default=True, description="Enable deployment learning")
    timeout_seconds: int = Field(default=3600, description="Deployment timeout")
    rollback_on_failure: bool = Field(default=True, description="Auto-rollback on failure")
    notify_on_completion: bool = Field(default=True, description="Send notifications on completion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DeploymentResult(BaseModel):
    """Deployment execution result"""
    deployment_id: str
    plan: DeploymentPlan
    status: str = Field(..., description="Status: success, failed, partial, rolled_back")
    services_deployed: List[str] = Field(default_factory=list)
    services_failed: List[str] = Field(default_factory=list)
    execution_time_seconds: int
    started_at: datetime
    completed_at: datetime
    lessons_learned: List[str] = Field(default_factory=list, description="AI-extracted lessons")
    improvements_suggested: List[str] = Field(default_factory=list, description="AI improvement suggestions")
    error_messages: Dict[str, str] = Field(default_factory=dict, description="Error messages by service")
    ai_decisions_made: List[Dict[str, Any]] = Field(default_factory=list, description="AI decisions during deployment")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")