"""
Authentication Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class UserContext(BaseModel):
    """
    User context extracted from JWT token

    Attributes:
        user_id: Unique identifier for the user
        tenant_id: Tenant/organization ID for multi-tenancy
        email: User's email address
        roles: List of user roles
        is_superadmin: Whether user has superadmin privileges
    """
    user_id: str = Field(..., description="User ID from JWT token")
    tenant_id: str = Field(..., description="Tenant ID for multi-tenancy")
    email: str = Field(..., description="User email address")
    roles: List[str] = Field(default_factory=list, description="User roles")
    is_superadmin: bool = Field(default=False, description="Superadmin flag")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "tenant_id": "tenant-456",
                "email": "user@example.com",
                "roles": ["bcm_manager", "strategy_editor"],
                "is_superadmin": False
            }
        }
