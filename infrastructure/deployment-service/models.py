"""
Deployment Service Data Models
==============================

Pydantic models for API requests/responses and database entities.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4


class DeploymentStatus(str, Enum):
    """Deployment status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ServiceStatus(str, Enum):
    """Service status enum"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


class DeploymentRequest(BaseModel):
    """Deployment request model"""
    tenant_id: str = Field(default="system", description="Tenant ID for multi-tenancy")
    services: Optional[List[str]] = Field(
        default=None,
        description="Specific services to deploy (None = all services)"
    )
    strategy: Optional[str] = Field(
        default="sequential",
        description="Deployment strategy: sequential, parallel, ai_optimized"
    )
    rollback_on_failure: bool = Field(
        default=True,
        description="Automatically rollback on critical failure"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class DeploymentRecord(BaseModel):
    """Deployment record for database persistence"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    status: DeploymentStatus
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None

    # Deployment details
    strategy: str
    requested_services: Optional[List[str]] = None
    deployed_services: List[str] = Field(default_factory=list)
    failed_services: List[str] = Field(default_factory=list)

    # Metadata
    initiated_by: Optional[str] = None
    ai_strategy_used: bool = False
    rollback_executed: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class DeploymentResponse(BaseModel):
    """Deployment response model"""
    deployment_id: str
    status: DeploymentStatus
    deployed_services: List[str]
    failed_services: List[str]
    execution_time: int
    total_services: int
    rollback_executed: bool = False
    message: Optional[str] = None

    class Config:
        use_enum_values = True


class ServiceHealthCheck(BaseModel):
    """Service health check result"""
    service_name: str
    status: ServiceStatus
    healthy: bool
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class ServicesStatusResponse(BaseModel):
    """Response for services status endpoint"""
    services: Dict[str, ServiceHealthCheck]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_services: int
    healthy_services: int
    unhealthy_services: int


class RestartServiceRequest(BaseModel):
    """Request to restart a service"""
    service_name: str
    tenant_id: str = Field(default="system")
    force: bool = Field(default=False, description="Force restart even if healthy")


class AIDeploymentStrategy(BaseModel):
    """AI-generated deployment strategy"""
    strategy_type: str
    service_order: List[str]
    parallel_groups: Optional[List[List[str]]] = None
    estimated_duration: int
    risk_assessment: str
    recommendations: List[str]
    confidence: float
