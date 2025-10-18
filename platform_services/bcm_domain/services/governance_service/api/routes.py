"""
Governance Service API Routes
ALL endpoints from original /Users/MD/ISO-22301—копия/services/SERVICES/BCM/governance/main.py

ISO 22301 Clauses: 4 (Context), 5 (Leadership), 6 (Planning), 7 (Support)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
from datetime import datetime

from shared.database import get_db
from shared.eventbus.client import get_eventbus
from shared.auth.dependencies import get_current_user_dep, require_role
from models.database import (
    BCMPolicy, PolicyStatus, PolicyType,
    OrganizationalRole, RoleType, RoleStatus,
    BCMResource, ResourceType, ResourceAvailability,
    CompetenceRecord, CompetenceLevel, EvidenceType,
    BCMObjective, CommunicationPlan,
    Stakeholder, ContextAnalysis
)

router = APIRouter()

# Import Pydantic models from original
from pydantic import BaseModel, Field

# ===== PYDANTIC MODELS =====

class PolicyCreate(BaseModel):
    """Create Policy Request"""
    title: str
    policy_type: PolicyType
    version: str = "1.0"
    content: str
    summary: Optional[str] = None
    iso_clause: Optional[str] = None
    scope: Optional[str] = None
    applicable_departments: List[str] = Field(default_factory=list)
    applicable_locations: List[str] = Field(default_factory=list)
    policy_owner: Optional[str] = None
    review_frequency_months: int = 12

class PolicyUpdate(BaseModel):
    """Update Policy Request"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    policy_owner: Optional[str] = None
    approved_by: Optional[str] = None
    status: Optional[PolicyStatus] = None

class PolicyResponse(BaseModel):
    """Policy Response"""
    id: int
    tenant_id: str
    title: str
    policy_type: str
    version: str
    status: str
    policy_owner: Optional[str]
    created_at: datetime
    updated_at: datetime
    next_review_date: Optional[datetime]

    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    """Create Role Request"""
    role_name: str
    role_type: RoleType
    description: Optional[str] = None
    responsibilities: List[Dict] = Field(default_factory=list)
    authorities: List[Dict] = Field(default_factory=list)
    competence_requirements: List[Dict] = Field(default_factory=list)
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None

class RoleUpdate(BaseModel):
    """Update Role Request"""
    role_name: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    status: Optional[RoleStatus] = None

class RoleResponse(BaseModel):
    """Role Response"""
    id: int
    tenant_id: str
    role_name: str
    role_type: str
    assigned_to: Optional[str]
    assigned_to_name: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ResourceCreate(BaseModel):
    """Create Resource Request"""
    resource_name: str
    resource_type: ResourceType
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    cost_per_unit: Optional[float] = None
    total_cost: Optional[float] = None
    criticality: Optional[int] = Field(None, ge=1, le=5)
    is_critical: bool = False
    owner: Optional[str] = None

class ResourceUpdate(BaseModel):
    """Update Resource Request"""
    resource_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    availability: Optional[ResourceAvailability] = None

class ResourceResponse(BaseModel):
    """Resource Response"""
    id: int
    tenant_id: str
    resource_name: str
    resource_type: str
    availability: str
    quantity: Optional[float]
    is_critical: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ObjectiveCreate(BaseModel):
    """Create Objective Request"""
    title: str
    description: str
    objective_type: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = 0.0
    unit_of_measure: Optional[str] = None
    objective_owner: str
    target_date: datetime

