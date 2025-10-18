"""
Authentication Models
Pydantic models for user context and authentication
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class UserContext(BaseModel):
    """
    User context extracted from JWT token

    Attributes:
        user_id: Unique user identifier
        tenant_id: Tenant/organization identifier for multi-tenancy
        email: User email address
        roles: List of user roles (e.g., ['admin', 'bcm_manager'])
        is_superadmin: Whether user has superadmin privileges
    """
    user_id: str = Field(..., description="Unique user identifier")
    tenant_id: str = Field(..., description="Tenant/organization identifier")
    email: str = Field(..., description="User email address")
    roles: List[str] = Field(default_factory=list, description="User roles")
    is_superadmin: bool = Field(default=False, description="Superadmin flag")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "tenant_id": "org_456",
                "email": "bcm.manager@company.com",
                "roles": ["bcm_manager", "plan_approver"],
                "is_superadmin": False
            }
        }
