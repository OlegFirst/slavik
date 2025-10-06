"""
Common Pydantic Models
======================

Shared Pydantic models used across BCM Platform services.

Features:
- User models
- Tenant models
- Health check models
- Pagination models
"""

from typing import Optional, List, Generic, TypeVar, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator


class User(BaseModel):
    """
    User model.

    Example:
        ```python
        user = User(
            user_id="user123",
            tenant_id="tenant456",
            email="user@example.com",
            role="bcm_manager"
        )
        ```
    """
    user_id: str
    tenant_id: str
    email: EmailStr
    role: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "tenant_id": "tenant456",
                "email": "john.doe@example.com",
                "role": "bcm_manager",
                "full_name": "John Doe",
                "is_active": True
            }
        }


class Tenant(BaseModel):
    """
    Tenant model.

    Example:
        ```python
        tenant = Tenant(
            tenant_id="tenant123",
            name="ACME Corporation",
            industry="Technology"
        )
        ```
    """
    tenant_id: str
    name: str
    industry: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    is_active: bool = True
    subscription_tier: str = "standard"
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant123",
                "name": "ACME Corporation",
                "industry": "Technology",
                "contact_email": "admin@acme.com",
                "subscription_tier": "enterprise"
            }
        }


class HealthCheck(BaseModel):
    """
    Health check response model.

    Example:
        ```python
        @app.get("/health", response_model=HealthCheck)
        async def health_check():
            return HealthCheck(
                status="healthy",
                service="validation-service",
                version="1.0.0"
            )
        ```
    """
    status: str = Field(..., description="Health status: healthy, degraded, unhealthy")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Optional[dict] = Field(None, description="Detailed health checks")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "validation-service",
                "version": "1.0.0",
                "timestamp": "2025-10-03T10:30:00Z",
                "checks": {
                    "database": "up",
                    "redis": "up",
                    "eventbus": "up"
                }
            }
        }


class PaginationParams(BaseModel):
    """
    Pagination parameters.

    Example:
        ```python
        @router.get("/exercises")
        async def list_exercises(
            pagination: PaginationParams = Depends()
        ):
            offset = (pagination.page - 1) * pagination.page_size
            exercises = await repo.list(
                limit=pagination.page_size,
                offset=offset
            )
            return PaginatedResponse(
                items=exercises,
                total=total_count,
                page=pagination.page,
                page_size=pagination.page_size
            )
        ```
    """
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response model.

    Example:
        ```python
        response = PaginatedResponse(
            items=[exercise1, exercise2, exercise3],
            total=50,
            page=1,
            page_size=20
        )
        # response.total_pages = 3
        # response.has_next = True
        ```
    """
    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1

    class Config:
        json_schema_extra = {
            "example": {
                "items": ["item1", "item2", "item3"],
                "total": 50,
                "page": 1,
                "page_size": 20
            }
        }


class AuditLog(BaseModel):
    """
    Audit log entry model.

    Example:
        ```python
        log = AuditLog(
            action="exercise.created",
            user_id="user123",
            tenant_id="tenant456",
            entity_type="exercise",
            entity_id=123,
            details={"exercise_type": "tabletop"}
        )
        ```
    """
    action: str = Field(..., description="Action performed")
    user_id: str = Field(..., description="User who performed the action")
    tenant_id: str = Field(..., description="Tenant ID")
    entity_type: str = Field(..., description="Type of entity (exercise, document, etc.)")
    entity_id: Any = Field(..., description="Entity identifier")
    details: Optional[dict] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "action": "exercise.created",
                "user_id": "user123",
                "tenant_id": "tenant456",
                "entity_type": "exercise",
                "entity_id": 123,
                "details": {"exercise_type": "tabletop"},
                "timestamp": "2025-10-03T10:30:00Z"
            }
        }
