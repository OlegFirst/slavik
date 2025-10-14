"""
Evidence API
Provides endpoints for evidence management with workflow integration
JWT-based authentication with RBAC
"""

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import logging

from compliance.database.connection import get_db
from shared.exceptions import EntityNotFoundError, TenantMismatchError, ValidationError
from compliance.models.schemas import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
    EvidenceWorkflowTransition
)
from compliance.models.database import EvidenceModel, EvidenceStatus
from compliance.workflows.evidence_workflow import EvidenceWorkflow
from compliance.repositories.evidence_repository import EvidenceRepository
from compliance.integrations.eventbus import EventBusService
from compliance.config.settings import settings
from sqlalchemy import select, and_
from shared.auth import get_current_user, Permission, require_permission

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_tenant_access(current_user: dict, tenant_id: str) -> None:
    """Verify user has access to tenant"""
    if current_user.get("tenant_id") != tenant_id:
        raise TenantMismatchError(
            user_tenant=current_user.get("tenant_id"),
            resource_tenant=tenant_id
        )


# Dependency injection factories
def get_evidence_repository(db: AsyncSession = Depends(get_db)) -> EvidenceRepository:
    """Get Evidence repository with database session"""
    return EvidenceRepository(db)


async def get_evidence_workflow(
    db: AsyncSession = Depends(get_db)
) -> EvidenceWorkflow:
    """Dependency to get evidence workflow instance"""
    eventbus = None
    if settings.eventbus_url:
        eventbus = EventBusService(settings.eventbus_url)
    return EvidenceWorkflow(db, eventbus)


@router.post(
    "/",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED
)
@require_permission(Permission.EVIDENCE_CREATE)
async def create_evidence(
    evidence_data: EvidenceCreate,
    workflow: EvidenceWorkflow = Depends(get_evidence_workflow),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> EvidenceResponse:
    """
    Create new evidence

    Creates evidence in DRAFT status. Use workflow transitions to move through states.
    Requires: EVIDENCE_CREATE permission

    Args:
        evidence_data: Evidence creation data
        workflow: Evidence workflow instance
        db: Database session
        current_user: Authenticated user

    Returns:
        Created evidence
    """
    try:
        # Verify tenant access
        verify_tenant_access(current_user, evidence_data.tenant_id)
        # Create evidence via workflow (ensures proper initial state)
        evidence = await workflow.create_evidence(
            tenant_id=evidence_data.tenant_id,
            requirement_id=evidence_data.requirement_id,
            title=evidence_data.title,
            description=evidence_data.description,
            evidence_type=evidence_data.evidence_type,
            file_path=evidence_data.file_path,
            file_size=evidence_data.file_size,
            mime_type=evidence_data.mime_type,
            metadata=evidence_data.metadata
        )

        logger.info(
            f"Evidence created: {evidence['id']} "
            f"for requirement {evidence_data.requirement_id}"
        )

        return EvidenceResponse(**evidence)

    except Exception as e:
        logger.error(f"Failed to create evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create evidence: {str(e)}"
        )


@router.get("/", response_model=List[EvidenceResponse])
@require_permission(Permission.EVIDENCE_VIEW)
async def list_evidence(
    tenant_id: str,
    requirement_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    repository: EvidenceRepository = Depends(get_evidence_repository),
    current_user: dict = Depends(get_current_user)
) -> List[EvidenceResponse]:
    """
    List evidence with optional filters
    Requires: EVIDENCE_VIEW permission

    Args:
        tenant_id: Tenant identifier
        requirement_id: Optional requirement filter
        status_filter: Optional status filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        repository: Evidence repository
        current_user: Authenticated user

    Returns:
        List of evidence
    """
    try:
        # Verify tenant access
        verify_tenant_access(current_user, tenant_id)
        # Use repository to get evidence list
        evidence_list = await repository.list_by_tenant(
            tenant_id=tenant_id,
            requirement_id=requirement_id,
            status=status_filter,
            skip=skip,
            limit=limit
        )

        return [EvidenceResponse.model_validate(e) for e in evidence_list]

    except Exception as e:
        logger.error(f"Failed to list evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list evidence: {str(e)}"
        )


@router.get("/{evidence_id}", response_model=EvidenceResponse)
@require_permission(Permission.EVIDENCE_VIEW)
async def get_evidence(
    evidence_id: str,
    tenant_id: str,
    repository: EvidenceRepository = Depends(get_evidence_repository),
    current_user: dict = Depends(get_current_user)
) -> EvidenceResponse:
    """
    Get evidence by ID
    Requires: EVIDENCE_VIEW permission

    Args:
        evidence_id: Evidence identifier
        tenant_id: Tenant identifier
        repository: Evidence repository
        current_user: Authenticated user

    Returns:
        Evidence details
    """
    try:
        # Verify tenant access
        verify_tenant_access(current_user, tenant_id)

        evidence = await repository.get_by_id(evidence_id, tenant_id)

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence {evidence_id} not found"
            )

        return EvidenceResponse.model_validate(evidence)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get evidence: {str(e)}"
        )