class ObjectiveUpdate(BaseModel):
    """Update Objective Request"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    target_date: Optional[datetime] = None

class ObjectiveResponse(BaseModel):
    """Objective Response"""
    id: int
    tenant_id: str
    title: str
    objective_owner: str
    status: str
    progress_percentage: int
    target_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class CompetenceCreate(BaseModel):
    """Create Competence Record Request"""
    person_id: str
    person_name: str
    role_id: Optional[int] = None
    competence_area: str
    competence_category: Optional[str] = None
    required_level: CompetenceLevel
    current_level: Optional[CompetenceLevel] = None
    evidence_type: EvidenceType
    evidence_details: Dict = Field(default_factory=dict)

class CompetenceResponse(BaseModel):
    """Competence Response"""
    id: int
    tenant_id: str
    person_id: str
    person_name: str
    competence_area: str
    required_level: str
    current_level: Optional[str]
    gap_exists: bool
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CommunicationPlanCreate(BaseModel):
    """Create Communication Plan Request"""
    name: str
    description: Optional[str] = None
    plan_type: Optional[str] = None
    stakeholders: List[Dict] = Field(default_factory=list)
    channels: List[Dict] = Field(default_factory=list)

class CommunicationPlanResponse(BaseModel):
    """Communication Plan Response"""
    id: int
    tenant_id: str
    name: str
    plan_type: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# POLICY ENDPOINTS - ISO 22301 Clause 5.2
# ============================================================================

@router.post("/policies", response_model=PolicyResponse, status_code=201)
async def create_policy(
    policy: PolicyCreate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Create new BCM policy (admin, bcm_manager only)"""
    try:
        from services.governance_service import PolicyService
        service = PolicyService(db)

        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        db_policy = await service.create_policy(
            tenant_id=tenant_id,
            title=policy.title,
            policy_type=policy.policy_type,
            version=policy.version,
            content=policy.content,
            summary=policy.summary,
            iso_clause=policy.iso_clause,
            scope=policy.scope,
            applicable_departments=policy.applicable_departments,
            applicable_locations=policy.applicable_locations,
            policy_owner=policy.policy_owner,
            review_frequency_months=policy.review_frequency_months,
        )

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.policy.created",
                {
                    "policy_id": db_policy.id,
                    "tenant_id": db_policy.tenant_id,
                    "title": db_policy.title,
                    "policy_type": db_policy.policy_type.value,
                },
                tenant_id=db_policy.tenant_id
            )
        except:
            pass  # Don't fail if eventbus unavailable

        return db_policy

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies", response_model=List[PolicyResponse])
async def list_policies(
    status: Optional[PolicyStatus] = None,
    policy_type: Optional[PolicyType] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List policies with filters (all authenticated users)"""
    try:
        from services.governance_service import PolicyService
        service = PolicyService(db)

        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        policies = await service.list_policies(
            tenant_id=tenant_id,
            status=status,
            policy_type=policy_type
        )

        return policies

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get policy by ID (all authenticated users)"""
    try:
        from services.governance_service import PolicyService
        service = PolicyService(db)

        policy = await service.get_policy(policy_id)
        return policy

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: int,
    updates: PolicyUpdate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Update policy (admin, bcm_manager only)"""
    try:
        from services.governance_service import PolicyService
        service = PolicyService(db)

        # Extract fields from updates
        update_data = updates.dict(exclude_unset=True)

        policy = await service.update_policy(
            policy_id=policy_id,
            title=update_data.get('title'),
            content=update_data.get('content'),
            summary=update_data.get('summary'),
            policy_owner=update_data.get('policy_owner'),
            approved_by=update_data.get('approved_by'),
            status=update_data.get('status'),
        )

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.policy.updated",
                {"policy_id": policy_id},
                tenant_id=policy.tenant_id
            )
        except:
            pass

        return policy

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: int,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Delete policy (admin, bcm_manager only)"""
    try:
        result = await db.execute(select(BCMPolicy).filter(BCMPolicy.id == policy_id))
        policy = result.scalar_one_or_none()

        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")

        tenant_id = policy.tenant_id
        await db.delete(policy)
        await db.commit()

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.policy.deleted",
                {"policy_id": policy_id},
                tenant_id=tenant_id
            )
        except:
            pass

        return {"message": "Policy deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies/{policy_id}/approve", response_model=PolicyResponse)
