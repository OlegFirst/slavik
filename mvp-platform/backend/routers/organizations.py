"""
Organizations Router
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from models import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationDetailed,
    OrganizationStats,
    ProcessCreate,
    ProcessResponse,
    AIGenerateProcessesRequest,
    AIProcessSuggestion
)
from auth import get_current_user_id
from database import DatabaseClient
from ai_service import AIService

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


def get_db() -> DatabaseClient:
    """Get database client"""
    return DatabaseClient()


def get_ai() -> AIService:
    """Get AI service"""
    return AIService()


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    request: OrganizationCreate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Create organization

    User can only own one organization in MVP
    """
    # Check if user already has an organization
    existing_org = await db.get_organization_by_owner(user_id)
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already owns an organization"
        )

    # Create organization
    org_data = {
        "owner_id": user_id,
        "name": request.name,
        "industry": request.industry.value if request.industry else None,
        "size": request.size,
        "country": request.country,
        "description": request.description,
        "website": request.website,
        "bcm_maturity_score": 0
    }

    org = await db.create_organization(org_data)

    # Log audit
    await db.create_audit_log({
        "user_id": user_id,
        "organization_id": org["id"],
        "action": "organization.created",
        "resource_type": "organization",
        "resource_id": org["id"]
    })

    return OrganizationResponse(**org)


@router.get("/my", response_model=Optional[OrganizationDetailed])
async def get_my_organization(
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Get current user's organization
    """
    org = await db.get_organization_by_owner(user_id)

    if not org:
        return None

    # Get statistics
    processes = await db.list_processes(org["id"])
    bia_analyses = await db.list_bia_analyses(org["id"])

    stats = OrganizationStats(
        processes_count=len(processes),
        bia_analyses_count=len(bia_analyses)
    )

    return OrganizationDetailed(**org, stats=stats)


@router.get("/{org_id}", response_model=OrganizationDetailed)
async def get_organization(
    org_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Get organization by ID
    """
    org = await db.get_organization(org_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Check ownership
    if org["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get statistics
    processes = await db.list_processes(org["id"])
    bia_analyses = await db.list_bia_analyses(org["id"])

    stats = OrganizationStats(
        processes_count=len(processes),
        bia_analyses_count=len(bia_analyses)
    )

    return OrganizationDetailed(**org, stats=stats)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    request: OrganizationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Update organization
    """
    org = await db.get_organization(org_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    if org["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update only provided fields
    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.industry is not None:
        update_data["industry"] = request.industry.value
    if request.size is not None:
        update_data["size"] = request.size
    if request.country is not None:
        update_data["country"] = request.country
    if request.description is not None:
        update_data["description"] = request.description
    if request.website is not None:
        update_data["website"] = request.website

    updated_org = await db.update_organization(org_id, update_data)

    return OrganizationResponse(**updated_org)


@router.post("/{org_id}/processes", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
async def create_process(
    org_id: str,
    request: ProcessCreate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Create business process
    """
    org = await db.get_organization(org_id)

    if not org or org["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    process_data = {
        "organization_id": org_id,
        "name": request.name,
        "description": request.description,
        "category": request.category,
        "criticality": request.criticality.value if request.criticality else None,
        "department_id": request.department_id,
        "owner_person": request.owner_person
    }

    process = await db.create_process(process_data)

    return ProcessResponse(**process)


@router.get("/{org_id}/processes", response_model=List[ProcessResponse])
async def list_processes(
    org_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    List organization processes
    """
    org = await db.get_organization(org_id)

    if not org or org["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    processes = await db.list_processes(org_id)

    return [ProcessResponse(**p) for p in processes]


@router.post("/{org_id}/processes/generate-ai", response_model=List[AIProcessSuggestion])
async def generate_processes_ai(
    org_id: str,
    request: AIGenerateProcessesRequest,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db),
    ai: AIService = Depends(get_ai)
):
    """
    Generate process suggestions using AI
    """
    org = await db.get_organization(org_id)

    if not org or org["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        suggestions = await ai.generate_processes_for_industry(
            industry=request.industry,
            size=request.size,
            country=request.country,
            user_id=user_id,
            organization_id=org_id
        )

        return [AIProcessSuggestion(**s) for s in suggestions]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}"
        )
