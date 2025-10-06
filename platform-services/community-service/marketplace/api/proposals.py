"""
Proposals API Router
Endpoints for specialist proposals to client projects
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.connection import get_db
from api.dependencies import (
    get_current_user,
    require_client,
    require_specialist,
    require_verified_specialist,
    get_db_with_context
)
from schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse
)
from services.proposal_service import proposal_service

router = APIRouter(prefix="/api/marketplace/proposals", tags=["proposals"])


# ============================================================================
# Proposal Management Endpoints (Specialist)
# ============================================================================

@router.post("", response_model=ProposalResponse, status_code=201)
async def submit_proposal(
    proposal_data: ProposalCreate,
    current_user: dict = Depends(require_verified_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Submit proposal to project (Specialist action)

    **Requires:** Verified Specialist role

    **Business Rules:**
    - Can only propose to 'open' projects
    - Specialist must be verified
    - One proposal per specialist per project
    - Proposed budget should be within project budget range (warning only)
    - Estimated duration should match project timeline
    - Status starts as 'pending'

    **Flow:**
    1. Specialist sees open project
    2. Writes cover letter and proposes budget/timeline
    3. Submits proposal
    4. Client reviews and can accept/reject
    5. If accepted → Project assigned to specialist
    """
    # Get specialist_id from current user's profile
    from services.specialist_service import specialist_service

    specialist = await specialist_service.get_specialist_by_user(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"]
    )

    if not specialist:
        raise HTTPException(
            status_code=404,
            detail="Specialist profile not found. Create one first."
        )

    try:
        proposal = await proposal_service.create_proposal(
            db=db,
            proposal_data=proposal_data,
            specialist_id=specialist.id,
            tenant_id=current_user["tenant_id"],
            user_id=current_user["user_id"]
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ProposalResponse])
async def get_my_proposals(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get my proposals (Specialist view)

    **Requires:** Specialist or Admin role

    **Returns:** All proposals submitted by current specialist

    **Filters:**
    - status: pending, accepted, rejected, withdrawn
    """
    # Get specialist_id
    from services.specialist_service import specialist_service

    specialist = await specialist_service.get_specialist_by_user(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"]
    )

    if not specialist:
        raise HTTPException(
            status_code=404,
            detail="Specialist profile not found"
        )

    proposals = await proposal_service.get_proposals_by_specialist(
        db=db,
        specialist_id=specialist.id,
        tenant_id=current_user["tenant_id"],
        status=status,
        limit=limit
    )

    return proposals


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get proposal by ID

    **Requires:** Authentication

    **Access Control:**
    - Specialist: Can view own proposals
    - Client: Can view proposals for own projects
    - Admin: Can view all proposals
    """
    proposal = await proposal_service.get_proposal(
        db=db,
        proposal_id=proposal_id,
        tenant_id=current_user["tenant_id"]
    )

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Verify access
    user_type = current_user["user_type"]
    user_id = current_user["user_id"]

    if user_type == "admin":
        # Admin can see everything
        pass
    elif user_type == "specialist":
        # Specialist can only see own proposals
        if str(proposal.specialist.user_id) != str(user_id):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own proposals"
            )
    elif user_type == "client":
        # Client can only see proposals for own projects
        if str(proposal.project.client_id) != str(user_id):
            raise HTTPException(
                status_code=403,
                detail="You can only view proposals for your own projects"
            )
    else:
        raise HTTPException(status_code=403, detail="Access denied")

    return proposal


@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: int,
    proposal_data: ProposalUpdate,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Update proposal (Specialist action)

    **Requires:** Specialist ownership

    **Business Rules:**
    - Can only update 'pending' proposals
    - Cannot update 'accepted', 'rejected', or 'withdrawn'
    - Can update cover letter, budget, timeline
    """
    # Get proposal
    proposal = await proposal_service.get_proposal(
        db=db,
        proposal_id=proposal_id,
        tenant_id=current_user["tenant_id"]
    )

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Verify ownership
    if str(proposal.specialist.user_id) != str(current_user["user_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own proposals"
        )

    try:
        proposal = await proposal_service.update_proposal(
            db=db,
            proposal_id=proposal_id,
            proposal_data=proposal_data,
            tenant_id=current_user["tenant_id"]
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{proposal_id}", status_code=204)
async def delete_proposal(
    proposal_id: int,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Delete proposal (Specialist action)

    **Requires:** Specialist ownership

    **Business Rules:**
    - Can only delete 'pending' proposals
    - Hard delete (permanent)
    - Use withdraw endpoint for soft withdrawal with reason
    """
    # Get proposal
    proposal = await proposal_service.get_proposal(
        db=db,
        proposal_id=proposal_id,
        tenant_id=current_user["tenant_id"]
    )

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Verify ownership
    if str(proposal.specialist.user_id) != str(current_user["user_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own proposals"
        )

    if proposal.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Can only delete 'pending' proposals, current: '{proposal.status}'"
        )

    # Hard delete
    from database.models import Proposal
    from sqlalchemy import delete as sql_delete

    await db.execute(
        sql_delete(Proposal).where(Proposal.id == proposal_id)
    )
    await db.commit()