@router.patch("/{evidence_id}", response_model=EvidenceResponse)
@require_permission(Permission.EVIDENCE_UPDATE)
async def update_evidence(
    evidence_id: str,
    tenant_id: str,
    update_data: EvidenceUpdate,
    repository: EvidenceRepository = Depends(get_evidence_repository),
    current_user: dict = Depends(get_current_user)
) -> EvidenceResponse:
    """
    Update evidence metadata
    Requires: EVIDENCE_UPDATE permission

    Note: Status changes must use workflow transition endpoint

    Args:
        evidence_id: Evidence identifier
        tenant_id: Tenant identifier
        update_data: Fields to update
        repository: Evidence repository
        current_user: Authenticated user

    Returns:
        Updated evidence
    """
    try:
        # Verify tenant access
        verify_tenant_access(current_user, tenant_id)

        # Update fields (excluding status - use workflow)
        update_dict = update_data.model_dump(exclude_unset=True, exclude={"status"})

        evidence = await repository.update(evidence_id, tenant_id, update_dict)

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence {evidence_id} not found"
            )

        logger.info(f"Evidence {evidence_id} updated")

        return EvidenceResponse.model_validate(evidence)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update evidence: {str(e)}"
        )


@router.post("/{evidence_id}/transition", response_model=EvidenceResponse)
@require_permission(Permission.EVIDENCE_SUBMIT)
async def transition_evidence(
    evidence_id: str,
    tenant_id: str,
    transition: EvidenceWorkflowTransition,
    workflow: EvidenceWorkflow = Depends(get_evidence_workflow),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> EvidenceResponse:
    """
    Execute workflow transition
    Requires: EVIDENCE_SUBMIT permission (additional checks for review/verify actions)

    Workflow transitions (AI-proof fixed state machine):
    - DRAFT → SUBMITTED (submit)
    - SUBMITTED → UNDER_REVIEW (review)
    - UNDER_REVIEW → VERIFIED (verify)
    - UNDER_REVIEW → REJECTED (reject)
    - REJECTED → DRAFT (revise)

    Args:
        evidence_id: Evidence identifier
        tenant_id: Tenant identifier
        transition: Transition action and metadata
        workflow: Evidence workflow instance
        db: Database session
        current_user: Authenticated user

    Returns:
        Evidence after transition
    """
    try:
        # Verify tenant access
        verify_tenant_access(current_user, tenant_id)

        # Get evidence
        stmt = select(EvidenceModel).where(
            and_(
                EvidenceModel.id == evidence_id,
                EvidenceModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence {evidence_id} not found"
            )

        # Execute transition based on action
        if transition.action == "submit":
            result_evidence = await workflow.submit_evidence(
                evidence_id=evidence_id,
                tenant_id=tenant_id
            )
        elif transition.action == "review":
            result_evidence = await workflow.start_review(
                evidence_id=evidence_id,
                tenant_id=tenant_id,
                reviewer_id=transition.reviewer_id
            )
        elif transition.action == "verify":
            result_evidence = await workflow.verify_evidence(
                evidence_id=evidence_id,
                tenant_id=tenant_id,
                reviewer_id=transition.reviewer_id,
                reviewer_notes=transition.notes
            )
        elif transition.action == "reject":
            result_evidence = await workflow.reject_evidence(
                evidence_id=evidence_id,
                tenant_id=tenant_id,
                reviewer_id=transition.reviewer_id,
                rejection_reason=transition.notes or "Does not meet requirements"
            )
        elif transition.action == "revise":
            result_evidence = await workflow.revise_evidence(
                evidence_id=evidence_id,
                tenant_id=tenant_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid transition action: {transition.action}"
            )

        logger.info(
            f"Evidence {evidence_id} transitioned: "
            f"{evidence.status} → {result_evidence['status']}"
        )

        return EvidenceResponse(**result_evidence)

    except ValueError as e:
        # Workflow validation error (invalid transition)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to transition evidence: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transition evidence: {str(e)}"
        )


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(Permission.EVIDENCE_DELETE)
async def delete_evidence(
    evidence_id: str,
    tenant_id: str,
    workflow: EvidenceWorkflow = Depends(get_evidence_workflow),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete evidence
    Requires: EVIDENCE_DELETE permission

    Only evidence in DRAFT or REJECTED status can be deleted

    Args:
        evidence_id: Evidence identifier
        tenant_id: Tenant identifier
        workflow: Evidence workflow instance
        db: Database session
        current_user: Authenticated user
    """
    try:
        # Verify tenant access
        verify_tenant_access(current_user, tenant_id)

        # Get evidence
        stmt = select(EvidenceModel).where(
            and_(
                EvidenceModel.id == evidence_id,
                EvidenceModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence {evidence_id} not found"
            )

        # Check if deletion is allowed
        if evidence.status not in [EvidenceStatus.DRAFT.value, EvidenceStatus.REJECTED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete evidence in {evidence.status} status"
            )

        # Delete via workflow (handles cleanup and events)
        await workflow.delete_evidence(evidence_id, tenant_id)

        logger.info(f"Evidence {evidence_id} deleted")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete evidence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete evidence: {str(e)}"
        )


@router.get("/{evidence_id}/history", response_model=List[dict])
@require_permission(Permission.EVIDENCE_VIEW)
async def get_evidence_history(
    evidence_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[dict]:
    """
    Get evidence workflow history
    Requires: EVIDENCE_VIEW permission

    Returns all state transitions and actions performed on evidence

    Args:
        evidence_id: Evidence identifier
        tenant_id: Tenant identifier
        db: Database session
        current_user: Authenticated user

    Returns:
        List of workflow events
    """
    try:
        # Verify tenant access
        verify_tenant_access(current_user, tenant_id)

        # Check evidence exists
        stmt = select(EvidenceModel).where(
            and_(
                EvidenceModel.id == evidence_id,
                EvidenceModel.tenant_id == tenant_id
            )
        )
        result = await db.execute(stmt)
        evidence = result.scalar_one_or_none()

        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence {evidence_id} not found"
            )

        # Get workflow history from metadata or separate audit table
        # For now, return basic info from evidence record
        history = [
            {
                "timestamp": evidence.created_at.isoformat(),
                "action": "created",
                "status": EvidenceStatus.DRAFT.value,
                "actor": evidence.created_by if hasattr(evidence, "created_by") else None
            },
            {
                "timestamp": evidence.updated_at.isoformat(),
                "action": "last_updated",
                "status": evidence.status,
                "actor": evidence.reviewed_by if evidence.reviewed_by else None
            }
        ]

        # Add verification info if available
        if evidence.verified_at:
            history.append({
                "timestamp": evidence.verified_at.isoformat(),
                "action": "verified",
                "status": EvidenceStatus.VERIFIED.value,
                "actor": evidence.reviewed_by,
                "notes": evidence.reviewer_notes
            })

        return history

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get evidence history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get evidence history: {str(e)}"
        )
