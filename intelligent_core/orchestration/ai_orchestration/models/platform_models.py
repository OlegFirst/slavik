"""
Platform Models - Data models for platform orchestration
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class EventPublishRequest(BaseModel):
    """Request model for publishing events"""
    type: str = Field(..., description="Event type (e.g., bcm.bia.completed)")
    tenant_id: str = Field(..., description="Tenant identifier")
    actor: str = Field(..., description="User or system that triggered the event")
    module: str = Field(..., description="BCM module name")
    data: Dict[str, Any] = Field(..., description="Event payload data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WorkflowStartRequest(BaseModel):
    """Request to start a workflow"""
    workflow_type: str = Field(..., description="Type of workflow (bia, incident, audit)")
    tenant_id: str
    user_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class BIAStartRequest(BaseModel):
    """Request to start BIA process"""
    tenant_id: str
    user_id: str
    departments: List[str] = Field(..., description="List of departments for BIA")


class IncidentReportRequest(BaseModel):
    """Request to report an incident"""
    tenant_id: str
    title: str
    description: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    type: str = Field(default="operational")
    affected_systems: List[str] = Field(default_factory=list)


class AuditStartRequest(BaseModel):
    """Request to start audit"""
    tenant_id: str
    auditor_id: str
    audit_type: str = Field(default="ISO_22301")
    scope: List[str] = Field(default_factory=list)