# ============================================================================
# Proposal Actions (Client)
# ============================================================================

@router.post("/{proposal_id}/accept", response_model=ProposalResponse)
async def accept_proposal(
    proposal_id: int,
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Accept proposal (Client action)

    **Requires:** Project ownership

    **Business Rules:**
    - Can only accept 'pending' proposals
    - Changes proposal status to 'accepted'
    - Rejects all other proposals for same project
    - Assigns specialist to project (status: open → in_progress)
    - Emits proposal.accepted + project.assigned events
    - Should trigger contract creation (future)

    **This is the CRITICAL BUSINESS TRANSACTION**

    **Flow:**
    1. Client reviews multiple proposals
    2. Selects best specialist
    3. Accepts proposal
    4. All other proposals auto-rejected
    5. Project status → in_progress
    6. Specialist assigned to project
    7. Work begins
    """
    # Get proposal
    proposal = await proposal_service.get_proposal(
        db=db,
        proposal_id=proposal_id,
        tenant_id=current_user["tenant_id"]
    )

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Verify project ownership
    if str(proposal.project.client_id) != str(current_user["user_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only accept proposals for your own projects"
        )

    try:
        proposal = await proposal_service.accept_proposal(
            db=db,
            proposal_id=proposal_id,
            tenant_id=current_user["tenant_id"],
            client_id=current_user["user_id"]
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{proposal_id}/reject", response_model=ProposalResponse)
async def reject_proposal(
    proposal_id: int,
    reason: Optional[str] = Query(None, description="Rejection reason"),
    current_user: dict = Depends(require_client),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Reject proposal (Client action)

    **Requires:** Project ownership

    **Business Rules:**
    - Can only reject 'pending' proposals
    - Changes status to 'rejected'
    - Optional reason for rejection (feedback for specialist)
    - Emits proposal.rejected event
    """
    # Get proposal
    proposal = await proposal_service.get_proposal(
        db=db,
        proposal_id=proposal_id,
        tenant_id=current_user["tenant_id"]
    )

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Verify project ownership
    if str(proposal.project.client_id) != str(current_user["user_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only reject proposals for your own projects"
        )

    try:
        proposal = await proposal_service.reject_proposal(
            db=db,
            proposal_id=proposal_id,
            tenant_id=current_user["tenant_id"],
            client_id=current_user["user_id"],
            reason=reason
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Proposal Actions (Specialist)
# ============================================================================

@router.post("/{proposal_id}/withdraw", response_model=ProposalResponse)
async def withdraw_proposal(
    proposal_id: int,
    reason: Optional[str] = Query(None, description="Withdrawal reason"),
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Withdraw proposal (Specialist action)

    **Requires:** Specialist ownership

    **Business Rules:**
    - Can only withdraw 'pending' proposals
    - Changes status to 'withdrawn'
    - Decrements project proposal_count
    - Optional reason

    **Use Cases:**
    - Specialist no longer available
    - Found better opportunity
    - Project requirements changed
    """
    # Get proposal
    proposal = await proposal_service.get_proposal(
        db=db,
        proposal_id=proposal_id,
        tenant_id=current_user["tenant_id"]
    )

    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Verify ownership
    if str(proposal.specialist.user_id) != str(current_user["user_id"]):
        raise HTTPException(
            status_code=403,
            detail="You can only withdraw your own proposals"
        )

    try:
        proposal = await proposal_service.withdraw_proposal(
            db=db,
            proposal_id=proposal_id,
            tenant_id=current_user["tenant_id"],
            reason=reason
        )
        return proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Statistics
# ============================================================================

@router.get("/stats/my")
async def get_my_proposal_stats(
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db_with_context)
):
    """
    Get my proposal statistics (Specialist view)

    **Requires:** Specialist role

    **Returns:**
    - Total proposals submitted
    - By status (pending, accepted, rejected, withdrawn)
    - Acceptance rate (accepted / (accepted + rejected))
    - Current pending count

    **Use Cases:**
    - Specialist dashboard
    - Track performance
    - Identify improvement areas
    """
    # Get specialist_id
    from services.specialist_service import specialist_service

    specialist = await specialist_service.get_specialist_by_user(
        db=db,
        user_id=current_user["user_id"],
        tenant_id=current_user["tenant_id"]
    )

    if not specialist:
        raise HTTPException(
            status_code=404,
            detail="Specialist profile not found"
        )

    stats = await proposal_service.get_proposal_stats(
        db=db,
        specialist_id=specialist.id,
        tenant_id=current_user["tenant_id"]
    )

    return stats