async def approve_policy(
    policy_id: int,
    approved_by: str,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Approve policy (admin, bcm_manager only)"""
    try:
        from services.governance_service import PolicyService
        service = PolicyService(db)

        policy = await service.approve_policy(
            policy_id=policy_id,
            approved_by=approved_by
        )

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.policy.approved",
                {
                    "policy_id": policy_id,
                    "approved_by": approved_by,
                },
                tenant_id=policy.tenant_id
            )
        except:
            pass

        return policy

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies/{policy_id}/publish", response_model=PolicyResponse)
async def publish_policy(
    policy_id: int,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Publish policy (admin, bcm_manager only)"""
    try:
        from services.governance_service import PolicyService
        service = PolicyService(db)

        policy = await service.activate_policy(policy_id)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.policy.published",
                {"policy_id": policy_id},
                tenant_id=policy.tenant_id
            )
        except:
            pass

        return policy

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROLE ENDPOINTS - ISO 22301 Clause 5.3
# ============================================================================

@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    role: RoleCreate,
    current_user: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Create organizational role (admin only)"""
    try:
        from services.governance_service import RoleService
        service = RoleService(db)

        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        db_role = await service.create_role(
            tenant_id=tenant_id,
            role_name=role.role_name,
            role_type=role.role_type,
            description=role.description,
            responsibilities=role.responsibilities,
            authorities=role.authorities,
            competence_requirements=role.competence_requirements,
            assigned_to=role.assigned_to,
            assigned_to_name=role.assigned_to_name,
        )

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.role.created",
                {
                    "role_id": db_role.id,
                    "tenant_id": db_role.tenant_id,
                    "role_name": db_role.role_name,
                },
                tenant_id=db_role.tenant_id
            )
        except:
            pass

        return db_role

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    status: Optional[RoleStatus] = None,
    role_type: Optional[RoleType] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List roles with filters (all authenticated users)"""
    try:
        from services.governance_service import RoleService
        service = RoleService(db)

        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        roles = await service.list_roles(
            tenant_id=tenant_id,
            status=status,
            role_type=role_type
        )

        return roles

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get role by ID (all authenticated users)"""
    try:
        from services.governance_service import RoleService
        service = RoleService(db)

        role = await service.get_role(role_id)
        return role

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    updates: RoleUpdate,
    current_user: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Update role (admin only)"""
    try:
        result = await db.execute(select(OrganizationalRole).filter(OrganizationalRole.id == role_id))
        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Update fields
        for field, value in updates.dict(exclude_unset=True).items():
            setattr(role, field, value)

        await db.commit()
        await db.refresh(role)

        return role

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/roles/{role_id}/assign", response_model=RoleResponse)
async def assign_role(
    role_id: int,
    assigned_to: str,
    assigned_to_name: str,
    current_user: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Assign role to person (admin only)"""
    try:
        from services.governance_service import RoleService
        service = RoleService(db)

        role = await service.assign_role(
            role_id=role_id,
            assigned_to=assigned_to,
            assigned_to_name=assigned_to_name
        )

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.role.assigned",
                {
                    "role_id": role_id,
                    "assigned_to": assigned_to,
                    "assigned_to_name": assigned_to_name,
                },
                tenant_id=role.tenant_id
            )
        except:
            pass

        return role

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RESOURCE ENDPOINTS - ISO 22301 Clause 7.1
# ============================================================================

@router.post("/resources", response_model=ResourceResponse, status_code=201)
async def create_resource(
    resource: ResourceCreate,
    current_user: dict = Depends(require_role("admin", "resource_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Create BCM resource (admin, resource_manager only)"""
    try:
        from services.governance_service import ResourceService
        service = ResourceService(db)

        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        db_resource = await service.create_resource(
            tenant_id=tenant_id,
            resource_name=resource.resource_name,
            resource_type=resource.resource_type,
            description=resource.description,
            quantity=resource.quantity,
            unit=resource.unit,
            cost_per_unit=resource.cost_per_unit,
            total_cost=resource.total_cost,
            criticality=resource.criticality,
            is_critical=resource.is_critical,
            owner=resource.owner,
        )

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.resource.created",
                {
                    "resource_id": db_resource.id,
                    "tenant_id": db_resource.tenant_id,
                    "resource_name": db_resource.resource_name,
                    "is_critical": db_resource.is_critical,
                },
                tenant_id=db_resource.tenant_id
            )
        except:
            pass

        return db_resource

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources", response_model=List[ResourceResponse])
async def list_resources(
    resource_type: Optional[ResourceType] = None,
    availability: Optional[ResourceAvailability] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List resources with filters (all authenticated users)"""
    try:
        from services.governance_service import ResourceService
        service = ResourceService(db)

        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        resources = await service.list_resources(
            tenant_id=tenant_id,
            resource_type=resource_type,
            availability=availability
        )

        return resources

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get resource by ID (all authenticated users)"""
    try:
        from services.governance_service import ResourceService
        service = ResourceService(db)

        resource = await service.get_resource(resource_id)
        return resource

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    updates: ResourceUpdate,
    current_user: dict = Depends(require_role("admin", "resource_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Update resource (admin, resource_manager only)"""
    try:
        result = await db.execute(select(BCMResource).filter(BCMResource.id == resource_id))
        resource = result.scalar_one_or_none()

        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        # Update fields
        for field, value in updates.dict(exclude_unset=True).items():
            setattr(resource, field, value)

        await db.commit()
        await db.refresh(resource)

        # Publish event if availability changed
        if updates.availability:
            try:
                eventbus = get_eventbus()
                await eventbus.publish(
                    "governance.resource.allocated" if updates.availability == ResourceAvailability.ALLOCATED else "governance.resource.updated",
                    {
                        "resource_id": resource_id,
                        "availability": resource.availability.value,
                    },
                    tenant_id=resource.tenant_id
                )
            except:
                pass

        return resource

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMPETENCE ENDPOINTS - ISO 22301 Clause 7.2
# ============================================================================

@router.post("/competence", response_model=CompetenceResponse, status_code=201)
async def create_competence_record(
    comp: CompetenceCreate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Create competence record - ISO 7.2 (admin, bcm_manager only)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        # Calculate gap
        gap_exists = False
        if comp.current_level:
            levels = ["basic", "intermediate", "advanced", "expert"]
            req_idx = levels.index(comp.required_level.value)
            cur_idx = levels.index(comp.current_level.value)
            gap_exists = cur_idx < req_idx

        db_comp = CompetenceRecord(
            tenant_id=tenant_id,
            person_id=comp.person_id,
            person_name=comp.person_name,
            role_id=comp.role_id,
            competence_area=comp.competence_area,
            competence_category=comp.competence_category,
            required_level=comp.required_level,
            current_level=comp.current_level,
            gap_exists=gap_exists,
            evidence_type=comp.evidence_type,
            evidence_details=comp.evidence_details
        )

        db.add(db_comp)
        await db.commit()
        await db.refresh(db_comp)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.competence.recorded",
                {
                    "competence_id": db_comp.id,
                    "tenant_id": db_comp.tenant_id,
                    "person_id": db_comp.person_id,
                    "gap_exists": gap_exists,
                },
                tenant_id=db_comp.tenant_id
            )
        except:
            pass

        return db_comp

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competence", response_model=List[CompetenceResponse])
async def list_competence(
    person_id: Optional[str] = None,
    gap_exists: Optional[bool] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List competence records (all authenticated users)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        query = select(CompetenceRecord).filter(CompetenceRecord.tenant_id == tenant_id)

        if person_id:
            query = query.filter(CompetenceRecord.person_id == person_id)
        if gap_exists is not None:
            query = query.filter(CompetenceRecord.gap_exists == gap_exists)

        result = await db.execute(query)
        records = result.scalars().all()
        return records

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# OBJECTIVE ENDPOINTS - ISO 22301 Clause 6.2
# ============================================================================

@router.post("/objectives", response_model=ObjectiveResponse, status_code=201)
async def create_objective(
    objective: ObjectiveCreate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Create BCM objective - ISO 6.2 (admin, bcm_manager only)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        db_objective = BCMObjective(
            tenant_id=tenant_id,
            title=objective.title,
            description=objective.description,
            objective_type=objective.objective_type,
            target_value=objective.target_value,
            current_value=objective.current_value,
            unit_of_measure=objective.unit_of_measure,
            objective_owner=objective.objective_owner,
            target_date=objective.target_date,
            status="not_started",
            progress_percentage=0
        )

        db.add(db_objective)
        await db.commit()
        await db.refresh(db_objective)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.objective.created",
                {
                    "objective_id": db_objective.id,
                    "tenant_id": db_objective.tenant_id,
                    "title": db_objective.title,
                },
                tenant_id=db_objective.tenant_id
            )
        except:
            pass

        return db_objective

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/objectives", response_model=List[ObjectiveResponse])
async def list_objectives(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List BC objectives (all authenticated users)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        query = select(BCMObjective).filter(BCMObjective.tenant_id == tenant_id)

        if status:
            query = query.filter(BCMObjective.status == status)

        result = await db.execute(query)
        objectives = result.scalars().all()
        return objectives

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/objectives/{objective_id}", response_model=ObjectiveResponse)
async def get_objective(
    objective_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get objective by ID (all authenticated users)"""
    try:
        result = await db.execute(select(BCMObjective).filter(BCMObjective.id == objective_id))
        objective = result.scalar_one_or_none()

        if not objective:
            raise HTTPException(status_code=404, detail="Objective not found")

        return objective

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/objectives/{objective_id}", response_model=ObjectiveResponse)
async def update_objective(
    objective_id: int,
    updates: ObjectiveUpdate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Update BCM objective - ISO 6.2 (admin, bcm_manager only)"""
    try:
        result = await db.execute(select(BCMObjective).filter(BCMObjective.id == objective_id))
        objective = result.scalar_one_or_none()

        if not objective:
            raise HTTPException(status_code=404, detail="Objective not found")

        # Update fields
        for field, value in updates.dict(exclude_unset=True).items():
            setattr(objective, field, value)

        # Recalculate progress if current_value or target_value changed
        if objective.target_value and objective.target_value > 0:
            objective.progress_percentage = min(100, int((objective.current_value / objective.target_value) * 100))

        await db.commit()
        await db.refresh(objective)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "governance.objective.updated",
                {
                    "objective_id": objective_id,
                    "progress_percentage": objective.progress_percentage,
                },
                tenant_id=objective.tenant_id
            )
        except:
            pass

        return objective

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMMUNICATION PLANS ENDPOINTS - ISO 22301 Clause 7.4
# ============================================================================

@router.post("/communication-plans", response_model=CommunicationPlanResponse, status_code=201)
async def create_communication_plan(
    plan: CommunicationPlanCreate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Create communication plan - ISO 7.4 (admin, bcm_manager only)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        db_plan = CommunicationPlan(
            tenant_id=tenant_id,
            name=plan.name,
            description=plan.description,
            plan_type=plan.plan_type,
            stakeholders=plan.stakeholders,
            channels=plan.channels,
            is_active=True
        )

        db.add(db_plan)
        await db.commit()
        await db.refresh(db_plan)

        return db_plan

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/communication-plans", response_model=List[CommunicationPlanResponse])
async def list_communication_plans(
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List communication plans (all authenticated users)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        query = select(CommunicationPlan).filter(CommunicationPlan.tenant_id == tenant_id)

        if is_active is not None:
            query = query.filter(CommunicationPlan.is_active == is_active)

        result = await db.execute(query)
        plans = result.scalars().all()
        return plans

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STAKEHOLDER ENDPOINTS - ISO 22301 Clause 4.2
# ============================================================================

class StakeholderCreate(BaseModel):
    """Create Stakeholder Request"""
    stakeholder_name: str
    stakeholder_type: str
    category: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    influence_level: str
    interest_level: str
    power_level: Optional[str] = None
    requirements: List[Dict] = Field(default_factory=list)
    expectations: List[Dict] = Field(default_factory=list)
    communication_frequency: Optional[str] = None
    communication_method: Optional[str] = None
    communication_language: Optional[str] = "en"
    needs_notification_during_incident: bool = False
    notification_priority: Optional[int] = None
    critical_to_bcms: bool = False
    related_processes: List[int] = Field(default_factory=list)
    related_risks: List[int] = Field(default_factory=list)
    notes: Optional[str] = None

class StakeholderResponse(BaseModel):
    """Stakeholder Response"""
    id: int
    tenant_id: str
    stakeholder_name: str
    stakeholder_type: str
    category: Optional[str]
    influence_level: str
    interest_level: str
    power_level: Optional[str]
    critical_to_bcms: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/stakeholders", response_model=StakeholderResponse, status_code=201)
async def create_stakeholder(
    stakeholder: StakeholderCreate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Create stakeholder - ISO 4.2 (admin, bcm_manager only)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        db_stakeholder = Stakeholder(
            tenant_id=tenant_id,
            stakeholder_name=stakeholder.stakeholder_name,
            stakeholder_type=stakeholder.stakeholder_type,
            category=stakeholder.category,
            contact_person=stakeholder.contact_person,
            contact_email=stakeholder.contact_email,
            contact_phone=stakeholder.contact_phone,
            influence_level=stakeholder.influence_level,
            interest_level=stakeholder.interest_level,
            power_level=stakeholder.power_level,
            requirements=stakeholder.requirements,
            expectations=stakeholder.expectations,
            communication_frequency=stakeholder.communication_frequency,
            communication_method=stakeholder.communication_method,
            communication_language=stakeholder.communication_language,
            needs_notification_during_incident=stakeholder.needs_notification_during_incident,
            notification_priority=stakeholder.notification_priority,
            critical_to_bcms=stakeholder.critical_to_bcms,
            related_processes=stakeholder.related_processes,
            related_risks=stakeholder.related_risks,
            notes=stakeholder.notes
        )

        db.add(db_stakeholder)
        await db.commit()
        await db.refresh(db_stakeholder)

        return db_stakeholder

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stakeholders", response_model=List[StakeholderResponse])
async def list_stakeholders(
    stakeholder_type: Optional[str] = None,
    influence_level: Optional[str] = None,
    critical_to_bcms: Optional[bool] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List stakeholders with filters (all authenticated users)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        query = select(Stakeholder).filter(Stakeholder.tenant_id == tenant_id)

        if stakeholder_type:
            query = query.filter(Stakeholder.stakeholder_type == stakeholder_type)
        if influence_level:
            query = query.filter(Stakeholder.influence_level == influence_level)
        if critical_to_bcms is not None:
            query = query.filter(Stakeholder.critical_to_bcms == critical_to_bcms)

        result = await db.execute(query)
        stakeholders = result.scalars().all()
        return stakeholders

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stakeholders/{stakeholder_id}", response_model=StakeholderResponse)
async def get_stakeholder(
    stakeholder_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get stakeholder by ID (all authenticated users)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        query = select(Stakeholder).filter(
            Stakeholder.id == stakeholder_id,
            Stakeholder.tenant_id == tenant_id
        )
        result = await db.execute(query)
        stakeholder = result.scalar_one_or_none()

        if not stakeholder:
            raise HTTPException(status_code=404, detail=f"Stakeholder {stakeholder_id} not found")

        return stakeholder

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/stakeholders/{stakeholder_id}", response_model=StakeholderResponse)
async def update_stakeholder(
    stakeholder_id: int,
    updates: Dict,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Update stakeholder (admin, bcm_manager only)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        query = select(Stakeholder).filter(
            Stakeholder.id == stakeholder_id,
            Stakeholder.tenant_id == tenant_id
        )
        result = await db.execute(query)
        stakeholder = result.scalar_one_or_none()

        if not stakeholder:
            raise HTTPException(status_code=404, detail=f"Stakeholder {stakeholder_id} not found")

        # Update fields
        for field, value in updates.items():
            if hasattr(stakeholder, field):
                setattr(stakeholder, field, value)

        await db.commit()
        await db.refresh(stakeholder)

        return stakeholder

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CONTEXT ANALYSIS ENDPOINTS - ISO 22301 Clause 4.1
# ============================================================================

class ContextAnalysisCreate(BaseModel):
    """Create Context Analysis Request"""
    analysis_type: str  # PESTLE, SWOT, PORTER, VUCA, SCENARIO
    analysis_name: str
    analysis_date: datetime
    review_date: Optional[datetime] = None
    analysis_data: Dict
    insights: List[Dict] = Field(default_factory=list)
    action_items: List[Dict] = Field(default_factory=list)
    identified_risks: List[int] = Field(default_factory=list)
    identified_opportunities: List[int] = Field(default_factory=list)
    impacts_on_scope: bool = False
    impacts_on_objectives: bool = False
    related_bc_objectives: List[int] = Field(default_factory=list)
    notes: Optional[str] = None

class ContextAnalysisResponse(BaseModel):
    """Context Analysis Response"""
    id: int
    tenant_id: str
    analysis_type: str
    analysis_name: str
    analysis_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/context-analysis", response_model=ContextAnalysisResponse, status_code=201)
async def create_context_analysis(
    analysis: ContextAnalysisCreate,
    current_user: dict = Depends(require_role("admin", "bcm_manager")),
    db: AsyncSession = Depends(get_db)
):
    """Create context analysis - ISO 4.1 (admin, bcm_manager only)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        db_analysis = ContextAnalysis(
            tenant_id=tenant_id,
            analysis_type=analysis.analysis_type,
            analysis_name=analysis.analysis_name,
            analysis_date=analysis.analysis_date,
            review_date=analysis.review_date,
            analysis_data=analysis.analysis_data,
            insights=analysis.insights,
            action_items=analysis.action_items,
            identified_risks=analysis.identified_risks,
            identified_opportunities=analysis.identified_opportunities,
            impacts_on_scope=analysis.impacts_on_scope,
            impacts_on_objectives=analysis.impacts_on_objectives,
            related_bc_objectives=analysis.related_bc_objectives,
            notes=analysis.notes
        )

        db.add(db_analysis)
        await db.commit()
        await db.refresh(db_analysis)

        return db_analysis

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context-analysis", response_model=List[ContextAnalysisResponse])
async def list_context_analyses(
    analysis_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """List context analyses (all authenticated users)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        query = select(ContextAnalysis).filter(ContextAnalysis.tenant_id == tenant_id)

        if analysis_type:
            query = query.filter(ContextAnalysis.analysis_type == analysis_type)

        query = query.order_by(ContextAnalysis.analysis_date.desc())

        result = await db.execute(query)
        analyses = result.scalars().all()
        return analyses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context-analysis/{analysis_id}")
async def get_context_analysis(
    analysis_id: int,
    current_user: dict = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """Get context analysis by ID (all authenticated users)"""
    try:
        # Extract tenant_id from JWT token
        tenant_id = current_user["tenant_id"]

        query = select(ContextAnalysis).filter(
            ContextAnalysis.id == analysis_id,
            ContextAnalysis.tenant_id == tenant_id
        )
        result = await db.execute(query)
        analysis = result.scalar_one_or_none()

        if not analysis:
            raise HTTPException(status_code=404, detail=f"Context analysis {analysis_id} not found")

        return {
            "id": analysis.id,
            "tenant_id": analysis.tenant_id,
            "analysis_type": analysis.analysis_type,
            "analysis_name": analysis.analysis_name,
            "analysis_date": analysis.analysis_date.isoformat(),
            "review_date": analysis.review_date.isoformat() if analysis.review_date else None,
            "analysis_data": analysis.analysis_data,
            "insights": analysis.insights,
            "action_items": analysis.action_items,
            "identified_risks": analysis.identified_risks,
            "identified_opportunities": analysis.identified_opportunities,
            "status": analysis.status,
            "impacts_on_scope": analysis.impacts_on_scope,
            "impacts_on_objectives": analysis.impacts_on_objectives,
            "related_bc_objectives": analysis.related_bc_objectives,
            "notes": analysis.notes,
            "created_at": analysis.created_at.isoformat(),
            "updated_at": analysis.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
